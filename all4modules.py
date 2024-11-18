import streamlit as st
from fuzzywuzzy import fuzz
from docx import Document
from difflib import Differ
import requests
import base64
import os
import json

# Constants
NVIDIA_API_KEY = "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"
TEMP_IMAGE_PATH = "temp_image.png"

def upload_asset(path, desc):
    """Upload asset to NVIDIA API for large files"""
    assets_url = "https://api.nvcf.nvidia.com/v2/nvcf/assets"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "accept": "application/json",
    }
    payload = {
        "contentType": "image/png",
        "description": desc
    }
    
    response = requests.post(assets_url, headers=headers, json=payload, timeout=30)
    
    if response.status_code != 200:
        st.error(f"Failed to upload asset: {response.text}")
        return None
        
    data = response.json()
    current_pre_signed_url = data["uploadUrl"]
    asset_id = data["assetId"]

    headers = {
        "Content-Type": "image/png",
        "x-amz-meta-nvcf-asset-description": desc,
    }

    with open(path, "rb") as input_data:
        response = requests.put(
            current_pre_signed_url,
            data=input_data,
            headers=headers,
            timeout=300,
        )
    
    if response.status_code != 200:
        st.error("Failed to upload to pre-signed URL")
        return None
        
    return asset_id

def extract_text_from_doc(file):
    """Extract text from a Word document"""
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def check_text_similarity(source_text, uploaded_text):
    """Compare two texts and return differences"""
    differ = Differ()
    diffs = list(differ.compare(source_text.splitlines(), uploaded_text.splitlines()))
    differences = [line for line in diffs if line.startswith("- ") or line.startswith("+ ")]
    is_identical = len(differences) == 0
    return is_identical, differences

def check_metadata():
    """Compare document metadata"""
    source_metadata = {"author": "John Doe", "created": "2023-01-01"}
    uploaded_metadata = {"author": "John Doe", "created": "2023-01-01"}
    is_metadata_identical = source_metadata == uploaded_metadata
    return is_metadata_identical, source_metadata, uploaded_metadata

def process_image(image_path, api_endpoint, is_kosmos=False):
    """Generic function to process images through NVIDIA APIs"""
    try:
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if is_kosmos:
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
        else:
            if len(image_b64) < 180_000:
                payload = {
                    "input": [f"data:image/png;base64,{image_b64}"]
                }
            else:
                asset_id = upload_asset(image_path, "Input Image")
                if not asset_id:
                    return None
                
                payload = {
                    "input": [f"data:image/png;asset_id,{asset_id}"]
                }
                headers["NVCF-INPUT-ASSET-REFERENCES"] = asset_id

        response = requests.post(api_endpoint, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def main():
    st.title("AI Analysis Tool")
    st.write("Upload documents for comparison and images for AI analysis")

    tabs = st.tabs(["Document Comparison", "Deepfake Detection", "AI-Generated Detection", "Photo Identification"])

    with tabs[0]:
        st.subheader("Document Comparison")
        source_file = st.file_uploader("Upload Source Document (.docx)", type="docx", key="source")
        compare_file = st.file_uploader("Upload Document to Compare (.docx)", type="docx", key="compare")

        if source_file and compare_file:
            source_text = extract_text_from_doc(source_file)
            compare_text = extract_text_from_doc(compare_file)
            
            is_identical, differences = check_text_similarity(source_text, compare_text)
            
            st.write("### Results")
            st.write(f"Documents are {'identical' if is_identical else 'different'}")
            
            if not is_identical:
                st.write("### Differences Found")
                for diff in differences:
                    if diff.startswith("- "):
                        st.markdown(f"🔴 Removed: `{diff[2:]}`")
                    elif diff.startswith("+ "):
                        st.markdown(f"🟢 Added: `{diff[2:]}`")

    with tabs[1]:
        st.subheader("Deepfake Detection")
        image_file = st.file_uploader("Upload image for deepfake detection", type=["png", "jpg", "jpeg"], key="deepfake")
        
        if image_file:
            with open(TEMP_IMAGE_PATH, "wb") as f:
                f.write(image_file.getbuffer())
            
            result = process_image(
                TEMP_IMAGE_PATH,
                "https://ai.api.nvidia.com/v1/cv/hive/deepfake-image-detection"
            )
            
            if result:
                st.json(result)

    with tabs[2]:
        st.subheader("AI-Generated Image Detection")
        image_file = st.file_uploader("Upload image for AI generation detection", type=["png", "jpg", "jpeg"], key="ai_gen")
        
        if image_file:
            with open(TEMP_IMAGE_PATH, "wb") as f:
                f.write(image_file.getbuffer())
            
            result = process_image(
                TEMP_IMAGE_PATH,
                "https://ai.api.nvidia.com/v1/cv/hive/ai-generated-image-detection"
            )
            
            if result:
                st.json(result)
                if 'data' in result and result['data']:
                    data = result['data'][0]
                    st.write(f"### AI Generation Probability: {data['is_ai_generated']:.2%}")
                    
                    if 'possible_sources' in data:
                        st.write("### Possible AI Sources:")
                        sources = data['possible_sources']
                        for source, prob in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]:
                            st.write(f"- {source}: {prob:.2%}")

    with tabs[3]:
        st.subheader("Photo Identification (Kosmos-2)")
        image_file = st.file_uploader("Upload photo for identification", type=["png", "jpg", "jpeg"], key="kosmos")
        
        if image_file:
            with open(TEMP_IMAGE_PATH, "wb") as f:
                f.write(image_file.getbuffer())
            
            result = process_image(
                TEMP_IMAGE_PATH,
                "https://ai.api.nvidia.com/v1/vlm/microsoft/kosmos-2",
                is_kosmos=True
            )
            
            if result:
                st.json(result)

    # Cleanup temporary files
    if os.path.exists(TEMP_IMAGE_PATH):
        os.remove(TEMP_IMAGE_PATH)

if __name__ == "__main__":
    main()