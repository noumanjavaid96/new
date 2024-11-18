import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ExifTags
import requests
from io import BytesIO
import numpy as np
import pandas as pd
from skimage.metrics import structural_similarity as ssim
import fitz  # PyMuPDF for PDF handling
import docx  # For handling Word documents
from difflib import HtmlDiff, SequenceMatcher  # For text comparison
import os
import cv2
import logging
import base64
import zipfile
from typing import Dict

# Page configuration with custom theme
st.set_page_config(
    page_title="Centurion Analysis Tool",  # Title of the web app
    page_icon="https://raw.githubusercontent.com/noumanjavaid96/ai-as-an-api/refs/heads/master/image%20(39).png",  # Icon displayed in the browser tab
    layout="wide",  # Layout of the app# Initial state of the sidebar
)



# Apply custom theme using CSS
st.markdown(
    """
    <style>
    {
        --primary-color: #aba9aa;  # Primary color for the theme
        --background-color: #fdfdfd;  # Background color
        --secondary-background-color: #4a4c56;  # Secondary background color
        --text-color: #030104;  # Text color
    }
    body {
        background-color: var(--background-color);  # Set background color
    }
    </style>
    """,
    unsafe_allow_html=True  # Allow HTML in markdown
)

# Display the title with the icon
st.markdown(
    """
    <div class="title-container">
        <img class="title-icon" src="https://raw.githubusercontent.com/noumanjavaid96/ai-as-an-api/refs/heads/master/image%20(39).png" alt="Icon" width="50" height="50">
        <div class="title-text" style="font-size: 36px; font-weight: bold; color: var(--text-color);">Centurion</div>
    </div>
    """,
    unsafe_allow_html=True  # Allow HTML in markdown
)

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO
logger = logging.getLogger(__name__)  # Create a logger

UPLOAD_DIR = "uploaded_files"  # Directory to store uploaded files
NVIDIA_API_KEY = "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"  # Store API key securely

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)  # Create the directory

class NVIDIAOCRHandler:
    def __init__(self):
        self.api_key = NVIDIA_API_KEY  # Initialize API key
        self.nvai_url = "https://ai.api.nvidia.com/v1/cv/nvidia/ocdrnet"  # NVIDIA OCR API URL
        self.headers = {"Authorization": f"Bearer {self.api_key}"}  # Set headers for API requests

    def process_image(self, file_path: str) -> str:
        try:
            with open(file_path, "rb") as image_file:  # Open the image file
                files = {'image': image_file}  # Prepare file for upload
                response = requests.post(self.nvai_url, headers=self.headers, files=files)  # Send POST request
                response.raise_for_status()  # Raise an error for bad responses
                result = response.json()  # Parse JSON response
                return result.get("text", "")  # Return extracted text
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")  # Display error message
            return ""  # Return empty string on error

def save_uploaded_file(uploaded_file):
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)  # Create file path
    with open(file_path, "wb") as f:  # Open file for writing
        f.write(uploaded_file.getbuffer())  # Write uploaded file to disk
    return file_path  # Return the file path

