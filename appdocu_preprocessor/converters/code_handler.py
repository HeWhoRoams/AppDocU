"""
Code Handler
Handles code files by copying them to normalized structure while preserving directory structure
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import shutil
from appdocu_preprocessor.converters.base_converter import BaseConverter, ConversionResult


class CodeHandler(BaseConverter):
    def __init__(self):
        super().__init__("code_handler", "text")
    
    def convert(self, file_path: Path, output_dir: Path, root_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Copy code file to normalized structure while preserving directory structure
        
        Args:
            file_path: Path to the input code file
            output_dir: Directory where output should be written
            root_path: Root path of the repository (for relative path calculation)
        
        Returns:
            Dictionary with conversion result
        """
        try:
            # Validate input file
            if not self.validate_input_file(file_path):
                return ConversionResult("code_handler").set_failed("Invalid input file").build()
            
            # Create output file path that preserves directory structure
            output_file = self.write_output_file_with_structure(output_dir, file_path, root_path)
            
            # Copy the file content
            shutil.copy2(file_path, output_file)
            
            # Read file content for metadata extraction
            with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Count lines and basic metrics
            lines = len(content.splitlines())
            words = len(content.split())
            chars = len(content)
            
            # Create result with metadata
            result = ConversionResult("code_handler")
            result.set_success(str(output_file.relative_to(output_dir.parent)))
            result.add_metadata('lines', lines)
            result.add_metadata('words', words)
            result.add_metadata('characters', chars)
            result.add_metadata('file_info', self.get_file_info(file_path))
            result.add_metadata('extension', file_path.suffix.lower())
            result.add_metadata('language', self._detect_language(file_path.suffix.lower()))
            
            conversion_result = result.build()
            self.log_conversion_result(file_path, conversion_result)
            return conversion_result
            
        except Exception as e:
            error_result = self.handle_conversion_error(file_path, e)
            return error_result
    
    def write_output_file_with_structure(self, output_dir: Path, file_path: Path, root_path: Optional[Path] = None) -> Path:
        """
        Write file to output directory preserving the original directory structure
        
        Args:
            output_dir: Base output directory
            file_path: Original file path
            root_path: Root path of the repository (for relative path calculation)
            
        Returns:
            Path to the output file with preserved structure
        """
        # Create the text subdirectory
        text_dir = output_dir / "text"
        text_dir.mkdir(exist_ok=True)
        
        if root_path:
            # Calculate relative path from the root directory to preserve structure
            try:
                relative_path = file_path.relative_to(root_path)
                output_file = text_dir / relative_path
            except ValueError:
                # If file is not relative to root_path, use just the filename
                output_file = text_dir / file_path.name
        else:
            # If no root_path provided, use just the filename
            output_file = text_dir / file_path.name
        
        # Create parent directories if they don't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        return output_file
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cs': 'csharp',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.sql': 'sql',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.md': 'markdown',
            '.txt': 'text',
            '.rst': 'restructuredtext',
        }
        return language_map.get(extension.lower(), 'unknown')


def convert(file_path: Path, output_dir: Path, root_path: Optional[Path] = None) -> Dict[str, Any]:
    """Wrapper function for backward compatibility"""
    handler = CodeHandler()
    # Use the provided root_path, or fall back to a heuristic if not provided
    actual_root_path = root_path or file_path.parent
    return handler.convert(file_path, output_dir, actual_root_path)
