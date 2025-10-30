"""
AppDocU Preprocessor Validation
Validates preprocessing results and generates quality reports

This module provides comprehensive validation capabilities for the AppDocU preprocessor system,
including file manifest validation, conversion coverage analysis, metadata verification, and
quality metrics reporting. It ensures the integrity and completeness of the preprocessing workflow.
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import hashlib

from appdocu_preprocessor.file_enumerator import FileInfo, FileType
from appdocu_preprocessor.converters.base_converter import BaseConverter
# get_global_config import removed - not used in this module and causes import crashes

logger = logging.getLogger(__name__)


class ValidationResult:
    """Represents a validation result for a file or overall process"""
    
    def __init__(self, target: str, validator: str):
        """
        Initialize validation result
        
        Args:
            target: Target being validated (file path, directory, etc.)
            validator: Name of validator that performed the validation
        """
        self.target = target
        self.validator = validator
        self.passed = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metrics: Dict[str, Any] = {}
        self.timestamp = datetime.now(timezone.utc).isoformat() + 'Z'
    
    def add_error(self, error: str):
        """Add an error to the validation result"""
        self.errors.append(error)
        self.passed = False
        logger.error(f"Validation error for {self.target}: {error}")
    
    def add_warning(self, warning: str):
        """Add a warning to the validation result"""
        self.warnings.append(warning)
        logger.warning(f"Validation warning for {self.target}: {warning}")
    
    def add_metric(self, name: str, value: Any):
        """Add a metric to the validation result"""
        self.metrics[name] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary"""
        return {
            'target': self.target,
            'validator': self.validator,
            'passed': self.passed,
            'errors': self.errors,
            'warnings': self.warnings,
            'metrics': self.metrics,
            'timestamp': self.timestamp
        }


