"""
TalentForge AI – Feature Engineering Module
Re-exports and consolidates all feature scoring functions.
"""

from __future__ import annotations
from src.candidate_analyzer import CandidateAnalyzer
from src.parser import CandidateProfile, JDProfile


class FeatureEngineer:
    def __init__(self, jd: JDProfile):
        self.analyzer = CandidateAnalyzer(jd)

    def extract_all(self, c: CandidateProfile) -> dict:
        return self.analyzer.analyze(c)

    def extract_experience_features(self, c: CandidateProfile) -> dict:
        return {
            "total_experience_years": c.total_experience_years,
            "experience_score": self.analyzer.score_experience(c),
            "career_growth_score": self.analyzer.score_career_growth(c),
            "job_stability_score": self.analyzer.score_job_stability(c),
        }

    def extract_skill_features(self, c: CandidateProfile) -> dict:
        return {
            "skill_count": len(c.skills),
            "skill_coverage_score": self.analyzer.score_skill_coverage(c),
            "skill_depth_score": self.analyzer.score_skill_depth(c),
            "skill_duration_score": self.analyzer.score_skill_duration(c),
            "skill_endorsement_score": self.analyzer.score_skill_endorsement(c),
            "retrieval_score": self.analyzer.score_retrieval_expertise(c),
        }

    def extract_profile_features(self, c: CandidateProfile) -> dict:
        return {
            "title_quality_score": self.analyzer.score_title_quality(c),
            "education_score": self.analyzer.score_education(c),
            "location_score": self.analyzer.score_location(c),
            "product_company_score": self.analyzer.score_product_company(c),
            "leadership_score": self.analyzer.score_leadership(c),
            "startup_mindset_score": self.analyzer.score_startup_mindset(c),
        }
