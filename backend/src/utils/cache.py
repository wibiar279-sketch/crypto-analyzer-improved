"""
Caching utilities using Redis.
"""
import json
import functools
from typing import Any, Callable, Optional
import redis
from flask import current_app


class CacheManager:
    """Redis cache manager"""
    
    def __init__(self, redis_client: redis.Redis = None):
        self.redis_client = redis_client
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            current_app.logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            current_app.logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            current_app.logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., 'ticker:*')
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            current_app.logger.error(f"Cache clear pattern error: {e}")
            return 0


def cached(ttl: int = 300, key_prefix: str = ''):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    
    Example:
        @cached(ttl=60, key_prefix='ticker')
        def get_ticker(pair_id):
            return fetch_from_api(pair_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_parts = [key_prefix or func.__name__]
            cache_key_parts.extend(str(arg) for arg in args)
            cache_key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ':'.join(cache_key_parts)
            
            # Try to get from cache
            from flask import current_app
            cache_manager = current_app.extensions.get('cache_manager')
            
            if cache_manager:
                cached_value = cache_manager.get(cache_key)
                if cached_value is not None:
                    current_app.logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            if cache_manager and result is not None:
                cache_manager.set(cache_key, result, ttl)
                current_app.logger.debug(f"Cache set: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Invalidate cache keys matching pattern.
    
    Args:
        pattern: Key pattern to invalidate
    
    Example:
        invalidate_cache('ticker:btcidr*')
    """
    from flask import current_app
    cache_manager = current_app.extensions.get('cache_manager')
    
    if cache_manager:
        deleted = cache_manager.clear_pattern(pattern)
        current_app.logger.info(f"Invalidated {deleted} cache keys matching: {pattern}")
        return deleted
    return 0
