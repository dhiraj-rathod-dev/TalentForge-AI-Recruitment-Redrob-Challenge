# TalentForge AI — Q&A Store for PPT

## Problem Statement

**Recruiters go through hundreds of profiles and still often miss the right person. Not because the talent isn't there — but because keyword filters can't see what actually matters.**

**Build an AI system that ranks candidates the way a great recruiter would — not by matching keywords, but by actually understanding who fits the role.**

What your solution needs to do:
- Read a job description and actually understand what the role needs — not just pull out words.
- Look at the full picture — career history, skills, behavioral signals, platform activity — and figure out who genuinely fits.
- Deliver a shortlist that a recruiter can trust.

---

## Solution Overview

### What is your proposed solution?

- **TalentForge AI**: An intelligent candidate ranking system that reads the job description semantically, processes 100K candidate profiles holistically, and ranks them by who genuinely fits the role.
- **Hybrid retrieval engine**: SentenceTransformer (all-MiniLM-L6-v2) dense embeddings for semantic understanding + BM25 for keyword precision, with auto-fallback to sparse TF-IDF when dataset exceeds 10K candidates.
- **15-dimension weighted scoring** across semantic match (25%), experience fit (15%), behavioral signals (12%), retrieval expertise (10%), career growth, location, education, skill depth, leadership, stability, startup mindset, and more.
- **23 behavioral signals** from the Redrob platform: open_to_work_flag, recruiter_response_rate, github_activity_score, search_appearance_30d, willing_to_relocate, notice_period_days, applied_jobs_last_30d, profile_views_30d, interview_completion_rate, offer_acceptance_rate, and more.
- **7 honeypot detectors** catch fake/inflated profiles before ranking: IMPOSSIBLE_AGE, SKILL_OVERFLOW, CONTRADICTORY_PROFILE, SALARY_ANOMALY, TIMELINE_OVERLAP, BEHAVIORAL_ANOMALY, FAKE_EXPERIENCE.
- **Rank-aware reasoning** generated for every candidate with JD-specific references, so recruiters can trust and understand every ranking decision.

### What differentiates your approach from traditional candidate matching systems?

| Traditional ATS | TalentForge AI |
|----------------|----------------|
| Exact keyword matching only | Semantic embeddings understand "vector search" = "FAISS" |
| Binary pass/fail filters | Continuous 0–1 scoring across 15 weighted dimensions |
| Resume text only | 23 behavioral signals from platform activity |
| No fake profile detection | 7 honeypot types with graded penalties (0.2–0.5) |
| No explanations | Template-driven, rank-aware reasoning from actual scores |
| Ignores career trajectory | Career growth + job stability + leadership scoring |
| No skill depth analysis | Proficiency level, duration, and endorsement scoring |
| Single static ranking | Multi-dimensional weighted scoring with hybrid retrieval |

---

## JD Understanding & Candidate Evaluation

### What are the key requirements extracted from the JD?

The Senior AI Engineer — Founding Team JD requirements:

- **5–9 years experience** in ML/AI engineering
- **Expert-level Python**, Deep Learning, NLP, PyTorch/TensorFlow
- **Retrieval/ranking domain expertise**: BM25, FAISS, Vector Search, Elasticsearch, Information Retrieval, Learning to Rank
- **Product company experience** preferred (not consulting-only)
- **Startup mindset**: fast-paced, founding team, ownership, open source contributions
- **Preferred locations**: Bangalore, Pune, Hyderabad, Delhi NCR, Noida, Mumbai, Remote
- **Advanced degree** in CS/AI/ML preferred

### Which candidate signals are most important for determining relevance? How does your solution evaluate candidate fit beyond keyword matching?

**15 scoring dimensions ranked by weight:**

| Weight | Signal | Why It Matters |
|--------|--------|----------------|
| 25% | Semantic Match (Hybrid) | BM25 + embedding hybrid understands meaning beyond keywords |
| 15% | Experience | Years fit to the 5-9 range for a Senior role |
| 12% | Behavioral | 23 Redrob platform signals showing engagement and availability |
| 10% | Retrieval/Ranking | Domain expertise in search, vector DBs, evaluation metrics |
| 6% | Career Growth | Upward trajectory shows ambition and capability growth |
| 5% | Skill Depth | Proficiency level across skills (beginner→expert) |
| 4% | Location | Match to preferred cities |
| 4% | Education | Tier 1/2/3 university + advanced degrees |
| 3% | Skill Duration | Average months of skill usage |
| 3% | Leadership | Leadership/management title signals |
| 3% | Job Stability | Healthy tenure without job-hopping |
| 3% | Startup Mindset | Product company + open source + hackathons |
| 3% | Title Semantic | Current title similarity to JD requirements |
| 2% | Skill Endorsement | Peer endorsements validating skill claims |
| 2% | Exp Semantic | Career history similarity to JD |

