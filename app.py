import streamlit as st
import requests
import os
import subprocess
import time
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# --- Auto-start Backend ---
if not is_port_in_use(8000):
    with st.spinner("Starting Backend Engine..."):
        subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])
        time.sleep(3) # Wait for backend to initialize
# --------------------------

st.set_page_config(
    page_title="PDF Intel - Professional Extraction",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .stApp {
        background: transparent;
    }

    /* Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        margin-bottom: 20px;
    }
    
    .stButton>button {
        background: #1e3a8a;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: none;
        box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.3);
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background: #1e40af;
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(30, 58, 138, 0.4);
    }

    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e5e7eb;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        color: white;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] li {
        color: #f8fafc !important;
    }
    
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/pdf.png", width=80)
    st.title("Admin Panel")
    st.markdown("---")
    st.subheader("System Status")
    if is_port_in_use(8000):
        st.success("● AI Engine: Online")
    else:
        st.error("● AI Engine: Offline")
    
    st.markdown("---")
    st.subheader("Project Info")
    st.write("✅ **Fast Parsing**: Optimized for high speed.")
    st.write("✅ **Secure**: In-memory processing.")
    st.write("✅ **Clean**: Structured JSON outputs.")
    st.info("System version: 1.2.0-stable")

# --- Main Page ---
st.title("💼 PDF Intelligence Dashboard")
st.caption("Advanced document analysis and metadata extraction platform")

# Main Container
main_col, side_col = st.columns([2, 1])

with main_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📤 Data Ingestion")
    uploaded_file = st.file_uploader("Upload your PDF document for analysis", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        st.write(f"📂 Selected: **{uploaded_file.name}**")
        if st.button("Process Document"):
            API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/extract-pdf")
            with st.spinner("Processing in progress..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post(API_URL, files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.last_result = data
                        st.balloons()
                    else:
                        st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"🚨 Connection failed: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# Display Results if available
if 'last_result' in st.session_state:
    data = st.session_state.last_result
    
    # Text Preview Area
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📑 Content Intelligence")
    text = data.get("extracted_text")
    if text:
        st.markdown(f"> {text}")
    else:
        st.warning("No extractable text found in this document.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Metrics Row
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Pages", data.get("total_pages"))
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Char Count", data.get("characters_extracted"))
        st.markdown('</div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("File Size", f"{data.get('file_size_bytes') / 1024:.1f} KB")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("🔍 View Raw JSON Intelligence"):
        st.json(data)
else:
    with side_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Getting Started")
        st.write("1. Upload a PDF file in the left panel.")
        st.write("2. Click 'Process Document'.")
        st.write("3. View extracted text and metadata.")
        st.image("https://img.icons8.com/ios/100/null/document--v1.png", width=80)
        st.markdown('</div>', unsafe_allow_html=True)
