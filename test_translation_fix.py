#!/usr/bin/env python3
"""
Test script to verify the translation pipeline import fix.
"""

import sys
import os

def test_direct_import():
    """Test importing directly from main.py"""
    print("=== Testing Direct Import ===")
    try:
        sys.path.insert(0, '.')
        from main import run_translation_pipeline, setup_environment
        print("✓ SUCCESS: Direct import from main.py works")
        print(f"  run_translation_pipeline: {run_translation_pipeline}")
        print(f"  setup_environment: {setup_environment}")
        return True
    except ImportError as e:
        print(f"✗ FAILED: Direct import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ FAILED: Unexpected error: {e}")
        return False

def test_gui_import():
    """Test importing with the same path setup as the GUI translation worker"""
    print("\n=== Testing GUI-style Import ===")
    try:
        # Simulate the exact path setup from translation_worker.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from main import run_translation_pipeline, setup_environment
        print("✓ SUCCESS: GUI-style import works")
        print(f"  run_translation_pipeline: {run_translation_pipeline}")
        print(f"  setup_environment: {setup_environment}")
        return True
    except ImportError as e:
        print(f"✗ FAILED: GUI-style import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ FAILED: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_translation_worker():
    """Test importing the TranslationWorker"""
    print("\n=== Testing Translation Worker Import ===")
    try:
        # Use the same path setup as the translation worker
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Add gui directory to path
        gui_dir = os.path.join(parent_dir, 'gui')
        if gui_dir not in sys.path:
            sys.path.insert(0, gui_dir)
            
        from translation_worker import TranslationWorker
        print("✓ SUCCESS: TranslationWorker imported")
        print(f"  TranslationWorker: {TranslationWorker}")
        return True
    except ImportError as e:
        print(f"✗ FAILED: TranslationWorker import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ FAILED: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Testing translation pipeline import fix...\n")
    
    results = []
    results.append(test_direct_import())
    results.append(test_gui_import())
    results.append(test_translation_worker())
    
    print("\n=== Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if all(results):
        print("✓ ALL TESTS PASSED - The translation pipeline import fix is working!")
    else:
        print("✗ SOME TESTS FAILED - The import issue may still exist.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)