# 🔄 AppDocU VSCode Integration Guide

## 🎯 **Current Workflow Architecture**

The AppDocU system works in **3 distinct phases**:

### Phase 1: **Analysis Engine** (Python Scripts)
```bash
python appdoc.py --target C:\github\LMSconnect --pass 1  # Creates JSON analysis files
```
**Output**: Machine-readable JSON files with codebase structure
- `behavior-graph.json` - System architecture mapping
- `system-integrations.json` - External system connections  
- `docx-evidence.json` - Documentation evidence extraction

### Phase 2: **Documentation Generator** (AI Prompts)
VSCode/Copilot reads the JSON files and uses them as **context for AI prompts**
```markdown
<!-- AI Prompt Context -->
Based on behavior-graph.json, generate human-readable architecture documentation
```

### Phase 3: **Human Output** (Markdown Documentation)  
AI generates final documentation files:
- `architecture.md` - System architecture overview
- `logic-and-workflows.md` - Business logic documentation
- `change-impact-map.md` - Change impact analysis
- `developer-preflight.md` - Developer checklist
- `cognitive-audit.md` - Risk assessment report

## 🚀 **VSCode Integration Workflow**

### Step 1: **Run Analysis**
First, generate the machine-readable analysis files:
```powershell
# Terminal 1: Run discovery pass
python appdoc.py --target C:\github\LMSconnect --pass 1 --verbose
```

### Step 2: **Verify Analysis Files**
Check that JSON files were created:
```powershell
dir C:\github\LMSconnect\_normalized\.meta\*.json
```

Expected output:
```
behavior-graph.json      # System structure analysis
system-integrations.json  # Integration mapping  
docx-evidence.json        # Documentation evidence
```

### Step 3: **Use AI Prompts with Analysis Context**

#### Example: Generate Architecture Documentation
Create a new markdown file `architecture_prompt.md`:
```markdown
# AI Prompt: Generate Architecture Documentation

## Context
Based on the following system analysis from `behavior-graph.json`:

{
  "nodes": [...],           # 270 C# files analyzed
  "components": {...},      # Component relationships
  "entry_points": [...]     # Application entry points
}

## Instructions
Generate a comprehensive architecture.md file that includes:
1. System overview with component breakdown
2. Data flow diagrams based on node relationships  
3. Entry point analysis
4. Technology stack identification
5. Scalability considerations

## Format
Use clear headings, bullet points, and technical accuracy.
Target audience: Senior software architects and developers.
```

### Step 4: **VSCode Copilot Integration**

#### Method 1: **File-Based Prompting**
1. Open the JSON analysis file in VSCode
2. Select the relevant JSON content
3. Copy to clipboard
4. In a new markdown file, paste and add prompt:

```markdown
# Based on this system analysis:
[JSON CONTENT HERE]

Please generate architecture documentation with:
- Component overview
- Data flow description  
- Integration points
- Technology stack
```

5. Use **Ctrl+I** to trigger Copilot with selected content

#### Method 2: **Workspace Context Prompting**
1. Keep JSON files open in VSCode workspace
2. Create prompts that reference file paths:

```markdown
# System Architecture Generation

Refer to the following files in the workspace:
- `./_normalized/.meta/behavior-graph.json` for system structure
- `./_normalized/.meta/system-integrations.json` for integrations

Generate comprehensive architecture documentation.
```

### Step 5: **Automated Documentation Pipeline**

#### Create a PowerShell Script `generate-docs.ps1`:
```powershell
# Step 1: Run analysis
Write-Host "🚀 Running AppDocU Analysis..." -ForegroundColor Green
python appdoc.py --target "C:\github\LMSconnect" --pass 1 --verbose

# Step 2: Verify analysis files exist
$metaDir = "C:\github\LMSconnect\_normalized\.meta"
if (!(Test-Path "$metaDir\behavior-graph.json")) {
    Write-Error "❌ Analysis files not generated!"
    exit 1
}

Write-Host "✅ Analysis complete. Ready for AI documentation generation." -ForegroundColor Green
Write-Host "📁 Analysis files located at: $metaDir" -ForegroundColor Yellow
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Open JSON files in VSCode" -ForegroundColor White
Write-Host "   2. Create AI prompts referencing the analysis" -ForegroundColor White  
Write-Host "   3. Use Copilot to generate human-readable documentation" -ForegroundColor White
```

