from __future__ import annotations
import numpy as np
from src.parser import JDProfile, CandidateProfile
from src.candidate_analyzer import CandidateAnalyzer
from src.behavioral_engine import BehavioralEngine
from src.honeypot_detector import HoneypotDetector
from src.semantic_matcher import SemanticMatcher


class Scorer:
    def __init__(
        self,
        jd: JDProfile,
        analyzer: CandidateAnalyzer,
        behavioral_engine: BehavioralEngine,
        honeypot_detector: HoneypotDetector,
        semantic_matcher: SemanticMatcher,
    ):
        self.jd = jd
        self.analyzer = analyzer
        self.behavioral = behavioral_engine
        self.honeypot = honeypot_detector
        self.semantic = semantic_matcher

        self.weights = {
            "semantic_match_score": 0.25,
            "experience_score": 0.15,
            "behavioral_score": 0.12,
            "retrieval_ranking_score": 0.10,
            "career_growth_score": 0.06,
            "location_score": 0.04,
            "education_score": 0.04,
            "skill_depth_score": 0.05,
            "skill_duration_score": 0.03,
            "skill_endorsement_score": 0.02,
            "leadership_score": 0.03,
            "job_stability_score": 0.03,
            "startup_mindset_score": 0.03,
            "title_semantic_score": 0.03,
            "experience_semantic_score": 0.02,
        }

    def score_candidate(self, c: CandidateProfile, semantic_score: float, title_sem_score: float = 0.5, exp_sem_score: float = 0.5) -> dict:
        dim_scores = self.analyzer.analyze(c)
        behavioral_score = self.behavioral.score_behavioral(c)
        honey_result = self.honeypot.detect(c)

        final_score = (
            0.25 * semantic_score
            + 0.15 * dim_scores["experience_score"]
            + 0.12 * behavioral_score
            + 0.10 * dim_scores["retrieval_score"]
            + 0.06 * dim_scores["career_growth_score"]
            + 0.04 * dim_scores["location_score"]
            + 0.04 * dim_scores["education_score"]
            + 0.05 * dim_scores["skill_depth_score"]
            + 0.03 * dim_scores["skill_duration_score"]
            + 0.02 * dim_scores["skill_endorsement_score"]
            + 0.03 * dim_scores["leadership_score"]
            + 0.03 * dim_scores["job_stability_score"]
            + 0.03 * dim_scores["startup_mindset_score"]
            + 0.03 * title_sem_score
            + 0.02 * exp_sem_score
        ) - honey_result["honeypot_penalty"]

        final_score = max(0.0, min(1.0, final_score))

        return {
            "candidate_id": c.id,
            "name": c.name,
            "current_title": c.current_title,
            "current_company": c.current_company,
            "experience_years": c.total_experience_years,
            "location": c.location,
            "semantic_score": round(float(semantic_score), 4),
            "experience_score": round(float(dim_scores["experience_score"]), 4),
            "retrieval_score": round(float(dim_scores["retrieval_score"]), 4),
            "career_growth_score": round(float(dim_scores["career_growth_score"]), 4),
            "location_score": round(float(dim_scores["location_score"]), 4),
            "education_score": round(float(dim_scores["education_score"]), 4),
            "behavioral_score": round(float(behavioral_score), 4),
            "product_company_score": round(float(dim_scores["product_company_score"]), 4),
            "title_quality_score": round(float(dim_scores["title_quality_score"]), 4),
            "skill_coverage_score": round(float(dim_scores["skill_coverage_score"]), 4),
            "skill_depth_score": round(float(dim_scores["skill_depth_score"]), 4),
            "skill_duration_score": round(float(dim_scores["skill_duration_score"]), 4),
            "skill_endorsement_score": round(float(dim_scores["skill_endorsement_score"]), 4),
            "leadership_score": round(float(dim_scores["leadership_score"]), 4),
            "job_stability_score": round(float(dim_scores["job_stability_score"]), 4),
            "startup_mindset_score": round(float(dim_scores["startup_mindset_score"]), 4),
            "title_semantic_score": round(float(title_sem_score), 4),
            "experience_semantic_score": round(float(exp_sem_score), 4),
            "honeypot_flag": honey_result["is_honeypot"],
            "honeypot_type": honey_result["honeypot_type"],
            "honeypot_penalty": honey_result["honeypot_penalty"],
            "final_score": round(float(final_score), 4),
        }

    @staticmethod
    def sort_and_rank(results: list[dict]) -> list[dict]:
        results.sort(key=lambda r: r["final_score"], reverse=True)

        i = 0
        while i < len(results):
            j = i
            while j < len(results) and results[j]["final_score"] == results[i]["final_score"]:
                j += 1
            if j - i > 1:
                chunk = results[i:j]
                chunk.sort(key=lambda r: r.get("candidate_id", ""))
                results[i:j] = chunk
            i = j

        for i, r in enumerate(results):
            r["rank"] = i + 1

        return results
