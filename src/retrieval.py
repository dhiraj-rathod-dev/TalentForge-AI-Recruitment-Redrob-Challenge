"""
TalentForge AI – Retrieval Module
Re-exports semantic matching and BM25 retrieval functionality.
"""

from __future__ import annotations
from src.semantic_matcher import SemanticMatcher, BM25
from src.parser import JDProfile, CandidateProfile
from typing import List
import numpy as np


class RetrievalEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.matcher = SemanticMatcher(model_name)
        self._candidates: List[CandidateProfile] = []
        self._embeddings: np.ndarray | None = None
        self._faiss_index = None

    def index(self, candidates: List[CandidateProfile]):
        self._candidates = candidates
        self._embeddings, self._faiss_index = self.matcher.build_index(candidates)

    def dense_retrieval(self, jd: JDProfile, top_k: int = 100) -> np.ndarray:
        if self._embeddings is None:
            raise RuntimeError("Call index() first")
        return self.matcher.compute_similarities(jd, self._candidates, self._embeddings, self._faiss_index)

    def bm25_retrieve(self, jd: JDProfile) -> np.ndarray:
        if self.matcher._bm25 is None or not self.matcher._bm25_fitted:
            raise RuntimeError("BM25 not fitted. Call index() first.")
        return self.matcher._bm25.transform(jd.full_text)

    def hybrid_retrieve(self, jd: JDProfile, alpha: float = 0.7, top_k: int = 100) -> np.ndarray:
        return self.matcher.compute_similarities(jd, self._candidates, self._embeddings, self._faiss_index, hybrid_alpha=alpha)
