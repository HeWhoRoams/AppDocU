Excellent—this feedback makes the roadmap significantly more production-ready. Below is the **fully iterated `feature_roadmap.md`**, now incorporating **tight numeric success criteria, measurable gates, stack-specific gotchas, and validation loops** for each version (1.x → 3.x).

It’s structured for direct inclusion under `/docs/roadmap/feature_roadmap.md` in your GitLab repo, and written so both humans and CI validators can consume it.

---

# **AppDocU Feature Roadmap (v3.1)**

*Expanded, dependency-aware roadmap for static code assessment, runtime truth, and continuous validation.*

---

## **Version 1.x — Standalone Code Assessment and Deterministic Documentation**

### **1. Structural Intelligence (Roslyn + selective CodeQL)**

**Goal:** Derive the single source of structural truth for legacy C# repositories.

✅ **Success Criteria**

* MsBuildWorkspace loads **100 %** of projects; fail fast if any fail.
* Symbol resolution rate **≥ 98 %** across namespaces/classes/methods.
* Project inclusion by MSBuild configuration **≥ 95 %**.
* Code graph includes conditional code paths from all preprocessor symbols.

🧪 **Testing**

* Run AppDocU on itself with solution- and project-level entries.
* Cross-check a random subset using CodeQL flow queries for call-edge sanity.

⚠️ **Gotchas**

* Incorrect MsBuildLocator or missing SDK workloads cause silent skips.
* Missing preprocessor defines hide conditional paths—log all compilation symbols.

---

### **2. Adaptive Reasoning and Validators**

**Goal:** Iterate intelligently over the graph with local recursion and invariant checks.

✅ **Success Criteria**

* Iteration depth ≤ 3 unless uncertainty > threshold → adaptive expansion.
* Graph invariants (no orphan nodes, acyclic layers, consistent symbol IDs) = PASS.

🧪 **Testing**

* Two consecutive runs must show ≥ 50 % improvement in medium→high confidence.
* Verify `.meta/reflexion.memory.json` persists motifs between runs.

⚠️ **Gotchas**

* Reflexion memory not saved → cross-file inference drift.
* Failing invariant should hard-stop to avoid corrupt `.meta`.

---

### **3. Deterministic Doc Packaging (GitLab Artifacts)**

**Goal:** Create reproducible, checksum-stable documentation bundles.

✅ **Success Criteria**

* `/artifacts/docs/` bundle + `code.graph.json` have identical SHA across two builds.
* GitLab artifacts declare explicit `expire_in` and `needs:`.

🧪 **Testing**

* Rebuild twice; identical SHAs required before publish stage triggers.

⚠️ **Gotchas**

* Unset `expire_in` purges docs prematurely.
* Hidden file encoding differences alter SHAs.

---

### **Gate to 2.x**

Promote when:

* Solution coverage ≥ 95 %.
* Symbol resolution ≥ 98 %.
* Two consecutive builds produce identical artifacts and all invariants PASS.

---

## **Version 2.x — Runtime Truth and Portal Integrations**

### **1. Runtime Ground Truth (.NET OpenTelemetry)**

**Goal:** Validate static graph with observed runtime behavior.

✅ **Success Criteria**

* ≥ 90 % of high-traffic endpoints produce spans in `runtime.graph.json`.
* Drift ≤ 10 % between static vs runtime edges.

🧪 **Testing**

* CI smoke tests with sampling 0.3–0.5; diff graphs; flag async mismatches.

⚠️ **Gotchas**

* Sampling = 1.0 → exporter overload.
* Async spans mis-link without Activity.Parent enforcement.

---

### **2. Machine-Actionable Contracts (OpenAPI / AsyncAPI)**

**Goal:** Generate agent-readable interface specs for REST and events.

✅ **Success Criteria**

* Endpoint/channel coverage ≥ 95 %.
* Payload conformance ≥ 98 % in replay tests; < 2 % errors.

🧪 **Testing**

* Replay captured traces against generated OpenAPI.
* Validate AsyncAPI channels with sampled messages.

⚠️ **Gotchas**

* Missing attribute routing hides endpoints.
* AsyncAPI drift unless payloads re-sampled regularly.

---

### **3. SBOM Generation (CycloneDX)**

✅ **Success Criteria**

* 100 % direct / ≥ 80 % transitive dependency coverage.
* Vulnerability summary present in `audit-report.md`.

🧪 **Testing**

* Diff SBOM count vs `dotnet list package`; delta ≤ 5 %.
* Include unmanaged allow-lists for legacy DLLs.

⚠️ **Gotchas**

* Unmanaged DLLs → blind spots unless manually included.

---

