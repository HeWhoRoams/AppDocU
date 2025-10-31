#!/usr/bin/env python3
"""
Diagnostic tool to understand what's happening with AppDocU imports
"""
import sys
import os
from pathlib import Path
import time
 
def diagnose_imports():
    """Diagnose import issues step by step"""
    print("=== AppDocU Diagnostic Tool ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 paths
    
    # Test basic imports first
    basic_imports = [
        ('os', 'import os'),
        ('sys', 'import sys'), 
        ('json', 'import json'),
        ('pathlib', 'from pathlib import Path'),
        ('logging', 'import logging'),
    ]
    
    print("\n1. Testing basic imports:")
    for name, import_stmt in basic_imports:
        try:
            start_time = time.time()
            exec(import_stmt)
            end_time = time.time()
            print(f"   ✅ {name} - {end_time - start_time:.3f}s")
        except Exception as e:
            print(f"   ❌ {name} - FAILED: {e}")
            return False
    
    # Test appdocu_preprocessor imports
    print("\n2. Testing appdocu_preprocessor imports:")
    preprocessor_imports = [
        ('appdocu_preprocessor', 'import appdocu_preprocessor'),
        ('appdocu_preprocessor.config', 'from appdocu_preprocessor import config'),
        ('appdocu_preprocessor.workflow', 'from appdocu_preprocessor import workflow'),
        ('appdocu_preprocessor.validation', 'from appdocu_preprocessor import validation'),
        ('appdocu_preprocessor.file_enumerator', 'from appdocu_preprocessor import file_enumerator'),
        ('appdocu_preprocessor.caching', 'from appdocu_preprocessor import caching'),
        ('appdocu_preprocessor.normalize', 'from appdocu_preprocessor import normalize'),
        ('appdocu_preprocessor.monitoring', 'from appdocu_preprocessor import monitoring'),
        ('appdocu_preprocessor.exceptions', 'from appdocu_preprocessor import exceptions'),
    ]
    
    for name, import_stmt in preprocessor_imports:
        try:
            start_time = time.time()
            exec(import_stmt)
            end_time = time.time()
            print(f"   ✅ {name} - {end_time - start_time:.3f}s")
        except Exception as e:
            print(f"   ❌ {name} - FAILED: {e}")
            # Don't return here, continue to see all failures
    
    # Test specific class imports
    print("\n3. Testing specific class imports:")
    class_imports = [
        ('FileEnumerator', 'from appdocu_preprocessor.file_enumerator import FileEnumerator'),
        ('PreprocessorWorkflow', 'from appdocu_preprocessor.workflow import PreprocessorWorkflow'),
        ('PreprocessorValidator', 'from appdocu_preprocessor.validation import PreprocessorValidator'),
    ]
    
    for name, import_stmt in class_imports:
        try:
            start_time = time.time()
            exec(import_stmt)
            end_time = time.time()
            print(f"   ✅ {name} - {end_time - start_time:.3f}s")
        except Exception as e:
            print(f"   ❌ {name} - FAILED: {e}")
    
    print("\n=== Diagnostic Complete ===")
    return True

def diagnose_appdoc_py():
    """Diagnose the appdoc.py file specifically"""
    print("\n=== Diagnosing appdoc.py ===")
    
    appdoc_path = Path(__file__).parent / "appdoc.py"
    if not appdoc_path.exists():
        print(f"❌ appdoc.py not found at {appdoc_path}")
        return False
    
    try:
        print(f"✅ appdoc.py found at {appdoc_path}")
        print(f"   Size: {appdoc_path.stat().st_size} bytes")
        
        # Read first few lines to check for obvious issues
        with open(appdoc_path, 'r', encoding='utf-8') as f:
            first_lines = f.read(1000)
        
        if "get_global_config" in first_lines:
            print("⚠️  Found get_global_config in appdoc.py - this might cause issues")
        else:
            print("✅ No get_global_config found in appdoc.py")
            
        return True
        
    except Exception as e:
        print(f"❌ Error reading appdoc.py: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting AppDocU Diagnostic...")
    
    success = diagnose_imports()
    diagnose_appdoc_py()
    
    if success:
        print("\n🎉 Diagnostic completed successfully!")
    else:
        print("\n❌ Diagnostic failed!")
        sys.exit(1)
