"""
File Enumerator
Scans repository and classifies files for preprocessing

This module provides file enumeration and classification capabilities for the AppDocU system,
identifying supported file types, calculating file hashes, and creating comprehensive file
manifests for the preprocessing pipeline. It handles various file types and maintains
metadata for tracking and validation purposes.
"""
import os
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json

from appdocu_preprocessor.converters.base_converter import BaseConverter
# get_global_config import removed - not used in this module and causes import crashes

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Enumeration of supported file types"""
    CODE = "code"
    DOCX = "docx"
    EXCEL = "excel"
    VISIO = "visio"
    PDF = "pdf"
    PPTX = "pptx"
    IMAGE = "image"
    TICKET = "ticket"
    OTHER = "other"


@dataclass
class FileInfo:
    """Data class for file information"""
    file: str
    type: str
    handler: str
    size_kb: int
    hash: str
    last_modified: str
    status: str
    error: Optional[str] = None
    output_file: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FileEnumerator:
    """Enumerates and classifies files in a repository for preprocessing"""
    
    def __init__(self, root_path: Path):
        """
        Initialize file enumerator
        
        Args:
            root_path: Root path of repository to scan
        """
        self.root_path = root_path
        self.file_type_mapping = self._get_file_type_mapping()
        self.handler_mapping = self._get_handler_mapping()
        self.skip_directories = {'.git', '__pycache__', 'node_modules', '.vscode', '.idea'}
    
    def _get_file_type_mapping(self) -> Dict[str, FileType]:
        """Get mapping of file extensions to file types"""
        return {
            # Code files
            '.py': FileType.CODE, '.js': FileType.CODE, '.ts': FileType.CODE,
            '.cs': FileType.CODE, '.java': FileType.CODE, '.cpp': FileType.CODE,
            '.h': FileType.CODE, '.sql': FileType.CODE,
            '.yaml': FileType.CODE, '.yml': FileType.CODE, '.xml': FileType.CODE,
            '.html': FileType.CODE, '.css': FileType.CODE, '.txt': FileType.CODE,
            '.md': FileType.CODE, '.rst': FileType.CODE,
            # Document files
            '.docx': FileType.DOCX, '.doc': FileType.DOCX,
            # Excel files
            '.xlsx': FileType.EXCEL, '.xls': FileType.EXCEL, '.csv': FileType.EXCEL,
            # Visio files
            '.vsdx': FileType.VISIO, '.vssx': FileType.VISIO,
            # PDF files
            '.pdf': FileType.PDF,
            # PowerPoint files
            '.pptx': FileType.PPTX, '.ppt': FileType.PPTX,
            # Image files
            '.png': FileType.IMAGE, '.jpg': FileType.IMAGE, '.jpeg': FileType.IMAGE,
            '.svg': FileType.IMAGE,
            # Ticket exports
            '.json': FileType.TICKET,
        }
    
    def _get_handler_mapping(self) -> Dict[FileType, str]:
        """Get mapping of file types to handler names"""
        return {
            FileType.CODE: "CodeHandler",
            FileType.DOCX: "DocxHandler",
            FileType.EXCEL: "ExcelHandler",
            FileType.VISIO: "VisioHandler",
            FileType.PDF: "PdfHandler",
            FileType.PPTX: "PptxHandler",
            FileType.IMAGE: "ImageHandler",
            FileType.TICKET: "TicketHandler",
            FileType.OTHER: "GenericHandler"
        }
    
    def should_skip_directory(self, dir_path: Path) -> bool:
        """
        Check if directory should be skipped during enumeration
        
        Args:
            dir_path: Path to directory to check
            
        Returns:
            True if directory should be skipped, False otherwise
        """
        dir_name = dir_path.name.lower()
        return dir_name in self.skip_directories or dir_name.startswith('.')
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file for idempotency
        
        Args:
            file_path: Path to file to hash
            
        Returns:
            SHA256 hash as hex string (first 6 characters)
        """
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()[:6]
        except Exception as e:
            logger.warning(f"Could not calculate hash for {file_path}: {e}")
            return "000000"
    
    def classify_file(self, file_path: Path) -> FileType:
        """
        Classify file type based on extension
        
        Args:
            file_path: Path to file to classify
            
        Returns:
            Classified file type
        """
        extension = file_path.suffix.lower()
        return self.file_type_mapping.get(extension, FileType.OTHER)
    
    def get_handler_name(self, file_type: FileType) -> str:
        """
        Get handler name for file type
        
        Args:
            file_type: File type to get handler for
            
        Returns:
            Handler name
        """
        return self.handler_mapping.get(file_type, "UnknownHandler")
    
    def create_file_info(self, file_path: Path, status: str = "pending", 
                         error: Optional[str] = None, output_file: Optional[str] = None) -> FileInfo:
        """
        Create file info object for file
        
        Args:
            file_path: Path to file
            status: Processing status
            error: Error message if any
            output_file: Output file path if processed
            
        Returns:
            FileInfo object
        """
        stat = file_path.stat()
        file_type = self.classify_file(file_path)
        
        return FileInfo(
            file=str(file_path.relative_to(self.root_path)),
            type=file_type.value,
            handler=self.get_handler_name(file_type),
            size_kb=stat.st_size // 1024,
            hash=self.calculate_file_hash(file_path),
            last_modified=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            status=status,
            error=error,
            output_file=output_file
        )
    
    def enumerate_files(self) -> List[FileInfo]:
        """
        Enumerate all files in repository and create file manifest
        
        Returns:
            List of FileInfo objects for all files
        """
        file_infos = []
        logger.info(f"Enumerating files in {self.root_path}")
        
        for root, dirs, files in os.walk(self.root_path):
            # Remove directories that should be skipped
            dirs[:] = [d for d in dirs if not self.should_skip_directory(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                try:
                    file_info = self.create_file_info(file_path)
                    file_infos.append(file_info)
                except Exception as e:
                    logger.warning(f"Could not process file {file_path}: {e}")
                    continue
        
        logger.info(f"Found {len(file_infos)} files")
        return file_infos
    
    def write_file_manifest(self, file_infos: List[FileInfo], output_dir: Path) -> Path:
        """
        Write file manifest to JSON file
        
        Args:
            file_infos: List of file info objects
            output_dir: Directory to write manifest to
            
        Returns:
            Path to written manifest file
        """
        meta_dir = output_dir / ".meta"
        meta_dir.mkdir(exist_ok=True)
        
        manifest_file = meta_dir / "file_manifest.json"
        
        # Convert dataclass objects to dictionaries
        manifest_data = [asdict(info) for info in file_infos]
        
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Wrote file manifest to {manifest_file}")
        return manifest_file
    
    def get_files_by_type(self, file_infos: List[FileInfo]) -> Dict[FileType, List[FileInfo]]:
        """
        Group files by type
        
        Args:
            file_infos: List of file info objects
            
        Returns:
            Dictionary mapping file types to lists of file infos
        """
        files_by_type = {file_type: [] for file_type in FileType}
        
        for file_info in file_infos:
            try:
                file_type = FileType(file_info.type)
                files_by_type[file_type].append(file_info)
            except ValueError:
                files_by_type[FileType.OTHER].append(file_info)
        
        return files_by_type


def main():
    """Main function for testing file enumeration"""
    import argparse
    parser = argparse.ArgumentParser(description='Enumerate files in repository')
    parser.add_argument('--path', required=True, help='Root path of repository to scan')
    args = parser.parse_args()
    
    root_path = Path(args.path)
    enumerator = FileEnumerator(root_path)
    
    file_infos = enumerator.enumerate_files()
    manifest_file = enumerator.write_file_manifest(file_infos, root_path)
    
    print(f"File enumeration complete. Manifest written to {manifest_file}")
    print(f"Total files: {len(file_infos)}")
    
    # Show breakdown by type
    files_by_type = enumerator.get_files_by_type(file_infos)
    for file_type, files in files_by_type.items():
        if files:
            print(f"{file_type.value}: {len(files)} files")


if __name__ == '__main__':
    main()
