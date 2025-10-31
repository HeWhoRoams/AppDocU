# validate_gates.ps1
# Gate Validation Script for AppDoc
# Validates various checkpoints and quality gates for documentation processes

param(
    [string]$ConfigPath = "config.json",
    [string]$OutputPath = "validation_report.txt",
    [switch]$Verbose = $false,
    [switch]$FailFast = $false,
    [double]$MinCoverage = 70,
    [double]$MaxFailure = 10,
    [bool]$RequireDiagrams = $true
)

# Enable strict mode
Set-StrictMode -Version Latest

# Function to write verbose output
function Write-VerboseOutput {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "[VERBOSE] $Message" -ForegroundColor Cyan
    }
}

# Function to log validation results
function Write-ValidationResult {
    param(
        [string]$GateName,
        [bool]$Passed,
        [string]$Message,
        [string]$Details = ""
    )
    
    $status = if ($Passed) { "PASS" } else { "FAIL" }
    $color = if ($Passed) { "Green" } else { "Red" }
    
    Write-Host "[$status] $GateName - $Message" -ForegroundColor $color
    $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$status] $GateName - $Message"
    if ($Details) {
        $logEntry += " - Details: $Details"
    }
    Add-Content -Path $OutputPath -Value $logEntry
    
    if (-not $Passed -and $FailFast) {
        Write-Error "Gate validation failed: $GateName. Stopping due to FailFast flag."
        exit 1
    }
}

# Function to validate file existence gate
function Test-FileExistenceGate {
    param([string[]]$FilePaths, [string]$GateName = "File Existence")
    
    $allPassed = $true
    foreach ($filePath in $FilePaths) {
        $exists = Test-Path $filePath
        Write-ValidationResult -GateName $GateName -Passed $exists -Message "File $filePath exists" -Details "Path: $filePath"
        if (-not $exists) { $allPassed = $false }
    }
    return $allPassed
}

# Function to validate file content gate
function Test-FileContentGate {
    param([string]$FilePath, [string]$Pattern, [string]$GateName = "File Content")
    
    if (-not (Test-Path $FilePath)) {
        Write-ValidationResult -GateName $GateName -Passed $false -Message "File does not exist: $FilePath"
        return $false
    }
    
    $content = Get-Content $FilePath -Raw
    $matches = $content -match $Pattern
    Write-ValidationResult -GateName $GateName -Passed $matches -Message "Content matches pattern in $FilePath" -Details "Pattern: $Pattern"
    return $matches
}

# Function to validate directory structure gate
function Test-DirectoryStructureGate {
    param([hashtable]$Structure, [string]$BasePath = ".")
    
    $allPassed = $true
    foreach ($path in $Structure.Keys) {
        $expectedType = $Structure[$path]
        $fullPath = Join-Path $BasePath $path
        $exists = Test-Path $fullPath
        
        if ($expectedType -eq "directory") {
            $isCorrectType = $exists -and (Get-Item $fullPath) -is [System.IO.DirectoryInfo]
            $message = "Directory $fullPath exists"
        } elseif ($expectedType -eq "file") {
            $isCorrectType = $exists -and (Get-Item $fullPath) -is [System.IO.FileInfo]
            $message = "File $fullPath exists"
        } else {
            $isCorrectType = $exists
            $message = "Path $fullPath exists"
        }
        
        Write-ValidationResult -GateName "Directory Structure" -Passed $isCorrectType -Message $message -Details "Expected: $expectedType, Actual: $(if($exists){(Get-Item $fullPath).GetType().Name}else{'Not Found'})"
        if (-not $isCorrectType) { $allPassed = $false }
    }
    return $allPassed
}

# Function to validate configuration gate
function Test-ConfigurationGate {
    param([string]$ConfigPath)
    
    if (-not (Test-Path $ConfigPath)) {
        Write-ValidationResult -GateName "Configuration Validation" -Passed $false -Message "Config file not found: $ConfigPath"
        return $false
    }
    
    try {
        $config = Get-Content $ConfigPath | ConvertFrom-Json -ErrorAction Stop
        $hasRequiredProps = $config.PSObject.Properties.Name.Count -gt 0
        Write-ValidationResult -GateName "Configuration Validation" -Passed $hasRequiredProps -Message "Config file is valid JSON with properties" -Details "Properties: $($config.PSObject.Properties.Name -join ', ')"
        return $hasRequiredProps
    } catch {
        Write-ValidationResult -GateName "Configuration Validation" -Passed $false -Message "Config file is not valid JSON" -Details "Error: $($_.Exception.Message)"
        return $false
    }
}

