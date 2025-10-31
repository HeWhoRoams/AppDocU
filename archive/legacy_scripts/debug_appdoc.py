#!/usr/bin/env python3
"""
Debug script to test AppDocU functionality
"""
import sys
import logging
import traceback
from pathlib import Path
 
# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    try:
        from appdocu_preprocessor import preprocess_repository
        from appdocu_preprocessor.workflow import PreprocessorWorkflow
        from appdocu_preprocessor.validation import PreprocessorValidator
        from appdocu_preprocessor.config import get_global_config, ConfigManager
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_file_enumerator():
    """Test file enumerator"""
    print("\nTesting file enumerator...")
    try:
        from appdocu_preprocessor.file_enumerator import FileEnumerator
        import logging
        
        # Set up logging to see output
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        target_path = Path(r"C:\Github\LMSConnect")
        if not target_path.exists():
            print(f"❌ Target path does not exist: {target_path}")
            return False
            
        print(f"Scanning directory: {target_path}")
        enumerator = FileEnumerator(target_path)
        files = enumerator.enumerate_files()
        print(f"✅ Found {len(files)} files")
        return True
    except Exception as e:
        print(f"❌ File enumerator error: {e}")
        traceback.print_exc()
        return False

def test_preprocessing():
    """Test preprocessing function"""
    print("\nTesting preprocessing...")
    try:
        from appdocu_preprocessor import preprocess_repository
        import logging
        
        # Set up logging to see output
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        target_path = r"C:\Github\LMSConnect"
        output_dir = r"C:\Github\LMSConnect\_normalized"
        
        print(f"Preprocessing repository: {target_path}")
        result = preprocess_repository(target_path, output_dir, validate=True)
        print(f"Preprocessing result: {result}")
        return True
    except Exception as e:
        print(f"❌ Preprocessing error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("Starting AppDocU debug tests...")
    
    # Test imports
    if not test_imports():
        return False
    
    # Test file enumerator
    if not test_file_enumerator():
        return False
    
    # Test preprocessing
    if not test_preprocessing():
        return False
    
    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    main()
