from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


JD_TEXT = """
Role: Senior AI Engineer – Founding Team

We are building the next-generation intelligent talent discovery platform.
We need a Senior AI Engineer who can architect and ship retrieval systems,
ranking pipelines, and semantic search infrastructure from scratch.

Required:
- 5-9 years of experience
- Embeddings and vector representations
- Retrieval systems (BM25, dense retrieval, hybrid)
- Ranking systems and Learning to Rank
- Search infrastructure (Elasticsearch, FAISS, Milvus, Pinecone, Qdrant, Weaviate)
- Python (expert level)
- Evaluation frameworks (NDCG, MAP, MRR)
- Production ML systems at scale

Nice to Have:
- Fine-tuning (LoRA, QLoRA)
- HRTech experience
- Distributed systems
- Recommendation systems
- RAG pipelines

We value:
- Product mindset and fast shipping culture
- Startup experience
- Real production deployments
- Ownership mentality

We don't want:
- Pure research profiles (no production experience)
- LangChain-only engineers
- Consulting-only careers
- Framework enthusiasts without depth
- Non-NLP AI specialists (CV-only, RL-only)

Location: Bangalore, Pune, Hyderabad, Delhi NCR, Noida, Mumbai (or Remote)
"""

REQUIRED_SKILLS = [
    "embeddings", "retrieval", "retrieval systems", "ranking", "ranking systems",
    "search", "vector databases", "faiss", "elasticsearch", "milvus",
    "pinecone", "qdrant", "weaviate", "python", "ndcg", "map", "mrr",
    "evaluation frameworks", "production ml", "bm25", "semantic search",
    "dense retrieval", "information retrieval",
]

PREFERRED_SKILLS = [
    "fine-tuning", "lora", "qlora", "learning to rank", "hrtech",
    "distributed systems", "recommendation systems", "rag",
    "sentence transformers", "transformers", "nlp", "pytorch",
]

NEGATIVE_SIGNALS = [
    "pure research", "langchain only", "consulting only",
    "framework enthusiast", "computer vision only", "reinforcement learning only",
    "no production", "marketing", "hr manager", "operations manager",
    "customer success", "accountant", "sales", "content writer",
]

PREFERRED_LOCATIONS = [
    "pune", "noida", "delhi ncr", "delhi", "mumbai", "hyderabad",
    "bangalore", "bengaluru", "gurgaon", "gurugram",
]

RETRIEVAL_SIGNALS = [
    "retrieval", "search", "ranking", "recommendation", "semantic search",
    "vector search", "rag", "bm25", "elasticsearch", "faiss", "milvus",
    "pinecone", "qdrant", "weaviate", "ndcg", "map", "mrr",
    "information retrieval", "learning to rank", "dense retrieval",
    "hybrid search", "re-ranking", "reranking",
]

CONSULTING_COMPANIES = {
    "tcs", "infosys", "wipro", "cognizant", "mindtree", "hcl",
    "tech mahindra", "mphasis", "hexaware", "capgemini",
    "accenture", "ibm consulting", "deloitte", "ey", "kpmg", "pwc",
}


@dataclass
class JDProfile:
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    startup_signals: list[str] = field(default_factory=list)
    experience_min: int = 5
    experience_max: int = 9
    preferred_locations: list[str] = field(default_factory=list)
    negative_signals: list[str] = field(default_factory=list)
    retrieval_signals: list[str] = field(default_factory=list)
    full_text: str = ""


@dataclass
class CandidateProfile:
    id: str = ""
    name: str = ""
    summary: str = ""
    current_title: str = ""
    current_company: str = ""
    total_experience_years: float = 0.0
    location: str = ""
    skills: list[dict] = field(default_factory=list)
    skill_names: list[str] = field(default_factory=list)
    career_history: list[dict] = field(default_factory=list)
    education: dict = field(default_factory=dict)
    behavioral_signals: dict = field(default_factory=dict)
    is_honeypot: bool = False
    honeypot_type: str | None = None

    all_text: str = ""
    career_text: str = ""
    has_retrieval_experience: bool = False
    has_product_company: bool = False
    consulting_only: bool = False


