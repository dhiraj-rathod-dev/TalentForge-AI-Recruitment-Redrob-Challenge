from __future__ import annotations
import re
from src.parser import CandidateProfile, JDProfile, RETRIEVAL_SIGNALS, PREFERRED_LOCATIONS

TIER1_UNIVERSITIES = {
    "iit", "iitb", "iitd", "iitm", "iisc", "bits pilani",
    "iiit hyderabad", "iiit bangalore", "iiit delhi",
}

TIER2_UNIVERSITIES = {
    "nit", "vit", "manipal", "pune university", "delhi university",
    "anna university", "jadavpur", "thapar",
}

NEGATIVE_TITLE_TERMS = {
    "marketing", "hr ", "human resource", "operations", "customer success",
    "customer support", "accountant", "sales", "content", "scrum",
    "business development", "ux designer", "recruiter",
}

STRONG_TITLE_TERMS = {
    "ai engineer", "ml engineer", "machine learning", "nlp", "search engineer",
    "retrieval", "ranking", "recommendation", "data scientist", "applied scientist",
    "research engineer", "platform engineer", "infrastructure engineer",
}

LEADERSHIP_TITLE_TERMS = {
    "lead", "head", "director", "vp", "principal", "architect",
    "manager", "staff", "fellow", "chief",
}

PROFICIENCY_WEIGHTS = {
    "beginner": 0.3,
    "intermediate": 0.6,
    "advanced": 0.85,
    "expert": 1.0,
}


