# AppDocU Preprocessor & Normalizer

## Overview

The AppDocU Preprocessor & Normalizer is a document conversion system that transforms Microsoft Office and binary document formats into text- or structure-based representations before AppDocU analysis. This ensures that all documentation in a repository can be treated as searchable text or structured evidence.

## Features

- **Multi-format Support**: Converts `.docx`, `.xlsx`, `.pptx`, `.pdf`, and `.vsdx` files
- **Deterministic Output**: Idempotent conversions with file hash validation
- **Comprehensive Indexing**: JSON index files with metadata for all conversions
- **Error Resilience**: Individual file failures don't halt the entire process
- **Thread-Safe**: Supports concurrent conversion with file-level locks

## Installation

The preprocessor is included as part of the AppDocU package. Ensure you have the required dependencies installed:

```bash
pip install python-docx docx2txt openpyxl python-pptx pdfminer.six vsdx
```

## Usage

### Command Line Interface

```bash
python -m appdocu_preprocessor.normalize --path <repository_path>
```

**Example:**
```bash
python -m appdocu_preprocessor.normalize --path "C:\Github\MyProject"
```

### Output Structure

After running the preprocessor, you'll find the following structure in your repository:

```
MyProject/
├── _normalized/
│   ├── docx/          # Converted DOCX files -> Markdown
│   ├── xlsx/          # Converted XLSX files -> CSV (per sheet)
│   ├── pptx/          # Converted PPTX files -> Markdown outline
│   ├── pdf/           # Converted PDF files -> Markdown
│   ├── visio/         # Converted VSDX files -> JSON + Mermaid
│   ├── normalize.index.json    # Index of all conversions
│   ├── normalized-map.json     # Mapping of original to converted files
│   └── normalize.log          # Conversion logs
```

## Supported Formats

### DOCX → Markdown
- Preserves heading hierarchy (Heading 1 → `#`, Heading 2 → `##`, etc.)
- Maintains bullet lists, bold, italics
- Includes table conversion
- Adds metadata header with source information

### XLSX → CSV
- One CSV file per Excel sheet
- Uses first non-empty row as headers
- Strips formulas, keeps evaluated values
- Limits output to 50,000 rows per sheet
- UTF-8 encoding with proper quoting

### PPTX → Markdown Outline
- Each slide becomes a section with `##` heading
- Bullet points from slide content
- Speaker notes included under "Notes:" section
- Captures slide titles and hierarchy

### PDF → Markdown
- Extracts textual content only
- Reconstructs paragraphs from single-line breaks
- Preserves document structure
- Includes page count and character statistics

### Visio (VSDX) → JSON + Mermaid
- **JSON Output**: Semantic data with shapes, connectors, and coordinates
- **Mermaid Output**: Flowchart representation of the diagram
- Supports multiple pages
- Captures connector labels and relationships

## Output Files

### normalize.index.json
Structured metadata about all processed documents:

```json
{
  "generated_at": "2025-10-24T13:00:00Z",
  "documents": [
    {
      "source": "docs/Architecture.docx",
      "output": "_normalized/docx/Architecture.md",
      "converter": "docx_to_md",
      "status": "success",
      "pages": 12,
      "hash": "a2f4e..."
    }
  ]
}
```

### normalized-map.json
Simple mapping of original filenames to converted outputs:

```json
{
  "Architecture.docx": "_normalized/docx/Architecture.md",
  "Config.xlsx:Sheet1": "_normalized/xlsx/Config_Sheet1.csv",
  "Architecture.vsdx": "_normalized/visio/Architecture.json"
}
```

## Integration with AppDocU

The preprocessor should be run **before** any AppDocU Passes:

1. **Before Pass 1**: Run normalization step
2. **Pass 1 Discovery**: Treat `_normalized/` outputs as canonical text sources
3. **Pass 2 Enrichment**: Cite normalized outputs with `(Evidence: converted from <original>)`
4. **Diagram Orchestrator**: Merge Visio `.mmd` files with code-derived graphs

## Error Handling

- Individual file conversion failures are logged but don't stop the process
- Failed conversions are recorded in the index with error messages
- Corrupted or unsupported files are skipped with warnings
- All logs are written to `_normalized/normalize.log`

## Quality Assurance

- **Non-Destructive**: Original files are never modified
- **Idempotent**: Re-running on unchanged files does nothing
- **UTF-8 Compliance**: All text outputs are UTF-8 encoded
- **Schema Validation**: Index files conform to JSON schemas
- **Thread-Safe**: Concurrent conversion support with locks

## Adding New Converters

To add support for additional file formats:

1. Create a new converter module in `appdocu_preprocessor/converters/`
2. Implement a `convert(file_path, output_dir)` function
3. Register the converter in `normalize.py`:
   ```python
   normalizer.register_converter('.newext', new_converter.convert)
   ```

## Testing

Run the unit tests to verify functionality:

```bash
python -m unittest tests.test_normalize
```

## Troubleshooting

### Common Issues

- **Missing Dependencies**: Ensure all required libraries are installed
- **File Permissions**: Check that the tool has read/write access to the repository
- **Large Files**: XLSX files are limited to 50,000 rows per sheet
- **Corrupted Files**: Invalid format files are logged and skipped

### Logging

Detailed logs are available in `_normalized/normalize.log` with timestamps, errors, and conversion statistics.
