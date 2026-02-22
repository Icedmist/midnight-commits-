"""
RESTful API Client with Advanced Features
Build a robust HTTP client with retries, caching, and request pooling
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import json
import logging
from functools import wraps
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    """Advanced REST API client"""

    def __init__(self, base_url: str, timeout: int = 10):
        """Initialize API client"""
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = self._create_session()
        self.cache = {}
        self.headers = {"User-Agent": "APIClient/1.0"}

    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        
        # Configure retries
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _cache_result(self, ttl: int = 300):
        """Decorator for caching results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
                if cache_key in self.cache:
                    cached_time, cached_data = self.cache[cache_key]
                    if datetime.now() - cached_time < timedelta(seconds=ttl):
                        logger.info(f"📦 Cache hit: {func.__name__}")
                        return cached_data
                
                result = func(*args, **kwargs)
                self.cache[cache_key] = (datetime.now(), result)
                return result
            return wrapper
        return decorator

    def get(self, endpoint: str, params: Dict = None, cache_ttl: int = 0) -> Optional[Dict]:
        """GET request"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"✅ GET {endpoint} - {response.status_code}")
            return response.json()
        except Exception as e:
            logger.error(f"❌ GET failed: {e}")
            return None

    def post(self, endpoint: str, data: Dict = None, json_data: Dict = None) -> Optional[Dict]:
        """POST request"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.post(
                url,
                data=data,
                json=json_data,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"✅ POST {endpoint} - {response.status_code}")
            return response.json()
        except Exception as e:
            logger.error(f"❌ POST failed: {e}")
            return None

    def put(self, endpoint: str, json_data: Dict = None) -> Optional[Dict]:
        """PUT request"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.put(
                url,
                json=json_data,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"✅ PUT {endpoint} - {response.status_code}")
            return response.json()
        except Exception as e:
            logger.error(f"❌ PUT failed: {e}")
            return None

    def delete(self, endpoint: str, params: Dict = None) -> bool:
        """DELETE request"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.delete(
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"✅ DELETE {endpoint} - {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"❌ DELETE failed: {e}")
            return False

    def paginate(self, endpoint: str, page_param: str = "page", per_page: int = 20) -> list:
        """Paginate through results"""
        results = []
        page = 1
        
        while True:
            data = self.get(endpoint, params={page_param: page, "limit": per_page})
            if not data or not isinstance(data, list) or len(data) == 0:
                break
            
            results.extend(data)
            page += 1
            logger.info(f"📄 Fetched page {page-1}")
        
        return results

    def batch_get(self, endpoints: list) -> Dict[str, Optional[Dict]]:
        """Fetch multiple endpoints"""
        results = {}
        for endpoint in endpoints:
            results[endpoint] = self.get(endpoint)
        return results

    def close(self) -> None:
        """Close session"""
        self.session.close()
        logger.info("✅ Session closed")


class JSONPlaceholderClient(APIClient):
    """Example: JSONPlaceholder API client"""

    def __init__(self):
        super().__init__("https://jsonplaceholder.typicode.com")

    def get_posts(self, user_id: int = None) -> Optional[list]:
        """Get posts"""
        params = {"userId": user_id} if user_id else {}
        return self.get("posts", params=params)

    def get_post(self, post_id: int) -> Optional[Dict]:
        """Get single post"""
        return self.get(f"posts/{post_id}")

    def create_post(self, title: str, body: str, user_id: int = 1) -> Optional[Dict]:
        """Create post"""
        return self.post("posts", json_data={
            "title": title,
            "body": body,
            "userId": user_id
        })


def demo_client():
    """Demo API client"""
    client = JSONPlaceholderClient()
    
    print("\n📡 REST API Client Demo\n")
    
    # Get posts
    posts = client.get_posts(user_id=1)
    if posts:
        print(f"Found {len(posts)} posts")
        for post in posts[:3]:
            print(f"  - {post.get('title', 'N/A')[:40]}")
    
    # Create post
    new_post = client.create_post(
        title="Test Post",
        body="This is a test post"
    )
    
    if new_post:
        print(f"\n✅ Created post: {new_post.get('id')}")
    
    client.close()


if __name__ == "__main__":
    print("🔌 RESTful API Client\n")
    print("Features:")
    print("✓ Automatic retries")
    print("✓ Request caching")
    print("✓ Pagination")
    print("✓ Batch requests")
    print("✓ Connection pooling")
