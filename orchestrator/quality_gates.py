"""Quality gates for documentation runs.

Evaluates coverage, failure rate, diagrams presence, and doc sections.
Writes a machine-readable report (validation_report.json) and a human-readable
report (validation_report.md) into a provided run directory.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class QualityGates:
    def __init__(
        self,
        repo_root: Path,
        min_coverage_pct: float = 70.0,
        max_failure_rate_pct: float = 10.0,
        require_diagrams: bool = True,
        required_arch_sections: Optional[List[str]] = None,
        required_logic_sections: Optional[List[str]] = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.normalized = self.repo_root / "_normalized"
        self.meta_dir = self.normalized / ".meta"
        self.diagrams_dir = self.normalized / "diagrams"
        self.min_coverage_pct = min_coverage_pct
        self.max_failure_rate_pct = max_failure_rate_pct
        self.require_diagrams = require_diagrams
        self.required_arch_sections = required_arch_sections or [
            "## Components",
            "## Dependencies",
            "## Data Flow",
            "## Integration Points",
        ]
        self.required_logic_sections = required_logic_sections or [
            "## Workflows",
            "## Data Processing",
            "## Business Rules",
        ]

    @classmethod
    def from_env(
        cls,
        repo_root: Path,
        min_coverage_pct: Optional[float] = None,
        max_failure_rate_pct: Optional[float] = None,
        require_diagrams: Optional[bool] = None,
        required_arch_sections: Optional[List[str]] = None,
        required_logic_sections: Optional[List[str]] = None,
    ) -> "QualityGates":
        import os
        def _env_float(name: str, default: Optional[float]) -> Optional[float]:
            val = os.environ.get(name)
            if val is None:
                return default
            try:
                return float(val)
            except Exception:
                return default
        def _env_bool(name: str, default: Optional[bool]) -> Optional[bool]:
            val = os.environ.get(name)
            if val is None:
                return default
            v = val.strip().lower()
            if v in ("1","true","yes","on"): return True
            if v in ("0","false","no","off"): return False
            return default
        mc = min_coverage_pct if min_coverage_pct is not None else _env_float("APPDOC_MIN_COVERAGE", 70.0)
        mf = max_failure_rate_pct if max_failure_rate_pct is not None else _env_float("APPDOC_MAX_FAILURE", 10.0)
        rd = require_diagrams if require_diagrams is not None else _env_bool("APPDOC_REQUIRE_DIAGRAMS", True)
        return cls(
            repo_root=repo_root,
            min_coverage_pct=float(mc if mc is not None else 70.0),
            max_failure_rate_pct=float(mf if mf is not None else 10.0),
            require_diagrams=bool(True if rd is None else rd),
            required_arch_sections=required_arch_sections,
            required_logic_sections=required_logic_sections,
        )

    def _read_json(self, p: Path) -> Any:
        try:
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            return None
        return None

    def _file_text(self, p: Path) -> str:
        try:
            return p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    def evaluate(self) -> Dict[str, Any]:
        now = datetime.now().isoformat()
        result: Dict[str, Any] = {
            "evaluated_at": now,
            "status": "passed",
            "gates": [],
            "metrics": {},
        }

        # Coverage metrics
        behavior = self._read_json(self.meta_dir / "behavior-graph.json") or {}
        manifest = self._read_json(self.meta_dir / "file_manifest.json") or []
        nodes = behavior.get("nodes", []) if isinstance(behavior, dict) else []
        code_nodes = [n for n in nodes if (n.get("type") == "file") and (n.get("extension") in [".py", ".js", ".ts", ".cs"])]
        manifest_code = [m for m in manifest if (m.get("type") == "code")]
        coverage_pct = 0.0
        try:
            if manifest_code:
                coverage_pct = (len(code_nodes) / len(manifest_code)) * 100.0
            else:
                coverage_pct = float(behavior.get("statistics", {}).get("coverage_percentage", 0.0))
        except Exception:
            coverage_pct = 0.0
        result["metrics"]["coverage_pct"] = round(coverage_pct, 2)
        result["metrics"]["code_nodes"] = len(code_nodes)
        result["metrics"]["manifest_code"] = len(manifest_code)

        if coverage_pct < self.min_coverage_pct:
            result["gates"].append({"gate": "min_coverage", "status": "failed", "value": coverage_pct, "threshold": self.min_coverage_pct})
            result["status"] = "failed"
        else:
            result["gates"].append({"gate": "min_coverage", "status": "passed", "value": coverage_pct, "threshold": self.min_coverage_pct})

        # Failure rate
        failure_rate = 0.0
        conv_report = self._read_json(self.meta_dir / "conversion_report.json") or {}
        stats = conv_report.get("stats", {}) if isinstance(conv_report, dict) else {}
        total = max(1, int(stats.get("total_files", 0)))
        try:
            failure_rate = (int(stats.get("failed", 0)) / total) * 100.0
        except Exception:
            failure_rate = 0.0
        result["metrics"]["failure_rate_pct"] = round(failure_rate, 2)
        if failure_rate > self.max_failure_rate_pct:
            result["gates"].append({"gate": "max_failure_rate", "status": "failed", "value": failure_rate, "threshold": self.max_failure_rate_pct})
            result["status"] = "failed"
        else:
            result["gates"].append({"gate": "max_failure_rate", "status": "passed", "value": failure_rate, "threshold": self.max_failure_rate_pct})

        # Diagrams presence
        diagrams_ok = True
        if self.require_diagrams:
            expected = ["system_context", "dependency_graph", "component_flow", "data_flow"]
            missing = []
            for base in expected:
                if not ((self.diagrams_dir / f"{base}.mmd").exists() or (self.diagrams_dir / f"{base}.png").exists() or (self.diagrams_dir / f"{base}.svg").exists()):
                    missing.append(base)
            diagrams_ok = len(missing) == 0
            if not diagrams_ok:
                result["gates"].append({"gate": "diagrams", "status": "failed", "missing": missing})
                result["status"] = "failed"
            else:
                result["gates"].append({"gate": "diagrams", "status": "passed"})

        # Doc sections
        arch = self.repo_root / "architecture.md"
        llogic = self.repo_root / "logic-and-workflows.md"
        arch_text = self._file_text(arch)
        logic_text = self._file_text(llogic)
        missing_arch = [s for s in self.required_arch_sections if s not in arch_text]
        missing_logic = [s for s in self.required_logic_sections if s not in logic_text]
        if missing_arch:
            result["gates"].append({"gate": "doc_sections_architecture", "status": "warning", "missing": missing_arch})
            if result["status"] == "passed":
                result["status"] = "passed_with_warnings"
        else:
            result["gates"].append({"gate": "doc_sections_architecture", "status": "passed"})
        if missing_logic:
            result["gates"].append({"gate": "doc_sections_logic", "status": "warning", "missing": missing_logic})
            if result["status"] == "passed":
                result["status"] = "passed_with_warnings"
        else:
            result["gates"].append({"gate": "doc_sections_logic", "status": "passed"})

        return result

    def write_reports(self, run_dir: Path, report: Dict[str, Any]) -> Dict[str, Path]:
        run_dir = Path(run_dir)
        json_path = run_dir / "validation_report.json"
        md_path = run_dir / "validation_report.md"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        md = self._render_md(report)
        md_path.write_text(md, encoding="utf-8")
        return {"json": json_path, "md": md_path}

    def _render_md(self, report: Dict[str, Any]) -> str:
        lines = [
            f"# Quality Gates Report",
            f"Generated: {report.get('evaluated_at','')}",
            f"Status: {report.get('status','')}\n",
            "## Metrics",
            f"- Coverage: {report.get('metrics',{}).get('coverage_pct',0)}% ({report.get('metrics',{}).get('code_nodes',0)}/{report.get('metrics',{}).get('manifest_code',0)})",
            f"- Failure rate: {report.get('metrics',{}).get('failure_rate_pct',0)}%\n",
            "## Gates",
        ]
        for g in report.get("gates", []):
            gate = g.get("gate")
            status = g.get("status")
            extra = []
            if "value" in g and "threshold" in g:
                extra.append(f"value={g['value']} threshold={g['threshold']}")
            if "missing" in g:
                extra.append(f"missing={', '.join(g['missing'])}")
            lines.append(f"- {gate}: {status}{(' (' + '; '.join(extra) + ')') if extra else ''}")
        lines.append("")
        return "\n".join(lines)
