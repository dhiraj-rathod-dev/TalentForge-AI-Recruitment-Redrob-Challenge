# TalentForge AI — Complete Project Explanation
🌐 Live Demo

🚀 Streamlit Application

🔗 https://talentforge-ai-recruitment-redrob-challenge-szujfsyksbrhvmyqzb.streamlit.app/

Explore the live TalentForge AI application to upload a sample candidate dataset, generate ranked candidates, view score analytics, inspect behavioral insights, and understand AI-generated reasoning through an interactive Streamlit dashboard.

## What Is This Project?

TalentForge AI is an **intelligent AI-powered candidate discovery and ranking system** built for the **Redrob Hackathon**. It goes far beyond traditional keyword-based ATS (Applicant Tracking Systems) by using semantic understanding, BM25+embedding hybrid retrieval, behavioral signal analysis, multi-dimensional scoring, and honeypot detection to find the best candidates for a Senior AI Engineer role.

The system processes **100,000 real candidate profiles** (or 500 synthetic), scores them across **15 weighted dimensions**, detects **7 types of suspicious profiles**, and ranks them from best to worst match — all in **under 5 minutes on CPU** with no internet required.

---

## Main Motto / Purpose

> **"Beyond keyword matching — semantic, behavioral, and signal-aware AI candidate ranking for modern hiring."**

The core problem TalentForge solves: Traditional ATS systems miss great candidates because they only do exact keyword matching. A candidate who says "vector search" instead of "FAISS" gets rejected. A fake profile with 200 skills looks the same as a real expert. TalentForge fixes this by:

- **Understanding meaning**, not just keywords (semantic embeddings + BM25 hybrid)
- **Scoring 23 behavioral signals** from the Redrob platform to find actively available, engaged candidates
- **Detecting fake profiles** across 7 honeypot types
- **Explaining every ranking** with rank-aware, JD-referencing human-readable reasoning
- **Providing full transparency** with a 15-dimension weighted scoring breakdown

---

## Project Structure

```
TalentForge-AI/
├── data/
│   ├── candidates.json              # 500 synthetic candidate profiles (generated)
│   ├── generate_candidates.py       # Synthetic data generator
│   └── job_description.txt          # Senior AI Engineer JD
├── src/
│   ├── __init__.py                  # Package marker
│   ├── parser.py                    # JD & Candidate parsing with schema adapter
│   ├── semantic_matcher.py          # SentenceTransformer + BM25 + FAISS + TF-IDF fallback
│   ├── candidate_analyzer.py        # 14-dimension feature scoring engine
│   ├── behavioral_engine.py         # 23 Redrob behavioral signal scorer
│   ├── honeypot_detector.py         # 7-type fake profile detection
│   ├── scorer.py                    # Weighted final score + tie-breaking
│   ├── reasoning_generator.py       # Rank-aware human-readable explanations
│   ├── rank.py                      # Main pipeline orchestrator (CLI + args)
│   ├── feature_engineering.py       # Consolidated feature extraction API
│   └── retrieval.py                 # Dense + BM25 + hybrid retrieval API
├── output/
│   ├── top_100_candidates.csv       # Top 100 ranked candidates (full breakdown)
│   └── all_candidates_scored.csv    # All candidates with scores
├── app.py                           # Streamlit interactive dashboard
├── run_submission.py                # Submission entry point (--candidates --out)
├── requirements.txt                 # Python dependencies
├── candidate_schema.json            # Real dataset schema definition
├── validate_submission.py           # Official Redrob validator
├── submission_metadata_template.yaml # Metadata for submission portal
├── README.md                        # Quick-start guide
└── PROJECT_EXPLANATION.md           # This document
```

---

## File-by-File Explanation

### root files

