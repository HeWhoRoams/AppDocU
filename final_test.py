#!/usr/bin/env python3
"""
Final test to see what's happening with AppDocU imports
"""
import sys
import time
import logging
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    # Write output to a file to capture what's happening
    from pathlib import Path
    log_file = Path("debug_output.txt")
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== AppDocU Import Test Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Current working directory: {Path.cwd()}\n")
        
        try:
            f.write("1. Testing basic imports...\n")
            import os
            import json
            import argparse
            from pathlib import Path
            f.write("   SUCCESS: Basic imports successful\n")
            
            f.write("2. Testing appdocu_preprocessor import...\n")
            import appdocu_preprocessor
            f.write("   SUCCESS: appdocu_preprocessor import successful\n")
            
            f.write("3. Testing preprocess_repository function...\n")
            from appdocu_preprocessor import preprocess_repository
            f.write("   SUCCESS: preprocess_repository import successful\n")
            
            f.write("4. Testing workflow import...\n")
            from appdocu_preprocessor.workflow import PreprocessorWorkflow
            f.write("   SUCCESS: workflow import successful\n")
            
            f.write("5. Testing validation import...\n")
            from appdocu_preprocessor.validation import PreprocessorValidator
            f.write("   SUCCESS: validation import successful\n")
            
            f.write("6. Creating workflow instance...\n")
            workflow = PreprocessorWorkflow(Path(r"C:\Github\LMSConnect"), Path(r"C:\Github\LMSConnect\_normalized"))
            f.write("   SUCCESS: Workflow instance created\n")
            
            f.write("7. Running workflow...\n")
            result = workflow.run_workflow()
            f.write(f"   SUCCESS: Workflow completed with result: {result.get('status', 'unknown')}\n")
            
            f.write("=== Test completed successfully! ===\n")
            f.write(f"Result: {result}\n")
            
        except Exception as e:
            f.write(f"ERROR: Error occurred: {e}\n")
            import traceback
            f.write(f"Traceback: {traceback.format_exc()}\n")
            return False
    
    print(f"Debug output written to {log_file}")
    return True

if __name__ == "__main__":
    main()
