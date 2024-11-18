import streamlit as st
import fitz  # PyMuPDF
import docx
from difflib import HtmlDiff, SequenceMatcher
import os
import uuid
import logging
import requests
import zipfile
from typing import Union, Dict, Any
import time
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Document Comparison Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .upload-section {
        padding: 2rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin-bottom: 2rem;
    }
    .metrics-container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .diff-viewer {
        border: 1px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Constants
UPLOAD_DIR = "uploaded_files"
NVIDIA_API_KEY = "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"

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NVIDIAOCRHandler:
    def __init__(self):
        self.api_key = NVIDIA_API_KEY
        self.nvai_url = "https://ai.api.nvidia.com/v1/cv/nvidia/ocdrnet"
        self.assets_url = "https://api.nvcf.nvidia.com/v2/nvcf/assets"
        self.header_auth = f"Bearer {self.api_key}"

    def upload_asset(self, input_data: bytes, description: str) -> uuid.UUID:
        try:
            with st.spinner("Uploading document to NVIDIA OCR service..."):
                headers = {
                    "Authorization": self.header_auth,
                    "Content-Type": "application/json",
                    "accept": "application/json",
                }
                s3_headers = {
                    "x-amz-meta-nvcf-asset-description": description,
                    "content-type": "image/jpeg",
                }
                payload = {"contentType": "image/jpeg", "description": description}
                
                response = requests.post(self.assets_url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                
                upload_data = response.json()
                response = requests.put(
                    upload_data["uploadUrl"],
                    data=input_data,
                    headers=s3_headers,
                    timeout=300,
                )
                response.raise_for_status()
                return uuid.UUID(upload_data["assetId"])
        except Exception as e:
            st.error(f"Error uploading asset: {str(e)}")
            raise

    def process_image(self, image_path: str, output_dir: str) -> Dict[str, Any]:
        try:
            with st.spinner("Processing document with OCR..."):
                with open(image_path, "rb") as f:
                    asset_id = self.upload_asset(f.read(), "Input Image")

                inputs = {"image": f"{asset_id}", "render_label": False}
                asset_list = f"{asset_id}"
                headers = {
                    "Content-Type": "application/json",
                    "NVCF-INPUT-ASSET-REFERENCES": asset_list,
                    "NVCF-FUNCTION-ASSET-IDS": asset_list,
                    "Authorization": self.header_auth,
                }

                response = requests.post(self.nvai_url, headers=headers, json=inputs)
                response.raise_for_status()

                zip_path = f"{output_dir}.zip"
                with open(zip_path, "wb") as out:
                    out.write(response.content)

                with zipfile.ZipFile(zip_path, "r") as z:
                    z.extractall(output_dir)

                os.remove(zip_path)
                return {
                    "status": "success",
                    "output_directory": output_dir,
                    "files": os.listdir(output_dir)
                }
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            raise

def save_uploaded_file(uploaded_file):
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def extract_text_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_word(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def compare_texts(text1, text2):
    differ = HtmlDiff()
    return differ.make_file(
        text1.splitlines(),
        text2.splitlines(),
        fromdesc="Original",
        todesc="Modified",
        context=True,
        numlines=2
    )

def calculate_similarity(text1, text2):
    matcher = SequenceMatcher(None, text1, text2)
    return matcher.ratio()

# Main App
def main():
    st.title("📄 Advanced Document Comparison Tool")
    st.markdown("### Compare documents and detect changes with AI-powered OCR")

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This tool allows you to:
        - Compare PDF and Word documents
        - Process images using NVIDIA's OCR
        - Detect and highlight changes
        - Generate similarity metrics
        """)
        
        st.header("🛠️ Settings")
        show_metadata = st.checkbox("Show Metadata", value=True)
        show_detailed_diff = st.checkbox("Show Detailed Differences", value=True)

    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Original Document")
        original_file = st.file_uploader(
            "Upload original document",
            type=["pdf", "docx", "jpg", "jpeg", "png"],
            help="Supported formats: PDF, DOCX, JPG, PNG"
        )

    with col2:
        st.markdown("### Modified Document")
        modified_file = st.file_uploader(
            "Upload modified document",
            type=["pdf", "docx", "jpg", "jpeg", "png"],
            help="Supported formats: PDF, DOCX, JPG, PNG"
        )

    if original_file and modified_file:
        try:
            with st.spinner("Processing documents..."):
                # Initialize OCR handler
                ocr_handler = NVIDIAOCRHandler()
                
                # Process files
                original_file_path = save_uploaded_file(original_file)
                modified_file_path = save_uploaded_file(modified_file)
                
                # Extract text based on file type
                original_ext = os.path.splitext(original_file.name)[1].lower()
                modified_ext = os.path.splitext(modified_file.name)[1].lower()
                
                # Process original document
                if original_ext in ['.jpg', '.jpeg', '.png']:
                    original_result = ocr_handler.process_image(original_file_path, f"{UPLOAD_DIR}/original_ocr")
                    original_text = open(f"{UPLOAD_DIR}/original_ocr/text.txt").read()
                elif original_ext == '.pdf':
                    original_text = extract_text_pdf(original_file_path)
                else:
                    original_text = extract_text_word(original_file_path)

                # Process modified document
                if modified_ext in ['.jpg', '.jpeg', '.png']:
                    modified_result = ocr_handler.process_image(modified_file_path, f"{UPLOAD_DIR}/modified_ocr")
                    modified_text = open(f"{UPLOAD_DIR}/modified_ocr/text.txt").read()
                elif modified_ext == '.pdf':
                    modified_text = extract_text_pdf(modified_file_path)
                else:
                    modified_text = extract_text_word(modified_file_path)

                # Calculate similarity
                similarity_score = calculate_similarity(original_text, modified_text)
                
                # Display results
                st.markdown("### 📊 Analysis Results")
                
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                with metrics_col1:
                    st.metric("Similarity Score", f"{similarity_score:.2%}")
                with metrics_col2:
                    st.metric("Changes Detected", "Yes" if similarity_score < 1 else "No")
                with metrics_col3:
                    st.metric("Processing Status", "Complete ✅")

                if show_detailed_diff:
                    st.markdown("### 🔍 Detailed Comparison")
                    diff_html = compare_texts(original_text, modified_text)
                    st.components.v1.html(diff_html, height=600, scrolling=True)

                # Download results
                st.markdown("### 💾 Download Results")
                if st.button("Generate Report"):
                    with st.spinner("Generating report..."):
                        # Add report generation logic here
                        time.sleep(2)
                        st.success("Report generated successfully!")
                        st.download_button(
                            label="Download Report",
                            data=diff_html,
                            file_name="comparison_report.html",
                            mime="text/html"
                        )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Error processing documents: {str(e)}")
    else:
        st.info("👆 Please upload both documents to begin comparison")

if __name__ == "__main__":
    main()
