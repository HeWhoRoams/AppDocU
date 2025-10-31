"""
AppDocU Preprocessor Workflow
Orchestrates the complete preprocessing pipeline from file enumeration to normalization

This module provides the core workflow orchestration for the AppDocU preprocessor system,
handling file enumeration, processing, validation, and reporting. It manages the complete
end-to-end preprocessing pipeline with proper error handling, logging, and metrics collection.
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import traceback

# Import modules only when needed to avoid config initialization issues
# Move all imports inside methods where they're actually used
# from appdocu_preprocessor.file_enumerator import FileEnumerator, FileInfo, FileType
# from appdocu_preprocessor.converters.base_converter import BaseConverter, ConversionResult
# from appdocu_preprocessor.converters.code_handler import CodeHandler
# from appdocu_preprocessor.converters.docx_to_md import DocxToMdConverter
# from appdocu_preprocessor.converters.xlsx_to_csv import XlsxToCsvConverter
# from appdocu_preprocessor.converters.visio_to_json import VisioToJsonConverter
# from appdocu_preprocessor.converters.pdf_to_md import PdfToMdConverter
# from appdocu_preprocessor.converters.pptx_to_md import PptxToMdConverter
# from appdocu_preprocessor.converters.ticket_handler import TicketHandler
# from appdocu_preprocessor.converters.image_handler import ImageHandler
# Import get_global_config only when needed to avoid config initialization issues
# get_global_config is not actually used in this module, so we can remove it
# from appdocu_preprocessor.config import get_global_config

logger = logging.getLogger(__name__)


class PreprocessorWorkflow:
    """Orchestrates the complete preprocessing workflow"""
    
    def __init__(self, root_path: Path, output_dir: Optional[Path] = None):
        """
        Initialize preprocessor workflow
        
        Args:
            root_path: Root path of repository to process
            output_dir: Output directory (defaults to root_path/_normalized)
        """
        logger.debug("Initializing PreprocessorWorkflow")
        self.root_path = Path(root_path)
        self.output_dir = Path(output_dir) if output_dir else self.root_path / "_normalized"
        self.meta_dir = self.output_dir / ".meta"
        self.normalized_dir = self.output_dir / "normalized"
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.meta_dir.mkdir(exist_ok=True)
        self.normalized_dir.mkdir(exist_ok=True)
        
        # Import and initialize components only when needed
        # Move FileEnumerator import here to avoid config issues
        logger.debug("Importing FileEnumerator and initializing components")
        from appdocu_preprocessor.file_enumerator import FileEnumerator
        self.enumerator = FileEnumerator(root_path)
        self.handlers = self._initialize_handlers()
        self.file_manifest: List[Any] = []  # Will be populated during workflow execution
        self.conversion_results: List[Dict[str, Any]] = []
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def _initialize_handlers(self) -> Dict['FileType', object]:
        """Initialize file type handlers with minimal safe set.
        Avoid importing heavy converters that may not be available.
        """
        from appdocu_preprocessor.converters.code_handler import CodeHandler
        from appdocu_preprocessor.file_enumerator import FileType

        return {
            FileType.CODE: CodeHandler(),
            # Other handlers intentionally omitted to avoid optional deps
        }
    
    def run_workflow(self) -> Dict[str, Any]:
        """
        Run the complete preprocessing workflow
        
        Returns:
            Dictionary with workflow results and statistics
        """
        logger.info(f"🚀 Starting AppDocU Preprocessor Workflow")
        logger.info(f"Root path: {self.root_path}")
        logger.info(f"Output directory: {self.output_dir}")
        
        try:
            # Step 1: Enumerate files
            logger.info("📋 Step 1: Enumerating files...")
            self.file_manifest = self.enumerator.enumerate_files()
            self.stats['total_files'] = len(self.file_manifest)
            logger.info(f"   Found {len(self.file_manifest)} files")
            
            # Step 2: Write initial file manifest
            logger.info("📝 Step 2: Writing initial file manifest...")
            self.enumerator.write_file_manifest(self.file_manifest, self.output_dir)
            
            # Step 3: Process files
            logger.info("⚙️  Step 3: Processing files...")
            self._process_files()
            
            # Step 4: Update file manifest with results
            logger.info("📊 Step 4: Updating file manifest with results...")
            self.enumerator.write_file_manifest(self.file_manifest, self.output_dir)
            
            # Step 5: Generate reports
            logger.info("📈 Step 5: Generating reports...")
            self._generate_reports()
            
            # Step 6: Final summary
            logger.info("✅ Step 6: Workflow completed")
            return self._generate_summary()
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {str(e)}", exc_info=True)
            return {
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def _process_files(self):
        """Process all files in the manifest"""
        for i, file_info in enumerate(self.file_manifest):
            try:
                file_path = self.root_path / file_info.file
                logger.info(f"[{i+1}/{len(self.file_manifest)}] Processing {file_info.file}")
                
                # Get appropriate handler
                try:
                    file_type = FileType(file_info.type)
                    handler = self.handlers.get(file_type)
                except ValueError:
                    file_type = FileType.OTHER
                    handler = None
                
                if handler is None:
                    logger.warning(f"No handler for file type {file_info.type}, skipping")
                    file_info.status = "skipped"
                    file_info.error = "No handler available"
                    self.stats['skipped'] += 1
                    continue
                
                # Process file
                result = handler.convert(file_path, self.normalized_dir, self.root_path)
                self.conversion_results.append(result)
                
                # Update file info
                if result['status'] == 'success':
                    file_info.status = "converted"
                    file_info.output_file = result.get('output')
                    self.stats['successful'] += 1
                    logger.info(f"✅ Converted {file_info.file} → {result['output']}")
                elif result['status'] == 'failed':
                    file_info.status = "failed"
                    file_info.error = result.get('error')
                    self.stats['failed'] += 1
                    logger.warning(f"❌ Failed to convert {file_info.file}: {result['error']}")
                else:
                    file_info.status = "skipped"
                    file_info.error = result.get('reason')
                    self.stats['skipped'] += 1
                    logger.info(f"⏭️  Skipped {file_info.file}: {result.get('reason', 'Unknown reason')}")
                
                self.stats['processed'] += 1
                
            except Exception as e:
                logger.error(f"Unexpected error processing {file_info.file}: {str(e)}", exc_info=True)
                file_info.status = "failed"
                file_info.error = f"Unexpected error: {str(e)}"
                self.stats['failed'] += 1
                self.stats['processed'] += 1
    
    def _generate_reports(self):
        """Generate workflow reports and statistics"""
        # Conversion report
        conversion_report = {
            'generated_at': datetime.now(timezone.utc).isoformat() + 'Z',
            'stats': self.stats,
            'conversion_rate': self._calculate_conversion_rate(),
            'coverage_percentage': self._calculate_coverage_percentage(),
            'errors': self._collect_errors(),
            'warnings': self._collect_warnings()
        }
        
        # Write conversion report
        conversion_report_file = self.meta_dir / "conversion_report.json"
        with open(conversion_report_file, 'w', encoding='utf-8') as f:
            json.dump(conversion_report, f, indent=2, ensure_ascii=False)
        logger.info(f"Wrote conversion report to {conversion_report_file}")
        
        # Handler versions report
        handler_versions = {}
        for file_type, handler in self.handlers.items():
            handler_versions[file_type.value] = {
                'handler_class': handler.__class__.__name__,
                'handler_module': handler.__class__.__module__
            }
        
        handlers_report = {
            'generated_at': datetime.now(timezone.utc).isoformat() + 'Z',
            'handlers': handler_versions
        }
        
        # Write handlers report
        handlers_report_file = self.meta_dir / "handlers.json"
        with open(handlers_report_file, 'w', encoding='utf-8') as f:
            json.dump(handlers_report, f, indent=2, ensure_ascii=False)
        logger.info(f"Wrote handlers report to {handlers_report_file}")
    
    def _calculate_conversion_rate(self) -> float:
        """Calculate conversion success rate"""
        if self.stats['processed'] == 0:
            return 100.0
        return (self.stats['successful'] / self.stats['processed']) * 100.0
    
    def _calculate_coverage_percentage(self) -> float:
        """Calculate file coverage percentage"""
        if self.stats['total_files'] == 0:
            return 100.0
        return (self.stats['processed'] / self.stats['total_files']) * 100.0
    
    def _collect_errors(self) -> List[Dict[str, str]]:
        """Collect all conversion errors"""
        errors = []
        for file_info in self.file_manifest:
            if file_info.status == "failed" and file_info.error:
                errors.append({
                    'file': file_info.file,
                    'error': file_info.error
                })
        return errors
    
    def _collect_warnings(self) -> List[str]:
        """Collect workflow warnings"""
        warnings = []
        coverage = self._calculate_coverage_percentage()
        if coverage < 95.0:
            warnings.append(f"Low coverage: {coverage:.1f}% of files processed")
        return warnings
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate final workflow summary"""
        conversion_rate = self._calculate_conversion_rate()
        coverage_percentage = self._calculate_coverage_percentage()
        
        summary = {
            'status': 'completed' if self.stats['failed'] == 0 else 'completed_with_errors',
            'generated_at': datetime.now(timezone.utc).isoformat() + 'Z',
            'repository': str(self.root_path),
            'stats': self.stats,
            'conversion_rate': f"{conversion_rate:.1f}%",
            'coverage_percentage': f"{coverage_percentage:.1f}%",
            'output_directory': str(self.output_dir),
            'normalized_directory': str(self.normalized_dir),
            'meta_directory': str(self.meta_dir)
        }
        
        logger.info("=" * 60)
        logger.info("📊 WORKFLOW SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Repository: {self.root_path}")
        logger.info(f"Total files: {self.stats['total_files']}")
        logger.info(f"Processed: {self.stats['processed']}")
        logger.info(f"Successful: {self.stats['successful']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Conversion rate: {conversion_rate:.1f}%")
        logger.info(f"Coverage: {coverage_percentage:.1f}%")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("=" * 60)
        
        if self.stats['failed'] > 0:
            logger.warning(f"⚠️  {self.stats['failed']} files failed to process")
            logger.warning("Check conversion_report.json for details")
        elif conversion_rate >= 95.0:
            logger.info("🎉 Excellent conversion rate achieved!")
        else:
            logger.info("✅ Workflow completed successfully")
        
        return summary


def main():
    """Main entry point for the preprocessor workflow"""
    import argparse
    parser = argparse.ArgumentParser(description='AppDocU Preprocessor Workflow')
    parser.add_argument('--path', required=True, help='Root path of repository to process')
    parser.add_argument('--output', help='Output directory (default: _normalized)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run workflow
    root_path = Path(args.path)
    output_dir = Path(args.output) if args.output else None
    
    workflow = PreprocessorWorkflow(root_path, output_dir)
    result = workflow.run_workflow()
    
    # Exit with appropriate code
    if result['status'] == 'failed':
        sys.exit(1)
    elif result['status'] == 'completed':
        sys.exit(0)
    else:
        sys.exit(0)  # Completed with warnings is still success


if __name__ == '__main__':
    main()