def upload_asset(input_data: bytes, description: str) -> str:
    try:
        assets_url = "https://api.nvcf.nvidia.com/v2/nvcf/assets"  # NVIDIA asset upload URL
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",  # Set authorization header
            "Content-Type": "application/json",  # Set content type
            "accept": "application/json",  # Accept JSON response
        }

        payload = {"contentType": "image/jpeg", "description": description}  # Prepare payload for upload
        
        response = requests.post(assets_url, headers=headers, json=payload)
        response.raise_for_status()

        asset_url = response.json()["uploadUrl"]
        asset_id = response.json()["assetId"]

        response = requests.put(
            asset_url,
            data=input_data,
            headers={"x-amz-meta-nvcf-asset-description": description, "content-type": "image/jpeg"},
            timeout=300,
        )

        response.raise_for_status()
        return asset_id
    except Exception as e:
        st.error(f"Error uploading asset: {str(e)}")
        return ""

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

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class NvidiaDeepfakeDetector:
    def __init__(self):
        """
        Initialize Deepfake Detection with configuration
        """
        self.api_key = f"Bearer NVIDIA_API_KEY"
        self.upload_dir = os.getenv('UPLOAD_DIR', '/tmp')
        self.max_image_size = 5 * 1024 * 1024  # 5MB
        self.invoke_url = "https://ai.api.nvidia.com/v1/cv/hive/deepfake-image-detection"
        
        # Validate critical configurations
        self._validate_config()

    def _validate_config(self):
        """
        Validate critical configuration parameters
        """
        if not self.api_key:
            raise ValueError("NVIDIA API Key is not configured")
        
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir, exist_ok=True)

    def validate_image(self, image_bytes: bytes) -> bool:
        """
        Validate image before processing
        
        Args:
            image_bytes (bytes): Image data
        
        Returns:
            bool: Image validation status
        """
        try:
            # Check image size
            if len(image_bytes) > self.max_image_size:
                st.error(f"Image exceeds maximum size of {self.max_image_size} bytes")
                return False
            
            # Try opening image
            Image.open(BytesIO(image_bytes))
            return True
        
        except Exception as e:
            st.error(f"Image validation failed: {e}")
            return False

    def upload_asset(self, path: str, desc: str) -> str:
        """
        Upload asset to NVIDIA's asset management system
        
        Args:
            path (str): Image file path
            desc (str): Asset description
        
        Returns:
            str: Asset ID
        """
        try:
            assets_url = "https://api.nvcf.nvidia.com/v2/nvcf/assets"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "accept": "application/json",
            }
            
            # Create asset
            payload = {
                "contentType": "image/png",
                "description": desc
            }
            
            response = requests.post(assets_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            upload_url = response.json()["uploadUrl"]
            asset_id = response.json()["assetId"]
            
            # Upload image
            with open(path, "rb") as input_data:
                upload_response = requests.put(
                    upload_url,
                    data=input_data,
                    headers={"Content-Type": "image/png"},
                    timeout=300
                )
                upload_response.raise_for_status()
            
            return asset_id
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Asset upload failed: {e}")
            st.error("Failed to upload image asset")
            return ""
        """
        Detect deepfake using NVIDIA API
        
        Args:
            image_bytes (bytes): Image data
        
        Returns:
            Optional[Dict]: Detection results
        """
        # Validate image
        if not self.validate_image(image_bytes):
            return None

        try:
            # Temporary image path
            temp_path = os.path.join(self.upload_dir, "temp_deepfake_image.png")
            with open(temp_path, "wb") as f:
                f.write(image_bytes)

            # Encode image
            image_b64 = base64.b64encode(image_bytes).decode()

            # Payload preparation
            if len(image_b64) < 180_000:
                payload = {"input": [f"data:image/png;base64,{image_b64}"]}
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json",
                }
            else:
                # Large image asset upload
                asset_id = self.upload_asset(temp_path, "Deepfake Detection")
                payload = {"input": [f"data:image/png;asset_id,{asset_id}"]}
                headers = {
                    "Content-Type": "application/json",
                    "NVCF-INPUT-ASSET-REFERENCES": asset_id,
                    "Authorization": f"Bearer {self.api_key}",
                }

            # API Call
            response = requests.post(self.invoke_url, headers=headers, json=payload)
            response.raise_for_status()

            # Clean up temporary file
            os.remove(temp_path)

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Deepfake detection error: {e}")
            st.error("Deepfake detection failed")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            st.error("An unexpected error occurred")
            return None

# Streamlit Integration Function
def nvidia_deepfake_detection_app():
    st.header("🕵️ Deepfake Detection")
    
    # Initialize detector
    detector = NvidiaDeepfakeDetector()
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload an image", 
        type=["jpg", "jpeg", "png"], 
        key="deepfake_nvidia"
    )

    if uploaded_file is not None:
        # Read image
        image_bytes = uploaded_file.getvalue()
        image = Image.open(BytesIO(image_bytes))
        
        # Layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            st.write("### Detection Results")
        
        # Detect deepfake
        with st.spinner("Analyzing image..."):
            result = detector.detect_deepfake(image_bytes)
        
        # Process and display results
        if result and 'data' in result and result['data']:  # Check data list too

            deepfake_data = result['data'][0]  # Access the data list inside the 'data' key
            is_deepfake = deepfake_data.get('isDeepfake', False)  # Access isDeepfake from deepfake_data
            confidence = deepfake_data.get('confidence', 0.0)
    
            with col2:
                # Confidence metrics
                st.metric(
                    label="Deepfake Probability", 
                    value=f"{confidence:.2f}%",
                    delta="High Risk" if confidence >= 70 else "Low Risk"
                )
                
                # Risk assessment
                if confidence > 90:
                    st.error("🚨 HIGH RISK: Likely a Deepfake")
                elif confidence > 70:
                    st.warning("⚠️ MODERATE RISK: Potential Deepfake")
                else:
                    st.success("✅ LOW RISK: Likely Authentic")
        else:
            st.error("Unable to perform deepfake detection")

