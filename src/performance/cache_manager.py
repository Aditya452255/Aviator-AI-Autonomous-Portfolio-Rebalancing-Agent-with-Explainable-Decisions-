"""Cache Manager implementing in-memory TTL and LRU caching."""

from typing import Any, Dict, Optional
from cachetools import TTLCache
from src.core.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Enterprise Cache Manager using in-memory TTL cache."""

    def __init__(self, maxsize: int = 1000, ttl_seconds: float = 300.0) -> None:
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl_seconds)

    def get(self, key: str) -> Optional[Any]:
        """Get cached value by key.

        Args:
            key: Cache key.

        Returns:
            Cached value or None.
        """
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Store key-value pair in TTL cache.

        Args:
            key: Cache key.
            value: Value object.
        """
        self.cache[key] = value

    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
