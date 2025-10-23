# Pattern Pack — Generic / Unknown Language Handler

## Purpose
Catches any file type not covered by a dedicated pattern pack (e.g., `.yml`, `.yaml`, `.ini`, `.json`, `.sh`, `.bat`, `.md`, `.dockerfile`, `.conf`, `.toml`, `.xml`).

Used for:
- Configuration inference
- Environment detection
- DevOps pipeline mapping
- Documentation linkage
- Unknown or proprietary syntax structures

---

## Configuration Recognition
Detect and record configuration or environment variables:
- `.env`, `config.*`, `settings.*`, `*.yaml`, `*.json`, `*.toml`
- Patterns:
  - `KEY=VALUE` → environment variable
  - `"connectionString"` / `"Database"` / `"URL"` → integration endpoints
  - `"auth"`, `"secret"`, `"token"`, `"key"` → potential credential keys
- Capture structure depth to infer hierarchy.

Output:
```json
{
  "type": "configuration",
  "keys_detected": [...],
  "is_secret": [true/false],
  "source_file": "...",
  "line_number": ...
  	}
  ```
  ## DevOps / Build Artifacts

Detect automation or build scripts:

CI/CD: .github/workflows, .gitlab-ci.yml, azure-pipelines.yml, jenkinsfile.

Containers: Dockerfile, compose.yaml, kubernetes/*.yaml.

Infrastructure: Terraform (.tf), CloudFormation (.template).

Extract:

Step names, environments, triggers.

External services (AWS, Azure, GCP, etc.).

Resource definitions (pods, buckets, queues).

Mark findings as:
category: devops
subtype: {build, deploy, container, infra}
## Documentation / Knowledge Files

Recognize doc anchors:

Markdown, RST, TXT, or XML docs referencing APIs, modules, or data models.

Extract heading structure for navigation metadata.

Capture links to internal components ([ComponentName]()).

Output type:
category: documentation
title: Heading
links: [array of targets]
## Security and Compliance Smells

Flag issues across all generic files:

Plaintext credentials or tokens in .env / .json.

Embedded API keys or SSH private keys.

Unrestricted CORS / access in deployment descriptors.

Missing environment segregation (same config for dev/prod).

## Integration Points

Identify cross-language glue code:

Config values referencing external services (databases, APIs, queues).

URLs or hostnames in config files.

Scripted service calls (curl, wget, Invoke-WebRequest, etc.).

Store as:
integration_type: {api, db, message_queue, external_service}
confidence: {HIGH|MEDIUM|LOW}
source_file: ...
## Summary Behavior

Use pattern-matching and key heuristics only (no AST).

Always assign confidence scores and store results in .meta/config-registry.json and .meta/integrations.json.

If overlapping with another handler, defer to higher-priority language.

Never discard partial results — tag them "handler": "generic_fallback".

## Confidence Heuristics
| Evidence Type                              | Confidence |
| ------------------------------------------ | ---------- |
| Explicit file (e.g., .env, Dockerfile)     | HIGH       |
| Structured key-value (e.g., YAML, JSON)    | MEDIUM     |
| Inferred pattern (e.g., plain text matches “password=”) | LOW |


---

### ✅ Manifest Update  
Now, update your `index.json` to register it:

Add at the end of the `"languages"` array:

```json
{
  "name": "generic",
  "aliases": ["config", "yaml", "yml", "json", "toml", "ini", "dockerfile", "bash", "sh", "powershell", "md", "xml"],
  "pattern_file": "generic.md",
  "handler": "regex_text_parser",
  "priority": 4
}
