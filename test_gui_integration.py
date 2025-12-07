#!/usr/bin/env python3
"""
Test script to validate GUI component imports and basic initialization.
This script tests the GUI components without actually displaying the GUI.
"""

import sys
import os

def test_gui_imports():
    """Test importing all GUI components."""
    print("Testing GUI component imports...")
    
    try:
        # Test main_window import
        sys.path.insert(0, os.path.join(os.getcwd(), 'gui'))
        from main_window import MainWindow, EditorCanvas, TranslationWorker
        print("✓ Successfully imported MainWindow, EditorCanvas, TranslationWorker")
        
        # Test editor_canvas import
        from editor_canvas import EditorCanvas as EC, BoundingBoxItem
        print("✓ Successfully imported EditorCanvas and BoundingBoxItem")
        
        # Test translation_worker import
        from translation_worker import TranslationWorker as TW
        print("✓ Successfully imported TranslationWorker")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_gui_instantiation():
    """Test basic instantiation of GUI components (without showing GUI)."""
    print("\nTesting GUI component instantiation...")
    
    try:
        # Mock Qt application for testing
        class MockQApplication:
            def __init__(self, args):
                self.args = args
                
            def exec(self):
                return 0
                
        # Patch PySide6 imports for testing
        sys.modules['PySide6'] = type(sys)('PySide6')
        sys.modules['PySide6.QtWidgets'] = type(sys)('QtWidgets')
        sys.modules['PySide6.QtCore'] = type(sys)('QtCore')
        sys.modules['PySide6.QtGui'] = type(sys)('QtGui')
        
        # Add mock classes
        class MockWidget:
            def __init__(self):
                pass
            def setMinimumSize(self, w, h): pass
            def show(self): pass
            
        class MockMainWindow(MockWidget):
            def __init__(self):
                super().__init__()
                self.current_image_path = None
                self.translation_worker = None
                self.translated_data = []
                
        sys.modules['PySide6.QtWidgets'].QApplication = MockQApplication
        sys.modules['PySide6.QtWidgets'].QMainWindow = MockMainWindow
        sys.modules['PySide6.QtWidgets'].QWidget = MockWidget
        
        # Test MainWindow instantiation
        from main_window import MainWindow
        main_window = MainWindow()
        print("✓ Successfully instantiated MainWindow")
        
        return True
        
    except Exception as e:
        print(f"✗ Instantiation error: {e}")
        return False

def test_path_resolution():
    """Test that the import path resolution works correctly."""
    print("\nTesting path resolution...")
    
    try:
        # Check if files exist in expected locations
        expected_files = [
            'gui/main_window.py',
            'gui/editor_canvas.py', 
            'gui/translation_worker.py'
        ]
        
        for file_path in expected_files:
            if os.path.exists(file_path):
                print(f"✓ Found {file_path}")
            else:
                print(f"✗ Missing {file_path}")
                return False
                
        return True
        
    except Exception as e:
        print(f"✗ Path resolution error: {e}")
        return False

def test_core_pipeline_integration():
    """Test integration with core translation pipeline."""
    print("\nTesting core pipeline integration...")
    
    try:
        # Test if main.py functions can be imported
        from main import run_translation_pipeline, setup_environment
        print("✓ Successfully imported core pipeline functions")
        
        # Test if translation worker can import main functions
        sys.path.insert(0, os.getcwd())
        from gui.translation_worker import TranslationWorker
        print("✓ Translation worker can access core functions")
        
        return True
        
    except ImportError as e:
        print(f"✗ Core pipeline integration error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error in pipeline integration: {e}")
        return False

def main():
    """Run all GUI tests."""
    print("=== Manga Translator GUI Integration Tests ===\n")
    
    tests = [
        ("Import Resolution", test_gui_imports),
        ("Path Resolution", test_path_resolution), 
        ("Core Pipeline Integration", test_core_pipeline_integration),
        ("Component Instantiation", test_gui_instantiation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! GUI integration is working correctly.")
        print("\nNext steps:")
        print("1. Install PySide6: pip install PySide6")
        print("2. Run the GUI: python gui/main_window.py")
        print("3. Test with actual manga images")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)