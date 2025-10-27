"""
PDF to Markdown Converter
Converts PDF documents to markdown format preserving text content
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import re
from appdocu_preprocessor.converters.base_converter import BaseConverter, ConversionResult


class PdfToMarkdownConverter(BaseConverter):
    def __init__(self):
        super().__init__("pdf_to_md", "pdf")
    
    def convert(self, file_path: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Convert PDF file to markdown format
        
        Args:
            file_path: Path to the input PDF file
            output_dir: Directory where output should be written
        
        Returns:
            Dictionary with conversion result
        """
        try:
            # Validate input file
            if not self.validate_input_file(file_path):
                return ConversionResult("pdf_to_md").set_failed("Invalid input file").build()
            
            # Extract text from PDF using pdfminer
            laparams = LAParams(
                char_margin=1.0,
                line_margin=0.5,
                word_margin=0.1
            )
            
            text = extract_text(str(file_path), laparams=laparams)
            
            # Clean up the extracted text
            # Remove extra whitespace and normalize line breaks
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line:  # Skip empty lines
                    cleaned_lines.append(line)
            
            # Reconstruct paragraphs by joining lines that appear to be part of the same paragraph
            paragraph_lines = []
            current_paragraph = []
            
            for line in cleaned_lines:
                # If line ends with punctuation, it's likely the end of a paragraph
                if line.endswith(('.', '!', '?', ':')) or len(line) > 100:  # Long lines are likely paragraph ends
                    if current_paragraph:
                        current_paragraph.append(line)
                        paragraph_lines.append(' '.join(current_paragraph))
                        current_paragraph = []
                    else:
                        paragraph_lines.append(line)
                else:
                    # This line continues the previous paragraph
                    current_paragraph.append(line)
            
            # Add any remaining lines
            if current_paragraph:
                paragraph_lines.append(' '.join(current_paragraph))
            
            # Create markdown content
            markdown_content = "\n\n".join(paragraph_lines)
            
            # Add metadata header
            markdown_content = self.add_metadata_header(markdown_content, file_path)
            
            # Write output file
            output_file = self.write_output_file(output_dir, file_path, markdown_content, ".md")
            
            # Get page count from extracted text
            page_count = len([p for p in text.split('\f') if p.strip()]) if text else 0
            
            # Create result with metadata
            result = ConversionResult("pdf_to_md")
            result.set_success(str(output_file.relative_to(output_dir.parent)))
            result.add_metadata('pages', page_count)
            result.add_metadata('characters', len(text))
            result.add_metadata('paragraphs', len(paragraph_lines))
            result.add_metadata('file_info', self.get_file_info(file_path))
            
            conversion_result = result.build()
            self.log_conversion_result(file_path, conversion_result)
            return conversion_result
            
        except Exception as e:
            error_result = self.handle_conversion_error(file_path, e)
            return error_result
    
    def extract_page_count(self, file_path: Path) -> int:
        """
        Helper function to extract page count from PDF
        """
        try:
            text = extract_text(str(file_path))
            # PDF text is often separated by form feed characters
            pages = text.split('\f')
            return len([p for p in pages if p.strip()])
        except Exception:
            return 0


def convert(file_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Wrapper function for backward compatibility"""
    converter = PdfToMarkdownConverter()
    return converter.convert(file_path, output_dir)
