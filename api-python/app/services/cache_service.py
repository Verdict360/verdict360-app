"""
Caching Service for Legal Query Performance Optimization
Implements in-memory and persistent caching for legal responses and vector searches
"""

import hashlib
import json
import time
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
import pickle
import os

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    data: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int
    ttl_seconds: int
    size_bytes: int

class LegalCacheService:
    """
    Multi-level caching service optimized for legal queries
    - Level 1: In-memory cache for frequent queries
    - Level 2: Persistent cache for complex responses
    - Level 3: Vector search result caching
    """
    
    def __init__(self, max_memory_size: int = 100 * 1024 * 1024):  # 100MB default
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.max_memory_size = max_memory_size
        self.current_memory_usage = 0
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_queries': 0
        }
        
        # Cache TTL settings (in seconds)
        self.ttl_settings = {
            'legal_query': 3600,      # 1 hour for legal queries
            'vector_search': 1800,    # 30 minutes for vector searches
            'document_content': 7200, # 2 hours for document content
            'quality_assessment': 900, # 15 minutes for QA results
            'user_session': 3600      # 1 hour for user session data
        }
        
        # Ensure cache directory exists
        self.cache_dir = "./cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    async def get_legal_query(self, query: str, jurisdiction: str = "South Africa") -> Optional[Dict[str, Any]]:
        """Get cached legal query response"""
        cache_key = self._generate_query_key(query, jurisdiction)
        return await self._get_from_cache(cache_key, 'legal_query')

    async def set_legal_query(self, query: str, response_data: Dict[str, Any], jurisdiction: str = "South Africa") -> bool:
        """Cache legal query response"""
        cache_key = self._generate_query_key(query, jurisdiction)
        return await self._set_in_cache(cache_key, response_data, 'legal_query')

    async def get_vector_search(self, query: str, filters: Dict[str, Any] = None) -> Optional[List[Dict[str, Any]]]:
        """Get cached vector search results"""
        cache_key = self._generate_vector_search_key(query, filters)
        return await self._get_from_cache(cache_key, 'vector_search')

    async def set_vector_search(self, query: str, results: List[Dict[str, Any]], filters: Dict[str, Any] = None) -> bool:
        """Cache vector search results"""
        cache_key = self._generate_vector_search_key(query, filters)
        return await self._set_in_cache(cache_key, results, 'vector_search')

    async def get_quality_assessment(self, query: str, response: str) -> Optional[Dict[str, Any]]:
        """Get cached quality assessment"""
        cache_key = self._generate_qa_key(query, response)
        return await self._get_from_cache(cache_key, 'quality_assessment')

    async def set_quality_assessment(self, query: str, response: str, assessment: Dict[str, Any]) -> bool:
        """Cache quality assessment results"""
        cache_key = self._generate_qa_key(query, response)
        return await self._set_in_cache(cache_key, assessment, 'quality_assessment')

    async def _get_from_cache(self, key: str, cache_type: str) -> Optional[Any]:
        """Get item from cache with TTL checking"""
        self.stats['total_queries'] += 1
        
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            
            # Check if expired
            if self._is_expired(entry):
                await self._remove_from_memory(key)
                self.stats['misses'] += 1
                return None
            
            # Update access metadata
            entry.accessed_at = datetime.now()
            entry.access_count += 1
            
            self.stats['hits'] += 1
            logger.debug(f"Cache hit for key: {key[:20]}...")
            return entry.data
        
        # Check persistent cache
        persistent_data = await self._get_from_persistent_cache(key, cache_type)
        if persistent_data:
            # Load back into memory cache
            await self._set_in_memory(key, persistent_data, cache_type)
            self.stats['hits'] += 1
            logger.debug(f"Persistent cache hit for key: {key[:20]}...")
            return persistent_data
        
        self.stats['misses'] += 1
        return None

    async def _set_in_cache(self, key: str, data: Any, cache_type: str) -> bool:
        """Set item in cache with appropriate storage strategy"""
        try:
            # Set in memory cache
            await self._set_in_memory(key, data, cache_type)
            
            # For important queries, also set in persistent cache
            if cache_type in ['legal_query', 'document_content']:
                await self._set_in_persistent_cache(key, data, cache_type)
            
            return True
        except Exception as e:
            logger.error(f"Cache set failed for key {key[:20]}...: {e}")
            return False

    async def _set_in_memory(self, key: str, data: Any, cache_type: str) -> bool:
        """Set item in memory cache with size management"""
        try:
            # Calculate size
            data_size = len(pickle.dumps(data))
            
            # Check if we need to evict items
            while (self.current_memory_usage + data_size > self.max_memory_size and 
                   len(self.memory_cache) > 0):
                await self._evict_lru_item()
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                data=data,
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                access_count=1,
                ttl_seconds=self.ttl_settings.get(cache_type, 3600),
                size_bytes=data_size
            )
            
            # Store in cache
            self.memory_cache[key] = entry
            self.current_memory_usage += data_size
            
            return True
        except Exception as e:
            logger.error(f"Memory cache set failed: {e}")
            return False

    async def _set_in_persistent_cache(self, key: str, data: Any, cache_type: str) -> bool:
        """Set item in persistent cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_type}_{key[:32]}.pkl")
            
            cache_data = {
                'data': data,
                'created_at': datetime.now().isoformat(),
                'cache_type': cache_type,
                'key': key
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
        except Exception as e:
            logger.error(f"Persistent cache set failed: {e}")
            return False

    async def _get_from_persistent_cache(self, key: str, cache_type: str) -> Optional[Any]:
        """Get item from persistent cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_type}_{key[:32]}.pkl")
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Check TTL
            created_at = datetime.fromisoformat(cache_data['created_at'])
            ttl_seconds = self.ttl_settings.get(cache_type, 3600)
            
            if datetime.now() - created_at > timedelta(seconds=ttl_seconds):
                # Expired, remove file
                try:
                    os.remove(cache_file)
                except:
                    pass
                return None
            
            return cache_data['data']
        except Exception as e:
            logger.error(f"Persistent cache get failed: {e}")
            return None

    async def _evict_lru_item(self) -> None:
        """Evict least recently used item from memory cache"""
        if not self.memory_cache:
            return
        
        # Find LRU item
        lru_key = min(self.memory_cache.keys(), 
                     key=lambda k: self.memory_cache[k].accessed_at)
        
        await self._remove_from_memory(lru_key)
        self.stats['evictions'] += 1

    async def _remove_from_memory(self, key: str) -> None:
        """Remove item from memory cache"""
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            self.current_memory_usage -= entry.size_bytes
            del self.memory_cache[key]

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry has expired"""
        age = datetime.now() - entry.created_at
        return age.total_seconds() > entry.ttl_seconds

    def _generate_query_key(self, query: str, jurisdiction: str) -> str:
        """Generate cache key for legal query"""
        content = f"legal_query:{query.lower().strip()}:{jurisdiction}"
        return hashlib.md5(content.encode()).hexdigest()

    def _generate_vector_search_key(self, query: str, filters: Dict[str, Any] = None) -> str:
        """Generate cache key for vector search"""
        filter_str = json.dumps(filters or {}, sort_keys=True)
        content = f"vector_search:{query.lower().strip()}:{filter_str}"
        return hashlib.md5(content.encode()).hexdigest()

    def _generate_qa_key(self, query: str, response: str) -> str:
        """Generate cache key for quality assessment"""
        content = f"qa:{query[:100].lower()}:{response[:100].lower()}"
        return hashlib.md5(content.encode()).hexdigest()

    async def clear_cache(self, cache_type: Optional[str] = None) -> Dict[str, int]:
        """Clear cache entries"""
        cleared_memory = 0
        cleared_persistent = 0
        
        if cache_type:
            # Clear specific cache type
            keys_to_remove = [key for key, entry in self.memory_cache.items() 
                            if key.startswith(cache_type)]
            for key in keys_to_remove:
                await self._remove_from_memory(key)
                cleared_memory += 1
        else:
            # Clear all memory cache
            cleared_memory = len(self.memory_cache)
            self.memory_cache.clear()
            self.current_memory_usage = 0
        
        # Clear persistent cache files
        try:
            for filename in os.listdir(self.cache_dir):
                if not cache_type or filename.startswith(cache_type):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
                    cleared_persistent += 1
        except Exception as e:
            logger.error(f"Error clearing persistent cache: {e}")
        
        return {
            'cleared_memory': cleared_memory,
            'cleared_persistent': cleared_persistent
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        hit_rate = (self.stats['hits'] / max(self.stats['total_queries'], 1)) * 100
        
        return {
            'memory_cache_size': len(self.memory_cache),
            'memory_usage_bytes': self.current_memory_usage,
            'memory_usage_mb': round(self.current_memory_usage / (1024 * 1024), 2),
            'hit_rate_percent': round(hit_rate, 2),
            'total_hits': self.stats['hits'],
            'total_misses': self.stats['misses'],
            'total_evictions': self.stats['evictions'],
            'total_queries': self.stats['total_queries']
        }

    async def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache by removing expired entries and defragmenting"""
        removed_count = 0
        
        # Remove expired entries from memory
        expired_keys = [key for key, entry in self.memory_cache.items() 
                       if self._is_expired(entry)]
        
        for key in expired_keys:
            await self._remove_from_memory(key)
            removed_count += 1
        
        # Clean up persistent cache
        persistent_removed = 0
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(file_path, 'rb') as f:
                        cache_data = pickle.load(f)
                    
                    created_at = datetime.fromisoformat(cache_data['created_at'])
                    cache_type = cache_data.get('cache_type', 'unknown')
                    ttl_seconds = self.ttl_settings.get(cache_type, 3600)
                    
                    if datetime.now() - created_at > timedelta(seconds=ttl_seconds):
                        os.remove(file_path)
                        persistent_removed += 1
                        
                except Exception:
                    # If file is corrupted, remove it
                    os.remove(file_path)
                    persistent_removed += 1
                    
        except Exception as e:
            logger.error(f"Error optimizing persistent cache: {e}")
        
        return {
            'memory_entries_removed': removed_count,
            'persistent_entries_removed': persistent_removed,
            'current_memory_usage_mb': round(self.current_memory_usage / (1024 * 1024), 2)
        }

# Global cache service instance
cache_service = LegalCacheService()