#!/usr/bin/env python3
"""
Test importing PreprocessorWorkflow to see what happens
"""
import sys
from pathlib import Path
import time

def test_import():
    print(f"Starting import test at {time.strftime('%H:%M:%S')}")
    
    # Add the project root to the path
    sys.path.insert(0, str(Path(__file__).parent))
    
    start_time = time.time()
    
    try:
        print("1. About to import PreprocessorWorkflow...")
        from appdocu_preprocessor.workflow import PreprocessorWorkflow
        print("2. ✅ PreprocessorWorkflow imported successfully!")
        
        elapsed = time.time() - start_time
        print(f"3. Import took {elapsed:.2f} seconds")
        
        print("4. About to create instance...")
        target_path = Path(r"C:\Github\LMSConnect")
        output_dir = Path(r"C:\Github\LMSConnect\_normalized")
        
        workflow = PreprocessorWorkflow(target_path, output_dir)
        print("5. ✅ Workflow instance created successfully!")
        
        elapsed = time.time() - start_time
        print(f"6. Total time to create instance: {elapsed:.2f} seconds")
        
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error after {elapsed:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_import()
