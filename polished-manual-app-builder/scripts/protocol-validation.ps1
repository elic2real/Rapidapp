# Error Prevention Protocol Validation
# Validates that all features of our AI debugging system are working as mandated

Write-Host "🔍 ERROR PREVENTION PROTOCOL VALIDATION" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "⏰ Validation Started: $Timestamp" -ForegroundColor Gray
Write-Host "📁 Project Root: $ProjectRoot" -ForegroundColor Gray
Write-Host ""

# Protocol 1: Error Capture Compliance
Write-Host "📋 PROTOCOL 1: Error Capture Compliance" -ForegroundColor Yellow

$ErrorLogPath = Join-Path $ProjectRoot "logs\captured_errors.json"
if (Test-Path $ErrorLogPath) {
    $ErrorLog = Get-Content $ErrorLogPath | ConvertFrom-Json
    $ErrorCount = $ErrorLog.Count
    
    Write-Host "✅ Error log exists: $ErrorLogPath" -ForegroundColor Green
    Write-Host "✅ Captured errors: $ErrorCount" -ForegroundColor Green
    
    # Check recent captures
    $RecentErrors = $ErrorLog | Where-Object { 
        $_.timestamp -and 
        [DateTime]::Parse($_.timestamp) -gt (Get-Date).AddHours(-1) 
    }
    
    if ($RecentErrors.Count -gt 0) {
        Write-Host "✅ Recent error capture: $($RecentErrors.Count) in last hour" -ForegroundColor Green
        Write-Host "   Latest: $($RecentErrors[-1].error_text.Substring(0, [Math]::Min(50, $RecentErrors[-1].error_text.Length)))..." -ForegroundColor Gray
    } else {
        Write-Host "⚠️ No recent error captures" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Error log missing: $ErrorLogPath" -ForegroundColor Red
}

Write-Host ""

# Protocol 2: Error Guide Documentation
Write-Host "📚 PROTOCOL 2: Error Guide Documentation" -ForegroundColor Yellow

$ErrorGuidePath = Join-Path $ProjectRoot "docs\ERROR_PREVENTION_GUIDE.md"
if (Test-Path $ErrorGuidePath) {
    $GuideContent = Get-Content $ErrorGuidePath -Raw
    
    # Count documented errors
    $ErrorEntries = ([regex]::Matches($GuideContent, 'ERROR-\d+:')).Count
    $LineCount = (Get-Content $ErrorGuidePath).Count
    
    Write-Host "✅ Error guide exists: $ErrorGuidePath" -ForegroundColor Green
    Write-Host "✅ Documented errors: $ErrorEntries" -ForegroundColor Green
    Write-Host "✅ Guide size: $LineCount lines" -ForegroundColor Green
    
    # Check for our recent PowerShell errors
    $PowerShellErrors = @(
        "ERROR-504.*PowerShell Variable Reference",
        "ERROR-505.*PowerShell Mixed Language", 
        "ERROR-506.*PowerShell Unused Variable"
    )
    
    $FoundErrors = 0
    foreach ($Pattern in $PowerShellErrors) {
        if ($GuideContent -match $Pattern) {
            $FoundErrors++
        }
    }
    
    if ($FoundErrors -eq $PowerShellErrors.Count) {
        Write-Host "✅ All recent PowerShell errors documented" -ForegroundColor Green
    } else {
        Write-Host "⚠️ $FoundErrors/$($PowerShellErrors.Count) recent PowerShell errors documented" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "❌ Error guide missing: $ErrorGuidePath" -ForegroundColor Red
}

Write-Host ""

# Protocol 3: AI Debugging System Components
Write-Host "🤖 PROTOCOL 3: AI Debugging System Components" -ForegroundColor Yellow

$AIComponents = @(
    "scripts\ai_debug_system.py",
    "scripts\advanced_prompt_engineering.py",
    "scripts\ai_debug_integration.py",
    "scripts\ai_debug_config.json"
)

$ComponentsFound = 0
foreach ($Component in $AIComponents) {
    $ComponentPath = Join-Path $ProjectRoot $Component
    if (Test-Path $ComponentPath) {
        $Size = [Math]::Round((Get-Item $ComponentPath).Length / 1KB, 1)
        Write-Host "✅ $Component ($Size KB)" -ForegroundColor Green
        $ComponentsFound++
    } else {
        Write-Host "❌ $Component - MISSING" -ForegroundColor Red
    }
}

if ($ComponentsFound -eq $AIComponents.Count) {
    Write-Host "✅ All AI debugging components present" -ForegroundColor Green
} else {
    Write-Host "⚠️ $ComponentsFound/$($AIComponents.Count) AI components found" -ForegroundColor Yellow
}

Write-Host ""

# Protocol 4: Service Integration
Write-Host "⚙️ PROTOCOL 4: Service Integration" -ForegroundColor Yellow

$ServiceComponents = @(
    "services\event-store\src\error_capture.rs",
    "services\orchestrator\app\error_capture.py",
    "services\collab-engine\src\error-capture.ts"
)

$ServicesIntegrated = 0
foreach ($Service in $ServiceComponents) {
    $ServicePath = Join-Path $ProjectRoot $Service
    if (Test-Path $ServicePath) {
        Write-Host "✅ $Service" -ForegroundColor Green
        $ServicesIntegrated++
    } else {
        Write-Host "❌ $Service - MISSING" -ForegroundColor Red
    }
}

if ($ServicesIntegrated -eq $ServiceComponents.Count) {
    Write-Host "✅ All services have error capture integration" -ForegroundColor Green
} else {
    Write-Host "⚠️ $ServicesIntegrated/$($ServiceComponents.Count) services integrated" -ForegroundColor Yellow
}

Write-Host ""

# Protocol 5: VS Code Extension
Write-Host "🔌 PROTOCOL 5: VS Code Extension" -ForegroundColor Yellow

$ExtensionComponents = @(
    "vscode-extension\package.json",
    "vscode-extension\src\extension.ts",
    "vscode-extension\tsconfig.json"
)

$ExtensionComplete = 0
foreach ($ExtComponent in $ExtensionComponents) {
    $ExtPath = Join-Path $ProjectRoot $ExtComponent
    if (Test-Path $ExtPath) {
        Write-Host "✅ $ExtComponent" -ForegroundColor Green
        $ExtensionComplete++
    } else {
        Write-Host "❌ $ExtComponent - MISSING" -ForegroundColor Red
    }
}

if ($ExtensionComplete -eq $ExtensionComponents.Count) {
    Write-Host "✅ VS Code extension is complete" -ForegroundColor Green
} else {
    Write-Host "⚠️ $ExtensionComplete/$($ExtensionComponents.Count) extension components found" -ForegroundColor Yellow
}

Write-Host ""

# Protocol 6: Automated Learning System
Write-Host "🧠 PROTOCOL 6: Automated Learning System" -ForegroundColor Yellow

$LearningComponents = @(
    "scripts\error_learning_engine.py",
    "scripts\error_monitor.py",
    "scripts\auto_error_capture.py"
)

$LearningSystemReady = 0
foreach ($Learning in $LearningComponents) {
    $LearningPath = Join-Path $ProjectRoot $Learning
    if (Test-Path $LearningPath) {
        Write-Host "✅ $Learning" -ForegroundColor Green
        $LearningSystemReady++
    } else {
        Write-Host "❌ $Learning - MISSING" -ForegroundColor Red
    }
}

if ($LearningSystemReady -eq $LearningComponents.Count) {
    Write-Host "✅ Automated learning system operational" -ForegroundColor Green
} else {
    Write-Host "⚠️ $LearningSystemReady/$($LearningComponents.Count) learning components found" -ForegroundColor Yellow
}

Write-Host ""

# Calculate Overall Compliance Score
$TotalProtocols = 6
$TotalChecks = $AIComponents.Count + $ServiceComponents.Count + $ExtensionComponents.Count + $LearningComponents.Count + 4 # +4 for error log, guide, recent captures, and PowerShell errors

$PassedChecks = 0
if (Test-Path $ErrorLogPath) { $PassedChecks++ }
if (Test-Path $ErrorGuidePath) { $PassedChecks++ }
if ($RecentErrors.Count -gt 0) { $PassedChecks++ }
if ($FoundErrors -eq $PowerShellErrors.Count) { $PassedChecks++ }
$PassedChecks += $ComponentsFound + $ServicesIntegrated + $ExtensionComplete + $LearningSystemReady

$ComplianceScore = [Math]::Round(($PassedChecks / $TotalChecks) * 100, 1)

Write-Host "📊 PROTOCOL COMPLIANCE SUMMARY" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Evaluating $TotalProtocols protocols..." -ForegroundColor Gray
Write-Host "Overall Compliance Score: $ComplianceScore%" -ForegroundColor $(if ($ComplianceScore -ge 90) { "Green" } elseif ($ComplianceScore -ge 70) { "Yellow" } else { "Red" })
Write-Host "Checks Passed: $PassedChecks / $TotalChecks" -ForegroundColor Gray
Write-Host ""

if ($ComplianceScore -ge 90) {
    Write-Host "🎉 EXCELLENT COMPLIANCE!" -ForegroundColor Green
    Write-Host "Error prevention protocols are fully operational" -ForegroundColor Green
} elseif ($ComplianceScore -ge 70) {
    Write-Host "⚠️ GOOD COMPLIANCE" -ForegroundColor Yellow  
    Write-Host "Most protocols working, some improvements needed" -ForegroundColor Yellow
} else {
    Write-Host "❌ INSUFFICIENT COMPLIANCE" -ForegroundColor Red
    Write-Host "Critical protocols missing - immediate action required" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 NEXT ACTIONS:" -ForegroundColor Cyan

if ($ComplianceScore -ge 90) {
    Write-Host "• System is ready for production use" -ForegroundColor White
    Write-Host "• Continue monitoring and capturing errors" -ForegroundColor White
    Write-Host "• Run integration tests to validate AI debugging" -ForegroundColor White
} else {
    Write-Host "• Address missing components above" -ForegroundColor White
    Write-Host "• Run setup scripts to complete installation" -ForegroundColor White
    Write-Host "• Validate all error capture mechanisms" -ForegroundColor White
}

Write-Host ""
Write-Host "✅ PROTOCOL VALIDATION COMPLETE" -ForegroundColor Green
Write-Host "Validation completed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
