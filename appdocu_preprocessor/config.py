"""
Configuration Management System for AppDocU Preprocessor
Centralized configuration management with validation and environment support

This module provides comprehensive configuration management for the AppDocU preprocessor system,
handling default values, environment variable overrides, configuration validation, and
centralized access to system settings. It enables flexible deployment configurations while
maintaining system reliability and consistency across different environments.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from datetime import datetime


class LogLevel(Enum):
    """Enumeration for log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class PreprocessorConfig:
    """Configuration data class for AppDocU Preprocessor"""
    # Directory and file settings
    output_directory: str = "_normalized"
    cache_directory: str = "_normalized/cache"
    meta_directory: str = "_normalized/.meta"
    normalized_directory: str = "_normalized/normalized"
    text_directory: str = "_normalized/normalized/text"
    docs_directory: str = "_normalized/normalized/docs"
    data_directory: str = "_normalized/normalized/data"
    diagrams_directory: str = "_normalized/normalized/diagrams"
    tickets_directory: str = "_normalized/normalized/tickets"
    
    # Caching settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 86400 # 24 hours
    cache_compress: bool = True
    cache_max_size_mb: int = 1000  # 1GB
    cache_cleanup_on_startup: bool = True
    
    # Processing settings
    max_file_size_mb: int = 50  # 50MB max file size
    max_concurrent_processes: int = 4
    timeout_seconds: int = 300  # 5 minutes
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    skip_hidden_directories: bool = True
    skip_directories: list = field(default_factory=lambda: ['.git', '__pycache__', 'node_modules', '.vscode', '.idea', 'documentation'])
    skip_extensions: list = field(default_factory=lambda: ['.tmp', '.log', '.bak', '.swp'])
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "_normalized/appdoc.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_max_size_mb: int = 10  # 10MB max log file size
    log_backup_count: int = 5
    log_to_console: bool = True
    log_to_file: bool = True
    
    # Validation settings
    validate_schemas: bool = True
    validate_file_integrity: bool = True
    validate_conversion_coverage: bool = True
    min_conversion_coverage: float = 90.0  # 90% minimum coverage
    max_failure_rate: float = 10.0  # 10% maximum failure rate
    
    # Performance settings
    memory_limit_mb: int = 1024  # 1GB memory limit
    performance_monitoring: bool = False
    performance_sample_rate: float = 0.1  # 10% sample rate
    performance_report_interval: int = 300  # 5 minutes
    
    # Feature flags
    enable_sql_analysis: bool = True
    enable_docx_conversion: bool = True
    enable_pdf_extraction: bool = True
    enable_visio_conversion: bool = True
    enable_performance_tracking: bool = False
    enable_detailed_metrics: bool = False


class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass


