#!/usr/bin/env python3
"""
Project Integrator - Day 15 Final Project
Integrates multiple concepts from previous days into a unified application.
Combines web scraping, machine learning, security, concurrency, and GUI elements.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import our own modules (simulated for integration)
try:
    from Day_05_Web_Scraping.book_scraper import BookScraper
    from Day_08_Web_Scraping_Advanced.weather_api import WeatherAPI
    from Day_12_Machine_Learning_Basics.data_preprocessing import DataPreprocessor
    from Day_13_Security_Cryptography.password_hasher import PasswordHasher
    from Day_14_Concurrency_Async.async_downloader import AsyncDownloader
except ImportError:
    # Fallback for demonstration
    pass

class ProjectIntegrator:
    """
    Main integration class that combines multiple project components.
    """

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.components = {}

        # Initialize components
        self._init_components()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        default_config = {
            "scraping": {
                "max_pages": 5,
                "delay": 1.0,
                "user_agent": "MidnightCommits/1.0"
            },
            "ml": {
                "model_path": "models/",
                "preprocessing": {
                    "normalize": True,
                    "handle_missing": "mean"
                }
            },
            "security": {
                "hash_algorithm": "argon2",
                "encryption_key": None
            },
            "concurrency": {
                "max_workers": 4,
                "timeout": 30
            },
            "output": {
                "format": "json",
                "directory": "output/"
            }
        }

        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                # Merge configs
                for key, value in user_config.items():
                    if key in default_config:
                        if isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
        else:
            # Save default config
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)

        return default_config

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging."""
        logger = logging.getLogger("ProjectIntegrator")
        logger.setLevel(logging.INFO)

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        # File handler
        log_file = Path("logs/project_integrator.log")
        log_file.parent.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _init_components(self):
        """Initialize all integrated components."""
        try:
            # Security component
            self.components['security'] = PasswordHasher(
                algorithm=self.config['security']['hash_algorithm']
            )
            self.logger.info("Security component initialized")

            # Data preprocessing component
            self.components['preprocessor'] = DataPreprocessor(
                config=self.config['ml']['preprocessing']
            )
            self.logger.info("Data preprocessor initialized")

            # Async downloader component
            self.components['downloader'] = AsyncDownloader(
                max_concurrent=self.config['concurrency']['max_workers']
            )
            self.logger.info("Async downloader initialized")

        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")

    async def run_integrated_workflow(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Run an integrated workflow combining multiple components.

        Args:
            task: Type of task to run
            **kwargs: Task-specific parameters

        Returns:
            Dict containing results
        """
        self.logger.info(f"Starting integrated workflow: {task}")

        start_time = time.time()

        try:
            if task == "data_analysis":
                result = await self._run_data_analysis_workflow(**kwargs)
            elif task == "web_intelligence":
                result = await self._run_web_intelligence_workflow(**kwargs)
            elif task == "security_audit":
                result = await self._run_security_audit_workflow(**kwargs)
            else:
                raise ValueError(f"Unknown task: {task}")

            execution_time = time.time() - start_time
            result['metadata'] = {
                'task': task,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'components_used': list(self.components.keys())
            }

            self.logger.info(f"Workflow completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            raise

    async def _run_data_analysis_workflow(self, data_source: str, **kwargs) -> Dict[str, Any]:
        """Run data analysis workflow combining scraping and ML."""
        self.logger.info("Running data analysis workflow")

        # Step 1: Gather data (simulated)
        raw_data = await self._gather_data_async(data_source)

        # Step 2: Preprocess data
        processed_data = self.components['preprocessor'].preprocess(raw_data)

        # Step 3: Analyze data (simulated ML)
        analysis_results = self._analyze_data(processed_data)

        return {
            'data_source': data_source,
            'raw_records': len(raw_data),
            'processed_records': len(processed_data),
            'analysis': analysis_results,
            'insights': self._generate_insights(analysis_results)
        }

    async def _run_web_intelligence_workflow(self, urls: List[str], **kwargs) -> Dict[str, Any]:
        """Run web intelligence workflow combining scraping and async downloading."""
        self.logger.info("Running web intelligence workflow")

        # Concurrent web scraping
        scrape_tasks = []
        for url in urls:
            task = self.components['downloader'].download_with_processing(url)
            scrape_tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*scrape_tasks, return_exceptions=True)

        # Process results
        successful = []
        failed = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append({'url': urls[i], 'error': str(result)})
            else:
                successful.append(result)

        return {
            'total_urls': len(urls),
            'successful': len(successful),
            'failed': len(failed),
            'data_collected': successful,
            'errors': failed
        }

    async def _run_security_audit_workflow(self, targets: List[str], **kwargs) -> Dict[str, Any]:
        """Run security audit workflow combining security and concurrency."""
        self.logger.info("Running security audit workflow")

        # Hash passwords concurrently
        hash_tasks = []
        for target in targets:
            task = self._hash_secure_async(target)
            hash_tasks.append(task)

        # Execute concurrently
        hashes = await asyncio.gather(*hash_tasks)

        # Security analysis
        security_report = self._analyze_security(hashes)

        return {
            'targets_audited': len(targets),
            'security_score': security_report['score'],
            'recommendations': security_report['recommendations'],
            'hashed_credentials': hashes
        }

    async def _gather_data_async(self, source: str) -> List[Dict]:
        """Simulate async data gathering."""
        # Simulate network delay
        await asyncio.sleep(0.1)

        # Mock data based on source
        if source == "books":
            return [
                {"title": "Python Crash Course", "price": 29.99, "rating": 4.5},
                {"title": "Clean Code", "price": 39.99, "rating": 4.7},
                {"title": "Design Patterns", "price": 49.99, "rating": 4.3}
            ]
        elif source == "weather":
            return [
                {"city": "New York", "temp": 22, "humidity": 65},
                {"city": "London", "temp": 18, "humidity": 70},
                {"city": "Tokyo", "temp": 25, "humidity": 60}
            ]
        else:
            return []

    def _analyze_data(self, data: List[Dict]) -> Dict[str, Any]:
        """Simulate data analysis."""
        if not data:
            return {}

        # Simple statistics
        numeric_fields = {}
        for item in data:
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    if key not in numeric_fields:
                        numeric_fields[key] = []
                    numeric_fields[key].append(value)

        stats = {}
        for field, values in numeric_fields.items():
            stats[field] = {
                'mean': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }

        return stats

    def _generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from analysis."""
        insights = []

        for field, stats in analysis.items():
            if 'mean' in stats:
                insights.append(f"Average {field}: {stats['mean']:.2f}")
                insights.append(f"{field} range: {stats['min']:.2f} - {stats['max']:.2f}")

        return insights

    async def _hash_secure_async(self, text: str) -> str:
        """Async wrapper for password hashing."""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            hashed = await loop.run_in_executor(
                executor,
                self.components['security'].hash_password,
                text
            )
        return hashed

    def _analyze_security(self, hashes: List[str]) -> Dict[str, Any]:
        """Analyze security of hashed passwords."""
        # Simple analysis
        unique_hashes = len(set(hashes))
        total_hashes = len(hashes)

        score = (unique_hashes / total_hashes) * 100 if total_hashes > 0 else 0

        recommendations = []
        if score < 80:
            recommendations.append("Consider using stronger passwords")
        if len(hashes[0]) < 60:  # Rough check for hash length
            recommendations.append("Use more secure hashing algorithms")

        return {
            'score': score,
            'unique_hashes': unique_hashes,
            'recommendations': recommendations
        }

    def export_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Export results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integration_results_{timestamp}.json"

        output_path = Path(self.config['output']['directory']) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        self.logger.info(f"Results exported to {output_path}")
        return str(output_path)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Project Integrator - Combine multiple Python concepts"
    )
    parser.add_argument(
        "task",
        choices=["data_analysis", "web_intelligence", "security_audit"],
        help="Task to execute"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Configuration file path"
    )
    parser.add_argument(
        "--output",
        help="Output filename"
    )

    # Task-specific arguments
    parser.add_argument(
        "--data-source",
        help="Data source for analysis (books, weather)"
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        help="URLs for web intelligence"
    )
    parser.add_argument(
        "--targets",
        nargs="+",
        help="Targets for security audit"
    )

    args = parser.parse_args()

    # Initialize integrator
    integrator = ProjectIntegrator(args.config)

    try:
        # Prepare task parameters
        kwargs = {}
        if args.data_source:
            kwargs['data_source'] = args.data_source
        if args.urls:
            kwargs['urls'] = args.urls
        if args.targets:
            kwargs['targets'] = args.targets

        # Run workflow
        result = asyncio.run(integrator.run_integrated_workflow(args.task, **kwargs))

        # Export results
        output_file = integrator.export_results(result, args.output)

        print(f"✓ Integration completed successfully")
        print(f"Results saved to: {output_file}")
        print(f"Execution time: {result['metadata']['execution_time']:.2f}s")

    except Exception as e:
        print(f"✗ Integration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()