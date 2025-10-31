"""Generate Mermaid diagrams from discovery artifacts.

Produces .mmd diagrams under `_normalized/diagrams/`:
- system_context.mmd
- dependency_graph.mmd
- component_flow.mmd
- data_flow.mmd

Input discovery artifacts (expected in `_normalized/.meta/`):
- behavior-graph.json
- system-integrations.json
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
import os


class DiagramGenerator:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.normalized = self.repo_root / "_normalized"
        self.meta_dir = self.normalized / ".meta"
        self.out_dir = self.normalized / "diagrams"
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.behavior = self._safe_read_json(self.meta_dir / "behavior-graph.json") or {}
        self.integrations = self._safe_read_json(self.meta_dir / "system-integrations.json") or {}
        # Tunables via env
        import os
        def _env_int(name: str, default: int) -> int:
            try:
                return int(os.environ.get(name, default))
            except Exception:
                return default
        def _env_bool(name: str, default: bool) -> bool:
            try:
                v = str(os.environ.get(name, str(int(default)))).strip().lower()
                if v in ("1","true","yes","on"): return True
                if v in ("0","false","no","off"): return False
            except Exception:
                pass
            return default
        self.max_nodes = _env_int("APPDOC_MMD_MAX_NODES", 60)
        self.max_edges = _env_int("APPDOC_MMD_MAX_EDGES", 120)
        self.include_prefixes = [p for p in (os.environ.get("APPDOC_DEP_INCLUDE_PREFIXES", "").split(",")) if p]
        self.only_files_targets = _env_bool("APPDOC_DEP_ONLY_FILE_TARGETS", False)
        self.only_code_nodes = _env_bool("APPDOC_DEP_ONLY_CODE_NODES", False)

        # Internal render/report state
        self._used_mmdc = self._has_mmdc()
        self._kroki_base = os.environ.get("KROKI_URL", "https://kroki.io")
        self._report = {
            "generated": [],
            "rendered": [],
            "errors": [],
            "settings": {
                "max_nodes": self.max_nodes,
                "max_edges": self.max_edges,
                "include_prefixes": self.include_prefixes,
                "only_file_targets": self.only_files_targets,
                "only_code_nodes": self.only_code_nodes,
                "used_mmdc": self._used_mmdc,
                "kroki_url": self._kroki_base,
            },
        }

    def _safe_read_json(self, path: Path) -> Dict[str, Any] | None:
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            return None
        return None

    def generate_all(self) -> List[str]:
        outputs: List[str] = []
        outputs.append(self._generate_system_context())
        outputs.append(self._generate_dependency_graph())
        outputs.append(self._generate_component_flow())
        outputs.append(self._generate_data_flow())
        outputs = [str(p) for p in outputs if p]
        try:
            rendered = self._render_outputs(outputs)
            outputs.extend(rendered)
        except Exception:
            # Rendering is optional; ignore failures
            pass
        # Write diagram report for diagnostics
        try:
            rep_path = self.meta_dir / "diagram_report.json"
            with open(rep_path, "w", encoding="utf-8") as f:
                json.dump(self._report, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return outputs

    def _generate_system_context(self) -> str:
        systems = self.integrations.get("external_systems", []) or []
        dbs = self.integrations.get("database_connections", []) or []
        apis = self.integrations.get("api_endpoints", []) or []
        queues = self.integrations.get("message_queues", []) or []

        mmd = ["graph LR", "  A[Application]:::app"]
        # External systems
        for i, s in enumerate(systems[:25]):
            node = f"ES{i}({s})"
            mmd.append(f"  {node}:::ext --> A")
        for i, s in enumerate(dbs[:15]):
            node = f"DB{i}([{s}])"
            mmd.append(f"  A --> {node}:::db")
        for i, s in enumerate(apis[:20]):
            node = f"API{i}{{{s}}}"
            mmd.append(f"  A --> {node}:::api")
        for i, s in enumerate(queues[:15]):
            node = f"MQ{i}[[{s}]]"
            mmd.append(f"  A <--> {node}:::mq")
        # styles
        mmd += [
            "classDef app fill:#2b6cb0,stroke:#1a202c,stroke-width:1,color:#fff",
            "classDef ext fill:#718096,stroke:#1a202c,stroke-width:1,color:#fff",
            "classDef db fill:#2f855a,stroke:#1a202c,stroke-width:1,color:#fff",
            "classDef api fill:#b7791f,stroke:#1a202c,stroke-width:1,color:#fff",
            "classDef mq fill:#805ad5,stroke:#1a202c,stroke-width:1,color:#fff",
        ]
        out = self.out_dir / "system_context.mmd"
        out.write_text("\n".join(mmd), encoding="utf-8")
        try:
            self._report["generated"].append(str(out))
        except Exception:
            pass
        return str(out)

    def _generate_dependency_graph(self) -> str:
        nodes = self.behavior.get("nodes", []) or []
        edges = self.behavior.get("edges", []) or []
        # Build a simplified graph of file dependencies and imports
        mmd = ["graph TD"]
        # Limit graph size for readability
        max_nodes = self.max_nodes
        max_edges = self.max_edges

        # Create a mapping for node ids in Mermaid
        def safe_id(idx: int) -> str:
            return f"N{idx}"

        file_nodes = [n for n in nodes if (n.get("type") == "file")]
        if self.only_code_nodes:
            file_nodes = [n for n in file_nodes if n.get("extension") in [".py", ".js", ".ts", ".cs"]]
        limited_nodes = file_nodes[:max_nodes]
        id_map: Dict[str, str] = {}
        for idx, n in enumerate(limited_nodes):
            nid = safe_id(idx)
            id_map[n.get("path", n.get("name", nid))] = nid
            label = n.get("name") or n.get("path") or nid
            mmd.append(f"  {nid}[{label}]")

        ecount = 0
        for e in edges:
            if ecount >= max_edges:
                break
            src = e.get("from")
            dst = e.get("to_module") or e.get("to_namespace") or e.get("to")
            if not src or not dst:
                continue
            # Optional filter by include prefixes (applied to src path)
            if self.include_prefixes:
                if not any((str(src).startswith(pref) for pref in self.include_prefixes)):
                    continue
            src_id = id_map.get(src)
            # For non-file endpoints (namespaces/modules), render as text nodes
            if dst in id_map:
                dst_id = id_map[dst]
                mmd.append(f"  {src_id} --> {dst_id}")
            else:
                if not self.only_files_targets:
                    dst_id = f"T{len(id_map)+ecount}"
                    label = dst.replace("\n", " ")
                    mmd.append(f"  {src_id} --> {dst_id}(({label}))")
            ecount += 1

        out = self.out_dir / "dependency_graph.mmd"
        out.write_text("\n".join(mmd), encoding="utf-8")
        try:
            self._report["generated"].append(str(out))
        except Exception:
            pass
        return str(out)

    def _generate_component_flow(self) -> str:
        # Approximate components by directory groupings of files
        nodes = self.behavior.get("nodes", []) or []
        mmd = ["flowchart LR"]
        groups: Dict[str, List[str]] = {}
        for n in nodes:
            if n.get("type") != "file":
                continue
            path = n.get("path") or n.get("name") or ""
            parts = Path(path).parts
            group = parts[0] if parts else "root"
            groups.setdefault(group, []).append(n.get("name") or Path(path).name)

        for g, files in list(groups.items())[:12]:
            mmd.append(f"  subgraph {g}")
            for i, fname in enumerate(files[:12]):
                mmd.append(f"    G{hash(g)%1000}_{i}([{fname}])")
            mmd.append("  end")

        out = self.out_dir / "component_flow.mmd"
        out.write_text("\n".join(mmd), encoding="utf-8")
        try:
            self._report["generated"].append(str(out))
        except Exception:
            pass
        return str(out)

    def _generate_data_flow(self) -> str:
        # If explicit data_flows exist, use them; otherwise synthesize from edges
        data_flows = self.behavior.get("data_flows", []) or []
        edges = self.behavior.get("edges", []) or []
        mmd = ["flowchart TD"]
        if data_flows:
            for i, df in enumerate(data_flows[:80]):
                src = df.get("from") or df.get("source") or f"S{i}"
                dst = df.get("to") or df.get("target") or f"D{i}"
                mmd.append(f"  {src} --> {dst}")
        else:
            count = 0
            for e in edges:
                src = e.get("from")
                dst = e.get("to_module") or e.get("to_namespace") or e.get("to")
                if not src or not dst:
                    continue
                mmd.append(f"  {src} --> {dst}")
                count += 1
                if count >= 120:
                    break

        out = self.out_dir / "data_flow.mmd"
        out.write_text("\n".join(mmd), encoding="utf-8")
        try:
            self._report["generated"].append(str(out))
        except Exception:
            pass
        return str(out)

    # ---------- Rendering helpers ----------
    def _render_outputs(self, mmd_paths: List[str]) -> List[str]:
        """Render Mermaid sources to PNG and SVG.

        Prefers local Mermaid CLI (`mmdc`) if available; otherwise falls back
        to Kroki web service if network is available.
        """
        rendered: List[str] = []
        # Try local mmdc first
        if self._used_mmdc:
            for p in mmd_paths:
                rendered.extend(self._render_with_mmdc(Path(p)))
            return rendered
        # Fallback to Kroki
        for p in mmd_paths:
            rendered.extend(self._render_with_kroki(Path(p)))
        return rendered

    def _has_mmdc(self) -> bool:
        """Return True if Mermaid CLI is available in PATH."""
        from shutil import which
        return which("mmdc") is not None

    def _render_with_mmdc(self, mmd_file: Path) -> List[str]:
        """Render a single .mmd file to PNG and SVG using Mermaid CLI."""
        import subprocess
        outs: List[str] = []
        for fmt in ("png", "svg"):
            out_path = mmd_file.with_suffix(f".{fmt}")
            try:
                subprocess.run(
                    ["mmdc", "-i", str(mmd_file), "-o", str(out_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if out_path.exists():
                    outs.append(str(out_path))
            except Exception as ex:
                try:
                    self._report["errors"].append({"file": str(mmd_file), "renderer": "mmdc", "fmt": fmt, "error": str(ex)})
                except Exception:
                    pass
        return outs

    def _render_with_kroki(self, mmd_file: Path) -> List[str]:
        """Render a single .mmd file to PNG and SVG using Kroki service."""
        outs: List[str] = []
        try:
            import requests
        except Exception:
            return outs

        kroki_base = self._kroki_base
        try:
            mmd_text = mmd_file.read_text(encoding="utf-8")
        except Exception:
            return outs

        for fmt in ("png", "svg"):
            url = f"{kroki_base}/mermaid/{fmt}"
            attempts = 0
            last_err = None
            while attempts < 3:
                attempts += 1
                try:
                    # Prefer text/plain body
                    resp = requests.post(url, data=mmd_text.encode("utf-8"), headers={"Content-Type": "text/plain"}, timeout=20)
                    if resp.status_code == 200 and resp.content:
                        out_path = mmd_file.with_suffix(f".{fmt}")
                        with open(out_path, "wb") as f:
                            f.write(resp.content)
                        outs.append(str(out_path))
                        break
                    # Fallback to JSON body
                    resp = requests.post(url, json={"diagram_source": mmd_text}, timeout=20)
                    if resp.status_code == 200 and resp.content:
                        out_path = mmd_file.with_suffix(f".{fmt}")
                        with open(out_path, "wb") as f:
                            f.write(resp.content)
                        outs.append(str(out_path))
                        break
                    last_err = Exception(f"HTTP {resp.status_code}")
                except Exception as ex:
                    last_err = ex
                # Backoff
                try:
                    import time
                    time.sleep(0.5 * attempts)
                except Exception:
                    pass
            # If failed after retries, write a small .err file for diagnostics
            if attempts >= 3 and not any(str(mmd_file.with_suffix(f".{fmt}")) == o for o in outs):
                err_path = mmd_file.with_suffix(f".{fmt}.err")
                try:
                    err_path.write_text(f"Kroki render failed: {last_err}", encoding="utf-8")
                except Exception:
                    pass
                try:
                    self._report["errors"].append({"file": str(mmd_file), "renderer": "kroki", "fmt": fmt, "error": str(last_err)})
                except Exception:
                    pass
        # Track rendered outputs
        try:
            for o in outs:
                self._report["rendered"].append(o)
        except Exception:
            pass
        return outs