class ConfigManager:
    """Centralized configuration manager with validation and environment support"""
    
    def __init__(self, config_file: Optional[str] = None, env_prefix: str = "APPDOC"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file (optional)
            env_prefix: Environment variable prefix (default: APPDOC)
        """
        self.env_prefix = env_prefix
        self.config_file = Path(config_file) if config_file else None
        self._config = PreprocessorConfig()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self._load_configuration()
        self._validate_configuration()
        self._setup_logging()
    
    def _load_configuration(self):
        """Load configuration from file and environment variables"""
        # Start with default configuration
        config_dict = asdict(self._config)
        
        # Load from file if provided
        if self.config_file and self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                config_dict.update(file_config)
            except json.JSONDecodeError as e:
                raise ConfigurationError(f"Invalid JSON in config file {self.config_file}: {e}")
            except Exception as e:
                raise ConfigurationError(f"Error reading config file {self.config_file}: {e}")
        
        # Override with environment variables
        env_config = self._load_from_environment()
        config_dict.update(env_config)
        
        # Update configuration
        for key, value in config_dict.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        env_config = {}
        prefix = f"{self.env_prefix}_"
        
        for key in asdict(self._config).keys():
            env_key = f"{prefix}{key.upper()}"
            env_value = os.getenv(env_key)
            
            if env_value is not None:
                # Convert environment variable to appropriate type
                current_value = getattr(self._config, key)
                env_config[key] = self._convert_env_value(env_value, current_value)
        
        return env_config
    
    def _convert_env_value(self, env_value: str, current_value: Any) -> Any:
        """Convert environment variable string to appropriate type"""
        if isinstance(current_value, bool):
            return env_value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(current_value, int):
            return int(env_value)
        elif isinstance(current_value, float):
            return float(env_value)
        elif isinstance(current_value, list):
            # Assume comma-separated values for lists
            return [item.strip() for item in env_value.split(',')]
        elif isinstance(current_value, str):
            return env_value
        else:
            # For complex types, try JSON parsing
            try:
                return json.loads(env_value)
            except json.JSONDecodeError:
                return env_value
    
    def _validate_configuration(self):
        """Validate configuration values"""
        errors = []
        
        # Validate output directory settings
        if not self._config.output_directory:
            errors.append("output_directory cannot be empty")
        if not self._config.cache_directory:
            errors.append("cache_directory cannot be empty")
        if not self._config.meta_directory:
            errors.append("meta_directory cannot be empty")
        if not self._config.normalized_directory:
            errors.append("normalized_directory cannot be empty")
        
        # Validate numeric ranges
        if self._config.max_file_size_mb <= 0:
            errors.append("max_file_size_mb must be positive")
        if self._config.max_concurrent_processes <= 0:
            errors.append("max_concurrent_processes must be positive")
        if self._config.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")
        if self._config.retry_attempts < 0:
            errors.append("retry_attempts cannot be negative")
        if self._config.retry_delay_seconds < 0:
            errors.append("retry_delay_seconds cannot be negative")
        if self._config.cache_ttl_seconds <= 0:
            errors.append("cache_ttl_seconds must be positive")
        if self._config.cache_max_size_mb <= 0:
            errors.append("cache_max_size_mb must be positive")
        if self._config.min_conversion_coverage < 0 or self._config.min_conversion_coverage > 100:
            errors.append("min_conversion_coverage must be between 0 and 100")
        if self._config.max_failure_rate < 0 or self._config.max_failure_rate > 100:
            errors.append("max_failure_rate must be between 0 and 100")
        if self._config.memory_limit_mb <= 0:
            errors.append("memory_limit_mb must be positive")
        if self._config.performance_sample_rate < 0 or self._config.performance_sample_rate > 1:
            errors.append("performance_sample_rate must be between 0 and 1")
        if self._config.performance_report_interval <= 0:
            errors.append("performance_report_interval must be positive")
        if self._config.log_max_size_mb <= 0:
            errors.append("log_max_size_mb must be positive")
        if self._config.log_backup_count < 0:
            errors.append("log_backup_count cannot be negative")
        
        # Validate log level
        try:
            LogLevel(self._config.log_level.upper())
        except ValueError:
            errors.append(f"Invalid log_level: {self._config.log_level}. Must be one of: {list(LogLevel.__members__)}")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def _setup_logging(self):
        """Setup logging based on configuration - DISABLED to prevent hangs"""
        # Convert string log level to enum
        try:
            log_level = LogLevel(self._config.log_level.upper()).value
        except ValueError:
            log_level = "INFO"
            # Use a simple logger for warnings during initialization
            print(f"Warning: Invalid log level '{self._config.log_level}', defaulting to INFO")
        
        # SKIP logging configuration to prevent hangs
        # This was causing the system to hang during import
        # logging configuration is now handled externally
        pass  # Do nothing - logging setup disabled
    
    def _get_log_handlers(self) -> list:
        """Get logging handlers based on configuration"""
        handlers = []
        
        if self._config.log_to_console:
            handlers.append(logging.StreamHandler())
        
        if self._config.log_to_file and self._config.log_file:
            from logging.handlers import RotatingFileHandler
            import os
            from pathlib import Path
            
            try:
                # Create directory for log file if it doesn't exist
                log_path = Path(self._config.log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                handler = RotatingFileHandler(
                    self._config.log_file,
                    maxBytes=self._config.log_max_size_mb * 1024 * 1024,
                    backupCount=self._config.log_backup_count,
                    encoding='utf-8'
                )
                handlers.append(handler)
            except Exception as e:
                # If file handler creation fails, log to console only
                print(f"Warning: Could not create file log handler: {e}")
                self.logger.warning(f"Could not create file log handler: {e}")
        
        return handlers
    
    def get_config(self) -> PreprocessorConfig:
        """Get the current configuration"""
        return self._config
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return asdict(self._config)
    
    def save_config(self, file_path: Union[str, Path]):
        """Save current configuration to file"""
        config_dict = self.get_config_dict()
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def update_config(self, **kwargs):
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                raise ConfigurationError(f"Unknown configuration key: {key}")
        
        # Re-validate after update
        self._validate_configuration()
        self._setup_logging()
    
    def get_output_path(self, base_path: Path) -> Path:
        """Get output directory path relative to base path"""
        return base_path / self._config.output_directory
    
    def get_cache_path(self, base_path: Path) -> Path:
        """Get cache directory path relative to base path"""
        return base_path / self._config.cache_directory
    
    def get_meta_path(self, base_path: Path) -> Path:
        """Get meta directory path relative to base path"""
        return base_path / self._config.meta_directory
    
    def get_normalized_path(self, base_path: Path) -> Path:
        """Get normalized directory path relative to base path"""
        return base_path / self._config.normalized_directory
    
    def is_directory_skipped(self, dir_path: Path) -> bool:
        """Check if directory should be skipped based on configuration"""
        dir_name = dir_path.name.lower()
        return dir_name in [d.lower() for d in self._config.skip_directories] or dir_name.startswith('.')
    
    def is_file_skipped(self, file_path: Path) -> bool:
        """Check if file should be skipped based on configuration"""
        extension = file_path.suffix.lower()
        return extension in [ext.lower() for ext in self._config.skip_extensions]
    
    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes"""
        return self._config.max_file_size_mb * 1024 * 1024


def get_global_config() -> ConfigManager:
    """Get global configuration manager instance"""
    if not hasattr(get_global_config, '_instance'):
        config_file = os.getenv('APPDOC_CONFIG_FILE')
        get_global_config._instance = ConfigManager(config_file)
    return get_global_config._instance


def reset_global_config():
    """Reset global configuration manager (for testing)"""
    if hasattr(get_global_config, '_instance'):
        delattr(get_global_config, '_instance')


# Example usage and default configuration
if __name__ == "__main__":
    # Create example configuration file
    example_config = PreprocessorConfig()
    example_config_dict = asdict(example_config)
    
    # Save example configuration
    example_file = Path("appdoc_config_example.json")
    with open(example_file, 'w', encoding='utf-8') as f:
        json.dump(example_config_dict, f, indent=2, ensure_ascii=False)
    
    print(f"Example configuration saved to {example_file}")
    print("Environment variable examples:")
    print(f"APPDOC_LOG_LEVEL=DEBUG")
    print(f"APPDOC_MAX_FILE_SIZE_MB=100")
    print(f"APPDOC_CACHE_ENABLED=true")
    print(f"APPDOC_OUTPUT_DIRECTORY=_appdoc_output")
