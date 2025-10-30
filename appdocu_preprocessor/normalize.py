"""
AppDocU Preprocessor & Normalizer
Entrypoint script for converting binary document formats to text/structured representations

This module provides the main normalization functionality for the AppDocU system,
handling file enumeration, classification, conversion, and output generation. It
manages the complete document preprocessing pipeline with caching, error handling,
and comprehensive reporting capabilities.
"""
import os
import sys
import json
import hashlib
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable
import fnmatch
from dataclasses import dataclass
from enum import Enum

from appdocu_preprocessor.config import get_global_config


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
class FileManifestEntry:
    """Data class for file manifest entries"""
    file: str
    type: str
    handler: str
    size_kb: int
    hash: str
    last_modified: str
    status: str
    error: Optional[str] = None
    output_file: Optional[str] = None


class DocumentNormalizer:
    def __init__(self, root_path: str, use_cache: bool = True, create_manifest: bool = True):
        self.root_path = Path(root_path)
        self.normalized_dir = self.root_path / "_normalized"
        self.meta_dir = self.root_path / ".meta"
        self.index_file = self.normalized_dir / "normalize.index.json"
        self.map_file = self.normalized_dir / "normalized-map.json"
        self.file_manifest_file = self.meta_dir / "file_manifest.json"
        self.conversion_report_file = self.meta_dir / "conversion_report.json"
        self.handlers_file = self.meta_dir / "handlers.json"
        self.preprocess_log_file = self.meta_dir / "preprocess.log"
        self.use_cache = use_cache
        self.create_manifest = create_manifest
        
        # Create directories
        self.normalized_dir.mkdir(exist_ok=True)
        self.meta_dir.mkdir(exist_ok=True)
        
        # Extension to converter mapping and type classification
        self.extension_map: Dict[str, Callable] = {}
        self.extension_to_type: Dict[str, FileType] = {
            # Code files (stored as-is in text/)
            '.py': FileType.CODE, '.js': FileType.CODE, '.ts': FileType.CODE,
            '.cs': FileType.CODE, '.java': FileType.CODE, '.cpp': FileType.CODE,
            '.h': FileType.CODE, '.sql': FileType.CODE,
            '.yaml': FileType.CODE, '.yml': FileType.CODE, '.xml': FileType.CODE,
            '.html': FileType.CODE, '.css': FileType.CODE, '.txt': FileType.CODE,
            '.md': FileType.CODE, '.rst': FileType.CODE,
            # Document files (converted to .md in docs/)
            '.docx': FileType.DOCX, '.doc': FileType.DOCX,
            # Excel files (converted to .csv in data/)
            '.xlsx': FileType.EXCEL, '.xls': FileType.EXCEL,
            # Visio files (converted to .mmd/.puml in diagrams/)
            '.vsdx': FileType.VISIO, '.vssx': FileType.VISIO,
            # PDF files (extracted to .md in docs/)
            '.pdf': FileType.PDF,
            # PowerPoint files (converted to .md in docs/)
            '.pptx': FileType.PPTX, '.ppt': FileType.PPTX,
            # Image files (processed for diagrams)
            '.png': FileType.IMAGE, '.jpg': FileType.IMAGE, '.jpeg': FileType.IMAGE,
            '.svg': FileType.IMAGE,
            # Other files
            '.other': FileType.OTHER,
        }
        
        # Results tracking
        self.conversion_results = []
        self.conversion_map = {}
        self.file_manifest = []
        self.handler_versions = {}
        self.failed_files = []
        self.skipped_files = []
        self.successful_files = []
        
        # Initialize caching if enabled
        if self.use_cache:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from caching import get_conversion_cache
            self.cache = get_conversion_cache(self.normalized_dir / "cache")
        else:
            self.cache = None
        
    def register_converter(self, extension: str, converter_func: Callable):
        """Register a converter function for a specific file extension"""
        self.extension_map[extension.lower()] = converter_func
        
    def calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file for idempotency"""
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
        
    def should_skip_directory(self, dir_path: Path) -> bool:
        """Check if directory should be skipped"""
        dir_name = dir_path.name.lower()
        if dir_name.startswith('.'):
            return True
        skip_dirs = {'documentation', 'node_modules', '_normalized'}
        return dir_name in skip_dirs
        
    def classify_file_type(self, file_path: Path) -> FileType:
        """Classify file type using extension and path/name heuristics for .json/.csv"""
        extension = file_path.suffix.lower()
        path_parts = [p.lower() for p in file_path.parts]
        stem = file_path.stem.lower()
        parent_name = file_path.parent.name.lower() if file_path.parent else ""

        # Heuristic for .json and .csv
        if extension in {'.json', '.csv'}:
            # Check if in a tickets directory or name contains 'ticket'
            if any('ticket' in part for part in path_parts) or 'ticket' in stem or 'ticket' in parent_name:
                return FileType.TICKET
            if extension == '.csv':
                return FileType.EXCEL
            if extension == '.json':
                return FileType.OTHER
        # Fallback for other extensions
        return self.extension_to_type.get(extension, FileType.OTHER)
    
    def get_handler_name(self, file_path: Path) -> str:
        """Get appropriate handler name for file type"""
        file_type = self.classify_file_type(file_path)
        handler_map = {
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
        return handler_map.get(file_type, "UnknownHandler")
    
    def create_file_manifest_entry(self, file_path: Path, status: str = "pending", 
                                 error: Optional[str] = None, output_file: Optional[str] = None) -> FileManifestEntry:
        """Create a file manifest entry for the given file"""
        stat = file_path.stat()
        return FileManifestEntry(
            file=str(file_path.relative_to(self.root_path)),
            type=self.classify_file_type(file_path).value,
            handler=self.get_handler_name(file_path),
            size_kb=stat.st_size // 1024,  # Convert to KB
            hash=self.calculate_file_hash(file_path)[:6],  # Short hash for manifest
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            status=status,
            error=error,
            output_file=output_file
        )
    
    def find_all_files(self) -> List[Path]:
        """Find all files in the repository (not just supported ones for manifest)"""
        found_files = []
        supported_extensions = set(self.extension_map.keys())
        all_extensions = set(self.extension_to_type.keys())
        relevant_extensions = supported_extensions.union(all_extensions)
        
        for root, dirs, files in os.walk(self.root_path):
            # Remove directories that should be skipped
            dirs[:] = [d for d in dirs if not self.should_skip_directory(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in relevant_extensions:
                    found_files.append(file_path)
                    
        return found_files
    
    def find_supported_files(self) -> List[Path]:
        """Find all supported files in the repository (those with registered converters)"""
        supported_extensions = set(self.extension_map.keys())
        found_files = []
        
        for root, dirs, files in os.walk(self.root_path):
            # Remove directories that should be skipped
            dirs[:] = [d for d in dirs if not self.should_skip_directory(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in supported_extensions:
                    found_files.append(file_path)
                    
        return found_files
    
    def convert_file(self, file_path: Path) -> Dict:
        """Convert a single file using appropriate converter"""
        extension = file_path.suffix.lower()
        converter = self.extension_map.get(extension)
        
        if not converter:
            return {
                'source': str(file_path.relative_to(self.root_path)),
                'status': 'skipped',
                'error': f'No converter registered for {extension}'
            }
        
        # Check cache if enabled
        if self.use_cache and not self.cache.should_convert_file(file_path):
            logger.info(f"⏭️ Skipping {file_path.name} (cached)")
            return {
                'source': str(file_path.relative_to(self.root_path)),
                'status': 'skipped',
                'reason': 'file unchanged'
            }
        
        try:
            # Calculate hash for idempotency check
            original_hash = self.calculate_file_hash(file_path)
            
            # Determine the appropriate handler based on file type classification
            file_type = self.classify_file_type(file_path)
            
            if file_type == FileType.CODE:
                # Import the CodeHandler to call it directly with root_path
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from converters.code_handler import CodeHandler
                handler = CodeHandler()
                result = handler.convert(file_path, self.normalized_dir, self.root_path)
            elif file_type == FileType.TICKET:
                # Use the registered ticket converter for JSON/CSV ticket exports
                result = converter(file_path, self.normalized_dir)
            else:
                # Use the registered converter for other file types
                result = converter(file_path, self.normalized_dir)
            
            if result['status'] == 'success':
                # Store conversion result
                conversion_entry = {
                    'source': str(file_path.relative_to(self.root_path)),
                    'output': result['output'],
                    'converter': result.get('converter', extension),
                    'status': 'success',
                    'hash': original_hash,
                    **result.get('metadata', {})
                }
                
                # Add to conversion map
                filename = file_path.name
                self.conversion_map[filename] = result['output']
                
                # Mark file as converted in cache if enabled
                if self.use_cache:
                    self.cache.mark_file_converted_with_dependencies(file_path)
                
                return conversion_entry
            else:
                # Mark file as failed in cache if enabled
                if self.use_cache:
                    self.cache.mark_file_failed(file_path)
                
                return {
                    'source': str(file_path.relative_to(self.root_path)),
                    'status': 'failed',
                    'error': result.get('error', 'Unknown error'),
                    'converter': result.get('converter', extension)
                }
                
        except Exception as e:
            # Mark file as failed in cache if enabled
            if self.use_cache:
                self.cache.mark_file_failed(file_path)
            
            logger.error(f"Failed to convert {file_path}: {str(e)}", exc_info=True)
            return {
                'source': str(file_path.relative_to(self.root_path)),
                'status': 'failed',
                'error': str(e),
                'converter': extension
            }
    
    def run_normalization(self):
        """Run the complete normalization process"""
        logger.info(f"Starting normalization for {self.root_path}")
        if self.use_cache:
            logger.info("Caching enabled - will skip unchanged files")
        else:
            logger.info("Caching disabled - will convert all files")
        
        # Create file manifest first (before processing)
        self.create_file_manifest()
        logger.info(f"✅ Created file manifest with {len(self.file_manifest)} entries")
        
        # Find all supported files
        files_to_convert = self.find_supported_files()
        logger.info(f"Found {len(files_to_convert)} supported files to convert")
        
        # Convert each file
        successful = 0
        failed = 0
        skipped = 0
        
        for file_path in files_to_convert:
            logger.info(f"Processing {file_path}")
            result = self.convert_file(file_path)
            self.conversion_results.append(result)
            
            # Update manifest with conversion results
            self.update_manifest_entry(file_path, result)
            
            if result['status'] == 'success':
                successful += 1
                logger.info(f"✅ Converted {result['source']} → {result['output']}")
                self.successful_files.append(file_path)
            elif result['status'] == 'failed':
                failed += 1
                logger.warning(f"❌ Failed to convert {result['source']}: {result['error']}")
                self.failed_files.append(file_path)
            else:
                skipped += 1
                logger.info(f"⏭️ Skipped {result['source']} ({result.get('reason', 'cached')})")
                self.skipped_files.append(file_path)
                
        # Write all required output files
        self.write_index_files()
        self.write_file_manifest()
        self.write_conversion_report()
        self.write_handler_versions()
        self.write_preprocess_log()
        
        # Print summary
        logger.info(f"✅ Completed {successful} conversions, {failed} failed, {skipped} skipped")
        logger.info(f"📊 Conversion coverage: {self.get_conversion_coverage():.1f}%")
        
        
    def create_file_manifest(self):
        """Create the initial file manifest with all relevant files"""
        all_files = self.find_all_files()
        self.file_manifest = []
        
        for file_path in all_files:
            entry = self.create_file_manifest_entry(file_path)
            self.file_manifest.append(entry)
    
    
    def update_manifest_entry(self, file_path: Path, result: Dict):
        """Update manifest entry with conversion results"""
        relative_path = str(file_path.relative_to(self.root_path))
        
        for entry in self.file_manifest:
            if entry.file == relative_path:
                entry.status = result['status']
                if result['status'] == 'failed':
                    entry.error = result.get('error')
                elif result['status'] == 'success':
                    entry.output_file = result.get('output')
                break
    
    
    def get_conversion_coverage(self) -> float:
        """Calculate conversion coverage percentage"""
        total_files = len(self.file_manifest)
        if total_files == 0:
            return 100.0
        successful_conversions = len(self.successful_files)
        return (successful_conversions / total_files) * 100.0
    
    
    def write_file_manifest(self):
        """Write the file manifest to JSON file"""
        manifest_data = []
        for entry in self.file_manifest:
            manifest_data.append({
                'file': entry.file,
                'type': entry.type,
                'handler': entry.handler,
                'size_kb': entry.size_kb,
                'hash': entry.hash,
                'last_modified': entry.last_modified,
                'status': entry.status,
                'error': entry.error,
                'output_file': entry.output_file
            })
        
        with open(self.file_manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ File manifest written: {self.file_manifest_file}")
    
    
    def write_conversion_report(self):
        """Write the conversion report with statistics"""
        total_files = len(self.file_manifest)
        successful = len(self.successful_files)
        failed = len(self.failed_files)
        skipped = len(self.skipped_files)
        coverage = self.get_conversion_coverage()
        
        report_data = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'total_files': total_files,
            'successful_conversions': successful,
            'failed_conversions': failed,
            'skipped_files': skipped,
            'conversion_coverage_percent': coverage,
            'status': 'complete' if failed == 0 else 'partial_with_errors',
            'errors': [{
                'file': str(f.relative_to(self.root_path)),
                'error': self.get_file_error(f)
            } for f in self.failed_files],
            'warnings': [] if coverage >= 95.0 else [f'Conversion coverage below 95%: {coverage:.1f}%']
        }
        
        with open(self.conversion_report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Conversion report written: {self.conversion_report_file}")
    
    
    def get_file_error(self, file_path: Path) -> str:
        """Get error message for a failed file"""
        for result in self.conversion_results:
            if result['source'] == str(file_path.relative_to(self.root_path)):
                return result.get('error', 'Unknown error')
        return 'Error not found in results'
    
    
    def write_handler_versions(self):
        """Write registered handler versions"""
        # For now, just store the basic handler mapping
        handler_data = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'handlers': {ext: handler.__name__ if hasattr(handler, '__name__') else str(handler) 
                        for ext, handler in self.extension_map.items()},
            'file_type_mapping': {ext: file_type.value for ext, file_type in self.extension_to_type.items()}
        }
        
        with open(self.handlers_file, 'w', encoding='utf-8') as f:
            json.dump(handler_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Handler versions written: {self.handlers_file}")
    
    
    def write_preprocess_log(self):
        """Write preprocessing execution log"""
        log_data = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'root_path': str(self.root_path),
            'normalized_dir': str(self.normalized_dir),
            'use_cache': self.use_cache,
            'total_files_processed': len(self.conversion_results),
            'successful_conversions': len(self.successful_files),
            'failed_conversions': len(self.failed_files),
            'skipped_files': len(self.skipped_files),
            'conversion_coverage': self.get_conversion_coverage(),
            'files_converted': [str(f.relative_to(self.root_path)) for f in self.successful_files],
            'files_failed': [str(f.relative_to(self.root_path)) for f in self.failed_files],
            'files_skipped': [str(f.relative_to(self.root_path)) for f in self.skipped_files]
        }
        
        with open(self.preprocess_log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Preprocess log written: {self.preprocess_log_file}")
    
    
    def write_index_files(self):
        """Write the index and map files"""
        # Write normalize.index.json
        index_data = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'documents': self.conversion_results
        }
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
            
        # Write normalized-map.json
        with open(self.map_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversion_map, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Index files written: {self.index_file}, {self.map_file}")


def main():
    parser = argparse.ArgumentParser(description='AppDocU Preprocessor & Normalizer')
    parser.add_argument('--path', required=True, help='Root path of repository to normalize')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching (convert all files)')
    args = parser.parse_args()
    
    normalizer = DocumentNormalizer(args.path, use_cache=not args.no_cache)
    
    # Import and register all converters (using the new class-based converters)
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from converters.docx_to_md import convert as docx_convert
    from converters.xlsx_to_csv import convert as xlsx_convert
    from converters.pptx_to_md import convert as pptx_convert
    from converters.pdf_to_md import convert as pdf_convert
    from converters.visio_to_json import convert as visio_convert
    from converters.code_handler import convert as code_convert
    from converters.sql_converter import convert as sql_convert
    from converters.ticket_handler import convert as ticket_convert
    from converters.image_handler import convert as image_convert
    
    # Register all converters
    normalizer.register_converter('.docx', docx_convert)
    normalizer.register_converter('.xlsx', xlsx_convert)
    normalizer.register_converter('.pptx', pptx_convert)
    normalizer.register_converter('.pdf', pdf_convert)
    normalizer.register_converter('.vsdx', visio_convert)
    # Code file converters
    normalizer.register_converter('.py', code_convert)
    normalizer.register_converter('.js', code_convert)
    normalizer.register_converter('.ts', code_convert)
    normalizer.register_converter('.cs', code_convert)
    normalizer.register_converter('.java', code_convert)
    normalizer.register_converter('.cpp', code_convert)
    normalizer.register_converter('.h', code_convert)
    normalizer.register_converter('.sql', sql_convert)
    # Register ticket handler for JSON files (ticket exports)
    normalizer.register_converter('.json', ticket_convert)
    normalizer.register_converter('.yaml', code_convert)
    normalizer.register_converter('.yml', code_convert)
    normalizer.register_converter('.xml', code_convert)
    normalizer.register_converter('.html', code_convert)
    normalizer.register_converter('.css', code_convert)
    normalizer.register_converter('.txt', code_convert)
    normalizer.register_converter('.md', code_convert)
    normalizer.register_converter('.rst', code_convert)
    # CSV files can be both data exports and ticket exports
    normalizer.register_converter('.csv', ticket_convert)
    # Image files
    normalizer.register_converter('.png', image_convert)
    normalizer.register_converter('.jpg', image_convert)
    normalizer.register_converter('.jpeg', image_convert)
    normalizer.register_converter('.svg', image_convert)
    
    normalizer.run_normalization()


if __name__ == '__main__':
    main()
