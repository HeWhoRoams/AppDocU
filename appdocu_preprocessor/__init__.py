"""
AppDocU Preprocessor Package
Entry point and main exports for the preprocessing system
"""
import logging
from pathlib import Path
from typing import Optional

from appdocu_preprocessor.workflow import PreprocessorWorkflow
from appdocu_preprocessor.validation import PreprocessorValidator
from appdocu_preprocessor.file_enumerator import FileEnumerator, FileInfo, FileType

# Configure package-level logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "1.0.0"
__author__ = "AppDocU Team"
__email__ = "support@appdocu.org"


class AppDocUPreprocessor:
    """Main entry point for the AppDocU Preprocessor system"""
    
    def __init__(self, root_path: str, output_dir: Optional[str] = None):
        """
        Initialize the preprocessor
        
        Args:
            root_path: Root path of repository to process
            output_dir: Output directory (defaults to root_path/_normalized)
        """
        self.root_path = Path(root_path)
        self.output_dir = Path(output_dir) if output_dir else self.root_path / "_normalized"
        self.workflow = PreprocessorWorkflow(self.root_path, self.output_dir)
        self.validator = PreprocessorValidator(self.root_path, self.output_dir)
        self.enumerator = FileEnumerator(self.root_path)
    
    def run_preprocessing(self, validate: bool = True) -> dict:
        """
        Run the complete preprocessing workflow
        
        Args:
            validate: Whether to run validation after preprocessing
            
        Returns:
            Dictionary with workflow results
        """
        # Run preprocessing workflow
        workflow_result = self.workflow.run_workflow()
        
        if not workflow_result['status'] == 'completed':
            return workflow_result
        
        # Run validation if requested
        if validate:
            validation_result = self.validator.validate_preprocessing()
            validation_report = self.validator.generate_validation_report()
            quality_score = self.validator.get_quality_score()
            
            # Add validation results to workflow result
            workflow_result['validation'] = {
                'passed': validation_result.passed,
                'quality_score': quality_score,
                'report': validation_report
            }
        
        return workflow_result
    
    def get_file_manifest(self) -> list:
        """
        Get current file manifest
        
        Returns:
            List of file information
        """
        return self.enumerator.enumerate_files()
    
    def get_quality_metrics(self) -> dict:
        """
        Get quality metrics for the preprocessing
        
        Returns:
            Dictionary with quality metrics
        """
        return {
            'conversion_rate': self._calculate_conversion_rate(),
            'coverage_percentage': self._calculate_coverage_percentage(),
            'total_files': self._get_total_files(),
            'successful_conversions': self._get_successful_conversions()
        }
    
    def _calculate_conversion_rate(self) -> float:
        """Calculate conversion success rate"""
        # Implementation would read from conversion report
        return 100.0  # Placeholder
    
    def _calculate_coverage_percentage(self) -> float:
        """Calculate file coverage percentage"""
        # Implementation would read from file manifest
        return 100.0  # Placeholder
    
    def _get_total_files(self) -> int:
        """Get total number of files processed"""
        # Implementation would read from file manifest
        return 0  # Placeholder
    
    def _get_successful_conversions(self) -> int:
        """Get number of successful conversions"""
        # Implementation would read from conversion report
        return 0  # Placeholder


# Convenience functions for common use cases
def preprocess_repository(root_path: str, output_dir: Optional[str] = None, 
                          validate: bool = True) -> dict:
    """
    Convenience function to preprocess a repository
    
    Args:
        root_path: Root path of repository to process
        output_dir: Output directory (defaults to root_path/_normalized)
        validate: Whether to run validation after preprocessing
        
    Returns:
        Dictionary with preprocessing results
    """
    preprocessor = AppDocUPreprocessor(root_path, output_dir)
    return preprocessor.run_preprocessing(validate=validate)


def get_file_manifest(root_path: str) -> list:
    """
    Convenience function to get file manifest for a repository
    
    Args:
        root_path: Root path of repository to analyze
        
    Returns:
        List of file information
    """
    enumerator = FileEnumerator(Path(root_path))
    return enumerator.enumerate_files()


# Package exports
__all__ = [
    'AppDocUPreprocessor',
    'PreprocessorWorkflow',
    'PreprocessorValidator',
    'FileEnumerator',
    'FileInfo',
    'FileType',
    'preprocess_repository',
    'get_file_manifest'
]
