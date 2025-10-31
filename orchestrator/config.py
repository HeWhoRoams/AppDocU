"""Configuration management for the orchestrator.

Centralizes runtime configuration with precedence:
CLI > environment (.env) > appdoc.config.json > defaults.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os
import json
from contextlib import suppress

load_dotenv()


@dataclass
class Config:
    """Global configuration for C# + LLM pieces (legacy struct)."""

    # Paths
    repo_path: Path = None
    output_path: Path = None
    artifacts_dir: Optional[Path] = None

    # C# Worker
    csharp_tool_path: Path = field(default_factory=lambda: Path("./DocTool/bin/Release/net8.0/DocTool.exe"))
    csharp_timeout: int = 300

    # LLM Configuration
    llm_endpoint: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_model: str = "qwen-coder-3b"
    llm_timeout: int = 120
    max_retries: int = 3

    # Workflow
    verbose: bool = False
    dry_run: bool = False

    # File patterns (for C# scan)
    include_patterns: list = field(default_factory=lambda: ["*.cs"])
    exclude_patterns: list = field(default_factory=lambda: ["**/obj/**", "**/bin/**", "**/packages/**"])

    def __post_init__(self):
        if self.llm_endpoint is None:
            self.llm_endpoint = os.getenv("LLM_ENDPOINT")
        if self.llm_api_key is None:
            self.llm_api_key = os.getenv("LLM_API_KEY")
        if self.artifacts_dir is None:
            self.artifacts_dir = self.output_path / "artifacts"
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class CentralConfig:
    """Centralized config knobs for the whole pipeline."""

    # Preprocess mode
    preprocess_mode: str = "minimal"  # minimal|full

    # Quality gates
    min_coverage_pct: float = 70.0
    max_failure_rate_pct: float = 10.0
    require_diagrams: bool = True

    # Diagrams / rendering
    mmd_max_nodes: int = 60
    mmd_max_edges: int = 120
    dep_include_prefixes: str = ""  # comma-separated
    dep_only_file_targets: bool = False
    dep_only_code_nodes: bool = False
    kroki_url: Optional[str] = None
    prefer_mmdc: bool = True  # if mmdc available, use it

    # Registry
    symbol_registry: bool = True

    # Include/exclude patterns (generic)
    include_patterns: Optional[list] = None
    exclude_patterns: Optional[list] = None

    # LLM (for convenience)
    llm_endpoint: Optional[str] = None

    @staticmethod
    def load(repo_root: Path) -> "CentralConfig":
        cfg = CentralConfig()  # defaults
        # Load from config file if present
        json_path = Path(repo_root) / "appdoc.config.json"
        if json_path.exists():
            with suppress(Exception):
                with open(json_path, "r", encoding="utf-8") as f:
                    data: Dict[str, Any] = json.load(f)
                CentralConfig._apply_dict(cfg, data)
        # YAML support (optional)
        for yname in ("appdoc.config.yaml", "appdoc.config.yml"):
            ypath = Path(repo_root) / yname
            if ypath.exists():
                with suppress(Exception):
                    import yaml  # type: ignore
                    with open(ypath, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                    if isinstance(data, dict):
                        CentralConfig._apply_dict(cfg, data) 
        # Apply environment overrides
        CentralConfig._apply_env(cfg)
        return cfg

    @staticmethod
    def _apply_dict(cfg: "CentralConfig", data: Dict[str, Any]) -> None:
        for k, v in (data or {}).items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)

    @staticmethod
    def _apply_env(cfg: "CentralConfig") -> None:
        def env_bool(name: str, cur: bool) -> bool:
            val = os.getenv(name)
            if val is None:
                return cur
            v = val.strip().lower()
            if v in ("1", "true", "yes", "on"):
                return True
            if v in ("0", "false", "no", "off"):
                return False
            return cur

        def env_float(name: str, cur: float) -> float:
            val = os.getenv(name)
            if val is None:
                return cur
            try:
                return float(val)
            except Exception:
                return cur

        def env_int(name: str, cur: int) -> int:
            val = os.getenv(name)
            if val is None:
                return cur
            try:
                return int(val)
            except Exception:
                return cur

        cfg.preprocess_mode = os.getenv("APPDOC_PREPROCESS", cfg.preprocess_mode)
        cfg.min_coverage_pct = env_float("APPDOC_MIN_COVERAGE", cfg.min_coverage_pct)
        cfg.max_failure_rate_pct = env_float("APPDOC_MAX_FAILURE", cfg.max_failure_rate_pct)
        cfg.require_diagrams = env_bool("APPDOC_REQUIRE_DIAGRAMS", cfg.require_diagrams)

        cfg.mmd_max_nodes = env_int("APPDOC_MMD_MAX_NODES", cfg.mmd_max_nodes)
        cfg.mmd_max_edges = env_int("APPDOC_MMD_MAX_EDGES", cfg.mmd_max_edges)
        cfg.dep_include_prefixes = os.getenv("APPDOC_DEP_INCLUDE_PREFIXES", cfg.dep_include_prefixes)
        cfg.dep_only_file_targets = env_bool("APPDOC_DEP_ONLY_FILE_TARGETS", cfg.dep_only_file_targets)
        cfg.dep_only_code_nodes = env_bool("APPDOC_DEP_ONLY_CODE_NODES", cfg.dep_only_code_nodes)
        cfg.kroki_url = os.getenv("KROKI_URL", cfg.kroki_url)
        cfg.symbol_registry = env_bool("APPDOC_SYMBOL_REGISTRY", cfg.symbol_registry)
        cfg.llm_endpoint = os.getenv("LLM_ENDPOINT", cfg.llm_endpoint)

    def apply_env(self) -> None:
        """Propagate relevant settings to environment for components that read env."""
        os.environ["APPDOC_PREPROCESS"] = self.preprocess_mode
        os.environ["APPDOC_MIN_COVERAGE"] = str(self.min_coverage_pct)
        os.environ["APPDOC_MAX_FAILURE"] = str(self.max_failure_rate_pct)
        os.environ["APPDOC_REQUIRE_DIAGRAMS"] = "1" if self.require_diagrams else "0"
        os.environ["APPDOC_MMD_MAX_NODES"] = str(self.mmd_max_nodes)
        os.environ["APPDOC_MMD_MAX_EDGES"] = str(self.mmd_max_edges)
        if self.dep_include_prefixes is not None:
            os.environ["APPDOC_DEP_INCLUDE_PREFIXES"] = str(self.dep_include_prefixes)
        os.environ["APPDOC_DEP_ONLY_FILE_TARGETS"] = "1" if self.dep_only_file_targets else "0"
        os.environ["APPDOC_DEP_ONLY_CODE_NODES"] = "1" if self.dep_only_code_nodes else "0"
        if self.kroki_url:
            os.environ["KROKI_URL"] = self.kroki_url
        os.environ["APPDOC_SYMBOL_REGISTRY"] = "1" if self.symbol_registry else "0"
        if self.llm_endpoint:
            os.environ["LLM_ENDPOINT"] = self.llm_endpoint

    def to_dict(self) -> Dict[str, Any]:
        return {
            "preprocess_mode": self.preprocess_mode,
            "min_coverage_pct": self.min_coverage_pct,
            "max_failure_rate_pct": self.max_failure_rate_pct,
            "require_diagrams": self.require_diagrams,
            "mmd_max_nodes": self.mmd_max_nodes,
            "mmd_max_edges": self.mmd_max_edges,
            "dep_include_prefixes": self.dep_include_prefixes,
            "dep_only_file_targets": self.dep_only_file_targets,
            "dep_only_code_nodes": self.dep_only_code_nodes,
            "kroki_url": self.kroki_url,
            "symbol_registry": self.symbol_registry,
            "include_patterns": self.include_patterns,
            "exclude_patterns": self.exclude_patterns,
            "llm_endpoint": self.llm_endpoint,
        }