**Beyond keyword matching:**
- Semantic embeddings capture meaning: "vector search engineer" ~ "FAISS specialist" ~ "retrieval engineer"
- Behavioral signals quantify real engagement — a candidate open to work with high GitHub activity and fast response rate is more likely to accept an offer
- Honeypot detection removes fake/inflated profiles that keyword matching would rank highly
- Multi-dimensional scoring produces a nuanced fit score, not a binary yes/no
- Career progression analysis checks if the candidate has grown, not just accumulated years

---

## Ranking Methodology

### How does your system retrieve, score, and rank candidates?

**Retrieval — Hybrid (Dense + BM25):**

```
Score = 0.7 × cos(embedding_JD, embedding_candidate) + 0.3 × BM25(JD, candidate)
```

- **Dense**: SentenceTransformer (all-MiniLM-L6-v2) → 384-dim embeddings → FAISS cosine similarity
- **Sparse**: BM25 (k1=1.5, b=0.75) for keyword-level precision
- **Auto-fallback**: TF-IDF (4000 features, sparse CSR matrix) for datasets >10K candidates to avoid OOM
- Additional similarities: title semantic similarity, experience semantic similarity

**Scoring — Weighted 15-dim formula:**

```
final_score = (0.25 × semantic_match) + (0.15 × experience) + (0.12 × behavioral)
            + (0.10 × retrieval) + (0.06 × career_growth) + (0.04 × location)
            + (0.04 × education) + (0.05 × skill_depth) + (0.03 × skill_duration)
            + (0.02 × skill_endorsement) + (0.03 × leadership) + (0.03 × job_stability)
            + (0.03 × startup_mindset) + (0.03 × title_semantic) + (0.02 × exp_semantic)
            - honeypot_penalty
```

**Ranking:**
- Sort by `final_score` descending
- Deterministic tie-breaking: equal scores sorted by `candidate_id` ascending
- Output: top 100 candidates with reasoning

### What models, algorithms, or heuristics are used?

| Component | Technology |
|-----------|-----------|
| Dense embeddings | SentenceTransformer (all-MiniLM-L6-v2) |
| Similarity search | FAISS (CPU, inner product / cosine) |
| Sparse retrieval | BM25 (custom implementation, k1=1.5, b=0.75) |
| Fallback | TF-IDF (scikit-learn, max_features=4000) |
| Scoring | Custom 15-dim weighted formula |
| Behavioral | 23-signal weighted combination |
| Honeypot | 7 rule-based detectors |
| Reasoning | Template-based (no LLM) |

### How are multiple candidate signals combined into a final ranking?

All 15 dimension scores are normalized to 0–1, multiplied by their respective weights, summed, then the honeypot penalty (0.0 to -0.5) is subtracted. Final score is clamped to [0, 1]. Candidates are sorted by final score descending with deterministic tie-breaking.

---

## Explainability & Data Validation

### How are ranking decisions explained?

- **Rank-aware prefix**: "Rank #1: Strong match for retrieval-focused AI engineering role..."
- **JD requirement references**: "meets the 5-9 year experience requirement (7 yrs)", "demonstrates retrieval/ranking expertise required by the JD", "has the required expert-level Python"
- **Behavioral signal mentions**: "actively looking and open to work", "high recruiter engagement (response rate 0.94)", "strong open-source activity (github score 94.8)", "high recruiter search visibility (1291 appearances in 30d)"
- **Concern flags**: "Consulting-only background", "outside preferred cities", "limited retrieval expertise"

### How do you prevent hallucinations or unsupported justifications?

- **No LLM used** in the ranking pipeline — zero hallucination risk
- All reasoning is **template-based** from actual computed scores and parsed data fields
- Every claim references a real data point or computed metric:
  - "meets the 5-9 year experience requirement" → from parsed `total_experience_years`
  - "response rate 0.94" → from `recruiter_response_rate` field
  - "GitHub score 94.8" → from `github_activity_score` field
- No generative text, no free-form explanations — fully deterministic and auditable

### How does your solution handle inconsistent, low-quality, or suspicious profiles?

**7 Honeypot Types with Graded Penalties:**

| Type | Detection Rule | Penalty |
|------|---------------|---------|
| IMPOSSIBLE_AGE | Graduation year + experience > current year (2026) | 0.5 |
| SKILL_OVERFLOW | >50 skills (suspicious), >100 (definite fake) | 0.3–0.5 |
| CONTRADICTORY_PROFILE | Non-technical title (e.g., "Fashion Designer") with 5+ advanced AI skills | 0.4 |
| SALARY_ANOMALY | Minimum salary > maximum salary | 0.3 |
| TIMELINE_OVERLAP | Overlapping employment dates in career history | 0.3 |
| BEHAVIORAL_ANOMALY | High GitHub score + high response rate but zero profile views/appearances | 0.3 |
| FAKE_EXPERIENCE | Inflated tenure (20+ years), impossible title+experience combos | 0.2–0.4 |

