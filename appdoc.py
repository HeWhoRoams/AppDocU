#!/usr/bin/env python3
"""
AppDocU Main Orchestrator
Main entry point for the AppDocU documentation automation system
Implements the 3-pass workflow: Discovery → Enrichment → Cognitive Audit
"""
import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to the path to import modules
sys.path.insert(0, str(Path(__file__).parent))

# Import modules only when needed to avoid config initialization issues
# from appdocu_preprocessor import preprocess_repository
# from appdocu_preprocessor.workflow import PreprocessorWorkflow
# from appdocu_preprocessor.validation import PreprocessorValidator
# from appdocu_preprocessor.config import get_global_config, ConfigManager


class AppDocUOrchestrator:
    """Main orchestrator for the AppDocU 3-pass workflow"""
    
    def __init__(self, target_path: str, output_dir: Optional[str] = None):
        """
        Initialize the orchestrator
        
        Args:
            target_path: Path to the codebase to document
            output_dir: Output directory (defaults to target_path/_normalized)
        """
        self.target_path = Path(target_path)
        self.output_dir = Path(output_dir) if output_dir else self.target_path / "_normalized"
        self.meta_dir = self.output_dir / ".meta"
        
        # Create metadata directory
        self.meta_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize workflow components (lazy import)
        self.workflow = None
        self.validator = None
        
        self.logger.info(f"AppDocU Orchestrator initialized")
        self.logger.info(f"Target: {self.target_path}")
        self.logger.info(f"Output: {self.output_dir}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.meta_dir / "appdoc.log"
        
        # Remove any existing handlers to avoid duplicates
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        logging.basicConfig(
            level=logging.DEBUG,  # Changed to DEBUG for more verbose output
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ],
            force=True  # This ensures the configuration is applied even if already set
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_pass_1_discovery(self) -> Dict[str, Any]:
        """
        Pass 1: Discovery
        - Analyze codebase structure
        - Discover runtime behavior through IO operations
        - Generate behavior-graph.json and system-integrations.json
        - Extract docx evidence
        
        Returns:
            Dictionary with pass 1 results
        """
        self.logger.info("🚀 Starting Pass 1: Discovery")
        
        try:
            # Import required modules locally to avoid config initialization issues
            from appdocu_preprocessor import preprocess_repository
            from appdocu_preprocessor.workflow import PreprocessorWorkflow
            from appdocu_preprocessor.validation import PreprocessorValidator
            
            # Initialize workflow components if not already done
            if self.workflow is None:
                self.workflow = PreprocessorWorkflow(self.target_path, self.output_dir)
            if self.validator is None:
                self.validator = PreprocessorValidator(self.target_path, self.output_dir)
            
            # Run preprocessing first (normalize binary documents)
            self.logger.info("📋 Preprocessing binary documents...")
            preprocessing_result = preprocess_repository(
                str(self.target_path), 
                str(self.output_dir),
                validate=True
            )
            
            if preprocessing_result['status'] != 'completed':
                self.logger.error(f"Preprocessing failed: {preprocessing_result.get('error')}")
                return {
                    'status': 'failed',
                    'error': f"Preprocessing failed: {preprocessing_result.get('error')}",
                    'preprocessing_result': preprocessing_result
                }
            
            # Generate discovery artifacts from preprocessing results
            discovery_results = self._generate_discovery_artifacts_from_analysis(preprocessing_result)
            
            result = {
                'status': 'completed',
                'generated_at': datetime.now().isoformat(),
                'preprocessing': preprocessing_result,
                'discovery': discovery_results,
                'output_files': {
                    'behavior_graph': str(self.meta_dir / 'behavior-graph.json'),
                    'system_integrations': str(self.meta_dir / 'system-integrations.json'),
                    'docx_evidence': str(self.meta_dir / 'docx-evidence.json')
                }
            }
            
            self.logger.info("✅ Pass 1: Discovery completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Pass 1: Discovery failed - {str(e)}", exc_info=True)
            return {
                'status': 'failed',
                'error': str(e),
                'traceback': str(e.__traceback__) if e.__traceback__ else None
            }
    
    def _generate_discovery_artifacts_from_analysis(self, preprocessing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate discovery artifacts from preprocessing analysis results"""
        self.logger.info("Generating discovery artifacts from analysis...")
        
        # Read the file manifest to understand the codebase structure
        manifest_file = self.output_dir / ".meta" / "file_manifest.json"
        file_manifest = []
        if manifest_file.exists():
            with open(manifest_file, 'r', encoding='utf-8') as f:
                file_manifest = json.load(f)
            self.logger.info(f"Found {len(file_manifest)} files in manifest for analysis")
        else:
            self.logger.warning("File manifest not found, using empty analysis")
        
        # Analyze code files to extract components and relationships
        code_files = [f for f in file_manifest if f.get('type') == 'code']
        docx_files = [f for f in file_manifest if f.get('type') == 'docx']
        other_files = [f for f in file_manifest if f.get('type') not in ['code', 'docx']]
        
        # Generate behavior graph from code analysis
        behavior_graph = self._analyze_code_structure(code_files)
        
        # Generate system integrations from file analysis
        system_integrations = self._analyze_system_integrations(code_files, other_files)
        
        # Generate docx evidence from document files
        docx_evidence = self._analyze_documentation(docx_files)
        
        # Write discovery files
        behavior_graph_file = self.meta_dir / 'behavior-graph.json'
        with open(behavior_graph_file, 'w', encoding='utf-8') as f:
            json.dump(behavior_graph, f, indent=2, ensure_ascii=False)
        
        system_integrations_file = self.meta_dir / 'system-integrations.json'
        with open(system_integrations_file, 'w', encoding='utf-8') as f:
            json.dump(system_integrations, f, indent=2, ensure_ascii=False)
        
        docx_evidence_file = self.meta_dir / 'docx-evidence.json'
        with open(docx_evidence_file, 'w', encoding='utf-8') as f:
            json.dump(docx_evidence, f, indent=2, ensure_ascii=False)
        
        return {
            'behavior_graph_generated': True,
            'system_integrations_generated': True,
            'docx_evidence_generated': True,
            'files_created': [
                str(behavior_graph_file),
                str(system_integrations_file),
                str(docx_evidence_file)
            ],
            'analysis_summary': {
                'total_files_analyzed': len(file_manifest),
                'code_files': len(code_files),
                'docx_files': len(docx_files),
                'other_files': len(other_files)
            }
        }

    def _analyze_code_structure(self, code_files: list) -> dict:
        """Analyze code files to extract structure and relationships"""
        behavior_graph = {
            'generated_at': datetime.now().isoformat(),
            'nodes': [],
            'edges': [],
            'components': {},
            'entry_points': [],
            'data_flows': [],
            'code_files_analyzed': len(code_files)
        }
        
        # Extract file-level information
        for file_info in code_files:
            file_path = file_info.get('file', '')
            file_size = file_info.get('size_kb', 0)
            file_hash = file_info.get('hash', '')
            status = file_info.get('status', 'unknown')
            
            # Create node for the file
            node = {
                'id': file_hash[:8] if file_hash else f"file_{len(behavior_graph['nodes'])}",
                'name': Path(file_path).name,
                'path': file_path,
                'type': 'file',
                'size_kb': file_size,
                'status': status,
                'extension': Path(file_path).suffix
            }
            behavior_graph['nodes'].append(node)
            behavior_graph['components'][file_path] = node
            
            # Identify potential entry points based on file names and extensions
            if any(keyword in file_path.lower() for keyword in ['main', 'index', 'app', 'entry', 'start']):
                behavior_graph['entry_points'].append(file_path)
        
        # Add basic statistics
        behavior_graph['statistics'] = {
            'total_nodes': len(behavior_graph['nodes']),
            'total_components': len(behavior_graph['components']),
            'entry_points_count': len(behavior_graph['entry_points'])
        }
        
        return behavior_graph

    def _analyze_system_integrations(self, code_files: list, other_files: list) -> dict:
        """Analyze files to identify system integrations"""
        system_integrations = {
            'generated_at': datetime.now().isoformat(),
            'external_systems': [],
            'database_connections': [],
            'api_endpoints': [],
            'message_queues': [],
            'file_systems': [],
            'integration_points': [],
            'total_integrations': 0
        }
        
        # Look for integration patterns in code files
        integration_keywords = {
            'database': ['db', 'database', 'sql', 'mysql', 'postgres', 'mongodb', 'connection', 'pool'],
            'api': ['api', 'endpoint', 'url', 'http', 'rest', 'graphql', 'client', 'request'],
            'messaging': ['queue', 'message', 'kafka', 'rabbitmq', 'redis', 'pubsub'],
            'external': ['external', 'third-party', 'service', 'integration', 'sdk', 'library']
        }
        
        # Analyze code files for integration patterns
        for file_info in code_files:
            file_path = file_info.get('file', '')
            # For now, we'll add basic integration detection based on file content analysis
            # In a real implementation, this would read and analyze the actual file content
            if any(keyword in file_path.lower() for keyword in integration_keywords['database']):
                db_name = Path(file_path).stem
                if db_name not in system_integrations['database_connections']:
                    system_integrations['database_connections'].append(db_name)
            
            if any(keyword in file_path.lower() for keyword in integration_keywords['api']):
                api_name = Path(file_path).stem
                if api_name not in system_integrations['api_endpoints']:
                    system_integrations['api_endpoints'].append(api_name)
        
        # Add other file types as potential integration points
        for file_info in other_files:
            file_path = file_info.get('file', '')
            file_type = file_info.get('type', '')
            system_integrations['integration_points'].append({
                'path': file_path,
                'type': file_type,
                'size_kb': file_info.get('size_kb', 0)
            })
        
        system_integrations['total_integrations'] = len(system_integrations['integration_points'])
        return system_integrations

    def _analyze_documentation(self, docx_files: list) -> dict:
        """Analyze documentation files to extract evidence"""
        docx_evidence = {
            'generated_at': datetime.now().isoformat(),
            'documents_found': [],
            'evidence_items': [],
            'confidence_scores': {},
            'total_documents': len(docx_files)
        }
        
        # Add document information to evidence
        for file_info in docx_files:
            doc_info = {
                'path': file_info.get('file', ''),
                'size_kb': file_info.get('size_kb', 0),
                'last_modified': file_info.get('last_modified', ''),
                'status': file_info.get('status', 'unknown')
            }
            docx_evidence['documents_found'].append(doc_info)
            docx_evidence['confidence_scores'][file_info.get('file', '')] = 0.8  # Default confidence
        
        return docx_evidence

    def _generate_discovery_artifacts(self) -> Dict[str, Any]:
        """Generate discovery artifacts for Pass 1 (legacy method)"""
        self.logger.info("Generating discovery artifacts...")
        
        # Generate behavior graph (simplified for now)
        behavior_graph = {
            'generated_at': datetime.now().isoformat(),
            'nodes': [],
            'edges': [],
            'components': {},
            'entry_points': [],
            'data_flows': []
        }
        
        # Generate system integrations (simplified for now)
        system_integrations = {
            'generated_at': datetime.now().isoformat(),
            'external_systems': [],
            'database_connections': [],
            'api_endpoints': [],
            'message_queues': [],
            'file_systems': []
        }
        
        # Generate docx evidence (simplified for now)
        docx_evidence = {
            'generated_at': datetime.now().isoformat(),
            'documents_found': [],
            'evidence_items': [],
            'confidence_scores': {}
        }
        
        # Write discovery files
        behavior_graph_file = self.meta_dir / 'behavior-graph.json'
        with open(behavior_graph_file, 'w', encoding='utf-8') as f:
            json.dump(behavior_graph, f, indent=2, ensure_ascii=False)
        
        system_integrations_file = self.meta_dir / 'system-integrations.json'
        with open(system_integrations_file, 'w', encoding='utf-8') as f:
            json.dump(system_integrations, f, indent=2, ensure_ascii=False)
        
        docx_evidence_file = self.meta_dir / 'docx-evidence.json'
        with open(docx_evidence_file, 'w', encoding='utf-8') as f:
            json.dump(docx_evidence, f, indent=2, ensure_ascii=False)
        
        return {
            'behavior_graph_generated': True,
            'system_integrations_generated': True,
            'docx_evidence_generated': True,
            'files_created': [
                str(behavior_graph_file),
                str(system_integrations_file),
                str(docx_evidence_file)
            ]
        }
    
    def run_pass_2_enrichment(self) -> Dict[str, Any]:
        """
        Pass 2: Enrichment
        - Generate human-readable documentation
        - Create architecture.md and logic-and-workflows.md
        - Generate change-impact-map.md
        
        Returns:
            Dictionary with pass 2 results
        """
        self.logger.info("🚀 Starting Pass 2: Enrichment")
        
        try:
            # Generate enrichment artifacts
            enrichment_results = self._generate_enrichment_artifacts()
            
            result = {
                'status': 'completed',
                'generated_at': datetime.now().isoformat(),
                'enrichment': enrichment_results,
                'output_files': {
                    'architecture': str(self.target_path / 'architecture.md'),
                    'logic_workflows': str(self.target_path / 'logic-and-workflows.md'),
                    'change_impact': str(self.target_path / 'change-impact-map.md')
                }
            }
            
            self.logger.info("✅ Pass 2: Enrichment completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Pass 2: Enrichment failed - {str(e)}", exc_info=True)
            return {
                'status': 'failed',
                'error': str(e),
                'traceback': str(e.__traceback__) if e.__traceback__ else None
            }
    
    def _generate_enrichment_artifacts(self) -> Dict[str, Any]:
        """Generate enrichment artifacts for Pass 2"""
        self.logger.info("Generating enrichment artifacts...")
        
        # Generate architecture documentation
        architecture_content = self._generate_architecture_documentation()
        architecture_file = self.target_path / 'architecture.md'
        with open(architecture_file, 'w', encoding='utf-8') as f:
            f.write(architecture_content)
        
        # Generate logic and workflows documentation
        logic_workflows_content = self._generate_logic_workflows_documentation()
        logic_workflows_file = self.target_path / 'logic-and-workflows.md'
        with open(logic_workflows_file, 'w', encoding='utf-8') as f:
            f.write(logic_workflows_content)
        
        # Generate change impact map
        change_impact_content = self._generate_change_impact_map()
        change_impact_file = self.target_path / 'change-impact-map.md'
        with open(change_impact_file, 'w', encoding='utf-8') as f:
            f.write(change_impact_content)
        
        return {
            'architecture_generated': True,
            'logic_workflows_generated': True,
            'change_impact_map_generated': True,
            'files_created': [
                str(architecture_file),
                str(logic_workflows_file),
                str(change_impact_file)
            ]
        }
    
    def _generate_architecture_documentation(self) -> str:
        """Generate architecture documentation template"""
        return f"""# Architecture Documentation

Generated by AppDocU at {datetime.now().isoformat()}

This document provides an overview of the system architecture.

## System Overview
- **Target Path**: {self.target_path}
- **Generated At**: {datetime.now().isoformat()}

## Components
[Architecture components will be generated here based on code analysis]

## Dependencies
[Dependencies will be analyzed and documented here]

## Data Flow
[Data flow patterns will be documented here]

## Integration Points
[External integrations will be documented here]
"""
    
    def _generate_logic_workflows_documentation(self) -> str:
        """Generate logic and workflows documentation template"""
        return f"""# Logic & Workflows Documentation

Generated by AppDocU at {datetime.now().isoformat()}

This document describes the business logic and workflows.

## Business Logic Overview
- **Target Path**: {self.target_path}
- **Generated At**: {datetime.now().isoformat()}

## Workflows
[Business workflows will be documented here based on code analysis]

## Data Processing
[Data processing logic will be documented here]

## Business Rules
[Business rules will be extracted and documented here]
"""
    
    def _generate_change_impact_map(self) -> str:
        """Generate change impact map template"""
        return f"""# Change Impact Map

Generated by AppDocU at {datetime.now().isoformat()}

This document maps the potential impact of changes.

## Change Impact Analysis
- **Target Path**: {self.target_path}
- **Generated At**: {datetime.now().isoformat()}

## Component Dependencies
[Component dependencies and impact relationships will be mapped here]

## Risk Assessment
[Risk levels for different components will be documented here]

## Modification Guidelines
[Guidelines for safely modifying components will be provided here]
"""
    
    def run_pass_3_cognitive_audit(self) -> Dict[str, Any]:
        """
        Pass 3: Cognitive Audit
        - Generate developer-preflight.md and cognitive-audit.md
        - Perform proactive risk assessment
        - Analyze fragility and predicted failure chains
        
        Returns:
            Dictionary with pass 3 results
        """
        self.logger.info("🚀 Starting Pass 3: Cognitive Audit")
        
        try:
            # Generate cognitive audit artifacts
            audit_results = self._generate_cognitive_audit_artifacts()
            
            result = {
                'status': 'completed',
                'generated_at': datetime.now().isoformat(),
                'cognitive_audit': audit_results,
                'output_files': {
                    'developer_preflight': str(self.target_path / 'developer-preflight.md'),
                    'cognitive_audit': str(self.target_path / 'cognitive-audit.md')
                }
            }
            
            self.logger.info("✅ Pass 3: Cognitive Audit completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Pass 3: Cognitive Audit failed - {str(e)}", exc_info=True)
            return {
                'status': 'failed',
                'error': str(e),
                'traceback': str(e.__traceback__) if e.__traceback__ else None
            }
    
    def _generate_cognitive_audit_artifacts(self) -> Dict[str, Any]:
        """Generate cognitive audit artifacts for Pass 3"""
        self.logger.info("Generating cognitive audit artifacts...")
        
        # Generate developer preflight
        preflight_content = self._generate_developer_preflight()
        preflight_file = self.target_path / 'developer-preflight.md'
        with open(preflight_file, 'w', encoding='utf-8') as f:
            f.write(preflight_content)
        
        # Generate cognitive audit
        cognitive_audit_content = self._generate_cognitive_audit()
        cognitive_audit_file = self.target_path / 'cognitive-audit.md'
        with open(cognitive_audit_file, 'w', encoding='utf-8') as f:
            f.write(cognitive_audit_content)
        
        return {
            'developer_preflight_generated': True,
            'cognitive_audit_generated': True,
            'files_created': [
                str(preflight_file),
                str(cognitive_audit_file)
            ]
        }
    
    def _generate_developer_preflight(self) -> str:
        """Generate developer preflight checklist"""
        return f"""# Developer Preflight Checklist

Generated by AppDocU at {datetime.now().isoformat()}

This checklist helps developers understand the system before making changes.

## Pre-Development Checklist
- **Target Path**: {self.target_path}
- **Generated At**: {datetime.now().isoformat()}

### Before You Start
- [ ] Review architecture documentation
- [ ] Understand component dependencies
- [ ] Check change impact map
- [ ] Identify test coverage gaps
- [ ] Review security considerations
- [ ] Verify backup procedures

### Code Modification Guidelines
[Specific guidelines for this codebase will be provided here]

### Testing Requirements
[Testing requirements will be documented here]

### Deployment Considerations
[Deployment considerations will be documented here]
"""
    
    def _generate_cognitive_audit(self) -> str:
        """Generate cognitive audit report"""
        return f"""# Cognitive Audit Report

Generated by AppDocU at {datetime.now().isoformat()}

This report provides a cognitive analysis of the system.

## System Analysis
- **Target Path**: {self.target_path}
- **Generated At**: {datetime.now().isoformat()}

## Risk Assessment
[Risk assessment will be documented here]

## Fragility Analysis
[Fragility analysis will be documented here]

## Predicted Failure Chains
[Predicted failure chains will be documented here]

## Cognitive Load Assessment
[Cognitive load assessment will be documented here]

## Recommendations
[Recommendations for improvement will be provided here]
"""
    
    def run_full_workflow(self) -> Dict[str, Any]:
        """
        Run the complete 3-pass workflow
        
        Returns:
            Dictionary with complete workflow results
        """
        self.logger.info("🚀 Starting Full AppDocU Workflow")
        
        results = {
            'generated_at': datetime.now().isoformat(),
            'target_path': str(self.target_path),
            'output_dir': str(self.output_dir),
            'passes': {}
        }
        
        # Run Pass 1: Discovery
        pass_1_result = self.run_pass_1_discovery()
        results['passes']['pass_1'] = pass_1_result
        
        if pass_1_result['status'] != 'completed':
            self.logger.error("❌ Pass 1 failed, stopping workflow")
            results['status'] = 'failed'
            results['error'] = f"Pass 1 failed: {pass_1_result.get('error')}"
            return results
        
        # Run Pass 2: Enrichment
        pass_2_result = self.run_pass_2_enrichment()
        results['passes']['pass_2'] = pass_2_result
        
        if pass_2_result['status'] != 'completed':
            self.logger.error("❌ Pass 2 failed, stopping workflow")
            results['status'] = 'failed'
            results['error'] = f"Pass 2 failed: {pass_2_result.get('error')}"
            return results
        
        # Run Pass 3: Cognitive Audit
        pass_3_result = self.run_pass_3_cognitive_audit()
        results['passes']['pass_3'] = pass_3_result
        
        if pass_3_result['status'] != 'completed':
            self.logger.error("❌ Pass 3 failed, stopping workflow")
            results['status'] = 'failed'
            results['error'] = f"Pass 3 failed: {pass_3_result.get('error')}"
            return results
        
        # Generate final summary
        results['status'] = 'completed'
        results['summary'] = self._generate_workflow_summary(results)
        
        self.logger.info("✅ Full AppDocU Workflow completed successfully")
        return results
    
    def _generate_workflow_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of the complete workflow"""
        pass_1_files = results['passes']['pass_1'].get('output_files', {})
        pass_2_files = results['passes']['pass_2'].get('output_files', {})
        pass_3_files = results['passes']['pass_3'].get('output_files', {})
        
        return {
            'total_files_generated': len(pass_1_files) + len(pass_2_files) + len(pass_3_files),
            'pass_1_status': results['passes']['pass_1']['status'],
            'pass_2_status': results['passes']['pass_2']['status'],
            'pass_3_status': results['passes']['pass_3']['status'],
            'generated_files': {
                'discovery': list(pass_1_files.values()),
                'enrichment': list(pass_2_files.values()),
                'audit': list(pass_3_files.values())
            }
        }


def main():
    """Main entry point for AppDocU"""
    parser = argparse.ArgumentParser(
        description='AppDocU - Documentation Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --target /path/to/codebase                    # Run full 3-pass workflow
  %(prog)s --target /path/to/codebase --pass 1          # Run only Pass 1 (Discovery)
  %(prog)s --target /path/to/codebase --pass 2          # Run only Pass 2 (Enrichment)
  %(prog)s --target /path/to/codebase --pass 3          # Run only Pass 3 (Cognitive Audit)
 %(prog)s --target /path/to/codebase --output /out     # Specify custom output directory
        '''
    )
    
    parser.add_argument(
        '--target',
        required=True,
        help='Path to the codebase to document'
    )
    
    parser.add_argument(
        '--pass',
        dest='pass_num',
        type=int,
        choices=[1, 2, 3],
        help='Run specific pass only (1=Discovery, 2=Enrichment, 3=Cognitive Audit)'
    )
    
    parser.add_argument(
        '--output',
        help='Output directory (default: target_path/_normalized)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag - ensure it's applied before creating orchestrator
    # Use a simple logging setup to avoid config module issues
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', force=True)
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', force=True)
        logging.getLogger().setLevel(logging.INFO)
    
    # Create orchestrator
    orchestrator = AppDocUOrchestrator(args.target, args.output)
    
    try:
        if args.pass_num:
            # Run specific pass
            if args.pass_num == 1:
                result = orchestrator.run_pass_1_discovery()
            elif args.pass_num == 2:
                result = orchestrator.run_pass_2_enrichment()
            elif args.pass_num == 3:
                result = orchestrator.run_pass_3_cognitive_audit()
            
            if result['status'] == 'completed':
                print(f"✅ Pass {args.pass_num} completed successfully")
                if 'output_files' in result:
                    print("Generated files:")
                    for name, path in result['output_files'].items():
                        print(f"  - {name}: {path}")
            else:
                print(f"❌ Pass {args.pass_num} failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
        else:
            # Run full workflow
            result = orchestrator.run_full_workflow()
            
            if result['status'] == 'completed':
                print("✅ AppDocU workflow completed successfully!")
                print(f"Generated {result['summary']['total_files_generated']} documentation files")
                print("Summary:")
                for pass_name, pass_result in result['passes'].items():
                    status = pass_result['status']
                    print(f"  - {pass_name}: {status}")
            else:
                print(f"❌ AppDocU workflow failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ AppDocU failed with error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
