from googletrans import Translator
from typing import Any, List
import os
import csv
from collections import defaultdict

# Kanji dictionary globals
KANJI_DICT_PATH = "joyo.csv"
kanji_dictionary: Any = None

# Translator globals
SOURCE_LANG = "auto" # Auto-detect source language
TARGET_LANG = "en" # English

# Global variable to hold the translator
translator: Translator = None

def load_kanji_dictionary():
    """
    Loads the kanji dictionary from joyo.csv into a global dictionary.
    Kanji is at column 2 (index 1), meanings are at column 8 (index 7).
    """
    global kanji_dictionary
    if kanji_dictionary is not None:
        return

    print(f"Loading kanji dictionary from {KANJI_DICT_PATH}...")
    kanji_dictionary = {}
    try:
        with open(KANJI_DICT_PATH, 'r', encoding='utf-8') as f:
            # Use csv.reader to handle CSV format correctly
            reader = csv.reader(f)
            # Skip header
            next(reader)
            for row in reader:
                if len(row) > 7:
                    kanji = row[1].strip()
                    # Meanings are pipe-separated in the 8th column (index 7)
                    meanings = [m.strip() for m in row[7].split('|') if m.strip()]
                    if kanji and meanings:
                        # Store as a list of meanings
                        kanji_dictionary[kanji] = meanings
        print(f"Kanji dictionary loaded successfully with {len(kanji_dictionary)} entries.")
    except Exception as e:
        print(f"Error loading kanji dictionary: {e}")
        kanji_dictionary = None
        raise

def initialize_translator():
    """
    Initializes the googletrans Translator object and loads the kanji dictionary.
    """
    global translator
    if translator is not None:
        return

    print("Initializing googletrans Translator...")
    try:
        translator = Translator()
        load_kanji_dictionary()
        print("Translator initialized successfully.")
    except Exception as e:
        print(f"Error initializing translator: {e}")
        translator = None
        raise

def translate_japanese_to_english(japanese_text: str) -> str:
    """
    Translates a single string of text to English using the googletrans library.
    The source language is automatically detected by googletrans.
    A Japanese-specific kanji dictionary fallback is used if the primary translation is empty.

    Args:
        japanese_text: The text to translate (originally intended for Japanese, but now auto-detects).

    Returns:
        The translated English text.
    """
    global translator
    if translator is None:
        try:
            initialize_translator()
        except Exception:
            return "[Translation Error: Translator initialization failed]"

    # Explicit check after initialization attempt
    if translator is None:
        return "[Translation Error: Translator not initialized]"

    if not japanese_text.strip():
        return ""

    try:
        # Use googletrans to translate
        translation = translator.translate(
            japanese_text,
            src=SOURCE_LANG,
            dest=TARGET_LANG
        )
        english_text = translation.text
        
        # Fallback logic: If the translation is empty, try to use the kanji dictionary
        if not english_text.strip() and kanji_dictionary:
            fallback_translation = []
            for char in japanese_text:
                if char in kanji_dictionary:
                    # Use the first meaning as a fallback
                    fallback_translation.append(f"[{kanji_dictionary[char][0]}]")
                else:
                    # Keep non-kanji characters (hiragana, katakana, punctuation, etc.)
                    fallback_translation.append(char)
            
            # If the fallback is not just empty spaces, use it.
            if "".join(fallback_translation).strip() != japanese_text.strip():
                print(f"Warning: Translator returned empty translation for '{japanese_text}'. Using kanji dictionary fallback.")
                english_text = "".join(fallback_translation)
        
        return english_text
    except Exception as e:
        print(f"Error during translation: {e}")
        return f"[Translation Error: {e}]"

if __name__ == '__main__':
    # Example usage for testing
    sample_japanese = [
        "こんにちは、世界！", # Hello, world!
        "これは漫画の翻訳プロジェクトです。", # This is a manga translation project.
        "私はソフトウェアエンジニアです。", # I am a software engineer.
        "お腹が空いた。", # I'm hungry.
        "ごめん。", # Test for the problematic word "gomen"
        "" # Empty string test
    ]

    try:
        initialize_translator()
    except Exception:
        print("Skipping translation test due to translator initialization failure.")
        exit()
    
    import json
    output_data = []
    
    for text in sample_japanese:
        if text:
            english_text = translate_japanese_to_english(text)
            output_data.append({"japanese": text, "english": english_text})
        else:
            output_data.append({"japanese": "(empty string)", "english": "(empty string)"})

    # Write results to a file to avoid console encoding issues
    output_file = "translation_test_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print(f"Translation test results written to {output_file}")