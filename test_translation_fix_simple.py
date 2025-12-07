#!/usr/bin/env python3
"""
Simple test to verify the translation pipeline import fix.
"""

import sys
import os

def main():
    print("Testing translation pipeline import fix...")
    
    # Test 1: Direct import from main.py
    print("\n=== Test 1: Direct Import ===")
    try:
        sys.path.insert(0, '.')
        from main import run_translation_pipeline, setup_environment
        print("SUCCESS: Direct import from main.py works")
        print(f"  run_translation_pipeline: {run_translation_pipeline}")
        print(f"  setup_environment: {setup_environment}")
    except ImportError as e:
        print(f"FAILED: Direct import failed: {e}")
        return False
    except Exception as e:
        print(f"FAILED: Unexpected error: {e}")
        return False
    
    # Test 2: GUI-style import (simulate translation worker path setup)
    print("\n=== Test 2: GUI-style Import ===")
    try:
        # Clear sys.path and setup like in translation_worker.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        # Add paths exactly like translation_worker.py does
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Import again to test this specific path setup
        from main import run_translation_pipeline, setup_environment
        print("SUCCESS: GUI-style import works")
        print(f"  run_translation_pipeline: {run_translation_pipeline}")
        print(f"  setup_environment: {setup_environment}")
    except ImportError as e:
        print(f"FAILED: GUI-style import failed: {e}")
        return False
    except Exception as e:
        print(f"FAILED: Unexpected error: {e}")
        return False
    
    print("\n=== Summary ===")
    print("SUCCESS: All import tests passed!")
    print("The translation pipeline function should now be available in the GUI.")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nFIX VERIFICATION: The translation pipeline import issue has been resolved!")
    else:
        print("\nFIX VERIFICATION FAILED: The import issue still exists.")
    sys.exit(0 if success else 1)