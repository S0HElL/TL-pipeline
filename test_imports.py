"""
Test script to verify all required libraries are installed correctly.
Run this after installing dependencies to catch any issues early.
"""

import sys

def test_import(module_name, package_name=None):
    """Try importing a module and report success/failure."""
    try:
        __import__(module_name)
        print(f"✓ {package_name or module_name} - OK")
        return True
    except ImportError as e:
        print(f"✗ {package_name or module_name} - FAILED")
        print(f"  Error: {e}")
        return False

def main():
    print("Testing imports for Manga Translator project...\n")
    
    all_passed = True
    
    # Core Python libraries
    print("Core Libraries:")
    all_passed &= test_import("PIL", "Pillow (PIL)")
    all_passed &= test_import("cv2", "OpenCV (opencv-python)")
    all_passed &= test_import("numpy", "NumPy")
    all_passed &= test_import("matplotlib", "Matplotlib")
    
    print("\nMachine Learning:")
    all_passed &= test_import("torch", "PyTorch")
    all_passed &= test_import("torchvision", "TorchVision")
    
    print("\nOCR Libraries:")
    all_passed &= test_import("manga_ocr", "manga-ocr")
    
    # Test manga-ocr can actually initialize (this downloads the model on first run)
    print("\nTesting manga-ocr initialization...")
    try:
        from manga_ocr import MangaOcr
        print("  Initializing MangaOcr (may download model on first run)...")
        mocr = MangaOcr()
        print("✓ manga-ocr initialization - OK")
    except Exception as e:
        print(f"✗ manga-ocr initialization - FAILED")
        print(f"  Error: {e}")
        all_passed = False
    
    # Python version check
    print("\nPython Version:")
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python version - OK (3.8+)")
    else:
        print("✗ Python version - Need 3.8 or higher")
        all_passed = False
    
    # GPU check
    print("\nGPU Availability:")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA version: {torch.version.cuda}")
        else:
            print("⚠ No GPU detected - will use CPU (slower but functional)")
    except Exception as e:
        print(f"⚠ Could not check GPU: {e}")
    
    # Final result
    print("\n" + "="*50)
    if all_passed:
        print("SUCCESS: All required libraries are installed correctly!")
        print("You're ready to proceed to Phase 2 (OCR Module).")
    else:
        print("FAILED: Some libraries are missing or not working.")
        print("Please install missing packages and run this test again.")
    print("="*50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())