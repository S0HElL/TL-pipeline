"""
Manga Translator GUI - Performance Optimized Translation Worker
Enhanced version with improved progress reporting, memory management, and error handling.
"""

import sys
import traceback
import time
import psutil
import gc
from PySide6.QtCore import QThread, Signal, QTimer
from PIL import Image

# Import the core pipeline function from main.py
try:
    from main import run_translation_pipeline, setup_environment
except ImportError as e:
    print(f"Warning: Could not import from main.py: {e}")
    # Fallback for testing without full pipeline
    run_translation_pipeline = None
    setup_environment = None


class PerformanceOptimizedTranslationWorker(QThread):
    """
    Performance-optimized QThread worker for running the translation pipeline asynchronously.
    
    Enhanced features:
    - Real-time progress reporting with timing
    - Memory usage monitoring
    - Better error handling and recovery
    - Resource cleanup
    - Performance metrics collection
    """
    
    # Signals for communication with the main thread
    finished = Signal(object, object)  # (inpainted_image, translated_data)
    error = Signal(str)  # error_message
    progress = Signal(str)  # progress_message
    performance_update = Signal(dict)  # performance_metrics
    
    def __init__(self, image_path, enable_monitoring=True):
        """
        Initialize the performance-optimized translation worker.
        
        Args:
            image_path (str): Path to the image to translate
            enable_monitoring (bool): Enable performance monitoring
        """
        super().__init__()
        self.image_path = image_path
        self.is_running = False
        self.enable_monitoring = enable_monitoring
        
        # Performance tracking
        self.start_time = None
        self.performance_metrics = {
            'start_time': None,
            'end_time': None,
            'total_duration': 0,
            'memory_usage': {},
            'cpu_usage': [],
            'steps': {}
        }
        
        # Progress reporting
        self.current_step = ""
        self.step_start_time = None
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.report_progress)
        
    def run(self):
        """
        Execute the translation pipeline in a background thread with performance optimization.
        
        This method is called automatically when the thread starts.
        It emits signals to communicate progress and results back to the GUI.
        """
        self.is_running = True
        self.start_time = time.time()
        self.performance_metrics['start_time'] = self.start_time
        
        try:
            # Start progress reporting
            if self.enable_monitoring:
                self.progress_timer.start(100)  # Report every 100ms
                
            self.report_progress("Initializing translation pipeline...")
            
            # Setup environment with error handling
            if setup_environment:
                self.start_step("environment_setup")
                setup_environment()
                self.end_step("environment_setup")
                self.report_progress("Environment initialized.")
            else:
                self.report_progress("Warning: Environment setup not available.")
                
            # Check if image file exists
            import os
            if not os.path.exists(self.image_path):
                error_msg = f"Image file not found: {self.image_path}"
                self.error.emit(error_msg)
                return
                
            self.report_progress("Starting OCR and translation...")
            
            # Check if the core pipeline function is available
            if not run_translation_pipeline:
                error_msg = "Core translation pipeline function not available."
                self.error.emit(error_msg)
                return
                
            # Execute the core translation pipeline with monitoring
            self.start_step("core_pipeline")
            inpainted_image, translated_data = run_translation_pipeline(self.image_path)
            self.end_step("core_pipeline")
            
            # Check for errors in the pipeline results
            if inpainted_image is None and translated_data is None:
                error_msg = "Translation pipeline failed completely."
                self.error.emit(error_msg)
                return
                
            if translated_data is None:
                error_msg = "Translation completed but no data was returned."
                self.error.emit(error_msg)
                return
                
            # Memory cleanup after pipeline
            self.cleanup_memory()
                
            # Emit success with timing information
            if translated_data:
                self.report_progress(f"Translation completed successfully. Found {len(translated_data)} text regions.")
            else:
                self.report_progress("Translation completed. No text regions detected.")
                
            # Collect final performance metrics
            self.collect_final_metrics()
            
            # Emit the results
            self.finished.emit(inpainted_image, translated_data)
            
        except Exception as e:
            # Handle any unexpected errors with detailed logging
            error_msg = f"Unexpected error during translation: {str(e)}"
            print(f"TranslationWorker error: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
            
            # Collect error metrics
            self.performance_metrics['error'] = {
                'message': error_msg,
                'timestamp': time.time(),
                'step': self.current_step
            }
            
            self.error.emit(error_msg)
            
        finally:
            self.is_running = False
            if self.enable_monitoring:
                self.progress_timer.stop()
                # Emit final performance report
                self.performance_update.emit(self.performance_metrics)
                
    def start_step(self, step_name):
        """Mark the start of a processing step."""
        self.current_step = step_name
        self.step_start_time = time.time()
        self.performance_metrics['steps'][step_name] = {
            'start': self.step_start_time,
            'end': None,
            'duration': 0
        }
        
    def end_step(self, step_name):
        """Mark the end of a processing step."""
        if step_name in self.performance_metrics['steps']:
            end_time = time.time()
            duration = end_time - self.performance_metrics['steps'][step_name]['start']
            self.performance_metrics['steps'][step_name]['end'] = end_time
            self.performance_metrics['steps'][step_name]['duration'] = duration
            
    def report_progress(self, message=None):
        """Report current progress with performance metrics."""
        if message:
            current_message = f"[{self.get_elapsed_time():.1f}s] {message}"
        else:
            current_message = f"[{self.get_elapsed_time():.1f}s] Processing: {self.current_step}"
            
        self.progress.emit(current_message)
        
        # Update performance metrics
        if self.enable_monitoring:
            self.update_performance_metrics()
            
    def get_elapsed_time(self):
        """Get elapsed time since start."""
        if self.start_time:
            return time.time() - self.start_time
        return 0
        
    def update_performance_metrics(self):
        """Update real-time performance metrics."""
        try:
            # Memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            self.performance_metrics['memory_usage'][time.time()] = {
                'rss': memory_info.rss,  # Resident Set Size
                'vms': memory_info.vms,  # Virtual Memory Size
                'percent': process.memory_percent()
            }
            
            # CPU usage
            self.performance_metrics['cpu_usage'].append({
                'time': time.time(),
                'percent': process.cpu_percent()
            })
            
            # Keep only recent data (last 100 entries)
            if len(self.performance_metrics['cpu_usage']) > 100:
                self.performance_metrics['cpu_usage'] = self.performance_metrics['cpu_usage'][-100:]
                
        except Exception as e:
            # Silently ignore monitoring errors
            pass
            
    def collect_final_metrics(self):
        """Collect final performance metrics."""
        self.performance_metrics['end_time'] = time.time()
        self.performance_metrics['total_duration'] = self.performance_metrics['end_time'] - self.performance_metrics['start_time']
        
        # Calculate summary statistics
        if self.performance_metrics['memory_usage']:
            memory_values = [m['rss'] for m in self.performance_metrics['memory_usage'].values()]
            self.performance_metrics['memory_summary'] = {
                'min_mb': min(memory_values) / (1024 * 1024),
                'max_mb': max(memory_values) / (1024 * 1024),
                'avg_mb': sum(memory_values) / len(memory_values) / (1024 * 1024)
            }
            
        if self.performance_metrics['cpu_usage']:
            cpu_values = [c['percent'] for c in self.performance_metrics['cpu_usage']]
            self.performance_metrics['cpu_summary'] = {
                'min': min(cpu_values),
                'max': max(cpu_values),
                'avg': sum(cpu_values) / len(cpu_values)
            }
            
    def cleanup_memory(self):
        """Perform memory cleanup."""
        try:
            # Force garbage collection
            collected = gc.collect()
            if collected > 0:
                self.report_progress(f"Memory cleanup: collected {collected} objects")
        except Exception:
            # Silently ignore cleanup errors
            pass
            
    def stop(self):
        """Stop the worker thread with cleanup."""
        self.is_running = False
        self.terminate()
        self.wait()
        
    def is_alive(self):
        """Check if the worker is still running."""
        return self.is_running
        
    def get_performance_summary(self):
        """Get a summary of performance metrics."""
        if not self.performance_metrics['start_time']:
            return "No performance data available"
            
        summary = f"Total duration: {self.performance_metrics['total_duration']:.2f}s\\n"
        
        if 'memory_summary' in self.performance_metrics:
            mem = self.performance_metrics['memory_summary']
            summary += f"Memory usage: {mem['min_mb']:.1f}MB - {mem['max_mb']:.1f}MB (avg: {mem['avg_mb']:.1f}MB)\\n"
            
        if 'cpu_summary' in self.performance_metrics:
            cpu = self.performance_metrics['cpu_summary']
            summary += f"CPU usage: {cpu['min']:.1f}% - {cpu['max']:.1f}% (avg: {cpu['avg']:.1f}%)"
            
        return summary