| File | Purpose |
|------|---------|
| `run_submission.py` | **Submission entry point.** Accepts `--candidates <path>` and `--out <path>` CLI args. Detects JSON vs JSONL format automatically. Runs end-to-end pipeline and outputs `submission.csv` in validator-compatible format. |
| `app.py` | **Streamlit Dashboard.** 4 tabs: Dashboard (metrics, score distribution), Top 100 (filterable table), Candidate Deep Dive (radar chart + reasoning), Honeypot Report (flagged profiles with type distribution). |
| `validate_submission.py` | **Official Redrob submission validator.** Checks header format (`candidate_id,rank,score,reasoning`), CAND_XXXXXXX ID format, unique ranks 1-100, non-increasing scores, tie-breaking order, UTF-8 encoding. |
| `requirements.txt` | Python dependencies: pandas, numpy, scikit-learn, sentence-transformers, faiss-cpu, streamlit, plotly, tqdm. |
| `candidate_schema.json` | JSON Schema defining the real dataset structure. Used as reference for the `_adapt_real_schema` adapter in parser.py. |
| `submission_metadata_template.yaml` | Metadata template for hackathon submission portal (team info, compute environment, AI tools declaration). |

### data/ files

| File | Purpose |
|------|---------|
| `candidates.jsonl` | **Real dataset: 100,000 candidates.** JSONL format, each line is a full candidate object per `candidate_schema.json`. Contains `candidate_id`, `profile`, `career_history`, `education`, `skills`, `redrob_signals`. |
| `sample_candidates.json` | Sample of ~50 real candidates from the 100K dataset for testing and review. |
| `candidates.json` | 500 synthetic candidates generated by `generate_candidates.py`. Uses different schema (`id` as UUID, `behavioral_signals`, `total_experience_years`). |
| `generate_candidates.py` | Synthetic data generator. Creates 500 profiles: 150 strong matches, 100 medium AI, 100 consulting, 120 weak/non-technical, 30 honeypots. |
| `job_description.txt` | Senior AI Engineer – Founding Team JD used for the challenge. |

### src/ files

| File | Purpose |
|------|---------|
| `parser.py` | **JD & Candidate Parsing.** Contains `JDProfile` and `CandidateProfile` dataclasses. `parse_jd()` extracts structured requirements (required skills, preferred skills, disqualifiers, preferred locations, startup mindset signals). `parse_candidate()` handles both synthetic and real dataset schemas via `_adapt_real_schema()` which maps `candidate_id`→`id`, `profile.years_of_experience`→`total_experience_years`, `redrob_signals`→`behavioral_signals`, `education` array→dict, `start_date`/`end_date`→years. |
| `semantic_matcher.py` | **Semantic Matching Engine.** Three retrieval modes: (1) SentenceTransformer (all-MiniLM-L6-v2) with FAISS index for dense retrieval, (2) TF-IDF fallback for offline/large-scale, (3) BM25 for keyword-level retrieval. Hybrid retrieval combines dense + BM25 with configurable alpha. Also computes title semantic similarity and experience semantic similarity via batched encoding. |
| `candidate_analyzer.py` | **Feature Scoring Engine.** 14 dimension scores: experience, retrieval expertise, product company, career growth, location, education, title quality, skill coverage, skill depth (proficiency level), skill duration (months used), skill endorsement (avg endorsements), leadership (title signals), job stability (avg tenure), startup mindset (product + open source + hackathons). |
| `behavioral_engine.py` | **Behavioral Signal Scoring.** 23 signals from Redrob platform: open_to_work_flag, recruiter_response_rate, last_active_days_ago, github_activity_score, saved_by_recruiters_30d, interview_completion_rate, offer_acceptance_rate, notice_period_days, profile_completeness_score, response_time_hours, applied_jobs_last_30d, profile_views_30d, search_appearance_30d, willing_to_relocate, endorsements_received, skill_endorsement_velocity, recommendation_count, publication_count, open_source_contributions, hackathon_participations, certification_count, avg_tenure_years, job_switch_frequency. |
| `honeypot_detector.py` | **Honeypot Detection.** 7 detection types: IMPOSSIBLE_AGE (grad year + experience > 2026), SKILL_OVERFLOW (>50/100+ skills), CONTRADICTORY_PROFILE (non-technical title + strong AI skills), SALARY_ANOMALY (min > max salary), TIMELINE_OVERLAP (overlapping employment), BEHAVIORAL_ANOMALY (high activity + zero visibility), FAKE_EXPERIENCE (inflated tenure, impossible title+experience combos). Penalties range 0.2-0.5. |
| `scorer.py` | **Final Scoring.** Weighted formula combining all 15 dimensions (semantic match 25%, experience 15%, behavioral 12%, retrieval 10%, career growth 6%, location 4%, education 4%, skill depth 5%, skill duration 3%, skill endorsement 2%, leadership 3%, job stability 3%, startup mindset 3%, title semantic 3%, experience semantic 2%). Subtracts honeypot penalty. Includes `sort_and_rank()` with deterministic tie-breaking by candidate_id ascending. |
| `reasoning_generator.py` | **Explanation Generator.** Produces human-readable reasoning per candidate. Rank-aware ("Rank #1: ..."), references JD requirements ("meets the 5-9 year experience requirement", "has the required expert-level Python"), mentions candidate strengths (companies, skills, years), concerns (consulting-only, limited retrieval, location), behavioral signals (open to work, response rate, notice period, GitHub score, willingness to relocate, search visibility). |
| `rank.py` | **Pipeline Orchestrator.** End-to-end: load (auto-detect JSON/JSONL), parse (schema-adaptive), embed (auto-select SentenceTransformer or TF-IDF for 10K+), compute all scores, sort with tie-breaking, generate reasoning, export. Accepts `--candidates`, `--out`, `--top-k` CLI args. For large datasets (10K+), auto-selects TF-IDF for performance. |
| `feature_engineering.py` | **Feature Engineering API.** Wraps `CandidateAnalyzer` with grouped feature extraction: `extract_experience_features()`, `extract_skill_features()`, `extract_profile_features()`, `extract_all()`. |
| `retrieval.py` | **Retrieval API.** Wraps `SemanticMatcher` with `dense_retrieval()`, `bm25_retrieve()`, `hybrid_retrieve()` methods for programmatic access. |

