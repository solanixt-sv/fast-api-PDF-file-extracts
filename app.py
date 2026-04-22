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
    page_title="PDF Intelligence Extractor",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a premium look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: none;
        color: white;
    }
    .css-1kyxreq {
        display: flex;
        justify-content: center;
    }
    .reportview-container .main .block-container {
        max-width: 800px;
    }
    .extracted-box {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #4b6cb7;
        margin-top: 1rem;
    }
    header {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 PDF Intelligence Extractor")
st.markdown("---")

col_a, col_b = st.columns([1, 1])

with col_a:
    st.subheader("Upload & Process")
    st.info("Our AI-powered engine will extract key metadata and the first 200 characters from your PDF instantly.")
    uploaded_file = st.file_uploader("Drop your PDF here", type=["pdf"])

with col_b:
    st.subheader("Why use this?")
    st.write("✅ **Fast Parsing**: Optimized for speed.")
    st.write("✅ **Secure**: Files are processed in memory.")
    st.write("✅ **Clean Metadata**: Get structured JSON responses.")
# Use environment variable for API URL with a fallback for local development
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/extract-pdf")

if uploaded_file is not None:
    if st.button("Extract Text"):
        with st.spinner("Communicating with FastAPI backend..."):
            try:
                # Prepare the file for the POST request
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Extraction Successful!")
                    
                    st.subheader("Extracted Text Preview")
                    extracted_text = data.get("extracted_text")
                    if extracted_text:
                        st.info(extracted_text)
                    else:
                        st.warning("No text could be extracted or the file is an image-based PDF.")
                    
                    st.divider()
                    
                    st.subheader("File & Metadata")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("File Size (bytes)", data.get("file_size_bytes"))
                    col2.metric("Total Pages", data.get("total_pages"))
                    col3.metric("Chars Extracted", data.get("characters_extracted"))
                    
                    with st.expander("View Full API Raw Response"):
                        st.json(data)
                        
                else:
                    st.error(f"Error {response.status_code}: {response.json().get('detail', response.text)}")
            
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to the FastAPI backend! Please make sure it is running via `uvicorn main:app --reload` on port 8000.")
