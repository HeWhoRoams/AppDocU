"""
Base Converter Class
Abstract base class for all file converters with common functionality

This module provides the abstract base converter class that defines the interface and
common functionality shared by all file converters in the AppDocU system. It includes
standardized methods for file processing, metadata handling, error management, and
output generation to ensure consistency across all converter implementations.
"""
import os
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json

# get_global_config import removed - not used in this module and causes import crashes


logger = logging.getLogger(__name__)


class BaseConverter(ABC):
    """Abstract base class for all file converters"""
    
    def __init__(self, converter_name: str, output_subdir: str):
        """
        Initialize base converter
        
        Args:
            converter_name: Name of the converter (e.g., 'docx_to_md')
            output_subdir: Subdirectory name for output files
        """
        self.converter_name = converter_name
        self.output_subdir = output_subdir
        self.logger = logging.getLogger(f"{__name__}.{converter_name}")
    
    
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file for idempotency
        
        Args:
            file_path: Path to the file to hash
            
        Returns:
            SHA256 hash as hex string
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def create_output_directory(self, output_dir: Path) -> Path:
        """
        Create converter-specific output directory
        
        Args:
            output_dir: Base output directory
            
        Returns:
            Path to converter-specific output directory
        """
        converter_dir = output_dir / self.output_subdir
        converter_dir.mkdir(exist_ok=True)
        return converter_dir
    
    def add_metadata_header(self, content: str, file_path: Path, 
                           additional_metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add standard metadata header to output content
        
        Args:
            content: Original content to add header to
            file_path: Path to source file
            additional_metadata: Additional metadata to include
            
        Returns:
            Content with metadata header added
        """
        metadata = {
            'source': str(file_path.relative_to(file_path.parent)),
            'converted_at': datetime.now(timezone.utc).isoformat(),
            'converter': self.converter_name
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        header = "---\n"
        for key, value in metadata.items():
            if isinstance(value, str):
                header += f"{key}: {value}\n"
            else:
                header += f"{key}: {json.dumps(value)}\n"
        header += "---\n\n"
        
        return header + content
    
    def write_output_file(self, output_dir: Path, file_path: Path, 
                         content: str, extension: str) -> Path:
        """
        Write content to output file with proper naming
        
        Args:
            output_dir: Directory to write output
            file_path: Original source file path
            content: Content to write
            extension: Output file extension (with dot, e.g., '.md')
            
        Returns:
            Path to written output file
        """
        output_dir = self.create_output_directory(output_dir)
        
        output_filename = file_path.stem + extension
        output_file = output_dir / output_filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file
    
    def log_conversion_result(self, file_path: Path, result: Dict[str, Any]):
        """
        Log conversion result with appropriate level
        
        Args:
            file_path: Source file that was converted
            result: Conversion result dictionary
        """
        if result['status'] == 'success':
            self.logger.info(f"✅ Converted {file_path.name} → {result['output']}")
        elif result['status'] == 'failed':
            self.logger.warning(f"❌ Failed to convert {file_path.name}: {result.get('error', 'Unknown error')}")
        else:
            self.logger.info(f"⏭️ Skipped {file_path.name}")
    
    def handle_conversion_error(self, file_path: Path, error: Exception) -> Dict[str, Any]:
        """
        Handle conversion errors and return standardized error result
        
        Args:
            file_path: Source file that failed to convert
            error: Exception that occurred
            
        Returns:
            Standardized error result dictionary
        """
        self.logger.error(f"Conversion failed for {file_path}: {str(error)}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(error),
            'converter': self.converter_name
        }
    
    def validate_input_file(self, file_path: Path) -> bool:
        """
        Validate that input file exists and is accessible
        
        Args:
            file_path: Path to input file
            
        Returns:
            True if file is valid, False otherwise
        """
        if not file_path.exists():
            self.logger.error(f"Input file does not exist: {file_path}")
            return False
        
        if not file_path.is_file():
            self.logger.error(f"Input path is not a file: {file_path}")
            return False
        
        return True
    
    @abstractmethod
    def convert(self, file_path: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Abstract method for converting a file
        
        Args:
            file_path: Path to the input file
            output_dir: Directory where output should be written
            
        Returns:
            Dictionary with conversion result
        """
        pass
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get basic file information for metadata
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        stat = file_path.stat()
        return {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            'extension': file_path.suffix.lower()
        }


class ConversionResult:
    """Helper class for building standardized conversion results"""
    
    def __init__(self, converter_name: str):
        self.converter_name = converter_name
        self.result = {
            'status': 'success',
            'converter': converter_name,
            'metadata': {}
        }
    
    def set_success(self, output_path: str, metadata: Optional[Dict[str, Any]] = None):
        """Set successful conversion result"""
        self.result['status'] = 'success'
        self.result['output'] = output_path
        if metadata:
            self.result['metadata'].update(metadata)
        return self
    
    def set_failed(self, error: str):
        """Set failed conversion result"""
        self.result['status'] = 'failed'
        self.result['error'] = error
        return self
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to result"""
        self.result['metadata'][key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the final result"""
        return self.result

