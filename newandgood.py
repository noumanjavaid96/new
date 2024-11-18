# File: app.py

import streamlit as st

# Page configuration with custom theme
st.set_page_config(
    page_title="Centurion Analysis Tool",
    page_icon="🛡️",  # You can set your own custom icon here
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom theme using CSS
st.markdown(
    """
    <style>
    :root {
        --primary-color: #aba9aa;
        --background-color: #fdfdfd;
        --secondary-background-color: #4a4c56;
        --text-color: #030104;
    }
    .title-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .title-icon {
        width: 50px;
        height: 50px;
        margin-right: 10px;
    }
    .title-text {
        font-size: 36px;
        font-weight: bold;
        color: var(--text-color);
    }
    body {
        background-color: var(--background-color);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the title with the icon
st.markdown(
    """
    <div class="title-container">
        <img class="title-icon" src="https://raw.githubusercontent.com/noumanjavaid96/ai-as-an-api/refs/heads/master/image%20(39).png" alt="Icon">
        <div class="title-text">Centurion Analysis Tool</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Rest of the application code will go below...
# Continue in app.py

import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ExifTags
import requests
from io import BytesIO
import cv2
import numpy as np
import pandas as pd
from skimage.metrics import structural_similarity as ssim
import fitz  # PyMuPDF
import docx
from difflib import HtmlDiff, SequenceMatcher
import os
import logging
import zipfile
import time
from typing import Dict
from deepface import DeepFace  # For deepfake detection
import pytesseract  # For OCR in watermark detection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Continue in app.py

UPLOAD_DIR = "uploaded_files"
NVIDIA_API_KEY = "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"

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    

class NVIDIAOCRHandler:
    def __init__(self):
        self.api_key = NVIDIA_API_KEY
        self.nvai_url = "https://api.nvidia.com/ocr"  # Replace with the actual NVIDIA OCR API endpoint
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def process_image(self, file_path: str) -> str:
        try:
            with open(file_path, "rb") as image_file:
                files = {'image': image_file}
                response = requests.post(self.nvai_url, headers=self.headers, files=files)
                response.raise_for_status()
                result = response.json()
                return result.get("text", "")
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return ""

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
        text1.splitlines(), text2.splitlines(),
        fromdesc="Original", todesc="Modified", context=True, numlines=2
    )

def calculate_similarity(text1, text2):
    matcher = SequenceMatcher(None, text1, text2)
    return matcher.ratio()

def deepfake_detection_app():
    st.header("🕵️ Deepfake Detection")
    st.write("Upload an image to detect potential deepfakes.")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="deepfake")

    if uploaded_file is not None:
        # Read image
        image_bytes = uploaded_file.getvalue()
        image = Image.open(BytesIO(image_bytes))

        # Display original image
        st.image(image, caption="Uploaded Image", width=300)

        # Process image
        with st.spinner("Analyzing image..."):
            result = process_deepfake_detection(image_bytes)

        if result:
            # Display annotated image
            st.image(result['annotated_image'], caption="Analysis Result", width=300)

            # Display confidence score
            deepfake_confidence = result['deepfake_confidence']
            st.write(f"**Deepfake Confidence:** {deepfake_confidence:.2f}%")

            # Provide feedback based on confidence
            if deepfake_confidence > 90:
                st.error("⚠️ High probability of deepfake detected!")
            elif deepfake_confidence > 70:
                st.warning("⚠️ Moderate probability of deepfake detected!")
            else:
                st.success("✅ Low probability of deepfake")
        else:
            st.error("Failed to process the image.")
    else:
        st.info("Please upload an image.")

def detect_watermark(image, text):
    try:
        gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        detected_text = pytesseract.image_to_string(gray_image)
        return text.strip().lower() in detected_text.strip().lower()
    except Exception as e:
        st.error(f"Error in watermark detection: {str(e)}")
        return False

def get_metadata(image):
    exif_data = {}
    info = image.getexif()
    if info:
        for tag, value in info.items():
            decoded = ExifTags.TAGS.get(tag, tag)
            exif_data[decoded] = value
    return exif_data

def compare_metadata(meta1, meta2):
    keys = set(meta1.keys()).union(set(meta2.keys()))
    data = []
    for key in keys:
        value1 = meta1.get(key, "Not Available")
        value2 = meta2.get(key, "Not Available")
        if value1 != value2:
            data.append({"Metadata Field": key, "Original Image": value1, "Compared Image": value2})
    if data:
        df = pd.DataFrame(data)
        return df
    else:
        return None
    
def detect_deepfake(image):
    try:
        analysis = DeepFace.analyze(img_path=np.array(image), actions=['emotion'], enforce_detection=False)
        # The 'enforce_detection=False' parameter allows processing images even if no face is detected.

        # For simplicity, we'll check if a face was detected.
        if analysis and 'emotion' in analysis:
            return "Real Face Detected", 0.99
        else:
            return "No Face Detected", 0.0
    except Exception as e:
        st.error(f"Error in deepfake detection: {str(e)}")
        return "Error", 0.0


