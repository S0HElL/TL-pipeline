import os
from ocr_module import load_image, extract_text_from_image
from translation_module import translate_japanese_to_english

OUTPUT_FILE = "image_translation_output.txt"

def test_image_translation(image_path: str):
    """
    Loads an image, extracts text using OCR, and translates the text.
    Writes the output to a file to avoid console encoding issues.
    """
    output_lines = []
    output_lines.append(f"--- Testing translation on image: {image_path} ---")
    
    # 1. Load the image
    image = load_image(image_path)
    if not image:
        output_lines.append("Image loading failed. Exiting test.")
        write_output(output_lines)
        return

    output_lines.append("Image loaded successfully.")

    # 2. Use the correct Japanese text provided by the user for testing the translation logic
    # The user suggests splitting the text to avoid large input issues.
    japanese_phrases = [
        "私に","ごめん","って言え", 
        "私に","ごめん",        
        "この","クソガキが",  
        "私にごめんって言え 私にごめん このクソガキが"     
    ]
    output_lines.append("\n--- Test Japanese Phrases ---")
    output_lines.append('\n'.join(japanese_phrases))
    output_lines.append("-----------------------------")

    # 3. Translate each phrase individually
    translated_phrases = []
    for phrase in japanese_phrases:
        # The translation module will initialize the model and dictionary on first call.
        translated_phrase = translate_japanese_to_english(phrase)
        translated_phrases.append(translated_phrase)

    translated_text = ' '.join(translated_phrases)

    output_lines.append("\n--- Translated English Text ---")
    output_lines.append(translated_text)
    output_lines.append("-----------------------------")
    
    write_output(output_lines)

def write_output(lines: list):
    """Writes the list of strings to the global output file."""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"Test results written to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == '__main__':
    # The user specified the image path is in the data directory
    IMAGE_PATH = os.path.join('data', 'sample_manga_2.jpg')
    test_image_translation(IMAGE_PATH)