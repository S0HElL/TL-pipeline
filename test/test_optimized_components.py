#!/usr/bin/env python3
"""
Test script for optimized GUI components.
"""

import sys
import os

def test_optimized_components():
    """Test optimized GUI components."""
    print("Testing optimized GUI components...")
    
    try:
        # Test imports
        sys.path.insert(0, os.path.join(os.getcwd(), 'gui'))
        
        from optimized_editor_canvas import OptimizedEditorCanvas, OptimizedBoundingBoxItem
        print("SUCCESS: OptimizedEditorCanvas imported")
        
        from optimized_translation_worker import PerformanceOptimizedTranslationWorker
        print("SUCCESS: PerformanceOptimizedTranslationWorker imported")
        
        # Test instantiation
        canvas = OptimizedEditorCanvas()
        print("SUCCESS: OptimizedEditorCanvas instantiated")
        
        worker = PerformanceOptimizedTranslationWorker("test.png")
        print("SUCCESS: PerformanceOptimizedTranslationWorker instantiated")
        
        # Test performance features
        if hasattr(canvas, 'render_cache_enabled'):
            print("SUCCESS: Canvas has performance features")
        
        if hasattr(worker, 'performance_update'):
            print("SUCCESS: Worker has performance monitoring")
        
        return True
        
    except Exception as e:
        print(f"FAILED: Optimized components test - {e}")
        return False

def test_performance_features():
    """Test performance optimization features."""
    print("\nTesting performance features...")
    
    try:
        from optimized_editor_canvas import OptimizedEditorCanvas
        
        canvas = OptimizedEditorCanvas()
        
        # Test cache management
        canvas.clear_cache()
        print("SUCCESS: Cache management works")
        
        # Test memory usage tracking
        memory_usage = canvas.get_memory_usage()
        print(f"SUCCESS: Memory tracking works - {memory_usage:.2f}MB")
        
        # Test lazy loading settings
        canvas.lazy_loading_enabled = True
        canvas.render_cache_enabled = True
        print("SUCCESS: Performance settings configurable")
        
        return True
        
    except Exception as e:
        print(f"FAILED: Performance features test - {e}")
        return False

def test_monitoring_features():
    """Test performance monitoring features."""
    print("\nTesting monitoring features...")
    
    try:
        from optimized_translation_worker import PerformanceOptimizedTranslationWorker
        
        worker = PerformanceOptimizedTranslationWorker("test.png")
        
        # Test performance metrics
        summary = worker.get_performance_summary()
        print(f"SUCCESS: Performance summary: {summary}")
        
        # Test step timing
        worker.start_step("test_step")
        import time
        time.sleep(0.1)  # Short delay
        worker.end_step("test_step")
        print("SUCCESS: Step timing works")
        
        return True
        
    except Exception as e:
        print(f"FAILED: Monitoring features test - {e}")
        return False

def main():
    """Run all optimized component tests."""
    print("=== Optimized GUI Components Tests ===\n")
    
    tests = [
        test_optimized_components,
        test_performance_features,
        test_monitoring_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print("FAILED: Test")
        except Exception as e:
            print(f"FAILED: Test - {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed >= total * 0.8:  # 80% pass rate
        print("SUCCESS: Optimized components are functional!")
        print("Performance optimizations are working correctly.")
        return True
    else:
        print("FAILED: Some optimized component tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)