---

## How It Works — Step by Step

### Stage 1: Data Loading & Schema Adaptation
`rank.py:load_candidates()` auto-detects JSON vs JSONL format. For each candidate, `parser.py:parse_candidate()` calls `_adapt_real_schema()` to map the real dataset schema to internal `CandidateProfile` dataclass:
- `candidate_id` → `id` (CAND_XXXXXXX preserved)
- `profile.years_of_experience` → `total_experience_years`
- `redrob_signals` → `behavioral_signals` (23 fields mapped with correct names)
- `education` array → dict (takes highest degree)
- `start_date`/`end_date` → `start_year`/`end_year`

### Stage 2: Semantic Matching (`semantic_matcher.py`)
- **Dense retrieval**: SentenceTransformer (all-MiniLM-L6-v2) → 384-dim embeddings → FAISS cosine search
- **BM25 retrieval**: Custom BM25 implementation with k1=1.5, b=0.75
- **Hybrid**: `0.7 × dense + 0.3 × BM25`
- **Title similarity**: Batch-encoded current titles vs JD requirements
- **Experience similarity**: Batch-encoded career history vs JD
- **Auto-fallback**: TF-IDF for 10K+ candidates (sparse matrix, no GPU)

### Stage 3: Feature Engineering (`candidate_analyzer.py`)
14 dimension scores computed per candidate:
- **Experience**: 5-9 years ideal → 1.0, graduated curve to 0.2
- **Retrieval Expertise**: Count retrieval-domain signals in profile
- **Product Company**: Ratio of product vs consulting companies in career
- **Career Growth**: Title level progression over career history
- **Location**: Match to Bangalore, Pune, Hyderabad, Delhi NCR, Noida, Mumbai, Remote
- **Education**: Tier 1/2/3 university + advanced degree boost
- **Title Quality**: Current title relevance to AI/ML
- **Skill Coverage**: Fraction of required skills matched
- **Skill Depth**: Average proficiency level (beginner→expert)
- **Skill Duration**: Average months of skill usage (capped at 36mo)
- **Skill Endorsement**: Average endorsements per skill (capped at 50)
- **Leadership**: Leadership title signals in current and past roles
- **Job Stability**: Average tenure (1.5-4yr ideal)
- **Startup Mindset**: Product company + open source + hackathons

### Stage 4: Behavioral Scoring (`behavioral_engine.py`)
23 Redrob platform signals weighted and combined into 0-1 behavioral score.
New signals added: `search_appearance_30d`, `willing_to_relocate`, `endorsements_received`.

