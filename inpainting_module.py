import numpy as np
from PIL import Image
import cv2 # Keep cv2 for mask drawing utility
import subprocess
import tempfile
import os
import torch # Import torch to check for CUDA availability

def create_mask(image_shape, bounding_boxes, padding=10):
    """
    Creates a binary mask from a list of bounding boxes.

    Args:
        image_shape (tuple): The shape of the image (height, width, channels).
        bounding_boxes (list): A list of bounding boxes, where each box is
                               (x_min, y_min, x_max, y_max).
        padding (int): Extra pixels to add around the bounding box for the mask.

    Returns:
        np.ndarray: A binary mask (dtype=np.uint8) where text regions are white (255).
    """
    # Note: We use cv2 for the rectangle drawing utility, but the mask is a numpy array
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    
    for box in bounding_boxes:
        x_min, y_min, x_max, y_max = box
        
        # Apply padding and clamp to image boundaries
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(image_shape[1], x_max + padding)
        y_max = min(image_shape[0], y_max + padding)
        
        # Draw the white rectangle on the mask
        # The mask is 0 (black) for background, 255 (white) for area to inpaint
        cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)
        
    return mask

def remove_text(image_path, bounding_boxes, padding=10):
    """
    Removes text from an image by calling the iopaint CLI with a generated mask.

    Args:
        image_path (str): Path to the input image.
        bounding_boxes (list): A list of bounding boxes, where each box is
                               (x_min, y_min, x_max, y_max).
        padding (int): Extra pixels to add around the bounding box for the mask.

    Returns:
        PIL.Image.Image: The image with text removed (inpainted).
    """
    # 1. Load image and create mask
    try:
        img_pil = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError(f"Image not found at {image_path}")
    
    img_np = np.array(img_pil)
    mask_np = create_mask(img_np.shape, bounding_boxes, padding)
    mask_pil = Image.fromarray(mask_np)

    # 2. Save mask to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_mask_file:
        mask_path = tmp_mask_file.name
        mask_pil.save(mask_path)

    # 3. Define output path for the CLI
    # The CLI will save the output image with a suffix, e.g., 'input_image_path_out.png'
    # We will use a temporary directory to ensure a clean output path
    with tempfile.TemporaryDirectory() as tmp_output_dir:
        # The iopaint CLI requires the output directory, not the full path
        
        # 4. Execute iopaint CLI
        # We use 'lama' as the model name as intended by the project
        command = [
            "iopaint",
            "run",
            "--image", image_path,
            "--mask", mask_path,
            "--output", tmp_output_dir,
            "--model", "lama",
            "--device", "cuda" if torch.cuda.is_available() else "cpu", # Use CUDA if available
        ]
        
        print(f"Running iopaint CLI: {' '.join(command)}")
        
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            print("iopaint CLI failed.")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            # Clean up the temporary mask file
            os.unlink(mask_path)
            raise RuntimeError(f"iopaint CLI failed with exit code {result.returncode}")

        # 5. Find and load the output image
        # The CLI names the output file based on the input image name
        input_filename = os.path.basename(image_path)
        # iopaint CLI output file name format is typically {input_name}_out.{ext}
        # We'll assume it saves as a PNG in the temp directory
        output_filename = os.path.splitext(input_filename)[0] + "_out.png"
        output_path = os.path.join(tmp_output_dir, output_filename)
        
        if not os.path.exists(output_path):
            # Fallback: check for other common output names
            output_files = os.listdir(tmp_output_dir)
            if output_files:
                output_path = os.path.join(tmp_output_dir, output_files[0])
            else:
                # Clean up the temporary mask file
                os.unlink(mask_path)
                raise FileNotFoundError("iopaint CLI did not produce an output image.")

        inpainted_pil = Image.open(output_path).convert("RGB")

    # 6. Clean up the temporary mask file
    os.unlink(mask_path)
    
    return inpainted_pil

if __name__ == '__main__':
    # This is a placeholder for testing.
    # A real test would require a sample image and bounding boxes from ocr_module.py
    print("Inpainting module created. Ready for integration and testing.")
    # Example usage (requires a test image and bounding boxes):
    # test_image_path = "data/sample_manga.jpg"
    # test_boxes = [(100, 50, 300, 150), (500, 400, 700, 500)]
    # try:
    #     # NOTE: The first call to remove_text will initialize the model, which can be slow.
    #     # It's better to call initialize_inpainter() once at the start of the main script.
    #     inpainted_img = remove_text(test_image_path, test_boxes)
    #     inpainted_img.save("data/sample_manga_inpainted.jpg")
    #     print("Inpainting test successful.")
    # except FileNotFoundError as e:
    #     print(e)
    # except Exception as e:
    #     print(f"An error occurred during inpainting test: {e}")