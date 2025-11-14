import os
from PIL import Image
from text_renderer import render_text

# Define paths
DATA_DIR = "data"
OUTPUT_IMAGE_PATH = os.path.join(DATA_DIR, 'text_render_test.png')

def run_text_render_test():
    """
    Runs a test for the text rendering module.
    Tests font sizing, word wrapping, and centering.
    """
    print("--- Starting Text Renderer Test ---")

    # 1. Create a dummy image (e.g., a white canvas)
    # Use a size that is representative of a manga panel
    img_width, img_height = 800, 600
    img = Image.new('RGB', (img_width, img_height), color = 'white')
    
    # 2. Define a sample bounding box and text
    # Test case 1: Long text that requires wrapping and sizing
    box_1 = (50, 50, 350, 250) # A wide, short box
    text_1 = "This is a long sentence that needs to be wrapped to fit inside the speech bubble."
    
    # Test case 2: Short text that should be centered
    box_2 = (450, 300, 750, 500) # A square box
    text_2 = "Hello World!"
    
    # Test case 3: Very long text to test height constraint
    box_3 = (50, 300, 250, 500) # A tall, narrow box
    text_3 = "This is a very very very very very very very very very very very very long text."

    # 3. Render text for all test cases
    print("Rendering Test Case 1 (Long text, wide box)...")
    img = render_text(img, text_1, box_1)
    
    print("Rendering Test Case 2 (Short text, square box)...")
    img = render_text(img, text_2, box_2)
    
    print("Rendering Test Case 3 (Very long text, narrow box)...")
    img = render_text(img, text_3, box_3)

    # 4. Save the result
    os.makedirs(DATA_DIR, exist_ok=True)
    img.save(OUTPUT_IMAGE_PATH)
    
    print(f"Text rendering test successful. Result saved to: {OUTPUT_IMAGE_PATH}")
    print("Please check the output image to verify text is wrapped, sized, and centered correctly.")

if __name__ == '__main__':
    run_text_render_test()