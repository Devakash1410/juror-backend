"""
Timing utilities for performance monitoring.
"""
import time
from contextlib import contextmanager
from app.utils.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def timer(name: str = "Operation"):
    """Context manager for timing operations."""
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        logger.info(f"{name} took {elapsed:.2f}s")
