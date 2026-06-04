from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.report_generator import generate_briefing
from src.scoring import calculate_match
from src.text_utils import load_sample, read_uploaded_file

st.set_page_config(
    page_title="Recruitment Copilot",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main { background: linear-gradient(180deg, #fff7fb 0%, #f8fbff 45%, #ffffff 100%); }
    .block-container { padding-top: 2rem; }
    .hero {
        padding: 2rem;
        border-radius: 28px;
        background: linear-gradient(135deg, #301934 0%, #7f2ccb 50%, #ff8a65 100%);
        color: white;
        margin-bottom: 1.2rem;
        box-shadow: 0 18px 45px rgba(80, 38, 120, 0.22);
    }
    .hero h1 { font-size: 3rem; margin-bottom: 0.2rem; }
    .hero p { font-size: 1.05rem; opacity: 0.92; max-width: 820px; }
    .card {
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(130, 90, 160, 0.18);
        border-radius: 22px;
        padding: 1.2rem;
        box-shadow: 0 10px 30px rgba(80, 50, 110, 0.08);
        min-height: 145px;
    }
    .decision-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.96), rgba(245,238,255,0.96));
        border: 1px solid rgba(130, 90, 160, 0.18);
        border-radius: 24px;
        padding: 1.4rem 1.6rem;
        margin: 1.2rem 0;
        box-shadow: 0 12px 32px rgba(80, 50, 110, 0.10);
    }
    .decision-title { font-size: 1rem; text-transform: uppercase; letter-spacing: 0.08em; color: #6d5a73; margin-bottom: 0.25rem; }
    .decision-score { font-size: 3.8rem; line-height: 1; font-weight: 850; color: #301934; margin: 0.2rem 0; }
    .decision-reco { font-size: 1.25rem; font-weight: 750; color: #0f7a3b; margin-bottom: 0.5rem; }
    .summary-card {
        background: rgba(255,255,255,0.88);
        border-left: 6px solid #7f2ccb;
        border-radius: 18px;
        padding: 1rem 1.2rem;
        box-shadow: 0 8px 24px rgba(80, 50, 110, 0.06);
        margin-bottom: 1rem;
    }
    .evidence-card {
        background: #ffffff;
        border: 1px solid rgba(130, 90, 160, 0.14);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.7rem;
        box-shadow: 0 8px 20px rgba(80, 50, 110, 0.05);
    }
    .evidence-card strong { color: #301934; }
    .score-note { color: #6d5a73; font-size: 0.9rem; }
    .metric-big { font-size: 3.2rem; font-weight: 800; margin: 0; color: #5c2483; }
    .metric-label { font-size: 0.92rem; text-transform: uppercase; letter-spacing: 0.08em; color: #6d5a73; }
    .pill {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: #f4e7ff;
        color: #5c2483;
        margin: 0.2rem 0.25rem 0.2rem 0;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .pill-gap { background: #fff0e9; color: #a3441f; }
    .pill-partial { background: #eef4ff; color: #255b96; }
    .section-title { margin-top: 1.2rem; color: #301934; }
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.86);
        border-radius: 18px;
        padding: 1rem;
        border: 1px solid rgba(130, 90, 160, 0.14);
        box-shadow: 0 8px 24px rgba(80, 50, 110, 0.06);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <h1>Recruitment Copilot</h1>
        <p>AI-assisted candidate screening for human recruiters. Compare a CV with a job description, identify strengths and gaps, generate interview prompts, and create a structured recruiter briefing.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Candidate inputs")
    use_samples = st.toggle("Use sample data", value=True)
    uploaded_cv = st.file_uploader("Upload CV", type=["txt", "pdf", "docx"])
    uploaded_job = st.file_uploader("Upload job description", type=["txt", "pdf", "docx"])
    candidate_name = st.text_input("Candidate name", value="Alex Martin")
    st.caption("This prototype supports TXT, PDF and DOCX extraction. Human review remains required.")

if use_samples:
    default_cv = load_sample("sample_cv.txt")
    default_job = load_sample("sample_job_description.txt")
else:
    default_cv = ""
    default_job = ""

cv_text = read_uploaded_file(uploaded_cv) or default_cv
job_text = read_uploaded_file(uploaded_job) or default_job

left, right = st.columns(2)
with left:
    cv_text = st.text_area("CV text", value=cv_text, height=260)
with right:
    job_text = st.text_area("Job description", value=job_text, height=260)

analyze = st.button("Analyze candidate", type="primary", use_container_width=True)

if analyze or (cv_text and job_text):
    result = calculate_match(cv_text, job_text)
    briefing = generate_briefing(result, candidate_name)

    st.markdown(
        f'''
        <div class="decision-card">
            <div class="decision-title">Recommendation</div>
            <div class="decision-score">{result.overall_score}%</div>
            <div class="decision-reco">{result.recommendation}</div>
            <div class="score-note">Confidence: {result.confidence} · Human recruiter review required</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    strengths_preview = ", ".join(result.matched_skills[:5]) if result.matched_skills else "No direct skill match detected"
    st.markdown(
        f'''
        <div class="summary-card">
            <strong>Executive summary</strong><br>
            This candidate appears to be a <strong>{result.recommendation.lower()}</strong>. The strongest detected evidence relates to {strengths_preview}. Use the scorecard and evidence highlights below to decide what to verify in interview.
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown('<h2 class="section-title">Candidate Match Overview</h2>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Overall Match", f"{result.overall_score}%", result.recommendation)
    c2.metric("Technical Fit", f"{result.technical_score}%")
    c3.metric("Experience Fit", f"{result.experience_score}%")
    c4.metric("Communication", f"{result.communication_score}%")
    c5.metric("Portfolio", f"{result.portfolio_score}%")

    st.markdown("---")
    score_col, skills_col = st.columns([1, 1.35])

    with score_col:
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=result.overall_score,
                number={"suffix": "%", "font": {"size": 48}},
                title={"text": "Candidate match"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"thickness": 0.28},
                    "steps": [
                        {"range": [0, 50], "color": "#f7e9e2"},
                        {"range": [50, 75], "color": "#f2e7ff"},
                        {"range": [75, 100], "color": "#e7f6ef"},
                    ],
                },
            )
        )
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with skills_col:
        st.markdown("### Skill evidence")
        st.markdown("**Matched skills**")
        st.markdown("".join(f'<span class="pill">{skill}</span>' for skill in result.matched_skills) or "None", unsafe_allow_html=True)
        st.markdown("**Partial / adjacent evidence**")
        st.markdown("".join(f'<span class="pill pill-partial">{skill}</span>' for skill in result.partial_skills) or "None", unsafe_allow_html=True)
        st.markdown("**Skills to verify**")
        st.markdown("".join(f'<span class="pill pill-gap">{skill}</span>' for skill in result.missing_skills) or "No major gaps detected", unsafe_allow_html=True)

        st.markdown("**Additional evidence signals**")
        if result.signal_matches:
            for signal, keywords in result.signal_matches.items():
                st.markdown(
                    f'<span class="pill pill-partial">{signal}: {", ".join(keywords[:4])}</span>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("None")

    st.markdown('<h2 class="section-title">Top Evidence Highlights</h2>', unsafe_allow_html=True)
    if result.evidence_highlights:
        highlight_cols = st.columns(2)
        for index, highlight in enumerate(result.evidence_highlights):
            with highlight_cols[index % 2]:
                st.markdown(f'<div class="evidence-card"><strong>✓ {highlight}</strong></div>', unsafe_allow_html=True)
    else:
        st.write("No specific evidence highlights detected.")

    st.markdown('<h2 class="section-title">Why This Score?</h2>', unsafe_allow_html=True)
    why_score = pd.DataFrame(
        [
            {"Component": "Technical fit", "Score": result.technical_score, "Reason": "Explicit overlap between required skills and CV evidence."},
            {"Component": "Experience fit", "Score": result.experience_score, "Reason": "Project, delivery, business and stakeholder signals."},
            {"Component": "Education fit", "Score": result.education_score, "Reason": "Degree, certification and formal learning signals."},
            {"Component": "Communication evidence", "Score": result.communication_score, "Reason": "Teaching, mentoring, training and explanation signals."},
            {"Component": "Portfolio evidence", "Score": result.portfolio_score, "Reason": "Project, GitHub, dashboard, notebook and prototype signals."},
        ]
    )
    st.dataframe(why_score, use_container_width=True, hide_index=True)

    st.markdown('<h2 class="section-title">Scorecard</h2>', unsafe_allow_html=True)
    scorecard = pd.DataFrame(
        [
            {"Dimension": "Technical fit", "Score": result.technical_score, "Reviewer note": "Based on explicit skill matches in the CV."},
            {"Dimension": "Experience fit", "Score": result.experience_score, "Reviewer note": "Based on project, stakeholder and delivery signals."},
            {"Dimension": "Education fit", "Score": result.education_score, "Reviewer note": "Based on degree/certification signals."},
            {"Dimension": "Communication evidence", "Score": result.communication_score, "Reviewer note": "Based on teaching, mentoring, training and stakeholder communication signals."},
            {"Dimension": "Portfolio evidence", "Score": result.portfolio_score, "Reviewer note": "Based on project, GitHub, dashboard and prototype signals."},
        ]
    )
    st.dataframe(scorecard, use_container_width=True, hide_index=True)

    st.markdown('<h2 class="section-title">Recruiter Briefing</h2>', unsafe_allow_html=True)
    st.markdown(briefing)

    st.download_button(
        label="Download recruiter briefing as Markdown",
        data=briefing,
        file_name=f"{candidate_name.lower().replace(' ', '_')}_recruiter_briefing.md",
        mime="text/markdown",
        use_container_width=True,
    )

    st.info("Human review required: this tool structures information and suggests questions. It must not be used as an automated hiring decision system.")
else:
    st.warning("Add a CV and a job description to start the analysis.")
