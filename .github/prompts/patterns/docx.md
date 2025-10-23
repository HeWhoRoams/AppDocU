# Pattern Pack — Microsoft Word (.docx) / Documentation Files

## Purpose
Extracts contextual and architectural information from `.docx` documents that may contain:
- Functional specifications
- Design notes
- Architecture diagrams (captions / alt text)
- API definitions
- Meeting records or decisions

---

## Parsing Strategy
1. Read all `.docx` files in the repository.  
2. Convert them to plain text (preserving headings and bullet indentation).  
3. Detect sections with headers such as:
   - “Overview”, “Architecture”, “Components”, “Data Flow”
   - “Authentication”, “Security”, “Known Issues”
   - “API”, “Endpoints”, “Inputs”, “Outputs”
4. Extract paragraphs and list items beneath each heading.

---

## Extraction Goals
Produce metadata entries for each `.docx` containing:

```json
{
  "file": "docs/Architecture.docx",
  "section": "Authentication Flow",
  "summary": "Describes JWT issuance from API Gateway",
  "inferred_component": "AuthService",
  "confidence": "MEDIUM",
  "tags": ["design", "security", "auth"]
}
If diagrams or tables are present:

Extract their captions (<w:caption> or paragraph before image).

Record them as inferred relationships or configuration hints.

Integration Behavior

Feed results into .meta/docx-evidence.json.

These become part of Pass 2 inference (inference-evidence.md).

Use docx-derived sections to resolve $PLACEHOLDERs (e.g., $ARCHITECTURE_OVERVIEW).

Confidence Rules
Evidence Type	Confidence
Explicit section headers	HIGH
Bulleted details under known headings	MEDIUM
Unstructured narrative text	LOW


---

## 🧭 2. Update `patterns/index.json`

Add the new handler entry just before “generic”:

```json
{
  "name": "docx",
  "aliases": [".docx"],
  "pattern_file": "docx.md",
  "handler": "docx_text_extractor",
  "priority": 4
}
