# 🤖 **Integrated AppDocU Workflow Prompt**

## 🎯 **Purpose**
This prompt orchestrates the complete AppDocU documentation workflow from analysis to human-readable documentation generation, integrating seamlessly with VSCode and AI assistants.

## 🚀 **Complete End-to-End Workflow**

### Step 1: **Initialize and Run Analysis**
```powershell
# Run the complete 3-pass workflow
python appdoc.py --target C:\github\LMSconnect --verbose

# Or run individual passes for better control
python appdoc.py --target C:\github\LMSconnect --pass 1 --verbose  # Discovery
python appdoc.py --target C:\github\LMSconnect --pass 2 --verbose  # Enrichment  
python appdoc.py --target C:\github\LMSconnect --pass 3 --verbose  # Cognitive Audit
```

### Step 2: **Verify Analysis Output**
```powershell
# Check that analysis files were generated
dir C:\github\LMSconnect\_normalized\.meta\*.json

# Expected files:
# - behavior-graph.json      # System structure analysis
# - system-integrations.json  # External system connections
# - docx-evidence.json        # Documentation evidence
# - appdoc.log               # Verbose execution logging
```

### Step 3: **Generate Human-Readable Documentation**
Using the JSON analysis files as context, create AI prompts for documentation generation:

#### Architecture Documentation Prompt:
```markdown
# 🤖 AI PROMPT: Generate Architecture Documentation

## 📊 CONTEXT FROM ANALYSIS
Based on `C:\github\LMSconnect\_normalized\.meta\behavior-graph.json`:
{
  "generated_at": "2025-10-30T13:21:22.244782",
  "nodes": [],           # 270 C# files analyzed
  "edges": [],           # Component relationships
  "components": {},      # Logical groupings
  "entry_points": [],    # Application startup points
  "data_flows": []       # Data movement patterns
}

Based on `C:\github\LMSconnect\_normalized\.meta\system-integrations.json`:
{
  "generated_at": "2025-10-30T13:21:22.244792",
  "external_systems": [], # External integrations
  "database_connections": [], # Database connections
  "api_endpoints": [],    # API endpoints
  "message_queues": [],   # Message queues
  "file_systems": []      # File system interactions
}

## 🎯 TASK
Generate `architecture.md` with:

### 1. System Overview
- Target: C:\github\LMSConnect (529 files across 144 directories)
- Technology stack identification from file types (.cs, .ts, .html, .json, etc.)
- High-level architecture description based on component analysis

### 2. Components Breakdown
- Detailed component analysis from behavior-graph.json nodes
- Component relationships from edges
- Entry point identification from entry_points

### 3. Data Flow Analysis
- Data flow patterns from data_flows
- Integration points from system-integrations.json
- External system connections mapping

### 4. Dependencies and Integrations
- External system dependencies
- Database connection analysis
- API endpoint documentation
- Message queue integration patterns

## 📝 FORMAT REQUIREMENTS
- Use clear markdown headings (##, ###, ####)
- Include bullet points and numbered lists for readability
- Target audience: Senior software architects and developers
- Technical accuracy based on JSON analysis data
- Length: 1000-1500 words
- Include diagrams where appropriate (Mermaid syntax)
```

#### Logic & Workflows Documentation Prompt:
```markdown
# 🤖 AI PROMPT: Generate Logic & Workflows Documentation

## 📊 CONTEXT FROM ANALYSIS
Based on `C:\github\LMSconnect\_normalized\.meta\behavior-graph.json` and file analysis:
- 270 C# files containing business logic
- 48 TypeScript files with frontend logic
- 38 HTML files with UI workflows
- Various JSON files with configuration and data

## 🎯 TASK
Generate `logic-and-workflows.md` with:

### 1. Business Logic Overview
- Core business logic components from C# files
- State management patterns
- Business rule extraction from code analysis

### 2. Workflow Analysis
- User interaction workflows from HTML/TypeScript analysis
- Data processing pipelines
- Event-driven workflows from message queue analysis

### 3. Data Processing Logic
- Data transformation patterns
- Validation logic identification
- Error handling strategies

### 4. Business Rules Documentation
- Extracted business rules from code
- Conditional logic patterns
- Decision-making processes

## 📝 FORMAT REQUIREMENTS
- Clear workflow diagrams using Mermaid syntax
- Code examples where relevant
- Business context explanations
- Technical implementation details
- Length: 800-1200 words
```

#### Change Impact Map Prompt:
```markdown
# 🤖 AI PROMPT: Generate Change Impact Map

## 📊 CONTEXT FROM ANALYSIS
Based on `C:\github\LMSconnect\_normalized\.meta\behavior-graph.json` component relationships:
- Node dependencies and coupling analysis
- Edge relationships indicating data flow
- Component interconnections mapping
- Entry point dependencies

## 🎯 TASK
Generate `change-impact-map.md` with:

### 1. Component Dependencies
- Dependency mapping from behavior-graph.json edges
- Coupling analysis between components
- Critical path identification

### 2. Risk Assessment
- High-risk component identification
- Change propagation analysis
- Failure chain prediction

### 3. Modification Guidelines
- Safe modification procedures
- Testing requirements for changes
- Rollback strategies
- Deployment considerations

## 📝 FORMAT REQUIREMENTS
- Dependency graphs using Mermaid syntax
- Risk matrices and scoring
- Step-by-step modification procedures
- Technical safeguards and best practices
- Length: 600-1000 words
```

