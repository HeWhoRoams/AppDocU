<!--
Sync Impact Report
Version change: 1.1 → 1.2 (MAJOR: Architectural enforcement, language boundary laws)
Added sections: Language Boundary Law, Implementation Order Doctrine, Stub Detection Protocol
Modified sections: Operational Doctrine (added verification gates), Evaluation Metrics (added architectural compliance)
Reason: Emergency amendment to prevent stub file generation and architectural violations
-->
Core Principles
Truth over appearance
Never infer without evidence. NEVER generate stub files and claim success.
Recursion is lawful
You may revisit prior conclusions to strengthen confidence, but must never overwrite verified human edits.
Auditability is sacred
Every claim must have traceable evidence (file, line, or runtime link). Empty files have zero evidence.
Non-destructive iteration
Always generate additive, versioned artifacts. Additive means adding REAL CONTENT, not empty files.
Governance by confidence
No artifact is "final" unless its mean confidence ≥ 0.8. Stub files have confidence = 0.0.
Human sovereignty
When evidence is ambiguous, defer to human oversight and preserve all alternate hypotheses.
Agental interoperability
All outputs must be consumable by both humans (Markdown, prose) and agents (JSON, schemas, graphs).
NEW: Architecture over expedience
The specified architecture MUST be implemented. Workarounds that violate architectural boundaries are FORBIDDEN.
Language Boundary Law (NEW)
Article 1: Strict Separation of Concerns
The AppDocU system consists of TWO components with ZERO overlap:

C# Worker (DocTool.exe)

MUST perform ALL Roslyn-based code analysis
MUST perform ALL AST inspection and traversal
MUST generate normalized JSON artifacts
MUST use Microsoft.CodeAnalysis.CSharp packages
FORBIDDEN to call Python or LLM APIs


Python Orchestrator (run_docs.py)

MUST provide the single CLI entry point
MUST call C# Worker via subprocess
MUST handle LLM API interaction
MUST aggregate results and write final documentation
FORBIDDEN to perform Roslyn analysis or AST inspection



Article 2: Communication Contract
C# Worker Output Specification:

STDOUT: JSON response with status, artifacts, errors
STDERR: Structured JSON logs only
Exit Codes: 0=success, 1=error, 2=file not found, 3=compilation error, 4=invalid args

Python Orchestrator Responsibilities:

Parse C# Worker exit codes
Capture and log STDERR streams
Parse STDOUT JSON artifacts
Continue on non-fatal errors
Aggregate all artifacts before LLM calls

Article 3: Violation Consequences
Any implementation that violates Language Boundary Law is VOID and must be deleted.
Examples of VOID implementations:

❌ Python code attempting Roslyn analysis
❌ "Standalone Python version" without C# Worker
❌ C# code making LLM API calls
❌ Mixed-language analysis logic

Implementation Order Doctrine (NEW)
Phase 1: C# Worker Foundation (MANDATORY FIRST)
Gate 1.1: Project Structure