def parse_jd() -> JDProfile:
    return JDProfile(
        required_skills=REQUIRED_SKILLS,
        preferred_skills=PREFERRED_SKILLS,
        startup_signals=[
            "product mindset", "fast shipping", "startup experience",
            "production deployments", "ownership mentality",
        ],
        experience_min=5,
        experience_max=9,
        preferred_locations=PREFERRED_LOCATIONS,
        negative_signals=NEGATIVE_SIGNALS,
        retrieval_signals=RETRIEVAL_SIGNALS,
        full_text=JD_TEXT,
    )


def _adapt_real_schema(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert real dataset schema (candidate_schema.json / JSONL) to internal format."""

    profile = raw.get("profile", {})

    adapted: dict[str, Any] = {
        "id": raw.get("candidate_id") or raw.get("id", ""),
        "name": profile.get("anonymized_name") or raw.get("name", ""),
        "summary": profile.get("summary") or raw.get("summary", ""),
        "current_title": profile.get("current_title") or raw.get("current_title", ""),
        "current_company": profile.get("current_company") or raw.get("current_company", ""),
        "total_experience_years": float(profile.get("years_of_experience", 0) or raw.get("total_experience_years", 0)),
        "location": profile.get("location") or raw.get("location", ""),
        "is_honeypot": raw.get("is_honeypot", False),
        "honeypot_type": raw.get("honeypot_type"),
    }

    redrob = raw.get("redrob_signals", {})
    adapted["behavioral_signals"] = {
        "open_to_work_flag": redrob.get("open_to_work_flag", False),
        "recruiter_response_rate": redrob.get("recruiter_response_rate", 0.5),
        "last_active_days_ago": _days_since(redrob.get("last_active_date", "")),
        "github_activity_score": redrob.get("github_activity_score", 0),
        "saved_by_recruiters_30d": redrob.get("saved_by_recruiters_30d", 0),
        "interview_completion_rate": redrob.get("interview_completion_rate", 0.5),
        "offer_acceptance_rate": redrob.get("offer_acceptance_rate", 0.5),
        "notice_period_days": redrob.get("notice_period_days", 90),
        "profile_completeness_score": redrob.get("profile_completeness_score", 50) / 100.0,
        "response_time_hours": redrob.get("avg_response_time_hours", 72),
        "applied_jobs_last_30d": redrob.get("applications_submitted_30d", 0),
        "profile_views_30d": redrob.get("profile_views_received_30d", 0),
        "connection_count": redrob.get("connection_count", 0),
        "skill_endorsement_velocity": redrob.get("endorsements_received", 0) / 10.0,
        "search_appearance_30d": redrob.get("search_appearance_30d", 0),
        "willing_to_relocate": redrob.get("willing_to_relocate", False),
        "endorsements_received": redrob.get("endorsements_received", 0),
        "recommendation_count": 0,
        "publication_count": 0,
        "open_source_contributions": max(0, int(redrob.get("github_activity_score", 0) * 0.8)),
        "hackathon_participations": 0,
        "certification_count": 0,
        "avg_tenure_years": 0.0,
        "job_switch_frequency": 0.0,
    }

    salary_range = redrob.get("expected_salary_range_inr_lpa", {})
    if isinstance(salary_range, dict):
        adapted["behavioral_signals"]["salary_expectation_min"] = salary_range.get("min", 0) * 100000
        adapted["behavioral_signals"]["salary_expectation_max"] = salary_range.get("max", 0) * 100000
    else:
        adapted["behavioral_signals"]["salary_expectation_min"] = 0
        adapted["behavioral_signals"]["salary_expectation_max"] = 0

    raw_skills = raw.get("skills", [])
    adapted["skills"] = []
    for s in raw_skills:
        adapted["skills"].append({
            "name": s.get("name", ""),
            "proficiency": s.get("proficiency", "intermediate"),
            "endorsements": s.get("endorsements", 0),
            "years": round(s.get("duration_months", 0) / 12.0, 1),
            "duration_months": s.get("duration_months", 0),
        })

    raw_career = raw.get("career_history", [])
    adapted["career_history"] = []
    for job in raw_career:
        start_y = _extract_year(job.get("start_date", ""))
        end_raw = job.get("end_date", "")
        end_y = _extract_year(end_raw) if end_raw else 2026
        adapted["career_history"].append({
            "company": job.get("company", ""),
            "title": job.get("title", ""),
            "description": job.get("description", ""),
            "start_year": start_y,
            "end_year": end_y,
            "duration_years": round(job.get("duration_months", 0) / 12.0, 1),
        })

    raw_edu = raw.get("education", [])
    if isinstance(raw_edu, dict):
        adapted["education"] = {
            "degree": raw_edu.get("degree", ""),
            "field": raw_edu.get("field", ""),
            "university": raw_edu.get("university", ""),
            "tier": raw_edu.get("tier", "Tier 3"),
            "year": raw_edu.get("year", 0),
        }
    elif isinstance(raw_edu, list) and raw_edu:
        top = raw_edu[0]
        tier_raw = top.get("tier", "unknown")
        adapted["education"] = {
            "degree": top.get("degree", ""),
            "field": top.get("field_of_study", ""),
            "university": top.get("institution", ""),
            "tier": tier_raw.replace("tier_", "Tier ").title() if isinstance(tier_raw, str) else "Tier 3",
            "year": top.get("end_year", 0),
        }
    else:
        adapted["education"] = {}

    return adapted


def _days_since(date_str: str) -> int:
    if not date_str:
        return 999
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return (datetime.now() - dt).days
    except (ValueError, TypeError):
        return 999


def _extract_year(date_str: str) -> int:
    if not date_str:
        return 2020
    try:
        return int(date_str.split("-")[0])
    except (ValueError, IndexError):
        return 2020


def parse_candidate(raw: dict[str, Any]) -> CandidateProfile:
    if "candidate_id" in raw or "profile" in raw:
        raw = _adapt_real_schema(raw)

    c = CandidateProfile()
    c.id = raw.get("id", "")
    c.name = raw.get("name", "")
    c.summary = raw.get("summary", "")
    c.current_title = raw.get("current_title", "")
    c.current_company = raw.get("current_company", "")
    c.total_experience_years = float(raw.get("total_experience_years", 0))
    c.location = raw.get("location", "")
    c.skills = raw.get("skills", [])
    c.skill_names = [s["name"].lower() for s in c.skills]
    c.career_history = raw.get("career_history", [])
    c.education = raw.get("education", {})
    c.behavioral_signals = raw.get("behavioral_signals", {})
    c.is_honeypot = raw.get("is_honeypot", False)
    c.honeypot_type = raw.get("honeypot_type")

    career_pieces = []
    for job in c.career_history:
        career_pieces.append(
            f"{job.get('title', '')} at {job.get('company', '')}: {job.get('description', '')}"
        )
    c.career_text = " ".join(career_pieces)

    skill_text = " ".join(s["name"] for s in c.skills)
    c.all_text = f"{c.summary} {c.current_title} {skill_text} {c.career_text}"

    all_lower = c.all_text.lower()
    c.has_retrieval_experience = any(term in all_lower for term in RETRIEVAL_SIGNALS)

    company_names_lower = [
        job.get("company", "").lower() for job in c.career_history
    ] + [c.current_company.lower()]

    consulting_count = sum(
        1 for cn in company_names_lower
        if any(cc in cn for cc in CONSULTING_COMPANIES)
    )
    product_count = len(company_names_lower) - consulting_count

    c.has_product_company = product_count > 0
    c.consulting_only = (consulting_count == len(company_names_lower) and len(company_names_lower) > 0)

    return c
