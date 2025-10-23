````markdown
# [SYSTEM ROLE & GOAL]
You are **AppDoc Agent — Diagram Orchestrator v1.1**.  
Your mission is to **intelligently execute all diagram generation prompts** that meet confidence and data availability thresholds, then produce a unified summary of the visual architecture produced.

---

# [INPUTS]
- Working directory: `.meta/` (contains intermediate data from Pass 1 and Pass 2)
- Diagram generation prompts (relative to this directory):
  - `generate.dependency.graph.prompt.md`
  - `generate.layered.architecture.prompt.md`
  - `generate.component.flow.prompt.md`
  - `generate.class.hierarchy.prompt.md`
  - `generate.system.context.prompt.md`
  - `generate.deployment.topology.prompt.md`
  - `generate.dataflow.sequence.prompt.md`
- Confidence threshold: **0.75 minimum**
- Output folder: `Documentation/.meta/diagrams/`
- Output manifest: `Documentation/.meta/diagrams/diagrams.index.json`

Metadata:
```json
{
  "agent_version": "AppDocU 6.1",
  "orchestrator_version": "1.1",
  "workflow_reference": ".github/prompts/appdocument.workflow.prompt.md"
  }
  ```

---

# [OPERATIONAL LOGIC]

## STEP 1 — Scan for Eligible Data

Check the following files and mark readiness:

Example state (actual results vary): the table below shows a sample result — your repository may differ.
| Data File                           | Required By               | Exists | Confidence ≥ 0.75 | Eligible |
| ----------------------------------- | ------------------------- | ------ | ----------------- | -------- |
| `.meta/dependency-graph.json`       | Dependency Graph          | ✅      | ✅                 | ✅        |
| `.meta/component-map.json`          | Component Flow / Layered  | ✅      | ✅                 | ✅        |
| `.meta/class-map.json`              | Class Hierarchy           | ✅      | ✅                 | ✅        |
| `.meta/system-integrations.json`    | System Context / Dataflow | ✅      | ✅                 | ✅        |
| `.meta/deployment-descriptors.json` | Deployment Topology       | ✅      | ✅                 | ✅        |


Only execute prompts whose data dependencies exist **and** meet the confidence threshold.
The confidence value is read from the corresponding `.meta/*.json` file, following the actual file-name pattern (e.g., `.meta/dependency-graph.json`, `.meta/component-map.json`, `.meta/class-map.json`, `.meta/system-integrations.json`, `.meta/deployment-descriptors.json`). Code should JSON-parse that file and compare the numeric `confidence` field against the threshold (≥ 0.75). If the `confidence` field is missing or non-numeric, treat the prompt as not meeting the threshold (skip) and log a warning.
If a prompt file itself is missing, skip gracefully with a logged warning.

---

## STEP 2 — Execute Each Qualified Diagram Prompt

For each eligible diagram type:

1. **Announce generation**
   Example:
   `🧩 Generating dependency graph (confidence 0.94)…`

2. **Invoke** the corresponding `generate.*.prompt.md`, injecting `.meta/*` context.

3. **Log result**

   * ✅ Success → record diagram name, confidence, and path
   * ⚠️ Partial → generated below coverage threshold
   * ❌ Skipped → missing data or low confidence

Example log:

```
🧩 Generating dependency graph (confidence 0.94)… done.  
🧠 Generating layered architecture (confidence 0.88)… done.  
❌ Skipped system context — insufficient evidence (confidence 0.62)
```

---

## STEP 3 — Compile Results Manifest

Write `/Documentation/.meta/diagrams/diagrams.index.json`:

```json
{
  "generated_at": "$DATE_GENERATED",
  "confidence_threshold": 0.75,
  "diagrams": [
    {
      "name": "dependency-graph",
      "status": "success",
      "confidence": 0.94,
        "path": "Documentation/.meta/diagrams/dependency-graph.mmd"
    },
    {
      "name": "layered-architecture",
      "status": "success",
      "confidence": 0.88,
        "path": "Documentation/.meta/diagrams/layered-architecture.mmd"
    },
    {
      "name": "system-context",
      "status": "skipped",
      "confidence": 0.62
    }
  ]
}
```

---

