#!/usr/bin/env python3
"""
Concurrent Web Scraper
A concurrent web scraper using asyncio and aiohttp for high-performance scraping.
Features: Concurrent requests, rate limiting, data extraction, and result storage.
"""

import asyncio
import aiohttp
from aiohttp import ClientTimeout
import aiofiles
import json
import csv
import time
from typing import List, Dict, Any, Optional
import argparse
import sys
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging


class ConcurrentScraper:
    """Concurrent web scraper with rate limiting and data extraction."""

    def __init__(self, max_concurrent: int = 10, delay: float = 0.1, timeout: int = 30):
        """Initialize the scraper."""
        self.max_concurrent = max_concurrent
        self.delay = delay  # Delay between requests
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
        self.last_request_time = 0

    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.delay:
            await asyncio.sleep(self.delay - time_since_last)
        self.last_request_time = time.time()

    async def scrape_url(self, url: str, extractors: Dict[str, callable] = None) -> Dict[str, Any]:
        """Scrape a single URL with optional data extraction."""
        async with self.semaphore:
            await self._rate_limit()

            try:
                async with self.session.get(url) as response:
                    if response.status != 200:
                        return {
                            'url': url,
                            'success': False,
                            'error': f'HTTP {response.status}: {response.reason}',
                            'status_code': response.status
                        }

                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'text/html' not in content_type:
                        return {
                            'url': url,
                            'success': False,
                            'error': f'Unsupported content type: {content_type}'
                        }

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Extract data
                    data = {
                        'url': url,
                        'success': True,
                        'status_code': response.status,
                        'title': self._extract_title(soup),
                        'links': self._extract_links(soup, url),
                        'text_content': self._extract_text(soup),
                        'meta_tags': self._extract_meta(soup)
                    }

                    # Apply custom extractors
                    if extractors:
                        for key, extractor_func in extractors.items():
                            try:
                                data[key] = extractor_func(soup, url)
                            except Exception as e:
                                data[key] = f"Extraction error: {str(e)}"

                    return data

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

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else ""

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from the page."""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
        return links

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text

    def _extract_meta(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta tags."""
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content
        return meta_tags

    async def scrape_multiple(self, urls: List[str], extractors: Dict[str, callable] = None,
                           progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently."""
        tasks = []
        for url in urls:
            task = self.scrape_url(url, extractors)
            tasks.append(task)

        # Add progress tracking
        if progress_callback:
            results = []
            for i, task in enumerate(asyncio.as_completed(tasks)):
                result = await task
                results.append(result)
                progress_callback(i + 1, len(urls))
            return results
        else:
            return await asyncio.gather(*tasks, return_exceptions=True)


class DataExtractor:
    """Common data extraction patterns."""

    @staticmethod
    def extract_emails(soup: BeautifulSoup, url: str) -> List[str]:
        """Extract email addresses from page."""
        text = soup.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))  # Remove duplicates

    @staticmethod
    def extract_phone_numbers(soup: BeautifulSoup, url: str) -> List[str]:
        """Extract phone numbers from page."""
        text = soup.get_text()
        # Simple phone pattern (US format)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        return list(set(phones))

    @staticmethod
    def extract_prices(soup: BeautifulSoup, url: str) -> List[str]:
        """Extract prices from page."""
        text = soup.get_text()
        price_pattern = r'\$\d+(?:\.\d{2})?'
        prices = re.findall(price_pattern, text)
        return list(set(prices))

    @staticmethod
    def extract_images(soup: BeautifulSoup, url: str) -> List[str]:
        """Extract image URLs."""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(url, src)
            images.append(absolute_url)
        return images

    @staticmethod
    def extract_headings(soup: BeautifulSoup, url: str) -> Dict[str, List[str]]:
        """Extract headings by level."""
        headings = {}
        for level in range(1, 7):
            tag_name = f'h{level}'
            headings[tag_name] = [h.get_text().strip() for h in soup.find_all(tag_name)]
        return headings


class ScraperManager:
    """High-level scraper manager with result storage."""

    def __init__(self, max_concurrent: int = 10, delay: float = 0.1):
        """Initialize scraper manager."""
        self.scraper = ConcurrentScraper(max_concurrent, delay)
        self.results = []

    def progress_callback(self, completed: int, total: int):
        """Progress callback."""
        percentage = (completed / total) * 100
        print(f"Progress: {completed}/{total} ({percentage:.1f}%)")

    async def scrape_sites(self, urls: List[str], extractors: Dict[str, callable] = None,
                         show_progress: bool = True) -> List[Dict[str, Any]]:
        """Scrape multiple sites."""
        callback = self.progress_callback if show_progress else None

        async with self.scraper as scraper:
            results = await scraper.scrape_multiple(urls, extractors, callback)

        # Process results (handle exceptions)
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result)
                })
            else:
                processed_results.append(result)

        self.results = processed_results
        return processed_results

    def save_results(self, filename: str, format: str = 'json'):
        """Save scraping results to file."""
        if format.lower() == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
        elif format.lower() == 'csv':
            if not self.results:
                return

            # Get all unique keys
            all_keys = set()
            for result in self.results:
                all_keys.update(result.keys())

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(self.results)

    def get_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        if not self.results:
            return {}

        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('success', False))
        failed = total - successful

        # Content statistics
        total_links = sum(len(r.get('links', [])) for r in self.results if r.get('success'))
        total_emails = sum(len(r.get('emails', [])) for r in self.results if r.get('emails'))
        total_phones = sum(len(r.get('phone_numbers', [])) for r in self.results if r.get('phone_numbers'))

        return {
            'total_urls': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total) * 100 if total > 0 else 0,
            'total_links_found': total_links,
            'total_emails_found': total_emails,
            'total_phones_found': total_phones
        }


async def scrape_from_file(file_path: str, output_file: str = None, format: str = 'json',
                         max_concurrent: int = 10, delay: float = 0.1):
    """Scrape URLs from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        if not urls:
            print("No URLs found in file")
            return

        print(f"Found {len(urls)} URLs to scrape")

        # Common extractors
        extractors = {
            'emails': DataExtractor.extract_emails,
            'phone_numbers': DataExtractor.extract_phone_numbers,
            'prices': DataExtractor.extract_prices,
            'images': DataExtractor.extract_images,
            'headings': DataExtractor.extract_headings
        }

        manager = ScraperManager(max_concurrent, delay)
        results = await manager.scrape_sites(urls, extractors)

        # Save results
        if output_file:
            manager.save_results(output_file, format)
            print(f"Results saved to {output_file}")

        # Print statistics
        stats = manager.get_statistics()
        print("\n" + "="*50)
        print("SCRAPING STATISTICS")
        print("="*50)
        print(f"Total URLs: {stats['total_urls']}")
        print(f"Successful: {stats['successful']}")
        print(f"Failed: {stats['failed']}")
        print(".1f")
        print(f"Links found: {stats['total_links_found']}")
        print(f"Emails found: {stats['total_emails_found']}")
        print(f"Phone numbers found: {stats['total_phones_found']}")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Concurrent Web Scraper")
    parser.add_argument("urls", nargs='*', help="URLs to scrape")
    parser.add_argument("--file", help="File containing URLs (one per line)")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--format", choices=['json', 'csv'], default='json', help="Output format")
    parser.add_argument("--max-concurrent", type=int, default=10, help="Maximum concurrent requests")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between requests")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress display")

    args = parser.parse_args()

    if not args.urls and not args.file:
        parser.error("Either provide URLs as arguments or use --file")

    # Configure logging
    logging.basicConfig(level=logging.WARNING)

    try:
        if args.file:
            asyncio.run(scrape_from_file(args.file, args.output, args.format,
                                       args.max_concurrent, args.delay))
        else:
            extractors = {
                'emails': DataExtractor.extract_emails,
                'phone_numbers': DataExtractor.extract_phone_numbers,
                'images': DataExtractor.extract_images
            }

            manager = ScraperManager(args.max_concurrent, args.delay)
            results = asyncio.run(manager.scrape_sites(args.urls, extractors, not args.no_progress))

            if args.output:
                manager.save_results(args.output, args.format)
                print(f"Results saved to {args.output}")

            stats = manager.get_statistics()
            print(f"\nScraped {stats['total_urls']} URLs, {stats['successful']} successful")

    except KeyboardInterrupt:
        print("\nScraping interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()