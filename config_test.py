#!/usr/bin/env python3
"""
Test to isolate the config issue
"""
import sys
import logging
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_config_import():
    """Test config import without initialization"""
    print("=== Config Import Test ===")
    
    # Disable logging to avoid file handler issues
    logging.disable(logging.CRITICAL)
    
    try:
        print("1. Importing config module...")
        import appdocu_preprocessor.config as config_module
        print("✅ Config module imported successfully")
        
        print("2. Testing PreprocessorConfig class...")
        config = config_module.PreprocessorConfig()
        print("✅ PreprocessorConfig instantiated successfully")
        print(f"   Output directory: {config.output_directory}")
        
        print("3. Testing ConfigManager class (without initialization)...")
        print("   ConfigManager class exists:", hasattr(config_module, 'ConfigManager'))
        
        # Try to access the get_global_config function without calling it
        print("   get_global_config function exists:", hasattr(config_module, 'get_global_config'))
        
        # Now try to call get_global_config (this might be the issue)
        print("4. Testing get_global_config function call...")
        try:
            config_manager = config_module.get_global_config()
            print("✅ get_global_config called successfully")
        except Exception as e:
            print(f"❌ get_global_config failed: {e}")
            import traceback
            traceback.print_exc()
            
        # Re-enable logging
        logging.disable(logging.NOTSET)
        
        print("\n✅ Config test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    return test_config_import()

if __name__ == "__main__":
    main()
