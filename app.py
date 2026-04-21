import threading
import time

import requests
import streamlit as st
import uvicorn

# ── Start FastAPI in a background thread (only once) ──────────────────────────
def run_fastapi():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="error")

if "fastapi_started" not in st.session_state:
    t = threading.Thread(target=run_fastapi, daemon=True)
    t.start()
    st.session_state["fastapi_started"] = True
    time.sleep(2)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PDF Extractor Pro",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

API_URL = "http://localhost:8000/extract-pdf"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
}

/* ── Animated background ── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 20% 20%, rgba(99,102,241,0.12) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(168,85,247,0.10) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(14,165,233,0.06) 0%, transparent 60%);
    animation: bgPulse 8s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes bgPulse {
    0%   { transform: scale(1) rotate(0deg); }
    100% { transform: scale(1.05) rotate(3deg); }
}

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}

.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.4);
    color: #a5b4fc;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.35rem 1rem;
    border-radius: 999px;
    margin-bottom: 1.2rem;
}

.hero-title {
    font-size: clamp(2rem, 6vw, 3.2rem);
    font-weight: 800;
    line-height: 1.15;
    background: linear-gradient(135deg, #e2e8f0 0%, #a5b4fc 40%, #c084fc 70%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
}

.hero-sub {
    font-size: 1rem;
    color: #94a3b8;
    font-weight: 400;
    max-width: 480px;
    margin: 0 auto 2.5rem;
    line-height: 1.65;
}

/* ── Upload card ── */
.upload-card {
    background: rgba(255,255,255,0.04);
    border: 1.5px dashed rgba(99,102,241,0.45);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    transition: border-color 0.3s ease, background 0.3s ease;
    backdrop-filter: blur(10px);
}

.upload-card:hover {
    border-color: rgba(99,102,241,0.75);
    background: rgba(99,102,241,0.06);
}

/* ── Streamlit uploader override ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
}

[data-testid="stFileUploader"] > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1.5px dashed rgba(99,102,241,0.5) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"] > div:hover {
    border-color: rgba(99,102,241,0.85) !important;
    background: rgba(99,102,241,0.06) !important;
}

[data-testid="stFileUploader"] label {
    color: #94a3b8 !important;
    font-size: 0.9rem !important;
}

/* ── Button ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.02em !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.35) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(99,102,241,0.55) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Result card ── */
.result-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 2rem;
    margin: 1.5rem 0;
    backdrop-filter: blur(12px);
    animation: fadeUp 0.5s ease both;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

.result-title {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 0.75rem;
}

.result-text {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    color: #e2e8f0;
    font-size: 0.95rem;
    line-height: 1.7;
    word-break: break-word;
}

/* ── Metrics ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}

.metric-pill {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: transform 0.2s ease;
}

.metric-pill:hover { transform: translateY(-3px); }

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a5b4fc, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}

.metric-label {
    font-size: 0.72rem;
    font-weight: 500;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.35rem;
}

/* ── Success / Error banners ── */
.banner-success {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 12px;
    padding: 0.9rem 1.25rem;
    color: #86efac;
    font-weight: 500;
    margin-bottom: 1.25rem;
    animation: fadeUp 0.4s ease both;
}

.banner-error {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 12px;
    padding: 0.9rem 1.25rem;
    color: #fca5a5;
    font-weight: 500;
    margin-bottom: 1rem;
    animation: fadeUp 0.4s ease both;
}

.banner-warning {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 12px;
    padding: 0.9rem 1.25rem;
    color: #fcd34d;
    font-weight: 500;
    margin-bottom: 1rem;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
}

[data-testid="stExpander"] summary {
    color: #94a3b8 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] > div {
    border-top-color: #6366f1 !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.07) !important;
    margin: 1.5rem 0 !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    color: #334155;
    font-size: 0.78rem;
}

.footer span { color: #6366f1; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">⚡ Powered by FastAPI + PyPDF2</div>
    <div class="hero-title">PDF Text Extractor</div>
    <div class="hero-sub">
        Upload any PDF and instantly extract its text content.
        Handles encrypted, multi-page, and image-based documents with ease.
    </div>
</div>
""", unsafe_allow_html=True)

# ── File Uploader ─────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Drop your PDF here or click to browse",
    type=["pdf"],
    label_visibility="visible",
)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Extract Button & Results ──────────────────────────────────────────────────
if uploaded_file is not None:

    # File info pill
    file_size_kb = round(len(uploaded_file.getvalue()) / 1024, 1)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.6rem;
                background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.25);
                border-radius:10px;padding:0.65rem 1.1rem;margin-bottom:1rem;font-size:0.88rem;color:#a5b4fc;">
        📎 <strong style="color:#c7d2fe">{uploaded_file.name}</strong>
        <span style="color:#475569;margin-left:auto">{file_size_kb} KB</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔍  Extract Text", key="extract_btn"):
        with st.spinner("Analyzing PDF..."):
            try:
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                }
                response = requests.post(API_URL, files=files)

                # ── Success ──────────────────────────────────────────────────
                if response.status_code == 200:
                    data = response.json()

                    st.markdown("""
                    <div class="banner-success">
                        ✅ &nbsp;Extraction completed successfully!
                    </div>
                    """, unsafe_allow_html=True)

                    # Metrics
                    st.markdown(f"""
                    <div class="metrics-grid">
                        <div class="metric-pill">
                            <div class="metric-value">{data.get("total_pages", 0)}</div>
                            <div class="metric-label">Pages</div>
                        </div>
                        <div class="metric-pill">
                            <div class="metric-value">{data.get("characters_extracted", 0)}</div>
                            <div class="metric-label">Characters</div>
                        </div>
                        <div class="metric-pill">
                            <div class="metric-value">{data.get("file_size_bytes", 0):,}</div>
                            <div class="metric-label">Bytes</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Extracted text
                    extracted_text = data.get("extracted_text")
                    if extracted_text:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="result-title">📝 Extracted Text Preview</div>
                            <div class="result-text">{extracted_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        note = data.get("note", "No extractable text found.")
                        st.markdown(f"""
                        <div class="banner-warning">
                            ⚠️ &nbsp;{note}
                        </div>
                        """, unsafe_allow_html=True)

                    # Raw JSON expander
                    with st.expander("🔧 View Raw API Response"):
                        st.json(data)

                # ── Error ────────────────────────────────────────────────────
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                        if isinstance(detail, dict):
                            detail = detail.get("message", str(detail))
                    except Exception:
                        detail = response.text

                    st.markdown(f"""
                    <div class="banner-error">
                        ❌ &nbsp;Error {response.status_code}: {detail}
                    </div>
                    """, unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.markdown("""
                <div class="banner-error">
                    🚨 &nbsp;Cannot reach the API. Please refresh the page and try again.
                </div>
                """, unsafe_allow_html=True)

# ── Empty state ───────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 0.5rem;color:#334155;font-size:0.88rem;">
        Supports standard, encrypted, and multi-page PDF files
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Built with <span>FastAPI</span> &amp; <span>Streamlit</span> &nbsp;·&nbsp; AI Team
</div>
""", unsafe_allow_html=True)
