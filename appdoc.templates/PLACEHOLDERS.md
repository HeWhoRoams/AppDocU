# PLACEHOLDERS.md — Troubleshooting Playbook Template

This file documents all placeholders used in `troubleshooting.playbook.template.md`.

| Placeholder Name         | Description                                 | Data Source/Path         | Required/Optional | Default/Fallback Value                |
|-------------------------|---------------------------------------------|--------------------------|-------------------|---------------------------------------|
| $ARGUMENTS              | App name or arguments for playbook          | Workflow input           | Required          | N/A                                   |
| $DATE_GENERATED         | Timestamp of playbook generation            | System clock/workflow    | Required          | Current date/time                     |
| $SOURCES_SCANNED        | List of sources scanned                     | Codebase scan            | Optional          | "N/A" or empty string                 |
| $TROUBLE_TRIGGER_SUMMARY| Summary of trigger conditions               | Workflow analysis        | Optional          | "None detected"                      |
| $FILES_NETWORK          | Network/API layer files                     | Directory scan           | Optional          | "N/A"                                |
| $FILES_APP              | Application/Logic layer files               | Directory scan           | Optional          | "N/A"                                |
| $FILES_DATA             | Data/Persistence layer files                | Directory scan           | Optional          | "N/A"                                |
| $FILES_CONFIG           | Configuration files                         | Directory scan           | Optional          | "N/A"                                |
| $FILES_UI               | UI/Interface layer files                    | Directory scan           | Optional          | "N/A"                                |
| $COUNT_HIGH             | Count of high-confidence failures           | Static analysis          | Required          | 0                                     |
| $COUNT_MED              | Count of medium-confidence failures         | Static analysis          | Required          | 0                                     |
| $COUNT_LOW              | Count of low-confidence failures            | Static analysis          | Required          | 0                                     |
| $TOP_RISK_LAYER         | Highest-risk system layer                   | Static analysis          | Required          | "N/A"                                |
| $TOP_CAUSE_CATEGORY     | Most common root-cause category             | Static analysis          | Required          | "N/A"                                |
| $INSIGHT_1              | Key observation #1                          | Agent inference          | Optional          | "No insight"                         |
| $INSIGHT_2              | Key observation #2                          | Agent inference          | Optional          | "No insight"                         |
| $INSIGHT_3              | Key observation #3                          | Agent inference          | Optional          | "No insight"                         |
| $SCAN_TIMESTAMP         | Timestamp of codebase scan                  | System clock/workflow    | Required          | Current date/time                     |
| $FILES_SCANNED          | Total files scanned                         | Codebase scan            | Required          | 0                                     |
| $EXCEPTIONS_FOUND       | Total exceptions detected                   | Static analysis          | Required          | 0                                     |


## Convention for Optional Placeholders
- Optional placeholders are prefixed with `$` and documented as "Optional" in this file.
- If a value is missing, use the default/fallback value listed above.

### Cross-Reference Guidance
For example usages, see:
- Main template: `audit.report.template.md` section "METADATA" (lines 7–15)
- Architecture template: `architecture.template.md` (lines 3–10)

### Inline Examples
- app-name: `$ARGUMENTS` (e.g., `app: "$ARGUMENTS"`)
- Generated: `$DATE_GENERATED` (e.g., `generated_at: "$DATE_GENERATED"`)

---
For details on placeholder usage and expected formats, see inline comments in the template and refer to this file for all placeholder definitions.

---
Last updated: 2025-10-23
Template version: v3.5
