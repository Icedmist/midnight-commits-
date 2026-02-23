"""
Advanced Logging Framework
Structured logging with multiple handlers and formatters
"""

import logging
import logging.handlers
from typing import Dict, Optional
from datetime import datetime
import json
from pathlib import Path
import sys

# Custom formatters
class JSONFormatter(logging.Formatter):
    """JSON log formatter"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m'    # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """Format with colors"""
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')

        record.levelname = f"{color}{levelname}{self.RESET}"
        return super().format(record)


class StructuredLogger:
    """Structured logging system"""

    def __init__(self, name: str = "App"):
        """Initialize logger"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.handlers: Dict[str, logging.Handler] = {}

    def add_console_handler(self, level=logging.INFO, colored=True) -> None:
        """Add console handler"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        if colored:
            formatter = ColoredFormatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.handlers['console'] = handler

    def add_file_handler(self, filename: str, level=logging.DEBUG, json_format=False) -> None:
        """Add file handler"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        handler = logging.handlers.RotatingFileHandler(
            filename,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        handler.setLevel(level)

        if json_format:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.handlers['file'] = handler

    def debug(self, msg: str, **kwargs) -> None:
        """Log debug message"""
        self.logger.debug(msg, extra=kwargs)

    def info(self, msg: str, **kwargs) -> None:
        """Log info message"""
        self.logger.info(msg, extra=kwargs)

    def warning(self, msg: str, **kwargs) -> None:
        """Log warning message"""
        self.logger.warning(msg, extra=kwargs)

    def error(self, msg: str, **kwargs) -> None:
        """Log error message"""
        self.logger.error(msg, extra=kwargs)

    def critical(self, msg: str, **kwargs) -> None:
        """Log critical message"""
        self.logger.critical(msg, extra=kwargs)

    def exception(self, msg: str) -> None:
        """Log exception"""
        self.logger.exception(msg)

    def set_level(self, level: int) -> None:
        """Set logger level"""
        self.logger.setLevel(level)


class ContextFilter(logging.Filter):
    """Add context to logs"""

    def __init__(self, user_id: str = None, session_id: str = None):
        """Initialize filter"""
        super().__init__()
        self.user_id = user_id
        self.session_id = session_id

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to record"""
        record.user_id = self.user_id or "anonymous"
        record.session_id = self.session_id or "unknown"
        return True


class PerformanceLogger:
    """Log performance metrics"""

    def __init__(self, logger: StructuredLogger):
        """Initialize performance logger"""
        self.logger = logger
        self.metrics: Dict[str, list] = {}

    def log_duration(self, operation: str, duration: float) -> None:
        """Log operation duration"""
        if operation not in self.metrics:
            self.metrics[operation] = []

        self.metrics[operation].append(duration)
        self.logger.info(f"⏱️  {operation}: {duration:.4f}s")

    def get_stats(self, operation: str) -> Dict:
        """Get operation statistics"""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}

        times = self.metrics[operation]
        return {
            'operation': operation,
            'count': len(times),
            'min': min(times),
            'max': max(times),
            'avg': sum(times) / len(times),
            'total': sum(times)
        }


def demo_logger():
    """Demo logging framework"""
    
    # Create logger
    logger = StructuredLogger("DemoApp")
    logger.add_console_handler(colored=True)
    logger.add_file_handler("logs/app.log")
    logger.add_file_handler("logs/app.json", json_format=True)

    # Log messages
    logger.debug("This is a debug message")
    logger.info("Application started")
    logger.warning("This is a warning")
    logger.error("An error occurred")

    # Performance logging
    perf_logger = PerformanceLogger(logger)
    perf_logger.log_duration("database_query", 0.234)
    perf_logger.log_duration("api_call", 0.567)
    perf_logger.log_duration("database_query", 0.189)

    stats = perf_logger.get_stats("database_query")
    logger.info(f"DB Stats: {stats}")


if __name__ == "__main__":
    print("📝 Advanced Logging Framework\n")
    
    print("Features:")
    print("✓ Multiple log levels")
    print("✓ Console & file handlers")
    print("✓ JSON formatting")
    print("✓ Colored output")
    print("✓ Log rotation")
    print("✓ Context filters")
    print("✓ Performance metrics")
