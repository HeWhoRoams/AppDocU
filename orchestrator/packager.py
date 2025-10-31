"""Packaging and manifest writer for documentation runs.

Creates a timestamped snapshot under `docs_runs/YYYYMMDD-HHMMSS/` with
subfolders:
  - meta/       -> _normalized/.meta/*
  - diagrams/   -> _normalized/diagrams/*
  - context/    -> _normalized/context/*
  - docs/       -> architecture.md, logic-and-workflows.md, change-impact-map.md,
                   developer-preflight.md, cognitive-audit.md (if present)
  - llm/        -> generated docs in external output folder (if provided)
  - artifacts/  -> additional analyzer artifacts (e.g., csharp)

Writes a `manifest.json` with file list (relative path), sizes, sha256, and last_run_date,
and a human-friendly `index.md` summarizing contents.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json
import shutil


@dataclass
class PackageResult:
    run_dir: Path
    manifest_path: Path
    index_path: Path
    files: List[Dict[str, Any]]


class Packager:
    def __init__(self, repo_root: Path, runs_root: Optional[Path] = None) -> None:
        self.repo_root = Path(repo_root)
        self.normalized = self.repo_root / "_normalized"
        self.meta_dir = self.normalized / ".meta"
        self.diagrams_dir = self.normalized / "diagrams"
        self.context_dir = self.normalized / "context"
        self.runs_root = Path(runs_root) if runs_root else (self.repo_root / "docs_runs")
        self.runs_root.mkdir(parents=True, exist_ok=True)

    def package(self, llm_output: Optional[Path] = None) -> PackageResult:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = self.runs_root / timestamp
        # Subfolders
        dst_meta = run_dir / "meta"
        dst_diagrams = run_dir / "diagrams"
        dst_context = run_dir / "context"
        dst_docs = run_dir / "docs"
        dst_llm = run_dir / "llm"
        dst_artifacts = run_dir / "artifacts"
        for d in (dst_meta, dst_diagrams, dst_context, dst_docs, dst_llm, dst_artifacts):
            d.mkdir(parents=True, exist_ok=True)

        files: List[Dict[str, Any]] = []

        # Copy helpers
        def copy_tree(src: Path, dst: Path, category: str, exts: Optional[List[str]] = None):
            if not src.exists():
                return
            for p in src.rglob('*'):
                if p.is_dir():
                    continue
                if exts and p.suffix.lower() not in exts:
                    continue
                rel = p.relative_to(src)
                target = dst / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
                files.append(self._file_entry(run_dir, target, category))

        # meta
        copy_tree(self.meta_dir, dst_meta, category="meta")
        # diagrams (.mmd and rendered images)
        copy_tree(self.diagrams_dir, dst_diagrams, category="diagrams", exts=None)
        # context
        copy_tree(self.context_dir, dst_context, category="context")

        # docs in repo root
        doc_names = [
            "architecture.md",
            "logic-and-workflows.md",
            "change-impact-map.md",
            "developer-preflight.md",
            "cognitive-audit.md",
        ]
        for name in doc_names:
            src = self.repo_root / name
            if src.exists() and src.is_file():
                dst = dst_docs / name
                shutil.copy2(src, dst)
                files.append(self._file_entry(run_dir, dst, category="docs"))

        # llm output (optional): copy everything under provided output path
        if llm_output:
            llm_output = Path(llm_output)
            copy_tree(llm_output, dst_llm, category="llm")

        # artifacts: copy selected analyzer artifacts (e.g., meta/csharp folder)
        csharp_dir = self.meta_dir / "csharp"
        copy_tree(csharp_dir, dst_artifacts / "csharp", category="artifacts")

        # Write manifest
        manifest = {
            "last_run_date": timestamp,
            "root": str(run_dir),
            "files": files,
        }
        manifest_path = run_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # Write index
        index_md = self._build_index_md(manifest)
        index_path = run_dir / "index.md"
        index_path.write_text(index_md, encoding='utf-8')

        return PackageResult(run_dir=run_dir, manifest_path=manifest_path, index_path=index_path, files=files)

    def _file_entry(self, run_dir: Path, path: Path, category: str) -> Dict[str, Any]:
        st = path.stat()
        sha = self._sha256(path)
        return {
            "path": str(path.relative_to(run_dir)),
            "category": category,
            "size_bytes": st.st_size,
            "size_kb": st.st_size // 1024,
            "sha256": sha,
        }

    def _sha256(self, p: Path) -> str:
        h = hashlib.sha256()
        try:
            with open(p, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def _build_index_md(self, manifest: Dict[str, Any]) -> str:
        lines = [
            f"# Documentation Run {manifest.get('last_run_date', '')}",
            "",
            "This snapshot contains the analysis meta, diagrams, prompts, and generated docs.",
            "",
            "## Contents",
        ]
        cats = ["meta", "diagrams", "context", "docs", "llm", "artifacts"]
        files = manifest.get("files", [])
        for cat in cats:
            cat_files = [f for f in files if f.get("category") == cat]
            if not cat_files:
                continue
            lines.append(f"### {cat.title()}")
            for fentry in cat_files[:200]:
                lines.append(f"- {fentry.get('path')} ({fentry.get('size_kb')} KB)")
            lines.append("")
        lines.append("")
        lines.append("---")
        lines.append("Generated by AppDocU Packager.")
        return "\n".join(lines)

