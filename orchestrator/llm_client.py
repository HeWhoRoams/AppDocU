"""LLM API interaction with retry logic."""

from typing import Dict, Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from orchestrator.logger import setup_logger


logger = setup_logger(__name__)


class LLMAPIError(Exception):
    """LLM API call failed."""
    pass


class LLMClient:
    """Manages LLM API calls for documentation generation."""

    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        if config.llm_api_key:
            self.session.headers.update({"Authorization": f"Bearer {config.llm_api_key}"})

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, LLMAPIError)),
        reraise=True,
    )
    def generate_documentation(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation by calling LLM API, or a basic fallback when no endpoint is configured."""
        logger.info("Calling LLM API for documentation generation...")
        if not self.config.llm_endpoint:
            logger.warning("No LLM endpoint configured, generating basic documentation")
            return self._generate_basic_documentation(processed_data)

        prompt = self._build_prompt(processed_data)
        try:
            response = self.session.post(
                self.config.llm_endpoint,
                json={
                    "model": self.config.llm_model,
                    "prompt": prompt,
                    "max_tokens": 4096,
                    "temperature": 0.3,
                },
                timeout=self.config.llm_timeout,
            )
            response.raise_for_status()
            result = response.json()
            logger.info("LLM generation successful")
            return self._parse_llm_response(result)
        except requests.RequestException as e:
            logger.error(f"LLM API request failed: {e}")
            raise LLMAPIError(f"API request failed: {e}")

    def _build_prompt(self, processed_data: Dict[str, Any]) -> str:
        """Build prompt for LLM."""
        parts = [
            "# Documentation Generation Task",
            "",
            "Generate comprehensive, human-readable documentation for the following C# codebase.",
            "",
            "## Code Structure",
            f"- Total Files: {processed_data.get('total_files', 0)}",
            f"- Total Classes: {processed_data.get('total_classes', 0)}",
            f"- Total Methods: {processed_data.get('total_methods', 0)}",
            f"- Namespaces: {', '.join(processed_data.get('namespaces', [])[:5])}",
            "",
            "## Requirements",
            "1. Generate a README.md with overview and architecture",
            "2. Document key classes with purpose and usage",
            "3. Identify design patterns",
            "4. Create a quick-start guide",
            "",
            "## Code Details",
            "",
        ]
        for artifact in processed_data.get("artifacts", [])[:3]:
            parts.append(f"### File: {artifact.get('file_path')}")
            parts.append(f"Namespace: {artifact.get('namespace')}")
            for cls in artifact.get("classes", [])[:2]:
                parts.append(f"- Class: {cls.get('name')}")
                parts.append(f"  Methods: {len(cls.get('methods', []))}")
            parts.append("")
        return "\n".join(parts)

    def _parse_llm_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM API response."""
        generated_text = (
            (response.get("choices", [{}])[0].get("text", ""))
            or response.get("content", "")
            or response.get("response", "")
        )
        return {"readme": generated_text, "raw_response": response}

    def _generate_basic_documentation(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic documentation without LLM."""
        ns_lines = "\n".join(f"- {ns}" for ns in processed_data.get("namespaces", []))
        dep_lines = "\n".join(
            f"- {dep} (used {count} times)" for dep, count in list(processed_data.get("dependencies", {}).items())[:10]
        )
        file_lines = "\n".join(
            f"- {a.get('file_path')} ({len(a.get('classes', []))} classes)" for a in processed_data.get("artifacts", [])[:20]
        )
        readme = (
            f"# Codebase Documentation\n\n"
            f"## Overview\n\n"
            f"This codebase contains {processed_data.get('total_files',0)} C# files "
            f"with {processed_data.get('total_classes',0)} classes and {processed_data.get('total_methods',0)} methods.\n\n"
            f"## Namespaces\n\n{ns_lines}\n\n"
            f"## Top Dependencies\n\n{dep_lines}\n\n"
            f"## Files\n\n{file_lines}\n\n---\n\n*Generated automatically by AppDocU*\n"
        )
        return {"readme": readme}