### **4. BookStack Publishing (REST API)**

✅ **Success Criteria**

* 100 % page upserts succeed (HTTP 200) with single retry backoff.
* Page IDs preserved → no duplication.

🧪 **Testing**

* Publish AppDocU docs to sandbox; verify idempotent updates.

⚠️ **Gotchas**

* Race conditions on concurrent runs → implement per-page locks.

---

### **5. TeamDynamix Ticket Automation**

✅ **Success Criteria**

* High-signal validator failures → tickets auto-opened with artifact links.
* Deduplication by validator ID + commit hash → no spam.

🧪 **Testing**

* Trigger intentional schema drift; confirm one ticket per failure.

⚠️ **Gotchas**

* Missing rate-limits → duplicate tickets.

---

### **Gate to 3.x**

Promote when:

* Runtime coverage ≥ 90 % of high-traffic endpoints.
* OpenAPI visible via ApiExplorer.
* BookStack/TeamDynamix flows ≥ 99 % success under controlled failures.

---

## **Version 3.x — Continuous Validation and Governance (CI/CD)**

### **1. GitLab Pipeline Integration**

✅ **Success Criteria**

* Graph/OpenAPI/Runtime/SBOM artifacts reused across jobs via `needs:`.
* 0 manual approvals required for publishing.

🧪 **Testing**

* Full pipeline on AppDocU repo; verify publish job waits for all artifact SHAs.

⚠️ **Gotchas**

* Artifact expiry or path mismatch → publish fails silently.

---

### **2. Continuous Drift Detection and ADR Governance**

✅ **Success Criteria**

* ≤ 2 % weekly drift on stable modules.
* ADRs auto-created for schema/dependency changes.

🧪 **Testing**

* Nightly diffs of graph/specs; confirm ADRs contain links to evidence.

⚠️ **Gotchas**

* Timestamps or GUID regen simulate drift—normalize before diff.

---

### **3. Docs-as-Code Publishing**

✅ **Success Criteria**

* BookStack pages re-render on merge with commit hash visible.
* 100 % pages contain “Edit in Repo” link.

🧪 **Testing**

* Validate hash in page footer matches GitLab commit ID.

⚠️ **Gotchas**

* API throttling (HTTP 429) on large repos—add exponential backoff.

---

### **4. Policy and Compute Tuning**

✅ **Success Criteria**

* ≥ 30 % token reduction with equal accuracy.
* Reflexion motifs reused ≥ 5 consecutive runs.

🧪 **Testing**

* Benchmark 10 passes; observe iteration depth decline and confidence stability.

⚠️ **Gotchas**

* Over-aggressive thresholds truncate complex modules.

---

## **Cross-Cutting Data Contracts and IDs**

* **Stable Symbol IDs:** `Namespace.Class.Member(signature)` + project GUID.
* **Span↔Symbol Linking:** map Activities to controllers via route templates and method metadata.
* **Contract Versioning:** store OpenAPI/AsyncAPI hashes for payload diff tracking.

---

## **Expanded Success Criteria Summary**

| Phase | Metric                    | Target                           | Validation                      |
| ----- | ------------------------- | -------------------------------- | ------------------------------- |
| 1.x   | Symbol resolution         | ≥ 98 %                           | Roslyn log + CodeQL cross-check |
| 2.x   | Endpoint runtime coverage | ≥ 90 %                           | OpenTelemetry traces            |
| 2.x   | Payload conformance       | ≥ 98 %                           | Replay tests vs OpenAPI         |
| 2.x   | SBOM coverage             | 100 % direct / ≥ 80 % transitive | CycloneDX diff                  |
| 3.x   | Drift rate                | ≤ 2 % / week                     | Graph diff job                  |
| 3.x   | Token efficiency gain     | ≥ 30 %                           | Reflexion metrics               |

---

## **High-Risk Gotchas to Track**

* **MsBuildWorkspace/SDK Workloads:** verify presence before analysis.
* **ApiExplorer Gaps:** enforce attribute routing for OpenAPI.
* **OTel Sampling/Async:** keep sampling ≤ 0.5 and maintain Activity links.
* **SBOM Blind Spots:** manually add unmanaged DLLs.

---

### **Rationale Recap**

* **v1.x → Static Truth:** Roslyn/CodeQL foundation with deterministic artifacts.
* **v2.x → Runtime Truth:** Telemetry and contracts validated by measurements.
* **v3.x → Governed Truth:** GitLab pipelines continuously validate and publish accurate docs.

---

Would you like me to output a **checklist-enabled version** (`- [ ]` tasks per feature and gate) so it can be directly used for milestone tracking in GitLab’s “Issues → Roadmap” view?