# Function to validate documentation quality gate
function Test-DocumentationQualityGate {
    param([string]$DocPath, [int]$MinWordCount = 100, [string[]]$RequiredSections = @())
    
    if (-not (Test-Path $DocPath)) {
        Write-ValidationResult -GateName "Documentation Quality" -Passed $false -Message "Documentation file not found: $DocPath"
        return $false
    }
    
    $content = Get-Content $DocPath -Raw
    $wordCount = ($content -split '\s+' | Where-Object { $_.Trim() -ne '' }).Count
    $hasMinWords = $wordCount -ge $MinWordCount
    
    $missingSections = @()
    foreach ($section in $RequiredSections) {
        if ($content -notmatch [regex]::Escape($section)) {
            $missingSections += $section
        }
    }
    
    $hasAllSections = $missingSections.Count -eq 0
    $passed = $hasMinWords -and $hasAllSections
    
    $details = "Word count: $wordCount (min: $MinWordCount), Sections found: $(($RequiredSections | Where-Object { $content -match [regex]::Escape($_) }).Count)/$($RequiredSections.Count)"
    Write-ValidationResult -GateName "Documentation Quality" -Passed $passed -Message "Documentation meets quality standards" -Details $details
    
    if ($missingSections.Count -gt 0) {
        Write-ValidationResult -GateName "Documentation Quality" -Passed $false -Message "Missing required sections" -Details "Missing: $($missingSections -join ', ')"
    }
    
    return $passed
}

# Invoke AppDocU Python quality gates (run_docs.py validate)
function Invoke-AppDocValidate {
    param(
        [string]$RepoPath = ".",
        [double]$MinCoverage = 70,
        [double]$MaxFailure = 10,
        [bool]$RequireDiagrams = $true
    )

    Write-VerboseOutput "Invoking AppDocU quality gates via run_docs.py validate"
    $env:APPDOC_MIN_COVERAGE = [string]$MinCoverage
    $env:APPDOC_MAX_FAILURE = [string]$MaxFailure
    $env:APPDOC_REQUIRE_DIAGRAMS = if ($RequireDiagrams) { "1" } else { "0" }
    $python = "python"
    $args = @("run_docs.py", "validate", "--path", $RepoPath)
    try {
        $proc = Start-Process -FilePath $python -ArgumentList $args -Wait -PassThru -NoNewWindow -ErrorAction Stop
        $code = $proc.ExitCode
    } catch {
        Write-ValidationResult -GateName "AppDocU Quality Gates" -Passed $false -Message "Failed to execute run_docs.py validate" -Details $_.Exception.Message
        return $false
    }
    if ($code -eq 0) {
        Write-ValidationResult -GateName "AppDocU Quality Gates" -Passed $true -Message "Validation passed" -Details "coverage>=$MinCoverage, failure<=$MaxFailure, diagrams=$RequireDiagrams"
        return $true
    } elseif ($code -eq 2) {
        Write-ValidationResult -GateName "AppDocU Quality Gates" -Passed $false -Message "Validation failed (thresholds not met)" -Details "coverage>=$MinCoverage, failure<=$MaxFailure, diagrams=$RequireDiagrams"
        return $false
    } else {
        Write-ValidationResult -GateName "AppDocU Quality Gates" -Passed $false -Message "Validation error (exit code $code)" -Details "Check _normalized/.meta/validation_report.md"
        return $false
    }
}

