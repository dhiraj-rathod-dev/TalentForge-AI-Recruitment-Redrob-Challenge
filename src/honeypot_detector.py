from __future__ import annotations
from src.parser import CandidateProfile
from src.parser import NEGATIVE_SIGNALS

HONEYPOT_TYPES = {
    "IMPOSSIBLE_AGE": "impossible_age",
    "SKILL_OVERFLOW": "skill_overflow",
    "CONTRADICTORY_PROFILE": "contradictory",
    "SALARY_ANOMALY": "salary_anomaly",
    "TIMELINE_OVERLAP": "timeline_overlap",
    "BEHAVIORAL_ANOMALY": "behavioral_anomaly",
    "FAKE_EXPERIENCE": "fake_experience",
}


class HoneypotDetector:
    def detect(self, c: CandidateProfile) -> dict:
        checks = []

        self._check_impossible_age(c, checks)
        self._check_skill_overflow(c, checks)
        self._check_contradictory(c, checks)
        self._check_salary_anomaly(c, checks)
        self._check_timeline_overlap(c, checks)
        self._check_behavioral_anomaly(c, checks)
        self._check_fake_experience(c, checks)

        if not checks:
            return {"is_honeypot": False, "honeypot_type": None, "honeypot_penalty": 0.0}

        worst = max(checks, key=lambda x: x[1])
        return {
            "is_honeypot": True,
            "honeypot_type": worst[0],
            "honeypot_penalty": worst[1],
        }

    def _check_impossible_age(self, c: CandidateProfile, checks: list):
        edu = c.education
        if isinstance(edu, dict):
            edu_year = edu.get("year", 0)
        else:
            edu_year = 0
        if edu_year and c.total_experience_years > 0:
            grad_year = int(edu_year) if edu_year else 0
            if grad_year + c.total_experience_years > 2026:
                checks.append(("IMPOSSIBLE_AGE", 0.5))

    def _check_skill_overflow(self, c: CandidateProfile, checks: list):
        skill_count = len(c.skills)
        if skill_count > 100:
            checks.append(("SKILL_OVERFLOW", 0.5))
        elif skill_count > 50:
            checks.append(("SKILL_OVERFLOW", 0.3))

    def _check_contradictory(self, c: CandidateProfile, checks: list):
        title_lower = c.current_title.lower()
        is_non_technical = any(nt in title_lower for nt in NEGATIVE_SIGNALS)
        if is_non_technical:
            ai_skill_count = sum(
                1 for sn in c.skill_names
                if any(term in sn for term in [
                    "ai", "machine learning", "deep learning", "nlp",
                    "neural", "pytorch", "tensorflow", "transformer",
                    "embedding", "retrieval", "rag", "llm", "faiss",
                    "elasticsearch", "bm25", "vector database", "semantic search",
                    "ranking", "search", "recommendation", "fine-tuning",
                    "lora", "milvus", "pinecone", "qdrant", "weaviate",
                    "information retrieval", "learning to rank",
                ])
            )
            if ai_skill_count >= 5:
                checks.append(("CONTRADICTORY_PROFILE", 0.4))

    def _check_salary_anomaly(self, c: CandidateProfile, checks: list):
        sig = c.behavioral_signals
        sal_min = sig.get("salary_expectation_min", 0)
        sal_max = sig.get("salary_expectation_max", 0)
        if sal_min > sal_max and sal_max > 0:
            checks.append(("SALARY_ANOMALY", 0.3))

    def _check_timeline_overlap(self, c: CandidateProfile, checks: list):
        periods = []
        for job in c.career_history:
            start = job.get("start_year")
            end = job.get("end_year")
            if start and end:
                periods.append((start, end))

        for i in range(len(periods)):
            for j in range(i + 1, len(periods)):
                s1, e1 = periods[i]
                s2, e2 = periods[j]
                if s1 < e2 and s2 < e1:
                    checks.append(("TIMELINE_OVERLAP", 0.3))
                    return

    def _check_behavioral_anomaly(self, c: CandidateProfile, checks: list):
        sig = c.behavioral_signals
        flags = 0

        gh = sig.get("github_activity_score", -1)
        saved = sig.get("saved_by_recruiters_30d", 0)
        views = sig.get("profile_views_30d", 0)
        response_rate = sig.get("recruiter_response_rate", 0.0)

        if gh > 90 and saved == 0 and views == 0:
            flags += 1

        if response_rate > 0.95 and saved == 0 and views == 0:
            flags += 1

        apps = sig.get("applied_jobs_last_30d", 0)
        if apps > 15 and saved == 0 and views < 10:
            flags += 1

        if flags >= 2:
            checks.append(("BEHAVIORAL_ANOMALY", 0.3))

    def _check_fake_experience(self, c: CandidateProfile, checks: list):
        if not c.career_history:
            return

        for job in c.career_history:
            desc = (job.get("description", "") or "").lower()
            title = (job.get("title", "") or "").lower()
            company = (job.get("company", "") or "").lower()

            if "llm" in desc and "manager" in title and "marketing" in title:
                checks.append(("FAKE_EXPERIENCE", 0.3))
                return

            if "chief ai" in title and c.total_experience_years < 3:
                checks.append(("FAKE_EXPERIENCE", 0.4))
                return

            start = job.get("start_year", 0)
            end = job.get("end_year", 0)
            dur = job.get("duration_years", 0)
            if start and end and dur:
                expected = end - start
                if abs(expected - dur) > 3 and expected > 0:
                    checks.append(("FAKE_EXPERIENCE", 0.3))
                    return

        exp = c.total_experience_years
        total_dur = sum(job.get("duration_years", 0) for job in c.career_history)
        if total_dur > exp * 1.5 and exp > 0:
            checks.append(("FAKE_EXPERIENCE", 0.2))
