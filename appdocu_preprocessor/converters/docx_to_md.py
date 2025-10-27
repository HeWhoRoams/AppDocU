"""
DOCX to Markdown Converter
Converts Microsoft Word documents to markdown format preserving structure
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import docx
import docx2txt
from appdocu_preprocessor.converters.base_converter import BaseConverter, ConversionResult


class DocxToMarkdownConverter(BaseConverter):
    def __init__(self):
        super().__init__("docx_to_md", "docx")
    
    def convert(self, file_path: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Convert DOCX file to markdown format
        
        Args:
            file_path: Path to the input DOCX file
            output_dir: Directory where output should be written
        
        Returns:
            Dictionary with conversion result
        """
        try:
            # Validate input file
            if not self.validate_input_file(file_path):
                return ConversionResult("docx_to_md").set_failed("Invalid input file").build()
            
            # Read the DOCX file
            doc = docx.Document(str(file_path))
            
            # Build markdown content
            markdown_lines = []
            
            # Process paragraphs and preserve structure
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if not text:
                    continue
                    
                # Determine paragraph style
                style = paragraph.style.name.lower()
                
                if style.startswith('heading'):
                    # Convert heading levels (Heading 1 -> #, Heading 2 -> ##, etc.)
                    import re
                    match = re.search(r'\d+', style)
                    if match:
                        level = int(match.group())
                    else:
                        level = 1
                    level = max(1, min(6, level))  # Limit to h1-h6
                    markdown_lines.append(f"{'#' * level} {text}")
                else:
                    # Handle bullet lists and regular text
                    if paragraph.style.name.lower() in ['list paragraph', 'bullet']:
                        markdown_lines.append(f"- {text}")
                    else:
                        markdown_lines.append(text)
                
                markdown_lines.append("")  # Add blank line after each paragraph
            
            # Process tables if any
            for table in doc.tables:
                if table.rows:
                    markdown_lines.append("### Table")
                    # Add table header
                    header_cells = table.rows[0].cells
                    header_line = "| " + " | ".join([cell.text.strip() for cell in header_cells]) + " |"
                    separator_line = "| " + " | ".join(["---"] * len(header_cells)) + " |"
                    markdown_lines.extend([header_line, separator_line])
                    
                    # Add table rows
                    for row in table.rows[1:]:
                        row_line = "| " + " | ".join([cell.text.strip() for cell in row.cells]) + " |"
                        markdown_lines.append(row_line)
                    
                    markdown_lines.append("")  # Blank line after table
            
            # Join all lines
            markdown_content = "\n".join(markdown_lines).strip()
            
            # Add metadata header
            markdown_content = self.add_metadata_header(markdown_content, file_path)
            
            # Write output file
            output_file = self.write_output_file(output_dir, file_path, markdown_content, ".md")
            
            # Create result with metadata
            result = ConversionResult("docx_to_md")
            result.set_success(str(output_file.relative_to(output_dir.parent)))
            result.add_metadata('sections', len(doc.sections))
            result.add_metadata('paragraphs', len(doc.paragraphs))
            result.add_metadata('tables', len(doc.tables))
            result.add_metadata('file_info', self.get_file_info(file_path))
            
            conversion_result = result.build()
            self.log_conversion_result(file_path, conversion_result)
            return conversion_result
            
        except Exception as e:
            error_result = self.handle_conversion_error(file_path, e)
            return error_result


def convert(file_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Wrapper function for backward compatibility"""
    converter = DocxToMarkdownConverter()
    return converter.convert(file_path, output_dir)


# Alternative implementation using docx2txt for simpler text extraction
def convert_simple(file_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Simple DOCX to text conversion using docx2txt
    """
    try:
        from appdocu_preprocessor.converters.base_converter import BaseConverter, ConversionResult
        
        # Create converter instance for common functionality
        converter = BaseConverter("docx_to_md", "docx")
        
        # Validate input file
        if not converter.validate_input_file(file_path):
            return ConversionResult("docx_to_md").set_failed("Invalid input file").build()
        
        # Extract text using docx2txt
        text = docx2txt.process(str(file_path))
        
        # Create markdown content
        markdown_content = text
        
        # Add metadata header
        markdown_content = converter.add_metadata_header(markdown_content, file_path)
        
        # Write output file
        output_file = converter.write_output_file(output_dir, file_path, markdown_content, ".md")
        
        # Count paragraphs roughly
        paragraphs = len([p for p in text.split('\n') if p.strip()])
        
        # Create result with metadata
        result = ConversionResult("docx_to_md")
        result.set_success(str(output_file.relative_to(output_dir.parent)))
        result.add_metadata('paragraphs', paragraphs)
        result.add_metadata('file_info', converter.get_file_info(file_path))
        
        conversion_result = result.build()
        converter.log_conversion_result(file_path, conversion_result)
        return conversion_result
        
    except Exception as e:
        from appdocu_preprocessor.converters.base_converter import BaseConverter
        converter = BaseConverter("docx_to_md", "docx")
        return converter.handle_conversion_error(file_path, e)
