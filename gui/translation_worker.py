"""
Manga Translator GUI - Translation Worker
Asynchronous worker for running the translation pipeline without blocking the GUI.
"""

import sys
import os
import traceback
from PySide6.QtCore import QThread, Signal
from PIL import Image

# Import the core pipeline function from main.py
try:
    # Add parent directory to path to find main.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from main import run_translation_pipeline, setup_environment
except ImportError as e:
    print(f"Warning: Could not import from main.py: {e}")
    # Fallback for testing without full pipeline
    run_translation_pipeline = None
    setup_environment = None


class TranslationWorker(QThread):
    """
    QThread worker for running the translation pipeline asynchronously.
    
    This worker prevents the GUI from freezing during long-running
    translation operations by executing the pipeline in a separate thread.
    """
    
    # Signals for communication with the main thread
    finished = Signal(object, object)  # (inpainted_image, translated_data)
    error = Signal(str)  # error_message
    progress = Signal(str)  # progress_message
    
    def __init__(self, image_path):
        """
        Initialize the translation worker.
        
        Args:
            image_path (str): Path to the image to translate
        """
        super().__init__()
        self.image_path = image_path
        self.is_running = False
        
    def run(self):
        """
        Execute the translation pipeline in a background thread.
        
        This method is called automatically when the thread starts.
        It emits signals to communicate progress and results back to the GUI.
        """
        self.is_running = True
        
        try:
            # Emit initial progress
            self.progress.emit("Initializing translation pipeline...")
            
            # Setup environment (initialize models, etc.)
            if setup_environment:
                setup_environment()
                self.progress.emit("Environment initialized.")
            else:
                self.progress.emit("Warning: Environment setup not available.")
                
            # Check if image file exists
            import os
            if not os.path.exists(self.image_path):
                error_msg = f"Image file not found: {self.image_path}"
                self.error.emit(error_msg)
                return
                
            self.progress.emit("Starting OCR and translation...")
            
            # Check if the core pipeline function is available
            if not run_translation_pipeline:
                error_msg = "Core translation pipeline function not available."
                self.error.emit(error_msg)
                return
                
            # Execute the core translation pipeline
            # This should return (inpainted_image, translated_data_list)
            inpainted_image, translated_data = run_translation_pipeline(self.image_path)
            
            # Check for errors in the pipeline results
            if inpainted_image is None and translated_data is None:
                error_msg = "Translation pipeline failed completely."
                self.error.emit(error_msg)
                return
                
            if translated_data is None:
                error_msg = "Translation completed but no data was returned."
                self.error.emit(error_msg)
                return
                
            # Emit success
            if translated_data:
                self.progress.emit(f"Translation completed successfully. Found {len(translated_data)} text regions.")
            else:
                self.progress.emit("Translation completed. No text regions detected.")
                
            # Emit the results
            self.finished.emit(inpainted_image, translated_data)
            
        except Exception as e:
            # Handle any unexpected errors
            error_msg = f"Unexpected error during translation: {str(e)}"
            print(f"TranslationWorker error: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
            self.error.emit(error_msg)
            
        finally:
            self.is_running = False
            
    def stop(self):
        """Stop the worker thread."""
        self.is_running = False
        self.terminate()
        self.wait()
        
    def is_alive(self):
        """Check if the worker is still running."""
        return self.is_running


# Test function for standalone execution
def test_worker():
    """Test the translation worker with a sample image."""
    import os
    
    # Create a test image path (you would replace this with an actual image)
    test_image_path = "data/sample_manga.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"Test image not found at {test_image_path}")
        print("Please provide a sample manga image for testing.")
        return
        
    # Create and test the worker
    worker = TranslationWorker(test_image_path)
    
    # Connect signals for testing
    def on_finished(inpainted_image, translated_data):
        # Translation completed successfully
        pass
        
    def on_error(error_message):
        # Translation error occurred
        pass
        
    def on_progress(message):
        # Progress update received
        pass
        
    worker.finished.connect(on_finished)
    worker.error.connect(on_error)
    worker.progress.connect(on_progress)
    
    # Start the worker
    worker.start()
    
    # Wait for completion
    worker.wait()




if __name__ == "__main__":
    test_worker()