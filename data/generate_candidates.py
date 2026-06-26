"""
TalentForge AI – Synthetic Candidate Data Generator
Generates 500 realistic candidate profiles for the Redrob hackathon challenge.
Includes strong matches, weak matches, and honeypot candidates.
"""

import json
import os
import random
import uuid
from datetime import datetime, timedelta

random.seed(42)

# ── Pools ──────────────────────────────────────────────────────────────────────

STRONG_AI_TITLES = [
    "Senior AI Engineer", "ML Engineer", "Search Engineer",
    "Retrieval Engineer", "NLP Engineer", "Ranking Engineer",
    "Recommendation Systems Engineer", "Applied ML Engineer",
    "Senior NLP Scientist", "AI Platform Engineer",
    "Senior Machine Learning Engineer", "Search Infrastructure Engineer",
    "Vector Search Engineer", "AI Infrastructure Engineer",
]

WEAK_TITLES = [
    "Marketing Manager", "HR Business Partner", "Operations Manager",
    "Customer Success Manager", "Account Executive", "Financial Analyst",
    "Business Development Manager", "Content Writer", "Project Manager",
    "UX Designer", "Scrum Master", "Data Entry Specialist",
    "Accountant", "Recruiter", "Sales Manager",
]

PRODUCT_COMPANIES = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple", "Flipkart",
    "Swiggy", "Razorpay", "CRED", "Zepto", "Meesho", "PhonePe",
    "Paytm", "Zomato", "Ola", "Freshworks", "Zoho", "Postman",
    "BrowserStack", "Hasura", "Setu", "Sarvam AI", "Krutrim",
    "Nixtla", "Unacademy", "ShareChat", "Dukaan", "Cashfree",
]

CONSULTING_COMPANIES = [
    "TCS", "Infosys", "Wipro", "Cognizant", "Mindtree",
    "HCL Technologies", "Tech Mahindra", "Mphasis", "Hexaware",
    "Capgemini", "Accenture", "IBM Consulting", "Deloitte Tech",
]

UNIVERSITIES = [
    ("IIT Bombay", "Tier 1"), ("IIT Delhi", "Tier 1"),
    ("IIT Madras", "Tier 1"), ("IIT Kharagpur", "Tier 1"),
    ("IISc Bangalore", "Tier 1"), ("BITS Pilani", "Tier 1"),
    ("NIT Trichy", "Tier 2"), ("NIT Warangal", "Tier 2"),
    ("VIT Vellore", "Tier 2"), ("SRM University", "Tier 3"),
    ("Pune University", "Tier 2"), ("Delhi University", "Tier 2"),
    ("IIIT Hyderabad", "Tier 1"), ("IIIT Bangalore", "Tier 1"),
    ("Manipal University", "Tier 2"),
]

LOCATIONS = [
    "Bangalore", "Pune", "Mumbai", "Hyderabad", "Delhi NCR",
    "Noida", "Chennai", "Kolkata", "Gurgaon", "Ahmedabad",
    "Remote", "Singapore", "San Francisco, USA",
]

STRONG_SKILLS = [
    "Embeddings", "Retrieval Systems", "Vector Databases", "FAISS",
    "Elasticsearch", "BM25", "Semantic Search", "Python", "PyTorch",
    "Transformers", "Sentence Transformers", "RAG", "Ranking Systems",
    "NDCG", "MAP", "MRR", "Fine-Tuning", "LoRA", "QLoRA",
    "Pinecone", "Qdrant", "Weaviate", "Milvus", "LLMs",
    "NLP", "Information Retrieval", "Learning to Rank",
    "Recommendation Systems", "A/B Testing", "MLflow",
    "FastAPI", "Docker", "Kubernetes", "Distributed Systems",
]

GENERIC_SKILLS = [
    "Python", "Machine Learning", "TensorFlow", "Keras", "SQL",
    "Data Analysis", "Pandas", "NumPy", "Scikit-learn",
    "LangChain", "OpenAI API", "ChatGPT", "Prompt Engineering",
    "Jupyter Notebook", "GitHub", "REST APIs",
]

