# AppDocU Preprocessor Optimization Tasks

This document outlines the detailed tasks for optimizing the AppDocU preprocessor based on the identified requirements for modularization, performance, and maintainability.

## Sprint 1: Modularize Converters & Consolidate Schemas

### Task 1.1: Create Base Converter Class
- [ ] Create `appdocu_preprocessor/converters/base_converter.py`
- [ ] Define abstract base class with common functionality:
  - File hash calculation
  - Output directory creation
  - Metadata handling
  - Error handling and logging
  - Common file operations
- [ ] Add abstract methods for core conversion logic
- [ ] Implement common utility methods

### Task 1.2: Refactor DOCX Converter
- [ ] Update `appdocu_preprocessor/converters/docx_to_md.py` to inherit from BaseConverter
- [ ] Fix syntax errors in existing code
- [ ] Move common functionality to base class
- [ ] Implement only DOCX-specific conversion logic
- [ ] Add proper error handling and logging

### Task 1.3: Refactor XLSX Converter
- [ ] Update `appdocu_preprocessor/converters/xlsx_to_csv.py` to inherit from BaseConverter
- [ ] Move common functionality to base class
- [ ] Implement only XLSX-specific conversion logic
- [ ] Add proper error handling and logging

### Task 1.4: Refactor Visio Converter
- [ ] Update `appdocu_preprocessor/converters/visio_to_json.py` to inherit from BaseConverter
- [ ] Move common functionality to base class
- [ ] Implement only Visio-specific conversion logic
- [ ] Add proper error handling and logging

### Task 1.5: Refactor PDF Converter
- [ ] Update `appdocu_preprocessor/converters/pdf_to_md.py` to inherit from BaseConverter
- [ ] Fix syntax errors in existing code
- [ ] Move common functionality to base class
- [ ] Implement only PDF-specific conversion logic
- [ ] Add proper error handling and logging

### Task 1.6: Refactor PPTX Converter
- [ ] Update `appdocu_preprocessor/converters/pptx_to_md.py` to inherit from BaseConverter
- [ ] Move common functionality to base class
- [ ] Implement only PPTX-specific conversion logic
- [ ] Add proper error handling and logging

### Task 1.7: Consolidate Schemas
- [ ] Create `appdocu_preprocessor/schemas/base.schema.json` with common metadata fields
- [ ] Update `normalize.index.schema.json` to use composition/inheritance
- [ ] Create specific schema extensions for each converter type
- [ ] Add schema validation utilities
- [ ] Update normalize.py to use schema validation

## Sprint 2: Prioritize Core File Types

### Task 2.1: Focus on Core Converters
- [ ] Mark DOCX, XLSX, Visio as primary converters
- [ ] Create optional module loading for secondary types (PDF, PPTX)
- [ ] Add configuration to enable/disable converter types
- [ ] Update requirements.txt to make optional dependencies optional

