#!/usr/bin/env python3
"""
Minimal test to isolate the import issue
"""
import sys
import logging
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_minimal_import():
    """Test minimal import without configuration initialization"""
    print("=== Minimal Import Test ===")
    
    # Temporarily disable logging configuration to avoid file handler issues
    logging.disable(logging.CRITICAL)
    
    try:
        print("1. Testing basic imports...")
        import os
        import json
        import argparse
        from pathlib import Path
        print("✅ Basic imports successful")
        
        print("2. Testing config module import...")
        # Import config module but don't call get_global_config()
        from appdocu_preprocessor.config import PreprocessorConfig, ConfigManager
        print("✅ Config module imported successfully")
        
        print("3. Testing exceptions module...")
        import appdocu_preprocessor.exceptions
        print("✅ Exceptions module imported successfully")
        
        print("4. Testing monitoring module...")
        import appdocu_preprocessor.monitoring
        print("✅ Monitoring module imported successfully")
        
        print("5. Testing base converter...")
        from appdocu_preprocessor.converters.base_converter import BaseConverter, ConversionResult
        print("✅ Base converter imported successfully")
        
        print("6. Testing file enumerator...")
        from appdocu_preprocessor.file_enumerator import FileEnumerator, FileInfo, FileType
        print("✅ File enumerator imported successfully")
        
        print("7. Testing workflow...")
        from appdocu_preprocessor.workflow import PreprocessorWorkflow
        print("✅ Workflow imported successfully")
        
        print("8. Testing validation...")
        from appdocu_preprocessor.validation import PreprocessorValidator
        print("✅ Validation imported successfully")
        
        print("9. Testing main preprocessor...")
        from appdocu_preprocessor import preprocess_repository
        print("✅ Main preprocessor imported successfully")
        
        # Re-enable logging
        logging.disable(logging.NOTSET)
        
        print("\n✅ All imports successful! The issue was likely with logging configuration.")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    return test_minimal_import()

if __name__ == "__main__":
    main()