### Stage 5: Honeypot Detection (`honeypot_detector.py`)
7 detection types with configurable penalties:
- **IMPOSSIBLE_AGE** (0.5): Graduation year + experience > current year
- **SKILL_OVERFLOW** (0.3-0.5): >50/100+ skills
- **CONTRADICTORY_PROFILE** (0.4): Non-technical title + strong AI skills
- **SALARY_ANOMALY** (0.3): Min salary > max salary
- **TIMELINE_OVERLAP** (0.3): Overlapping employment dates
- **BEHAVIORAL_ANOMALY** (0.3): High GitHub/response rate with zero profile views
- **FAKE_EXPERIENCE** (0.2-0.4): Impossible title+exp combos, inflated tenure

### Stage 6: Weighted Scoring (`scorer.py`)
Combines all scores with final formula, subtracts honeypot penalty, clamps 0-1.
Deterministic tie-breaking: equal scores sorted by candidate_id ascending.

### Stage 7: Reasoning Generation (`reasoning_generator.py`)
Produces rank-aware, JD-referencing explanations:
- "Rank #1: Strong match for retrieval-focused AI engineering role..."
- "JD fit: meets the 5-9 year experience requirement (7 yrs); demonstrates retrieval/ranking expertise..."
- Behavioral signals: open to work, response rate, search visibility, willingness to relocate

### Stage 8: Export
- `submission.csv`: `candidate_id,rank,score,reasoning` (validator-compatible)
- `top_100_candidates.csv`: Full 23-column score breakdown
- `all_candidates_scored.csv`: All candidates with complete breakdown

---

## How to Run

### Prerequisites
- Python 3.10+
- 16GB RAM recommended for 100K dataset

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2a: Run on real dataset (100K candidates)
```bash
python run_submission.py --candidates ./candidates.jsonl --out ./submission.csv
```

### Step 2b: Run on synthetic test data (500 candidates)
```bash
python data/generate_candidates.py
python src/rank.py
```

### Step 3: Validate submission
```bash
python validate_submission.py submission.csv
```
Expected output: `Submission is valid.`

### Step 4: Launch interactive dashboard
```bash
python -m streamlit run app.py
```

### Expected Performance

| Dataset | Candidates | Runtime | Memory | Model |
|---------|-----------|---------|--------|-------|
| Synthetic | 500 | ~17s | < 1GB | SentenceTransformer |
| Real (small) | 200 | ~24s | < 1GB | SentenceTransformer |
| Real (full) | 100,000 | ~256s (4.27 min) | ~3 GB | TF-IDF + BM25 |

---

## Scoring Formula

```
final_score = (0.25 × semantic_match) + (0.15 × experience) + (0.12 × behavioral)
            + (0.10 × retrieval) + (0.06 × career_growth) + (0.04 × location)
            + (0.04 × education) + (0.05 × skill_depth) + (0.03 × skill_duration)
            + (0.02 × skill_endorsement) + (0.03 × leadership) + (0.03 × job_stability)
            + (0.03 × startup_mindset) + (0.03 × title_semantic) + (0.02 × exp_semantic)
            - honeypot_penalty
```

| Weight | Component | Why It Matters |
|--------|-----------|----------------|
| **25%** | Semantic Match (Hybrid) | BM25 + embedding hybrid that understands meaning beyond keywords |
| **15%** | Experience | Years in the right 5-9 range for a Senior role |
| **12%** | Behavioral | 23 Redrob platform signals showing engagement and availability |
| **10%** | Retrieval/Ranking | Domain expertise in search, vector DBs, evaluation metrics |
| **6%** | Career Growth | Upward trajectory shows ambition and capability growth |
| **5%** | Skill Depth | Proficiency level across skills (beginner→expert) |
| **4%** | Location | Preferred cities + remote |
| **4%** | Education | Tier 1/2/3 university + advanced degrees |
| **3%** | Skill Duration | Average months of skill usage |
| **3%** | Leadership | Leadership/management title signals |
| **3%** | Job Stability | Healthy tenure without job-hopping |
| **3%** | Startup Mindset | Product company + open source + hackathons |
| **3%** | Title Semantic | Current title semantic similarity to JD |
| **2%** | Skill Endorsement | Peer endorsements validating skill claims |
| **2%** | Exp Semantic | Career history semantic similarity to JD |

