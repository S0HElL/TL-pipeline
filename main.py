import os
import argparse
import logging
from typing import List, Tuple
from PIL import Image # Import PIL for image cropping

# Import modules
from ocr_module import load_image, extract_text_from_image
from text_location_detection import detect_text_regions
from translation_module import initialize_translator, translate_japanese_to_english
from inpainting_module import remove_text
from text_renderer import render_text

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
OUTPUT_DIR = "output"
# Padding for the inpainting mask (Task 4.3.1)
INPAINT_PADDING = 10 

def setup_environment():
    """Ensures necessary directories exist and initializes models."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logging.info(f"Ensured output directory '{OUTPUT_DIR}' exists.")
    
    # Initialize the translation model once
    try:
        initialize_translator()
        logging.info("Translation model initialized.")
    except Exception as e:
        logging.error(f"Failed to initialize translation model: {e}")
        # The pipeline will handle the error if translation is called later

def group_bounding_boxes(boxes: List[Tuple[int, int, int, int]], y_threshold: int = 50) -> List[List[Tuple[int, int, int, int]]]:
    """
    Groups bounding boxes that are vertically close to each other.
    This assumes the input boxes are already sorted in reading order (e.g., top-to-bottom).
    
    Args:
        boxes: A list of bounding box tuples: [(x_min, y_min, x_max, y_max), ...]
        y_threshold: The maximum vertical distance between two boxes to be considered a group.
        
    Returns:
        A list of groups, where each group is a list of original bounding boxes.
    """
    if not boxes:
        return []

    # Sort boxes by y_min (top-to-bottom) as a primary sort, then x_min (left-to-right)
    # This is crucial for correct reading order.
    sorted_boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
    
    groups = []
    current_group = [sorted_boxes[0]]

    for i in range(1, len(sorted_boxes)):
        prev_box = sorted_boxes[i-1]
        current_box = sorted_boxes[i]
        
        # Check vertical distance: if the top of the current box is close to the bottom of the previous box
        prev_y_max = prev_box[3]
        current_y_min = current_box[1]
        
        # Simple vertical proximity check
        vertical_distance = current_y_min - prev_y_max
        
        if 0 <= vertical_distance <= y_threshold:
            # They are close enough vertically, group them
            current_group.append(current_box)
        else:
            # New group starts
            groups.append(current_group)
            current_group = [current_box]

    # Add the last group
    if current_group:
        groups.append(current_group)
        
    return groups

def get_group_bounding_box(group: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
    """Calculates the minimum bounding box that encompasses all boxes in a group."""
    x_min = min(box[0] for box in group)
    y_min = min(box[1] for box in group)
    x_max = max(box[2] for box in group)
    y_max = max(box[3] for box in group)
    return (x_min, y_min, x_max, y_max)

def run_translation_pipeline(input_image_path: str) -> Tuple[Image.Image | None, List[dict] | None]:
    """
    Runs the core translation pipeline, designed to be called by a GUI worker.
    It returns the inpainted image and structured translation data.

    Steps:
    1. Load image
    2. Detect text regions (bounding boxes)
    3. Extract Japanese text (OCR) & Translate
    4. Remove Japanese text (Inpainting)

    Args:
        input_image_path: Path to the input manga image file.

    Returns:
        Tuple: (inpainted_image, translated_data_list)
        translated_data_list: A list of dicts, where each dict contains:
            {
                'group_box': (x_min, y_min, x_max, y_max),
                'japanese_text': str,
                'english_text': str,
                'original_boxes': List[Tuple[int, int, int, int]],
            }
    """
    logging.info(f"--- Starting core pipeline for {input_image_path} ---")

    # 1. Load image
    original_image = load_image(input_image_path)
    if original_image is None:
        logging.error("Pipeline aborted: Image loading failed.")
        return None, None

    # 2. Detect text regions (bounding boxes)
    try:
        # detect_text_regions returns (bounding_boxes, pil_img)
        # We pass the path and get the boxes.
        bounding_boxes, _ = detect_text_regions(input_image_path)
        if not bounding_boxes:
            logging.warning("No text regions detected.")
            # Return original image if no boxes found, but we still need to inpaint for clean slate
            # No, if no boxes, we skip inpainting and translation.
            return original_image, []
        logging.info(f"Detected {len(bounding_boxes)} text regions.")
    except Exception as e:
        logging.error(f"Pipeline aborted: Text detection failed: {e}")
        return None, None

    # 3. Extract Japanese text (OCR) and Translate per bounding box
    translated_data_list: List[dict] = []

    # Group the bounding boxes that are close together (likely a single speech bubble)
    grouped_boxes = group_bounding_boxes(bounding_boxes)
    logging.info(f"Grouped {len(bounding_boxes)} boxes into {len(grouped_boxes)} translation units.")

    for i, group in enumerate(grouped_boxes):
        # Calculate the single bounding box for the entire group
        group_box = get_group_bounding_box(group)

        # Collect text from all individual boxes within the group
        combined_japanese_text = []
        successful_original_boxes = []

        for j, box in enumerate(group):
            x_min, y_min, x_max, y_max = box

            try:
                # Crop the image to the individual bounding box region
                cropped_image = original_image.crop((x_min, y_min, x_max, y_max))

                # Extract Japanese text from the cropped region
                japanese_text_raw = extract_text_from_image(cropped_image)

                if japanese_text_raw is None or not str(japanese_text_raw).strip():
                    # logging.warning(f"OCR returned no text for box {j+1} in group {i+1}. Skipping.")
                    continue

                japanese_text = str(japanese_text_raw)
                combined_japanese_text.append(japanese_text)
                successful_original_boxes.append(box)

            except Exception as e:
                logging.error(f"Pipeline error during OCR for box {j+1} in group {i+1}: {e}. Skipping.")
                continue

        # Join the text from all boxes in the group for a single, context-aware translation
        full_japanese_text = " ".join(combined_japanese_text)

        if not full_japanese_text.strip():
            logging.warning(f"No text was extracted for group {i+1}/{len(grouped_boxes)}. Skipping translation.")
            continue

        logging.info(f"Group {i+1}/{len(grouped_boxes)}: Extracted Japanese Text: {full_japanese_text[:30]}...")

        try:
            # Translate the combined Japanese text to English
            english_text = translate_japanese_to_english(full_japanese_text)

            if "[Translation Error" in english_text:
                logging.error(f"Translation failed for group {i+1}/{len(grouped_boxes)}: {english_text}. Skipping.")
                continue

            logging.info(f"Group {i+1}/{len(grouped_boxes)}: Translated English Text: {english_text[:30]}...")

            # Store the data required for the GUI editor
            translated_data_list.append({
                'group_box': group_box,
                'japanese_text': full_japanese_text,
                'english_text': english_text,
                'original_boxes': successful_original_boxes,
            })

        except Exception as e:
            logging.error(f"Pipeline error during Translation for group {i+1}/{len(grouped_boxes)}: {e}. Skipping.")
            continue

    if not translated_data_list:
        logging.warning("No text was successfully extracted and translated. Returning original image.")
        return original_image, []

    # 4. Remove Japanese text (Inpainting)
    try:
        # Inpainting still needs the original, un-grouped bounding boxes for the mask
        inpainted_image = remove_text(input_image_path, bounding_boxes, padding=INPAINT_PADDING)
        logging.info("Inpainting complete.")
    except Exception as e:
        logging.error(f"Inpainting failed: {e}. Returning original image for editing.")
        return original_image, translated_data_list

    logging.info("--- Core pipeline finished successfully. ---")
    return inpainted_image, translated_data_list


def process_manga_page(input_image_path: str, output_image_path: str):
    """
    Legacy main pipeline function for CLI usage (modified to use the new core function).
    
    Steps:
    1. Run core pipeline to get inpainted image and translation data.
    2. Render English text onto the inpainted image using original bounding boxes.
    3. Save the final image.
    """
    logging.info(f"--- Starting CLI pipeline for {input_image_path} ---")

    inpainted_image, translated_data_list = run_translation_pipeline(input_image_path)

    if inpainted_image is None or not translated_data_list:
        if inpainted_image is not None:
            # If we successfully loaded the image but got no translation data, save original/inpainted (depending on run_translation_pipeline)
            inpainted_image.save(output_image_path)
            logging.info(f"Pipeline finished. Saved image to {output_image_path}")
        else:
            logging.error("CLI Pipeline aborted due to core failure.")
        return

    # 6. Render English text
    try:
        current_image = inpainted_image
        
        # Adapt data for render_text signature (box, text)
        render_data = [(d['group_box'], d['english_text']) for d in translated_data_list]
        
        for i, (box, text) in enumerate(render_data):
            logging.info(f"Rendering text for region {i+1}/{len(render_data)}.")
            current_image = render_text(current_image, text, box)
            
        final_image = current_image
        logging.info("Text rendering complete.")
    except Exception as e:
        logging.error(f"CLI Pipeline aborted: Text rendering failed: {e}")
        return

    # 7. Save the final image
    try:
        final_image.save(output_image_path)
        logging.info(f"CLI Pipeline finished successfully. Saved to {output_image_path}")
    except Exception as e:
        logging.error(f"Failed to save final image to {output_image_path}: {e}")


def main():
    """Main function to parse arguments and run the pipeline."""
    parser = argparse.ArgumentParser(description="Manga Translation Pipeline.")
    parser.add_argument("input_file", type=str, help="Path to the input manga image file.")
    
    args = parser.parse_args()
    
    # Setup environment and models
    setup_environment()
    
    input_path = os.path.normpath(args.input_file)
    
    # Create output filename
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    output_filename = f"{name}_translated{ext}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Run the pipeline
    process_manga_page(input_path, output_path)

if __name__ == '__main__':
    main()