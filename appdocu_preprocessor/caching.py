"""
Caching System for AppDocU Preprocessor
Implements file change detection and caching to avoid unnecessary conversions

This module provides intelligent caching capabilities for the AppDocU preprocessor system,
enabling efficient file processing by detecting changes and avoiding unnecessary conversions.
It tracks file hashes, manages cache expiration, handles dependencies, and provides
comprehensive cache management functionality for optimal performance.
"""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
import logging

# get_global_config import removed - not used in this module and causes import crashes


logger = logging.getLogger(__name__)


class FileCache:
    """Manages caching of file hashes to detect changes and avoid unnecessary conversions"""
    
    def __init__(self, cache_dir: Path):
        """
        Initialize file cache
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "file_hashes.json"
        self._cache: Dict[str, str] = self._load_cache()
    
    def _load_cache(self) -> Dict[str, str]:
        """Load cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load cache file {self.cache_file}: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Could not save cache file {self.cache_file}: {e}")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file
        
        Args:
            file_path: Path to file to hash
            
        Returns:
            SHA256 hash as hex string
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def is_file_changed(self, file_path: Path) -> bool:
        """
        Check if file has changed since last conversion
        
        Args:
            file_path: Path to file to check
            
        Returns:
            True if file has changed or is new, False if unchanged
        """
        current_hash = self.calculate_file_hash(file_path)
        relative_path = str(file_path.relative_to(file_path.parent))
        
        cached_hash = self._cache.get(relative_path)
        
        if cached_hash is None:
            # File not in cache, consider it changed
            logger.debug(f"File {file_path} not in cache, marking as changed")
            return True
        
        if current_hash != cached_hash:
            # File hash changed
            logger.debug(f"File {file_path} hash changed, marking as changed")
            return True
        
        logger.debug(f"File {file_path} unchanged, skipping conversion")
        return False
    
    def mark_file_converted(self, file_path: Path):
        """
        Mark file as successfully converted and update its hash in cache
        
        Args:
            file_path: Path to file that was converted
        """
        current_hash = self.calculate_file_hash(file_path)
        relative_path = str(file_path.relative_to(file_path.parent))
        self._cache[relative_path] = current_hash
        self._save_cache()
        logger.debug(f"Marked file {file_path} as converted with hash {current_hash[:8]}")
    
    def mark_file_failed(self, file_path: Path):
        """
        Mark file as failed conversion (still update hash to avoid retrying immediately)
        
        Args:
            file_path: Path to file that failed conversion
        """
        current_hash = self.calculate_file_hash(file_path)
        relative_path = str(file_path.relative_to(file_path.parent))
        self._cache[relative_path] = current_hash
        self._save_cache()
        logger.debug(f"Marked file {file_path} as failed with hash {current_hash[:8]}")
    
    def clear_cache(self):
        """Clear all cached file hashes"""
        self._cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Cleared file cache")
    
    def get_cached_files(self) -> Set[str]:
        """Get set of all cached file paths"""
        return set(self._cache.keys())


class ConversionCache:
    """Higher-level cache for managing conversion results and dependencies"""
    
    def __init__(self, cache_dir: Path):
        """
        Initialize conversion cache
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self.file_cache = FileCache(cache_dir)
        self.dependency_cache_file = cache_dir / "dependencies.json"
        self._dependencies: Dict[str, list] = self._load_dependencies()
    
    def _load_dependencies(self) -> Dict[str, list]:
        """Load dependency cache from file"""
        if self.dependency_cache_file.exists():
            try:
                with open(self.dependency_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load dependency cache {self.dependency_cache_file}: {e}")
                return {}
        return {}
    
    def _save_dependencies(self):
        """Save dependency cache to file"""
        try:
            with open(self.dependency_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._dependencies, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Could not save dependency cache {self.dependency_cache_file}: {e}")
    
    def should_convert_file(self, file_path: Path) -> bool:
        """
        Determine if file should be converted based on cache status
        
        Args:
            file_path: Path to file to check
            
        Returns:
            True if file should be converted, False if cached/skippable
        """
        return self.file_cache.is_file_changed(file_path)
    
    def mark_file_converted_with_dependencies(self, file_path: Path, dependencies: Optional[list] = None):
        """
        Mark file as converted and record its dependencies
        
        Args:
            file_path: Path to file that was converted
            dependencies: List of file paths this conversion depends on
        """
        self.file_cache.mark_file_converted(file_path)
        
        if dependencies:
            relative_path = str(file_path.relative_to(file_path.parent))
            self._dependencies[relative_path] = dependencies
            self._save_dependencies()
    
    def invalidate_dependents(self, changed_file: Path):
        """
        Invalidate all files that depend on a changed file
        
        Args:
            changed_file: Path to file that changed
        """
        changed_relative = str(changed_file.relative_to(changed_file.parent))
        files_to_invalidate = []
        
        for file_path, deps in self._dependencies.items():
            if changed_relative in deps:
                files_to_invalidate.append(file_path)
        
        for file_path in files_to_invalidate:
            if file_path in self.file_cache._cache:
                del self.file_cache._cache[file_path]
        
        if files_to_invalidate:
            self.file_cache._save_cache()
            logger.info(f"Invalidated {len(files_to_invalidate)} files dependent on {changed_file}")
    
    def clear_all_caches(self):
        """Clear all conversion caches"""
        self.file_cache.clear_cache()
        self._dependencies = {}
        if self.dependency_cache_file.exists():
            self.dependency_cache_file.unlink()
        logger.info("Cleared all conversion caches")


def get_conversion_cache(cache_dir: Optional[Path] = None) -> ConversionCache:
    """
    Get a conversion cache instance
    
    Args:
        cache_dir: Directory for cache files (default: _normalized/cache)
        
    Returns:
        ConversionCache instance
    """
    if cache_dir is None:
        cache_dir = Path("_normalized") / "cache"
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    return ConversionCache(cache_dir)


# Example usage
if __name__ == "__main__":
    # Example of how to use the caching system
    cache = get_conversion_cache()
    
    # Check if a file needs conversion
    test_file = Path("test.docx")
    if cache.should_convert_file(test_file):
        print(f"File {test_file} needs conversion")
        # Perform conversion...
        cache.mark_file_converted_with_dependencies(test_file)
    else:
        print(f"File {test_file} is cached, skipping conversion")
