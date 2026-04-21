import streamlit as st
import requests

st.set_page_config(page_title="PDF Text Extractor", page_icon="📄", layout="centered")

st.title("📄 PDF Text Extractor")
st.write("Upload a PDF file to extract the first 200 characters of its text via our FastAPI backend.")

# Map this to your FastAPI backend URL
API_URL = "http://127.0.0.1:8000/extract-pdf"

merged_style = """
<style>
.stButton>button {
    width: 100%;
}
</style>
"""
st.markdown(merged_style, unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

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
