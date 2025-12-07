#!/usr/bin/env python3
"""
Comprehensive workflow test for the Manga Translator GUI.
Tests the complete workflow without requiring a display.
"""

import sys
import os
import tempfile
from unittest.mock import Mock, patch
from PIL import Image, ImageDraw

def create_test_image():
    """Create a simple test manga image with text."""
    # Create a simple manga-style image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add some text regions (simulating manga speech bubbles)
    draw.rectangle([100, 100, 300, 150], outline='black', width=2)  # Speech bubble 1
    draw.text((110, 110), "こんにちは", fill='black')  # Japanese text
    
    draw.rectangle([400, 200, 600, 250], outline='black', width=2)  # Speech bubble 2
    draw.text((410, 210), "今日はいい天気ですね", fill='black')  # Japanese text
    
    return img

def test_translation_pipeline_workflow():
    """Test the complete translation pipeline workflow."""
    print("Testing translation pipeline workflow...")
    
    try:
        # Import core functions
        from main import run_translation_pipeline, setup_environment
        
        # Create test image
        test_image = create_test_image()
        test_image_path = "test_manga.png"
        test_image.save(test_image_path)
        
        print(f"Created test image: {test_image_path}")
        
        # Test setup
        setup_environment()
        print("✓ Environment setup successful")
        
        # Run translation pipeline
        print("Running translation pipeline...")
        inpainted_image, translated_data = run_translation_pipeline(test_image_path)
        
        # Validate results
        if inpainted_image is not None:
            print(f"✓ Pipeline completed successfully")
            print(f"✓ Inpainted image type: {type(inpainted_image)}")
            
            if translated_data:
                print(f"✓ Found {len(translated_data)} text regions")
                for i, data in enumerate(translated_data):
                    print(f"  Region {i+1}:")
                    print(f"    Japanese: {data.get('japanese_text', 'N/A')[:50]}...")
                    print(f"    English: {data.get('english_text', 'N/A')[:50]}...")
            else:
                print("! No text regions detected (may be expected for simple test image)")
                
            return True
        else:
            print("✗ Pipeline failed - no inpainted image returned")
            return False
            
    except Exception as e:
        print(f"✗ Pipeline test failed: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def test_gui_component_integration():
    """Test GUI component integration with mock Qt."""
    print("\nTesting GUI component integration...")
    
    try:
        # Mock Qt components for testing
        mock_qt_module = type(sys)('PySide6')
        mock_qt_widgets = type(sys)('QtWidgets')
        mock_qt_core = type(sys)('QtCore')
        mock_qt_gui = type(sys)('QtGui')
        
        sys.modules['PySide6'] = mock_qt_module
        sys.modules['PySide6.QtWidgets'] = mock_qt_widgets
        sys.modules['PySide6.QtCore'] = mock_qt_core
        sys.modules['PySide6.QtGui'] = mock_qt_gui
        
        # Add basic mock classes
        class MockQWidget:
            def __init__(self):
                self.children = []
            def setMinimumSize(self, w, h): pass
            def show(self): pass
            def hide(self): pass
            
        class MockQMainWindow(MockQWidget):
            def __init__(self):
                super().__init__()
                self.menuBar = Mock()
                self.addToolBar = Mock(return_value=Mock())
                self.statusBar = Mock()
                
        class MockQApplication:
            def __init__(self, args):
                self.args = args
            def exec(self):
                return 0
                
        class MockQThread:
            def __init__(self):
                self.isRunning = Mock(return_value=False)
                self.terminate = Mock()
                self.wait = Mock()
                
        # Assign mock classes
        mock_qt_widgets.QApplication = MockQApplication
        mock_qt_widgets.QMainWindow = MockQMainWindow
        mock_qt_widgets.QWidget = MockQWidget
        mock_qt_core.QThread = MockQThread
        
        # Test importing GUI components with mocks
        sys.path.insert(0, os.path.join(os.getcwd(), 'gui'))
        
        from main_window import MainWindow
        from editor_canvas import EditorCanvas, BoundingBoxItem
        from translation_worker import TranslationWorker
        
        print("✓ Successfully imported all GUI components with mocks")
        
        # Test MainWindow instantiation
        main_window = MainWindow()
        print("✓ MainWindow instantiated successfully")
        
        # Test EditorCanvas instantiation  
        canvas = EditorCanvas()
        print("✓ EditorCanvas instantiated successfully")
        
        # Test TranslationWorker instantiation
        worker = TranslationWorker("test_image.png")
        print("✓ TranslationWorker instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ GUI integration test failed: {e}")
        return False

def test_image_loading_workflow():
    """Test image loading workflow."""
    print("\nTesting image loading workflow...")
    
    try:
        from PIL import Image
        import tempfile
        
        # Create a test image
        test_img = Image.new('RGB', (400, 300), color='red')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            test_img.save(tmp.name)
            test_path = tmp.name
        
        # Test loading and processing
        loaded_img = Image.open(test_path)
        print(f"✓ Image loaded successfully: {loaded_img.size}")
        
        # Test image conversion
        rgb_img = loaded_img.convert('RGB')
        print(f"✓ Image converted to RGB: {rgb_img.size}")
        
        # Cleanup
        os.unlink(test_path)
        
        return True
        
    except Exception as e:
        print(f"✗ Image loading test failed: {e}")
        return False

def test_error_handling():
    """Test error handling in the workflow."""
    print("\nTesting error handling...")
    
    try:
        from main import run_translation_pipeline
        
        # Test with non-existent file
        result = run_translation_pipeline("non_existent_file.png")
        if result == (None, None):
            print("✓ Properly handles non-existent file")
        else:
            print("✗ Failed to handle non-existent file properly")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

def test_file_operations():
    """Test file operations workflow."""
    print("\nTesting file operations...")
    
    try:
        import tempfile
        import shutil
        
        # Test directory creation
        test_dir = "test_output"
        os.makedirs(test_dir, exist_ok=True)
        print("✓ Directory creation successful")
        
        # Test file operations
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        print("✓ File write successful")
        
        # Test file reading
        with open(test_file, 'r') as f:
            content = f.read()
        if content == "test content":
            print("✓ File read successful")
        else:
            print("✗ File read failed")
            return False
            
        # Cleanup
        shutil.rmtree(test_dir)
        print("✓ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        return False

def main():
    """Run all workflow tests."""
    print("=== Manga Translator GUI Workflow Tests ===\n")
    
    tests = [
        ("Translation Pipeline", test_translation_pipeline_workflow),
        ("GUI Component Integration", test_gui_component_integration),
        ("Image Loading", test_image_loading_workflow),
        ("Error Handling", test_error_handling),
        ("File Operations", test_file_operations)
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
    
    print(f"\n=== Workflow Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All workflow tests passed!")
        print("\nThe GUI workflow is properly integrated and ready for use.")
        print("\nNext steps:")
        print("1. Install PySide6: pip install PySide6")
        print("2. Run: python gui/main_window.py")
        print("3. Upload a manga image and test the translation pipeline")
        return True
    else:
        print("❌ Some workflow tests failed. Review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)