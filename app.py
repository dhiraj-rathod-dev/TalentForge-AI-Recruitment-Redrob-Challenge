"""
TalentForge AI – Streamlit Dashboard
"""

import os, sys, tempfile
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="TalentForge AI — Intelligent Candidate Discovery",
    page_icon="⚡",
    layout="wide",
)

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 20px; }
    div[data-testid="metric-card"] { border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; }
    .score-green { background-color: #d4edda; color: #155724; }
    .score-yellow { background-color: #fff3cd; color: #856404; }
    .score-red { background-color: #f8d7da; color: #721c24; }
    </style>
""", unsafe_allow_html=True)

WEIGHTS = {
    "Semantic Match": 0.25,
    "Experience": 0.15,
    "Behavioral": 0.12,
    "Retrieval/Ranking": 0.10,
    "Career Growth": 0.06,
    "Location": 0.04,
    "Education": 0.04,
    "Skill Depth": 0.05,
    "Leadership": 0.03,
    "Job Stability": 0.03,
    "Startup Mindset": 0.03,
    "Title Semantic": 0.03,
    "Exp Semantic": 0.02,
    "Skill Duration": 0.03,
    "Skill Endorsement": 0.02,
}

DATA_PATH = os.path.join("data", "candidates.json")
DATA_PATH_JSONL = os.path.join(".", "candidates.jsonl")
DATA_PATH_SAMPLE = os.path.join(".", "sample_candidates.json")
TOP_100_PATH = os.path.join("output", "top_100_candidates.csv")
ALL_SCORED_PATH = os.path.join("output", "all_candidates_scored.csv")


def get_candidates_path():
    if os.path.exists(DATA_PATH_JSONL):
        return DATA_PATH_JSONL
    return DATA_PATH


def reset_pipeline_results():
    for k in ["pipeline_result", "top_df", "all_df", "timing"]:
        if k in st.session_state:
            del st.session_state[k]


def run_full_pipeline(dataset_choice, uploaded_file=None):
    from src.rank import run_pipeline
    if uploaded_file is not None:
        suffix = ".jsonl" if uploaded_file.name.endswith(".jsonl") else ".json" if uploaded_file.name.endswith(".json") else ".csv"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            cand_path = tmp.name
        limit = None
    elif dataset_choice == "Synthetic (500)":
        cand_path = DATA_PATH
        limit = 500
    elif dataset_choice == "Sample (50)":
        cand_path = DATA_PATH_SAMPLE
        limit = 50
    else:
        cand_path = get_candidates_path()
        limit = 100000
    top_df, all_df, timing = run_pipeline(candidates_path=cand_path, max_candidates=limit)
    st.session_state["top_df"] = top_df
    st.session_state["all_df"] = all_df
    st.session_state["timing"] = timing
    return top_df, all_df, timing


@st.cache_data
def load_scored_data():
    if os.path.exists(ALL_SCORED_PATH) and os.path.exists(TOP_100_PATH):
        top_df = pd.read_csv(TOP_100_PATH)
        all_df = pd.read_csv(ALL_SCORED_PATH)
        return top_df, all_df
    return None, None


@st.cache_data
def load_row_count(path: str) -> int:
    if os.path.exists(path):
        return len(pd.read_csv(path))
    return 0


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    st.title("TalentForge AI")
    st.caption("Intelligent Candidate Discovery")

    st.divider()
    st.subheader("Dataset Settings")

    uploaded_file = st.file_uploader(
        "Upload your own dataset (JSON / JSONL / CSV)",
        type=["json", "jsonl", "csv"],
        help="If uploaded, this file is used instead of the dataset below",
    )

    dataset_choice = st.selectbox(
        "Select Dataset",
        ["Full (100K real)", "Synthetic (500)", "Sample (50)"],
        index=0,
        disabled=uploaded_file is not None,
        help="Choose which dataset to run the pipeline on",
    )

    if st.button("Run Pipeline", type="primary", use_container_width=True):
        with st.spinner("Running pipeline — may take a few minutes..."):
            run_full_pipeline(dataset_choice, uploaded_file)
        st.success("Pipeline complete!")
        st.rerun()

    st.divider()
    st.subheader("Scoring Weights")
    for label, weight in WEIGHTS.items():
        st.progress(weight, text=f"{label}: {weight:.0%}")
    st.divider()

    st.subheader("Model Info")
    st.text("Embedding: all-MiniLM-L6-v2")
    st.text("Fallback: TF-IDF (no GPU)")
    st.text("Search: FAISS (cosine IP)")

    st.divider()
    st.caption("Redrob Hackathon 2025")

# ── Tabs ─────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "🏆 Top 100 Candidates",
    "🔍 Candidate Deep Dive",
    "⚠️ Honeypot Report",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Dashboard
# ══════════════════════════════════════════════════════════════════════════════

with tab1:
    st.header("Pipeline Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    top_df = st.session_state.get("top_df", None)
    all_df = st.session_state.get("all_df", None)
    timing = st.session_state.get("timing", None)

    if top_df is None or all_df is None:
        top_df, all_df = load_scored_data()

    if top_df is not None and all_df is not None:
        total_candidates = len(all_df)
        top_100_count = len(top_df)
        honeypot_count = int(all_df["honeypot_flag"].sum())
        avg_score = all_df["final_score"].mean()

        with col1:
            st.metric("Total Candidates", f"{total_candidates:,}")
        with col2:
            st.metric("Top 100 Selected", top_100_count)
        with col3:
            st.metric("Honeypots Detected", honeypot_count)
        with col4:
            st.metric("Avg Score", f"{avg_score:.3f}")

        st.divider()
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Score Distribution (Top 100)")
            fig_hist = px.histogram(
                top_df, x="final_score", nbins=20,
                color_discrete_sequence=["#636efa"],
                labels={"final_score": "Final Score", "count": "Number of Candidates"},
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, width='stretch')

        with col_right:
            st.subheader("Location Breakdown (Top 100)")
            loc_counts = top_df["location"].value_counts().reset_index()
            loc_counts.columns = ["location", "count"]
            fig_pie = px.pie(
                loc_counts, names="location", values="count",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, width='stretch')

        if timing is not None:
            st.info(f"⏱️ Last pipeline run: {timing:.2f}s ({timing/60:.2f} min)")
    else:
        st.info("No pipeline results found. Upload your own dataset in the sidebar or select one, then click 'Run Pipeline'.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – Top 100 Candidates
# ══════════════════════════════════════════════════════════════════════════════

with tab2:
    st.markdown('<div class="top100-tab">', unsafe_allow_html=True)
    st.markdown("""
        <style>
        .top100-tab {
            background-color: #2a2a2e !important;
            padding: 20px;
            border-radius: 8px;
        }
        .top100-tab, .top100-tab p, .top100-tab div, .top100-tab span,
        .top100-tab h1, .top100-tab h2, .top100-tab h3,
        .top100-tab label, .top100-tab .st-bb, .top100-tab .st-at,
        .top100-tab .st-bw, .top100-tab .st-bv,
        .top100-tab [data-testid="stMarkdownContainer"] p {
            color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.header("Top 100 Candidates")

    if top_df is None:
        st.info("Run the pipeline first to see results.")
    else:
        filtered = top_df.copy()

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            locations = ["All"] + sorted(filtered["location"].dropna().unique().tolist())
            loc_filter = st.selectbox("Filter by Location", locations)
        with col_f2:
            min_score = st.slider("Minimum Score", 0.0, 1.0, 0.0, 0.01)

        if loc_filter != "All":
            filtered = filtered[filtered["location"] == loc_filter]
        filtered = filtered[filtered["final_score"] >= min_score]

        def color_row(row):
            score = row["final_score"]
            if score > 0.7:
                # light green background, dark green text
                return ["background-color: #d4edda; color: #0b3d1f; font-weight:500;"] * len(row)
            elif score >= 0.5:
                # light yellow background, dark brown text
                return ["background-color: #fff3cd; color: #5c4400; font-weight:500;"] * len(row)
            else:
                # light red background, dark red text
                return ["background-color: #f8d7da; color: #5c0a14; font-weight:500;"] * len(row)

        display_cols = [
            "rank", "name", "final_score", "current_title", "current_company",
            "experience_years", "location", "reasoning",
        ]
        display_df = filtered[display_cols].copy()
        display_df["final_score"] = display_df["final_score"].round(3)

        st.dataframe(
            display_df.style.apply(color_row, axis=1),
            width='stretch',
            hide_index=True,
            height=600,
        )

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Filtered CSV",
            data=csv,
            file_name="filtered_top_100.csv",
            mime="text/csv",
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – Candidate Deep Dive
# ══════════════════════════════════════════════════════════════════════════════

with tab3:
    st.header("Candidate Deep Dive")

    if top_df is None:
        st.info("Run the pipeline first to see candidates.")
    else:
        candidate_names = top_df["name"].tolist()
        selected_name = st.selectbox("Select a Candidate", candidate_names)

        cand_row = top_df[top_df["name"] == selected_name].iloc[0]

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.metric("Final Score", f"{cand_row['final_score']:.3f}")
        with col_d2:
            st.metric("Title", cand_row["current_title"])
        with col_d3:
            st.metric("Company", cand_row["current_company"])

        st.divider()

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("Score Breakdown")

            score_categories = [
                "semantic_score", "experience_score", "behavioral_score",
                "retrieval_score", "career_growth_score", "location_score",
                "education_score", "skill_depth_score", "skill_duration_score",
                "skill_endorsement_score", "leadership_score", "job_stability_score",
                "startup_mindset_score", "title_semantic_score", "experience_semantic_score",
            ]
            score_labels = [
                "Semantic", "Experience", "Behavioral",
                "Retrieval", "Growth", "Location",
                "Education", "Skill Depth", "Skill Duration",
                "Endorsements", "Leadership", "Stability",
                "Startup Mindset", "Title Sem", "Exp Sem",
            ]
            score_values = [float(cand_row.get(c, 0)) for c in score_categories]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=score_values + [score_values[0]],
                theta=score_labels + [score_labels[0]],
                fill="toself",
                name=selected_name,
                line_color="#636efa",
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                height=400,
                showlegend=False,
            )
            st.plotly_chart(fig_radar, width='stretch')

        with col_chart2:
            st.subheader("Dimension Scores (Bar)")
            fig_bar = px.bar(
                x=score_labels,
                y=score_values,
                color=score_values,
                color_continuous_scale="Viridis",
                labels={"x": "Dimension", "y": "Score"},
                range_color=[0, 1],
            )
            fig_bar.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_bar, width='stretch')

        st.divider()
        st.subheader("Reasoning")
        st.info(cand_row.get("reasoning", ""))

        st.subheader("Candidate Details")
        detail_cols = [
            "rank", "name", "final_score", "semantic_score", "experience_score",
            "behavioral_score", "retrieval_score", "career_growth_score",
            "location_score", "education_score", "honeypot_flag", "honeypot_type",
            "current_title", "current_company", "experience_years", "location",
        ]
        detail_data = {k: cand_row.get(k, "") for k in detail_cols}
        st.json(detail_data)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – Honeypot Report
# ══════════════════════════════════════════════════════════════════════════════

with tab4:
    st.header("Honeypot Report")

    if all_df is None:
        st.info("Run the pipeline first to see honeypot results.")
    else:
        honeypots = all_df[all_df["honeypot_flag"] == True].copy()
        if len(honeypots) == 0:
            st.success("No honeypot candidates detected!")
        else:
            st.warning(f"{len(honeypots)} suspicious candidates flagged")

            honeypot_display = honeypots[[
                "rank", "name", "final_score", "honeypot_type",
                "current_title", "current_company", "location",
                "reasoning",
            ]].copy()
            honeypot_display["final_score"] = honeypot_display["final_score"].round(3)

            st.dataframe(
                honeypot_display,
                width='stretch',
                hide_index=True,
                height=500,
            )

            st.divider()
            st.subheader("Honeypot Type Distribution")
            type_counts = honeypots["honeypot_type"].value_counts().reset_index()
            type_counts.columns = ["Honeypot Type", "Count"]
            fig_honey = px.bar(
                type_counts, x="Honeypot Type", y="Count",
                color="Count", color_continuous_scale="Reds",
            )
            st.plotly_chart(fig_honey, width='stretch')

            st.divider()
            st.subheader("Honeypot Detection Criteria")
            st.markdown("""
            | Type | Detection Rule | Penalty |
            |------|---------------|---------|
            | **IMPOSSIBLE_AGE** | Graduation year + experience > current year | 0.5 |
            | **SKILL_OVERFLOW** | >50 skills (suspicious), >100 (definite flag) | 0.3–0.5 |
            | **CONTRADICTORY_PROFILE** | Non-technical title but strong AI skills | 0.4 |
            | **SALARY_ANOMALY** | Min salary > max salary | 0.3 |
            | **TIMELINE_OVERLAP** | Overlapping employment dates | 0.3 |
            | **BEHAVIORAL_ANOMALY** | Impossibly high activity with zero visibility | 0.3 |
            | **FAKE_EXPERIENCE** | Inflated tenure, impossible title+exp combos | 0.2–0.4 |
            """)

