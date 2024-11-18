import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ExifTags
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import pandas as pd

def main():
    st.title("Image Comparison and Watermarking App")
    st.write("""
    Upload two images to compare them, find differences, add a watermark, and compare metadata.
    """)

    # Upload images
    st.header("Upload Images")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        uploaded_file1 = st.file_uploader("Choose the original image", type=["png", "jpg", "jpeg"], key="1")

    with col2:
        st.subheader("Image to Compare")
        uploaded_file2 = st.file_uploader("Choose the image to compare", type=["png", "jpg", "jpeg"], key="2")

    watermark_text = st.text_input("Enter watermark text (optional):", value="")

    if uploaded_file1 is not None and uploaded_file2 is not None:
        # Read images
        image1 = Image.open(uploaded_file1).convert("RGB")
        image2 = Image.open(uploaded_file2).convert("RGB")

        # Display original images
        st.write("### Uploaded Images")
        st.image([image1, image2], caption=["Original Image", "Image to Compare"], width=300)

        # Add watermark if text is provided
        if watermark_text:
            st.write("### Watermarked Original Image")
            image1_watermarked = add_watermark(image1, watermark_text)
            st.image(image1_watermarked, caption="Original Image with Watermark", width=300)
        else:
            image1_watermarked = image1.copy()

        # Convert images to OpenCV format
        img1 = cv2.cvtColor(np.array(image1_watermarked), cv2.COLOR_RGB2BGR)
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

        # Display images with differences highlighted
        st.write("## Results")
        st.write("Differences are highlighted in red boxes.")

        st.image([img1_display, img2_display], caption=["Original Image with Differences", "Compared Image with Differences"], width=300)

        st.write("## Difference Image")
        st.image(diff_display, caption="Difference Image", width=300)

        st.write("## Thresholded Difference Image")
        st.image(thresh_display, caption="Thresholded Difference Image", width=300)

        # Metadata comparison
        st.write("## Metadata Comparison")
        metadata1 = get_metadata(image1)
        metadata2 = get_metadata(image2)

        if metadata1 and metadata2:
            metadata_df = compare_metadata(metadata1, metadata2)
            if metadata_df is not None:
                st.write("### Metadata Differences")
                st.dataframe(metadata_df)
            else:
                st.write("No differences in metadata.")
        else:
            st.write("Metadata not available for one or both images.")

    else:
        st.info("Please upload both images.")

def add_watermark(image, text):
    # Create a blank image for the text with transparent background
    txt = Image.new('RGBA', image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)

    # Choose a font and size
    font_size = max(20, image.size[0] // 20)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Calculate text bounding box using font.getbbox
    bbox = font.getbbox(text)
    textwidth = bbox[2] - bbox[0]
    textheight = bbox[3] - bbox[1]

    # Position the text at the bottom right
    x = image.size[0] - textwidth - 10
    y = image.size[1] - textheight - 10

    # Draw text with semi-transparent fill
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 128))

    # Combine the original image with the text overlay
    watermarked = Image.alpha_composite(image.convert('RGBA'), txt)

    return watermarked.convert('RGB')


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

if __name__ == "__main__":
    main()

