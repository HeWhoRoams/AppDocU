# Developer Preflight Checklist

---
# METADATA
---
title: "Developer Preflight"
app: "$ARGUMENTS"
template: "developer-preflight.md"
version: "1.0"
doc_version: "$DOC_VERSION"
generated_by: "AppDoc Agent v7.0"
generated_at: "$DATE_GENERATED"
code_last_modified: "$LAST_CODE_CHANGE_DATE"
sources_scanned: "$SOURCES_SCANNED"
behavior_graph_analyzed: "$BEHAVIOR_GRAPH_NODES nodes, $BEHAVIOR_GRAPH_EDGES edges"
system_integrations_mapped: "$SYSTEM_INTEGRATIONS_COUNT"---

## Overview
This preflight checklist provides essential information for developers before modifying components. Each item includes evidence and confidence ratings from behavioral analysis.

---

## 1. Component: $COMPONENT_NAME

### Purpose
$COMPONENT_PURPOSE[CONFIDENCE:HIGH]

### Inputs
$COMPONENT_INPUTS[CONFIDENCE:HIGH]

### Transformations
$COMPONENT_TRANSFORMATIONS[CONFIDENCE:HIGH]

### Outputs
$COMPONENT_OUTPUTS[CONFIDENCE:HIGH]

### Dependencies
$COMPONENT_DEPENDENCIES[CONFIDENCE:HIGH]

### Risk if Modified
$COMPONENT_RISK_LEVEL[CONFIDENCE:HIGH]
- **High Fan-out**: $COMPONENT_FAN_OUT_COUNT components depend on this
- **IO Operations**: $COMPONENT_IO_COUNT database/file/network operations
- **External Dependencies**: $COMPONENT_EXTERNAL_DEPS_COUNT external integrations
- **Test Coverage**: $COMPONENT_TEST_COVERAGE_STATUS

### Tests to Run/Add
$COMPONENT_TEST_RECOMMENDATIONS[CONFIDENCE:HIGH]

### Evidence & Confidence
- **Code Location**: $COMPONENT_CODE_LOCATION[CONFIDENCE:HIGH]
- **Behavior Graph Evidence**: $COMPONENT_BEHAVIOR_EVIDENCE (e.g., `behavior-graph.json#edge123`)
- **System Integration Links**: $COMPONENT_INTEGRATION_LINKS
- **Confidence Level**: HIGH/MEDIUM/LOW
- **Inference Source**: Behavioral analysis + System integrations + Test mapping

---

## 2. Component: $COMPONENT_NAME_2

### Purpose
$COMPONENT_PURPOSE[CONFIDENCE:HIGH]

### Inputs
$COMPONENT_INPUTS[CONFIDENCE:HIGH]

### Transformations
$COMPONENT_TRANSFORMATIONS[CONFIDENCE:HIGH]

### Outputs
$COMPONENT_OUTPUTS[CONFIDENCE:HIGH]

### Dependencies
$COMPONENT_DEPENDENCIES[CONFIDENCE:HIGH]

### Risk if Modified
$COMPONENT_RISK_LEVEL[CONFIDENCE:HIGH]
- **High Fan-out**: $COMPONENT_FAN_OUT_COUNT components depend on this
- **IO Operations**: $COMPONENT_IO_COUNT database/file/network operations
- **External Dependencies**: $COMPONENT_EXTERNAL_DEPS_COUNT external integrations
- **Test Coverage**: $COMPONENT_TEST_COVERAGE_STATUS

### Tests to Run/Add
$COMPONENT_TEST_RECOMMENDATIONS[CONFIDENCE:HIGH]

### Evidence & Confidence
- **Code Location**: $COMPONENT_CODE_LOCATION[CONFIDENCE:HIGH]
- **Behavior Graph Evidence**: $COMPONENT_BEHAVIOR_EVIDENCE (e.g., `behavior-graph.json#edge123`)
- **System Integration Links**: $COMPONENT_INTEGRATION_LINKS
- **Confidence Level**: HIGH/MEDIUM/LOW
- **Inference Source**: Behavioral analysis + System integrations + Test mapping

---

<!-- [REPEATABLE COMPONENT BLOCK] -->
_Repeat the above Component block for each component in the codebase. Duplicate and fill out the section for every relevant component._

---

## 3. Cognitive Audit Summary

### Fragility Table
| Component | Fan-in | Fan-out | IO Edges | Test Presence | Risk Score | Confidence |
|-----------|--------|---------|----------|---------------|------------|------------|
| $FRAGILE_COMPONENT_NAME | $FAN_IN_COUNT | $FAN_OUT_COUNT | $IO_EDGES_COUNT | $TEST_PRESENCE | $RISK_SCORE | $CONFIDENCE_LEVEL |

### Predicted Failure Chains
$PREDICTED_FAILURE_CHAINS[CONFIDENCE:HIGH]

### Top 10 Watchpoints
$TOP_10_WATCHPOINTS[CONFIDENCE:HIGH]

---

## 4. Modification Guidelines

### Before Modifying Any Component:
1. Check this preflight checklist for the component
2. Review behavioral evidence in `behavior-graph.json`
3. Verify system integration dependencies in `system-integrations.json`
4. Run recommended tests
5. Consider impact on dependent components (see `change-impact-map.md`)

### Risk Assessment Scale:
- **CRITICAL**: High fan-out + multiple IO operations + low test coverage
- **HIGH**: Multiple dependencies + external integrations
- **MEDIUM**: Internal dependencies only
- **LOW**: No external dependencies, good test coverage

---

## 5. References

### Related Documentation
- Architecture: `architecture.md`
- Logic & Workflows: `logic-and-workflows.md`
- Change Impact Map: `change-impact-map.md`
- Cognitive Audit: `cognitive-audit.md`
- Inference Evidence: `inference-evidence.md`

### Source Evidence
- Behavior graph: `.meta/behavior-graph.json`
- System integrations: `.meta/system-integrations.json`
- Component dependencies: `.meta/component-map.json`
- Test mapping: `.meta/test-coverage-map.json`

### Version Control
- Current version: v$DOC_VERSION
- Previous version: v$PREV_DOC_VERSION
- Changes: See `CHANGELOG.md`

---

## Quick Reference for Modifications

### Common Modification Scenarios
- **Adding new functionality**: Check dependencies and IO operations
- **Changing existing logic**: Review behavioral evidence and test coverage
- **Modifying external integrations**: Verify system integration mapping
- **Database schema changes**: Check all IO operations and dependent components

### Before Committing Changes
1. Update this preflight checklist if component behavior changes
2. Regenerate behavior graph if new IO operations are added
3. Update system integrations if new external dependencies are introduced
4. Add/update tests for new behavioral patterns

*(end of developer preflight document)*
