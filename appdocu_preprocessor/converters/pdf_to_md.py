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


def convert(file_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Convert PDF file to markdown format
    
    Args:
        file_path: Path to the input PDF file
        output_dir: Directory where output should be written
    
    Returns:
        Dictionary with conversion result
    """
    try:
        # Create pdf output directory if it doesn't exist
        pdf_dir = output_dir / "pdf"
        pdf_dir.mkdir(exist_ok=True)
        
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
        
        # Add metadata header
        markdown_content = f"""---
source: {file_path.relative_to(file_path.parent)}
converted_at: {datetime.utcnow().isoformat()}Z
converter: pdf_to_md
---

{"\\n\\n".join(paragraph_lines)}
"""
        
        # Write output file
        output_filename = file_path.stem + ".md"
        output_file = pdf_dir / output_filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Get page count
        # Get page count from already extracted text
        page_count = len(text.split('\f')) if text else 0        
        # Safely compute output path string
        try:
            output_path = str(output_file.relative_to(output_dir.parent))
        except ValueError:
            import os
            try:
                output_path = os.path.relpath(str(output_file), str(output_dir.parent))
            except Exception:
                output_path = str(output_file)

        return {
            'status': 'success',
            'output': output_path,
            'converter': 'pdf_to_md',
            'metadata': {
                'pages': page_count,
                'characters': len(text),
                'paragraphs': len(paragraph_lines)
            }
def extract_page_count(file_path: Path) -> int:
    """
    Helper function to extract page count from PDF
    """
    try:
        text = extract_text(str(file_path))
        # PDF text is often separated by form feed characters
        pages = text.split('\f')
        return len([p for p in pages if p.strip()])
    except Exception:
        return 0    """
    Helper function to extract page count from PDF
    """
    try:
        text = extract_text(str(file_path))
        # PDF text is often separated by form feed characters
        pages = text.split('\f')
        return len([p for p in pages if p.strip()])
    except:
        return 0