WEAK_SKILLS = [
    "Microsoft Excel", "PowerPoint", "Communication", "Leadership",
    "Project Management", "Salesforce", "HubSpot", "Google Analytics",
    "Content Marketing", "SEO", "Social Media", "Budget Management",
    "Stakeholder Management", "JIRA", "Confluence",
]

RETRIEVAL_TERMS = [
    "retrieval", "search", "ranking", "recommendation", "semantic search",
    "vector search", "RAG", "BM25", "Elasticsearch", "FAISS", "Milvus",
    "Pinecone", "Qdrant", "Weaviate", "NDCG", "MAP", "MRR",
    "information retrieval", "learning to rank",
]

SUMMARIES_STRONG = [
    "Senior AI engineer with 7 years building production retrieval systems. Deep expertise in vector search, BM25 hybrid ranking, and NDCG-driven evaluation frameworks. Shipped semantic search at scale serving 50M+ queries/day.",
    "ML engineer specializing in ranking and recommendation systems. Led search infrastructure at a Series B fintech, cutting latency 40% and improving MRR by 22%. Strong product mindset, fast shipping culture.",
    "NLP/Search engineer with hands-on experience in Elasticsearch, FAISS, and embedding fine-tuning. Built RAG pipelines for enterprise knowledge retrieval. Contributed to open-source IR benchmarks.",
    "Retrieval systems engineer with startup DNA. 6 years building semantic search and recommendation engines. Proficient with Sentence Transformers, Pinecone, and production LLM integrations.",
    "Applied ML engineer focused on information retrieval and LLM-based ranking. 5+ years shipping models into production. Experience with LoRA fine-tuning, custom evaluation pipelines (NDCG/MAP), and distributed inference.",
    "Search platform engineer who has led teams building enterprise search at product companies. Deep knowledge of BM25, dense retrieval, and hybrid re-ranking. Startup experience at two YC-backed companies.",
]

SUMMARIES_WEAK = [
    "Experienced marketing professional with a passion for data-driven campaigns. Familiar with AI tools and leveraging ChatGPT for content generation.",
    "Results-oriented HR business partner. Used machine learning concepts to streamline talent acquisition. Passionate about the future of AI in HR.",
    "Financial analyst with strong Excel skills. Recently completed an online ML course and exploring data science opportunities.",
    "Operations manager with experience in process optimization. Knowledge of Python for automation tasks and basic data analysis.",
    "Customer success manager with 8 years in SaaS. Experience with AI-driven CRM tools and automation platforms.",
]


