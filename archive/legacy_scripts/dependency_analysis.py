#!/usr/bin/env python3
"""
Analyze and test dependencies one by one to identify the problematic ones
"""
import sys
import time
from pathlib import Path
 
def test_single_import(module_name, import_statement):
    """Test importing a single module safely"""
    print(f"Testing import: {module_name}")
    start_time = time.time()
    
    try:
        # Use exec to safely test the import
        exec(import_statement, globals())
        elapsed = time.time() - start_time
        print(f"  SUCCESS in {elapsed:.2f}s")
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f" FAILED after {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=== Dependency Analysis for AppDocU ===\n")
    
    # Test basic imports first
    basic_imports = [
        ("os", "import os"),
        ("sys", "import sys"),
        ("json", "import json"),
        ("pathlib", "from pathlib import Path"),
        ("logging", "import logging"),
    ]
    
    print("1. Testing Basic Python Imports:")
    for name, stmt in basic_imports:
        test_single_import(name, stmt)
    print()
    
    # Test the converter imports that might be problematic
    converter_imports = [
        ("Base Converter", "from appdocu_preprocessor.converters.base_converter import BaseConverter"),
        ("Code Handler", "from appdocu_preprocessor.converters.code_handler import CodeHandler"),
        ("Docx Converter", "from appdocu_preprocessor.converters.docx_to_md import DocxToMdConverter"),
        ("PDF Converter", "from appdocu_preprocessor.converters.pdf_to_md import PdfToMdConverter"),
        ("PPTX Converter", "from appdocu_preprocessor.converters.pptx_to_md import PptxToMdConverter"),
        ("XLSX Converter", "from appdocu_preprocessor.converters.xlsx_to_csv import XlsxToCsvConverter"),
        ("Visio Converter", "from appdocu_preprocessor.converters.visio_to_json import VisioToJsonConverter"),
        ("Image Handler", "from appdocu_preprocessor.converters.image_handler import ImageHandler"),
        ("Ticket Handler", "from appdocu_preprocessor.converters.ticket_handler import TicketHandler"),
    ]
    
    print("2. Testing Converter Imports:")
    for name, stmt in converter_imports:
        test_single_import(name, stmt)
    print()
    
    # Test core modules
    core_imports = [
        ("File Enumerator", "from appdocu_preprocessor.file_enumerator import FileEnumerator"),
        ("Config", "from appdocu_preprocessor.config import get_global_config"),
        ("Workflow", "from appdocu_preprocessor.workflow import PreprocessorWorkflow"),
        ("Validation", "from appdocu_preprocessor.validation import PreprocessorValidator"),
    ]
    
    print("3. Testing Core Module Imports:")
    for name, stmt in core_imports:
        test_single_import(name, stmt)
    print()
    
    # Test the main preprocessor
    print("4. Testing Main Preprocessor Import:")
    test_single_import("Main Preprocessor", "import appdocu_preprocessor")
    print()
    
    print("5. Testing preprocess_repository function:")
    test_single_import("preprocess_repository", "from appdocu_preprocessor import preprocess_repository")
    print()
    
    print("=== Dependency Analysis Complete ===")

if __name__ == "__main__":
    main()