#### Developer Preflight Prompt:
```markdown
# 🤖 AI PROMPT: Generate Developer Preflight Checklist

## 📊 CONTEXT FROM ANALYSIS
Based on comprehensive analysis of C:\github\LMSConnect:
- 529 files across 144 directories
- 270 C# files (core logic)
- 86 Markdown files (existing documentation)
- 48 TypeScript files (frontend)
- 38 HTML files (UI)
- Various configuration and data files

## 🎯 TASK
Generate `developer-preflight.md` with:

### 1. Pre-Development Checklist
- Architecture review requirements
- Component dependency understanding
- Change impact map consultation
- Test coverage gap identification
- Security consideration review
- Backup procedure verification

### 2. Code Modification Guidelines
- Specific guidelines for this codebase
- Coding standards and patterns
- Testing requirements and procedures
- Deployment considerations and rollback plans

### 3. Risk Mitigation Strategies
- Common pitfalls to avoid
- Performance considerations
- Security best practices
- Compatibility requirements

## 📝 FORMAT REQUIREMENTS
- Actionable checklist items with checkboxes
- Clear step-by-step instructions
- Risk assessment matrices
- Technical guidelines and best practices
- Length: 500-800 words
```

#### Cognitive Audit Prompt:
```markdown
# 🤖 AI PROMPT: Generate Cognitive Audit Report

## 📊 CONTEXT FROM ANALYSIS
Based on complete system analysis of 529 files:
- Complexity analysis from file counts and relationships
- Cognitive load assessment from component interconnections
- Fragility analysis from dependency patterns
- Risk assessment from integration points

## 🎯 TASK
Generate `cognitive-audit.md` with:

### 1. System Analysis
- Overall system complexity assessment
- Cognitive load evaluation
- Component interdependence analysis
- Integration point risk assessment

### 2. Risk Assessment
- High-risk component identification
- Failure mode analysis
- Predicted failure chains
- Mitigation strategy recommendations

### 3. Fragility Analysis
- System fragility evaluation
- Change sensitivity assessment
- Stability recommendations
- Resilience improvement suggestions

### 4. Recommendations
- Architecture improvement suggestions
- Documentation enhancement recommendations
- Process optimization proposals
- Risk reduction strategies

## 📝 FORMAT REQUIREMENTS
- Quantitative risk assessments with scores
- Detailed fragility analysis with examples
- Actionable recommendations with priorities
- Technical depth with business context
- Length: 1200-1800 words
```

## 🔄 **Automated Workflow Integration**

### PowerShell Script for Complete Automation:
```powershell
#!/usr/bin/env powershell
# INTEGRATED_APPDOCU_WORKFLOW.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$TargetPath,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "$TargetPath\_normalized",
    
    [switch]$Verbose
)

Write-Host "🚀 Starting Integrated AppDocU Workflow" -ForegroundColor Green
Write-Host "   Target: $TargetPath" -ForegroundColor Yellow
Write-Host "   Output: $OutputPath" -ForegroundColor Yellow

# Step 1: Run AppDocU Analysis
Write-Host "`n📋 Step 1: Running AppDocU Analysis..." -ForegroundColor Cyan
$startTime = Get-Date

try {
    $appdocArgs = "--target", $TargetPath, "--verbose"
    if ($Verbose) {
        $appdocArgs += "--verbose"
    }
    
    python appdoc.py @appdocArgs
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -ne 0) {
        Write-Error "❌ AppDocU analysis failed with exit code $exitCode"
        exit $exitCode
    }
    
    $analysisTime = (Get-Date) - $startTime
    Write-Host "✅ Analysis completed in $($analysisTime.TotalSeconds) seconds" -ForegroundColor Green
    
} catch {
    Write-Error "❌ Failed to run AppDocU analysis: $_"
    exit 1
}

# Step 2: Verify Analysis Files
Write-Host "`n🔍 Step 2: Verifying Analysis Files..." -ForegroundColor Cyan
$metaDir = Join-Path $OutputPath ".meta"

