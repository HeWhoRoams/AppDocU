#!/usr/bin/env python3
"""
Test importing appdocu_preprocessor without calling functions
"""
import sys
import logging
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_import_only():
    """Test importing without calling functions"""
    print("=== Import Only Test ===")
    
    # Disable logging to prevent file handler issues
    logging.disable(logging.CRITICAL)
    
    try:
        print("Starting import test...")
        
        # Import the main package without calling anything
        import appdocu_preprocessor
        print("✅ Main package imported successfully")
        
        # Check if preprocess_repository function is available
        print(f"✅ preprocess_repository function exists: {hasattr(appdocu_preprocessor, 'preprocess_repository')}")
        
        # Re-enable logging
        logging.disable(logging.NOTSET)
        
        print("✅ Import test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_import_only()
