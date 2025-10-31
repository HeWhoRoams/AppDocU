#!/usr/bin/env python3
"""
One-Command Documentation Workflow
Entry point for the documentation generation system.
"""

import typer
from pathlib import Path
from orchestrator.logger import setup_logger
from orchestrator.config import Config, CentralConfig
from orchestrator.file_scanner import FileScanner
from orchestrator.csharp_runner import CSharpRunner
from orchestrator.artifact_processor import ArtifactProcessor
from orchestrator.llm_client import LLMClient
from orchestrator.error_handler import ErrorHandler
from orchestrator.packager import Packager
from orchestrator.quality_gates import QualityGates
from orchestrator.self_tester import SelfTester
import time
from datetime import datetime
import json

app = typer.Typer(help="AppDocU - One-Command Documentation System")
logger = setup_logger(__name__)


@app.command()
def generate(
    path: Path = typer.Option(..., "--path", "-p", help="Path to repository or project"),
    output: Path = typer.Option("./docs_output", "--output", "-o", help="Output directory"),
    llm_endpoint: str = typer.Option(None, "--llm-endpoint", help="LLM API endpoint"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Run without calling LLM"),
    max_retries: int = typer.Option(3, "--max-retries", help="Max retries for LLM calls"),
):
    """Generate documentation for the specified repository."""
    
    # Load central config (file/env) and propagate to env first
    central = CentralConfig.load(path)
    central.apply_env()

    # Initialize configuration for C# + LLM flow
    config = Config(
        repo_path=path,
        output_path=output,
        llm_endpoint=llm_endpoint,
        verbose=verbose,
        dry_run=dry_run,
        max_retries=max_retries
    )
    
    if verbose:
        logger.setLevel("DEBUG")
    
    logger.info(f"Starting documentation generation for: {path}")
    logger.info(f"   Output: {output}")
    
    try:
        # Phase 1: Scan for C# files
        logger.info("Phase 1: Scanning repository for C# files...")
        scanner = FileScanner(config)
        csharp_files = scanner.scan_for_csharp_files()
        logger.info(f"Found {len(csharp_files)} C# files")
        
        if not csharp_files:
            logger.warning("No C# files found in repository")
            raise typer.Exit(code=0)
        
        # Phase 2: Run C# analysis
        logger.info("Phase 2: Running Roslyn analysis...")
        runner = CSharpRunner(config)
        artifacts = runner.analyze_files(csharp_files)
        logger.info(f"Generated {len(artifacts)} artifacts")
        
        # Phase 3: Process artifacts
        logger.info("Phase 3: Processing artifacts...")
        processor = ArtifactProcessor(config)
        processed_data = processor.process_artifacts(artifacts)
        
        # Phase 4: Generate documentation via LLM
        if not dry_run:
            logger.info("Phase 4: Generating documentation via LLM...")
            llm_client = LLMClient(config)
            documentation = llm_client.generate_documentation(processed_data)
            
            # Phase 5: Write output
            logger.info("Phase 5: Writing documentation files...")
            processor.write_documentation(documentation)
        else:
            logger.info("Dry run mode - skipping LLM generation")
        
        logger.info(f"✅ Documentation generated successfully in: {output}")
        
    except Exception as e:
        error_handler = ErrorHandler(config)
        error_handler.handle_fatal_error(e)
        raise typer.Exit(code=1)


@app.command()
def iterate(
    path: Path = typer.Option(..., "--path", "-p", help="Path to repository or project"),
    output: Path = typer.Option("./docs_output", "--output", "-o", help="Output directory (for generated docs)"),
    llm_endpoint: str = typer.Option(None, "--llm-endpoint", help="LLM API endpoint (optional; use with --llm)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    run_llm: bool = typer.Option(False, "--llm/--no-llm", help="Run LLM generation each iteration (default: off for speed)"),
):
    """Interactive loop: discovery -> (optional) LLM -> ROI report -> repeat?"""

    # Load central config and propagate env
    central = CentralConfig.load(path)
    central.apply_env()
    # Configure logging
    if verbose:
        logger.setLevel("DEBUG")

    # Ensure normalized meta path (used by discovery)
    normalized_root = path / "_normalized"
    meta_dir = normalized_root / ".meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    history_file = meta_dir / "run_history.json"

    # Helper: compute ROI metrics from current meta files
    def compute_roi() -> dict:
        import json
        roi = {"timestamp": None, "coverage": {}, "completeness": {}, "complexity": {}, "integrations": {}, "per_language": {}, "diff": {}}
        try:
            with open(meta_dir / "behavior-graph.json", "r", encoding="utf-8") as f:
                bg = json.load(f)
        except Exception:
            bg = {}
        try:
            with open(meta_dir / "file_manifest.json", "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = []
        # Basic counts
        stats = bg.get("statistics", {}) if isinstance(bg, dict) else {}
        nodes = bg.get("nodes", []) if isinstance(bg, dict) else []
        edges = bg.get("edges", []) if isinstance(bg, dict) else []
        code_nodes = [n for n in nodes if (n.get("type") == "file") and (n.get("extension") in [".py", ".js", ".ts", ".cs"])]
        # Coverage: if manifest present, compare nodes to code files in manifest (overall and per-language)
        manifest_code = [m for m in manifest if (m.get("type") == "code")]
        coverage_pct = 0.0
        try:
            if manifest_code:
                coverage_pct = (len(code_nodes) / len(manifest_code)) * 100.0
            else:
                coverage_pct = float(stats.get("coverage_percentage", 0.0))
        except Exception:
            coverage_pct = 0.0
        # Per-language coverage
        def ext_of(n: dict) -> str:
            return (n.get("extension") or "").lower()
        langs = [".py", ".js", ".ts", ".cs"]
        per_lang = {}
        for ext in langs:
            n_nodes = [n for n in code_nodes if ext_of(n) == ext]
            m_nodes = [m for m in manifest_code if str(m.get("file", "")).lower().endswith(ext)]
            try:
                cov = (len(n_nodes) / len(m_nodes) * 100.0) if m_nodes else (100.0 if n_nodes else 0.0)
            except Exception:
                cov = 0.0
            per_lang[ext] = {"nodes": len(n_nodes), "manifest": len(m_nodes), "coverage_pct": round(cov, 2)}
        # Failure rate: from conversion report if present
        failure_rate = 0.0
        try:
            with open(meta_dir / "conversion_report.json", "r", encoding="utf-8") as f:
                cr = json.load(f)
            st = cr.get("stats", {})
            total = max(1, int(st.get("total_files", 0)))
            failure_rate = (int(st.get("failed", 0)) / total) * 100.0
        except Exception:
            failure_rate = 0.0
        # Completeness: proportion of code nodes with functions/classes/imports/metrics
        completed = 0
        for n in code_nodes:
            if n.get("functions") or n.get("classes") or n.get("imports") or n.get("metrics"):
                completed += 1
        completeness_pct = (completed / len(code_nodes) * 100.0) if code_nodes else 100.0
        # Complexity averages (overall and per-language)
        def node_complexity(n: dict) -> float:
            try:
                c = n.get("metrics", {}).get("complexity")
                return float(c) if c is not None else 0.0
            except Exception:
                return 0.0
        complexities = [node_complexity(n) for n in code_nodes if node_complexity(n) > 0.0]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0.0
        per_lang_cplx = {}
        for ext in langs:
            vals = [node_complexity(n) for n in code_nodes if ext_of(n) == ext and node_complexity(n) > 0.0]
            per_lang_cplx[ext] = round(sum(vals) / len(vals), 2) if vals else 0.0
        # Integrations counts
        try:
            with open(meta_dir / "system-integrations.json", "r", encoding="utf-8") as f:
                si = json.load(f)
        except Exception:
            si = {}
        integrations_counts = {
            "external_systems": len(si.get("external_systems", []) or []),
            "database_connections": len(si.get("database_connections", []) or []),
            "api_endpoints": len(si.get("api_endpoints", []) or []),
            "message_queues": len(si.get("message_queues", []) or []),
        }
        # Package ROI metrics
        roi["timestamp"] = __import__("datetime").datetime.now().isoformat()
        roi["coverage"] = {
            "code_nodes": len(code_nodes),
            "manifest_code": len(manifest_code),
            "coverage_pct": round(coverage_pct, 2),
            "edges": len(edges),
        }
        roi["completeness"] = {
            "completed_nodes": completed,
            "total_code_nodes": len(code_nodes),
            "completeness_pct": round(completeness_pct, 2),
            "failure_rate_pct": round(failure_rate, 2)
        }
        roi["complexity"] = {
            "avg_overall": round(avg_complexity, 2),
            "per_language": per_lang_cplx,
        }
        roi["integrations"] = integrations_counts
        roi["per_language"] = per_lang
        return roi

    # Helper: load history
    def load_history() -> dict:
        import json
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"runs": []}
        return {"runs": []}

    # Helper: append to history with diffs
    def append_history(current: dict):
        import json
        hist = load_history()
        runs = hist.get("runs", [])
        if runs:
            prev = runs[-1]
            # Diff metrics
            try:
                d_nodes = current["coverage"]["code_nodes"] - prev["coverage"]["code_nodes"]
                d_edges = current["coverage"]["edges"] - prev["coverage"]["edges"]
                # Per-language deltas
                lang_deltas = {}
                for ext in current.get("per_language", {}).keys():
                    try:
                        lang_deltas[ext] = {
                            "delta_nodes": current["per_language"][ext]["nodes"] - prev.get("per_language", {}).get(ext, {}).get("nodes", 0),
                            "delta_manifest": current["per_language"][ext]["manifest"] - prev.get("per_language", {}).get(ext, {}).get("manifest", 0),
                        }
                    except Exception:
                        continue
                # Integration deltas
                integ_prev = prev.get("integrations", {})
                integ_cur = current.get("integrations", {})
                integ_deltas = {k: integ_cur.get(k, 0) - integ_prev.get(k, 0) for k in ("external_systems", "database_connections", "api_endpoints", "message_queues")}
                # Complexity delta
                cplx_delta = current.get("complexity", {}).get("avg_overall", 0.0) - prev.get("complexity", {}).get("avg_overall", 0.0)
                current["diff"] = {"delta_code_nodes": d_nodes, "delta_edges": d_edges, "per_language": lang_deltas, "integrations": integ_deltas, "delta_complexity": round(cplx_delta, 2)}
            except Exception:
                current["diff"] = {}
        runs.append(current)
        hist["runs"] = runs
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(hist, f, indent=2, ensure_ascii=False)
        return current

    # One iteration: run Pass 1 discovery and optionally LLM generation
    def do_iteration(iter_idx: int):
        logger.info(f"Iteration {iter_idx}: Running discovery (Pass 1)")
        # Use AppDocU Pass 1 directly
        try:
            from appdoc import AppDocUOrchestrator
            orch = AppDocUOrchestrator(str(path))
            res = orch.run_pass_1_discovery()
            if res.get("status") != "completed":
                typer.echo(f"Discovery failed: {res.get('error')}")
                raise typer.Exit(code=1)
        except Exception as e:
            typer.echo(f"Discovery exception: {e}")
            raise typer.Exit(code=1)

        # Optionally run LLM doc generation after discovery
        if run_llm:
            logger.info("Iteration: Running LLM documentation generation")
            cfg = Config(
                repo_path=path,
                output_path=output,
                llm_endpoint=llm_endpoint,
                verbose=verbose
            )
            try:
                scanner = FileScanner(cfg)
                runner = CSharpRunner(cfg)
                processor = ArtifactProcessor(cfg)
                files = scanner.scan_for_csharp_files()
                artifacts = runner.analyze_files(files)
                processed = processor.process_artifacts(artifacts)
                if llm_endpoint and not cfg.dry_run:
                    llm_client = LLMClient(cfg)
                    documentation = llm_client.generate_documentation(processed)
                    processor.write_documentation(documentation)
            except Exception as e:
                error_handler = ErrorHandler(cfg)
                error_handler.handle_fatal_error(e)
                # Continue; ROI still computed

        # Compute ROI and store history
        roi = compute_roi()
        entry = append_history(roi)
        # Present ROI summary
        typer.echo("\nROI Summary:")
        typer.echo(f"  Coverage: {entry['coverage'].get('coverage_pct',0)}% ({entry['coverage'].get('code_nodes',0)}/{entry['coverage'].get('manifest_code',0)}) edges={entry['coverage'].get('edges',0)}")
        # Per-language quick view
        pl = entry.get('per_language', {})
        if pl:
            view = []
            for ext in [".py", ".js", ".ts", ".cs"]:
                if ext in pl:
                    view.append(f"{ext}:{pl[ext]['coverage_pct']}%({pl[ext]['nodes']}/{pl[ext]['manifest']})")
            if view:
                typer.echo("  Per-language: " + ", ".join(view))
        typer.echo(f"  Completeness: {entry['completeness'].get('completeness_pct',0)}%  Failure: {entry['completeness'].get('failure_rate_pct',0)}%  Complexity(avg): {entry.get('complexity',{}).get('avg_overall',0)}")
        # Integrations
        integ = entry.get('integrations', {})
        if integ:
            typer.echo(f"  Integrations: ext={integ.get('external_systems',0)} db={integ.get('database_connections',0)} api={integ.get('api_endpoints',0)} mq={integ.get('message_queues',0)}")
        # Deltas
        if entry.get('diff'):
            typer.echo(f"  Δ nodes: {entry['diff'].get('delta_code_nodes',0)}  Δ edges: {entry['diff'].get('delta_edges',0)}  Δ complexity: {entry['diff'].get('delta_complexity',0)}")
            if entry['diff'].get('integrations'):
                d = entry['diff']['integrations']
                typer.echo(f"  Δ integrations: ext={d.get('external_systems',0)} db={d.get('database_connections',0)} api={d.get('api_endpoints',0)} mq={d.get('message_queues',0)}")

    # Loop
    idx = 1
    while True:
        do_iteration(idx)
        idx += 1
        if not typer.confirm("Run another iteration?", default=False):
            break


@app.command()
def package(
    path: Path = typer.Option(..., "--path", "-p", help="Path to repository or project"),
    llm_output: Path = typer.Option(None, "--llm-output", help="Optional generated docs output directory"),
):
    """Create a timestamped packaging snapshot with manifest and index."""
    try:
        # Apply central config
        central = CentralConfig.load(path)
        central.apply_env()
        pk = Packager(path)
        res = pk.package(llm_output)
        logger.info(f"Packaged to: {res.run_dir}")
        logger.info(f"Manifest: {res.manifest_path}")
        logger.info(f"Index: {res.index_path}")
        # Run quality gates and write reports into the run folder
        try:
            gates = QualityGates.from_env(path)
            report = gates.evaluate()
            out = gates.write_reports(res.run_dir, report)
            logger.info(f"Quality report: {out['json']}")
            logger.info(f"Quality summary: {out['md']}")
            # Exit non-zero if failed
            if report.get('status') == 'failed':
                typer.echo("Quality gates failed. See validation_report.md for details.")
                raise typer.Exit(code=2)
        except Exception as ge:
            logger.warning(f"Quality gates execution failed: {ge}")
    except Exception as e:
        logger.error(f"Packaging failed: {e}")
        raise typer.Exit(code=1)


@app.command()
def full(
    path: Path = typer.Option(..., "--path", "-p", help="Path to repository or project"),
    output: Path = typer.Option("./docs_output", "--output", "-o", help="Output directory for LLM docs (optional)"),
    llm_endpoint: str = typer.Option(None, "--llm-endpoint", help="LLM API endpoint (optional)"),
    run_llm: bool = typer.Option(False, "--llm/--no-llm", help="Run LLM generation as part of the pipeline"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging")
):
    """Run full pipeline: Pass 1 → Pass 2 → Pass 3 → diagrams → package → quality gates."""
    # Apply central config (env + defaults)
    central = CentralConfig.load(path)
    central.apply_env()
    if verbose:
        logger.setLevel("DEBUG")
    # Reduce noise from requests
    try:
        import logging as _logging
        _logging.getLogger("requests").setLevel(_logging.WARNING)
    except Exception:
        pass

    def _banner(title: str):
        typer.echo("\n" + "=" * 60)
        typer.echo(f"{title}")
        typer.echo("=" * 60)

    start_all = time.perf_counter()
    _banner("AppDocU Full Workflow")
    typer.echo(f"Start: {datetime.now().isoformat()}")

    # Pass 1: Discovery
    t0 = time.perf_counter()
    _banner("Pass 1: Discovery")
    try:
        from appdoc import AppDocUOrchestrator
        orch = AppDocUOrchestrator(str(path))
        res1 = orch.run_pass_1_discovery()
        if res1.get("status") != "completed":
            typer.echo(f"Pass 1 failed: {res1.get('error')}")
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Pass 1 exception: {e}")
        raise typer.Exit(code=1)
    typer.echo(f"Pass 1 duration: {time.perf_counter() - t0:0.2f}s")

    # Pass 2: Enrichment (also generates initial diagrams)
    t0 = time.perf_counter()
    _banner("Pass 2: Enrichment")
    try:
        res2 = orch.run_pass_2_enrichment()
        if res2.get("status") != "completed":
            typer.echo(f"Pass 2 failed: {res2.get('error')}")
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Pass 2 exception: {e}")
        raise typer.Exit(code=1)
    typer.echo(f"Pass 2 duration: {time.perf_counter() - t0:0.2f}s")

    # Optional: Pass 3: Cognitive Audit (if implemented and safe)
    t0 = time.perf_counter()
    _banner("Pass 3: Cognitive Audit")
    try:
        if hasattr(orch, "run_pass_3_cognitive_audit"):
            res3 = orch.run_pass_3_cognitive_audit()
            if res3.get("status") != "completed":
                typer.echo(f"Pass 3 warning: {res3.get('error')}")
        else:
            typer.echo("Pass 3 not implemented; skipping")
    except Exception as e:
        typer.echo(f"Pass 3 exception (continuing): {e}")
    typer.echo(f"Pass 3 duration: {time.perf_counter() - t0:0.2f}s")

    # Optional: LLM documentation generation
    if run_llm and llm_endpoint:
        t0 = time.perf_counter()
        _banner("LLM Documentation Generation")
        cfg = Config(
            repo_path=path,
            output_path=output,
            llm_endpoint=llm_endpoint,
            verbose=verbose
        )
        try:
            scanner = FileScanner(cfg)
            runner = CSharpRunner(cfg)
            processor = ArtifactProcessor(cfg)
            files = scanner.scan_for_csharp_files()
            artifacts = runner.analyze_files(files)
            processed = processor.process_artifacts(artifacts)
            llm_client = LLMClient(cfg)
            documentation = llm_client.generate_documentation(processed)
            processor.write_documentation(documentation)
        except Exception as e:
            err = ErrorHandler(cfg)
            err.handle_fatal_error(e)
            # Continue; docs are optional
        typer.echo(f"LLM duration: {time.perf_counter() - t0:0.2f}s")

    # Ensure diagrams rendered (re-run generator to render images with current env)
    t0 = time.perf_counter()
    _banner("Diagram Rendering")
    try:
        from orchestrator.diagram_generator import DiagramGenerator
        dg = DiagramGenerator(path)
        outs = dg.generate_all()
        typer.echo(f"Diagrams generated: {len(outs)} files")
    except Exception as e:
        typer.echo(f"Diagram generation error (continuing): {e}")
    typer.echo(f"Diagram duration: {time.perf_counter() - t0:0.2f}s")

    # Package + quality gates
    t0 = time.perf_counter()
    _banner("Packaging + Quality Gates")
    try:
        pk = Packager(path)
        res = pk.package(output)
        logger.info(f"Packaged to: {res.run_dir}")
        # Quality gates
        gates = QualityGates.from_env(path)
        report = gates.evaluate()
        out = gates.write_reports(res.run_dir, report)
        typer.echo(f"Quality report: {out['md']}")
        if report.get('status') == 'failed':
            typer.echo("Quality gates failed. See report for details.")
            raise typer.Exit(code=2)
    except typer.Exit:
        raise
    except Exception as e:
        logger.error(f"Packaging/validation failed: {e}")
        raise typer.Exit(code=1)
    typer.echo(f"Packaging duration: {time.perf_counter() - t0:0.2f}s")

    typer.echo("\nCompleted successfully.")
    typer.echo(f"Total duration: {time.perf_counter() - start_all:0.2f}s")

@app.command()
def validate(
    path: Path = typer.Option(..., "--path", "-p", help="Path to repository or project"),
    min_coverage: float = typer.Option(None, "--min-coverage", help="Minimum coverage percent to pass gates (env APPDOC_MIN_COVERAGE)"),
    max_failure: float = typer.Option(None, "--max-failure", help="Maximum failure rate percent (env APPDOC_MAX_FAILURE)"),
    require_diagrams: bool = typer.Option(None, "--require-diagrams/--no-require-diagrams", help="Require diagrams gate (env APPDOC_REQUIRE_DIAGRAMS)")
):
    """Run quality gates without packaging. Writes reports under _normalized/.meta/."""
    try:
        # Apply central config first; CLI flags override via parameters below
        central = CentralConfig.load(path)
        central.apply_env()
        gates = QualityGates.from_env(
            repo_root=path,
            min_coverage_pct=min_coverage,
            max_failure_rate_pct=max_failure,
            require_diagrams=require_diagrams,
        )
        report = gates.evaluate()
        # Write to meta dir
        meta_dir = path / "_normalized" / ".meta"
        meta_dir.mkdir(parents=True, exist_ok=True)
        outs = gates.write_reports(meta_dir, report)
        logger.info(f"Validation report: {outs['json']}")
        logger.info(f"Summary: {outs['md']}")
        if report.get('status') == 'failed':
            typer.echo("Quality gates failed.")
            raise typer.Exit(code=2)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise typer.Exit(code=1)


@app.command()
def selftest(
    path: Path = typer.Option(..., "--path", "-p", help="Path to repository or project"),
    min_words: int = typer.Option(150, "--min-words", help="Minimum words required in docs"),
    require_diagrams: bool = typer.Option(True, "--require-diagrams/--no-require-diagrams", help="Require diagrams present"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging")
):
    """Run the workflow against the repo and evaluate outputs for non-trivial content."""
    # Apply central config
    central = CentralConfig.load(path)
    central.apply_env()
    if verbose:
        logger.setLevel("DEBUG")

    # Run full pipeline (without LLM) first
    try:
        full(path=path, output=Path("./docs_output"), llm_endpoint=None, run_llm=False, verbose=verbose)  # type: ignore[arg-type]
    except SystemExit as e:
        # Typer Exit propagates as SystemExit; continue to selftest report either way
        if int(getattr(e, "code", 0)) not in (0, 2):
            # 2 means quality gates failed; still evaluate docs
            pass
    except Exception as e:
        logger.warning(f"Full pipeline encountered an error: {e}. Continuing to self-test evaluation.")

    # Evaluate outputs
    tester = SelfTester(path, min_words=min_words, require_diagrams=require_diagrams)
    report = tester.evaluate()
    outs = tester.write_reports(report)
    logger.info(f"Self-test report: {outs['md']}")
    if report.get('status') != 'passed':
        typer.echo("Self-test failed. See selftest_report.md for details.")
        raise typer.Exit(code=2)
    typer.echo("Self-test passed.")


@app.command()
def config(
    path: Path = typer.Option(".", "--path", "-p", help="Path to repository or project"),
    apply: bool = typer.Option(True, "--apply/--no-apply", help="Apply resolved config to environment before printing"),
    pretty: bool = typer.Option(True, "--pretty/--no-pretty", help="Pretty-print JSON output")
):
    """Print the resolved central configuration (from file/env/defaults)."""
    central = CentralConfig.load(path)
    if apply:
        central.apply_env()
    data = central.to_dict()
    text = json.dumps(data, indent=2 if pretty else None)
    typer.echo(text)

if __name__ == "__main__":
    app()

