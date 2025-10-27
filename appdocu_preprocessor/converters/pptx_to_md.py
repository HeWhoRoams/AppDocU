"""
PPTX to Markdown Converter
Converts Microsoft PowerPoint presentations to markdown outline format
"""
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any
from pptx import Presentation
from appdocu_preprocessor.converters.base_converter import BaseConverter, ConversionResult


class PptxToMarkdownConverter(BaseConverter):
    def __init__(self):
        super().__init__("pptx_to_md", "pptx")
    
    def convert(self, file_path: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Convert PPTX file to markdown outline format
        
        Args:
            file_path: Path to the input PPTX file
            output_dir: Directory where output should be written
        
        Returns:
            Dictionary with conversion result
        """
        try:
            # Validate input file
            if not self.validate_input_file(file_path):
                return ConversionResult("pptx_to_md").set_failed("Invalid input file").build()
            
            # Load the presentation
            prs = Presentation(str(file_path))
            
            # Build markdown content
            markdown_lines = []
            
            # Process each slide
            for slide_idx, slide in enumerate(prs.slides, 1):
                # Get slide title (usually from the first shape)
                slide_title = f"Slide {slide_idx}"
                title_found = False
                
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        # Often the title is in the first shape or has a title-like style
                        if shape.has_text_frame:
                            text_frame = shape.text_frame
                            if text_frame.text.strip():
                                # Check if this looks like a title (short text, often first shape)
                                if len(text_frame.text.strip()) < 100 and not title_found:
                                    slide_title = text_frame.text.strip().replace('\n', ' ').replace('\r', ' ')
                                    title_found = True
                                    break
                
                # Add slide header
                markdown_lines.append(f"## {slide_title}")
                
                # Collect all text from shapes
                slide_content = []
                
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        text_frame = shape.text_frame
                        for paragraph in text_frame.paragraphs:
                            text = paragraph.text.strip()
                            if text and text != slide_title:
                                slide_content.append(text)  # Add slide content as bullet points
                for content in slide_content:
                    # Split by lines and add as separate bullet points
                    for line in content.split('\n'):
                        line = line.strip()
                        if line:
                            markdown_lines.append(f"- {line}")
                
                # Add speaker notes if present
                if slide.has_notes_slide:
                    notes_slide = slide.notes_slide
                    if notes_slide.notes_text_frame:
                        notes_text = notes_slide.notes_text_frame.text.strip()
                        if notes_text:
                            markdown_lines.append("\n**Notes:**")
                            for note_line in notes_text.split('\n'):
                                note_line = note_line.strip()
                                if note_line:
                                    markdown_lines.append(f"- {note_line}")
                
                # Add blank line between slides
                markdown_lines.append("")
            
            # Join all lines
            markdown_content = "\n".join(markdown_lines).strip()
            
            # Add metadata header
            markdown_content = self.add_metadata_header(markdown_content, file_path)
            
            # Write output file
            output_file = self.write_output_file(output_dir, file_path, markdown_content, ".md")
            
            # Create result with metadata
            result = ConversionResult("pptx_to_md")
            result.set_success(str(output_file.relative_to(output_dir.parent)))
            result.add_metadata('slides', len(prs.slides))
            result.add_metadata('has_notes', any(slide.has_notes_slide for slide in prs.slides))
            result.add_metadata('file_info', self.get_file_info(file_path))
            
            conversion_result = result.build()
            self.log_conversion_result(file_path, conversion_result)
            return conversion_result
            
        except Exception as e:
            error_result = self.handle_conversion_error(file_path, e)
            return error_result


def convert(file_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Wrapper function for backward compatibility"""
    converter = PptxToMarkdownConverter()
    return converter.convert(file_path, output_dir)
