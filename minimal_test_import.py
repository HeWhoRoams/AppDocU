#!/usr/bin/env python3
"""
Minimal test to identify which import causes the crash
"""
import sys
from pathlib import Path

def test_imports():
    print("Testing imports one by one...")
    
    # Add project root to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    imports_to_test = [
        ("os", "import os"),
        ("sys", "import sys"),
        ("json", "import json"),
        ("argparse", "import argparse"),
        ("logging", "import logging"),
        ("pathlib", "from pathlib import Path"),
        ("datetime", "from datetime import datetime"),
        ("typing", "from typing import Dict, Any, Optional"),
        ("appdocu_preprocessor", "import appdocu_preprocessor"),
        ("preprocess_repository", "from appdocu_preprocessor import preprocess_repository"),
        ("PreprocessorWorkflow", "from appdocu_preprocessor.workflow import PreprocessorWorkflow"),
        ("PreprocessorValidator", "from appdocu_preprocessor.validation import PreprocessorValidator"),
        ("FileEnumerator", "from appdocu_preprocessor.file_enumerator import FileEnumerator"),
        ("ConfigManager", "from appdocu_preprocessor.config import ConfigManager"),
        ("get_global_config", "from appdocu_preprocessor.config import get_global_config"),
    ]
    
    for i, (name, import_stmt) in enumerate(imports_to_test, 1):
        print(f"{i:2d}. Testing {name}...", end=" ")
        try:
            exec(import_stmt)
            print("✅ SUCCESS")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("Import test completed.")

if __name__ == "__main__":
    test_imports()
