import os
from text_location_detection import detect_text_regions
from inpainting_module import remove_text

# Define paths
# Assuming the user meant 'data/sample_manga_1.jpg' relative to the workspace
# as 'data/' is a common project structure and is listed in the environment details.
DATA_DIR = "data"
INPUT_IMAGE_PATH = os.path.join(DATA_DIR, 'sample_manga_1.jpg')
OUTPUT_IMAGE_PATH = os.path.join(DATA_DIR, 'sample_manga_1_inpainted.jpg')

def run_inpainting_test():
    """
    Runs the OCR detection and inpainting removal pipeline on a sample image.
    """
    print(f"--- Starting Inpainting Test with {INPUT_IMAGE_PATH} ---")

    # 0. Initialization is now handled by the iopaint CLI call inside remove_text
    print("0. Initialization is handled by the iopaint CLI.")

    if not os.path.exists(INPUT_IMAGE_PATH):
        print(f"Error: Input image not found at {INPUT_IMAGE_PATH}")
        print("Please ensure 'data/sample_manga_1.jpg' exists.")
        return

    # 1. Detect text regions (Bounding Boxes)
    print("1. Detecting text regions...")
    bounding_boxes, _ = detect_text_regions(INPUT_IMAGE_PATH)

    if not bounding_boxes:
        print("No text regions detected. Cannot proceed with inpainting.")
        return

    print(f"Detected {len(bounding_boxes)} text regions.")
    print(f"Sample Bounding Boxes: {bounding_boxes[:2]}...")

    # 2. Apply Inpainting
    print("2. Applying inpainting to remove text...")
    try:
        # Use a padding of 10 pixels as requested by the user
        inpainted_img = remove_text(INPUT_IMAGE_PATH, bounding_boxes, padding=10)
        
        # 3. Save the result
        os.makedirs(DATA_DIR, exist_ok=True)
        inpainted_img.save(OUTPUT_IMAGE_PATH)
        
        print(f"3. Inpainting successful. Result saved to: {OUTPUT_IMAGE_PATH}")
        print("Please check the output image to verify text is cleanly removed.")
        
    except Exception as e:
        print(f"An error occurred during inpainting: {e}")

if __name__ == '__main__':
    run_inpainting_test()