Honeypot penalties are subtracted from the final score, pushing fake profiles to the bottom of the ranking. The honeypot type is also recorded in the output for auditability.

---

## End-to-End Workflow

**Complete pipeline from JD input to ranked candidate output:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. LOAD                                                             │
│    Auto-detect JSON (array) or JSONL (line-by-line) format          │
│    Stream 100K candidates — never load full file into memory        │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. PARSE                                                            │
│    Schema adapter maps real Redrob fields→internal dataclass        │
│    candidate_id→id, profile.years_of_experience→total_exp,          │
│    redrob_signals→behavioral_signals, education array→dict,         │
│    start_date/end_date→start_year/end_year                          │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. EMBED                                                            │
│    Build TF-IDF matrix (sparse CSR, 4000 features) if >10K cands    │
│    OR SentenceTransformer embeddings + FAISS index if ≤10K          │
│    Build BM25 index for all candidates                               │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. MATCH                                                            │
│    Hybrid: 0.7×dense_sim + 0.3×bm25_sim                             │
│    Title semantic similarity (batch-encoded)                         │
│    Experience semantic similarity (batch-encoded)                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. SCORE                                                            │
│    15-dimension scoring engine (CandidateAnalyzer)                   │
│    23 behavioral signal scoring (BehavioralEngine)                   │
│    7-type honeypot detection (HoneypotDetector)                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. RANK                                                             │
│    final_score = Σ(weight_i × score_i) - honeypot_penalty           │
│    Sort descending by final_score                                   │
│    Tie-breaking: candidate_id ascending                             │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 7. EXPLAIN                                                          │
│    Template-based reasoning per candidate                           │
│    Rank prefix + JD references + behavioral signals + concerns      │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 8. EXPORT                                                           │
│    submission.csv (candidate_id,rank,score,reasoning)                │
│    top_100_candidates.csv (full 23-column breakdown)                │
│    all_candidates_scored.csv (complete dataset with scores)         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## System Architecture

```
                                  ┌─────────────────────┐
                                  │   candidates.jsonl  │
                                  │   (100K profiles)   │
                                  └──────────┬──────────┘
                                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        run_submission.py                             │
│              CLI entry: --candidates --out --top-k                    │
│              Auto-detects JSON/JSONL format                          │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  src/parser.py                                                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ parse_jd() → JDProfile (skills, location, startup signals)     │  │
│  │ parse_candidate() → CandidateProfile                           │  │
│  │ _adapt_real_schema() → maps Redrob fields to internal format   │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  src/semantic_matcher.py                                             │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ SentenceTransformer (all-MiniLM-L6-v2) + FAISS (dense sim)    │  │
│  │ TF-IDF (scikit-learn, 4K features, sparse CSR) - fallback     │  │
│  │ BM25 (k1=1.5, b=0.75) - keyword retrieval                     │  │
│  │ Hybrid: α×dense + (1-α)×BM25                                 │  │
│  │ compute_title_similarities(), compute_experience_similarities()│  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  src/candidate_analyzer.py          src/behavioral_engine.py          │
│  ┌────────────────────────────┐    ┌────────────────────────────┐   │
│  │ 14 dimension scores:      │    │ 23 behavioral signals:     │   │
│  │ experience, retrieval,    │    │ open_to_work, response_rate│   │
│  │ product_company, growth,  │    │ github_score, search_vis,  │   │
│  │ location, education,      │    │ notice_period, relocate,   │   │
│  │ title_quality, coverage,  │    │ profile_views, applied_jobs│   │
│  │ depth, duration, endorse, │    │ interview_rate, offers,    │   │
│  │ leadership, stability,    │    │ certs, open_source, etc    │   │
│  │ startup_mindset           │    │                             │   │
│  └────────────────────────────┘    └────────────────────────────┘   │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  src/honeypot_detector.py                                            │
│  7 types: IMPOSSIBLE_AGE, SKILL_OVERFLOW, CONTRADICTORY_PROFILE,    │
│  SALARY_ANOMALY, TIMELINE_OVERLAP, BEHAVIORAL_ANOMALY, FAKE_EXPER   │
│  Penalties: 0.0 to -0.5                                             │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  src/scorer.py                                                       │
│  Weighted 15-dim formula + honeypot subtraction + clamp [0,1]       │
│  sort_and_rank(): sort desc by score, tie-break by candidate_id asc │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  src/reasoning_generator.py                                          │
│  Rank-aware template reasoning from actual computed scores          │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  src/rank.py - Pipeline Orchestrator                                 │
│  load → parse → embed → match → score → rank → explain → export     │
└──────────────────────────────────────────────────────────────────────┘
                                   ▼
                          ┌─────────────────┐
                          │  submission.csv  │
                          │  (validated ✓)   │
                          └─────────────────┘

Supporting files:
  app.py                          — Streamlit dashboard (4 tabs)
  src/feature_engineering.py      — Consolidated feature extraction API
  src/retrieval.py                 — Dense + BM25 + hybrid retrieval API
  validate_submission.py          — Official Redrob submission validator
  requirements.txt                — Python dependencies
  candidate_schema.json           — Real dataset schema definition
  submission_metadata_template.yaml — Metadata for submission portal
```