### Task 2.2: Language Handler Optimization (if applicable)
- [ ] Identify language-specific handlers in the codebase
- [ ] Create generic fallback handler
- [ ] Prioritize major languages (Python, C#, JavaScript, SQL)

## Sprint 3: Template and Prompt Refactoring

### Task 3.1: Extract Common Template Sections
- [ ] Analyze existing templates in `appdoc.templates/`
- [ ] Create shared header/partials for common sections
- [ ] Implement template composition system
- [ ] Add style guide for template consistency

### Task 3.2: Prompt Template Optimization
- [ ] Extract common prompt sections
- [ ] Create template partials for "Role", "Goal", "Inputs" sections
- [ ] Add prompt validation and linting
- [ ] Update existing prompts to use shared components

## Sprint 4: Performance & Scale Guardrails

### Task 4.1: Implement Caching System
- [ ] Add file change detection using hash comparison
- [ ] Skip conversion if file hasn't changed
- [ ] Implement cache invalidation logic
- [ ] Add cache configuration options

### Task 4.2: Batch Processing for Large Repositories
- [ ] Implement streaming file list processing
- [ ] Add memory usage monitoring
- [ ] Batch processing for large codebases
- [ ] Progress tracking and reporting

### Task 4.3: Cleanup and Archive System
- [ ] Create cleanup script for old normalized outputs
- [ ] Add archive functionality for older versions
- [ ] Implement pruning based on age/frequency
- [ ] Add cleanup scheduling options

### Task 4.4: Warnings-Only Mode
- [ ] Add configuration for different logging levels
- [ ] Implement warnings-only mode
- [ ] Add error recovery and graceful degradation
- [ ] Update normalize.py with new configuration options

## Sprint 5: Documentation and Testing

### Task 5.1: Architectural Decision Records (ADRs)
- [ ] Create `docs/adr/` directory
- [ ] Document modular converter architecture decision
- [ ] Document file type prioritization strategy
- [ ] Document performance optimization decisions

### Task 5.2: Developer Documentation
- [ ] Update README with new architecture
- [ ] Create "How to add a new converter" guide
- [ ] Create "How to add a new language handler" guide
- [ ] Add examples folder with sample outputs

### Task 5.3: Unit Testing
- [ ] Add unit tests for BaseConverter class
- [ ] Add tests for each specific converter
- [ ] Add tests for schema validation
- [ ] Add integration tests for the pipeline
- [ ] Add tests for caching functionality

### Task 5.4: VS Code Integration
- [ ] Update tasks.json with new development tasks
- [ ] Add launch configurations for testing
- [ ] Add debugging configurations
- [ ] Add code snippets for converter development

## Sprint 6: Code Quality and Maintenance

### Task 6.1: Consistent Naming and Structure
- [ ] Normalize folder structure and naming conventions
- [ ] Update versioning scheme (e.g., normalize-v1, behavior-graph-v1)
- [ ] Add consistent error handling across all modules
- [ ] Implement proper logging throughout the system

### Task 6.2: Error Handling and Recovery
- [ ] Add comprehensive exception handling in all converters
- [ ] Implement graceful degradation for partial failures
- [ ] Add retry mechanisms for transient failures
- [ ] Create error reporting and monitoring

### Task 6.3: Code Linting and Style
- [ ] Add linting configuration (flake8, mypy, black)
- [ ] Create pre-commit hooks
- [ ] Add style guide for Python code
- [ ] Add documentation standards

## Sprint 7: Advanced Features

### Task 7.1: Performance Monitoring
- [ ] Add performance metrics collection
- [ ] Add conversion time tracking
- [ ] Add memory usage monitoring
- [ ] Create performance reporting

### Task 7.2: Configuration Management
- [ ] Create comprehensive configuration system
- [ ] Add command-line option parsing
- [ ] Add configuration validation
- [ ] Create configuration examples

## Sprint 8: Final Integration and Testing

### Task 8.1: Integration Testing
- [ ] Test complete workflow with all converter types
- [ ] Test error scenarios and recovery
- [ ] Test performance with large repositories
- [ ] Test memory usage optimization

### Task 8.2: User Acceptance Testing
- [ ] Test with real-world examples
- [ ] Validate output quality
- [ ] Verify performance improvements
- [ ] Document any issues and fixes

### Task 8.3: Documentation Finalization
- [ ] Complete all documentation updates
- [ ] Create migration guide for existing users
- [ ] Update all examples and tutorials
- [ ] Create troubleshooting guide

## Priority Order for Implementation:

**Phase 1 (Immediate)**: Tasks 1.1 - 1.7 (Sprint 1)
**Phase 2 (High Priority)**: Tasks 2.1, 4.1, 5.1, 5.2 (Sprints 2, 4, 5)
**Phase 3 (Medium Priority)**: Tasks 3.1, 3.2, 6.1, 6.2 (Sprints 3, 6)
**Phase 4 (Lower Priority)**: Tasks 4.2, 4.3, 4.4, 7.1, 7.2 (Sprints 4, 7)
**Phase 5 (Final)**: Tasks 8.1, 8.2, 8.3 (Sprint 8)

Each phase builds upon the previous one, with the most critical architectural changes implemented first to provide the foundation for subsequent improvements.