# Main validation workflow
function Start-GateValidation {
    Write-Host "Starting Gate Validation Process..." -ForegroundColor Yellow
    Write-Host "Configuration: $ConfigPath" -ForegroundColor Gray
    Write-Host "Output Log: $OutputPath" -ForegroundColor Gray
    Write-Host "Verbose: $Verbose, FailFast: $FailFast" -ForegroundColor Gray
    Write-Host ""

    # Initialize output file
    $header = "# Gate Validation Report`nGenerated: $(Get-Date)`nConfiguration: $ConfigPath`n"
    $header | Out-File -FilePath $OutputPath -Encoding UTF8

    $overallPassed = $true

    # Gate 1: Configuration Validation
    Write-Host "Gate 1: Configuration Validation" -ForegroundColor Magenta
    $configPassed = Test-ConfigurationGate -ConfigPath $ConfigPath
    $overallPassed = $overallPassed -and $configPassed

    # Gate 2: Required Files Existence
    Write-Host "`nGate 2: Required Files Existence" -ForegroundColor Magenta
    $requiredFiles = @(
        "README.md",
        "appdoc.py",
        "IMPLEMENTATION_PLAN.md",
        "appdocu_preprocessor/__init__.py"
    )
    $filesPassed = Test-FileExistenceGate -FilePaths $requiredFiles -GateName "Required Files"
    $overallPassed = $overallPassed -and $filesPassed

    # Gate 3: Documentation Quality
    Write-Host "`nGate 3: Documentation Quality" -ForegroundColor Magenta
    if (Test-Path "README.md") {
        $docPassed = Test-DocumentationQualityGate -DocPath "README.md" -MinWordCount 50 -RequiredSections @("##", "# ", "Usage", "Installation")
        $overallPassed = $overallPassed -and $docPassed
    } else {
        Write-ValidationResult -GateName "Documentation Quality" -Passed $false -Message "README.md not found"
        $overallPassed = $false
    }

    # Gate 4: Code Quality Gates
    Write-Host "`nGate 4: Code Quality Gates" -ForegroundColor Magenta
    if (Test-Path "appdoc.py") {
        $pythonQualityPassed = Test-FileContentGate -FilePath "appdoc.py" -Pattern "def\s+\w+\s*\(" -GateName "Python Functions"
        $overallPassed = $overallPassed -and $pythonQualityPassed
    }

    # Gate 5: Directory Structure Validation
    Write-Host "`nGate 5: Directory Structure Validation" -ForegroundColor Magenta
    $expectedStructure = @{
        "appdocu_preprocessor" = "directory"
        "docs" = "directory"
        "patterns" = "directory"
        "appdoc.py" = "file"
        "README.md" = "file"
    }
    $structurePassed = Test-DirectoryStructureGate -Structure $expectedStructure
    $overallPassed = $overallPassed -and $structurePassed

    # Gate 6: Template Validation
    Write-Host "`nGate 6: Template Validation" -ForegroundColor Magenta
    $templateFiles = Get-ChildItem -Path "appdoc.templates" -Filter "*.template.md" -ErrorAction SilentlyContinue
    if ($templateFiles) {
        foreach ($template in $templateFiles) {
            $templatePassed = Test-FileContentGate -FilePath $template.FullName -Pattern "{{\s*\w+\s*}}" -GateName "Template Placeholders"
            $overallPassed = $overallPassed -and $templatePassed
        }
    } else {
        Write-ValidationResult -GateName "Template Validation" -Passed $false -Message "No template files found in appdoc.templates"
        $overallPassed = $false
    }

    # Gate 7: AppDocU Quality Gates (Python)
    Write-Host "`nGate 7: AppDocU Quality Gates" -ForegroundColor Magenta
    $appdocPassed = Invoke-AppDocValidate -RepoPath "." -MinCoverage $MinCoverage -MaxFailure $MaxFailure -RequireDiagrams $RequireDiagrams
    $overallPassed = $overallPassed -and $appdocPassed

    # Final Summary
    Write-Host "`n" * 2 -NoNewline
    Write-Host "=" * 60 -ForegroundColor White
    if ($overallPassed) {
        Write-Host "ALL GATES PASSED - Validation Successful!" -ForegroundColor Green
        Write-Host "=" * 60 -ForegroundColor White
        Add-Content -Path $OutputPath -Value "`nOVERALL RESULT: SUCCESS - All gates passed"
    } else {
        Write-Host "VALIDATION FAILED - Some gates did not pass" -ForegroundColor Red
        Write-Host "=" * 60 -ForegroundColor White
        Add-Content -Path $OutputPath -Value "`nOVERALL RESULT: FAILED - Some gates did not pass"
        exit 1
    }

    return $overallPassed
}

# Execute validation if script is run directly
if ($MyInvocation.InvocationName -ne '.') {
    try {
        Start-GateValidation
    } catch {
        Write-Error "Gate validation failed with error: $($_.Exception.Message)"
        exit 1
    }
}