class MemoryEfficientTranslationWorker(PerformanceOptimizedTranslationWorker):
    """
    Extended version with additional memory optimization features.
    """
    
    def __init__(self, image_path, max_memory_mb=512):
        super().__init__(image_path, enable_monitoring=True)
        self.max_memory_mb = max_memory_mb
        
    def run(self):
        """Run with additional memory monitoring."""
        try:
            # Check initial memory usage
            initial_memory = self.get_current_memory_mb()
            if initial_memory > self.max_memory_mb * 0.8:  # 80% threshold
                self.report_progress(f"High memory usage detected: {initial_memory:.1f}MB")
                
            super().run()
            
        except MemoryError:
            error_msg = f"Memory limit exceeded ({self.max_memory_mb}MB). Try with a smaller image."
            self.error.emit(error_msg)
            
    def get_current_memory_mb(self):
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0
            
    def check_memory_limit(self):
        """Check if memory usage exceeds limit."""
        current_memory = self.get_current_memory_mb()
        if current_memory > self.max_memory_mb:
            self.report_progress(f"Memory limit exceeded: {current_memory:.1f}MB > {self.max_memory_mb}MB")
            return True
        return False


# Test function for standalone execution
def test_optimized_worker():
    """Test the optimized translation worker."""
    import os
    
    # Create a test image path
    test_image_path = "data/sample_manga.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"Test image not found at {test_image_path}")
        print("Using dummy test...")
        
        # Test with non-existent file
        worker = PerformanceOptimizedTranslationWorker("dummy.png")
        
        def on_finished(inpainted_image, translated_data):
            print(f"Translation finished!")
            print(f"Performance summary: {worker.get_performance_summary()}")
            
        def on_error(error_message):
            print(f"Translation error: {error_message}")
            
        def on_performance(metrics):
            print(f"Performance metrics: {metrics}")
            
        worker.finished.connect(on_finished)
        worker.error.connect(on_error)
        worker.performance_update.connect(on_performance)
        
        worker.start()
        worker.wait()
        
        # Test completed
        return
        
    # Test with real image
    worker = PerformanceOptimizedTranslationWorker(test_image_path)
    
    # Connect signals for testing
    def on_finished(inpainted_image, translated_data):
        print(f"Translation finished!")
        print(f"Inpainted image type: {type(inpainted_image)}")
        print(f"Translated data: {translated_data}")
        print(f"Performance summary: {worker.get_performance_summary()}")
        
    def on_error(error_message):
        print(f"Translation error: {error_message}")
        
    def on_progress(message):
        print(f"Progress: {message}")
        
    def on_performance(metrics):
        print(f"Performance update: {metrics}")
        
    worker.finished.connect(on_finished)
    worker.error.connect(on_error)
    worker.progress.connect(on_progress)
    worker.performance_update.connect(on_performance)
    
    # Start the worker
    worker.start()
    
    # Wait for completion
    worker.wait()
    
    print("Optimized worker test completed.")


if __name__ == "__main__":
    test_optimized_worker()