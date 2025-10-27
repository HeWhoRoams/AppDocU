"""
Image Handler
Handles image files (PNG, JPG, SVG) that may contain diagrams or UI mockups
Converts to markdown with base64 references for downstream processing
"""
import os
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from PIL import Image
import io
from appdocu_preprocessor.converters.base_converter import BaseConverter, ConversionResult


class ImageHandler(BaseConverter):
    def __init__(self):
        super().__init__("image_handler", "docs")
    
    def convert(self, file_path: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Convert image file to markdown format with base64 reference and metadata
        
        Args:
            file_path: Path to the input image file
            output_dir: Directory where output should be written
        
        Returns:
            Dictionary with conversion result
        """
        try:
            # Validate input file
            if not self.validate_input_file(file_path):
                return ConversionResult("image_handler").set_failed("Invalid input file").build()
            
            # Get image info and check if it might contain diagrams
            image_info = self._get_image_info(file_path)
            
            # Create markdown content with image reference and metadata
            markdown_content = self._create_markdown_content(file_path, image_info)
            
            # Add metadata header
            markdown_content = self.add_metadata_header(markdown_content, file_path, {
                'image_info': image_info,
                'contains_diagram': self._likely_contains_diagram(file_path, image_info)
            })
            
            # Write output file
            output_file = self.write_output_file(output_dir, file_path, markdown_content, ".md")
            
            # Create result with metadata
            result = ConversionResult("image_handler")
            result.set_success(str(output_file.relative_to(output_dir.parent)))
            result.add_metadata('image_info', image_info)
            result.add_metadata('contains_diagram', self._likely_contains_diagram(file_path, image_info))
            result.add_metadata('file_info', self.get_file_info(file_path))
            result.add_metadata('extension', file_path.suffix.lower())
            
            conversion_result = result.build()
            self.log_conversion_result(file_path, conversion_result)
            return conversion_result
            
        except Exception as e:
            error_result = self.handle_conversion_error(file_path, e)
            return error_result
    
    def _get_image_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract information from the image file"""
        try:
            with Image.open(file_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'size_bytes': file_path.stat().st_size,
                    'aspect_ratio': round(img.width / img.height, 2) if img.height > 0 else 0
                }
        except Exception:
            # For SVG and other formats that PIL might not handle
            return {
                'width': 'unknown',
                'height': 'unknown',
                'mode': 'unknown',
                'format': file_path.suffix.lower().upper().lstrip('.'),
                'size_bytes': file_path.stat().st_size,
                'aspect_ratio': 'unknown'
            }
    
    def _create_markdown_content(self, file_path: Path, image_info: Dict[str, Any]) -> str:
        """Create markdown content with image reference"""
        # Read and encode image as base64
        with open(file_path, 'rb') as f:
            image_data = f.read()
            base64_encoded = base64.b64encode(image_data).decode('utf-8')
        
        # Create markdown content
        markdown_lines = []
        markdown_lines.append(f"# {file_path.stem}")
        markdown_lines.append("")
        markdown_lines.append(f"**File:** {file_path.name}")
        markdown_lines.append(f"**Dimensions:** {image_info.get('width', 'unknown')} x {image_info.get('height', 'unknown')}")
        markdown_lines.append(f"**Format:** {image_info.get('format', 'unknown')}")
        markdown_lines.append(f"**Size:** {image_info.get('size_bytes', 0)} bytes")
        markdown_lines.append("")
        markdown_lines.append("## Image Content")
        markdown_lines.append("")
        markdown_lines.append(f"![{file_path.stem}](data:image/{file_path.suffix.lower().lstrip('.')};base64,{base64_encoded})")
        markdown_lines.append("")
        markdown_lines.append("## Analysis")
        markdown_lines.append("")
        markdown_lines.append("- **Likely contains diagram:** " + ("Yes" if self._likely_contains_diagram(file_path, image_info) else "No"))
        markdown_lines.append("- **Purpose:** " + self._infer_purpose(file_path, image_info))
        markdown_lines.append("")
        markdown_lines.append("---")
        markdown_lines.append("")
        markdown_lines.append("*This image was processed by AppDocU ImageHandler for downstream analysis.*")
        markdown_lines.append("")
        
        return "\n".join(markdown_lines)
    
    def _likely_contains_diagram(self, file_path: Path, image_info: Dict[str, Any]) -> bool:
        """Determine if the image likely contains a diagram or UI mockup"""
        filename_lower = file_path.stem.lower()
        likely_diagram_keywords = [
            'diagram', 'flow', 'architecture', 'design', 'mockup', 'ui', 'interface',
            'screen', 'wireframe', 'schema', 'model', 'structure', 'layout', 'chart',
            'graph', 'map', 'process', 'workflow', 'sequence', 'class', 'entity'
        ]
        
        # Check filename for diagram-related keywords
        for keyword in likely_diagram_keywords:
            if keyword in filename_lower:
                return True
        
        # Check dimensions - diagrams often have specific aspect ratios
        aspect_ratio = image_info.get('aspect_ratio', 'unknown')
        if isinstance(aspect_ratio, (int, float)):
            # Diagrams often have wider aspect ratios (flowcharts, architecture diagrams)
            if aspect_ratio > 1.0 and aspect_ratio < 3.0:  # Common for diagrams
                return True
        
        return False
    
    def _infer_purpose(self, file_path: Path, image_info: Dict[str, Any]) -> str:
        """Infer the likely purpose of the image"""
        if self._likely_contains_diagram(file_path, image_info):
            return "Diagram or UI mockup for documentation"
        else:
            return "Image asset"


def convert(file_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Wrapper function for backward compatibility"""
    handler = ImageHandler()
    return handler.convert(file_path, output_dir)
