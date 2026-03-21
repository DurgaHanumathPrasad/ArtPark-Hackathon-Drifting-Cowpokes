"""
APP.PY — MAIN APPLICATION
==========================
Streamlit web app.
User uploads resume → app auto-detects domain + role → full analysis.

RUN:
    streamlit run app.py
"""

import os
import sys
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PATH SETUP
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'criteria'))

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

from resume_parser_FINAL import process_resume_file
from scorer              import score_resume
from output              import generate_output

# ─────────────────────────────────────────────────────────────────────────────
# UPLOADS FOLDER
# ─────────────────────────────────────────────────────────────────────────────

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title = "Resume Analyser",
    page_icon  = "📄",
    layout     = "wide"
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1a1a2e;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .detected-box {
        background: #ede9fe;
        border-left: 5px solid #7c3aed;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border-left: 5px solid #4f46e5;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #4f46e5;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1a1a2e;
        border-bottom: 2px solid #4f46e5;
        padding-bottom: 0.4rem;
        margin: 1.5rem 0 1rem 0;
    }
    .skill-matched {
        background: #d1fae5;
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        margin: 0.2rem 0;
        color: #065f46;
        font-size: 0.9rem;
    }
    .skill-missing {
        background: #fee2e2;
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        margin: 0.2rem 0;
        color: #991b1b;
        font-size: 0.9rem;
    }
    .swot-box {
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .strengths-box  { background: #d1fae5; border-left: 5px solid #10b981; }
    .weaknesses-box { background: #fef3c7; border-left: 5px solid #f59e0b; }
    .opps-box       { background: #dbeafe; border-left: 5px solid #3b82f6; }
    .threats-box    { background: #fee2e2; border-left: 5px solid #ef4444; }
    .roadmap-stage {
        background: #f0f4ff;
        border-left: 4px solid #4f46e5;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #1a1a2e;
    }
    .current-pos {
        background: #ede9fe;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border-left: 5px solid #7c3aed;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    .goal-box {
        background: #fef9c3;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border-left: 5px solid #eab308;
        margin-top: 1rem;
        font-size: 0.95rem;
    }
    .divider {
        border: none;
        border-top: 2px solid #e5e7eb;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="main-header">📄 Resume Analyser</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your resume — domain and role are detected automatically</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# UPLOAD SECTION — just the file, nothing else
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">📁 Upload Your Resume</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose your resume file (PDF, DOCX, or TXT)",
    type = ['pdf', 'docx', 'txt'],
    help = "Domain and role will be detected automatically from your resume"
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ANALYZE BUTTON
# ─────────────────────────────────────────────────────────────────────────────

analyze = st.button("🔍  ANALYZE RESUME", use_container_width=True, type="primary")

# ─────────────────────────────────────────────────────────────────────────────
# PROCESSING PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

if analyze:

    if not uploaded_file:
        st.error("❌ Please upload a resume file first.")
        st.stop()

    # ── Save uploaded file ────────────────────────────────────────────────
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    # ── Run pipeline ──────────────────────────────────────────────────────
    with st.spinner("⏳ Reading resume and detecting domain & role..."):
        try:
            # STEP 1 — Parse resume (auto-detects domain + role)
            parsed = process_resume_file(file_path)

        except Exception as e:
            st.error(f"❌ Parsing Error: {str(e)}")
            st.stop()

    # ── Show detected domain and role ─────────────────────────────────────
    st.markdown(f"""
    <div class="detected-box">
        🔎 <strong>Auto-Detected Domain:</strong> {parsed['domain']} &nbsp;&nbsp;|&nbsp;&nbsp;
        🎯 <strong>Auto-Detected Role:</strong> {parsed['role']}
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("⏳ Calculating score..."):
        try:
            # STEP 2 — Score
            scored = score_resume(parsed)

        except Exception as e:
            st.error(f"❌ Scoring Error: {str(e)}")
            st.stop()

    with st.spinner("⏳ Generating SWOT analysis and career roadmap via AI..."):
        try:
            # STEP 3 — LLaMA API SWOT + Roadmap
            final = generate_output(scored)

        except Exception as e:
            st.error(f"❌ AI Analysis Error: {str(e)}")
            st.stop()

    st.success("✅ Analysis Complete!")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # SECTION 1 — MAIN 3 OUTPUTS
    # ─────────────────────────────────────────────────────────────────────

    st.markdown('<div class="section-header">📊 Overall Results</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🎯 Score</div>
            <div class="metric-value">{round(final['score'] * 100, 1)}%</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        exp_emoji = {"NOVICE": "🌱", "INTERMEDIATE": "⚡", "VETERAN": "🏆"}.get(final['experience'], "📅")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📅 Experience Level</div>
            <div class="metric-value">{exp_emoji} {final['experience']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        cert_emoji = "🏅" if final['cert_count'] >= 3 else "📋"
        cert_short = "Ideal Exposure" if final['cert_count'] >= 3 else "Not Ideal"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏅 Certifications</div>
            <div class="metric-value">{cert_emoji} {cert_short}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # SECTION 2 — SCORE BREAKDOWN
    # ─────────────────────────────────────────────────────────────────────

    st.markdown('<div class="section-header">📈 Score Breakdown</div>', unsafe_allow_html=True)

    b = scored['breakdown']
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Core Skills (weight × 3)**")
        prog = b['core']['matched'] / b['core']['total'] if b['core']['total'] > 0 else 0
        st.progress(prog)
        st.caption(f"{b['core']['matched']} / {b['core']['total']} matched → {b['core']['points']} / {b['core']['max']} pts")

    with c2:
        st.markdown("**Supporting Skills (weight × 2)**")
        prog = b['supporting']['matched'] / b['supporting']['total'] if b['supporting']['total'] > 0 else 0
        st.progress(prog)
        st.caption(f"{b['supporting']['matched']} / {b['supporting']['total']} matched → {b['supporting']['points']} / {b['supporting']['max']} pts")

    with c3:
        st.markdown("**Advanced Skills (weight × 1)**")
        prog = b['advanced']['matched'] / b['advanced']['total'] if b['advanced']['total'] > 0 else 0
        st.progress(prog)
        st.caption(f"{b['advanced']['matched']} / {b['advanced']['total']} matched → {b['advanced']['points']} / {b['advanced']['max']} pts")

    st.caption(f"**Total Points: {b['total_earned']} / {b['total_max']}**")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # SECTION 3 — MATCHED AND MISSING SKILLS
    # ─────────────────────────────────────────────────────────────────────

    st.markdown('<div class="section-header">🎯 Skills Analysis</div>', unsafe_allow_html=True)

    col_match, col_miss = st.columns(2)

    with col_match:
        st.markdown("### ✅ Matched Skills")
        st.markdown("**Core:**")
        if final['matched_skills']['core']:
            for s in final['matched_skills']['core']:
                st.markdown(f'<div class="skill-matched">✅ {s}</div>', unsafe_allow_html=True)
        else:
            st.caption("None matched")

        st.markdown("**Supporting:**")
        if final['matched_skills']['supporting']:
            for s in final['matched_skills']['supporting']:
                st.markdown(f'<div class="skill-matched">✅ {s}</div>', unsafe_allow_html=True)
        else:
            st.caption("None matched")

        st.markdown("**Advanced:**")
        if final['matched_skills']['advanced']:
            for s in final['matched_skills']['advanced']:
                st.markdown(f'<div class="skill-matched">✅ {s}</div>', unsafe_allow_html=True)
        else:
            st.caption("None matched")

    with col_miss:
        st.markdown("### ❌ Missing Skills")
        st.markdown("**Core:**")
        if final['missing_skills']['core']:
            for s in final['missing_skills']['core']:
                st.markdown(f'<div class="skill-missing">❌ {s}</div>', unsafe_allow_html=True)
        else:
            st.caption("None missing")

        st.markdown("**Supporting:**")
        if final['missing_skills']['supporting']:
            for s in final['missing_skills']['supporting']:
                st.markdown(f'<div class="skill-missing">❌ {s}</div>', unsafe_allow_html=True)
        else:
            st.caption("None missing")

        st.markdown("**Advanced:**")
        if final['missing_skills']['advanced']:
            for s in final['missing_skills']['advanced']:
                st.markdown(f'<div class="skill-missing">❌ {s}</div>', unsafe_allow_html=True)
        else:
            st.caption("None missing")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # SECTION 4 — SWOT ANALYSIS
    # ─────────────────────────────────────────────────────────────────────

    st.markdown('<div class="section-header">🔍 SWOT Analysis</div>', unsafe_allow_html=True)

    col_s, col_w = st.columns(2)

    with col_s:
        st.markdown(f"""
        <div class="swot-box strengths-box">
            <strong>💪 Strengths</strong><br><br>
            {final['swot']['strengths']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="swot-box opps-box">
            <strong>🚀 Opportunities</strong><br><br>
            {final['swot']['opportunities']}
        </div>
        """, unsafe_allow_html=True)

    with col_w:
        st.markdown(f"""
        <div class="swot-box weaknesses-box">
            <strong>⚠️ Weaknesses</strong><br><br>
            {final['swot']['weaknesses']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="swot-box threats-box">
            <strong>🔴 Threats</strong><br><br>
            {final['swot']['threats']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # SECTION 5 — CAREER ROADMAP
    # ─────────────────────────────────────────────────────────────────────

    st.markdown('<div class="section-header">🗺️ Career Roadmap</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="current-pos">
        <strong>📍 Your Current Position</strong><br><br>
        {final['roadmap']['current_position']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**🗺️ Stages to Reach Full Efficiency:**")
    for i, stage in enumerate(final['roadmap']['stages'], 1):
        st.markdown(f"""
        <div class="roadmap-stage">
            <strong>Stage {i}</strong> → {stage}
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="goal-box">
        <strong>🏆 Your Goal</strong><br><br>
        {final['roadmap']['goal']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.caption("Powered by Google Gemma 3 (google/gemma-3-4b-it:free) via OpenRouter")
