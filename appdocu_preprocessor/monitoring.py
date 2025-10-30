"""
Performance Monitoring System for AppDocU Preprocessor
Provides timing measurements, performance metrics collection, and performance logging

This module provides comprehensive performance monitoring capabilities for the AppDocU
preprocessor system, enabling detailed timing measurements, performance metrics collection,
and performance logging for optimization and troubleshooting. It tracks operation durations,
resource usage, throughput metrics, and provides detailed performance reporting for
continuous system improvement.
"""
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import json
import statistics

from appdocu_preprocessor.config import get_global_config
from appdocu_preprocessor.exceptions import AppDocUException


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Data class for performance metrics"""
    operation: str
    duration_seconds: float
    start_time: datetime
    end_time: datetime
    memory_used_mb: Optional[float] = None
    file_size_mb: Optional[float] = None
    items_processed: Optional[int] = None
    success_rate: Optional[float] = None
    error_count: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class PerformanceMonitor:
    """Centralized performance monitoring system"""
    
    def __init__(self):
        self.config = get_global_config()
        self.metrics: List[PerformanceMetric] = []
        self.operation_timings: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()
        self.logger = logging.getLogger(f"{__name__}.PerformanceMonitor")
        self._enabled = self.config.get_config().performance_monitoring
        
    def is_enabled(self) -> bool:
        """Check if performance monitoring is enabled"""
        return self._enabled
    
    def start_timer(self, operation: str) -> float:
        """Start timing an operation"""
        if not self.is_enabled():
            return time.time()
        return time.time()
    
    def stop_timer(self, operation: str, start_time: float, **details) -> PerformanceMetric:
        """Stop timing an operation and record metrics"""
        if not self.is_enabled():
            return None
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Record timing for statistics
        self.operation_timings[operation].append(duration)
        
        # Create performance metric
        metric = PerformanceMetric(
            operation=operation,
            duration_seconds=duration,
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            details=details if details else {}
        )
        
        # Add to metrics list with thread safety
        with self.lock:
            self.metrics.append(metric)
        
        # Log performance if sample rate allows
        config = self.config.get_config()
        if config.performance_sample_rate >= 1.0 or hash(operation) % (1/config.performance_sample_rate) == 0:
            self.logger.info(f"⏱️ {operation}: {duration:.3f}s")
            if details:
                self.logger.debug(f"   Details: {details}")
        
        return metric
    
    def get_statistics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics"""
        with self.lock:
            if operation:
                timings = self.operation_timings.get(operation, [])
            else:
                # Combine all operation timings
                timings = []
                for op_timings in self.operation_timings.values():
                    timings.extend(op_timings)
            
            if not timings:
                return {}
            
            stats = {
                'count': len(timings),
                'total_time': sum(timings),
                'average_time': statistics.mean(timings),
                'median_time': statistics.median(timings),
                'min_time': min(timings),
                'max_time': max(timings),
            }
            
            if len(timings) > 1:
                stats['std_deviation'] = statistics.stdev(timings)
                stats['variance'] = statistics.variance(timings)
            
            return stats
    
    def get_recent_metrics(self, operation: Optional[str] = None, last_n: int = 100) -> List[PerformanceMetric]:
        """Get recent performance metrics"""
        with self.lock:
            if operation:
                metrics = [m for m in self.metrics if m.operation == operation]
            else:
                metrics = self.metrics
            
            return metrics[-last_n:]
    
    def report_performance(self, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'monitoring_enabled': self.is_enabled(),
            'total_operations': len(self.metrics),
            'operations': {}
        }
        
        # Generate statistics for each operation type
        for operation in set(m.operation for m in self.metrics):
            stats = self.get_statistics(operation)
            recent_metrics = self.get_recent_metrics(operation, 10)
            report['operations'][operation] = {
                'statistics': stats,
                'recent_samples': [asdict(m) for m in recent_metrics]
            }
        
        # Write report to file if output directory provided
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            report_file = output_dir / "performance_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            self.logger.info(f"Performance report written to {report_file}")
        
        return report
    
    def reset_metrics(self):
        """Reset all collected metrics"""
        with self.lock:
            self.metrics.clear()
            self.operation_timings.clear()
        self.logger.info("Performance metrics reset")


class TimedOperation:
    """Context manager for timing operations"""
    
    def __init__(self, operation: str, monitor: PerformanceMonitor, **details):
        self.operation = operation
        self.monitor = monitor
        self.details = details
        self.start_time = None
    
    def __enter__(self):
        if self.monitor.is_enabled():
            self.start_time = self.monitor.start_timer(self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.monitor.is_enabled() and self.start_time:
            details = self.details.copy()
            if exc_type:
                details['error'] = f"{exc_type.__name__}: {exc_val}"
            self.monitor.stop_timer(self.operation, self.start_time, **details)


def timed_function(operation_name: Optional[str] = None, monitor: Optional[PerformanceMonitor] = None):
    """Decorator for timing function execution"""
    def decorator(func: Callable) -> Callable:
        nonlocal operation_name
        if not operation_name:
            operation_name = f"{func.__module__}.{func.__name__}"
        
        def wrapper(*args, **kwargs):
            if monitor and monitor.is_enabled():
                start_time = monitor.start_timer(operation_name)
                try:
                    result = func(*args, **kwargs)
                    monitor.stop_timer(operation_name, start_time)
                    return result
                except Exception as e:
                    monitor.stop_timer(operation_name, start_time, error=str(e))
                    raise
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Global performance monitor instance
class GlobalPerformanceMonitor:
    """Singleton global performance monitor"""
    _instance: Optional[PerformanceMonitor] = None
    _lock = threading.Lock()
    
    @classmethod
    def get_monitor(cls) -> PerformanceMonitor:
        """Get the global performance monitor instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = PerformanceMonitor()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset the global monitor instance"""
        with cls._lock:
            cls._instance = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    return GlobalPerformanceMonitor.get_monitor()


def time_operation(operation: str, **details) -> TimedOperation:
    """Create a timed operation context manager"""
    monitor = get_performance_monitor()
    return TimedOperation(operation, monitor, **details)


def time_function(operation_name: Optional[str] = None):
    """Decorator to time a function"""
    monitor = get_performance_monitor()
    return timed_function(operation_name, monitor)


def get_performance_report(output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Get performance report from global monitor"""
    monitor = get_performance_monitor()
    return monitor.report_performance(output_dir)


def reset_performance_metrics():
    """Reset performance metrics in global monitor"""
    monitor = get_performance_monitor()
    monitor.reset_metrics()


# Example usage and testing
if __name__ == "__main__":
    import time
    from appdocu_preprocessor.config import ConfigManager
    
    # Enable performance monitoring for testing
    config = ConfigManager()
    config.update_config(performance_monitoring=True, performance_sample_rate=1.0)
    
    monitor = get_performance_monitor()
    print(f"Performance monitoring enabled: {monitor.is_enabled()}")
    
    # Test timing an operation
    with time_operation("test_operation", test_param="value"):
        time.sleep(0.1)  # Simulate work
    
    # Test timing function
    @time_function("test_function")
    def test_function():
        time.sleep(0.05)
        return "result"
    
    result = test_function()
    print(f"Function result: {result}")
    
    # Generate report
    report = get_performance_report()
    print(f"Total operations: {report['total_operations']}")
    print(f"Operations: {list(report['operations'].keys())}")
