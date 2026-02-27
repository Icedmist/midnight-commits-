#!/usr/bin/env python3
"""
Thread Pool Implementation
A custom thread pool implementation with task queuing and worker management.
Features: Thread pool, task scheduling, result collection, and graceful shutdown.
"""

import threading
import queue
import time
import logging
from typing import Callable, Any, List, Optional
import argparse
import sys


class ThreadPool:
    """Custom thread pool implementation."""

    def __init__(self, num_threads: int = 4):
        """Initialize thread pool with specified number of threads."""
        self.num_threads = num_threads
        self.tasks = queue.Queue()
        self.results = queue.Queue()
        self.workers = []
        self.shutdown_event = threading.Event()
        self.active_tasks = 0
        self.task_lock = threading.Lock()

        # Start worker threads
        for i in range(num_threads):
            worker = threading.Thread(target=self._worker, name=f"Worker-{i+1}")
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

        logging.info(f"Thread pool initialized with {num_threads} workers")

    def _worker(self):
        """Worker thread function."""
        while not self.shutdown_event.is_set():
            try:
                # Get task from queue with timeout
                task = self.tasks.get(timeout=1)
                if task is None:
                    break

                func, args, kwargs, task_id = task

                try:
                    # Execute task
                    result = func(*args, **kwargs)
                    self.results.put((task_id, result, None))
                except Exception as e:
                    self.results.put((task_id, None, str(e)))
                finally:
                    with self.task_lock:
                        self.active_tasks -= 1

                self.tasks.task_done()

            except queue.Empty:
                continue

        logging.debug(f"Worker {threading.current_thread().name} shutting down")

    def submit(self, func: Callable, *args, **kwargs) -> int:
        """Submit a task to the thread pool."""
        with self.task_lock:
            task_id = self.active_tasks
            self.active_tasks += 1

        self.tasks.put((func, args, kwargs, task_id))
        logging.debug(f"Task {task_id} submitted")
        return task_id

    def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """Apply function to each item in list using thread pool."""
        task_ids = []
        for item in items:
            task_id = self.submit(func, item)
            task_ids.append(task_id)

        # Collect results
        results = []
        result_dict = {}

        while len(result_dict) < len(task_ids):
            try:
                task_id, result, error = self.results.get(timeout=1)
                if error:
                    result_dict[task_id] = Exception(error)
                else:
                    result_dict[task_id] = result
            except queue.Empty:
                continue

        # Order results by task ID
        for i in range(len(task_ids)):
            results.append(result_dict[i])

        return results

    def shutdown(self, wait: bool = True):
        """Shutdown the thread pool."""
        logging.info("Shutting down thread pool...")

        # Signal shutdown
        self.shutdown_event.set()

        # Add poison pills for workers
        for _ in range(self.num_threads):
            self.tasks.put(None)

        # Wait for workers to finish
        if wait:
            for worker in self.workers:
                worker.join()

        logging.info("Thread pool shutdown complete")

    def get_results(self, timeout: float = None) -> List[tuple]:
        """Get all available results."""
        results = []
        while True:
            try:
                result = self.results.get(timeout=timeout)
                results.append(result)
                timeout = 0.1  # Short timeout for remaining results
            except queue.Empty:
                break
        return results

    def wait_completion(self, timeout: float = None):
        """Wait for all tasks to complete."""
        self.tasks.join()

        # Wait for all results to be processed
        start_time = time.time()
        while self.active_tasks > 0:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError("Timeout waiting for task completion")
            time.sleep(0.1)


class TaskScheduler:
    """Task scheduler with priority and timing support."""

    def __init__(self, thread_pool: ThreadPool):
        """Initialize task scheduler."""
        self.thread_pool = thread_pool
        self.scheduled_tasks = queue.PriorityQueue()
        self.scheduler_thread = None
        self.running = False

    def schedule_task(self, func: Callable, delay: float, *args, priority: int = 1, **kwargs):
        """Schedule a task to run after delay seconds."""
        execution_time = time.time() + delay
        self.scheduled_tasks.put((priority, execution_time, func, args, kwargs))

    def start(self):
        """Start the scheduler."""
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()

    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                # Check for due tasks
                if not self.scheduled_tasks.empty():
                    priority, execution_time, func, args, kwargs = self.scheduled_tasks.get()

                    current_time = time.time()
                    if current_time >= execution_time:
                        # Execute task
                        self.thread_pool.submit(func, *args, **kwargs)
                    else:
                        # Put back if not due yet
                        self.scheduled_tasks.put((priority, execution_time, func, args, kwargs))
                        time.sleep(min(1.0, execution_time - current_time))
                else:
                    time.sleep(1.0)

            except Exception as e:
                logging.error(f"Scheduler error: {e}")


def example_task(task_id: int, duration: float = 1.0):
    """Example task for demonstration."""
    print(f"Task {task_id} started")
    time.sleep(duration)
    result = f"Task {task_id} completed after {duration}s"
    print(result)
    return result


def cpu_intensive_task(n: int) -> int:
    """CPU-intensive task for testing."""
    result = 0
    for i in range(n):
        result += i ** 2
    return result


def io_task(url: str) -> str:
    """I/O bound task for testing."""
    import requests
    try:
        response = requests.get(url, timeout=5)
        return f"URL {url}: {response.status_code}"
    except Exception as e:
        return f"URL {url}: Error - {str(e)}"


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Thread Pool Tool")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads in pool")
    parser.add_argument("--tasks", type=int, default=10, help="Number of tasks to run")
    parser.add_argument("--task-type", choices=['cpu', 'io', 'mixed'], default='cpu',
                       help="Type of tasks to run")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        # Create thread pool
        pool = ThreadPool(args.threads)

        print(f"Running {args.tasks} {args.task_type} tasks with {args.threads} threads...")

        start_time = time.time()

        if args.task_type == 'cpu':
            # CPU-intensive tasks
            tasks = [lambda n=i: cpu_intensive_task(100000 + n * 1000) for i in range(args.tasks)]
            results = pool.map(lambda func: func(), tasks)

        elif args.task_type == 'io':
            # I/O tasks
            urls = [
                'https://httpbin.org/delay/1',
                'https://httpbin.org/get',
                'https://httpbin.org/status/200',
                'https://httpbin.org/json'
            ] * (args.tasks // 4 + 1)
            urls = urls[:args.tasks]

            results = pool.map(io_task, urls)

        else:  # mixed
            # Mix of CPU and I/O tasks
            results = []
            for i in range(args.tasks):
                if i % 2 == 0:
                    pool.submit(cpu_intensive_task, 50000 + i * 500)
                else:
                    pool.submit(example_task, i, 0.5)

            # Wait for completion
            pool.wait_completion()

            # Get results
            results = pool.get_results()

        end_time = time.time()

        print(f"\nCompleted {len(results)} tasks in {end_time - start_time:.2f} seconds")
        print(".2f")

        # Shutdown pool
        pool.shutdown()

    except KeyboardInterrupt:
        print("\nShutting down...")
        pool.shutdown(wait=False)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        pool.shutdown(wait=False)
        sys.exit(1)


if __name__ == "__main__":
    main()