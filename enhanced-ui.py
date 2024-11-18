import streamlit as st
from fuzzywuzzy import fuzz
from docx import Document
from difflib import Differ
import requests, base64

# Helper function to extract text from a Word document
def extract_text_from_doc(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Function to compare documents and return True/False for content differences
def check_text_similarity(source_text, uploaded_text):
    differ = Differ()
    diffs = list(differ.compare(source_text.splitlines(), uploaded_text.splitlines()))
    
    # Check if there are any differences
    differences = [line for line in diffs if line.startswith("- ") or line.startswith("+ ")]
    is_identical = len(differences) == 0  # True if no differences
    
    return is_identical, differences

# Mock metadata function (expand for real metadata extraction if needed)
def check_metadata():
    # Example: Replace with real metadata comparison if available
    source_metadata = {"author": "John Doe", "created": "2023-01-01"}
    uploaded_metadata = {"author": "John Doe", "created": "2023-01-01"}  # Simulated identical metadata
    
    is_metadata_identical = source_metadata == uploaded_metadata
    return is_metadata_identical, source_metadata, uploaded_metadata

# Function to detect deepfake using NVIDIA API
def detect_deepfake(image_path):
    header_auth = "Bearer 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"
    invoke_url = "https://ai.api.nvidia.com/v1/cv/hive/deepfake-image-detection"

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    if len(image_b64) < 180_000:
        payload = {
            "input": [f"data:image/png;base64,{image_b64}"]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": header_auth,
            "Accept": "application/json",
        }
    else:
        asset_id = upload_asset(image_path, "Input Image")
        
        payload = {
            "input": [f"data:image/png;asset_id,{asset_id}"]
        }
        headers = {
            "Content-Type": "application/json",
            "NVCF-INPUT-ASSET-REFERENCES": asset_id,
            "Authorization": header_auth,
        }

    response = requests.post(invoke_url, headers=headers, json=payload)
    return response.json()

# Function to detect AI-generated images using NVIDIA API
def detect_ai_generated(image_path):
    header_auth = "Bearer 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"
    invoke_url = "https://ai.api.nvidia.com/v1/cv/hive/ai-generated-image-detection"

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    if len(image_b64) < 180_000:
        payload = {
            "input": [f"data:image/png;base64,{image_b64}"]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": header_auth,
            "Accept": "application/json",
        }
    else:
        asset_id = upload_asset(image_path, "Input Image")
        
        payload = {
            "input": [f"data:image/png;asset_id,{asset_id}"]
        }
        headers = {
            "Content-Type": "application/json",
            "NVCF-INPUT-ASSET-REFERENCES": asset_id,
            "Authorization": header_auth,
        }

    response = requests.post(invoke_url, headers=headers, json=payload)
    return response.json()

# Function to identify who is in a photo using NVIDIA Kosmos-2 API
def identify_photo(image_path):
    header_auth = "Bearer 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"
    invoke_url = "https://ai.api.nvidia.com/v1/vlm/microsoft/kosmos-2"

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    assert len(image_b64) < 180_000, \
      "To upload larger images, use the assets API (see docs)"

    headers = {
      "Authorization": header_auth,
      "Accept": "application/json"
    }

    payload = {
      "messages": [
        {
          "role": "user",
          "content": f'Who is in this photo? <img src="data:image/png;base64,{image_b64}" />'
        }
      ],
      "max_tokens": 1024,
      "temperature": 0.20,
      "top_p": 0.20
    }

    response = requests.post(invoke_url, headers=headers, json=payload)
    return response.json()

# Streamlit UI
st.title("AI Analysis Tool")

# Tabs for different models
model_tabs = st.tabs(["Document Comparison", "Deepfake Detection", "AI-Generated Image Detection", "Photo Identification"])

with model_tabs[0]:
    st.subheader("Document Comparison")
    source_file = st.file_uploader("Upload Source Document (.docx)", type="docx")
    uploaded_file = st.file_uploader("Upload Document to Compare (.docx)", type="docx")

    if source_file and uploaded_file:
        source_text = extract_text_from_doc(source_file)
        uploaded_text = extract_text_from_doc(uploaded_file)
        
        # Check for text differences
        text_match, differences = check_text_similarity(source_text, uploaded_text)
        st.write("**Content Match:**", text_match)
        
        # Display differences if any
        if not text_match:
            st.write("**Differences Found:**")
            for line in differences:
                if line.startswith("- "):
                    st.write(f"Removed: {line[2:]}")
                elif line.startswith("+ "):
                    st.write(f"Added: {line[2:]}")
        
        # Check for metadata differences
        metadata_match, source_metadata, uploaded_metadata = check_metadata()
        st.write("**Metadata Match:**", metadata_match)
        
        # Display metadata if different
        if not metadata_match:
            st.write("**Metadata Differences:**")
            st.write("Source Metadata:", source_metadata)
            st.write("Uploaded Metadata:", uploaded_metadata)

with model_tabs[1]:
    st.subheader("Deepfake Detection")
    image_file = st.file_uploader("Upload Image for Deepfake Detection", type=["png", "jpg", "jpeg"])

    if image_file:
        with open("temp_image.png", "wb") as f:
            f.write(image_file.getbuffer())
        result = detect_deepfake("temp_image.png")
        st.write("**Deepfake Detection Result:**")
        st.write(result)

with model_tabs[2]:
    st.subheader("AI-Generated Image Detection")
    image_file = st.file_uploader("Upload Image for AI-Generated Image Detection", type=["png", "jpg", "jpeg"])

    if image_file:
        with open("temp_image.png", "wb") as f:
            f.write(image_file.getbuffer())
        result = detect_ai_generated("temp_image.png")
        st.write("**AI-Generated Image Detection Result:**")
        st.write(result)

with model_tabs[3]:
    st.subheader("Photo Identification")
    image_file = st.file_uploader("Upload Photo for Identification", type=["png", "jpg", "jpeg"])

    if image_file:
        with open("temp_image.png", "wb") as f:
            f.write(image_file.getbuffer())
        result = identify_photo("temp_image.png")
        st.write("**Photo Identification Result:**")
        st.write(result)

st.info("Please upload the required files for each analysis.")