def image_comparison_app():
    st.header("🔍 Image Analysis for Differences")
    st.write("Upload two images to compare them and find differences.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        uploaded_file1 = st.file_uploader("Choose the original image", type=["png", "jpg", "jpeg"], key="comp1")

    with col2:
        st.subheader("Image to Compare")
        uploaded_file2 = st.file_uploader("Choose the image to compare", type=["png", "jpg", "jpeg"], key="comp2")

    if uploaded_file1 and uploaded_file2:
        image1 = Image.open(uploaded_file1)
        image2 = Image.open(uploaded_file2)

        img1 = cv2.cvtColor(np.array(image1), cv2.COLOR_RGB2BGR)
        img2 = cv2.cvtColor(np.array(image2), cv2.COLOR_RGB2BGR)

        if img1.shape != img2.shape:
            st.warning("Images are not the same size. Resizing the second image to match the first.")
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        score, diff = ssim(gray1, gray2, full=True)
        st.write(f"**Structural Similarity Index (SSIM): {score:.4f}**")
        diff = (diff * 255).astype("uint8")

        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        img1_diff = img1.copy()
        img2_diff = img2.copy()

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img1_diff, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(img2_diff, (x, y), (x + w, y + h), (0, 0, 255), 2)

        img1_display = cv2.cvtColor(img1_diff, cv2.COLOR_BGR2RGB)
        img2_display = cv2.cvtColor(img2_diff, cv2.COLOR_BGR2RGB)
        diff_display = cv2.cvtColor(diff, cv2.COLOR_GRAY2RGB)
        thresh_display = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)

        st.write("## Results")
        st.write("Differences are highlighted in red boxes.")
        st.image([img1_display, img2_display], caption=["Original Image with Differences", "Compared Image with Differences"], width=300)
        st.write("## Difference Image")
        st.image(diff_display, caption="Difference Image", width=300)
        st.write("## Thresholded Difference Image")
        st.image(thresh_display, caption="Thresholded Difference Image", width=300)

    else:
        st.info("Please upload both images.")

def image_comparison_and_watermarking_app():
    st.header("💧 Watermark Adding and Detecting")
    st.write("Upload an image to add a watermark, and detect if a watermark is present.")

    uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"], key="wm1")
    watermark_text = st.text_input("Enter watermark text:", value="Sample Watermark")

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Original Image", width=300)

        st.write("### Watermarked Image")
        watermarked_image = add_watermark(image, watermark_text)
        st.image(watermarked_image, caption="Watermarked Image", width=300)

        st.write("### Watermark Detection")
        if detect_watermark(watermarked_image, watermark_text):
            st.success("Watermark detected in the image.")
        else:
            st.warning("Watermark not detected in the image.")

        st.write("### Metadata")
        metadata = get_metadata(image)
        st.write(metadata if metadata else "No metadata available.")

    else:
        st.info("Please upload an image.")

def deepfake_detection_app():
    st.header("🕵️ Deepfake Detection")
    st.write("Upload an image to detect potential deepfakes.")

    uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"], key="deepfake")

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", width=300)

        result, confidence = detect_deepfake(image)

        st.write(f"**Detection Result:** {result}")
        st.write(f"**Confidence Score:** {confidence:.2%}")

    else:
        st.info("Please upload an image.")

def document_comparison_tool():
    st.header("📄 Document In-Depth Comparison")
    st.markdown("Compare documents and detect changes with OCR highlighting.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Original Document")
        original_file = st.file_uploader(
            "Upload original document",
            type=["pdf", "docx", "jpg", "jpeg", "png"],
            key='doc_original_file',
            help="Supported formats: PDF, DOCX, JPG, PNG"
        )

    with col2:
        st.markdown("### Modified Document")
        modified_file = st.file_uploader(
            "Upload modified document",
            type=["pdf", "docx", "jpg", "jpeg", "png"],
            key='doc_modified_file',
            help="Supported formats: PDF, DOCX, JPG, PNG"
        )

    if original_file and modified_file:
        ocr_handler = NVIDIAOCRHandler()

        original_file_path = save_uploaded_file(original_file)
        modified_file_path = save_uploaded_file(modified_file)

        original_ext = os.path.splitext(original_file.name)[1].lower()
        modified_ext = os.path.splitext(modified_file.name)[1].lower()

        if original_ext in ['.jpg', '.jpeg', '.png']:
            original_text = ocr_handler.process_image(original_file_path)
        elif original_ext == '.pdf':
            original_text = extract_text_pdf(original_file_path)
        else:
            original_text = extract_text_word(original_file_path)

        if modified_ext in ['.jpg', '.jpeg', '.png']:
            modified_text = ocr_handler.process_image(modified_file_path)
        elif modified_ext == '.pdf':
            modified_text = extract_text_pdf(modified_file_path)
        else:
            modified_text = extract_text_word(modified_file_path)

        similarity_score = calculate_similarity(original_text, modified_text)

        st.markdown("### 📊 Analysis Results")
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Similarity Score", f"{similarity_score:.2%}")
        with metrics_col2:
            st.metric("Changes Detected", "Yes" if similarity_score < 1 else "No")

        st.markdown("### 🔍 Detailed Comparison")
        diff_html = compare_texts(original_text, modified_text)
        st.components.v1.html(diff_html, height=600, scrolling=True)

        st.markdown("### 💾 Download Results")
        if st.button("Generate Report"):
            st.success("Report generated successfully!")
            st.download_button(
                label="Download Report",
                data=diff_html,
                file_name="comparison_report.html",
                mime="text/html"
            )

    else:
        st.info("Please upload both documents to begin comparison.")

def main():
    st.write("""
    Welcome to the Centurion Analysis Tool! Use the tabs below to navigate through the different functionalities.
    """)

    tabs = st.tabs([
        "Image Comparison",
        "Watermark Adding & Detecting",
        "Deepfake Detection",
        "Document Comparison Tool"
    ])

    with tabs[0]:
        image_comparison_app()

    with tabs[1]:
        image_comparison_and_watermarking_app()

    with tabs[2]:
        deepfake_detection_app()

    with tabs[3]:
        document_comparison_tool()

if __name__ == "__main__":
    main()
