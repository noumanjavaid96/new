import streamlit as st
from PIL import Image
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def main():
    st.title("Image Comparison App")
    st.write("""
    Upload two images to compare them and find differences.
    """)

    # Upload images
    col1, col2 = st.columns(2)

    with col1:
        st.header("Original Image")
        uploaded_file1 = st.file_uploader("Choose the original image", type=["png", "jpg", "jpeg"], key="1")

    with col2:
        st.header("Image to Compare")
        uploaded_file2 = st.file_uploader("Choose the image to compare", type=["png", "jpg", "jpeg"], key="2")

    if uploaded_file1 is not None and uploaded_file2 is not None:
        # Read images
        image1 = Image.open(uploaded_file1)
        image2 = Image.open(uploaded_file2)

        # Convert images to OpenCV format
        img1 = cv2.cvtColor(np.array(image1), cv2.COLOR_RGB2BGR)
        img2 = cv2.cvtColor(np.array(image2), cv2.COLOR_RGB2BGR)

        # Resize images to the same size if necessary
        if img1.shape != img2.shape:
            st.warning("Images are not the same size. Resizing the second image to match the first.")
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Compute SSIM between two images
        score, diff = ssim(gray1, gray2, full=True)
        st.write(f"**Structural Similarity Index (SSIM): {score:.4f}**")
        diff = (diff * 255).astype("uint8")

        # Threshold the difference image
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # Find contours of the differences
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create copies of the images to draw on
        img1_diff = img1.copy()
        img2_diff = img2.copy()

        # Draw rectangles around differences
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img1_diff, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(img2_diff, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Convert images back to RGB for displaying with Streamlit
        img1_display = cv2.cvtColor(img1_diff, cv2.COLOR_BGR2RGB)
        img2_display = cv2.cvtColor(img2_diff, cv2.COLOR_BGR2RGB)
        diff_display = cv2.cvtColor(diff, cv2.COLOR_GRAY2RGB)
        thresh_display = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)

        # Display images
        st.write("## Results")
        st.write("Differences are highlighted in red boxes.")

        st.image([img1_display, img2_display], caption=["Original Image with Differences", "Compared Image with Differences"], width=300)

        st.write("## Difference Image")
        st.image(diff_display, caption="Difference Image", width=300)

        st.write("## Thresholded Difference Image")
        st.image(thresh_display, caption="Thresholded Difference Image", width=300)

    else:
        st.info("Please upload both images.")

if __name__ == "__main__":
    main()