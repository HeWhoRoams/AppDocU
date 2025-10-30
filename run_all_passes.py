#!/usr/bin/env python3
"""
Run all passes of AppDocU sequentially to show complete workflow
"""
import sys
from pathlib import Path
import time
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_simple_logging():
    """Setup simple logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True
    )
    return logging.getLogger(__name__)

def run_pass_sequentially(pass_number, target_path, output_dir=None):
    """Run a specific pass and wait for completion"""
    logger = setup_simple_logging()
    logger.info(f"🚀 Starting Pass {pass_number}...")
    
    try:
        # Import the orchestrator
        from appdoc import AppDocUOrchestrator
        
        # Create orchestrator with proper paths
        orchestrator = AppDocUOrchestrator(str(target_path), output_dir)
        
        # Run the specific pass
        if pass_number == 1:
            result = orchestrator.run_pass_1_discovery()
            logger.info("✅ Pass 1: Discovery completed")
        elif pass_number == 2:
            result = orchestrator.run_pass_2_enrichment()
            logger.info("✅ Pass 2: Enrichment completed")
        elif pass_number == 3:
            result = orchestrator.run_pass_3_cognitive_audit()
            logger.info("✅ Pass 3: Cognitive Audit completed")
        else:
            logger.error(f"❌ Invalid pass number: {pass_number}")
            return False
            
        if result and result.get('status') == 'completed':
            logger.info(f"✅ Pass {pass_number} completed successfully")
            return True
        else:
            logger.error(f"❌ Pass {pass_number} failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Pass {pass_number} crashed: {str(e)}")
        return False

def main():
    """Run all passes sequentially"""
    logger = setup_simple_logging()
    logger.info("🎯 Starting Sequential AppDocU Workflow")
    
    target_path = Path(r"C:\github\LMSconnect")
    output_dir = None  # Use default (_normalized)
    
    if not target_path.exists():
        logger.error(f"❌ Target path does not exist: {target_path}")
        return False
    
    logger.info(f"📂 Target: {target_path}")
    
    # Run all 3 passes
    passes = [1, 2, 3]
    success_count = 0
    
    for pass_num in passes:
        logger.info(f"\n📋 Running Pass {pass_num}...")
        start_time = time.time()
        
        success = run_pass_sequentially(pass_num, target_path, output_dir)
        
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"⏱️  Pass {pass_num} took {duration:.2f} seconds")
        
        if success:
            success_count += 1
        else:
            logger.error(f"❌ Stopping workflow due to Pass {pass_num} failure")
            break
    
    # Summary
    logger.info(f"\n🎯 Workflow Summary")
    logger.info("=" * 40)
    logger.info(f"Total passes attempted: {len(passes)}")
    logger.info(f"Successful passes: {success_count}")
    logger.info(f"Overall status: {'✅ SUCCESS' if success_count == len(passes) else '❌ PARTIAL FAILURE'}")
    
    if success_count == len(passes):
        logger.info("🎉 All passes completed successfully!")
        logger.info(f"📁 Output directory: {target_path / '_normalized'}")
        return True
    else:
        logger.error("💥 Some passes failed - check logs for details")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
