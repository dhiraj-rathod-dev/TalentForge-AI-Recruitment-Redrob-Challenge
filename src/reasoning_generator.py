from __future__ import annotations
from src.parser import CandidateProfile, RETRIEVAL_SIGNALS


class ReasoningGenerator:
    def generate(self, c: CandidateProfile, scores: dict) -> str:
        parts = []

        strength = self._get_rank_strength(c, scores)
        parts.append(strength)

        concern = self._get_concern(c, scores)
        if concern:
            parts.append(concern)

        behav = self._get_behavioral_signal(c)
        if behav:
            parts.append(behav)

        jd_ref = self._get_jd_requirement_reference(c, scores)
        if jd_ref:
            parts.append(jd_ref)

        return " ".join(parts)

    def _get_rank_strength(self, c: CandidateProfile, scores: dict) -> str:
        rank = scores.get("rank", 0)
        key_skills = [s["name"] for s in c.skills[:5]]
        key_companies = []
        for job in c.career_history[-3:]:
            if job.get("company") and job["company"] not in key_companies:
                key_companies.append(job["company"])

        exp_years = c.total_experience_years
        company_str = ", ".join(key_companies[:2]) if key_companies else c.current_company

        rank_prefix = f"Rank #{rank}: " if rank else ""

        if c.has_retrieval_experience:
            return (
                f"{rank_prefix}Strong match for retrieval-focused AI engineering role. "
                f"{exp_years:.0f} years at {company_str} building semantic search, "
                f"ranking, or retrieval systems with {', '.join(key_skills[:3])}."
            )
        elif "ai" in c.current_title.lower() or "ml" in c.current_title.lower() or "data" in c.current_title.lower():
            return (
                f"{rank_prefix}Relevant AI/ML profile with {exp_years:.0f} years of experience at {company_str}. "
                f"Skills include {', '.join(key_skills[:3])}."
            )
        else:
            return (
                f"{rank_prefix}Candidate with {exp_years:.0f} years at {company_str} as {c.current_title}. "
                f"Skilled in {', '.join(key_skills[:3])}."
            )

    def _get_jd_requirement_reference(self, c: CandidateProfile, scores: dict) -> str | None:
        refs = []
        exp = c.total_experience_years
        if 5 <= exp <= 9:
            refs.append(f"meets the 5-9 year experience requirement ({exp:.0f} yrs)")
        elif exp >= 5:
            refs.append(f"exceeds minimum experience ({exp:.0f} yrs vs 5 required)")

        if c.has_retrieval_experience:
            refs.append("demonstrates retrieval/ranking expertise required by the JD")

        skill_hits = scores.get("skill_coverage_score", 0)
        if skill_hits > 0.5:
            refs.append(f"covers {skill_hits:.0%} of required technical skills")

        title_lower = c.current_title.lower()
        if "python" in c.skill_names:
            refs.append("has the required expert-level Python")

        if not refs:
            return None

        return "JD fit: " + "; ".join(refs) + "."

    def _get_concern(self, c: CandidateProfile, scores: dict) -> str | None:
        concerns = []
        if c.consulting_only:
            concerns.append("Consulting-only background without product-company experience")

        if scores.get("retrieval_score", 0) < 0.2:
            concerns.append("Limited retrieval/ranking experience for this search-focused role")

        if scores.get("experience_score", 0) < 0.3:
            concerns.append(f"Experience level ({c.total_experience_years:.0f} years) is below the preferred range")

        if scores.get("location_score", 0) < 0.5:
            concerns.append(f"Located in {c.location}, outside preferred cities")

        if c.is_honeypot:
            concerns.append(f"Flagged as suspicious profile ({c.honeypot_type})")

        if not concerns:
            return None

        return concerns[0] + "."

    def _get_behavioral_signal(self, c: CandidateProfile) -> str | None:
        sig = c.behavioral_signals
        if not sig:
            return None

        signals = []
        if sig.get("open_to_work_flag", False):
            signals.append("actively looking and open to work")
        if sig.get("recruiter_response_rate", 0) > 0.8:
            signals.append(f"high recruiter engagement (response rate {sig['recruiter_response_rate']:.2f})")
        if sig.get("notice_period_days", 90) <= 15:
            signals.append(f"immediate availability (notice period {sig['notice_period_days']} days)")
        if sig.get("github_activity_score", 0) > 70:
            signals.append(f"strong open-source activity (github score {sig['github_activity_score']})")
        if sig.get("offer_acceptance_rate", 0) > 0.8:
            signals.append(f"high offer acceptance rate ({sig['offer_acceptance_rate']:.2f})")
        if sig.get("willing_to_relocate", False):
            signals.append("willing to relocate")
        if sig.get("search_appearance_30d", 0) > 100:
            signals.append(f"high recruiter search visibility ({sig['search_appearance_30d']} appearances in 30d)")

        if signals:
            return "Behavioral signals: " + "; ".join(signals) + "."

        inactive = sig.get("last_active_days_ago", 999)
        if inactive > 30:
            return f"Low engagement signal: last active {inactive} days ago."

        return None