# Main execution

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

    def add_watermark(image, text):
        txt = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)

        font_size = max(20, image.size[0] // 20)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()  # Fallback if font not found

        bbox = font.getbbox(text)
        textwidth = bbox[2] - bbox[0]
        textheight = bbox[3] - bbox[1]

        x = image.size[0] - textwidth - 10
        y = image.size[1] - textheight - 10

        draw.text((x, y), text, font=font, fill=(255, 255, 255, 128))
        watermarked = Image.alpha_composite(image.convert('RGBA'), txt)

        return watermarked.convert('RGB')

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

def process_deepfake_detection_nvidia(image_bytes):
    header_auth = f"Bearer {NVIDIA_API_KEY}"
    invoke_url = "https://ai.api.nvidia.com/v1/cv/hive/deepfake-image-detection"

    try:
        if image_bytes is not None:
            image_b64 = base64.b64encode(image_bytes).decode()
            payload = {"input": [f"data:image/jpeg;base64,{image_b64}"]}
            headers = {
                "Content-Type": "application/json",
                "Authorization": header_auth,
                "Accept": "application/json",
            }

            response = requests.post(invoke_url, headers=headers, json= payload)
            response.raise_for_status()
            response_json = response.json()
            return response_json  # Return the result
    except requests.exceptions.RequestException as e:
        st.error(f"Error with NVIDIA API: {e}")
        return None

def nvidia_deepfake_detection_app():
    st.header("NVIDIA Deepfake Detection")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="deepfake_nvidia")

    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        image = Image.open(BytesIO(image_bytes))
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Display original image
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            # Placeholder for detection results
            st.write("### Detection Results")
        
        # Perform deepfake detection
        with st.spinner("Analyzing image for deepfake..."):
            result = process_deepfake_detection_nvidia(image_bytes)

        if result and 'data' in result and result['data']:
            deepfake_data = result['data'][0]
            
            # Deepfake confidence
            is_deepfake = deepfake_data.get('isDeepfake', 0)
            deepfake_confidence = is_deepfake * 100
            
            # Face detection confidence
            face_confidence = deepfake_data.get('confidence', 0) * 100
            
            # Update the second column with detailed results
            with col2:
                # Deepfake Probability Card
                st.markdown("""
                <div style="background-color:#f0f2f6;padding:20px;border-radius:10px;">
                <h3 style="color:#333;margin-bottom:15px;">Deepfake Analysis</h3>
                """, unsafe_allow_html=True)
                
                # Deepfake Confidence Metric
                st.metric(
                    label="Deepfake Probability", 
                    value=f"{deepfake_confidence:.1f}%",
                    delta="High Risk" if deepfake_confidence > 70 else "Low Risk"
                )
                
                # Face Detection Confidence Metric
                st.metric(
                    label="Face Detection Confidence", 
                    value=f"{face_confidence:.1f}%"
                )
                
                # Risk Assessment
                if deepfake_confidence > 90:
                    st.error("🚨 HIGH RISK: Likely a Deepfake")
                elif deepfake_confidence > 70:
                    st.warning("⚠️ MODERATE RISK: Potential Deepfake")
                else:
                    st.success("✅ LOW RISK: Likely Authentic")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Detailed Explanation
            st.markdown("### Detailed Analysis")
            
            # Create expandable sections for more information
            with st.expander("Deepfake Detection Explanation"):
                st.write("""
                - **Deepfake Probability**: Indicates the likelihood of the image being artificially generated.
                - **Face Detection Confidence**: Measures the model's confidence in detecting a face in the image.
                - High probabilities suggest potential manipulation.
                """)
            
            # Raw JSON for technical users
            with st.expander("Technical Details"):
                if result:
                    st.json(result)
        
        else:
            st.error("Unable to perform deepfake detection. Please try another image.")
    
    else:
        st.info("Please upload an image to perform deepfake detection.")
        
        
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
        "Deepfake Detection (NVIDIA)",
        "Document Comparison Tool"
    ])

    with tabs[0]:
        image_comparison_app()

    with tabs[1]:
        image_comparison_and_watermarking_app()
    
    with tabs[2]:
        nvidia_deepfake_detection_app()

    with tabs[3]:
        document_comparison_tool()

if __name__ == "__main__":
    main()