class PreprocessorValidator:
    """Validates preprocessing results and generates quality reports"""
    
    def __init__(self, root_path: Path, output_dir: Path):
        """
        Initialize validator
        
        Args:
            root_path: Root path of repository that was processed
            output_dir: Output directory with preprocessing results
        """
        self.root_path = root_path
        self.output_dir = output_dir
        self.meta_dir = output_dir / ".meta"
        self.normalized_dir = output_dir / "normalized"
        self.results: List[ValidationResult] = []
    
    def validate_preprocessing(self) -> ValidationResult:
        """
        Validate the complete preprocessing results
        
        Returns:
            ValidationResult for the overall preprocessing
        """
        result = ValidationResult("preprocessing", "PreprocessorValidator")
        logger.info("🔍 Validating preprocessing results...")
        
        try:
            # Validate required directories exist
            self._validate_required_directories(result)
            
            # Validate metadata files exist
            self._validate_metadata_files(result)
            
            # Validate file manifest
            self._validate_file_manifest(result)
            
            # Validate normalized output structure
            self._validate_normalized_structure(result)
            
            # Validate conversion coverage
            self._validate_conversion_coverage(result)
            
            # Validate file integrity
            self._validate_file_integrity(result)
            
            logger.info(f"✅ Preprocessing validation {'passed' if result.passed else 'failed'}")
            if not result.passed:
                logger.info(f"   Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")
            
        except Exception as e:
            result.add_error(f"Unexpected error during validation: {str(e)}")
            logger.error(f"Validation failed with exception: {str(e)}", exc_info=True)
        
        self.results.append(result)
        return result
    
    def _validate_required_directories(self, result: ValidationResult):
        """Validate that required directories exist"""
        required_dirs = [self.meta_dir, self.normalized_dir]
        for directory in required_dirs:
            if not directory.exists():
                result.add_error(f"Required directory missing: {directory}")
            elif not directory.is_dir():
                result.add_error(f"Required path is not a directory: {directory}")
    
    def _validate_metadata_files(self, result: ValidationResult):
        """Validate that required metadata files exist"""
        required_files = [
            self.meta_dir / "file_manifest.json",
            self.meta_dir / "conversion_report.json",
            self.meta_dir / "handlers.json"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                result.add_error(f"Required metadata file missing: {file_path}")
            elif not file_path.is_file():
                result.add_error(f"Required metadata path is not a file: {file_path}")
    
    def _validate_file_manifest(self, result: ValidationResult):
        """Validate file manifest structure and content"""
        manifest_file = self.meta_dir / "file_manifest.json"
        if not manifest_file.exists():
            result.add_error("File manifest not found")
            return
        
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            if not isinstance(manifest_data, list):
                result.add_error("File manifest is not a list")
                return
            
            # Validate each entry
            for i, entry in enumerate(manifest_data):
                if not isinstance(entry, dict):
                    result.add_error(f"File manifest entry {i} is not a dictionary")
                    continue
                
                required_fields = ['file', 'type', 'handler', 'size_kb', 'hash', 'last_modified', 'status']
                for field in required_fields:
                    if field not in entry:
                        result.add_error(f"File manifest entry {i} missing required field: {field}")
                
                # Validate status values
                valid_statuses = ['pending', 'converted', 'failed', 'skipped']
                if entry.get('status') not in valid_statuses:
                    result.add_error(f"File manifest entry {i} has invalid status: {entry.get('status')}")
        
        except json.JSONDecodeError as e:
            result.add_error(f"File manifest is not valid JSON: {str(e)}")
        except Exception as e:
            result.add_error(f"Error validating file manifest: {str(e)}")
    
    def _validate_normalized_structure(self, result: ValidationResult):
        """Validate normalized output directory structure"""
        if not self.normalized_dir.exists():
            return  # Already validated in required directories
        
        # Check for expected subdirectories based on file types
        expected_dirs = ['text', 'docs', 'data', 'diagrams', 'tickets']
        found_dirs = [d.name for d in self.normalized_dir.iterdir() if d.is_dir()]
        
        # Log info about structure
        result.add_metric('normalized_subdirectories', found_dirs)
        result.add_metric('expected_subdirectories', expected_dirs)
    
    def _validate_conversion_coverage(self, result: ValidationResult):
        """Validate conversion coverage meets quality thresholds"""
        manifest_file = self.meta_dir / "file_manifest.json"
        if not manifest_file.exists():
            return
        
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            total_files = len(manifest_data)
            if total_files == 0:
                result.add_warning("No files found in manifest")
                return
            
            # Count statuses
            converted = sum(1 for entry in manifest_data if entry.get('status') == 'converted')
            failed = sum(1 for entry in manifest_data if entry.get('status') == 'failed')
            skipped = sum(1 for entry in manifest_data if entry.get('status') == 'skipped')
            
            # Calculate coverage
            coverage_percentage = (converted / total_files) * 100
            result.add_metric('total_files', total_files)
            result.add_metric('converted_files', converted)
            result.add_metric('failed_files', failed)
            result.add_metric('skipped_files', skipped)
            result.add_metric('coverage_percentage', round(coverage_percentage, 2))
            
            # Validate coverage thresholds
            if coverage_percentage < 95.0:
                result.add_warning(f"Low conversion coverage: {coverage_percentage:.1f}%")
            elif coverage_percentage < 100.0:
                result.add_warning(f"Incomplete conversion coverage: {coverage_percentage:.1f}%")
            else:
                result.add_metric('coverage_status', 'excellent')
            
            # Validate failure rate
            failure_rate = (failed / total_files) * 100
            if failure_rate > 5.0:
                result.add_error(f"High failure rate: {failure_rate:.1f}%")
            elif failure_rate > 0:
                result.add_warning(f"Some files failed to convert: {failure_rate:.1f}%")
        
        except Exception as e:
            result.add_error(f"Error validating conversion coverage: {str(e)}")
    
    def _validate_file_integrity(self, result: ValidationResult):
        """Validate integrity of converted files"""
        # This would check file hashes, sizes, and basic content validity
        # For now, we'll just check that converted files exist
        manifest_file = self.meta_dir / "file_manifest.json"
        if not manifest_file.exists():
            return
        
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            converted_files = [entry for entry in manifest_data if entry.get('status') == 'converted']
            missing_output_files = []
            
            for entry in converted_files:
                output_file = entry.get('output_file')
                if output_file:
                    full_output_path = self.normalized_dir / output_file
                    if not full_output_path.exists():
                        missing_output_files.append(output_file)
            
            if missing_output_files:
                result.add_error(f"{len(missing_output_files)} converted files missing from output")
                result.add_metric('missing_output_files', missing_output_files[:10])  # Limit to first 10
                if len(missing_output_files) > 10:
                    result.add_metric('additional_missing_files', len(missing_output_files) - 10)
        
        except Exception as e:
            result.add_error(f"Error validating file integrity: {str(e)}")
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive validation report
        
        Returns:
            Dictionary with validation report data
        """
        logger.info("📄 Generating validation report...")
        
        # Run validation if not already done
        if not self.results:
            self.validate_preprocessing()
        
        # Compile overall results
        passed_validations = sum(1 for result in self.results if result.passed)
        total_validations = len(self.results)
        overall_passed = passed_validations == total_validations
        
        report = {
            'generated_at': datetime.now(timezone.utc).isoformat() + 'Z',
            'repository': str(self.root_path),
            'output_directory': str(self.output_dir),
            'overall_status': 'passed' if overall_passed else 'failed',
            'validations_run': total_validations,
            'validations_passed': passed_validations,
            'validations_failed': total_validations - passed_validations,
            'results': [result.to_dict() for result in self.results]
        }
        
        # Write report to file
        report_file = self.meta_dir / "validation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Validation report written to {report_file}")
        return report
    
    def get_quality_score(self) -> float:
        """
        Calculate overall quality score based on validation results
        
        Returns:
            Quality score from 0.0 to 100.0
        """
        if not self.results:
            self.validate_preprocessing()
        
        # Simple scoring: 100 if all passed, 0 if any failed
        passed_validations = sum(1 for result in self.results if result.passed)
        total_validations = len(self.results)
        
        if total_validations == 0:
            return 100.0
        
        return (passed_validations / total_validations) * 100.0


def main():
    """Main function for running validation"""
    import argparse
    parser = argparse.ArgumentParser(description='Validate AppDocU Preprocessing Results')
    parser.add_argument('--path', required=True, help='Root path of repository that was processed')
    parser.add_argument('--output', required=True, help='Output directory with preprocessing results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run validation
    root_path = Path(args.path)
    output_dir = Path(args.output)
    
    validator = PreprocessorValidator(root_path, output_dir)
    validation_result = validator.validate_preprocessing()
    report = validator.generate_validation_report()
    quality_score = validator.get_quality_score()
    
    # Print summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"Repository: {root_path}")
    print(f"Output directory: {output_dir}")
    print(f"Overall status: {report['overall_status']}")
    print(f"Quality score: {quality_score:.1f}/100.0")
    print(f"Validations run: {report['validations_run']}")
    print(f"Validations passed: {report['validations_passed']}")
    print(f"Validations failed: {report['validations_failed']}")
    print("="*60)
    
    if validation_result.passed:
        print("✅ All validations passed!")
    else:
        print("❌ Some validations failed. Check validation_report.json for details.")
    
    return 0 if validation_result.passed else 1


if __name__ == '__main__':
    exit(main())
