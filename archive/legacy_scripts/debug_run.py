#!/usr/bin/env python3
"""
Debug run of AppDocU to capture actual output and errors
"""
import subprocess
import sys
import time
 
def main():
    print("Running AppDocU with debug output...")
    
    cmd = [sys.executable, 'appdoc.py', '--target', r'C:\github\LMSconnect', '--verbose']
    
    start_time = time.time()
    print(f"Command: {' '.join(cmd)}")
    print("Starting process...")
    
    try:
        # Run with timeout and capture output
        result = subprocess.run(
            cmd,
            timeout=120,  # 2 minute timeout
            capture_output=True,
            text=True,
            cwd='.' # Current directory
        )
        
        end_time = time.time()
        print(f"Process completed in {end_time - start_time:.2f} seconds")
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        print(f"Process timed out after {end_time - start_time:.2f} seconds")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"Command {'succeeded' if success else 'failed'}")
