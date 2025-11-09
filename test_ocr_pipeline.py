import os
from ocr_module import load_image, extract_text_from_image
from text_location_detection import detect_text_regions, visualize_bounding_boxes

def run_ocr_pipeline_test(image_path: str):
    """
    Runs the full OCR pipeline (detection and extraction) on a single image.
    
    Args:
        image_path: The file path to the image.
    """
    print(f"\n--- Running OCR Pipeline Test for: {image_path} ---")
    
    if not os.path.exists(image_path):
        print(f"Skipping test: Image file not found at {image_path}")
        return

    # 1. Text Location Detection (Bounding Boxes)
    print("1. Detecting text regions...")
    bounding_boxes, pil_image = detect_text_regions(image_path)
    
    if not pil_image:
        print("Failed to load image for detection.")
        return
        
    if not bounding_boxes:
        print("No text regions detected.")
        # Proceed to full image OCR just in case, but log the issue
        full_image_text = extract_text_from_image(pil_image)
        if full_image_text:
            print(f"Full image OCR result (no boxes): {full_image_text}")
        return

    print(f"Detected {len(bounding_boxes)} text regions.")
    
    # Save visualization of bounding boxes
    data_dir = os.path.dirname(image_path)
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)
    output_box_path = os.path.join(data_dir, f'{name}_boxes{ext}')
    visualize_bounding_boxes(pil_image.copy(), bounding_boxes, output_box_path)
    
    # 2. Text Extraction (OCR)
    # Note: manga-ocr is designed for full image, but for a complete pipeline, 
    # we would ideally crop and run OCR on each box. For this MVP, we'll 
    # run the full image OCR and compare the result to the detected boxes.
    # A more advanced implementation would iterate over the boxes.
    
    print("2. Extracting text from the full image (using manga-ocr)...")
    full_image_text = extract_text_from_image(pil_image)
    
    if full_image_text:
        print("\n--- Extracted Text (Full Image) ---")
        print(full_image_text)
        print("----------------------------------")
    else:
        print("Text extraction failed.")
        
    # 3. Verification (Manual step for the user)
    print("\n--- Verification ---")
    print(f"Please check the extracted text against the original image: {image_path}")
    print(f"Please check the bounding box visualization: {output_box_path}")
    print("Verify text extraction accuracy and debug any issues.")


if __name__ == '__main__':
    # --- Setup ---
    data_dir = "data"
    
    # Create the data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
        
    # Define sample image paths
    sample_images = [
        os.path.join(data_dir, 'sample_manga_1.jpg'),
        os.path.join(data_dir, 'sample_manga_2.png'),
        os.path.join(data_dir, 'sample_manga_3.jpeg'),
    ]
    
    print("--- OCR Pipeline Test Script ---")
    print("NOTE: This script requires sample Japanese manga images in the 'data/' directory.")
    print("Please ensure you have at least one of the following files:")
    for img_path in sample_images:
        print(f"- {img_path}")
        
    # Run test for each sample image
    for image_path in sample_images:
        run_ocr_pipeline_test(image_path)
