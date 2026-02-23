"""
Performance Profiler
Profile code execution, memory usage, and bottlenecks
"""

import cProfile
import pstats
import io
from typing import Callable, Dict, Any
import time
import tracemalloc
from contextlib import contextmanager
import functools
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Profiler:
    """Code performance profiler"""

    def __init__(self):
        """Initialize profiler"""
        self.profiles: Dict[str, pstats.Stats] = {}

    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile function"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            try:
                result = func(*args, **kwargs)
            finally:
                profiler.disable()
                self.profiles[func.__name__] = pstats.Stats(profiler)

            return result

        return wrapper

    def print_stats(self, func_name: str, top_n: int = 10) -> None:
        """Print profiling stats"""
        if func_name not in self.profiles:
            logger.error(f"❌ No profile for {func_name}")
            return

        stats = self.profiles[func_name]
        print(f"\n📊 Profile: {func_name}\n")
        stats.strip_dirs().sort_stats('cumulative').print_stats(top_n)

    def get_stats(self, func_name: str) -> Dict:
        """Get stats as dictionary"""
        if func_name not in self.profiles:
            return {}

        stats = self.profiles[func_name]
        stats_dict = {}

        for key, value in stats.stats.items():
            func_name_key = key[2]
            stats_dict[func_name_key] = {
                'calls': value[0],
                'total_time': value[3],
                'cumulative_time': value[4]
            }

        return stats_dict


class MemoryProfiler:
    """Memory usage profiler"""

    def __init__(self):
        """Initialize memory profiler"""
        self.snapshots: Dict[str, tracemalloc.Snapshot] = {}

    @contextmanager
    def track_memory(self, name: str):
        """Context manager to track memory"""
        tracemalloc.start()
        logger.info(f"🧠 Starting memory tracking: {name}")

        try:
            yield
        finally:
            current, peak = tracemalloc.get_traced_memory()
            self.snapshots[name] = tracemalloc.take_snapshot()
            tracemalloc.stop()

            logger.info(f"📊 Memory usage ({name}):")
            logger.info(f"   Current: {current / 1024 / 1024:.2f} MB")
            logger.info(f"   Peak: {peak / 1024 / 1024:.2f} MB")

    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile function memory"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.track_memory(func.__name__):
                return func(*args, **kwargs)

        return wrapper

    def print_top_allocations(self, name: str, limit: int = 10) -> None:
        """Print top memory allocations"""
        if name not in self.snapshots:
            logger.error(f"❌ No snapshot for {name}")
            return

        snapshot = self.snapshots[name]
        print(f"\n🧠 Top {limit} Memory Allocations: {name}\n")

        for stat in snapshot.statistics('lineno')[:limit]:
            print(stat)


class CPUProfiler:
    """CPU time profiler"""

    def __init__(self):
        """Initialize CPU profiler"""
        self.timings: Dict[str, list] = {}

    def time_function(self, func: Callable) -> Callable:
        """Decorator to time function"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start

            if func.__name__ not in self.timings:
                self.timings[func.__name__] = []

            self.timings[func.__name__].append(elapsed)
            logger.info(f"⏱️  {func.__name__}: {elapsed*1000:.2f}ms")

            return result

        return wrapper

    def get_stats(self, func_name: str) -> Dict:
        """Get timing statistics"""
        if func_name not in self.timings or not self.timings[func_name]:
            return {}

        times = self.timings[func_name]
        return {
            'function': func_name,
            'calls': len(times),
            'min': min(times),
            'max': max(times),
            'avg': sum(times) / len(times),
            'total': sum(times)
        }

    def print_stats(self, func_name: str = None) -> None:
        """Print timing statistics"""
        if func_name:
            if func_name not in self.timings:
                logger.error(f"❌ No timings for {func_name}")
                return

            stats = self.get_stats(func_name)
            print(f"\n⏱️  {func_name} Stats:")
            print(f"  Calls: {stats['calls']}")
            print(f"  Min: {stats['min']*1000:.2f}ms")
            print(f"  Max: {stats['max']*1000:.2f}ms")
            print(f"  Avg: {stats['avg']*1000:.2f}ms")
            print(f"  Total: {stats['total']*1000:.2f}ms")
        else:
            print("\n⏱️  Timing Statistics:\n")
            for name in self.timings:
                stats = self.get_stats(name)
                print(f"{name}: {stats['avg']*1000:.2f}ms (avg)")


class Bottleneck:
    """Identify performance bottlenecks"""

    def __init__(self, threshold_ms: float = 100):
        """Initialize bottleneck detector"""
        self.threshold_ms = threshold_ms
        self.slow_calls: Dict[str, list] = {}

    def track(self, func_name: str, duration_ms: float) -> None:
        """Track potentially slow call"""
        if duration_ms > self.threshold_ms:
            if func_name not in self.slow_calls:
                self.slow_calls[func_name] = []

            self.slow_calls[func_name].append(duration_ms)
            logger.warning(f"🚨 Slow call: {func_name} ({duration_ms:.2f}ms)")

    def get_bottlenecks(self) -> Dict:
        """Get identified bottlenecks"""
        bottlenecks = {}

        for func, times in self.slow_calls.items():
            bottlenecks[func] = {
                'count': len(times),
                'avg': sum(times) / len(times),
                'max': max(times)
            }

        return bottlenecks


def demo_profiler():
    """Demo profiler"""
    profiler = Profiler()
    mem_profiler = MemoryProfiler()
    cpu_profiler = CPUProfiler()

    @cpu_profiler.time_function
    def fibonacci(n):
        """Calculate fibonacci"""
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)

    @mem_profiler.profile_function
    def allocate_memory():
        """Allocate memory"""
        data = [i for i in range(1000000)]
        return sum(data)

    print("\n📊 Performance Profiler Demo\n")

    # CPU profile
    fibonacci(20)
    cpu_profiler.print_stats("fibonacci")

    # Memory profile
    allocate_memory()


if __name__ == "__main__":
    print("📊 Performance Profiler\n")
    
    print("Features:")
    print("✓ CPU profiling")
    print("✓ Memory profiling")
    print("✓ Function timing")
    print("✓ Bottleneck detection")
    print("✓ Statistics reporting")
