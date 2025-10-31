#!/usr/bin/env python3
"""
Direct run of AppDocU functionality to bypass import issues
"""
import sys
import logging
from pathlib import Path
 
# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("=== Direct AppDocU Run ===")
    
    # Set up basic logging to see output
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    target_path = r"C:\Github\LMSConnect"
    output_dir = r"C:\Github\LMSConnect\_normalized"
    
    print(f"Target path: {target_path}")
    print(f"Output directory: {output_dir}")
    
    try:
        # Import the preprocessing function
        from appdocu_preprocessor import preprocess_repository
        
        print("Calling preprocess_repository...")
        result = preprocess_repository(target_path, output_dir, validate=True)
        
        print(f"Preprocessing result: {result}")
        
        if result.get('status') == 'completed':
            print("✅ Preprocessing completed successfully!")
            
            # Now run the workflow
            from appdocu_preprocessor.workflow import PreprocessorWorkflow
            workflow = PreprocessorWorkflow(Path(target_path), Path(output_dir))
            
            print("Running full workflow...")
            workflow_result = workflow.run_workflow()
            print(f"Workflow result: {workflow_result}")
            
        else:
            print(f"❌ Preprocessing failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✅ Direct run completed!")
    return True

if __name__ == "__main__":
    main()
