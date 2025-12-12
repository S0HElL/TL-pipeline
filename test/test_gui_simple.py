#!/usr/bin/env python3
"""
Simple test script to validate GUI component imports.
"""

import sys
import os

def test_imports():
    """Test importing all GUI components."""
    print("Testing GUI component imports...")
    
    try:
        # Test path setup
        gui_path = os.path.join(os.getcwd(), 'gui')
        if gui_path not in sys.path:
            sys.path.insert(0, gui_path)
        
        # Test main_window import
        from main_window import MainWindow, EditorCanvas, TranslationWorker
        print("SUCCESS: Imported MainWindow, EditorCanvas, TranslationWorker")
        
        # Test editor_canvas import
        from editor_canvas import EditorCanvas as EC, BoundingBoxItem
        print("SUCCESS: Imported EditorCanvas and BoundingBoxItem")
        
        # Test translation_worker import
        from translation_worker import TranslationWorker as TW
        print("SUCCESS: Imported TranslationWorker")
        
        return True
        
    except ImportError as e:
        print(f"FAILED: Import error - {e}")
        return False
    except Exception as e:
        print(f"FAILED: Unexpected error - {e}")
        return False

def test_core_pipeline():
    """Test core pipeline integration."""
    print("\nTesting core pipeline integration...")
    
    try:
        from main import run_translation_pipeline, setup_environment
        print("SUCCESS: Core pipeline functions imported")
        return True
    except ImportError as e:
        print(f"FAILED: Core pipeline import error - {e}")
        return False
    except Exception as e:
        print(f"FAILED: Core pipeline error - {e}")
        return False

def test_files_exist():
    """Test that required files exist."""
    print("\nTesting file existence...")
    
    required_files = [
        'gui/main_window.py',
        'gui/editor_canvas.py', 
        'gui/translation_worker.py',
        'main.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"SUCCESS: Found {file_path}")
        else:
            print(f"FAILED: Missing {file_path}")
            all_exist = False
            
    return all_exist

def main():
    """Run all tests."""
    print("=== Manga Translator GUI Import Tests ===\n")
    
    tests = [
        test_imports,
        test_core_pipeline,
        test_files_exist
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"FAILED: Test exception - {e}")
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("SUCCESS: All import tests passed!")
        print("\nGUI components are properly integrated.")
        print("Next step: Install PySide6 to run the GUI")
        return True
    else:
        print("FAILED: Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)