# AppDocU Recovery Task List
 
## 🚨 IMMEDIATE ACTIONS (Do These First)

### Task 0: Clean Slate
```bash
# Delete all stub files
cd C:\Github\LMSconnect
del architecture.md change-impact-map.md logic-and-workflows.md

# Delete fake script
del C:\Github\AppDocU\clean_appdoc.py

# Verify cleanup
dir *.md  # Should not show the stub files
```

### Task 1: Update Constitution
```bash
# Replace constitution.md with the updated v1.2 version
# Save the artifact I provided as constitution.md
```

### Task 2: Create Gate Validation Script

Create `validate_gates.ps1`:

```powershell
# validate_gates.ps1
# Gate validation script for AppDocU implementation

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("1.1","1.2","1.3","2.1","2.2","2.3","3.1","3.2")]
    [string]$Gate
)

function Test-Gate11 {
    Write-Host "=== GATE 1.1: C# Project Structure ===" -ForegroundColor Yellow
    
    $required = @(
        "DocTool\DocTool.csproj",
        "DocTool\Program.cs",
        "DocTool\Models\CodeArtifact.cs"
    )
    
    foreach ($file in $required) {
        if (Test-Path $file) {
            Write-Host "✅ $file exists" -ForegroundColor Green
        } else {
            Write-Host "❌ $file MISSING" -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "`nBuilding C# project..." -ForegroundColor Yellow
    dotnet restore DocTool\DocTool.csproj
    $buildResult = dotnet build DocTool\DocTool.csproj -c Release
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Build successful" -ForegroundColor Green
        
        if (Test-Path "DocTool\bin\Release\net8.0\DocTool.exe") {
            Write-Host "✅ Executable exists" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Executable not found" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ Build failed" -ForegroundColor Red
        return $false
    }
}

function Test-Gate12 {
    Write-Host "=== GATE 1.2: Core Analysis Engine ===" -ForegroundColor Yellow
    
    # Check required files
    $required = @(
        "DocTool\Analysis\RoslynAnalyzer.cs",
        "DocTool\Analysis\AstInspector.cs",
        "DocTool\Commands\AnalyzeFileCommand.cs"
    )
    
    foreach ($file in $required) {
        if (Test-Path $file) {
            Write-Host "✅ $file exists" -ForegroundColor Green
        } else {
            Write-Host "❌ $file MISSING" -ForegroundColor Red
            return $false
        }
    }
    
    # Create test file
    $testFile = "TestClass.cs"
    @"
namespace TestNamespace {
    /// <summary>Test class</summary>
    public class TestClass {
        public void TestMethod() { }
    }
}
"@ | Out-File $testFile -Encoding UTF8
    
    Write-Host "`nAnalyzing test file..." -ForegroundColor Yellow
    & DocTool\bin\Release\net8.0\DocTool.exe analyze-file --file $testFile --output test.json
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path "test.json")) {
        $content = Get-Content test.json -Raw
        $size = (Get-Item test.json).Length
        
        if ($size -gt 500) {
            Write-Host "✅ Artifact generated ($size bytes)" -ForegroundColor Green
            
            # Verify JSON structure
            $json = $content | ConvertFrom-Json
            if ($json.classes -and $json.methods -and $json.namespace) {
                Write-Host "✅ Valid JSON structure" -ForegroundColor Green
                return $true
            } else {
                Write-Host "❌ Invalid JSON structure" -ForegroundColor Red
                return $false
            }
        } else {
            Write-Host "❌ Artifact too small ($size bytes) - likely a stub" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ Analysis failed or no output" -ForegroundColor Red
        return $false
    }
}

