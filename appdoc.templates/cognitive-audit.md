# Cognitive Audit

---
# METADATA
---
title: "Cognitive Audit"
app: "$ARGUMENTS"
template: "cognitive-audit.md"
version: "1.0"
doc_version: "$DOC_VERSION"
generated_by: "AppDoc Agent v7.0"
generated_at: "$DATE_GENERATED"
code_last_modified: "$LAST_CODE_CHANGE_DATE"
sources_scanned: $SOURCES_SCANNED
behavior_graph_analyzed: $BEHAVIOR_GRAPH_NODES nodes, $BEHAVIOR_GRAPH_EDGES edges
system_integrations_mapped: $SYSTEM_INTEGRATIONS_COUNT
---

## Executive Summary
This cognitive audit provides proactive mental scaffolding for developers before failures occur. It analyzes behavioral patterns, fragility indicators, and predicted failure chains from the behavior graph and system integrations.

---

## 1. Fragility Table

This table ranks components by fragility reasons: high fan-out, missing tests, many IO edges, complex branching.

| Component | Fan-in | Fan-out | IO Edges | Test Coverage | Risk Score | Fragility Reason | Confidence |
|-----------|--------|---------|----------|---------------|------------|------------------|------------|
| $FRAGILE_COMPONENT_NAME | $FAN_IN_COUNT | $FAN_OUT_COUNT | $IO_EDGES_COUNT | $TEST_COVERAGE | $RISK_SCORE | $FRAGILITY_REASON | $CONFIDENCE_LEVEL |
| $FRAGILE_COMPONENT_NAME_2 | $FAN_IN_COUNT_2 | $FAN_OUT_COUNT_2 | $IO_EDGES_COUNT_2 | $TEST_COVERAGE_2 | $RISK_SCORE_2 | $FRAGILITY_REASON_2 | $CONFIDENCE_LEVEL_2 |

### Fragility Scoring
- **Fan-out**: Number of components that depend on this component
- **IO Edges**: Database reads/writes, API calls, file operations
- **Test Coverage**: Percentage of behavioral flows covered by tests
- **Risk Score**: High (8-10), Medium (5-7), Low (1-4)
- **Confidence**: HIGH/MEDIUM/LOW based on behavioral evidence

---

## 2. Predicted Failure Chains

Based on behavior graph analysis, these are predicted failure propagation patterns:

### Chain 1: $FAILURE_CHAIN_NAME
**Trigger**: $FAILURE_TRIGGER[CONFIDENCE:HIGH]
**Propagation**: $FAILURE_PROPAGATION_PATH[CONFIDENCE:HIGH]
**Impact**: $FAILURE_IMPACT[CONFIDENCE:HIGH]
**Evidence**: $FAILURE_EVIDENCE (e.g., `behavior-graph.json` edges showing dependency chain)

### Chain 2: $FAILURE_CHAIN_NAME_2
**Trigger**: $FAILURE_TRIGGER_2[CONFIDENCE:HIGH]
**Propagation**: $FAILURE_PROPAGATION_PATH_2[CONFIDENCE:HIGH]
**Impact**: $FAILURE_IMPACT_2[CONFIDENCE:HIGH]
**Evidence**: $FAILURE_EVIDENCE_2

### Chain 3: $FAILURE_CHAIN_NAME_3
**Trigger**: $FAILURE_TRIGGER_3[CONFIDENCE:HIGH]
**Propagation**: $FAILURE_PROPAGATION_PATH_3[CONFIDENCE:HIGH]
**Impact**: $FAILURE_IMPACT_3[CONFIDENCE:HIGH]
**Evidence**: $FAILURE_EVIDENCE_3

### Example Patterns:
- "If Repo fails → Service fails → API returns 500"
- "If External API down → Payment processing fails → Order creation blocked"
- "If Database connection pool exhausted → All read operations timeout"

---


## 3. Top 10 Watchpoints

These are the components most likely to cause pain based on behavioral analysis:

| # | Watchpoint | Category/Layer | Reason/Description | Confidence |
|---|------------|---------------|-------------------|------------|
| 1 | $WATCHPOINT_1 | $WATCHPOINT_CATEGORY_1 | $WATCHPOINT_REASON_1 | $WATCHPOINT_CONFIDENCE_1 |
| 2 | $WATCHPOINT_2 | $WATCHPOINT_CATEGORY_2 | $WATCHPOINT_REASON_2 | $WATCHPOINT_CONFIDENCE_2 |
| 3 | $WATCHPOINT_3 | $WATCHPOINT_CATEGORY_3 | $WATCHPOINT_REASON_3 | $WATCHPOINT_CONFIDENCE_3 |
| 4 | $WATCHPOINT_4 | $WATCHPOINT_CATEGORY_4 | $WATCHPOINT_REASON_4 | $WATCHPOINT_CONFIDENCE_4 |
| 5 | $WATCHPOINT_5 | $WATCHPOINT_CATEGORY_5 | $WATCHPOINT_REASON_5 | $WATCHPOINT_CONFIDENCE_5 |
| 6 | $WATCHPOINT_6 | $WATCHPOINT_CATEGORY_6 | $WATCHPOINT_REASON_6 | $WATCHPOINT_CONFIDENCE_6 |
| 7 | $WATCHPOINT_7 | $WATCHPOINT_CATEGORY_7 | $WATCHPOINT_REASON_7 | $WATCHPOINT_CONFIDENCE_7 |
| 8 | $WATCHPOINT_8 | $WATCHPOINT_CATEGORY_8 | $WATCHPOINT_REASON_8 | $WATCHPOINT_CONFIDENCE_8 |
| 9 | $WATCHPOINT_9 | $WATCHPOINT_CATEGORY_9 | $WATCHPOINT_REASON_9 | $WATCHPOINT_CONFIDENCE_9 |
| 10 | $WATCHPOINT_10 | $WATCHPOINT_CATEGORY_10 | $WATCHPOINT_REASON_10 | $WATCHPOINT_CONFIDENCE_10 |