---

## Honeypot Detection (7 types)

| Type | Detection Rule | Penalty |
|------|---------------|---------|
| IMPOSSIBLE_AGE | Graduation year + experience > 2026 | 0.5 |
| SKILL_OVERFLOW | >50 skills (suspicious), >100 (definite) | 0.3-0.5 |
| CONTRADICTORY_PROFILE | Non-technical title + 5+ strong AI skills | 0.4 |
| SALARY_ANOMALY | Salary min > salary max | 0.3 |
| TIMELINE_OVERLAP | Overlapping employment dates | 0.3 |
| BEHAVIORAL_ANOMALY | High GitHub/response rate + zero visibility | 0.3 |
| FAKE_EXPERIENCE | Inflated tenure, impossible title+exp combos | 0.2-0.4 |

---

## Technical Details

### Constraints Respected
| Constraint | Status | Detail |
|------------|--------|--------|
| CPU only | ✅ | No CUDA/GPU code anywhere |
| No external APIs | ✅ | No API calls at inference |
| No internet required | ✅ | TF-IDF fallback works fully offline |
| Under 5 minutes | ✅ | 100K in 256s (4.27 min) |
| Under 16GB RAM | ✅ | ~3GB peak for 100K (sparse TF-IDF) |
| Reproducible | ✅ | `run_submission.py --candidates --out` |

### Dataset Support

| Feature | Status |
|---------|--------|
| JSONL streaming | ✅ Line-by-line, no full file in memory |
| JSON support | ✅ Backward compatible with synthetic data |
| Auto format detection | ✅ Checks first character: `{` → JSONL, `[` → JSON |
| Schema adapter | ✅ Maps candidate_schema.json fields to internal format |
| 100K candidates | ✅ Proven with full dataset |
| Sparse matrix | ✅ CSR format, ~800MB for 100K×4000 features |

### Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.10+ | Core language |
| pandas, numpy | Data processing & CSV export |
| scikit-learn | TF-IDF vectorizer, cosine similarity |
| sentence-transformers | Semantic embeddings (all-MiniLM-L6-v2) |
| FAISS (CPU) | Vector similarity search index |
| BM25 (custom) | Keyword-level retrieval for hybrid |
| Streamlit | Interactive dashboard |
| Plotly | Charts (histogram, pie, radar, bar) |
| tqdm | Progress bars |
| scipy.sparse | Memory-efficient TF-IDF storage |

---

## Key Results (from 100K real dataset run)

```
Total candidates: 100,000
Runtime: 256.34s (4.27 min)
Peak memory: ~3 GB
Output: submission.csv (100 candidates, validated ✓)
```

---

## What Makes TalentForge Different from Keyword ATS?

| Traditional ATS | TalentForge AI |
|----------------|----------------|
| Keyword matching (exact string) | **Semantic embeddings + BM25 hybrid** — understands "vector search" matches "FAISS" |
| Binary pass/fail filters | **Continuous 0.0–1.0 scoring** — nuanced ranking across 15 dimensions |
| No behavioral signals | **23 Redrob platform signals** — finds actively available, engaged candidates |
| Cannot detect fake profiles | **7 honeypot types** — catches impossible age, skill overflow, contradictions, anomalies |
| No explanations | **Rank-aware, JD-referencing reasoning** — "Rank #1: meets the 5-9yr experience requirement..." |
| Single score, no transparency | **Full score breakdown** with 15 weighted dimensions visible |
| Static keyword ranking | **Multi-dimensional weighted scoring** with hybrid retrieval |
| Ignores career trajectory | **Career growth + job stability + leadership scoring** |
| No skill depth analysis | **Proficiency level, duration, and endorsement scoring** |
| No title understanding | **Semantic title matching** — knows "Search Engineer" ≈ "Retrieval Engineer" |
| Fixed on one dataset format | **Auto-detects JSON / JSONL**, adapts to real schema |
