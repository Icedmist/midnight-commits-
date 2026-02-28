#!/usr/bin/env python3
"""
Performance Benchmark - Day 15 Final Project
Comprehensive performance benchmarking and profiling for the entire project.
"""

import argparse
import asyncio
import cProfile
import io
import json
import pstats
import sys
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import psutil
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    name: str
    execution_time: float
    memory_usage: int
    cpu_usage: float
    iterations: int
    avg_time_per_iteration: float
    min_time: float
    max_time: float
    std_dev: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PerformanceReport:
    """Container for comprehensive performance report."""
    benchmark_results: List[BenchmarkResult]
    system_info: Dict[str, Any]
    recommendations: List[str]
    bottlenecks: List[str]
    generated_at: str


class PerformanceBenchmark:
    """
    Comprehensive performance benchmarking suite for Midnight Commits.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results_dir = project_root / "benchmarks"
        self.results_dir.mkdir(exist_ok=True)
        self.system_info = self._get_system_info()

    def _get_system_info(self) -> Dict[str, Any]:
        """Gather system information."""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'python_version': sys.version,
            'platform': sys.platform
        }

    @contextmanager
    def memory_monitor(self):
        """Context manager for memory monitoring."""
        tracemalloc.start()
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        try:
            yield
        finally:
            current_memory = process.memory_info().rss
            memory_used = current_memory - initial_memory
            tracemalloc.stop()
            self._memory_usage = memory_used

    def benchmark_function(self, func: Callable, *args, iterations: int = 100,
                          warmup: int = 10, name: str = None) -> BenchmarkResult:
        """
        Benchmark a function with comprehensive metrics.

        Args:
            func: Function to benchmark
            *args: Arguments to pass to function
            iterations: Number of benchmark iterations
            warmup: Number of warmup iterations
            name: Benchmark name (defaults to function name)

        Returns:
            BenchmarkResult with comprehensive metrics
        """
        if name is None:
            name = func.__name__

        print(f"🔬 Benchmarking {name}...")

        # Warmup phase
        for _ in range(warmup):
            func(*args)

        # Benchmark phase
        times = []
        process = psutil.Process()

        for _ in range(iterations):
            # Memory monitoring
            with self.memory_monitor():
                start_time = time.perf_counter()
                cpu_start = process.cpu_percent()

                result = func(*args)

                cpu_end = process.cpu_percent()
                end_time = time.perf_counter()

            execution_time = end_time - start_time
            times.append(execution_time)

        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = np.std(times)

        # CPU usage (approximate)
        cpu_usage = process.cpu_percent()

        # Memory usage from last iteration
        memory_usage = getattr(self, '_memory_usage', 0)

        result = BenchmarkResult(
            name=name,
            execution_time=sum(times),
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            iterations=iterations,
            avg_time_per_iteration=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

        print(".4f"".4f"".2f"".4f"
        return result

    async def benchmark_async_function(self, func: Callable, *args, iterations: int = 100,
                                     warmup: int = 10, name: str = None) -> BenchmarkResult:
        """
        Benchmark an async function.

        Args:
            func: Async function to benchmark
            *args: Arguments to pass to function
            iterations: Number of benchmark iterations
            warmup: Number of warmup iterations
            name: Benchmark name

        Returns:
            BenchmarkResult with metrics
        """
        if name is None:
            name = func.__name__

        print(f"🔬 Benchmarking async {name}...")

        # Warmup phase
        for _ in range(warmup):
            await func(*args)

        # Benchmark phase
        times = []
        process = psutil.Process()

        for _ in range(iterations):
            with self.memory_monitor():
                start_time = time.perf_counter()
                cpu_start = process.cpu_percent()

                result = await func(*args)

                cpu_end = process.cpu_percent()
                end_time = time.perf_counter()

            execution_time = end_time - start_time
            times.append(execution_time)

        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = np.std(times)
        cpu_usage = process.cpu_percent()
        memory_usage = getattr(self, '_memory_usage', 0)

        result = BenchmarkResult(
            name=name,
            execution_time=sum(times),
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            iterations=iterations,
            avg_time_per_iteration=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

        print(".4f"".4f"".2f"".4f"
        return result

    def profile_function(self, func: Callable, *args, output_file: str = None) -> str:
        """
        Profile a function using cProfile.

        Args:
            func: Function to profile
            *args: Arguments to pass to function
            output_file: Output file for profile results

        Returns:
            Profile output as string
        """
        print(f"📊 Profiling {func.__name__}...")

        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args)

        profiler.disable()

        # Generate profile report
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats()

        profile_output = s.getvalue()

        if output_file:
            profile_path = self.results_dir / output_file
            with open(profile_path, 'w') as f:
                f.write(profile_output)
            print(f"Profile saved to: {profile_path}")

        return profile_output

    def run_comprehensive_benchmark(self) -> PerformanceReport:
        """
        Run comprehensive benchmark suite across all project components.

        Returns:
            PerformanceReport with all benchmark results
        """
        print("🚀 Starting comprehensive benchmark suite...")

        results = []
        recommendations = []
        bottlenecks = []

        # Import and benchmark key functions from each day
        benchmark_targets = self._discover_benchmark_targets()

        for target in benchmark_targets:
            try:
                if asyncio.iscoroutinefunction(target['function']):
                    result = asyncio.run(self.benchmark_async_function(
                        target['function'], *target.get('args', []),
                        name=target['name']
                    ))
                else:
                    result = self.benchmark_function(
                        target['function'], *target.get('args', []),
                        name=target['name']
                    )
                results.append(result)

            except Exception as e:
                print(f"⚠️  Failed to benchmark {target['name']}: {e}")

        # Analyze results for bottlenecks and recommendations
        if results:
            recommendations, bottlenecks = self._analyze_results(results)

        report = PerformanceReport(
            benchmark_results=results,
            system_info=self.system_info,
            recommendations=recommendations,
            bottlenecks=bottlenecks,
            generated_at=time.strftime("%Y-%m-%d %H:%M:%S")
        )

        print("✅ Benchmark suite completed")
        return report

    def _discover_benchmark_targets(self) -> List[Dict[str, Any]]:
        """Discover functions to benchmark across the project."""
        targets = []

        # Define key functions to benchmark from each day
        benchmark_functions = {
            'Day_02_Time_State': [
                ('timer', 'Timer', ['--duration', '1']),
                ('to_do', 'ToDoList', [])
            ],
            'Day_03_Game_Logic': [
                ('rock_paper_scissors', 'RockPaperScissors', []),
                ('tictactoe', 'TicTacToe', [])
            ],
            'Day_04_File_Automation': [
                ('backup', 'BackupManager', ['--source', '.', '--destination', './backup_test']),
                ('renamer', 'FileRenamer', ['--directory', '.', '--pattern', '*.txt'])
            ],
            'Day_05_Web_Scraping': [
                ('book_scraper', 'BookScraper', [])
            ],
            'Day_08_Web_Scraping_Advanced': [
                ('weather_api', 'WeatherAPI', [])
            ],
            'Day_12_Machine_Learning_Basics': [
                ('data_preprocessing', 'DataPreprocessor', [])
            ],
            'Day_13_Security_Cryptography': [
                ('password_hasher', 'PasswordHasher', [])
            ],
            'Day_14_Concurrency_Async': [
                ('async_downloader', 'AsyncDownloader', [])
            ]
        }

        for day, functions in benchmark_functions.items():
            day_path = self.project_root / day
            if day_path.exists():
                for module_name, class_name, args in functions:
                    try:
                        # Import the module
                        sys.path.insert(0, str(day_path))
                        module = __import__(module_name)

                        # Get the main class
                        cls = getattr(module, class_name)

                        # Create instance and get main method
                        if hasattr(cls, '__init__'):
                            instance = cls()
                            if hasattr(instance, 'run') and callable(instance.run):
                                targets.append({
                                    'name': f"{day}.{class_name}.run",
                                    'function': instance.run,
                                    'args': args
                                })
                            elif hasattr(instance, 'main') and callable(instance.main):
                                targets.append({
                                    'name': f"{day}.{class_name}.main",
                                    'function': instance.main,
                                    'args': args
                                })

                    except Exception as e:
                        print(f"Could not import {day}.{module_name}: {e}")
                    finally:
                        if str(day_path) in sys.path:
                            sys.path.remove(str(day_path))

        # Add some synthetic benchmarks
        targets.extend([
            {
                'name': 'synthetic_cpu_intensive',
                'function': self._synthetic_cpu_task,
                'args': [1000]
            },
            {
                'name': 'synthetic_memory_intensive',
                'function': self._synthetic_memory_task,
                'args': [100000]
            },
            {
                'name': 'synthetic_io_intensive',
                'function': self._synthetic_io_task,
                'args': [100]
            }
        ])

        return targets

    def _synthetic_cpu_task(self, iterations: int) -> int:
        """Synthetic CPU-intensive task."""
        result = 0
        for i in range(iterations):
            result += i ** 2
        return result

    def _synthetic_memory_task(self, size: int) -> int:
        """Synthetic memory-intensive task."""
        data = [i for i in range(size)]
        return sum(data)

    def _synthetic_io_task(self, files: int) -> int:
        """Synthetic I/O-intensive task."""
        total_size = 0
        for i in range(files):
            test_file = self.results_dir / f"temp_{i}.txt"
            with open(test_file, 'w') as f:
                f.write("x" * 1000)
            total_size += test_file.stat().st_size
            test_file.unlink()
        return total_size

    def _analyze_results(self, results: List[BenchmarkResult]) -> Tuple[List[str], List[str]]:
        """Analyze benchmark results for insights."""
        recommendations = []
        bottlenecks = []

        # Sort by execution time
        sorted_results = sorted(results, key=lambda x: x.avg_time_per_iteration, reverse=True)

        # Identify slowest components
        if sorted_results:
            slowest = sorted_results[0]
            if slowest.avg_time_per_iteration > 1.0:  # More than 1 second average
                bottlenecks.append(f"{slowest.name}: {slowest.avg_time_per_iteration:.4f}s avg execution time")
                recommendations.append(f"Consider optimizing {slowest.name} - high execution time detected")

        # Memory usage analysis
        high_memory = [r for r in results if r.memory_usage > 50 * 1024 * 1024]  # > 50MB
        for result in high_memory:
            bottlenecks.append(f"{result.name}: High memory usage ({result.memory_usage / 1024 / 1024:.1f} MB)")
            recommendations.append(f"Review memory usage in {result.name}")

        # CPU usage analysis
        high_cpu = [r for r in results if r.cpu_usage > 80.0]
        for result in high_cpu:
            bottlenecks.append(f"{result.name}: High CPU usage ({result.cpu_usage:.1f}%)")

        # Performance consistency
        inconsistent = [r for r in results if r.std_dev / r.avg_time_per_iteration > 0.5]  # > 50% variation
        for result in inconsistent:
            recommendations.append(f"Investigate performance consistency in {result.name}")

        return recommendations, bottlenecks

    def generate_performance_report(self, report: PerformanceReport, output_file: str = None) -> Path:
        """
        Generate detailed performance report.

        Args:
            report: PerformanceReport to save
            output_file: Output filename

        Returns:
            Path to generated report
        """
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"performance_report_{timestamp}.json"

        report_path = self.results_dir / output_file

        # Save JSON report
        with open(report_path, 'w') as f:
            json.dump({
                'performance_report': {
                    'benchmark_results': [r.to_dict() for r in report.benchmark_results],
                    'system_info': report.system_info,
                    'recommendations': report.recommendations,
                    'bottlenecks': report.bottlenecks,
                    'generated_at': report.generated_at
                }
            }, f, indent=2)

        # Generate markdown summary
        md_path = report_path.with_suffix('.md')
        self._generate_markdown_report(report, md_path)

        # Generate charts
        self._generate_performance_charts(report)

        print(f"📊 Performance report saved to: {report_path}")
        print(f"📋 Markdown summary: {md_path}")

        return report_path

    def _generate_markdown_report(self, report: PerformanceReport, output_path: Path):
        """Generate markdown performance report."""
        with open(output_path, 'w') as f:
            f.write("# Performance Benchmark Report\n\n")
            f.write(f"**Generated:** {report.generated_at}\n\n")

            f.write("## System Information\n\n")
            f.write(f"- **CPU Cores:** {report.system_info['cpu_count']} ({report.system_info['cpu_count_logical']} logical)\n")
            f.write(f"- **Memory:** {report.system_info['memory_total'] / 1024 / 1024 / 1024:.1f} GB total\n")
            f.write(f"- **Python:** {report.system_info['python_version']}\n")
            f.write(f"- **Platform:** {report.system_info['platform']}\n\n")

            f.write("## Benchmark Results\n\n")
            if report.benchmark_results:
                f.write("| Component | Avg Time | Memory (MB) | CPU % | Std Dev |\n")
                f.write("|-----------|----------|-------------|-------|--------|\n")

                for result in sorted(report.benchmark_results, key=lambda x: x.avg_time_per_iteration):
                    f.write(f"| {result.name} | {result.avg_time_per_iteration:.4f}s | {result.memory_usage / 1024 / 1024:.1f} | {result.cpu_usage:.1f} | {result.std_dev:.4f} |\n")

                f.write("\n")

            f.write("## Performance Analysis\n\n")

            if report.bottlenecks:
                f.write("### Bottlenecks Identified\n\n")
                for bottleneck in report.bottlenecks:
                    f.write(f"- ⚠️  {bottleneck}\n")
                f.write("\n")

            if report.recommendations:
                f.write("### Recommendations\n\n")
                for rec in report.recommendations:
                    f.write(f"- 💡 {rec}\n")
                f.write("\n")

            f.write("## Summary Statistics\n\n")
            if report.benchmark_results:
                total_time = sum(r.execution_time for r in report.benchmark_results)
                avg_memory = sum(r.memory_usage for r in report.benchmark_results) / len(report.benchmark_results)
                avg_cpu = sum(r.cpu_usage for r in report.benchmark_results) / len(report.benchmark_results)

                f.write(f"- **Total Benchmark Time:** {total_time:.2f}s\n")
                f.write(f"- **Average Memory Usage:** {avg_memory / 1024 / 1024:.1f} MB\n")
                f.write(f"- **Average CPU Usage:** {avg_cpu:.1f}%\n")
                f.write(f"- **Components Benchmarked:** {len(report.benchmark_results)}\n")

    def _generate_performance_charts(self, report: PerformanceReport):
        """Generate performance visualization charts."""
        if not report.benchmark_results:
            return

        # Execution time chart
        plt.figure(figsize=(12, 6))

        names = [r.name for r in report.benchmark_results]
        times = [r.avg_time_per_iteration for r in report.benchmark_results]

        plt.subplot(1, 2, 1)
        plt.barh(names, times)
        plt.title('Average Execution Time by Component')
        plt.xlabel('Time (seconds)')

        # Memory usage chart
        memory_mb = [r.memory_usage / 1024 / 1024 for r in report.benchmark_results]

        plt.subplot(1, 2, 2)
        plt.barh(names, memory_mb)
        plt.title('Memory Usage by Component')
        plt.xlabel('Memory (MB)')

        plt.tight_layout()

        chart_path = self.results_dir / f"performance_charts_{time.strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"📈 Performance charts saved to: {chart_path}")

    def compare_benchmarks(self, baseline_file: str, current_file: str) -> Dict[str, Any]:
        """
        Compare two benchmark reports.

        Args:
            baseline_file: Path to baseline benchmark results
            current_file: Path to current benchmark results

        Returns:
            Comparison results
        """
        # Load baseline
        with open(self.results_dir / baseline_file, 'r') as f:
            baseline_data = json.load(f)

        # Load current
        with open(self.results_dir / current_file, 'r') as f:
            current_data = json.load(f)

        baseline_results = {r['name']: r for r in baseline_data['performance_report']['benchmark_results']}
        current_results = {r['name']: r for r in current_data['performance_report']['benchmark_results']}

        comparison = {}

        for name in set(baseline_results.keys()) | set(current_results.keys()):
            if name in baseline_results and name in current_results:
                baseline = baseline_results[name]
                current = current_results[name]

                time_diff = current['avg_time_per_iteration'] - baseline['avg_time_per_iteration']
                memory_diff = current['memory_usage'] - baseline['memory_usage']

                comparison[name] = {
                    'time_change': time_diff,
                    'time_change_percent': (time_diff / baseline['avg_time_per_iteration']) * 100 if baseline['avg_time_per_iteration'] > 0 else 0,
                    'memory_change': memory_diff,
                    'memory_change_percent': (memory_diff / baseline['memory_usage']) * 100 if baseline['memory_usage'] > 0 else 0
                }

        return comparison


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Performance Benchmark for Midnight Commits"
    )
    parser.add_argument(
        "action",
        choices=["benchmark", "profile", "report", "compare"],
        help="Action to perform"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory"
    )
    parser.add_argument(
        "--output",
        help="Output file for results"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=50,
        help="Number of benchmark iterations"
    )
    parser.add_argument(
        "--baseline",
        help="Baseline benchmark file for comparison"
    )
    parser.add_argument(
        "--current",
        help="Current benchmark file for comparison"
    )

    args = parser.parse_args()

    # Initialize benchmark suite
    project_root = Path(args.project_root).resolve()
    benchmark = PerformanceBenchmark(project_root)

    try:
        if args.action == "benchmark":
            report = benchmark.run_comprehensive_benchmark()
            output_file = args.output or f"benchmark_{time.strftime('%Y%m%d_%H%M%S')}.json"
            benchmark.generate_performance_report(report, output_file)

        elif args.action == "profile":
            # Profile a specific function (example)
            from Day_02_Time_State.timer import Timer
            timer = Timer()
            profile_output = benchmark.profile_function(
                timer.run,
                ["--duration", "5"],
                output_file=args.output or "timer_profile.txt"
            )
            print("Profile completed")

        elif args.action == "report":
            # Generate report from existing benchmark file
            if not args.output:
                print("Error: --output required for report generation")
                sys.exit(1)

            with open(args.output, 'r') as f:
                data = json.load(f)

            report_data = data['performance_report']
            report = PerformanceReport(
                benchmark_results=[BenchmarkResult(**r) for r in report_data['benchmark_results']],
                system_info=report_data['system_info'],
                recommendations=report_data['recommendations'],
                bottlenecks=report_data['bottlenecks'],
                generated_at=report_data['generated_at']
            )

            benchmark.generate_performance_report(report, args.output.replace('.json', '_regenerated.json'))

        elif args.action == "compare":
            if not args.baseline or not args.current:
                print("Error: --baseline and --current required for comparison")
                sys.exit(1)

            comparison = benchmark.compare_benchmarks(args.baseline, args.current)

            print("Benchmark Comparison Results:")
            print("=" * 50)
            for name, comp in comparison.items():
                print(f"\n{name}:")
                print(".2f"                print(".2f"
        print("✓ Operation completed successfully")

    except Exception as e:
        print(f"✗ Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()