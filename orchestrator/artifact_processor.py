"""Artifact processing and aggregation."""

from typing import Dict, Any, List
from pathlib import Path
from orchestrator.logger import setup_logger

logger = setup_logger(__name__)


class ArtifactProcessor:
    """Processes and aggregates code artifacts."""
    
    def __init__(self, config):
        self.config = config
    
    def process_artifacts(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process and aggregate artifacts for documentation generation.
        
        Args:
            artifacts: List of artifact dictionaries from C# analysis
            
        Returns:
            Processed data structure for LLM consumption
        """
        logger.info(f"Processing {len(artifacts)} artifacts...")
        
        processed = {
            "total_files": len(artifacts),
            "total_classes": sum(len(a.get("classes", [])) for a in artifacts),
            "total_methods": sum(
                sum(len(c.get("methods", [])) for c in a.get("classes", []))
                for a in artifacts
            ),
            "artifacts": artifacts,
            "namespaces": self._extract_namespaces(artifacts),
            "dependencies": self._aggregate_dependencies(artifacts)
        }
        
        logger.info(f"Processed: {processed['total_classes']} classes, "
                   f"{processed['total_methods']} methods")
        
        return processed
    
    def _extract_namespaces(self, artifacts: List[Dict[str, Any]]) -> List[str]:
        """Extract unique namespaces from artifacts."""
        namespaces = set()
        for artifact in artifacts:
            ns = artifact.get("namespace", "")
            if ns:
                namespaces.add(ns)
        return sorted(list(namespaces))
    
    def _aggregate_dependencies(self, artifacts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Aggregate dependency usage across all files."""
        dep_counts = {}
        for artifact in artifacts:
            for dep in artifact.get("dependencies", []):
                ns = dep.get("namespace", "")
                if ns:
                    dep_counts[ns] = dep_counts.get(ns, 0) + 1
        return dict(sorted(dep_counts.items(), key=lambda x: x[1], reverse=True))
    
    def write_documentation(self, documentation: Dict[str, Any]):
        """
        Write documentation files to output directory.
        
        Args:
            documentation: Documentation structure from LLM
        """
        logger.info("Writing documentation files...")
        
        readme_content = documentation.get("readme", "# Documentation\n\nNo content generated.")
        readme_path = self.config.output_path / "README.md"
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info(f"Written: {readme_path}")
        
        # Write additional documentation files if present
        for doc_type in ["architecture", "api_reference", "quick_start"]:
            content = documentation.get(doc_type)
            if content:
                doc_path = self.config.output_path / f"{doc_type}.md"
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Written: {doc_path}")