---

## 4. Risk Analysis by Layer

### Controller Layer (API/HTTP)
- **High-risk components**: $CONTROLLER_HIGH_RISK[CONFIDENCE:HIGH]
- **IO operations**: $CONTROLLER_IO_COUNT database calls, $CONTROLLER_API_COUNT external API calls
- **Fragility indicators**: $CONTROLLER_FRAGILITY[CONFIDENCE:HIGH]

### Service Layer (Business Logic)
- **High-risk components**: $SERVICE_HIGH_RISK[CONFIDENCE:HIGH]
- **IO operations**: $SERVICE_IO_COUNT database calls, $SERVICE_API_COUNT external API calls
- **Fragility indicators**: $SERVICE_FRAGILITY[CONFIDENCE:HIGH]

### Repository Layer (Database/Storage)
- **High-risk components**: $REPO_HIGH_RISK[CONFIDENCE:HIGH]
- **IO operations**: $REPO_IO_COUNT database operations
- **Fragility indicators**: $REPO_FRAGILITY[CONFIDENCE:HIGH]

### External Dependencies
- **High-risk integrations**: $EXTERNAL_HIGH_RISK[CONFIDENCE:HIGH]
- **Failure impact**: $EXTERNAL_IMPACT[CONFIDENCE:HIGH]
- **Monitoring needs**: $EXTERNAL_MONITORING[CONFIDENCE:HIGH]

---

## 5. Suggested Tests per Risky Component

Based on uncovered edges and exception handling patterns in the behavior graph:

### Component: $TEST_COMPONENT_NAME
**Missing Coverage**: $TEST_MISSING_COVERAGE[CONFIDENCE:HIGH]
**Suggested Tests**:
- $TEST_SUGGESTION_1[CONFIDENCE:HIGH]
- $TEST_SUGGESTION_2[CONFIDENCE:HIGH]
- $TEST_SUGGESTION_3[CONFIDENCE:HIGH]

### Component: $TEST_COMPONENT_NAME_2
**Missing Coverage**: $TEST_MISSING_COVERAGE_2[CONFIDENCE:HIGH]
**Suggested Tests**:
- $TEST_SUGGESTION_4[CONFIDENCE:HIGH]
- $TEST_SUGGESTION_5[CONFIDENCE:HIGH]
- $TEST_SUGGESTION_6[CONFIDENCE:HIGH]

---

## 6. Cognitive Load Indicators

Components that require significant mental overhead to understand and modify:

| Component | Complexity Score | Cognitive Load Reason | Recommended Documentation | Confidence |
|-----------|------------------|----------------------|---------------------------|------------|
| $COMPLEX_COMPONENT_1 | $COMPLEXITY_SCORE_1 | $COGNITIVE_REASON_1 | $RECOMMENDED_DOCS_1 | $CONFIDENCE_1 |
| $COMPLEX_COMPONENT_2 | $COMPLEXITY_SCORE_2 | $COGNITIVE_REASON_2 | $RECOMMENDED_DOCS_2 | $CONFIDENCE_2 |

---

## 7. Pre-Modification Checklist

Before modifying any component, consider:

### High-Risk Components (Risk Score 8-10):
- [ ] Review behavioral evidence in `behavior-graph.json`
- [ ] Check system integration dependencies in `system-integrations.json`
- [ ] Verify all dependent components (fan-out analysis)
- [ ] Run comprehensive test suite
- [ ] Consider gradual rollout strategy

### Medium-Risk Components (Risk Score 5-7):
- [ ] Review behavioral evidence
- [ ] Check direct dependencies
- [ ] Run relevant tests
- [ ] Monitor after deployment

### Low-Risk Components (Risk Score 1-4):
- [ ] Quick behavioral check
- [ ] Basic testing
- [ ] Standard deployment

---

## 8. References

### Related Documentation
- Developer Preflight: `developer-preflight.md`
- Architecture: `architecture.md`
- Logic & Workflows: `logic-and-workflows.md`
- Change Impact Map: `change-impact-map.md`
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

## Quick Reference for Risk Assessment

### Risk Indicators:
- **High Fan-out**: Component used by many others
- **Many IO Operations**: Database, API, file system interactions
- **External Dependencies**: Calls to external services
- **Low Test Coverage**: Behavioral flows not covered
- **Complex Branching**: Multiple conditional paths

### Mitigation Strategies:
1. Add comprehensive tests before modification
2. Implement gradual rollout/feature flags
3. Add monitoring and alerting
4. Create fallback mechanisms
5. Document behavioral changes

*(end of cognitive audit document)*