function Test-Gate13 {
    Write-Host "=== GATE 1.3: Full Worker Completion ===" -ForegroundColor Yellow
    
    $required = @(
        "DocTool\Output\ArtifactGenerator.cs",
        "DocTool\Logging\StructuredLogger.cs"
    )
    
    foreach ($file in $required) {
        if (Test-Path $file) {
            Write-Host "✅ $file exists" -ForegroundColor Green
        } else {
            Write-Host "❌ $file MISSING" -ForegroundColor Red
            return $false
        }
    }
    
    # Find 5 C# files to analyze
    $testFiles = Get-ChildItem -Path "." -Filter "*.cs" -Recurse -Exclude "*\obj\*","*\bin\*" | Select-Object -First 5
    
    if ($testFiles.Count -lt 5) {
        Write-Host "⚠️ Less than 5 C# files found, analyzing available files" -ForegroundColor Yellow
    }
    
    $artifactsDir = "artifacts_test"
    New-Item -ItemType Directory -Force -Path $artifactsDir | Out-Null
    
    $successCount = 0
    foreach ($file in $testFiles) {
        $outputFile = Join-Path $artifactsDir "$($file.Name).json"
        & DocTool\bin\Release\net8.0\DocTool.exe analyze-file --file $file.FullName --output $outputFile
        
        if ($LASTEXITCODE -eq 0 -and (Test-Path $outputFile)) {
            $size = (Get-Item $outputFile).Length
            if ($size -gt 1024) {
                Write-Host "✅ $($file.Name) analyzed ($size bytes)" -ForegroundColor Green
                $successCount++
            } else {
                Write-Host "⚠️ $($file.Name) artifact too small ($size bytes)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ $($file.Name) analysis failed" -ForegroundColor Red
        }
    }
    
    if ($successCount -ge $testFiles.Count) {
        Write-Host "`n✅ All files analyzed successfully" -ForegroundColor Green
        return $true
    } else {
        Write-Host "`n❌ Some files failed analysis ($successCount/$($testFiles.Count))" -ForegroundColor Red
        return $false
    }
}

function Test-Gate21 {
    Write-Host "=== GATE 2.1: Python Basic Structure ===" -ForegroundColor Yellow
    
    $required = @(
        "requirements.txt",
        "orchestrator\__init__.py",
        "orchestrator\config.py",
        "orchestrator\logger.py"
    )
    
    foreach ($file in $required) {
        if (Test-Path $file) {
            Write-Host "✅ $file exists" -ForegroundColor Green
        } else {
            Write-Host "❌ $file MISSING" -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    Write-Host "`nTesting imports..." -ForegroundColor Yellow
    python -c "from orchestrator.config import Config; print('✅ Config import OK')"
    
    if ($LASTEXITCODE -eq 0) {
        return $true
    } else {
        Write-Host "❌ Import test failed" -ForegroundColor Red
        return $false
    }
}

function Test-Gate22 {
    Write-Host "=== GATE 2.2: C# Worker Integration ===" -ForegroundColor Yellow
    
    $required = @(
        "orchestrator\csharp_runner.py",
        "orchestrator\file_scanner.py"
    )
    
    foreach ($file in $required) {
        if (Test-Path $file) {
            Write-Host "✅ $file exists" -ForegroundColor Green
        } else {
            Write-Host "❌ $file MISSING" -ForegroundColor Red
            return $false
        }
    }
    
    # Test integration
    $testScript = @"
from pathlib import Path
from orchestrator.config import Config
from orchestrator.csharp_runner import CSharpRunner

config = Config(
    repo_path=Path('.'),
    output_path=Path('./test_output')
)

runner = CSharpRunner(config)
print('✅ CSharpRunner initialized')
"@
    
    $testScript | Out-File "test_integration.py" -Encoding UTF8
    python test_integration.py
    
    if ($LASTEXITCODE -eq 0) {
        Remove-Item "test_integration.py"
        return $true
    } else {
        Write-Host "❌ Integration test failed" -ForegroundColor Red
        return $false
    }
}

function Test-Gate23 {
    Write-Host "=== GATE 2.3: Full Orchestrator Completion ===" -ForegroundColor Yellow
    
    $required = @(
        "run_docs.py",
        "orchestrator\llm_client.py",
        "orchestrator\artifact_processor.py",
        "orchestrator\error_handler.py"
    )
    
    foreach ($file in $required) {
        if (Test-Path $file) {
            Write-Host "✅ $file exists" -ForegroundColor Green
        } else {
            Write-Host "❌ $file MISSING" -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "`nRunning dry-run test..." -ForegroundColor Yellow
    python run_docs.py --path . --dry-run --verbose
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dry-run successful" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Dry-run failed" -ForegroundColor Red
        return $false
    }
}

function Test-Gate31 {
    Write-Host "=== GATE 3.1: End-to-End Workflow ===" -ForegroundColor Yellow
    
    $testRepo = Read-Host "Enter path to test C# repository"
    
    Write-Host "`nRunning full workflow..." -ForegroundColor Yellow
    python run_docs.py --path $testRepo --output ./docs_output_test --verbose
    
    if ($LASTEXITCODE -eq 0) {
        $artifacts = Get-ChildItem -Path "docs_output_test\artifacts" -Filter "*.json"
        $stubCount = 0
        
        foreach ($artifact in $artifacts) {
            if ($artifact.Length -lt 1024) {
                $stubCount++
                Write-Host "⚠️ Potential stub: $($artifact.Name) ($($artifact.Length) bytes)" -ForegroundColor Yellow
            }
        }
        
        if ($stubCount -eq 0) {
            Write-Host "✅ All artifacts appear valid" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Found $stubCount potential stub files" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ Workflow failed" -ForegroundColor Red
        return $false
    }
}

function Test-Gate32 {
    Write-Host "=== GATE 3.2: LLM Integration ===" -ForegroundColor Yellow
    
    Write-Host "Checking .env configuration..." -ForegroundColor Yellow
    if (-not (Test-Path ".env")) {
        Write-Host "❌ .env file not found" -ForegroundColor Red
        return $false
    }
    
    $testRepo = Read-Host "Enter path to test C# repository"
    
    Write-Host "`nRunning full workflow with LLM..." -ForegroundColor Yellow
    python run_docs.py --path $testRepo --output ./docs_final
    
    if ($LASTEXITCODE -eq 0) {
        if (Test-Path "docs_final\README.md") {
            $size = (Get-Item "docs_final\README.md").Length
            if ($size -gt 5120) {
                Write-Host "✅ README.md generated ($size bytes)" -ForegroundColor Green
                return $true
            } else {
                Write-Host "❌ README.md too small ($size bytes) - likely stub" -ForegroundColor Red
                return $false
            }
        } else {
            Write-Host "❌ README.md not found" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ Workflow failed" -ForegroundColor Red
        return $false
    }
}

# Main execution
switch ($Gate) {
    "1.1" { $result = Test-Gate11 }
    "1.2" { $result = Test-Gate12 }
    "1.3" { $result = Test-Gate13 }
    "2.1" { $result = Test-Gate21 }
    "2.2" { $result = Test-Gate22 }
    "2.3" { $result = Test-Gate23 }
    "3.1" { $result = Test-Gate31 }
    "3.2" { $result = Test-Gate32 }
}

if ($result) {
    Write-Host "`n✅ GATE $Gate PASSED" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n❌ GATE $Gate FAILED" -ForegroundColor Red
    exit 1
}
```

---

## 📋 PHASE 1: C# WORKER IMPLEMENTATION

### Task 1.1: Create Project Structure

**Command to Cline/Qwen:**
```
TASK: Create C# Worker Project Structure

CONTEXT: We are implementing Gate 1.1 of the AppDocU Constitution v1.2

REQUIREMENTS:
1. Create directory structure:
   DocTool/
   ├── DocTool.csproj
   ├── Program.cs
   └── Models/
       └── CodeArtifact.cs

2. Use EXACTLY this DocTool.csproj content:
[paste exact content from specification]

3. Use EXACTLY this Program.cs content:
[paste exact content from specification]

4. Use EXACTLY this CodeArtifact.cs content:
[paste exact content from specification]

VALIDATION:
Run: .\validate_gates.ps1 -Gate "1.1"

STOP CONDITIONS:
- Do NOT proceed to Task 1.2 until Gate 1.1 passes
- Do NOT modify the provided code
- Do NOT create workarounds

DELIVERABLE:
- Working DocTool.exe in bin/Release/net8.0/
- Zero build errors
- Gate 1.1 validation passes
```

### Task 1.2: Implement Core Analysis

**Command to Cline/Qwen:**
```
TASK: Implement Roslyn Analysis Engine

CONTEXT: Gate 1.1 has passed. Implementing Gate 1.2.

PREREQUISITES:
- ✅ Gate 1.1 passed
- ✅ DocTool.exe builds successfully

REQUIREMENTS:
1. Create these files EXACTLY as specified:
   - DocTool/Analysis/RoslynAnalyzer.cs
   - DocTool/Analysis/AstInspector.cs
   - DocTool/Analysis/DependencyResolver.cs
   - DocTool/Commands/AnalyzeFileCommand.cs

2. Do NOT modify the architecture
3. Do NOT skip Roslyn usage
4. Implement ALL methods shown in specification

VALIDATION:
Run: .\validate_gates.ps1 -Gate "1.2"

Expected behavior:
- Analyzes TestClass.cs
- Generates test.json > 500 bytes
- JSON contains actual class/method data

STOP CONDITIONS:
- Do NOT proceed until test.json is REAL DATA
- Do NOT generate stub JSON
- Artifact must contain parsed AST information

DELIVERABLE:
- Working analyze-file command
- Real artifact generation
- Gate 1.2 validation passes
```

### Task 1.3: Complete C# Worker

**Command to Cline/Qwen:**
```
TASK: Complete C# Worker Implementation

CONTEXT: Gate 1.2 has passed. Completing Phase 1.

PREREQUISITES:
- ✅ Gate 1.1 passed
- ✅ Gate 1.2 passed
- ✅ Basic analysis works

REQUIREMENTS:
1. Create remaining files:
   - DocTool/Output/ArtifactGenerator.cs
   - DocTool/Logging/StructuredLogger.cs
   - DocTool/Models/[all remaining model classes]

2. Implement ALL missing Analysis/* files

VALIDATION:
Run: .\validate_gates.ps1 -Gate "1.3"

Expected behavior:
- Analyzes 5 real C# files
- All artifacts > 1KB
- No stub files
- Exit code 0 for all files

DELIVERABLE:
- Fully functional C# Worker
- All analysis features working
- Gate 1.3 validation passes
```

---

## 📋 PHASE 2: PYTHON ORCHESTRATOR

### Task 2.1: Python Foundation

**Command to Cline/Qwen:**
```
TASK: Create Python Orchestrator Foundation

CONTEXT: Phase 1 complete. Starting Phase 2, Gate 2.1.

PREREQUISITES:
- ✅ All Phase 1 gates passed
- ✅ DocTool.exe fully functional

REQUIREMENTS:
1. Create Python structure:
   orchestrator/
   ├── __init__.py
   ├── config.py
   ├── logger.py
   └── [as specified]

2. Create requirements.txt with exact dependencies

3. Implement EXACTLY as specified

VALIDATION:
Run: .\validate_gates.ps1 -Gate "2.1"

STOP CONDITIONS:
- Do NOT implement analysis logic in Python
- Do NOT skip C# Worker calls
- Configuration must load successfully

DELIVERABLE:
- Working Python package structure
- All imports work
- Gate 2.1 validation passes
```

### Task 2.2: C# Integration

**Command to Cline/Qwen:**
```
TASK: Implement C# Worker Integration

CONTEXT: Gate 2.1 passed. Implementing subprocess integration.

PREREQUISITES:
- ✅ Gate 2.1 passed
- ✅ Python structure working

REQUIREMENTS:
1. Create orchestrator/csharp_runner.py
2. Create orchestrator/file_scanner.py
3. Implement subprocess calls to DocTool.exe
4. Parse exit codes correctly
5. Capture stdout/stderr

VALIDATION:
Run: .\validate_gates.ps1 -Gate "2.2"

Expected behavior:
- Python calls DocTool.exe successfully
- Exit codes captured
- JSON artifacts parsed
- Logs show C# Worker output

DELIVERABLE:
- Working subprocess integration
- Artifact collection working
- Gate 2.2 validation passes
```

### Task 2.3: Complete Orchestrator

**Command to Cline/Qwen:**
```
TASK: Complete Python Orchestrator

CONTEXT: Gate 2.2 passed. Completing Phase 2.

PREREQUISITES:
- ✅ Gate 2.2 passed
- ✅ C# Worker integration works

REQUIREMENTS:
1. Create run_docs.py CLI
2. Implement LLM client
3. Implement artifact processor
4. Implement error handler

VALIDATION:
Run: .\validate_gates.ps1 -Gate "2.3"

Expected behavior:
- python run_docs.py --dry-run works
- Files scanned
- C# Worker called
- No crashes

DELIVERABLE:
- Complete CLI tool
- Dry-run mode functional
- Gate 2.3 validation passes
```

---

## 📋 PHASE 3: INTEGRATION & TESTING

### Task 3.1: End-to-End Test

**Command to Cline/Qwen:**
```
TASK: End-to-End Workflow Test

CONTEXT: Phase 2 complete. Testing full workflow.

PREREQUISITES:
- ✅ All Phase 1 & 2 gates passed

REQUIREMENTS:
1. Run full workflow on test repository
2. Verify all artifacts generated
3. Check artifact sizes (no stubs)
4. Validate JSON structure

VALIDATION:
Run: .\validate_gates.ps1 -Gate "3.1"

PASS CRITERIA:
- All C# files analyzed
- All artifacts > 1KB
- Zero stub files
- Workflow completes successfully

DELIVERABLE:
- Proven end-to-end functionality
- Gate 3.1 validation passes
```

### Task 3.2: LLM Integration

**Command to Cline/Qwen:**
```
TASK: LLM Integration & Final Testing

CONTEXT: Gate 3.1 passed. Final integration.

PREREQUISITES:
- ✅ Gate 3.1 passed
- ✅ .env configured with LLM endpoint

REQUIREMENTS:
1. Test LLM API connection
2. Generate real documentation
3. Verify README.md > 5KB
4. Check documentation quality

VALIDATION:
Run: .\validate_gates.ps1 -Gate "3.2"

PASS CRITERIA:
- LLM API called successfully
- README.md contains REAL CONTENT
- All docs meet size requirements
- Human review confirms quality

DELIVERABLE:
- Complete working system
- Real documentation generated
- Gate 3.2 validation passes
```

---

## 🎯 CRITICAL SUCCESS FACTORS

### For You (Human)

1. **Run validation after EVERY task**
2. **Do NOT let Cline proceed if a gate fails**
3. **Check file sizes manually** if suspicious
4. **Review generated content** for quality

### For Cline/Qwen

1. **Follow Constitution v1.2 absolutely**
2. **Pass each gate before proceeding**
3. **Never generate stub files**
4. **Request help if stuck - don't fake success**

---

## 📞 EMERGENCY PROCEDURES

### If Cline Creates Stubs Again

1. STOP immediately
2. Delete all stub files
3. Restart from last passed gate
4. Apply 24-hour timeout before retrying

### If Cline Ignores Architecture

1. STOP immediately
2. Cite Constitution v1.2 Article 3
3. Delete all invalid code
4. Restart from Phase 1, Gate 1.1

### If You Get Frustrated

1. Take a break
2. Run validation to see actual progress
3. Review what gates have actually passed
4. Start from last valid gate

---

## 📊 PROGRESS TRACKING

Use this template to track progress:

```
PHASE 1: C# WORKER
[ ] Gate 1.1 - Project Structure
[ ] Gate 1.2 - Core Analysis  
[ ] Gate 1.3 - Full Worker

PHASE 2: PYTHON ORCHESTRATOR
[ ] Gate 2.1 - Python Foundation
[ ] Gate 2.2 - C# Integration
[ ] Gate 2.3 - Complete Orchestrator

PHASE 3: INTEGRATION
[ ] Gate 3.1 - End-to-End Test
[ ] Gate 3.2 - LLM Integration

VALIDATION
[ ] No stub files detected
[ ] All artifacts > minimum size
[ ] Human quality review passed
[ ] Constitution compliance verified
```

---

**Ready to begin? Start with Task 0 (cleanup) and then give Cline Task 1.1.**
