# Documentation Tasks (Template)

---
# METADATA
---
title: "Documentation Tasks"
app: "$ARGUMENTS"
template: "documentation.tasks.template.md"
version: "2.0"
generated_by: "AppDoc Agent"
generated_at: "$DATE_GENERATED"
---

## Tasks (One entry per unresolved placeholder / issue)

Follow this exact task structure for every task created by the agent:

---
**Example Task Entry:**
	- **PRIORITY:** P0
	- **TASK:** Update SAP credential placeholder
	- **FILE or PLACEHOLDER:** [web.config | $CONFIG_STRING_SAP_CREDENTIAL]
	- **STATUS:** Blocked
	- **SOURCE/LINE:** [web.config:42]
	- **SEARCH/ACTION:** Locate and inject valid SAP credential
	- **JUSTIFICATION:** Required for production deployment; awaiting credential from security team.
---


- **PRIORITY:** [P0 / P1 / P2 / P3]
- **TASK:** [Action-oriented verb phrase. Max 10 words.]
- **FILE or PLACEHOLDER:** [document.md / $PLACEHOLDER_TEXT]
- **STATUS:** [Blocked / To Do / Auto-Resolved]
- **SOURCE/LINE:** [file:line or evidence source]
- **SEARCH/ACTION:** [Describe search or remediation action]
- **JUSTIFICATION:** [Required when STATUS is 'Blocked'; provide a brief reason. Otherwise omit.]

## Task Generation Rules (Agent MUST follow)

1. Create one task per unfilled placeholder.
2. Tasks for P0 items (security / critical) must be flagged as P0 and noted in the Audit Report.
3. The `TASK` sentence must be action-oriented and short (<= 10 words).
4. For `Auto-Resolved` tasks, include the injected value in `SEARCH/ACTION`.
5. Keep tasks atomic — do not combine multiple fixes into a single task.

*(end of tasks template)*
