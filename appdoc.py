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
# # removed PreprocessorWorkflow import
# # removed PreprocessorValidator import
# from appdocu_preprocessor.config import get_global_config, ConfigManager


class AppDocUOrchestrator:
    """Main orchestrator for the AppDocU 3-pass workflow"""
    
    def __init__(self, target_path: str, output_dir: Optional[str] = None, preprocess_mode: Optional[str] = None):
        """
        Initialize the orchestrator
        
        Args:
            target_path: Path to the codebase to document
            output_dir: Output directory (defaults to target_path/_normalized)
        """
        self.target_path = Path(target_path)
        self.output_dir = Path(output_dir) if output_dir else self.target_path / "_normalized"
        self.meta_dir = self.output_dir / ".meta"
        # Preprocess mode: 'minimal' (safe default) or 'full'
        env_mode = os.environ.get('APPDOC_PREPROCESS', '').strip().lower()
        self.preprocess_mode = (preprocess_mode or env_mode or 'minimal').lower()
        if self.preprocess_mode not in ('minimal', 'full'):
            self.preprocess_mode = 'minimal'
        
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
        self.logger.info(f"Preprocess mode: {self.preprocess_mode}")
    
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
        self.logger.info("Starting Pass 1: Discovery")
        
        try:
            # Import required modules locally to avoid config initialization issues
            from appdocu_preprocessor import preprocess_repository
            # removed PreprocessorWorkflow import
            # removed PreprocessorValidator import
            
            # Initialize workflow components if not already done
            if False and self.workflow is None:
                self.workflow = PreprocessorWorkflow(self.target_path, self.output_dir)
            if False and self.validator is None:
                self.validator = PreprocessorValidator(self.target_path, self.output_dir)
            
            # Choose preprocessing strategy
            if self.preprocess_mode == 'full':
                self.logger.info("Preprocessing (full converter pipeline)...")
                try:
                    preprocessing_result = preprocess_repository(
                        str(self.target_path),
                        str(self.output_dir),
                        validate=True
                    )
                except Exception as pe:
                    self.logger.warning(f"Full preprocessing failed, falling back to minimal enumeration: {pe}")
                    self.preprocess_mode = 'minimal'
                    manifest_path = self._basic_enumeration_write_manifest(self.target_path, self.output_dir)
                    preprocessing_result = {
                        'status': 'completed',
                        'fallback': True,
                        'manifest': str(manifest_path)
                    }
            else:
                self.logger.info("Preprocessing (basic enumeration)...")
                manifest_path = self._basic_enumeration_write_manifest(self.target_path, self.output_dir)
                preprocessing_result = {
                    'status': 'completed',
                    'fallback': True,
                    'manifest': str(manifest_path)
                }
            
            if preprocessing_result['status'] != 'completed':
                self.logger.error(f"Preprocessing failed: {preprocessing_result.get('error')}")
                return {
                    'status': 'failed',
                    'error': f"Preprocessing failed: {preprocessing_result.get('error')}",
                    'preprocessing_result': preprocessing_result
                }
            
            # Collect C# semantic artifacts (Roslyn) if available and merge
            self.logger.info("Collecting C# semantic artifacts (Roslyn)...")
            csharp_artifacts = self._collect_csharp_artifacts()

            # Generate discovery artifacts from preprocessing results + C# analysis
            discovery_results = self._generate_discovery_artifacts_from_analysis(preprocessing_result, csharp_artifacts)

            # Build Copilot handoff package under _normalized/context
            try:
                context_outputs = self._write_copilot_context_package()
            except Exception as e:
                self.logger.warning(f"Failed to write Copilot context package: {e}")
                context_outputs = {}
            
            # Update entity registry with current entities
            try:
                from orchestrator.entity_registry import EntityRegistry
                registry = EntityRegistry(self.target_path)
                registry.update_current(provenance="pass1")
            except Exception as e:
                self.logger.warning(f"Entity registry update (pass1) failed: {e}")

            result = {
                'status': 'completed',
                'generated_at': datetime.now().isoformat(),
                'preprocessing': preprocessing_result,
                'discovery': discovery_results,
                'output_files': {
                    'behavior_graph': str(self.meta_dir / 'behavior-graph.json'),
                    'system_integrations': str(self.meta_dir / 'system-integrations.json'),
                    'docx_evidence': str(self.meta_dir / 'docx-evidence.json'),
                    # Preprocessor meta files (exist in full mode)
                    'conversion_report': str(self.meta_dir / 'conversion_report.json') if (self.meta_dir / 'conversion_report.json').exists() else None,
                    'handlers': str(self.meta_dir / 'handlers.json') if (self.meta_dir / 'handlers.json').exists() else None,
                    'csharp_artifacts': str(self.meta_dir / 'csharp_artifacts.json') if csharp_artifacts is not None else None,
                    'copilot_prompt': context_outputs.get('prompt'),
                    'copilot_summary': context_outputs.get('summary')
                }
            }
            
            self.logger.info(" Pass 1: Discovery completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f" Pass 1: Discovery failed - {str(e)}", exc_info=True)
            return {
                'status': 'failed',
                'error': str(e),
                'traceback': str(e.__traceback__) if e.__traceback__ else None
            }
    
    def _generate_discovery_artifacts_from_analysis(self, preprocessing_result: Dict[str, Any], csharp_artifacts: Optional[list] = None) -> Dict[str, Any]:
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

        # Enrich with semantic C# artifacts if available
        if csharp_artifacts:
            self._augment_behavior_graph_with_csharp(behavior_graph, csharp_artifacts)

        # Enrich with lightweight Python/JS static parsing
        try:
            self._augment_behavior_graph_with_py_js(behavior_graph)
        except Exception as e:
            self.logger.warning(f"Failed to augment behavior graph with Python/JS analysis: {e}")

        # If full preprocessing, include converted outputs as nodes/edges
        try:
            if self.preprocess_mode == 'full':
                self._augment_behavior_graph_with_converted_outputs(file_manifest, behavior_graph)
        except Exception as e:
            self.logger.warning(f"Failed to augment behavior graph with converted outputs: {e}")

        # Index input sources (documents, tickets, images) as first-class nodes/evidence
        try:
            self._index_input_sources(behavior_graph, file_manifest)
        except Exception as e:
            self.logger.warning(f"Failed to index input sources: {e}")
        
        # Generate system integrations from file analysis (+ C# artifacts)
        system_integrations = self._analyze_system_integrations(code_files, other_files, csharp_artifacts or [])
        
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

        # Persist raw C# artifacts for traceability
        if csharp_artifacts is not None:
            with open(self.meta_dir / 'csharp_artifacts.json', 'w', encoding='utf-8') as f:
                json.dump(csharp_artifacts, f, indent=2, ensure_ascii=False)
        
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
                'other_files': len(other_files),
                'csharp_files_analyzed': len(csharp_artifacts) if csharp_artifacts else 0
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

    def _analyze_system_integrations(self, code_files: list, other_files: list, csharp_artifacts: list) -> dict:
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
        
        # Analyze code files for integration patterns (fallback by filename)
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

        # Enrich integrations from C# dependency namespaces
        try:
            dep_seen = set()
            for art in csharp_artifacts:
                for dep in art.get('dependencies', []) or []:
                    ns = (dep.get('namespace') or '').lower()
                    if not ns:
                        continue
                    if any(k in ns for k in ['entityframework', 'system.data', 'npgsql', 'mysql', 'mongodb', 'cosmos']):
                        if ns not in system_integrations['database_connections']:
                            system_integrations['database_connections'].append(ns)
                    if any(k in ns for k in ['system.net.http', 'refit', 'restsharp', 'grpc']):
                        if ns not in system_integrations['api_endpoints']:
                            system_integrations['api_endpoints'].append(ns)
                    if any(k in ns for k in ['kafka', 'rabbitmq', 'azure.messaging', 'azure.servicebus']):
                        if ns not in system_integrations['message_queues']:
                            system_integrations['message_queues'].append(ns)
                    dep_seen.add(ns)
            if dep_seen:
                system_integrations['external_systems'] = sorted(list(dep_seen))[:50]
        except Exception as e:
            self.logger.warning(f"Failed to enrich integrations from C# artifacts: {e}")

        # Enrich integrations by scanning Python/JS/TS code for endpoints/brokers/DB URIs
        try:
            self._enrich_integrations_from_py_js(code_files, system_integrations)
        except Exception as e:
            self.logger.warning(f"Failed to enrich integrations from Python/JS: {e}")
        
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

    def _enrich_integrations_from_py_js(self, code_files: list, system_integrations: dict) -> None:
        import re
        from urllib.parse import urlparse
        apis = set(system_integrations.get('api_endpoints', []) or [])
        dbs = set(system_integrations.get('database_connections', []) or [])
        mqs = set(system_integrations.get('message_queues', []) or [])
        externals = set(system_integrations.get('external_systems', []) or [])

        url_pattern = re.compile(r"https?://[^\s'\"]+")
        baseurl_pattern = re.compile(r"baseURL\s*:\s*['\"](https?://[^'\"]+)['\"]", re.I)

        # DB URI patterns
        db_uri_patterns = [
            re.compile(r"(postgres(?:ql)?://[^\s'\"]+)", re.I),
            re.compile(r"(mysql(?:\+pymysql)?://[^\s'\"]+)", re.I),
            re.compile(r"(sqlite://[^\s'\"]+)", re.I),
            re.compile(r"(mssql://[^\s'\"]+)", re.I),
            re.compile(r"(oracle://[^\s'\"]+)", re.I),
            re.compile(r"(mongodb(?:\+srv)?://[^\s'\"]+)", re.I),
            re.compile(r"(redis(?:\+ssl)?://[^\s'\"]+)", re.I),
        ]

        # Messaging endpoints
        mq_uri_patterns = [
            re.compile(r"(amqps?://[^\s'\"]+)", re.I),  # RabbitMQ
            re.compile(r"(kafka://[^\s'\"]+)", re.I),
            re.compile(r"(sb://[^\s'\"]+)", re.I),  # Azure Service Bus
        ]

        # KafkaJS brokers array: brokers: ['host:port']
        brokers_pattern = re.compile(r"brokers\s*:\s*\[(.*?)\]", re.I | re.S)
        hostport_pattern = re.compile(r"['\"]([a-zA-Z0-9_.\-]+:\d{2,5})['\"]")

        # grpc host:port if file references grpc
        grpc_hostport = re.compile(r"['\"]([a-zA-Z0-9_.\-]+:\d{2,5})['\"]")

        def add_api(url: str):
            try:
                p = urlparse(url)
                if p.scheme and p.netloc:
                    base = f"{p.scheme}://{p.netloc}"
                    apis.add(base)
                    externals.add(p.netloc)
            except Exception:
                pass

        def add_db(uri: str):
            dbs.add(uri)
            try:
                p = urlparse(uri)
                if p.netloc:
                    externals.add(p.netloc)
            except Exception:
                pass

        def add_mq(uri: str):
            mqs.add(uri)
            try:
                p = urlparse(uri)
                if p.netloc:
                    externals.add(p.netloc)
            except Exception:
                pass

        for f in code_files:
            fp = f.get('file') or ''
            ext = Path(fp).suffix.lower()
            if ext not in ('.py', '.js', '.ts'):
                continue
            full = self.target_path / fp
            if not full.exists():
                continue
            try:
                text = full.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue

            # HTTP endpoints: URLs and axios baseURL
            for m in url_pattern.finditer(text):
                add_api(m.group(0))
            for m in baseurl_pattern.finditer(text):
                add_api(m.group(1))

            # DB URIs
            for pat in db_uri_patterns:
                for m in pat.finditer(text):
                    add_db(m.group(1))

            # Messaging URIs
            for pat in mq_uri_patterns:
                for m in pat.finditer(text):
                    add_mq(m.group(1))

            # KafkaJS brokers
            if 'kafkajs' in text.lower() or 'new Kafka(' in text:
                bm = brokers_pattern.search(text)
                if bm:
                    segment = bm.group(1)
                    for hm in hostport_pattern.finditer(segment):
                        mqs.add(f"kafka://{hm.group(1)}")
                        externals.add(hm.group(1).split(':')[0])

            # grpc host:port if grpc appears
            if 'grpc' in text.lower():
                for hm in grpc_hostport.finditer(text):
                    host = hm.group(1)
                    apis.add(f"grpc://{host}")
                    externals.add(host.split(':')[0])

        # write back deduped lists
        system_integrations['api_endpoints'] = sorted(apis)[:200]
        system_integrations['database_connections'] = sorted(dbs)[:200]
        system_integrations['message_queues'] = sorted(mqs)[:200]
        system_integrations['external_systems'] = sorted(externals)[:200]

    def _basic_enumeration_write_manifest(self, root: Path, output_dir: Path) -> Path:
        """Minimal, dependency-free file enumeration and manifest writer."""
        import os, hashlib, json
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.vscode', '.idea'}
        def should_skip(d: str) -> bool:
            name = os.path.basename(d).lower()
            return name in skip_dirs or name.startswith('.')
        def sha256_6(p: Path) -> str:
            h = hashlib.sha256()
            try:
                with open(p, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b''):
                        h.update(chunk)
                return h.hexdigest()[:6]
            except Exception:
                return '000000'
        items = []
        for r, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if not should_skip(os.path.join(r, d))]
            for fname in files:
                fp = Path(r) / fname
                try:
                    st = fp.stat()
                    rel = str(fp.relative_to(root))
                    ext = fp.suffix.lower()
                    if ext in {'.py','.js','.ts','.cs','.java','.cpp','.h','.sql','.yaml','.yml','.xml','.html','.css','.txt','.md','.rst'}:
                        ftype = 'code'
                    elif ext in {'.docx','.doc'}:
                        ftype = 'docx'
                    elif ext in {'.xlsx','.xls','.csv'}:
                        ftype = 'excel'
                    elif ext in {'.vsdx','.vssx'}:
                        ftype = 'visio'
                    elif ext == '.pdf':
                        ftype = 'pdf'
                    elif ext in {'.pptx','.ppt'}:
                        ftype = 'pptx'
                    elif ext in {'.png','.jpg','.jpeg','.svg'}:
                        ftype = 'image'
                    elif ext == '.json':
                        ftype = 'ticket'
                    else:
                        ftype = 'other'
                    handler = {
                        'code':'CodeHandler','docx':'DocxHandler','excel':'ExcelHandler','visio':'VisioHandler','pdf':'PdfHandler','pptx':'PptxHandler','image':'ImageHandler','ticket':'TicketHandler','other':'GenericHandler'
                    }[ftype]
                    items.append({
                        'file': rel,
                        'type': ftype,
                        'handler': handler,
                        'size_kb': st.st_size // 1024,
                        'hash': sha256_6(fp),
                        'last_modified': datetime.fromtimestamp(st.st_mtime).isoformat(),
                        'status': 'pending'
                    })
                except Exception:
                    continue
        meta = output_dir / '.meta'
        meta.mkdir(parents=True, exist_ok=True)
        mf = meta / 'file_manifest.json'
        with open(mf, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        return mf

    def _write_copilot_context_package(self) -> Dict[str, str]:
        """Create a file-based handoff package for Copilot Chat under _normalized/context."""
        import json
        ctx_dir = self.output_dir / 'context'
        ctx_dir.mkdir(parents=True, exist_ok=True)

        behavior_path = self.meta_dir / 'behavior-graph.json'
        integrations_path = self.meta_dir / 'system-integrations.json'
        evidence_path = self.meta_dir / 'docx-evidence.json'

        # Curated summary for quick consumption
        summary = {
            'generated_at': datetime.now().isoformat(),
            'meta_files': {
                'behavior_graph': str(behavior_path),
                'system_integrations': str(integrations_path),
                'docx_evidence': str(evidence_path)
            },
            'counts': {},
            'integrations': {}
        }
        try:
            with open(behavior_path, 'r', encoding='utf-8') as f:
                bg = json.load(f)
            summary['counts'] = bg.get('statistics', {})
        except Exception:
            pass
        try:
            with open(integrations_path, 'r', encoding='utf-8') as f:
                si = json.load(f)
            summary['integrations'] = {
                'external_systems': si.get('external_systems', [])[:20],
                'database_connections': si.get('database_connections', [])[:20],
                'api_endpoints': si.get('api_endpoints', [])[:20],
                'message_queues': si.get('message_queues', [])[:20]
            }
        except Exception:
            pass

        summary_path = ctx_dir / 'summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Copilot prompt with instructions and links
        prompt_md = (
            "# Copilot Documentation Task\n\n"
            "Use this prompt with the attached analysis files to generate human-readable documentation.\n\n"
            "## Context Files (open these in the editor)\n"
            f"- Behavior Graph: `{behavior_path}`\n"
            f"- System Integrations: `{integrations_path}`\n"
            f"- Doc Evidence: `{evidence_path}`\n"
            f"- Summary: `{summary_path}`\n\n"
            "## What to Produce\n"
            "1. architecture.md — system overview with component breakdown and data flows\n"
            "2. logic-and-workflows.md — workflows, business rules, data processing\n"
            "3. change-impact-map.md — dependencies, risks, safe-modification guidance\n\n"
            "## Guidance\n"
            "- Cite concrete file paths and entities found in the JSONs\n"
            "- Call out fragile/risky areas and external integrations\n"
            "- Include simple Mermaid diagrams where helpful\n\n"
            "## How To Use In Copilot Chat\n"
            "- Open the JSON files listed above so Copilot can see them\n"
            "- Paste this prompt and ask Copilot to draft the docs\n"
            "- Iterate: ask Copilot to refine sections with more detail\n"
        )
        prompt_path = ctx_dir / 'prompt.md'
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(prompt_md)

        return {'prompt': str(prompt_path), 'summary': str(summary_path)}

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

    def _augment_behavior_graph_with_csharp(self, behavior_graph: dict, csharp_artifacts: list) -> None:
        """Augment behavior graph with semantic C# artifacts (classes, methods, dependencies)."""
        try:
            nodes_by_path = {n.get('path'): n for n in behavior_graph.get('nodes', [])}
            edges = behavior_graph.get('edges', [])

            for art in csharp_artifacts:
                file_path = art.get('file_path') or art.get('filePath') or ''
                if not file_path:
                    continue
                node = nodes_by_path.get(file_path)
                if node is None:
                    node = {
                        'id': f"cs_{len(nodes_by_path)}",
                        'name': Path(file_path).name,
                        'path': file_path,
                        'type': 'file',
                        'extension': '.cs'
                    }
                    behavior_graph['nodes'].append(node)
                    nodes_by_path[file_path] = node

                node['namespace'] = art.get('namespace', '')
                node['lines_of_code'] = art.get('lines_of_code', 0)
                node['classes'] = [c.get('name') for c in (art.get('classes') or [])]

                # Basic metrics for quick health checks
                try:
                    cls_list = art.get('classes') or []
                    method_count = sum(len(c.get('methods') or []) for c in cls_list)
                    metrics = node.get('metrics') or {}
                    metrics.update({
                        'loc': int(art.get('lines_of_code') or 0),
                        'class_count': len(cls_list),
                        'method_count': method_count
                    })
                    node['metrics'] = metrics
                except Exception:
                    pass

                for dep in art.get('dependencies') or []:
                    ns = dep.get('namespace')
                    if ns:
                        edges.append({
                            'from': file_path,
                            'to_namespace': ns,
                            'type': 'uses'
                        })

            behavior_graph['statistics'] = behavior_graph.get('statistics', {})
            behavior_graph['statistics']['csharp_files'] = len(csharp_artifacts)
        except Exception as e:
            self.logger.warning(f"Failed to augment behavior graph with C# artifacts: {e}")

    def _collect_csharp_artifacts(self) -> Optional[list]:
        """Run the C# analyzer to collect semantic artifacts for .cs files under target_path."""
        try:
            from orchestrator.config import Config as OrchestratorConfig
            from orchestrator.file_scanner import FileScanner
            from orchestrator.csharp_runner import CSharpRunner

            csharp_meta_dir = self.meta_dir / 'csharp'
            csharp_meta_dir.mkdir(parents=True, exist_ok=True)

            cfg = OrchestratorConfig(
                repo_path=self.target_path,
                output_path=csharp_meta_dir,
                dry_run=True,
                verbose=False
            )

            scanner = FileScanner(cfg)
            cs_files = scanner.scan_for_csharp_files()
            if not cs_files:
                self.logger.info("No C# files found for semantic analysis")
                return []

            runner = CSharpRunner(cfg)
            artifacts = runner.analyze_files(cs_files)

            if not isinstance(artifacts, list):
                return []
            return artifacts
        except FileNotFoundError as e:
            self.logger.warning(f"C# analyzer not available: {e}")
            return []
        except Exception as e:
            self.logger.warning(f"C# artifact collection failed: {e}")
            return []

    def _augment_behavior_graph_with_py_js(self, behavior_graph: dict) -> None:
        """Augment behavior graph with basic Python/JS parsing (functions and imports)."""
        import re
        import ast
        nodes_by_path = {n.get('path'): n for n in behavior_graph.get('nodes', [])}
        edges = behavior_graph.get('edges', [])

        def parse_python(text: str) -> tuple[list[str], list[str]]:
            funcs = re.findall(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text, flags=re.M)
            imports = []
            for m in re.finditer(r"^\s*import\s+([A-Za-z0-9_\.]+)", text, flags=re.M):
                imports.append(m.group(1))
            for m in re.finditer(r"^\s*from\s+([A-Za-z0-9_\.]+)\s+import\s+", text, flags=re.M):
                imports.append(m.group(1))
            return list(sorted(set(funcs))), list(sorted(set(imports)))

        def parse_js(text: str) -> tuple[list[str], list[str]]:
            funcs = []
            funcs += re.findall(r"^\s*function\s+([A-Za-z_\$][A-Za-z0-9_\$]*)\s*\(", text, flags=re.M)
            funcs += re.findall(r"^\s*(?:const|let|var)\s+([A-Za-z_\$][A-Za-z0-9_\$]*)\s*=\s*\(.*?\)\s*=>", text, flags=re.M)
            imports = []
            imports += re.findall(r"^\s*import\s+.*?from\s+['\"]([^'\"]+)['\"]", text, flags=re.M)
            imports += re.findall(r"require\(\s*['\"]([^'\"]+)['\"]\s*\)", text, flags=re.M)
            return list(sorted(set(funcs))), list(sorted(set(imports)))

        def compute_complexity(text: str, lang: str) -> int:
            try:
                if lang == 'python':
                    tokens = [' if ', '\nif ', ' for ', '\nfor ', ' while ', '\nwhile ', ' and ', ' or ', ' try:', ' except', ' with ', '\nelif ', ' case ']
                else:
                    tokens = [' if ', '\nif ', ' for ', '\nfor ', ' while ', '\nwhile ', ' case ', '&&', '||', ' try', ' catch']
                count = 1
                lower = text.lower()
                for t in tokens:
                    count += lower.count(t)
                return count
            except Exception:
                return 1

        for path, node in nodes_by_path.items():
            ext = (node.get('extension') or Path(path).suffix).lower()
            abs_path = (self.target_path / path) if path else None
            if not abs_path or not abs_path.exists():
                continue
            try:
                if ext in ('.py', '.js', '.ts'):
                    with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if ext == '.py':
                        funcs, imps = parse_python(content)
                        # AST enrich: classes/methods + import records
                        py_classes: list[str] = []
                        import_records = { 'rel': [], 'abs': [] }
                        try:
                            tree = ast.parse(content)
                            for n in ast.walk(tree):
                                if isinstance(n, ast.ClassDef):
                                    mcount = sum(1 for b in n.body if isinstance(b, ast.FunctionDef))
                                    label = n.name + (f" ({mcount} methods)" if mcount else "")
                                    py_classes.append(label)
                                elif isinstance(n, ast.ImportFrom):
                                    mod = n.module or ""
                                    if n.level and n.level > 0:
                                        import_records['rel'].append((n.level, mod))
                                    else:
                                        import_records['abs'].append(mod)
                                elif isinstance(n, ast.Import):
                                    for alias in n.names:
                                        if alias.name:
                                            import_records['abs'].append(alias.name)
                        except Exception:
                            pass
                        if py_classes:
                            node['classes'] = list(sorted(set((node.get('classes') or []) + py_classes)))
                        node['language'] = 'python'
                        complexity = compute_complexity(content, 'python')
                        # Resolve imports to file nodes
                        def _resolve_rel(cur: Path, level: int, module: str) -> str | None:
                            base = cur.parent
                            for _ in range(max(0, level)):
                                base = base.parent
                            parts = (module or '').split('.') if module else []
                            candidate = base
                            for pseg in parts:
                                if pseg:
                                    candidate = candidate / pseg
                            for cand in [candidate.with_suffix('.py'), candidate / '__init__.py']:
                                try:
                                    relp = str(cand.relative_to(self.target_path))
                                    if relp in nodes_by_path:
                                        return relp
                                except Exception:
                                    continue
                            return None
                        def _resolve_abs(cur: Path, module: str) -> str | None:
                            if not module:
                                return None
                            parts = module.split('.')
                            candidate = self.target_path
                            for pseg in parts:
                                if pseg:
                                    candidate = candidate / pseg
                            for cand in [candidate.with_suffix('.py'), candidate / '__init__.py']:
                                try:
                                    relp = str(cand.relative_to(self.target_path))
                                    if relp in nodes_by_path:
                                        return relp
                                except Exception:
                                    continue
                            return None
                        for lvl, mod in import_records['rel']:
                            dep = _resolve_rel(abs_path, lvl, mod)
                            if dep:
                                edges.append({'from': path, 'to': dep, 'type': 'depends_on'})
                        for mod in set(import_records['abs']):
                            dep = _resolve_abs(abs_path, mod)
                            if dep:
                                edges.append({'from': path, 'to': dep, 'type': 'depends_on'})
                    else:
                        funcs, imps = parse_js(content)
                        node['language'] = 'javascript' if ext == '.js' else 'typescript'
                        complexity = compute_complexity(content, 'javascript')
                        # JS/TS classes (cover plain class, export class, export default class)
                        js_classes = re.findall(r"^\s*(?:export\s+default\s+class|export\s+class|class)\s+([A-Za-z_\$][A-Za-z0-9_\$]*)", content, flags=re.M)
                        if js_classes:
                            node['classes'] = list(sorted(set((node.get('classes') or []) + js_classes)))
                        # Resolve relative imports -> file nodes
                        def _resolve_js(cur: Path, spec: str) -> str | None:
                            if not (spec.startswith('./') or spec.startswith('../')):
                                return None
                            base = cur.parent
                            target = (base / spec).resolve()
                            exts = ['.ts', '.js', '.tsx', '.jsx', '.mjs', '.cjs']
                            candidates: list[Path] = []
                            if target.suffix:
                                candidates.append(target)
                            else:
                                candidates += [target.with_suffix(e) for e in exts]
                                candidates += [(target / 'index').with_suffix(e) for e in exts]
                            for cand in candidates:
                                try:
                                    relp = str(cand.relative_to(self.target_path))
                                    if relp in nodes_by_path:
                                        return relp
                                except Exception:
                                    continue
                            return None
                        for spec in imps:
                            dep = _resolve_js(abs_path, spec)
                            if dep:
                                edges.append({'from': path, 'to': dep, 'type': 'depends_on'})
                    if funcs:
                        node['functions'] = funcs
                    if imps:
                        node['imports'] = imps
                        for mod in imps:
                            edges.append({'from': path, 'to_module': mod, 'type': 'imports'})
                    # Attach simple metrics
                    metrics = node.get('metrics') or {}
                    metrics.update({
                        'loc': len(content.splitlines()),
                        'function_count': len(funcs),
                        'import_count': len(imps),
                        'complexity': complexity
                    })
                    node['metrics'] = metrics
            except Exception as e:
                # Do not fail the workflow on parser errors
                self.logger.debug(f"Skipping parse for {path}: {e}")

    def _augment_behavior_graph_with_converted_outputs(self, file_manifest: list, behavior_graph: dict) -> None:
        """Add converted output files as nodes and connect with 'converted_to' edges.

        Reads _normalized/.meta/file_manifest.json entries where status == 'converted' and
        output_file is present. Creates nodes for outputs (type: 'converted') and edges:
        { from: <source_path>, to: <normalized_output_relative>, type: 'converted_to' }.
        """
        nodes_by_path = {n.get('path'): n for n in behavior_graph.get('nodes', [])}
        edges = behavior_graph.get('edges', [])
        normalized_dir = self.output_dir / 'normalized'
        for entry in file_manifest or []:
            if entry.get('status') != 'converted':
                continue
            src = entry.get('file')
            out_rel = entry.get('output_file')
            if not src or not out_rel:
                continue
            out_path = str(Path('normalized') / out_rel)
            # Add node if missing
            if out_path not in nodes_by_path:
                node = {
                    'id': f"conv_{len(behavior_graph.get('nodes', []))}",
                    'name': Path(out_path).name,
                    'path': out_path,
                    'type': 'converted',
                    'extension': Path(out_path).suffix
                }
                behavior_graph['nodes'].append(node)
                nodes_by_path[out_path] = node
            # Add edge from source file to converted file
            edges.append({'from': src, 'to': out_path, 'type': 'converted_to'})

    def _index_input_sources(self, behavior_graph: dict, file_manifest: list) -> None:
        """Add non-code inputs (docs, tickets, images) to the graph and evidence list."""
        nodes_by_path = {n.get('path'): n for n in behavior_graph.get('nodes', [])}
        evidence = {
            'documents': [],
            'tickets': []
        }
        doc_types = {'docx','excel','visio','pdf','pptx','image'}
        ticket_types = {'ticket'}

        document_count = 0
        ticket_count = 0

        for entry in file_manifest or []:
            ftype = (entry.get('type') or '').lower()
            fpath = entry.get('file') or ''
            if not fpath:
                continue
            if ftype in doc_types:
                document_count += 1
                info = {
                    'path': fpath,
                    'type': ftype,
                    'size_kb': entry.get('size_kb', 0),
                    'last_modified': entry.get('last_modified', ''),
                    'status': entry.get('status', 'unknown')
                }
                evidence['documents'].append(info)
                if fpath not in nodes_by_path:
                    node = {
                        'id': f"doc_{len(behavior_graph.get('nodes', []))}",
                        'name': Path(fpath).name,
                        'path': fpath,
                        'type': 'document',
                        'doc_type': ftype,
                        'extension': Path(fpath).suffix,
                        'size_kb': entry.get('size_kb', 0)
                    }
                    behavior_graph['nodes'].append(node)
                    nodes_by_path[fpath] = node
            elif ftype in ticket_types:
                ticket_count += 1
                info = {
                    'path': fpath,
                    'type': ftype,
                    'size_kb': entry.get('size_kb', 0),
                    'last_modified': entry.get('last_modified', ''),
                    'status': entry.get('status', 'unknown')
                }
                evidence['tickets'].append(info)
                if fpath not in nodes_by_path:
                    node = {
                        'id': f"ticket_{len(behavior_graph.get('nodes', []))}",
                        'name': Path(fpath).name,
                        'path': fpath,
                        'type': 'ticket',
                        'extension': Path(fpath).suffix,
                        'size_kb': entry.get('size_kb', 0)
                    }
                    behavior_graph['nodes'].append(node)
                    nodes_by_path[fpath] = node

        # Attach evidence and simple stats
        behavior_graph['evidence'] = evidence
        stats = behavior_graph.get('statistics', {})
        stats['document_files'] = document_count
        stats['ticket_files'] = ticket_count
        behavior_graph['statistics'] = stats

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
        self.logger.info("Starting Pass 2: Enrichment")
        
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
            
            self.logger.info(" Pass 2: Enrichment completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f" Pass 2: Enrichment failed - {str(e)}", exc_info=True)
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
        
        # Generate basic diagrams from discovery artifacts
        diagrams_created: list[str] = []
        try:
            from orchestrator.diagram_generator import DiagramGenerator
            dg = DiagramGenerator(self.target_path)
            diagrams_created = dg.generate_all()
        except Exception as e:
            self.logger.warning(f"Diagram generation skipped or failed: {e}")

        # Append diagram references to architecture doc if generated
        if diagrams_created:
            try:
                with open(architecture_file, 'a', encoding='utf-8') as f:
                    f.write("\n\n## Diagrams\n")
                    # Group by logical diagram base (without extension)
                    by_base = {}
                    for p in diagrams_created:
                        base = str(Path(p).with_suffix(''))
                        by_base.setdefault(base, []).append(p)
                    for base, files in by_base.items():
                        # Write links for all files
                        rel_links = []
                        for fp in files:
                            if Path(fp).exists():
                                rel = Path(fp).relative_to(self.target_path).as_posix()
                            else:
                                rel = fp.replace('\\\\', '/').replace('\\', '/')
                            rel_links.append(rel)
                        f.write(f"- {Path(base).name}:\n")
                        for link in rel_links:
                            f.write(f"  - {link}\n")
                        # Embed inline image if SVG (preferred) or PNG exists
                        svg = Path(base + '.svg')
                        png = Path(base + '.png')
                        embed_path = None
                        if svg.exists():
                            embed_path = svg
                        elif png.exists():
                            embed_path = png
                        if embed_path:
                            rel_img = embed_path.relative_to(self.target_path).as_posix()
                            f.write(f"\n![{Path(base).name}]({rel_img})\n\n")
            except Exception:
                pass

        # Also append diagram references inline to logic-and-workflows.md
        if diagrams_created:
            try:
                with open(logic_workflows_file, 'a', encoding='utf-8') as f:
                    f.write("\n\n## Diagrams\n")
                    by_base = {}
                    for p in diagrams_created:
                        base = str(Path(p).with_suffix(''))
                        by_base.setdefault(base, []).append(p)
                    for base, files in by_base.items():
                        rel_links = []
                        for fp in files:
                            if Path(fp).exists():
                                rel = Path(fp).relative_to(self.target_path).as_posix()
                            else:
                                rel = fp.replace('\\\\', '/').replace('\\', '/')
                            rel_links.append(rel)
                        f.write(f"- {Path(base).name}:\n")
                        for link in rel_links:
                            f.write(f"  - {link}\n")
                        svg = Path(base + '.svg')
                        png = Path(base + '.png')
                        embed_path = svg if svg.exists() else (png if png.exists() else None)
                        if embed_path:
                            rel_img = embed_path.relative_to(self.target_path).as_posix()
                            f.write(f"\n![{Path(base).name}]({rel_img})\n\n")
            except Exception:
                pass

        # Create a standalone diagrams.md with links and inline embeds
        diagrams_doc = self.target_path / 'diagrams.md'
        try:
            with open(diagrams_doc, 'w', encoding='utf-8') as f:
                f.write(f"# Diagrams\n\nGenerated by AppDocU at {datetime.now().isoformat()}\n\n")
                if not diagrams_created:
                    f.write("No diagrams were generated.\n")
                else:
                    by_base = {}
                    for p in diagrams_created:
                        base = str(Path(p).with_suffix(''))
                        by_base.setdefault(base, []).append(p)
                    for base, files in by_base.items():
                        title = Path(base).name
                        f.write(f"## {title}\n\n")
                        # Links
                        for fp in files:
                            if Path(fp).exists():
                                rel = Path(fp).relative_to(self.target_path).as_posix()
                            else:
                                rel = fp.replace('\\\\', '/').replace('\\', '/')
                            f.write(f"- {rel}\n")
                        # Inline image
                        svg = Path(base + '.svg')
                        png = Path(base + '.png')
                        embed_path = svg if svg.exists() else (png if png.exists() else None)
                        if embed_path:
                            rel_img = embed_path.relative_to(self.target_path).as_posix()
                            f.write(f"\n![{title}]({rel_img})\n\n")
        except Exception as e:
            self.logger.warning(f"Failed to write diagrams.md: {e}")

        # Update entity registry with doc provenance and append deprecations
        try:
            from orchestrator.entity_registry import EntityRegistry
            registry = EntityRegistry(self.target_path)
            registry.update_docs([
                str(architecture_file),
                str(logic_workflows_file),
                str(change_impact_file)
            ], provenance="pass2")
            registry.append_deprecations_to_doc(architecture_file)
            registry.append_deprecations_to_doc(logic_workflows_file)
        except Exception as e:
            self.logger.warning(f"Entity registry update (pass2) failed: {e}")

        return {
            'architecture_generated': True,
            'logic_workflows_generated': True,
            'change_impact_map_generated': True,
            'diagrams_generated': bool(diagrams_created),
            'files_created': [
                str(architecture_file),
                str(logic_workflows_file),
                str(change_impact_file),
                str(diagrams_doc)
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
        self.logger.info("Starting Pass 3: Cognitive Audit")
        
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
            
            self.logger.info(" Pass 3: Cognitive Audit completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f" Pass 3: Cognitive Audit failed - {str(e)}", exc_info=True)
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
        self.logger.info("Starting Full AppDocU Workflow")
        
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
            self.logger.error(" Pass 1 failed, stopping workflow")
            results['status'] = 'failed'
            results['error'] = f"Pass 1 failed: {pass_1_result.get('error')}"
            return results
        
        # Run Pass 2: Enrichment
        pass_2_result = self.run_pass_2_enrichment()
        results['passes']['pass_2'] = pass_2_result
        
        if pass_2_result['status'] != 'completed':
            self.logger.error(" Pass 2 failed, stopping workflow")
            results['status'] = 'failed'
            results['error'] = f"Pass 2 failed: {pass_2_result.get('error')}"
            return results
        
        # Run Pass 3: Cognitive Audit
        pass_3_result = self.run_pass_3_cognitive_audit()
        results['passes']['pass_3'] = pass_3_result
        
        if pass_3_result['status'] != 'completed':
            self.logger.error(" Pass 3 failed, stopping workflow")
            results['status'] = 'failed'
            results['error'] = f"Pass 3 failed: {pass_3_result.get('error')}"
            return results
        
        # Generate final summary
        results['status'] = 'completed'
        results['summary'] = self._generate_workflow_summary(results)
        
        self.logger.info(" Full AppDocU Workflow completed successfully")
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
        '--preprocess',
        choices=['minimal','full'],
        default='minimal',
        help='Preprocessing strategy: minimal (safe) or full (use converters). Can also set APPDOC_PREPROCESS=minimal|full.'
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
    orchestrator = AppDocUOrchestrator(args.target, args.output, preprocess_mode=args.preprocess)
    
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
                print(f" Pass {args.pass_num} completed successfully")
                if 'output_files' in result:
                    print("Generated files:")
                    for name, path in result['output_files'].items():
                        print(f"  - {name}: {path}")
            else:
                print(f" Pass {args.pass_num} failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
        else:
            # Run full workflow
            result = orchestrator.run_full_workflow()
            
            if result['status'] == 'completed':
                print(" AppDocU workflow completed successfully!")
                print(f"Generated {result['summary']['total_files_generated']} documentation files")
                print("Summary:")
                for pass_name, pass_result in result['passes'].items():
                    status = pass_result['status']
                    print(f"  - {pass_name}: {status}")
            else:
                print(f" AppDocU workflow failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f" AppDocU failed with error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()











