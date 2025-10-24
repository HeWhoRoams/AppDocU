"""
AppDocU Preprocessor & Normalizer
Entrypoint script for converting binary document formats to text/structured representations
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


logger = logging.getLogger(__name__)

class DocumentNormalizer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.normalized_dir = self.root_path / "_normalized"
        self.index_file = self.normalized_dir / "normalize.index.json"
        self.map_file = self.normalized_dir / "normalized-map.json"
        
        # Create normalized directory
        self.normalized_dir.mkdir(exist_ok=True)
        
        # Extension to converter mapping
        self.extension_map: Dict[str, Callable] = {}
        
        # Results tracking
        self.conversion_results = []
        self.conversion_map = {}
        
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
        
    def find_supported_files(self) -> List[Path]:
        """Find all supported files in the repository"""
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
        
        try:
            # Calculate hash for idempotency check
            original_hash = self.calculate_file_hash(file_path)
            
            # Call converter
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
                
                return conversion_entry
            else:
                return {
                    'source': str(file_path.relative_to(self.root_path)),
                    'status': 'failed',
                    'error': result.get('error', 'Unknown error'),
                    'converter': result.get('converter', extension)
                }
                
        except Exception as e:
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
        
        # Find all supported files
        files_to_convert = self.find_supported_files()
        logger.info(f"Found {len(files_to_convert)} supported files to convert")
        
        # Convert each file
        successful = 0
        failed = 0
        warnings = 0
        
        for file_path in files_to_convert:
            logger.info(f"Converting {file_path}")
            result = self.convert_file(file_path)
            self.conversion_results.append(result)
            
            if result['status'] == 'success':
                successful += 1
                logger.info(f"✅ Converted {result['source']} → {result['output']}")
            elif result['status'] == 'failed':
                failed += 1
                logger.warning(f"❌ Failed to convert {result['source']}: {result['error']}")
            else:
                warnings += 1
                
        # Write index and map files
        self.write_index_files()
        
        # Print summary
        logger.info(f"✅ Completed {successful} conversions, {failed} failed, {warnings} warnings")
        
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
    args = parser.parse_args()
    
    normalizer = DocumentNormalizer(args.path)
    
    # Import and register all converters
    from appdocu_preprocessor.converters.docx_to_md import convert as docx_convert
    from appdocu_preprocessor.converters.xlsx_to_csv import convert as xlsx_convert
    from appdocu_preprocessor.converters.pptx_to_md import convert as pptx_convert
    from appdocu_preprocessor.converters.pdf_to_md import convert as pdf_convert
    from appdocu_preprocessor.converters.visio_to_json import convert as visio_convert
    
    normalizer.register_converter('.docx', docx_convert)
    normalizer.register_converter('.xlsx', xlsx_convert)
    normalizer.register_converter('.pptx', pptx_convert)
    normalizer.register_converter('.pdf', pdf_convert)
    normalizer.register_converter('.vsdx', visio_convert)
    
    normalizer.run_normalization()


if __name__ == '__main__':
    main()