def random_date(start_year=2015, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def generate_career_history(profile_type, total_exp_years):
    history = []
    current_year = 2024
    years_left = total_exp_years

    if profile_type == "strong":
        title_progression = [
            ("Software Engineer", PRODUCT_COMPANIES),
            ("ML Engineer", PRODUCT_COMPANIES),
            ("Senior ML Engineer", PRODUCT_COMPANIES),
            ("Senior AI Engineer", PRODUCT_COMPANIES),
        ]
    elif profile_type == "consulting":
        title_progression = [
            ("Associate Engineer", CONSULTING_COMPANIES),
            ("Software Engineer", CONSULTING_COMPANIES),
            ("Senior Engineer", CONSULTING_COMPANIES),
        ]
    else:
        title_progression = [
            ("Analyst", WEAK_TITLES[:5]),
            ("Manager", WEAK_TITLES[:5]),
        ]

    for title, company_pool in reversed(title_progression[:min(3, len(title_progression))]):
        if years_left <= 0:
            break
        duration = random.randint(1, min(3, years_left))
        end_year = current_year
        start_year = end_year - duration
        company = random.choice(company_pool)

        if profile_type == "strong":
            desc = random.choice([
                f"Built and deployed production-grade retrieval systems using FAISS and Elasticsearch. Improved NDCG@10 by 18%.",
                f"Led semantic search infrastructure serving {random.randint(1,50)}M+ daily queries. Implemented BM25 + dense retrieval hybrid pipeline.",
                f"Developed RAG pipeline for enterprise knowledge base. Fine-tuned Sentence Transformers on domain-specific data. Reduced hallucination rate by 35%.",
                f"Owned ranking model training and evaluation. Implemented Learning-to-Rank with pairwise loss. A/B tested ranking strategies.",
                f"Built recommendation engine using collaborative filtering + embedding-based retrieval. Improved click-through rate by 24%.",
            ])
        elif profile_type == "consulting":
            desc = f"Delivered {random.choice(['data analytics', 'ML pipeline', 'ETL automation'])} projects for enterprise clients."
        else:
            desc = f"Managed {random.choice(['marketing campaigns', 'HR operations', 'customer accounts', 'financial reporting'])} for the organization."

        history.append({
            "company": company,
            "title": title,
            "description": desc,
            "start_year": start_year,
            "end_year": end_year,
            "duration_years": duration,
        })
        current_year = start_year
        years_left -= duration

    return list(reversed(history))


def generate_skills(profile_type, n=15):
    if profile_type == "strong":
        primary = random.sample(STRONG_SKILLS, min(10, n - 5))
        secondary = random.sample(GENERIC_SKILLS, 5)
        skills = primary + secondary
    elif profile_type == "generic_ai":
        skills = random.sample(GENERIC_SKILLS, min(n, len(GENERIC_SKILLS)))
    else:
        skills = random.sample(WEAK_SKILLS + GENERIC_SKILLS[:5], min(n, 15))

    result = []
    for s in skills[:n]:
        result.append({
            "name": s,
            "proficiency": random.choice(["Expert", "Advanced", "Intermediate", "Beginner"]),
            "years": round(random.uniform(0.5, 6), 1),
            "endorsements": random.randint(0, 150),
        })
    return result


def generate_behavioral_signals(engagement_level="high"):
    base = {
        "open_to_work_flag": False,
        "recruiter_response_rate": 0.0,
        "last_active_days_ago": 999,
        "github_activity_score": 0,
        "saved_by_recruiters_30d": 0,
        "interview_completion_rate": 0.0,
        "offer_acceptance_rate": 0.0,
        "notice_period_days": 90,
        "profile_completeness_score": 0.0,
        "response_time_hours": 72,
        "applied_jobs_last_30d": 0,
        "profile_views_30d": 0,
        "connection_growth_rate": 0.0,
        "skill_endorsement_velocity": 0.0,
        "recommendation_count": 0,
        "publication_count": 0,
        "open_source_contributions": 0,
        "hackathon_participations": 0,
        "certification_count": 0,
        "avg_tenure_years": 0.0,
        "job_switch_frequency": 0.0,
        "salary_expectation_min": 0,
        "salary_expectation_max": 0,
    }

    if engagement_level == "high":
        base.update({
            "open_to_work_flag": random.choice([True, True, False]),
            "recruiter_response_rate": round(random.uniform(0.7, 1.0), 2),
            "last_active_days_ago": random.randint(0, 7),
            "github_activity_score": random.randint(60, 100),
            "saved_by_recruiters_30d": random.randint(5, 30),
            "interview_completion_rate": round(random.uniform(0.75, 1.0), 2),
            "offer_acceptance_rate": round(random.uniform(0.5, 1.0), 2),
            "notice_period_days": random.choice([0, 15, 30, 30, 60]),
            "profile_completeness_score": round(random.uniform(0.85, 1.0), 2),
            "response_time_hours": random.randint(1, 12),
            "applied_jobs_last_30d": random.randint(3, 20),
            "profile_views_30d": random.randint(50, 300),
            "connection_growth_rate": round(random.uniform(0.05, 0.2), 2),
            "skill_endorsement_velocity": round(random.uniform(1.0, 5.0), 1),
            "recommendation_count": random.randint(3, 15),
            "publication_count": random.randint(0, 8),
            "open_source_contributions": random.randint(5, 80),
            "hackathon_participations": random.randint(1, 10),
            "certification_count": random.randint(2, 8),
            "avg_tenure_years": round(random.uniform(1.5, 3.5), 1),
            "job_switch_frequency": round(random.uniform(0.3, 0.8), 2),
            "salary_expectation_min": random.randint(2000000, 3500000),
            "salary_expectation_max": random.randint(3500001, 6000000),
        })
    elif engagement_level == "medium":
        base.update({
            "open_to_work_flag": random.choice([True, False]),
            "recruiter_response_rate": round(random.uniform(0.4, 0.7), 2),
            "last_active_days_ago": random.randint(7, 30),
            "github_activity_score": random.randint(20, 60),
            "saved_by_recruiters_30d": random.randint(1, 10),
            "interview_completion_rate": round(random.uniform(0.5, 0.75), 2),
            "offer_acceptance_rate": round(random.uniform(0.3, 0.6), 2),
            "notice_period_days": random.choice([30, 60, 90]),
            "profile_completeness_score": round(random.uniform(0.6, 0.85), 2),
            "response_time_hours": random.randint(12, 48),
            "applied_jobs_last_30d": random.randint(0, 5),
            "profile_views_30d": random.randint(10, 80),
            "recommendation_count": random.randint(0, 5),
            "open_source_contributions": random.randint(0, 10),
            "certification_count": random.randint(0, 3),
            "avg_tenure_years": round(random.uniform(1.0, 4.0), 1),
            "salary_expectation_min": random.randint(1000000, 2000000),
            "salary_expectation_max": random.randint(2000001, 3500000),
        })
    else:  # low
        base.update({
            "open_to_work_flag": False,
            "recruiter_response_rate": round(random.uniform(0.0, 0.4), 2),
            "last_active_days_ago": random.randint(30, 365),
            "github_activity_score": random.randint(0, 20),
            "saved_by_recruiters_30d": random.randint(0, 2),
            "interview_completion_rate": round(random.uniform(0.0, 0.5), 2),
            "notice_period_days": random.choice([60, 90, 120]),
            "profile_completeness_score": round(random.uniform(0.3, 0.6), 2),
            "response_time_hours": random.randint(48, 168),
            "salary_expectation_min": random.randint(500000, 1200000),
            "salary_expectation_max": random.randint(1200001, 2500000),
        })

    return base


def generate_honeypot():
    """Generate clearly fake/suspicious candidate profiles."""
    honeypot_type = random.choice(["impossible_age", "skill_overflow", "contradictory", "salary_anomaly"])

    candidate = {
        "id": str(uuid.uuid4()),
        "name": f"Honeypot_{random.randint(1000,9999)}",
        "headline": "AI Expert | Machine Learning | Python | Retrieval Systems",
        "summary": "Expert in all AI domains with 15 years of experience in every technology ever invented.",
        "current_title": random.choice(STRONG_AI_TITLES),
        "current_company": random.choice(PRODUCT_COMPANIES),
        "total_experience_years": 0,
        "location": random.choice(LOCATIONS),
        "career_history": [],
        "skills": [],
        "education": {"degree": "B.Tech", "field": "Computer Science", "university": "IIT Bombay", "tier": "Tier 1", "year": 2022},
        "behavioral_signals": generate_behavioral_signals("medium"),
        "is_honeypot": True,
        "honeypot_type": honeypot_type,
    }

    if honeypot_type == "impossible_age":
        candidate["total_experience_years"] = 15
        candidate["education"]["year"] = 2020  # Graduated 2020, but has 15 yrs exp
        candidate["name"] = f"YoungExpert_{random.randint(100,999)}"
        candidate["career_history"] = generate_career_history("strong", 15)

    elif honeypot_type == "skill_overflow":
        candidate["total_experience_years"] = random.randint(5, 8)
        # 200+ skills is impossible
        candidate["skills"] = [{"name": f"Skill_{i}", "proficiency": "Expert", "years": 5, "endorsements": 99} for i in range(220)]

    elif honeypot_type == "contradictory":
        candidate["current_title"] = "Marketing Manager"
        candidate["summary"] = "Marketing professional with 8 years in brand management."
        candidate["skills"] = generate_skills("strong", 12)  # Strong AI skills but marketing title

    elif honeypot_type == "salary_anomaly":
        candidate["total_experience_years"] = random.randint(4, 8)
        sig = generate_behavioral_signals("high")
        sig["salary_expectation_min"] = 5000000
        sig["salary_expectation_max"] = 2000000  # min > max
        candidate["behavioral_signals"] = sig
        candidate["skills"] = generate_skills("strong", 12)
        candidate["career_history"] = generate_career_history("strong", candidate["total_experience_years"])

    return candidate


def generate_candidate(profile_type="strong", index=0):
    if profile_type == "strong":
        exp = random.randint(5, 9)
        title = random.choice(STRONG_AI_TITLES)
        company = random.choice(PRODUCT_COMPANIES)
        summary = random.choice(SUMMARIES_STRONG)
        engagement = "high"
        loc = random.choice(["Bangalore", "Pune", "Hyderabad", "Delhi NCR", "Noida", "Mumbai"])
        skills = generate_skills("strong", random.randint(12, 20))
        tier = random.choice(["Tier 1", "Tier 1", "Tier 2"])
    elif profile_type == "medium_ai":
        exp = random.randint(3, 6)
        title = random.choice(STRONG_AI_TITLES[:8])
        company = random.choice(PRODUCT_COMPANIES + CONSULTING_COMPANIES)
        summary = f"ML engineer with {exp} years experience in Python, TensorFlow, and various AI frameworks. Some experience with NLP and search."
        engagement = "medium"
        loc = random.choice(LOCATIONS)
        skills = generate_skills("generic_ai", random.randint(10, 15))
        tier = random.choice(["Tier 2", "Tier 2", "Tier 3"])
    elif profile_type == "consulting":
        exp = random.randint(4, 10)
        title = "Senior Software Engineer"
        company = random.choice(CONSULTING_COMPANIES)
        summary = f"Experienced software engineer at {company} with {exp} years in enterprise delivery. Some ML exposure."
        engagement = "medium"
        loc = random.choice(["Pune", "Bangalore", "Chennai", "Kolkata"])
        skills = generate_skills("generic_ai", 12)
        tier = random.choice(["Tier 2", "Tier 3"])
    else:  # weak
        exp = random.randint(3, 12)
        title = random.choice(WEAK_TITLES)
        company = random.choice(CONSULTING_COMPANIES + ["Startups Ltd", "Corp Inc"])
        summary = random.choice(SUMMARIES_WEAK)
        engagement = random.choice(["low", "medium"])
        loc = random.choice(LOCATIONS)
        skills = generate_skills("weak", random.randint(8, 15))
        tier = random.choice(["Tier 2", "Tier 3"])

    uni, _ = random.choice(UNIVERSITIES)
    edu_year = 2024 - exp - random.randint(0, 2)

    return {
        "id": str(uuid.uuid4()),
        "name": f"Candidate_{index:04d}",
        "headline": f"{title} | {random.choice(['AI', 'ML', 'Tech'])} | {company}",
        "summary": summary,
        "current_title": title,
        "current_company": company,
        "total_experience_years": exp,
        "location": loc,
        "career_history": generate_career_history(
            "strong" if profile_type == "strong" else ("consulting" if profile_type == "consulting" else "weak"),
            exp
        ),
        "skills": skills,
        "education": {
            "degree": random.choice(["B.Tech", "M.Tech", "M.S.", "B.E."]),
            "field": random.choice(["Computer Science", "Information Technology", "Electronics", "Data Science"]),
            "university": uni,
            "tier": tier,
            "year": edu_year,
        },
        "behavioral_signals": generate_behavioral_signals(engagement),
        "is_honeypot": False,
        "honeypot_type": None,
    }


def main():
    candidates = []
    idx = 0

    # Strong matches: ~150
    for _ in range(150):
        candidates.append(generate_candidate("strong", idx)); idx += 1

    # Medium AI: ~100
    for _ in range(100):
        candidates.append(generate_candidate("medium_ai", idx)); idx += 1

    # Consulting profiles: ~100
    for _ in range(100):
        candidates.append(generate_candidate("consulting", idx)); idx += 1

    # Weak/non-technical: ~120
    for _ in range(120):
        candidates.append(generate_candidate("weak", idx)); idx += 1

    # Honeypot candidates: ~30
    for _ in range(30):
        candidates.append(generate_honeypot()); idx += 1

    random.shuffle(candidates)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "candidates.json")
    with open(output_path, "w") as f:
        json.dump(candidates, f, indent=2, default=str)

    print(f"✅ Generated {len(candidates)} candidates → {output_path}")
    print(f"   Strong: 150 | Medium AI: 100 | Consulting: 100 | Weak: 120 | Honeypot: 30")


if __name__ == "__main__":
    main()