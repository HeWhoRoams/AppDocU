# Diagram Orchestrator (All Diagrams)

## Objective
Generate all required system diagrams using the behavioral data from Pass 1 discovery phase. This orchestrator should coordinate the generation of multiple diagram types and ensure consistency across all visualizations using behavioral evidence.

## Data Sources (Preconditions)
- `.meta/behavior-graph.json` - Behavioral relationships and IO operations (required)
- `.meta/system-integrations.json` - External dependencies and integrations (required)
- `.meta/component-map.json` - Component definitions and relationships
- `.meta/dependency-graph.json` - Structural dependencies
- `.meta/dependency-graph.md` - Mermaid format dependencies
- `.meta/config-registry.json` - Configuration context
- `.meta/tests.map.json` - Test coverage for behavioral validation


## Diagram Types to Generate
1. **Dependency Graph** - Component relationships and behavioral flows from behavior-graph.json
2. **Layered Architecture** - Controller → Service → Repo → External layering with Mermaid diagrams
3. **External Integrations** - System integrations and external dependencies
4. **Dataflow Sequence** - Per major flow using S→I→T→O→P patterns from logic-and-workflows
5. **Component Flow** - Data flow between components with IO operations
6. **Deployment Topology** - Physical deployment structure

### Diagram Type to Prompt File Mapping
1. Dependency Graph → diagrams/generate.dependency.graph.prompt.md
2. Layered Architecture → diagrams/generate.layered.architecture.prompt.md
3. External Integrations → diagrams/generate.system.context.prompt.md
4. Dataflow Sequence → diagrams/generate.dataflow.sequence.prompt.md
5. Component Flow → diagrams/generate.component.flow.prompt.md
6. Deployment Topology → diagrams/generate.deployment.topology.prompt.md


## Output Requirements
- Generate all diagrams in `.mmd` (Mermaid) format with confidence ≥ 0.75
- Create index file `diagrams.index.json` with metadata and confidence scores
- Create summary file `diagrams.summary.md` with descriptions and confidence metrics
- Append diagram section to `audit-report.md` using an idempotent merge strategy:
	- Use unique markers (e.g., `<!-- diagrams:start:{ID} -->` and `<!-- diagrams:end:{ID} -->` or a named heading) to delimit the diagram section.
	- Before appending, search for an existing marker or heading using a regex-based search.
	- If found, replace the content between markers atomically with the new diagram section.
	- If identical content already exists, skip appending to avoid duplicates.
	- Generate deterministic IDs (e.g., hash of diagram content or timestamp) for marker uniqueness.
	- If no matching marker is found, create a new uniquely marked section at the end of the file.
	- This ensures only one up-to-date diagram section is present and prevents duplicate entries.


## Generation Workflow & Error Handling
1. Validate all required source files exist and meet confidence thresholds
	- If a source file is missing or fails validation, record it in the audit as `missing` or `validation_failed` with validation errors and confidence score.
	- Emit a non-fatal warning and continue processing other sources; do not halt orchestration for partial failures.
2. Generate each diagram type using specialized prompts with behavioral evidence
	- If diagram generation returns below-confidence, mark that diagram as `skipped` with reason, confidence value, and any behavioral evidence.
	- Include both skipped and generated diagram entries in the index and summary, with machine-readable fields: `status` (generated/skipped/missing/failed), `reason`, `confidence`, `evidence`.
3. Create index and summary files with confidence tracking
	- Totals: processed, generated, skipped, missing, failed.
4. Update audit report with diagram references, confidence metrics, and error/warning logs
	- Overall run status in the audit reflects partial success if any non-recoverable errors occurred.
	- Set a non-zero exit or CI signal only for fatal/unrecoverable failures (e.g., all diagrams failed or critical source files missing).
	- Log all errors, warnings, and skipped diagrams clearly for traceability.

## Confidence Validation
- Each diagram must reference behavior-graph.json edges with confidence scores
- Minimum confidence threshold: 0.75 for all generated diagrams
- Track and report mean confidence across all generated diagrams
- Skip diagrams that don't meet confidence requirements


## Required Diagram Prompts
See the explicit mapping above for which prompt file corresponds to each diagram type. If any prompt file is missing or misnamed, diagram generation for that type will fail and must be remediated.
1. diagrams/generate.dependency.graph.prompt.md - Uses behavior-graph.json for behavioral flows
2. diagrams/generate.layered.architecture.prompt.md - Creates internal/external component graphs
3. diagrams/generate.system.context.prompt.md - Uses system-integrations.json for external dependencies
4. diagrams/generate.dataflow.sequence.prompt.md - Creates sequence diagrams for major flows
5. diagrams/generate.component.flow.prompt.md - Maps component interactions with IO operations
6. diagrams/generate.deployment.topology.prompt.md - Physical deployment structure

## Output Format Requirements
- Diagrams: `diagrams/*.mmd` files with Mermaid syntax
- Index: `diagrams.index.json` with confidence scores and metadata
- Summary: `diagrams.summary.md` with confidence metrics and status
- Audit integration: Append to `audit-report.md` with confidence summary

## Success Criteria
- At least 3 diagrams generated with confidence ≥ 0.75
- All behavioral evidence properly cited in diagrams
- Consistent component naming across all diagrams
- Proper Mermaid syntax validation
