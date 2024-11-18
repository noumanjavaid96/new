import streamlit as st
from fuzzywuzzy import fuzz
from docx import Document
from difflib import Differ
import requests
import base64
import json
import os

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
    st.write("Upload images for AI analysis")

    tabs = st.tabs(["Deepfake Detection", "AI-Generated Detection", "Photo Identification"])

    with tabs[0]:
        st.subheader("Deepfake Detection")
        image_file = st.file_uploader("Upload image for deepfake detection", type=["png", "jpg", "jpeg"], key="deepfake")
        
        if image_file:
            with open(TEMP_IMAGE_PATH, "wb") as f:
                f.write(image_file.getbuffer())
            
            with st.spinner("Analyzing image for deepfake detection..."):
                result = process_image(
                    TEMP_IMAGE_PATH,
                    "https://ai.api.nvidia.com/v1/cv/hive/deepfake-image-detection"
                )
            
            if result and 'data' in result:
                data = result['data'][0]
                if 'bounding_boxes' in data:
                    for box in data['bounding_boxes']:
                        confidence = box['is_deepfake'] * 100
                        st.metric("Deepfake Confidence", f"{confidence:.1f}%")
                        
                        # Create a progress bar for confidence
                        st.progress(confidence/100)
                        
                        if confidence > 90:
                            st.error("⚠️ High probability of deepfake detected!")
                        elif confidence > 70:
                            st.warning("⚠️ Moderate probability of deepfake detected!")
                        else:
                            st.success("✅ Low probability of deepfake")
                
                # Display the analyzed image
                st.image(image_file, caption="Analyzed Image", use_column_width=True)

    with tabs[1]:
        st.subheader("AI-Generated Image Detection")
        image_file = st.file_uploader("Upload image for AI generation detection", type=["png", "jpg", "jpeg"], key="ai_gen")
        
        if image_file:
            with open(TEMP_IMAGE_PATH, "wb") as f:
                f.write(image_file.getbuffer())
            
            with st.spinner("Analyzing image for AI generation..."):
                result = process_image(
                    TEMP_IMAGE_PATH,
                    "https://ai.api.nvidia.com/v1/cv/hive/ai-generated-image-detection"
                )
            
            if result and 'data' in result:
                data = result['data'][0]
                confidence = data['is_ai_generated'] * 100
                st.metric("AI Generation Confidence", f"{confidence:.1f}%")
                
                # Create a progress bar for confidence
                st.progress(confidence/100)
                
                if 'possible_sources' in data:
                    st.subheader("Possible AI Sources")
                    sources = data['possible_sources']
                    
                    # Create a bar chart for top sources
                    top_sources = dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5])
                    st.bar_chart(top_sources)
                    
                    # Display detailed percentages
                    for source, prob in top_sources.items():
                        st.write(f"- {source}: {prob*100:.2f}%")
                
                # Display the analyzed image
                st.image(image_file, caption="Analyzed Image", use_column_width=True)

    with tabs[2]:
        st.subheader("Photo Identification (Kosmos-2)")
        image_file = st.file_uploader("Upload photo for identification", type=["png", "jpg", "jpeg"], key="kosmos")
        
        if image_file:
            with open(TEMP_IMAGE_PATH, "wb") as f:
                f.write(image_file.getbuffer())
            
            with st.spinner("Analyzing photo..."):
                result = process_image(
                    TEMP_IMAGE_PATH,
                    "https://ai.api.nvidia.com/v1/vlm/microsoft/kosmos-2",
                    is_kosmos=True
                )
            
            if result:
                st.write("### Analysis Result")
                st.json(result)
                
                # Display the analyzed image
                st.image(image_file, caption="Analyzed Image", use_column_width=True)

    # Cleanup temporary files
    if os.path.exists(TEMP_IMAGE_PATH):
        os.remove(TEMP_IMAGE_PATH)

if __name__ == "__main__":
    main()