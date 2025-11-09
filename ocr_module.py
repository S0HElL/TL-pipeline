import os
from PIL import Image
from manga_ocr import MangaOcr

# Initialize the MangaOcr model globally
# This model is used for text extraction (OCR)
try:
    mocr = MangaOcr()
except Exception as e:
    print(f"Error initializing MangaOcr: {e}")
    mocr = None

def load_image(image_path: str) -> Image.Image | None:
    """
    Loads an image from the specified path.
    
    Args:
        image_path: The file path to the image.
        
    Returns:
        A PIL Image object, or None if loading fails.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None
    
    try:
        # Use Image.open to load the image
        img = Image.open(image_path)
        return img
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def extract_text_from_image(img: Image.Image) -> str | None:
    """
    Extracts text from a PIL Image object using MangaOcr.
    
    Args:
        img: A PIL Image object.
        
    Returns:
        The extracted text as a string, or None if extraction fails.
    """
    if mocr is None:
        print("Error: MangaOcr model is not initialized.")
        return None
        
    try:
        # The MangaOcr model takes a PIL Image object
        text = mocr(img)
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

if __name__ == '__main__':
    # --- Simple Test Case ---
    # NOTE: You will need a sample Japanese manga image named 'sample_manga.jpg' 
    # in the 'data/' directory for this test to work.
    
    # Create the data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
        
    sample_image_path = os.path.join(data_dir, 'sample_manga.jpg')
    
    print(f"--- Testing Basic OCR with {sample_image_path} ---")
    
    if not os.path.exists(sample_image_path):
        print(f"Please place a sample Japanese manga image at: {sample_image_path}")
        print("Skipping OCR test.")
    else:
        image = load_image(sample_image_path)
        
        if image:
            print("Image loaded successfully.")
            extracted_text = extract_text_from_image(image)
            
            if extracted_text:
                print("\n--- Extracted Text ---")
                print(extracted_text)
                print("----------------------")
            else:
                print("Text extraction failed.")
        else:
            print("Image loading failed.")
