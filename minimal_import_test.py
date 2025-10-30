#!/usr/bin/env python3
"""
Test the most minimal imports to find the crash point
"""
import sys
from pathlib import Path

def test_imports():
    print("Testing basic imports...")
    
    # Add the project root to the path
    sys.path.insert(0, str(Path(__file__).parent))
    
    print("1. Basic imports...")
    import os
    import sys
    import json
    from pathlib import Path
    print("Basic imports: SUCCESS")
    
    print("2. Testing appdocu_preprocessor.__init__...")
    # Import the package __init__ file only
    import appdocu_preprocessor
    print("Package import: SUCCESS")
    
    print("3. Testing get_global_config import...")
    from appdocu_preprocessor.config import get_global_config
    print("Config import: SUCCESS")
    
    print("4. Testing file_enumerator import...")
    from appdocu_preprocessor.file_enumerator import FileEnumerator
    print("File enumerator import: SUCCESS")
    
    print("5. Testing base_converter import...")
    from appdocu_preprocessor.converters.base_converter import BaseConverter
    print("Base converter import: SUCCESS")
    
    print("6. Testing code_handler import...")
    from appdocu_preprocessor.converters.code_handler import CodeHandler
    print("Code handler import: SUCCESS")
    
    print("7. Testing workflow import...")
    from appdocu_preprocessor.workflow import PreprocessorWorkflow
    print("Workflow import: SUCCESS")
    
    print("All imports completed successfully!")

if __name__ == "__main__":
    test_imports()