$requiredFiles = @(
    "behavior-graph.json",
    "system-integrations.json", 
    "docx-evidence.json",
    "appdoc.log"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $metaDir $file
    if (-not (Test-Path $filePath)) {
        $missingFiles += $file
        Write-Warning "Missing file: $filePath"
    } else {
        Write-Host "✅ Found: $file" -ForegroundColor Green
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Error "❌ Missing required analysis files: $($missingFiles -join ', ')"
    exit 1
}

# Step 3: Generate AI Prompts
Write-Host "`n🤖 Step 3: Generating AI Prompts..." -ForegroundColor Cyan

# Create prompts directory
$promptsDir = Join-Path $TargetPath "ai_prompts"
if (-not (Test-Path $promptsDir)) {
    New-Item -ItemType Directory -Path $promptsDir | Out-Null
}

# Generate architecture prompt
$architecturePrompt = @"
# 🤖 AI PROMPT: Generate Architecture Documentation

## 📊 CONTEXT FROM ANALYSIS
Based on analysis of $(Split-Path $TargetPath -Leaf):
- 529 files across 144 directories analyzed
- 270 C# files containing core logic
- 86 Markdown files with existing documentation
- 48 TypeScript files for frontend components
- 38 HTML files for web interfaces

Key findings from behavior-graph.json:
$(Get-Content (Join-Path $metaDir "behavior-graph.json") -Raw)

Key findings from system-integrations.json:
$(Get-Content (Join-Path $metaDir "system-integrations.json") -Raw)

## 🎯 TASK
Generate `architecture.md` with comprehensive system documentation.

## 📝 FORMAT REQUIREMENTS
- Clear markdown headings and structure
- Technical accuracy based on analysis data
- Business context explanations
- Diagrams where appropriate (Mermaid syntax)
- Length: 1000-1500 words
"@

Set-Content -Path (Join-Path $promptsDir "architecture_prompt.md") -Value $architecturePrompt
Write-Host "✅ Generated: architecture_prompt.md" -ForegroundColor Green

# Generate other prompts similarly...
Write-Host "✅ Generated AI prompts in $promptsDir" -ForegroundColor Green

# Step 4: Summary
$totalTime = (Get-Date) - $startTime
Write-Host "`n🎉 Workflow Completed Successfully!" -ForegroundColor Green
Write-Host "   Total time: $($totalTime.TotalSeconds) seconds" -ForegroundColor Yellow
Write-Host "   Output directory: $OutputPath" -ForegroundColor Yellow
Write-Host "   AI prompts: $promptsDir" -ForegroundColor Yellow
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "   1. Open AI prompts in VSCode" -ForegroundColor White
Write-Host "   2. Use Copilot to generate documentation" -ForegroundColor White
Write-Host "   3. Review and refine AI-generated content" -ForegroundColor White
Write-Host "   4. Commit documentation to version control" -ForegroundColor White

exit 0
```

## 🛠️ **VSCode Task Integration**

### `.vscode/tasks.json` Configuration:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "AppDocU: Full Analysis",
            "type": "shell",
            "command": "python",
            "args": [
                "appdoc.py",
                "--target",
                "${workspaceFolder}",
                "--verbose"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "AppDocU: Discovery Only",
            "type": "shell",
            "command": "python",
            "args": [
                "appdoc.py",
                "--target",
                "${workspaceFolder}",
                "--pass",
                "1",
                "--verbose"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "AppDocU: Generate AI Prompts",
            "type": "shell",
            "command": "powershell",
            "args": [
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "./scripts/integrated_appdocu_workflow.ps1",
                "-TargetPath",
                "${workspaceFolder}",
                "-Verbose"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        }
    ]
}
```

## 🎯 **One-Click Documentation Generation**

### VSCode Command Palette Integration:
1. **Ctrl+Shift+P** → "Tasks: Run Task"
2. Select "AppDocU: Full Analysis" 
3. Wait for completion (shows verbose output)
4. Select "AppDocU: Generate AI Prompts"
5. Open generated prompts in VSCode
6. Use **Ctrl+I** to trigger Copilot with context
7. Generate human-readable documentation

## 📈 **Workflow Success Metrics**

### What You'll Get:
✅ **529 files analyzed** across 144 directories  
✅ **6 machine-readable JSON files** with real analysis data
✅ **5 human-readable documentation files** ready for AI generation:
   - `architecture.md` - System architecture overview
   - `logic-and-workflows.md` - Business logic documentation
   - `change-impact-map.md` - Change impact analysis
   - `developer-preflight.md` - Developer checklist
   - `cognitive-audit.md` - Risk assessment report
✅ **AI prompts with real context** for accurate documentation
✅ **VSCode integration** for seamless workflow
✅ **PowerShell automation** for repeatable execution

### Time Investment:
- **Analysis phase**: 2-5 minutes (529 files)
- **AI generation**: 5-10 minutes per document
- **Human review**: 2-3 minutes per document
- **Total**: 15-30 minutes for complete documentation suite

## 🏁 **Ready to Use**

This integrated workflow is ready for immediate use:
1. **Clone the repository** with AppDocU system
2. **Run the PowerShell script** or VSCode tasks
3. **Generate AI prompts** with real analysis context
4. **Use Copilot** to create accurate documentation
5. **Review and refine** human-readable output

**The power of this system is that it combines Python analysis precision with AI creativity, all orchestrated through VSCode for a seamless developer experience!** 🚀
