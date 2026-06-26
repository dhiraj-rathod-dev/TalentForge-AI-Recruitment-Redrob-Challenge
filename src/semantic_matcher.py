from __future__ import annotations
import numpy as np
from typing import List
from src.parser import JDProfile, CandidateProfile

try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
except ImportError:
    _ST_AVAILABLE = False

try:
    import faiss
    _FAISS_AVAILABLE = True
except ImportError:
    _FAISS_AVAILABLE = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs: list[dict[int, int]] = []
        self.idf: dict[int, float] = {}
        self.doc_lens: list[int] = []
        self.avg_doc_len: float = 0.0
        self.vocab: dict[str, int] = {}
        self.N: int = 0

    def fit(self, texts: List[str]):
        self.doc_freqs = []
        self.doc_lens = []
        self.vocab = {}
        for t in texts:
            tokens = t.lower().split()
            self.doc_lens.append(len(tokens))
            freqs: dict[int, int] = {}
            for tok in set(tokens):
                if tok not in self.vocab:
                    self.vocab[tok] = len(self.vocab)
                tid = self.vocab[tok]
                freqs[tid] = freqs.get(tid, 0) + 1
            self.doc_freqs.append(freqs)

        self.N = len(texts)
        self.avg_doc_len = sum(self.doc_lens) / max(self.N, 1)

        doc_count: dict[int, int] = {}
        for freqs in self.doc_freqs:
            for tid in freqs:
                doc_count[tid] = doc_count.get(tid, 0) + 1

        self.idf = {}
        for tid, df in doc_count.items():
            self.idf[tid] = np.log(1 + (self.N - df + 0.5) / (df + 0.5))

    def transform(self, query: str) -> np.ndarray:
        scores = np.zeros(self.N)
        q_tokens = query.lower().split()
        for tok in q_tokens:
            if tok not in self.vocab:
                continue
            tid = self.vocab[tok]
            idf_val = self.idf.get(tid, 0.0)
            for i in range(self.N):
                tf = self.doc_freqs[i].get(tid, 0)
                if tf > 0:
                    scores[i] += idf_val * (tf * (self.k1 + 1)) / (
                        tf + self.k1 * (1 - self.b + self.b * self.doc_lens[i] / self.avg_doc_len)
                    )
        return np.clip(scores / max(np.max(scores), 1e-10), 0, 1)


class SemanticMatcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", force_tfidf: bool = False):
        self.model = None
        self.model_name = model_name
        self.use_transformers = False
        self._tfidf = None
        self._tfidf_matrix = None
        self._candidate_ids: list[str] = []
        self._bm25 = None
        self._bm25_fitted = False

        if force_tfidf:
            return

        if _ST_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                self.use_transformers = True
            except Exception as e:
                pass

    def encode(self, texts: List[str]):
        if self.use_transformers and self.model is not None:
            return self.model.encode(texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
        else:
            from scipy.sparse import spmatrix
            if self._tfidf is None:
                self._tfidf = TfidfVectorizer(
                    max_features=4000, ngram_range=(1, 2), sublinear_tf=True
                )
                mat = self._tfidf.fit_transform(texts).tocsr()
                norms = np.sqrt(mat.multiply(mat).sum(axis=1)) + 1e-10
                return mat.multiply(1.0 / norms).tocsr()
            else:
                mat = self._tfidf.transform(texts).tocsr()
                norms = np.sqrt(mat.multiply(mat).sum(axis=1)) + 1e-10
                return mat.multiply(1.0 / norms).tocsr()

    def build_index(self, candidates: List[CandidateProfile]) -> tuple[any, "faiss.Index | None"]:
        texts = [c.all_text for c in candidates]
        self._candidate_ids = [c.id for c in candidates]

        if not self.use_transformers:
            from src.parser import JD_TEXT
            all_texts = [JD_TEXT] + texts
            self._tfidf = TfidfVectorizer(
                max_features=4000, ngram_range=(1, 2), sublinear_tf=True
            )
            all_mat = self._tfidf.fit_transform(all_texts).tocsr()
            norms = np.sqrt(all_mat.multiply(all_mat).sum(axis=1)) + 1e-10
            all_mat = all_mat.multiply(1.0 / norms).tocsr()
            candidate_embeddings = all_mat[1:]
        else:
            candidate_embeddings = self.encode(texts)

        self._bm25 = BM25()
        self._bm25.fit(texts)
        self._bm25_fitted = True

        if _FAISS_AVAILABLE and self.use_transformers:
            dim = candidate_embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(candidate_embeddings.astype(np.float32))
            return candidate_embeddings, index

        return candidate_embeddings, None

    def compute_similarities(
        self,
        jd: JDProfile,
        candidates: List[CandidateProfile],
        candidate_embeddings,
        faiss_index=None,
        hybrid_alpha: float = 0.7,
    ) -> np.ndarray:
        jd_embedding = self.encode([jd.full_text])

        if faiss_index is not None:
            sims = (jd_embedding @ candidate_embeddings.T).flatten()
            emb_scores = np.clip(sims, 0, 1)
        else:
            sims = sklearn_cosine(jd_embedding, candidate_embeddings).flatten()
            emb_scores = np.clip(sims, 0, 1)

        if self._bm25_fitted and self._bm25 is not None:
            bm25_scores = self._bm25.transform(jd.full_text)
            hybrid = hybrid_alpha * emb_scores + (1 - hybrid_alpha) * bm25_scores
            return np.clip(hybrid, 0, 1)

        return emb_scores

    def compute_skill_similarity(self, jd: JDProfile, candidate: CandidateProfile) -> float:
        if not candidate.skill_names:
            return 0.0
        skill_text = " ".join(candidate.skill_names)
        required_text = " ".join(jd.required_skills + jd.preferred_skills)
        if self.use_transformers and self.model is not None:
            emb = self.model.encode([skill_text, required_text], normalize_embeddings=True)
            return float(np.dot(emb[0], emb[1]))
        else:
            if self._tfidf is None:
                return 0.0
            skill_vec = self._tfidf.transform([skill_text]).toarray()
            req_vec = self._tfidf.transform([required_text]).toarray()
            sim = sklearn_cosine(skill_vec, req_vec)[0][0]
            return float(np.clip(sim, 0, 1))

    def _get_req_title_text(self) -> str:
        return " ".join([
            "ai engineer", "ml engineer", "search engineer", "nlp engineer",
            "ranking engineer", "retrieval engineer", "senior ai engineer",
            "machine learning engineer", "applied scientist",
        ])

    def compute_title_similarities(self, jd: JDProfile, candidates: List[CandidateProfile]) -> np.ndarray:
        title_texts = [c.current_title for c in candidates]
        req = self._get_req_title_text()
        if self.use_transformers and self.model is not None:
            all_texts = [req] + title_texts
            embs = self.model.encode(all_texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
            req_emb = embs[0:1]
            title_embs = embs[1:]
            sims = (req_emb @ title_embs.T).flatten()
            return np.clip(sims, 0, 1)
        else:
            if self._tfidf is None:
                return np.zeros(len(candidates))
            req_vec = self._tfidf.transform([req])
            title_vecs = self._tfidf.transform(title_texts)
            sims = sklearn_cosine(req_vec, title_vecs).flatten()
            return np.clip(sims, 0, 1)

    def compute_experience_similarities(self, jd: JDProfile, candidates: List[CandidateProfile]) -> np.ndarray:
        exp_texts = [f"{c.current_title} {c.career_text} {c.summary}" for c in candidates]
        jd_exp_text = " ".join(jd.required_skills + [jd.full_text])
        if self.use_transformers and self.model is not None:
            all_texts = [jd_exp_text] + exp_texts
            embs = self.model.encode(all_texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
            jd_emb = embs[0:1]
            exp_embs = embs[1:]
            sims = (jd_emb @ exp_embs.T).flatten()
            return np.clip(sims, 0, 1)
        else:
            if self._tfidf is None:
                return np.zeros(len(candidates))
            jd_vec = self._tfidf.transform([jd_exp_text])
            exp_vecs = self._tfidf.transform(exp_texts)
            sims = sklearn_cosine(jd_vec, exp_vecs).flatten()
            return np.clip(sims, 0, 1)
