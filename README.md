# TalentForge AI ⚡ — Intelligent Candidate Discovery

**Beyond keyword matching — semantic, behavioral, and signal-aware AI candidate ranking for modern hiring.**

## Architecture

TalentForge AI is a multi-stage candidate ranking pipeline:

1. **Parser** (`src/parser.py`) — Parses JD requirements and candidate profiles. Supports both synthetic JSON and real JSONL dataset format with automatic schema adaptation.
2. **Semantic Matcher** (`src/semantic_matcher.py`) — SentenceTransformer (all-MiniLM-L6-v2) embeddings, TF-IDF fallback, FAISS index, plus BM25 for hybrid retrieval.
3. **Candidate Analyzer** (`src/candidate_analyzer.py`) — 14 scoring dimensions: experience, retrieval, career growth, location, education, skill depth/duration/endorsement, leadership, job stability, startup mindset.
4. **Behavioral Engine** (`src/behavioral_engine.py`) — 23 behavioral signals including redrob platform signals (search appearance, willingness to relocate, endorsements).
5. **Honeypot Detector** (`src/honeypot_detector.py`) — 7-type fake profile detection including behavioral anomalies and fake experience.
6. **Scorer** (`src/scorer.py`) — Weighted scoring with deterministic tie-breaking via candidate ID.
7. **Reasoning Generator** (`src/reasoning_generator.py`) — Rank-aware, JD-referencing human-readable explanations.
8. **Rank Pipeline** (`src/rank.py`) — Orchestrates end-to-end: load → parse → embed → score → rank → reason → export.
9. **Streamlit Dashboard** (`app.py`) — Interactive UI with 4 tabs.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run submission pipeline (CLI)

```bash
python run_submission.py --candidates ./candidates.jsonl --out ./submission.csv
```

Supports both `.jsonl` (100K real dataset) and `.json` (synthetic) formats automatically.

### Generate synthetic test data (500 profiles)

```bash
python data/generate_candidates.py
python src/rank.py
```

Output:
- `output/top_100_candidates.csv` — Top 100 ranked with full score breakdown
- `output/all_candidates_scored.csv` — All candidates scored
- `submission.csv` (via `run_submission.py`) — Validated submission format

### Launch interactive dashboard

```bash
streamlit run app.py
```

## Scoring Formula

| Component | Weight | Description |
|-----------|--------|-------------|
| Semantic Match Score | 25% | Cosine similarity between JD and candidate text embeddings (hybrid: BM25 + dense) |
| Experience Score | 15% | Years of experience fit to JD range (5-9 years ideal) |
| Behavioral Score | 12% | 23 signals: open to work, response rate, GitHub activity, search appearance, etc. |
| Retrieval/Ranking Score | 10% | Domain expertise in search, retrieval, ranking, vector databases |
| Skill Depth Score | 5% | Proficiency level across skills (beginner→expert) |
| Career Growth Score | 6% | Upward title progression over career history |
| Title Semantic Score | 3% | Semantic similarity of current title to JD requirements |
| Experience Semantic Score | 2% | Semantic similarity of career history to JD |
| Leadership Score | 3% | Leadership/management title signals |
| Job Stability Score | 3% | Average tenure and switch frequency |
| Startup Mindset Score | 3% | Product company, open source, hackathon signals |
| Skill Duration Score | 3% | Average months of skill usage |
| Skill Endorsement Score | 2% | Average endorsements per skill |
| Location Score | 4% | Match to preferred locations |
| Education Score | 4% | Tier 1/2/3 university + degree level |
| **Honeypot Penalty** | -0.0 to -0.5 | Subtracted if profile flagged as suspicious |

## Dataset Support

| Feature | Status |
|---------|--------|
| JSONL (100K candidates) | ✅ Automatic format detection |
| JSON (synthetic) | ✅ Backward compatible |
| candidate_schema.json | ✅ Field mapping adapter |
| redrob_signals | ✅ All fields mapped to internal format |
| Streaming/chunking | ✅ JSONL line-by-line parsing |
| Memory optimization | ✅ Lazy loading, no full file in memory |

## Honeypot Detection (7 types)

| Type | Rule | Penalty |
|------|------|---------|
| IMPOSSIBLE_AGE | Grad year + experience > current year | 0.5 |
| SKILL_OVERFLOW | >50/100+ skills | 0.3/0.5 |
| CONTRADICTORY_PROFILE | Non-technical title + strong AI skills | 0.4 |
| SALARY_ANOMALY | Min salary > max salary | 0.3 |
| TIMELINE_OVERLAP | Overlapping employment dates | 0.3 |
| BEHAVIORAL_ANOMALY | High activity with zero visibility | 0.3 |
| FAKE_EXPERIENCE | Inflated tenure, impossible title+exp | 0.2-0.4 |

## Submission Format

Output CSV conforms to `validate_submission.py`:
```
candidate_id,rank,score,reasoning
CAND_0000001,1,0.9234,Rank #1: Strong match...
```

## What Makes TalentForge Different from Keyword ATS?

| Traditional ATS | TalentForge AI |
|----------------|----------------|
| Keyword matching | Semantic embeddings + BM25 hybrid retrieval |
| Binary pass/fail | Continuous 0.0–1.0 scoring (15 dimensions) |
| No behavioral signals | 23 redrob behavioral signals scored |
| Cannot detect fake profiles | 7 honeypot types with penalties |
| No explanations | Rank-aware, JD-referencing reasoning |
| Single score | Full transparency with weighted breakdown |
| No career trajectory | Career growth + job stability scoring |
| No skill depth analysis | Proficiency, duration, endorsement scoring |
