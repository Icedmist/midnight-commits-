"""
Rate Limiter & Throttle Manager
Implement rate limiting, throttling, and quota management
"""

from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, rate: int, per_seconds: int = 60):
        """
        Initialize rate limiter
        
        Args:
            rate: Number of requests allowed
            per_seconds: Time window in seconds
        """
        self.rate = rate
        self.per_seconds = per_seconds
        self.allowance: Dict[str, float] = defaultdict(lambda: rate)
        self.last_check: Dict[str, float] = {}
        self.lock = threading.Lock()

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        with self.lock:
            now = datetime.now().timestamp()
            last = self.last_check.get(identifier, now)
            time_passed = now - last

            # Replenish tokens
            self.allowance[identifier] += time_passed * (self.rate / self.per_seconds)
            self.allowance[identifier] = min(self.rate, self.allowance[identifier])

            self.last_check[identifier] = now

            if self.allowance[identifier] < 1.0:
                logger.warning(f"⚠️  Rate limit exceeded for {identifier}")
                return False

            self.allowance[identifier] -= 1.0
            logger.info(f"✅ Request allowed for {identifier}")
            return True

    def get_status(self, identifier: str) -> Dict:
        """Get rate limit status"""
        with self.lock:
            return {
                'identifier': identifier,
                'allowance': self.allowance.get(identifier, self.rate),
                'limit': self.rate,
                'window': self.per_seconds
            }


class SlidingWindowLimiter:
    """Sliding window rate limiter"""

    def __init__(self, max_requests: int, window_seconds: int = 60):
        """Initialize sliding window limiter"""
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        with self.lock:
            now = datetime.now().timestamp()
            window_start = now - self.window_seconds

            # Remove old requests
            while (self.requests[identifier] and 
                   self.requests[identifier][0] < window_start):
                self.requests[identifier].popleft()

            # Check limit
            if len(self.requests[identifier]) >= self.max_requests:
                logger.warning(f"⚠️  Sliding window limit exceeded for {identifier}")
                return False

            self.requests[identifier].append(now)
            logger.info(f"✅ Request allowed for {identifier}")
            return True

    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests"""
        with self.lock:
            now = datetime.now().timestamp()
            window_start = now - self.window_seconds

            # Count requests in window
            count = sum(1 for t in self.requests[identifier] if t >= window_start)
            return max(0, self.max_requests - count)


class ThrottleManager:
    """Manage request throttling"""

    def __init__(self):
        """Initialize throttle manager"""
        self.limiters: Dict[str, RateLimiter] = {}
        self.lock = threading.Lock()

    def add_limiter(self, name: str, rate: int, per_seconds: int = 60) -> None:
        """Add rate limiter"""
        with self.lock:
            self.limiters[name] = RateLimiter(rate, per_seconds)
            logger.info(f"✅ Limiter added: {name}")

    def check_throttle(self, identifier: str, limiter_name: str) -> bool:
        """Check if request passes throttle"""
        if limiter_name not in self.limiters:
            logger.error(f"❌ Limiter not found: {limiter_name}")
            return False

        return self.limiters[limiter_name].is_allowed(identifier)

    def throttle_decorator(self, limiter_name: str, key_func: Callable = None):
        """Decorator to throttle function calls"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Extract identifier from args/kwargs
                if key_func:
                    identifier = key_func(*args, **kwargs)
                else:
                    identifier = str(args[0]) if args else "default"

                if not self.check_throttle(identifier, limiter_name):
                    raise Exception(f"Rate limit exceeded ({limiter_name})")

                return func(*args, **kwargs)
            return wrapper
        return decorator


class QuotaManager:
    """Manage request quotas"""

    def __init__(self):
        """Initialize quota manager"""
        self.quotas: Dict[str, Dict] = {}
        self.reset_times: Dict[str, datetime] = {}

    def set_quota(self, identifier: str, quota: int, reset_hours: int = 24) -> None:
        """Set quota for identifier"""
        self.quotas[identifier] = {
            'limit': quota,
            'used': 0,
            'reset_hours': reset_hours
        }
        self.reset_times[identifier] = datetime.now() + timedelta(hours=reset_hours)
        logger.info(f"✅ Quota set: {identifier} ({quota})")

    def use_quota(self, identifier: str, amount: int = 1) -> bool:
        """Use quota"""
        if identifier not in self.quotas:
            logger.error(f"❌ No quota for {identifier}")
            return False

        # Check if quota needs reset
        if datetime.now() > self.reset_times[identifier]:
            self.quotas[identifier]['used'] = 0
            reset_hours = self.quotas[identifier]['reset_hours']
            self.reset_times[identifier] = datetime.now() + timedelta(hours=reset_hours)
            logger.info(f"🔄 Quota reset for {identifier}")

        quota = self.quotas[identifier]
        if quota['used'] + amount <= quota['limit']:
            quota['used'] += amount
            logger.info(f"✅ Quota used: {identifier} ({quota['used']}/{quota['limit']})")
            return True
        else:
            logger.warning(f"⚠️  Quota exceeded for {identifier}")
            return False

    def get_quota_status(self, identifier: str) -> Dict:
        """Get quota status"""
        if identifier not in self.quotas:
            return {"error": "No quota"}

        quota = self.quotas[identifier]
        remaining_time = (self.reset_times[identifier] - datetime.now()).total_seconds()

        return {
            'identifier': identifier,
            'used': quota['used'],
            'limit': quota['limit'],
            'remaining': quota['limit'] - quota['used'],
            'reset_seconds': int(remaining_time)
        }


def demo_rate_limiter():
    """Demo rate limiting"""
    print("\n⏱️ Rate Limiting Demo\n")
    
    # Token bucket
    limiter = RateLimiter(rate=10, per_seconds=60)
    
    for i in range(12):
        allowed = limiter.is_allowed("user1")
        print(f"Request {i+1}: {'✅' if allowed else '❌'}")
    
    # Quota manager
    print("\n📊 Quota Manager Demo\n")
    quota_mgr = QuotaManager()
    quota_mgr.set_quota("api_user", 100, reset_hours=24)
    
    for i in range(5):
        quota_mgr.use_quota("api_user", 20)
    
    status = quota_mgr.get_quota_status("api_user")
    print(status)


if __name__ == "__main__":
    print("⏱️ Rate Limiter & Throttle Manager\n")
    print("Features:")
    print("✓ Token bucket rate limiting")
    print("✓ Sliding window rate limiting")
    print("✓ Throttle decorators")
    print("✓ Quota management")
    print("✓ Thread-safe operations")
