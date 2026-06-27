from __future__ import annotations
import json
import os
import time
import sys
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.parser import parse_jd, parse_candidate
from src.candidate_analyzer import CandidateAnalyzer
from src.behavioral_engine import BehavioralEngine
from src.honeypot_detector import HoneypotDetector
from src.semantic_matcher import SemanticMatcher
from src.scorer import Scorer
from src.reasoning_generator import ReasoningGenerator


def detect_format(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        first = f.read(4096).strip()
    if first.startswith("{"):
        return "jsonl"
    if first.startswith("["):
        return "json"
    return "jsonl"


def load_candidates_jsonl(path: str) -> list[dict]:
    candidates = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    return candidates


def load_candidates_json(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_candidates(path: str) -> list[dict]:
    fmt = detect_format(path)
    if fmt == "jsonl":
        return load_candidates_jsonl(path)
    return load_candidates_json(path)


def run_pipeline(
    candidates_path: str = None,
    top_k: int = 100,
    output_dir: str = None,
    submission_path: str = None,
    max_candidates: int = None,
) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    if candidates_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates_path = os.path.join(script_dir, "..", "data", "candidates.json")

    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "..", "output")

    os.makedirs(output_dir, exist_ok=True)

    t_start = time.time()

    print("Loading candidates...")
    raw_candidates = load_candidates(candidates_path)
    if max_candidates and len(raw_candidates) > max_candidates:
        raw_candidates = raw_candidates[:max_candidates]
    print(f"   Loaded {len(raw_candidates)} candidates")

    print("Parsing job description...")
    jd = parse_jd()

    print("Parsing candidates...")
    candidates = [parse_candidate(raw) for raw in tqdm(raw_candidates)]

    print("Building semantic embeddings...")
    force_tfidf = len(raw_candidates) > 10000
    if force_tfidf:
        print("   Large dataset detected: using TF-IDF fallback for performance")
    matcher = SemanticMatcher(force_tfidf=force_tfidf)
    candidate_embeddings, faiss_index = matcher.build_index(candidates)
    semantic_scores = matcher.compute_similarities(jd, candidates, candidate_embeddings, faiss_index)

    print("Computing semantic title & experience scores...")
    title_sem_scores = matcher.compute_title_similarities(jd, candidates)
    exp_sem_scores = matcher.compute_experience_similarities(jd, candidates)

    print("Scoring candidates...")
    analyzer = CandidateAnalyzer(jd)
    behavioral_engine = BehavioralEngine()
    honeypot_detector = HoneypotDetector()
    scorer = Scorer(jd, analyzer, behavioral_engine, honeypot_detector, matcher)
    reasoning_gen = ReasoningGenerator()

    all_results = []
    for i, c in enumerate(tqdm(candidates)):
        result = scorer.score_candidate(
            c,
            float(semantic_scores[i]),
            float(title_sem_scores[i]),
            float(exp_sem_scores[i]),
        )
        result["candidate_obj"] = c
        all_results.append(result)

    all_results = Scorer.sort_and_rank(all_results)

    top_results = all_results[:top_k]

    print("Generating reasoning...")
    for r in tqdm(top_results):
        reasoning = reasoning_gen.generate(r["candidate_obj"], r)
        r["reasoning"] = reasoning

    score_reasoning_map = {}
    for r in tqdm(all_results):
        score_reasoning_map[r["candidate_id"]] = reasoning_gen.generate(r["candidate_obj"], r)

    top_df = pd.DataFrame([
        {
            "rank": idx + 1,
            "name": r["name"],
            "final_score": r["final_score"],
            "semantic_score": r["semantic_score"],
            "experience_score": r["experience_score"],
            "behavioral_score": r["behavioral_score"],
            "retrieval_score": r["retrieval_score"],
            "career_growth_score": r["career_growth_score"],
            "location_score": r["location_score"],
            "education_score": r["education_score"],
            "skill_depth_score": r["skill_depth_score"],
            "skill_duration_score": r["skill_duration_score"],
            "skill_endorsement_score": r["skill_endorsement_score"],
            "leadership_score": r["leadership_score"],
            "job_stability_score": r["job_stability_score"],
            "startup_mindset_score": r["startup_mindset_score"],
            "title_semantic_score": r["title_semantic_score"],
            "experience_semantic_score": r["experience_semantic_score"],
            "honeypot_flag": r["honeypot_flag"],
            "honeypot_type": r.get("honeypot_type", ""),
            "reasoning": score_reasoning_map.get(r["candidate_id"], ""),
            "current_title": r["current_title"],
            "current_company": r["current_company"],
            "experience_years": r["experience_years"],
            "location": r["location"],
        }
        for idx, r in enumerate(top_results)
    ])
    top_path = os.path.join(output_dir, "top_100_candidates.csv")
    top_df.to_csv(top_path, index=False)
    print(f"   Exported top 100 → {top_path}")

    all_df = pd.DataFrame([
        {
            "rank": idx + 1,
            "name": r["name"],
            "final_score": r["final_score"],
            "semantic_score": r["semantic_score"],
            "experience_score": r["experience_score"],
            "behavioral_score": r["behavioral_score"],
            "retrieval_score": r["retrieval_score"],
            "career_growth_score": r["career_growth_score"],
            "location_score": r["location_score"],
            "education_score": r["education_score"],
            "skill_depth_score": r["skill_depth_score"],
            "skill_duration_score": r["skill_duration_score"],
            "skill_endorsement_score": r["skill_endorsement_score"],
            "leadership_score": r["leadership_score"],
            "job_stability_score": r["job_stability_score"],
            "startup_mindset_score": r["startup_mindset_score"],
            "title_semantic_score": r["title_semantic_score"],
            "experience_semantic_score": r["experience_semantic_score"],
            "honeypot_flag": r["honeypot_flag"],
            "honeypot_type": r.get("honeypot_type", ""),
            "reasoning": score_reasoning_map.get(r["candidate_id"], ""),
            "current_title": r["current_title"],
            "current_company": r["current_company"],
            "experience_years": r["experience_years"],
            "location": r["location"],
        }
        for idx, r in enumerate(all_results)
    ])
    all_path = os.path.join(output_dir, "all_candidates_scored.csv")
    all_df.to_csv(all_path, index=False)
    print(f"   Exported all scores → {all_path}")

    if submission_path:
        sub_df = pd.DataFrame([
            {
                "candidate_id": r["candidate_id"],
                "rank": idx + 1,
                "score": r["final_score"],
                "reasoning": score_reasoning_map.get(r["candidate_id"], ""),
            }
            for idx, r in enumerate(top_results)
        ])
        sub_df.to_csv(submission_path, index=False)
        print(f"   Exported submission → {submission_path}")

    t_elapsed = time.time() - t_start
    print(f"\n   Total runtime: {t_elapsed:.2f}s ({t_elapsed/60:.2f} min)")

    return top_df, all_df, t_elapsed


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--top-k", type=int, default=100)
    args = parser.parse_args()
    run_pipeline(
        candidates_path=args.candidates,
        top_k=args.top_k,
        submission_path=args.out,
    )

