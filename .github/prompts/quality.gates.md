# Quality Gates & Validation Rules

## Confidence Gates

### Required Artifact Validation
- **FAIL** if any required artifact is missing:
  - `behavior-graph.json`
  - `system-integrations.json` 
  - `docx-evidence.json`
  - `architecture.md`
  - `logic-and-workflows.md`

### Mean Confidence Thresholds
- **FAIL** if mean confidence < 0.6 in `architecture.md`
- **WARN** if LOW confidence > 10% in `logic-and-workflows.md`
- **FAIL** if mean confidence < 0.7 in `diagrams/*.mmd` (when diagrams generated)
- **FAIL** if mean confidence < 0.5 in `cognitive-audit.md`

### Confidence Calculation Formula
```
Mean Confidence = Σ(percentage_of_bucket × weight_of_bucket)
Weights: HIGH=1.0, MEDIUM=0.5, LOW=0.0
```

## Style Gates

### Line Length Validation
- **FAIL** if any line exceeds 120 characters
- **WARN** if any line exceeds 100 characters

### Voice & Tone Validation
- **FAIL** if passive voice stack detected (>3 consecutive passive constructions)
- **FAIL** if sentence exceeds 25 words
- **FAIL** if technical jargon without explanation ratio > 20%

### Consistency Validation
- **FAIL** if component names differ across files (>5% variance)
- **FAIL** if configuration keys inconsistent between files
- **FAIL** if behavioral evidence citations missing or malformed

## Output Validation

### Index Page Generation
Generate `Documentation/index.md` with:
- Links to all generated outputs
- "Why care" description for each document type
- Confidence summary for each document
- Quick navigation links

### Required Index Content
```markdown
# Documentation Index

## Core Architecture
- [architecture.md](architecture.md) - System overview and component relationships (Confidence: X%)
- [logic-and-workflows.md](logic-and-workflows.md) - Process flows and business logic (Confidence: X%)

## Analysis & Audit
- [cognitive-audit.md](cognitive-audit.md) - Risk analysis and failure predictions (Confidence: X%)
- [developer-preflight.md](developer-preflight.md) - Component modification guidelines (Confidence: X%)

## Visualizations
- [diagrams/](diagrams/) - Generated architecture diagrams (Confidence: X%)

## Evidence & Traceability
- [inference-evidence.md](inference-evidence.md) - Claim citations and evidence (Confidence: X%)
- [change-impact-map.md](change-impact-map.md) - Component dependency analysis (Confidence: X%)
```

## Error Handling & Reporting

### Bad Run Detection
- Log actionable error messages when gates fail
- Provide specific remediation steps
- Reference exact files and line numbers when possible

### Example Error Messages
- "Missing system-integrations.json; add config parsing in Pass 1"
- "LOW confidence > 10% in logic-and-workflows.md; review behavioral evidence citations"
- "Component name inconsistency: 'UserService' vs 'User Service'; standardize naming"

## Gate Implementation

### Pre-generation Validation
Run before Pass 1 to validate input quality and completeness.

### Post-generation Validation  
Run after each pass to validate output quality and confidence.

### Final Validation
Run after all passes to validate complete documentation suite integrity.

## Success Criteria
- All confidence gates pass (no FAIL status)
- All style gates pass (no FAIL status)  
- Index page generated with all required links
- Error messages are actionable and specific
- Mean confidence thresholds met for all documents
