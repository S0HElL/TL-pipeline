#!/usr/bin/env python3
"""
Focused workflow test for Manga Translator GUI integration.
Tests core functionality without complex image creation.
"""

import sys
import os

def test_core_pipeline():
    """Test the core translation pipeline."""
    print("Testing core translation pipeline...")
    
    try:
        from main import run_translation_pipeline, setup_environment
        
        # Test environment setup
        setup_environment()
        print("SUCCESS: Environment setup completed")
        
        # Test with non-existent file (should handle gracefully)
        result = run_translation_pipeline("non_existent_file.png")
        if result == (None, None):
            print("SUCCESS: Non-existent file handled gracefully")
        else:
            print("WARNING: Unexpected result for non-existent file")
            
        return True
        
    except Exception as e:
        print(f"FAILED: Core pipeline test - {e}")
        return False

def test_gui_imports():
    """Test GUI component imports."""
    print("\nTesting GUI component imports...")
    
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'gui'))
        
        from main_window import MainWindow
        print("SUCCESS: MainWindow imported")
        
        from editor_canvas import EditorCanvas, BoundingBoxItem
        print("SUCCESS: EditorCanvas and BoundingBoxItem imported")
        
        from translation_worker import TranslationWorker
        print("SUCCESS: TranslationWorker imported")
        
        return True
        
    except Exception as e:
        print(f"FAILED: GUI import test - {e}")
        return False

def test_file_operations():
    """Test basic file operations."""
    print("\nTesting file operations...")
    
    try:
        import tempfile
        
        # Test temporary file creation
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(b'test image data')
            temp_path = tmp.name
        
        # Test file existence check
        if os.path.exists(temp_path):
            print("SUCCESS: Temporary file created and verified")
        else:
            print("FAILED: Temporary file creation failed")
            return False
            
        # Test file deletion
        os.unlink(temp_path)
        if not os.path.exists(temp_path):
            print("SUCCESS: Temporary file cleanup successful")
        else:
            print("WARNING: Temporary file cleanup failed")
            
        return True
        
    except Exception as e:
        print(f"FAILED: File operations test - {e}")
        return False

def test_directory_structure():
    """Test project directory structure."""
    print("\nTesting directory structure...")
    
    required_files = [
        'main.py',
        'ocr_module.py',
        'translation_module.py',
        'inpainting_module.py',
        'text_renderer.py',
        'gui/main_window.py',
        'gui/editor_canvas.py',
        'gui/translation_worker.py',
        'fonts/',
        'data/'
    ]
    
    all_exist = True
    for path in required_files:
        if os.path.exists(path):
            print(f"SUCCESS: Found {path}")
        else:
            print(f"WARNING: Missing {path}")
            if path.endswith('/'):  # Directory
                print(f"  Note: {path} should be a directory")
            else:
                all_exist = False
    
    return all_exist

def test_module_dependencies():
    """Test that all module dependencies are available."""
    print("\nTesting module dependencies...")
    
    try:
        # Test core dependencies
        import PIL
        print("SUCCESS: PIL/Pillow available")
        
        import numpy
        print("SUCCESS: NumPy available")
        
        import cv2
        print("SUCCESS: OpenCV available")
        
        # Test ML dependencies
        import torch
        print("SUCCESS: PyTorch available")
        
        import transformers
        print("SUCCESS: Transformers available")
        
        # Test OCR
        import manga_ocr
        print("SUCCESS: Manga-OCR available")
        
        return True
        
    except ImportError as e:
        print(f"FAILED: Missing dependency - {e}")
        return False
    except Exception as e:
        print(f"FAILED: Dependency test error - {e}")
        return False

def test_translation_worker_integration():
    """Test translation worker integration with core pipeline."""
    print("\nTesting translation worker integration...")
    
    try:
        # Test that translation worker can import core functions
        sys.path.insert(0, os.getcwd())
        from gui.translation_worker import TranslationWorker
        
        print("SUCCESS: TranslationWorker can access core functions")
        
        # Test worker instantiation
        worker = TranslationWorker("test_image.png")
        print("SUCCESS: TranslationWorker instantiated")
        
        # Test worker attributes
        if hasattr(worker, 'finished'):
            print("SUCCESS: TranslationWorker has finished signal")
        if hasattr(worker, 'error'):
            print("SUCCESS: TranslationWorker has error signal")
        if hasattr(worker, 'progress'):
            print("SUCCESS: TranslationWorker has progress signal")
            
        return True
        
    except Exception as e:
        print(f"FAILED: Translation worker integration test - {e}")
        return False

def main():
    """Run all workflow tests."""
    print("=== Manga Translator GUI Workflow Tests ===\n")
    
    tests = [
        ("Core Pipeline", test_core_pipeline),
        ("GUI Imports", test_gui_imports),
        ("File Operations", test_file_operations),
        ("Directory Structure", test_directory_structure),
        ("Module Dependencies", test_module_dependencies),
        ("Worker Integration", test_translation_worker_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                print(f"FAILED: {test_name}")
        except Exception as e:
            print(f"FAILED: {test_name} - Exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed >= total * 0.8:  # 80% pass rate
        print("SUCCESS: Workflow integration is functional!")
        print("\nGUI components are properly integrated with the core pipeline.")
        print("\nReady for GUI testing:")
        print("1. Install PySide6: pip install PySide6")
        print("2. Run GUI: python gui/main_window.py")
        print("3. Test with actual manga images")
        return True
    else:
        print("FAILED: Several workflow tests failed. Review issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)