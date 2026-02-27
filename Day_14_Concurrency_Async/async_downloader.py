#!/usr/bin/env python3
"""
Async File Downloader
An asynchronous file downloader using aiohttp and asyncio.
Features: Concurrent downloads, progress tracking, error handling, and rate limiting.
"""

import asyncio
import aiohttp
import aiofiles
import os
from typing import List, Dict, Optional
import argparse
import sys
import time
from urllib.parse import urlparse
import logging


class AsyncDownloader:
    """Asynchronous file downloader with progress tracking."""

    def __init__(self, max_concurrent: int = 5, timeout: int = 30):
        """Initialize the downloader."""
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def download_file(self, url: str, output_path: Optional[str] = None,
                          progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """Download a single file asynchronously."""
        async with self.semaphore:
            try:
                async with self.session.get(url) as response:
                    if response.status != 200:
                        return {
                            'url': url,
                            'success': False,
                            'error': f'HTTP {response.status}: {response.reason}'
                        }

                    # Determine output path
                    if not output_path:
                        filename = self._get_filename_from_url(url, response)
                        output_path = filename

                    # Ensure output directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0

                    async with aiofiles.open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            downloaded += len(chunk)

                            if progress_callback and total_size > 0:
                                progress = (downloaded / total_size) * 100
                                progress_callback(url, progress)

                    return {
                        'url': url,
                        'output_path': output_path,
                        'success': True,
                        'size': downloaded,
                        'total_size': total_size
                    }

            except asyncio.TimeoutError:
                return {
                    'url': url,
                    'success': False,
                    'error': 'Timeout'
                }
            except Exception as e:
                return {
                    'url': url,
                    'success': False,
                    'error': str(e)
                }

    def _get_filename_from_url(self, url: str, response) -> str:
        """Extract filename from URL or Content-Disposition header."""
        # Try Content-Disposition header first
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[-1].strip('"\'')

        else:
            # Extract from URL
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)

            # If no filename in path, use domain
            if not filename:
                filename = parsed.netloc.replace('.', '_') + '.html'

        return filename

    async def download_multiple(self, urls: List[str], output_dir: str = '.',
                              progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """Download multiple files concurrently."""
        tasks = []
        for i, url in enumerate(urls):
            output_path = os.path.join(output_dir, f"download_{i+1}_{self._get_filename_from_url(url, None)}")
            task = self.download_file(url, output_path, progress_callback)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'url': urls[i],
                    'success': False,
                    'error': str(result)
                })
            else:
                processed_results.append(result)

        return processed_results


class DownloadManager:
    """High-level download manager with batch processing and reporting."""

    def __init__(self, max_concurrent: int = 5):
        """Initialize download manager."""
        self.max_concurrent = max_concurrent
        self.download_stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'total_size': 0,
            'start_time': None,
            'end_time': None
        }

    def progress_callback(self, url: str, progress: float):
        """Progress callback function."""
        print(f"{url}: {progress:.1f}% complete")

    async def download_batch(self, urls: List[str], output_dir: str = 'downloads',
                           show_progress: bool = True) -> Dict[str, Any]:
        """Download a batch of files with progress reporting."""
        os.makedirs(output_dir, exist_ok=True)

        self.download_stats['total'] = len(urls)
        self.download_stats['start_time'] = time.time()

        callback = self.progress_callback if show_progress else None

        async with AsyncDownloader(self.max_concurrent) as downloader:
            results = await downloader.download_multiple(urls, output_dir, callback)

        self.download_stats['end_time'] = time.time()

        # Process results
        successful = []
        failed = []

        for result in results:
            if result['success']:
                successful.append(result)
                self.download_stats['successful'] += 1
                self.download_stats['total_size'] += result.get('size', 0)
            else:
                failed.append(result)
                self.download_stats['failed'] += 1

        duration = self.download_stats['end_time'] - self.download_stats['start_time']

        return {
            'stats': self.download_stats,
            'duration': duration,
            'successful': successful,
            'failed': failed,
            'results': results
        }

    def print_report(self, results: Dict[str, Any]):
        """Print download report."""
        stats = results['stats']
        duration = results['duration']

        print("\n" + "="*50)
        print("DOWNLOAD REPORT")
        print("="*50)
        print(f"Total URLs: {stats['total']}")
        print(f"Successful: {stats['successful']}")
        print(f"Failed: {stats['failed']}")
        print(".2f")
        print(".2f")
        print(".1f")

        if results['failed']:
            print(f"\nFailed downloads:")
            for fail in results['failed']:
                print(f"  ✗ {fail['url']}: {fail['error']}")


async def download_from_file(file_path: str, output_dir: str = 'downloads',
                           max_concurrent: int = 5, show_progress: bool = True):
    """Download files listed in a text file."""
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        if not urls:
            print("No URLs found in file")
            return

        print(f"Found {len(urls)} URLs to download")

        manager = DownloadManager(max_concurrent)
        results = await manager.download_batch(urls, output_dir, show_progress)
        manager.print_report(results)

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Async File Downloader")
    parser.add_argument("urls", nargs='*', help="URLs to download")
    parser.add_argument("--file", help="File containing URLs (one per line)")
    parser.add_argument("--output-dir", default="downloads", help="Output directory")
    parser.add_argument("--max-concurrent", type=int, default=5, help="Maximum concurrent downloads")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress display")

    args = parser.parse_args()

    if not args.urls and not args.file:
        parser.error("Either provide URLs as arguments or use --file")

    # Configure logging
    logging.basicConfig(level=logging.WARNING)

    try:
        if args.file:
            asyncio.run(download_from_file(args.file, args.output_dir,
                                         args.max_concurrent, not args.no_progress))
        else:
            manager = DownloadManager(args.max_concurrent)
            results = asyncio.run(manager.download_batch(args.urls, args.output_dir, not args.no_progress))
            manager.print_report(results)

    except KeyboardInterrupt:
        print("\nDownload interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()