## 🧠 **AI Prompt Strategies**

### Strategy 1: **Context-First Prompts**
```markdown
# Context
System analysis shows 270 C# files with the following structure:
{
  "components": {
    "Program.cs": {"type": "entry_point", "dependencies": ["Startup.cs"]},
    "Startup.cs": {"type": "configuration", "dependencies": ["Services/*"]}
  }
}

# Task
Generate architecture.md with component relationship diagrams.
```

### Strategy 2: **Template-Guided Prompts**  
```markdown
# Template
Follow this structure for architecture.md:

## System Overview
[Based on behavior-graph.json nodes count]

## Components  
[List components from behavior-graph.json components]

## Data Flow
[Based on edges from behavior-graph.json]

## Integrations
[From system-integrations.json external_systems]
```

### Strategy 3: **Iterative Refinement**
```markdown
# Round 1: High-Level Overview
Based on the JSON analysis, generate a 500-word system overview.

# Round 2: Detailed Components  
Now expand each component with technical details from the analysis.

# Round 3: Risk Assessment
Identify potential issues from the cognitive-audit perspective.
```

## 🛠️ **VSCode Extensions for Enhanced Workflow**

### Recommended Extensions:
1. **GitHub Copilot** - AI pair programming
2. **JSON Viewer** - Better JSON file visualization  
3. **Markdown All in One** - Enhanced markdown editing
4. **Code Spell Checker** - Documentation quality control
5. **File Utils** - Easy file navigation and management

### VSCode Settings for AppDocU:
```json
{
  "files.associations": {
    "*.json": "jsonc"
  },
  "json.schemas": [
    {
      "fileMatch": ["behavior-graph.json", "system-integrations.json"],
      "url": "./schemas/appdocu-schema.json"
    }
  ],
  "editor.wordWrap": "on",
  "editor.rulers": [80, 100]
}
```

## 📋 **Workflow Best Practices**

### 1. **Incremental Processing**
```bash
# Run discovery for initial analysis
python appdoc.py --target C:\github\LMSconnect --pass 1

# Generate specific documentation pieces
python appdoc.py --target C:\github\LMSconnect --pass 2 --verbose

# Run final audit
python appdoc.py --target C:\github\LMSconnect --pass 3
```

### 2. **Version Control Integration**
```bash
# Before running analysis, commit current state
git add . && git commit -m "Pre-AppDocU analysis"

# Run analysis
python appdoc.py --target C:\github\LMSconnect --pass 1

# Commit generated analysis files
git add _normalized/.meta/*.json
git commit -m "AppDocU analysis files generated"
```

### 3. **Parallel Development**
- **Developer 1**: Runs analysis and generates JSON files
- **Developer 2**: Reviews JSON files and creates AI prompts  
- **Developer 3**: Uses AI to generate final documentation

## 🎯 **Next Steps for Your Workflow**

### Immediate Actions:
1. **Run the analysis**: `python appdoc.py --target C:\github\LMSconnect --pass 1 --verbose`
2. **Review generated JSON files** in `_normalized\.meta\`
3. **Create your first AI prompt** referencing the analysis data
4. **Use Copilot** to generate human-readable documentation

### Advanced Integration:
1. **Create custom VSCode tasks** for one-click analysis
2. **Set up GitHub Actions** for automated documentation generation
3. **Build prompt templates** for consistent documentation style
4. **Establish review workflows** for AI-generated content

The key insight is that **AppDocU provides the analysis engine**, and **you use VSCode/Copilot as the documentation generator** that consumes that analysis to create human-readable output!