class CandidateAnalyzer:
    def __init__(self, jd: JDProfile):
        self.jd = jd

    def score_experience(self, c: CandidateProfile) -> float:
        exp = c.total_experience_years
        if 5 <= exp <= 9:
            return 1.0
        elif 4 <= exp < 5:
            return 0.75
        elif 9 < exp <= 12:
            return 0.70
        elif 3 <= exp < 4:
            return 0.50
        elif exp > 12:
            return 0.50
        else:
            return 0.20

    def score_retrieval_expertise(self, c: CandidateProfile) -> float:
        text_lower = c.all_text.lower()
        matched = [term for term in RETRIEVAL_SIGNALS if term in text_lower]
        skill_hits = sum(1 for sn in c.skill_names if any(t in sn for t in RETRIEVAL_SIGNALS))

        base = min(len(set(matched)) * 0.07, 0.70)
        skill_bonus = min(skill_hits * 0.05, 0.30)
        return min(base + skill_bonus, 1.0)

    def score_product_company(self, c: CandidateProfile) -> float:
        if c.consulting_only:
            return 0.2
        if c.has_product_company and not c.consulting_only:
            from src.parser import CONSULTING_COMPANIES
            all_companies = [job.get("company", "").lower() for job in c.career_history]
            if not all_companies:
                return 0.5
            consulting_count = sum(
                1 for cn in all_companies
                if any(cc in cn for cc in CONSULTING_COMPANIES)
            )
            product_ratio = 1.0 - (consulting_count / len(all_companies))
            return 0.4 + (product_ratio * 0.6)
        return 0.5

    def score_career_growth(self, c: CandidateProfile) -> float:
        if not c.career_history:
            return 0.3

        LEVEL_KEYWORDS = {
            "intern": 0, "trainee": 0, "junior": 1, "associate": 1,
            "engineer": 2, "developer": 2, "analyst": 2,
            "senior": 3, "lead": 4, "staff": 4, "principal": 5,
            "architect": 5, "manager": 3, "director": 6, "vp": 7, "head": 6,
        }

        def title_level(title: str) -> int:
            tl = title.lower()
            best = 2
            for kw, lvl in LEVEL_KEYWORDS.items():
                if kw in tl:
                    best = max(best, lvl)
            return best

        levels = [title_level(job.get("title", "")) for job in c.career_history]

        if len(levels) < 2:
            return 0.5

        deltas = [levels[i+1] - levels[i] for i in range(len(levels)-1)]
        positive = sum(1 for d in deltas if d > 0)
        stagnant = sum(1 for d in deltas if d == 0)
        regression = sum(1 for d in deltas if d < 0)

        score = 0.5
        score += positive * 0.15
        score -= regression * 0.10
        score -= stagnant * 0.03
        return max(0.0, min(1.0, score))

    def score_location(self, c: CandidateProfile) -> float:
        loc_lower = c.location.lower()
        if any(pl in loc_lower for pl in PREFERRED_LOCATIONS):
            return 1.0
        if "remote" in loc_lower:
            return 0.8
        return 0.3

    def score_education(self, c: CandidateProfile) -> float:
        tier = c.education.get("tier", "Tier 3")
        uni_lower = c.education.get("university", "").lower()
        degree = c.education.get("degree", "").lower()

        tier_map = {"Tier 1": 1.0, "Tier 2": 0.7, "Tier 3": 0.4}
        base = tier_map.get(tier, 0.4)

        if any(kw in degree for kw in ["m.tech", "m.s.", "phd", "ms"]):
            base = min(base + 0.1, 1.0)

        if any(t1 in uni_lower for t1 in TIER1_UNIVERSITIES):
            base = max(base, 0.9)

        return base

    def score_title_quality(self, c: CandidateProfile) -> float:
        title_lower = c.current_title.lower()
        if any(nt in title_lower for nt in NEGATIVE_TITLE_TERMS):
            return 0.0
        if any(st in title_lower for st in STRONG_TITLE_TERMS):
            return 1.0
        return 0.5

    def score_skill_coverage(self, c: CandidateProfile) -> float:
        if not c.skill_names:
            return 0.0
        hit = sum(1 for rs in self.jd.required_skills if any(rs in sn for sn in c.skill_names))
        return min(hit / len(self.jd.required_skills), 1.0)

    def score_skill_depth(self, c: CandidateProfile) -> float:
        if not c.skills:
            return 0.0
        total_depth = 0.0
        for s in c.skills:
            prof = s.get("proficiency", "intermediate").lower()
            weight = PROFICIENCY_WEIGHTS.get(prof, 0.5)
            total_depth += weight
        return min(total_depth / len(c.skills), 1.0)

    def score_skill_duration(self, c: CandidateProfile) -> float:
        if not c.skills:
            return 0.0
        durations = [s.get("duration_months", 0) or s.get("years", 0) * 12 for s in c.skills]
        avg_duration = sum(durations) / len(durations)
        return min(avg_duration / 36.0, 1.0)

    def score_skill_endorsement(self, c: CandidateProfile) -> float:
        if not c.skills:
            return 0.0
        endorsements = [s.get("endorsements", 0) for s in c.skills]
        avg_endorse = sum(endorsements) / len(endorsements)
        return min(avg_endorse / 50.0, 1.0)

    def score_leadership(self, c: CandidateProfile) -> float:
        title_lower = c.current_title.lower()
        title_leadership = any(lt in title_lower for lt in LEADERSHIP_TITLE_TERMS)

        career_leadership = 0
        for job in c.career_history:
            jt = job.get("title", "").lower()
            if any(lt in jt for lt in LEADERSHIP_TITLE_TERMS):
                career_leadership += 1

        score = 0.0
        if title_leadership:
            score += 0.5
        if career_leadership > 0:
            score += min(career_leadership * 0.15, 0.5)
        return min(score, 1.0)

    def score_job_stability(self, c: CandidateProfile) -> float:
        sig = c.behavioral_signals
        tenure = sig.get("avg_tenure_years", 0.0)
        job_switches = len(c.career_history)
        exp = c.total_experience_years

        if exp <= 0 or job_switches <= 0:
            return 0.5

        avg_tenure = exp / job_switches
        if 1.5 <= avg_tenure <= 4.0:
            return 1.0
        elif avg_tenure < 0.5:
            return 0.2
        elif avg_tenure > 6.0:
            return 0.5
        elif avg_tenure < 1.0:
            return 0.4
        else:
            return 0.7

    def score_startup_mindset(self, c: CandidateProfile) -> float:
        score = 0.0
        if c.has_product_company:
            score += 0.3
        if not c.consulting_only:
            score += 0.2
        if c.has_retrieval_experience:
            score += 0.2
        sig = c.behavioral_signals
        if sig.get("open_source_contributions", 0) > 10:
            score += 0.15
        if sig.get("hackathon_participations", 0) > 2:
            score += 0.15
        return min(score, 1.0)

    def analyze(self, c: CandidateProfile) -> dict:
        return {
            "experience_score": self.score_experience(c),
            "retrieval_score": self.score_retrieval_expertise(c),
            "product_company_score": self.score_product_company(c),
            "career_growth_score": self.score_career_growth(c),
            "location_score": self.score_location(c),
            "education_score": self.score_education(c),
            "title_quality_score": self.score_title_quality(c),
            "skill_coverage_score": self.score_skill_coverage(c),
            "skill_depth_score": self.score_skill_depth(c),
            "skill_duration_score": self.score_skill_duration(c),
            "skill_endorsement_score": self.score_skill_endorsement(c),
            "leadership_score": self.score_leadership(c),
            "job_stability_score": self.score_job_stability(c),
            "startup_mindset_score": self.score_startup_mindset(c),
        }
