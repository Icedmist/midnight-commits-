"""
Error Tracking & Exception Handler
Centralized error tracking, logging, and reporting
"""

from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
import json
import traceback
import logging
from enum import Enum
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ErrorTracker:
    """Track and manage errors"""

    def __init__(self):
        """Initialize error tracker"""
        self.errors: Dict[str, list] = {}
        self.stats = {
            'total_errors': 0,
            'errors_by_type': {},
            'errors_by_severity': {}
        }

    def record_error(self, error_type: str, message: str, 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    context: Dict = None) -> None:
        """Record error"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'severity': severity.name,
            'context': context or {},
            'traceback': traceback.format_exc()
        }

        if error_type not in self.errors:
            self.errors[error_type] = []

        self.errors[error_type].append(error_data)
        self.stats['total_errors'] += 1

        # Update stats
        self.stats['errors_by_type'][error_type] = self.stats['errors_by_type'].get(error_type, 0) + 1
        self.stats['errors_by_severity'][severity.name] = self.stats['errors_by_severity'].get(severity.name, 0) + 1

        logger.error(f"❌ [{error_type}] {message}")

    def get_errors(self, error_type: str = None, limit: int = None) -> list:
        """Get recorded errors"""
        if error_type:
            return self.errors.get(error_type, [])[:limit]
        else:
            all_errors = []
            for errors in self.errors.values():
                all_errors.extend(errors)
            return all_errors[:limit]

    def get_stats(self) -> Dict:
        """Get error statistics"""
        return self.stats

    def clear_errors(self, error_type: str = None) -> None:
        """Clear recorded errors"""
        if error_type:
            self.errors[error_type] = []
        else:
            self.errors.clear()
        logger.info("✅ Errors cleared")


class ExceptionHandler:
    """Handle and process exceptions"""

    def __init__(self, error_tracker: ErrorTracker = None):
        """Initialize exception handler"""
        self.error_tracker = error_tracker or ErrorTracker()
        self.handlers: Dict[type, Callable] = {}

    def register_handler(self, exception_type: type, handler: Callable) -> None:
        """Register exception handler"""
        self.handlers[exception_type] = handler
        logger.info(f"✅ Handler registered for {exception_type.__name__}")

    def handle(self, exception: Exception, context: Dict = None) -> None:
        """Handle exception"""
        exc_type = type(exception)

        # Record error
        self.error_tracker.record_error(
            error_type=exc_type.__name__,
            message=str(exception),
            context=context
        )

        # Call specific handler if registered
        if exc_type in self.handlers:
            self.handlers[exc_type](exception, context)

    def handle_with_fallback(self, func: Callable, fallback_value: Any = None) -> Callable:
        """Decorator with fallback"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.handle(e, context={'args': str(args), 'kwargs': str(kwargs)})
                return fallback_value

        return wrapper


class RetryPolicy:
    """Retry policy for failed operations"""

    def __init__(self, max_attempts: int = 3, backoff_seconds: float = 1):
        """Initialize retry policy"""
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute with retry"""
        import time

        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    wait_time = self.backoff_seconds * (2 ** attempt)
                    logger.warning(f"⚠️  Attempt {attempt+1} failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)

        logger.error(f"❌ All {self.max_attempts} attempts failed")
        raise last_exception

    def decorator(self, func: Callable) -> Callable:
        """Decorator for automatic retry"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)

        return wrapper


class CircuitBreaker:
    """Circuit breaker pattern implementation"""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        """Initialize circuit breaker"""
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker"""
        if self.state == 'OPEN':
            # Check if timeout has passed
            if datetime.now() - self.last_failure > timedelta(seconds=self.timeout_seconds):
                self.state = 'HALF_OPEN'
                logger.info("🔄 Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)

            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info("✅ Circuit breaker reset to CLOSED")

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error(f"❌ Circuit breaker opened after {self.failure_count} failures")

            raise

    def decorator(self, func: Callable) -> Callable:
        """Decorator for circuit breaker"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)

        return wrapper


def demo_error_tracking():
    """Demo error tracking"""
    print("\n🚨 Error Tracking & Exception Handling\n")
    
    tracker = ErrorTracker()
    handler = ExceptionHandler(tracker)

    # Register custom handler
    def handle_value_error(exc, context):
        logger.info(f"📞 Custom handler called for ValueError: {exc}")

    handler.register_handler(ValueError, handle_value_error)

    # Simulate errors
    try:
        raise ValueError("Invalid input")
    except Exception as e:
        handler.handle(e, context={"operation": "validation"})

    # Print stats
    stats = tracker.get_stats()
    print(f"\n📊 Error Statistics:")
    print(f"  Total Errors: {stats['total_errors']}")
    print(f"  By Type: {stats['errors_by_type']}")


if __name__ == "__main__":
    print("🚨 Error Tracking & Exception Handler\n")
    
    print("Features:")
    print("✓ Centralized error tracking")
    print("✓ Exception handling")
    print("✓ Context recording")
    print("✓ Retry policies")
    print("✓ Circuit breaker pattern")
    print("✓ Error statistics")