---

## Results & Performance

### What results or insights demonstrate ranking quality?

**From the 100K real candidate run:**

- **Top candidate**: CAND_0018499 — Score 0.7263 — 7 years at Zomato, Google building semantic search and ranking systems with Deep Learning, Weaviate, Recommendation Systems. Behavioral signals: actively looking, immediate availability (15 days notice), GitHub score 94.8, willing to relocate, 1291 recruiter search appearances in 30 days.
- **Top 5 candidates**: Scores 0.7263, 0.7020, 0.6994, 0.6990, 0.6969 — all have 6–9 years experience at top product companies (Zomato, Google, Ola, Netflix, Meta, Razorpay, Paytm, Salesforce, Verloop.io)
- **80%+ of top 100** are actively looking and open to work
- **60%+ of top 100** are willing to relocate
- **Domain expertise across top 100**: FAISS, BM25, Elasticsearch, Vector Search, OpenSearch, PyTorch, LangChain, Hugging Face Transformers, Weaviate, Milvus, Qdrant, Pinecone
- All top 100 have retrieval/ranking domain expertise matching the JD requirement
- The top candidate's reasoning is fully explainable and references actual data points

### How does your solution meet the challenge's runtime and compute constraints?

| Constraint | Result | Status |
|------------|--------|--------|
| Under 5 minutes | **256 seconds (4.27 min)** | ✅ |
| Under 16 GB RAM | **~3 GB peak** (sparse TF-IDF ~800MB) | ✅ |
| CPU only | No CUDA/GPU code anywhere | ✅ |
| No external APIs | Zero API calls at inference | ✅ |
| No internet required | TF-IDF fallback works fully offline | ✅ |
| Reproducible | Single command: `python run_submission.py --candidates --out` | ✅ |
| Validated output | `validate_submission.py` — "Submission is valid." | ✅ |

**Performance breakdown (100K candidates):**
- Parsing: ~1s
- TF-IDF fit: ~40s
- BM25 fit: ~50s
- Compute similarities: ~10s
- Scoring all 100K: ~150s
- Export: ~5s

---

## Technologies Used

### What technologies, frameworks, and tools were used and why were they selected for this solution?

| Technology | Purpose | Why Selected |
|-----------|---------|-------------|
| **Python 3.10+** | Core language | Rich ML/NLP ecosystem, cross-platform |
| **pandas, numpy** | Data processing & CSV export | Fast DataFrame operations, standard in data science |
| **scikit-learn** | TF-IDF vectorizer, cosine similarity | Mature, optimized sparse matrix support, no GPU needed |
| **sentence-transformers** | Semantic embeddings (all-MiniLM-L6-v2) | Lightweight (80MB), 384-dim, CPU-friendly, good semantic quality |
| **FAISS (CPU)** | Vector similarity search | Industry-standard, fast cosine search on CPU |
| **BM25 (custom)** | Keyword-level retrieval | Proven IR algorithm, complements dense embeddings |
| **Streamlit** | Interactive dashboard | Fast UI prototyping, native Python, plotly integration |
| **Plotly** | Charts (histogram, pie, radar, bar) | Interactive, good-looking, Streamlit-native |
| **scipy.sparse** | Memory-efficient TF-IDF storage | CSR format ~800MB for 100K×4000 features |
| **python-pptx** | Presentation generation | Programmatic PPT creation for hackathon submission |

**Why this stack over alternatives:**
- **No GPU needed**: all-MiniLM-L6-v2 runs efficiently on CPU; TF-IDF is CPU-native
- **No LLM APIs**: avoids cost, latency, internet dependency, and hallucination risks
- **Sparse matrices**: enables 100K-scale processing in ~3GB RAM
- **Custom BM25**: lightweight, no external dependency, tunable parameters (k1, b)
- **Streamlit over Flask/Dash**: faster development, built-in caching, less boilerplate
