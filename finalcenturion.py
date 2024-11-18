import streamlit as st
import requests
import base64
import cv2
import numpy as np
from PIL import Image
import io

# Constants
NVIDIA_API_KEY = "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"

def draw_bounding_box(image, vertices, confidence, is_deepfake):
    """Draw bounding box with confidence score on image"""
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # Extract coordinates
    x1, y1 = int(vertices[0]['x']), int(vertices[0]['y'])
    x2, y2 = int(vertices[1]['x']), int(vertices[1]['y'])
    
    # Calculate confidence percentages
    deepfake_conf = is_deepfake * 100
    bbox_conf = confidence * 100
    
    # Choose color based on deepfake confidence (red for high confidence)
    color = (0, 0, 255) if deepfake_conf > 70 else (0, 255, 0)
    
    # Draw bounding box
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    
    # Add text with confidence scores
    label = f"Deepfake ({deepfake_conf:.1f}%), Face ({bbox_conf:.1f}%)"
    cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # Convert back to RGB for Streamlit
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def process_image(image_bytes):
    """Process image through NVIDIA's deepfake detection API"""
    image_b64 = base64.b64encode(image_bytes).decode()
    
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "input": [f"data:image/png;base64,{image_b64}"]
    }
    
    try:
        response = requests.post(
            "https://ai.api.nvidia.com/v1/cv/hive/deepfake-image-detection",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def main():
    st.title("Deepfake Detection")
    st.write("Upload an image to detect potential deepfakes")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display original image
        image_bytes = uploaded_file.getvalue()
        image = Image.open(io.BytesIO(image_bytes))
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(image, use_column_width=True)
        
        # Process image
        with st.spinner("Analyzing image..."):
            result = process_image(image_bytes)
        
        if result and 'data' in result:
            data = result['data'][0]
            
            # Display results
            if 'bounding_boxes' in data:
                for box in data['bounding_boxes']:
                    # Draw bounding box on image
                    annotated_image = draw_bounding_box(
                        image,
                        box['vertices'],
                        box['bbox_confidence'],
                        box['is_deepfake']
                    )
                    
                    with col2:
                        st.subheader("Analysis Result")
                        st.image(annotated_image, use_column_width=True)
                    
                    # Display confidence metrics
                    deepfake_conf = box['is_deepfake'] * 100
                    bbox_conf = box['bbox_confidence'] * 100
                    
                    st.write("### Detection Confidence")
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        st.metric("Deepfake Confidence", f"{deepfake_conf:.1f}%")
                        st.progress(deepfake_conf/100)
                    
                    with col4:
                        st.metric("Face Detection Confidence", f"{bbox_conf:.1f}%")
                        st.progress(bbox_conf/100)
                    
                    if deepfake_conf > 90:
                        st.error("⚠️ High probability of deepfake detected!")
                    elif deepfake_conf > 70:
                        st.warning("⚠️ Moderate probability of deepfake detected!")
                    else:
                        st.success("✅ Low probability of deepfake")
                    
                    # Display raw JSON data in expander
                    with st.expander("View Raw JSON Response"):
                        st.json(result)
            else:
                st.warning("No faces detected in the image")
        else:
            st.error("Failed to process image")

if __name__ == "__main__":
    main()