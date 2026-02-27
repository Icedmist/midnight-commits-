#!/usr/bin/env python3
"""
Multiprocessing Calculator
A multiprocessing calculator for parallel computation of mathematical operations.
Features: Parallel processing, load balancing, result aggregation, and performance monitoring.
"""

import multiprocessing as mp
from multiprocessing import Pool, Manager, Queue, Value
import time
import math
import random
import argparse
import sys
from typing import List, Dict, Any, Callable
import logging


class MultiprocessingCalculator:
    """Multiprocessing calculator for parallel computations."""

    def __init__(self, num_processes: int = None):
        """Initialize the calculator."""
        self.num_processes = num_processes or mp.cpu_count()
        self.pool = None
        self.manager = None

    def __enter__(self):
        """Context manager entry."""
        self.manager = Manager()
        self.pool = Pool(processes=self.num_processes)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.pool:
            self.pool.close()
            self.pool.join()

    def calculate_factorial(self, numbers: List[int]) -> List[Dict[str, Any]]:
        """Calculate factorial for multiple numbers in parallel."""
        def factorial_worker(n: int) -> Dict[str, Any]:
            start_time = time.time()
            result = math.factorial(n)
            end_time = time.time()
            return {
                'input': n,
                'operation': 'factorial',
                'result': result,
                'computation_time': end_time - start_time
            }

        results = self.pool.map(factorial_worker, numbers)
        return results

    def calculate_primes(self, ranges: List[tuple]) -> List[Dict[str, Any]]:
        """Find prime numbers in multiple ranges in parallel."""
        def prime_worker(range_tuple: tuple) -> Dict[str, Any]:
            start, end = range_tuple
            start_time = time.time()

            def is_prime(n):
                if n <= 1:
                    return False
                if n <= 3:
                    return True
                if n % 2 == 0 or n % 3 == 0:
                    return False
                i = 5
                while i * i <= n:
                    if n % i == 0 or n % (i + 2) == 0:
                        return False
                    i += 6
                return True

            primes = [n for n in range(start, end + 1) if is_prime(n)]
            end_time = time.time()

            return {
                'input': f"{start}-{end}",
                'operation': 'prime_finding',
                'result': primes,
                'count': len(primes),
                'computation_time': end_time - start_time
            }

        results = self.pool.map(prime_worker, ranges)
        return results

    def matrix_operations(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform matrix operations in parallel."""
        def matrix_worker(op_data: Dict[str, Any]) -> Dict[str, Any]:
            operation = op_data['operation']
            matrices = op_data['matrices']
            start_time = time.time()

            try:
                if operation == 'multiply':
                    result = self._matrix_multiply(matrices[0], matrices[1])
                elif operation == 'add':
                    result = self._matrix_add(matrices[0], matrices[1])
                elif operation == 'transpose':
                    result = self._matrix_transpose(matrices[0])
                elif operation == 'determinant':
                    result = self._matrix_determinant(matrices[0])
                else:
                    raise ValueError(f"Unsupported operation: {operation}")

                end_time = time.time()
                return {
                    'input': op_data,
                    'operation': operation,
                    'result': result,
                    'success': True,
                    'computation_time': end_time - start_time
                }
            except Exception as e:
                end_time = time.time()
                return {
                    'input': op_data,
                    'operation': operation,
                    'result': None,
                    'success': False,
                    'error': str(e),
                    'computation_time': end_time - start_time
                }

        results = self.pool.map(matrix_worker, operations)
        return results

    def _matrix_multiply(self, A, B):
        """Matrix multiplication."""
        if len(A[0]) != len(B):
            raise ValueError("Matrix dimensions incompatible for multiplication")

        result = [[0 for _ in range(len(B[0]))] for _ in range(len(A))]
        for i in range(len(A)):
            for j in range(len(B[0])):
                for k in range(len(B)):
                    result[i][j] += A[i][k] * B[k][j]
        return result

    def _matrix_add(self, A, B):
        """Matrix addition."""
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            raise ValueError("Matrix dimensions incompatible for addition")

        result = [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
        return result

    def _matrix_transpose(self, A):
        """Matrix transpose."""
        result = [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]
        return result

    def _matrix_determinant(self, A):
        """Calculate matrix determinant (for 2x2 and 3x3 matrices)."""
        if len(A) != len(A[0]):
            raise ValueError("Matrix must be square")

        n = len(A)
        if n == 2:
            return A[0][0] * A[1][1] - A[0][1] * A[1][0]
        elif n == 3:
            return (A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) -
                   A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) +
                   A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))
        else:
            raise ValueError("Determinant calculation only supported for 2x2 and 3x3 matrices")

    def monte_carlo_simulation(self, simulations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run Monte Carlo simulations in parallel."""
        def monte_carlo_worker(sim_data: Dict[str, Any]) -> Dict[str, Any]:
            simulation_type = sim_data['type']
            params = sim_data['params']
            n_samples = sim_data.get('n_samples', 10000)
            start_time = time.time()

            if simulation_type == 'pi_estimation':
                result = self._estimate_pi(n_samples)
            elif simulation_type == 'integration':
                result = self._monte_carlo_integration(params['func'], params['a'], params['b'], n_samples)
            elif simulation_type == 'random_walk':
                result = self._random_walk_simulation(params['steps'], n_samples)
            else:
                raise ValueError(f"Unsupported simulation type: {simulation_type}")

            end_time = time.time()
            return {
                'input': sim_data,
                'operation': 'monte_carlo',
                'type': simulation_type,
                'result': result,
                'n_samples': n_samples,
                'computation_time': end_time - start_time
            }

        results = self.pool.map(monte_carlo_worker, simulations)
        return results

    def _estimate_pi(self, n_samples: int) -> float:
        """Estimate π using Monte Carlo method."""
        inside_circle = 0
        for _ in range(n_samples):
            x, y = random.random(), random.random()
            if x**2 + y**2 <= 1:
                inside_circle += 1
        return 4 * inside_circle / n_samples

    def _monte_carlo_integration(self, func: Callable, a: float, b: float, n_samples: int) -> float:
        """Monte Carlo integration."""
        total = 0
        for _ in range(n_samples):
            x = random.uniform(a, b)
            total += func(x)
        return (b - a) * total / n_samples

    def _random_walk_simulation(self, steps: int, n_samples: int) -> Dict[str, Any]:
        """Random walk simulation."""
        final_positions = []
        for _ in range(n_samples):
            position = 0
            for _ in range(steps):
                position += 1 if random.random() > 0.5 else -1
            final_positions.append(position)

        return {
            'mean_position': sum(final_positions) / len(final_positions),
            'std_position': math.sqrt(sum((x - sum(final_positions)/len(final_positions))**2 for x in final_positions) / len(final_positions)),
            'min_position': min(final_positions),
            'max_position': max(final_positions)
        }


class PerformanceMonitor:
    """Monitor performance of multiprocessing operations."""

    def __init__(self):
        """Initialize performance monitor."""
        self.start_time = None
        self.end_time = None

    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()

    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return statistics."""
        self.end_time = time.time()
        total_time = self.end_time - self.start_time

        return {
            'total_time': total_time,
            'cpu_count': mp.cpu_count(),
            'processes_used': mp.current_process().name
        }


def benchmark_operations():
    """Benchmark different operations."""
    print("Running multiprocessing benchmarks...")

    monitor = PerformanceMonitor()
    monitor.start_monitoring()

    with MultiprocessingCalculator() as calc:
        # Factorial benchmark
        numbers = [100, 150, 200, 250]
        factorial_results = calc.calculate_factorial(numbers)
        print(f"Factorial calculations: {len(numbers)} numbers")

        # Prime finding benchmark
        ranges = [(1, 10000), (10001, 20000), (20001, 30000), (30001, 40000)]
        prime_results = calc.calculate_primes(ranges)
        print(f"Prime finding: {len(ranges)} ranges")

        # Matrix operations benchmark
        operations = [
            {'operation': 'multiply', 'matrices': [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]},
            {'operation': 'add', 'matrices': [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]},
            {'operation': 'transpose', 'matrices': [[[1, 2, 3], [4, 5, 6]]]},
            {'operation': 'determinant', 'matrices': [[[1, 2], [3, 4]]]}
        ]
        matrix_results = calc.matrix_operations(operations)
        print(f"Matrix operations: {len(operations)} operations")

        # Monte Carlo simulations
        simulations = [
            {'type': 'pi_estimation', 'n_samples': 50000},
            {'type': 'random_walk', 'params': {'steps': 100}, 'n_samples': 1000}
        ]
        mc_results = calc.monte_carlo_simulation(simulations)
        print(f"Monte Carlo simulations: {len(simulations)} simulations")

    stats = monitor.stop_monitoring()

    print("
Benchmark Results:")
    print(".2f")
    print(f"CPU cores available: {stats['cpu_count']}")

    # Print sample results
    if factorial_results:
        print(f"\nSample factorial result: {factorial_results[0]['input']}! = {factorial_results[0]['result']}")

    if prime_results:
        total_primes = sum(r['count'] for r in prime_results)
        print(f"Total primes found: {total_primes}")

    if mc_results:
        for result in mc_results:
            if result['type'] == 'pi_estimation':
                print(".4f")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Multiprocessing Calculator")
    parser.add_argument("--operation", choices=['factorial', 'primes', 'matrix', 'monte_carlo', 'benchmark'],
                       default='benchmark', help="Operation to perform")
    parser.add_argument("--processes", type=int, default=None, help="Number of processes")
    parser.add_argument("--numbers", nargs='*', type=int, help="Numbers for factorial calculation")
    parser.add_argument("--ranges", nargs='*', help="Ranges for prime finding (format: start-end)")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    try:
        calc = MultiprocessingCalculator(args.processes)

        with calc:
            if args.operation == 'factorial':
                if not args.numbers:
                    print("Error: --numbers required for factorial operation")
                    sys.exit(1)

                results = calc.calculate_factorial(args.numbers)
                for result in results:
                    print(f"{result['input']}! = {result['result']} (time: {result['computation_time']:.4f}s)")

            elif args.operation == 'primes':
                if not args.ranges:
                    print("Error: --ranges required for prime finding")
                    sys.exit(1)

                ranges = []
                for r in args.ranges:
                    start, end = map(int, r.split('-'))
                    ranges.append((start, end))

                results = calc.calculate_primes(ranges)
                for result in results:
                    print(f"Range {result['input']}: {result['count']} primes found")

            elif args.operation == 'benchmark' or args.benchmark:
                benchmark_operations()

    except KeyboardInterrupt:
        print("\nOperation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()