"""File system traversal for C# files."""

from pathlib import Path
import fnmatch
from typing import List
from orchestrator.logger import setup_logger

logger = setup_logger(__name__)


class FileScanner:
    """Scans repository for C# files matching patterns."""
    
    def __init__(self, config):
        self.config = config
    
    def scan_for_csharp_files(self) -> List[Path]:
        """
        Scan repository for C# files.
        
        Returns:
            List of absolute paths to C# files
        """
        files = []
        repo_path = self.config.repo_path.resolve()
        
        logger.debug(f"Scanning directory: {repo_path}")
        
        for pattern in self.config.include_patterns:
            for file_path in repo_path.rglob(pattern):
                if self._should_include(file_path):
                    files.append(file_path)
                    logger.debug(f"Found: {file_path.relative_to(repo_path)}")
        
        return sorted(files)
    
    def _should_include(self, file_path: Path) -> bool:
        """Check if file should be included based on exclude patterns."""
        try:
            relative_path = str(file_path.relative_to(self.config.repo_path))
        except ValueError:
            # If file is not relative to repo_path, use absolute path for comparison
            relative_path = str(file_path)
        
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(relative_path, pattern):
                logger.debug(f"Excluded: {relative_path} (matched {pattern})")
                return False
        
        return True
