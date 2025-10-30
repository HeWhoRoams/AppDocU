#!/usr/bin/env python3
"""
Direct import test to see where the hang occurs
"""
import sys
import logging
import time
from pathlib import Path

def test_direct_import():
    """Test direct import with timing"""
    print("=== Direct Import Test ===")
    
    # Disable logging first
    logging.disable(logging.CRITICAL)
    
    start_time = time.time()
    print(f"Starting import at: {start_time}")
    
    try:
        print("About to import appdocu_preprocessor.config...")
        import appdocu_preprocessor.config
        print("Import successful!")
        
        end_time = time.time()
        print(f"Import completed at: {end_time}")
        print(f"Total time: {end_time - start_time:.2f} seconds")
        
        # Test creating a config instance without full initialization
        print("Testing PreprocessorConfig...")
        config_obj = appdocu_preprocessor.config.PreprocessorConfig()
        print(f"Config created successfully: {config_obj.output_directory}")
        
        # Re-enable logging
        logging.disable(logging.NOTSET)
        
        return True
        
    except KeyboardInterrupt:
        end_time = time.time()
        print(f"Import was interrupted at: {end_time}")
        print(f"Time elapsed: {end_time - start_time:.2f} seconds")
        print("The import was hanging!")
        return False
    except Exception as e:
        end_time = time.time()
        print(f"Import failed at: {end_time}")
        print(f"Time elapsed: {end_time - start_time:.2f} seconds")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_direct_import()
