"""Cache Utilities for Distance Matrix"""
import time
from typing import Optional, Dict, Tuple
from collections import OrderedDict


class DistanceMatrixCache:
    """Simple in-memory LRU cache for distance matrices"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize cache
        
        Args:
            max_size: Maximum number of cached entries
            ttl_seconds: Time to live for each entry
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, Tuple[float, float]] = OrderedDict()  # (value, timestamp)
    
    def _make_key(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> str:
        """Create cache key from coordinates"""
        return f"{origin[0]:.6f},{origin[1]:.6f}|{destination[0]:.6f},{destination[1]:.6f}"
    
    def get(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> Optional[Dict]:
        """
        Get cached distance data
        
        Args:
            origin: (latitude, longitude)
            destination: (latitude, longitude)
            
        Returns:
            Cached distance data or None if expired/missing
        """
        key = self._make_key(origin, destination)
        
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl_seconds:
            del self.cache[key]
            return None
        
        # Move to end (LRU)
        self.cache.move_to_end(key)
        return value
    
    def set(self, origin: Tuple[float, float], destination: Tuple[float, float], value: Dict) -> None:
        """
        Cache distance data
        
        Args:
            origin: (latitude, longitude)
            destination: (latitude, longitude)
            value: Distance data to cache
        """
        key = self._make_key(origin, destination)
        
        # Remove oldest if cache is full
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        self.cache[key] = (value, time.time())
        self.cache.move_to_end(key)
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)


# Global cache instance
_distance_cache: Optional[DistanceMatrixCache] = None


def get_distance_cache(ttl_seconds: int = 3600) -> DistanceMatrixCache:
    """Get or create global distance cache"""
    global _distance_cache
    if _distance_cache is None:
        _distance_cache = DistanceMatrixCache(ttl_seconds=ttl_seconds)
    return _distance_cache
