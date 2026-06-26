from __future__ import annotations
from src.parser import CandidateProfile


class BehavioralEngine:
    def score_behavioral(self, c: CandidateProfile) -> float:
        sig = c.behavioral_signals
        if not sig:
            return 0.5

        weights = {
            "open_to_work_flag": 0.10,
            "recruiter_response_rate": 0.08,
            "last_active_days_ago": 0.08,
            "github_activity_score": 0.08,
            "saved_by_recruiters_30d": 0.06,
            "interview_completion_rate": 0.06,
            "offer_acceptance_rate": 0.04,
            "notice_period_days": 0.08,
            "profile_completeness_score": 0.05,
            "response_time_hours": 0.05,
            "applied_jobs_last_30d": 0.03,
            "profile_views_30d": 0.03,
            "search_appearance_30d": 0.04,
            "willing_to_relocate": 0.04,
            "endorsements_received": 0.03,
            "skill_endorsement_velocity": 0.03,
            "recommendation_count": 0.03,
            "publication_count": 0.02,
            "open_source_contributions": 0.03,
            "hackathon_participations": 0.02,
            "certification_count": 0.02,
            "avg_tenure_years": 0.02,
            "job_switch_frequency": 0.02,
        }

        total_weight = sum(weights.values())
        score = 0.0

        if sig.get("open_to_work_flag", False):
            score += 1.0 * weights["open_to_work_flag"]

        score += min(sig.get("recruiter_response_rate", 0.0), 1.0) * weights["recruiter_response_rate"]

        lada = sig.get("last_active_days_ago", 999)
        if lada <= 1:
            lada_score = 1.0
        elif lada >= 30:
            lada_score = 0.0
        else:
            lada_score = 1.0 - (lada / 30)
        score += lada_score * weights["last_active_days_ago"]

        gh = min(sig.get("github_activity_score", 0), 100)
        score += (gh / 100.0) * weights["github_activity_score"]

        saved = min(sig.get("saved_by_recruiters_30d", 0), 30)
        score += (saved / 30.0) * weights["saved_by_recruiters_30d"]

        score += min(sig.get("interview_completion_rate", 0.0), 1.0) * weights["interview_completion_rate"]

        score += min(sig.get("offer_acceptance_rate", 0.0), 1.0) * weights["offer_acceptance_rate"]

        npd = sig.get("notice_period_days", 90)
        if npd <= 0:
            np_score = 1.0
        elif npd >= 90:
            np_score = 0.0
        else:
            np_score = 1.0 - (npd / 90)
        score += np_score * weights["notice_period_days"]

        score += min(sig.get("profile_completeness_score", 0.0), 1.0) * weights["profile_completeness_score"]

        rth = sig.get("response_time_hours", 72)
        if rth <= 1:
            rth_score = 1.0
        elif rth >= 168:
            rth_score = 0.0
        else:
            rth_score = 1.0 - (rth / 168)
        score += rth_score * weights["response_time_hours"]

        applied = min(sig.get("applied_jobs_last_30d", 0), 20)
        score += (applied / 20.0) * weights["applied_jobs_last_30d"]

        views = min(sig.get("profile_views_30d", 0), 300)
        score += (views / 300.0) * weights["profile_views_30d"]

        search_app = min(sig.get("search_appearance_30d", 0), 300)
        score += (search_app / 300.0) * weights["search_appearance_30d"]

        if sig.get("willing_to_relocate", False):
            score += 1.0 * weights["willing_to_relocate"]

        endorse_rec = min(sig.get("endorsements_received", 0), 100)
        score += (endorse_rec / 100.0) * weights["endorsements_received"]

        sev = min(sig.get("skill_endorsement_velocity", 0.0), 5.0)
        score += (sev / 5.0) * weights["skill_endorsement_velocity"]

        rc = min(sig.get("recommendation_count", 0), 15)
        score += (rc / 15.0) * weights["recommendation_count"]

        pc = min(sig.get("publication_count", 0), 10)
        score += (pc / 10.0) * weights["publication_count"]

        osc = min(sig.get("open_source_contributions", 0), 80)
        score += (osc / 80.0) * weights["open_source_contributions"]

        hp = min(sig.get("hackathon_participations", 0), 10)
        score += (hp / 10.0) * weights["hackathon_participations"]

        cc = min(sig.get("certification_count", 0), 8)
        score += (cc / 8.0) * weights["certification_count"]

        tenure = sig.get("avg_tenure_years", 0.0)
        if 1.5 <= tenure <= 4.0:
            tenure_score = 1.0
        elif tenure < 1.0:
            tenure_score = 0.3
        elif tenure > 5.0:
            tenure_score = 0.5
        else:
            tenure_score = 0.7
        score += tenure_score * weights["avg_tenure_years"]

        jf = sig.get("job_switch_frequency", 0.0)
        if 0.3 <= jf <= 0.8:
            jf_score = 1.0
        elif jf < 0.2:
            jf_score = 0.3
        elif jf > 1.0:
            jf_score = 0.4
        else:
            jf_score = 0.7
        score += jf_score * weights["job_switch_frequency"]

        return max(0.0, min(1.0, score / total_weight))
