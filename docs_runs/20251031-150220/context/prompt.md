# Copilot Documentation Task

Use this prompt with the attached analysis files to generate human-readable documentation.

## Context Files (open these in the editor)
- Behavior Graph: `_normalized\.meta\behavior-graph.json`
- System Integrations: `_normalized\.meta\system-integrations.json`
- Doc Evidence: `_normalized\.meta\docx-evidence.json`
- Summary: `_normalized\context\summary.json`

## What to Produce
1. architecture.md — system overview with component breakdown and data flows
2. logic-and-workflows.md — workflows, business rules, data processing
3. change-impact-map.md — dependencies, risks, safe-modification guidance

## Guidance
- Cite concrete file paths and entities found in the JSONs
- Call out fragile/risky areas and external integrations
- Include simple Mermaid diagrams where helpful

## How To Use In Copilot Chat
- Open the JSON files listed above so Copilot can see them
- Paste this prompt and ask Copilot to draft the docs
- Iterate: ask Copilot to refine sections with more detail