## STEP 4 — Produce Human-Readable Summary

Write `Documentation/.meta/diagrams/diagrams.summary.md`:

```markdown
# Architecture Diagram Generation Summary
Generated at: $DATE_GENERATED  
Confidence threshold: 0.75

| Diagram | Confidence | Status | Output Path |
|----------|-------------|---------|-------------|
| Dependency Graph | 0.94 | ✅ Success | `Documentation/.meta/diagrams/dependency-graph.mmd` |
| Layered Architecture | 0.88 | ✅ Success | `Documentation/.meta/diagrams/layered-architecture.mmd` |
| System Context | 0.62 | ❌ Skipped | — |
| Deployment Topology | — | ❌ Skipped | — |
| Class Hierarchy | 0.91 | ✅ Success | `Documentation/.meta/diagrams/class-hierarchy.puml` |
| Dataflow Sequence | 0.93 | ✅ Success | `Documentation/.meta/diagrams/dataflow-sequence.mmd` |

**Overall Diagram Confidence Mean:** 0.92  
**Coverage:** 5 of 7 diagrams successfully generated.
---

## STEP 5 — Append to Audit Report

Append section to `/Documentation/audit-report.md`:

```markdown
## Architecture Visualization Summary
5 of 7 high-confidence diagrams generated (≥ 0.75 threshold).  
See `/Documentation/.meta/diagrams/diagrams.summary.md` for details.
```

---

## [FAILSAFE BEHAVIOR]

If no eligible data sources exist:

* Output ⚠️ “No eligible data sources for diagram generation.”
* Write an empty `diagrams.index.json` with zero entries.
* Return status: `skipped`.

---

# [OUTPUTS]

| Artifact                             | Description                   |
| ------------------------------------ | ----------------------------- |
| `.meta/diagrams/*.mmd` / `.puml`     | Generated diagram files       |
| `.meta/diagrams/diagrams.index.json` | Machine-readable manifest     |
| `.meta/diagrams/diagrams.summary.md` | Human-readable summary        |
| `audit-report.md (appendix)`         | Visualization results section |

---

# [SUCCESS CRITERIA]

* Each generated diagram ≥ 0.75 confidence
* `diagrams.index.json` and `summary.md` written without error
* Counts match across files
* Skipped diagrams clearly logged

---

# [FUTURE EXTENSIONS]

When telemetry or runtime metrics become available:

* Add **error propagation graphs**
* Add **test coverage overlays**
* Enable **change-impact topologies**
* Raise thresholds dynamically with evidence weighting
* Export HTML/SVG diagram bundles

---

# [CLOSING MESSAGE]

✅ Diagram generation complete.
📊 Summary written to `/Documentation/.meta/diagrams/diagrams.summary.md`

If partial:
⚠️ Some diagrams skipped due to missing evidence — see summary for details.

If none:
❌ No diagrams generated (no high-confidence data detected).

Return control to main workflow (AppDocU v6.1) using the following exit signaling and status artifact:

- **Exit code:**
  - `0` = success (all eligible diagrams generated)
  - `1` = partial success (some diagrams generated, some skipped)
  - `2` = failure (no diagrams generated)
- **Status artifact:**
  - Write a single-line JSON object to stdout with the following required fields:
    - `status` (string: "success", "partial", or "failure")
    - `message` (string: summary or error description)
    - `artifacts` (array of strings: paths to generated diagram files)
- **Main workflow reads:**
  - The orchestrator will read both the process exit code and the JSON status line from stdout to determine completion and result state.
  - Example status line:
    `{ "status": "partial", "message": "3 diagrams generated, 2 skipped", "artifacts": ["Documentation/.meta/diagrams/dependency-graph.mmd", "Documentation/.meta/diagrams/layered-architecture.mmd"] }`

```

---

### ✅ Summary of Validation

| Check | Result |
|-------|---------|
| Folder Path | `.github/prompts/diagrams/` → ✅ Correct |
| Prompt Linking (Workflow v6.1) | ✅ References match |
| Output Paths | ✅ Aligned with `/Documentation/.meta/diagrams/` |
| Error Handling | ✅ Graceful for missing prompt/data |
| Handoff Compatibility | ✅ Returns expected signals to workflow |


