# Error Prevention & Learning System Deployment Script

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("install", "start", "stop", "status", "update", "reset")]
    [string]$Action = "status",
    
    [Parameter(Mandatory=$false)]
    [switch]$StartLearning = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$StartServer = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Enable verbose output if requested
if ($Verbose) {
    $VerbosePreference = "Continue"
}

Write-Host "🧠 Polished Manual App Builder - Error Prevention & Learning System" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

function Test-PythonPackages {
    Write-Host "🔍 Checking Python dependencies..." -ForegroundColor Yellow
    
    $requiredPackages = @(
        "aiohttp",
        "aiofiles", 
        "psutil",
        "docker",
        "structlog"
    )
    
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        try {
            $result = python -c "import $package" 2>&1
            if ($LASTEXITCODE -ne 0) {
                $missingPackages += $package
            }
        }
        catch {
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host "❌ Missing packages: $($missingPackages -join ', ')" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ All Python dependencies are installed" -ForegroundColor Green
    return $true
}

function Install-Dependencies {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    
    $packages = @(
        "aiohttp>=3.8.0",
        "aiofiles>=0.8.0",
        "psutil>=5.9.0", 
        "docker>=6.0.0",
        "structlog>=22.0.0"
    )
    
    foreach ($package in $packages) {
        Write-Host "Installing $package..." -ForegroundColor Gray
        python -m pip install $package
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install $package" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "✅ All dependencies installed successfully" -ForegroundColor Green
}

function Start-ErrorLearningSystem {
    Write-Host "🚀 Starting Error Learning System..." -ForegroundColor Yellow
    
    # Start the error monitor server
    if ($StartServer) {
        Write-Host "Starting error monitor server..." -ForegroundColor Gray
        Start-Process python -ArgumentList "scripts\error_monitor_server.py" -WindowStyle Hidden
        Start-Sleep 2
        
        # Test if server is running
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8090/health" -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Error monitor server started successfully" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "❌ Failed to start error monitor server" -ForegroundColor Red
        }
    }
    
    # Start learning engine if requested
    if ($StartLearning) {
        Write-Host "Starting error learning engine..." -ForegroundColor Gray
        python scripts\error_learning_engine.py
        Write-Host "✅ Learning cycle completed" -ForegroundColor Green
    }
}

function Stop-ErrorLearningSystem {
    Write-Host "🛑 Stopping Error Learning System..." -ForegroundColor Yellow
    
    # Stop Python processes
    Get-Process | Where-Object { $_.Name -eq "python" -and $_.CommandLine -like "*error_monitor_server*" } | Stop-Process -Force
    Get-Process | Where-Object { $_.Name -eq "python" -and $_.CommandLine -like "*error_learning_engine*" } | Stop-Process -Force
    
    Write-Host "✅ Error learning system stopped" -ForegroundColor Green
}

function Get-SystemStatus {
    Write-Host "📊 Error Learning System Status" -ForegroundColor Yellow
    Write-Host "===============================" -ForegroundColor Yellow
    
    # Check if error monitor server is running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8090/health" -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Error Monitor Server: Running" -ForegroundColor Green
            
            # Get server statistics
            try {
                $statsResponse = Invoke-WebRequest -Uri "http://localhost:8090/stats" -TimeoutSec 2
                $stats = $statsResponse.Content | ConvertFrom-Json
                
                Write-Host "   📈 Total errors received: $($stats.total_errors_received)" -ForegroundColor Cyan
                Write-Host "   🏃 Learning runs: $($stats.learning_runs)" -ForegroundColor Cyan
                
                if ($stats.errors_by_service) {
                    Write-Host "   📋 Errors by service:" -ForegroundColor Cyan
                    foreach ($service in $stats.errors_by_service.PSObject.Properties) {
                        Write-Host "      - $($service.Name): $($service.Value)" -ForegroundColor Gray
                    }
                }
            }
            catch {
                Write-Host "   ⚠️  Could not retrieve detailed statistics" -ForegroundColor Yellow
            }
        }
    }
    catch {
        Write-Host "❌ Error Monitor Server: Not Running" -ForegroundColor Red
    }
    
    # Check error logs
    $logsDir = "logs\errors"
    if (Test-Path $logsDir) {
        $errorFiles = Get-ChildItem "$logsDir\*.jsonl" | Measure-Object
        Write-Host "📁 Error log files: $($errorFiles.Count)" -ForegroundColor Cyan
        
        # Check recent activity
        $recentErrors = Get-ChildItem "$logsDir\*.jsonl" | ForEach-Object {
            if ($_.LastWriteTime -gt (Get-Date).AddHours(-1)) {
                $_
            }
        }
        
        if ($recentErrors) {
            Write-Host "⚡ Recent activity: $($recentErrors.Count) files updated in last hour" -ForegroundColor Green
        } else {
            Write-Host "😴 No recent error activity" -ForegroundColor Gray
        }
    } else {
        Write-Host "📁 Error logs: Not found" -ForegroundColor Gray
    }
    
    # Check error guide
    $errorGuide = "docs\ERROR_PREVENTION_GUIDE.md"
    if (Test-Path $errorGuide) {
        $guideInfo = Get-Item $errorGuide
        Write-Host "📖 Error Prevention Guide: Last updated $($guideInfo.LastWriteTime)" -ForegroundColor Cyan
        
        # Count error entries in guide
        $content = Get-Content $errorGuide -Raw
        $errorMatches = [regex]::Matches($content, "ERROR-\d+")
        Write-Host "   📝 Documented errors: $($errorMatches.Count)" -ForegroundColor Cyan
    } else {
        Write-Host "📖 Error Prevention Guide: Not found" -ForegroundColor Red
    }
    
    # Check knowledge base
    $knowledgeBase = "logs\errors\error_knowledge_base.json"
    if (Test-Path $knowledgeBase) {
        try {
            $kb = Get-Content $knowledgeBase | ConvertFrom-Json
            $patternCount = ($kb.PSObject.Properties | Measure-Object).Count
            Write-Host "🧠 Knowledge Base: $patternCount error patterns learned" -ForegroundColor Cyan
        }
        catch {
            Write-Host "🧠 Knowledge Base: Found but could not parse" -ForegroundColor Yellow
        }
    } else {
        Write-Host "🧠 Knowledge Base: Empty (no patterns learned yet)" -ForegroundColor Gray
    }
}

function Update-ErrorSystem {
    Write-Host "🔄 Updating Error Learning System..." -ForegroundColor Yellow
    
    # Run learning engine to process any pending errors
    python scripts\error_learning_engine.py
    
    Write-Host "✅ Update completed" -ForegroundColor Green
}

function Reset-ErrorSystem {
    Write-Host "🔄 Resetting Error Learning System..." -ForegroundColor Yellow
    
    $confirm = Read-Host "This will clear all error logs and learning data. Continue? (y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        # Clear error logs
        if (Test-Path "logs\errors") {
            Remove-Item "logs\errors\*" -Recurse -Force
            Write-Host "✅ Error logs cleared" -ForegroundColor Green
        }
        
        # Reset server stats if running
        try {
            Invoke-WebRequest -Uri "http://localhost:8090/reset-stats" -Method POST -TimeoutSec 2
            Write-Host "✅ Server statistics reset" -ForegroundColor Green
        }
        catch {
            Write-Host "ℹ️  Server not running, stats will reset on next start" -ForegroundColor Gray
        }
        
        Write-Host "✅ System reset completed" -ForegroundColor Green
    } else {
        Write-Host "❌ Reset cancelled" -ForegroundColor Yellow
    }
}

function Show-Help {
    Write-Host @"
🧠 Error Prevention & Learning System

USAGE:
    .\error-learning-system.ps1 [ACTION] [OPTIONS]

ACTIONS:
    install     Install Python dependencies
    start       Start the error learning system
    stop        Stop the error learning system  
    status      Show system status (default)
    update      Run learning engine to process pending errors
    reset       Clear all error data and logs

OPTIONS:
    -StartLearning    Start learning engine with start action
    -StartServer      Start error monitor server with start action
    -Verbose          Enable verbose output

EXAMPLES:
    .\error-learning-system.ps1 install
    .\error-learning-system.ps1 start -StartServer -StartLearning
    .\error-learning-system.ps1 status
    .\error-learning-system.ps1 update

ENDPOINTS (when server is running):
    http://localhost:8090/health      - Health check
    http://localhost:8090/stats       - Error statistics
    http://localhost:8090/analytics   - Learning analytics
"@
}

# Main execution logic
switch ($Action.ToLower()) {
    "install" {
        if (-not (Test-PythonPackages)) {
            Install-Dependencies
        } else {
            Write-Host "✅ All dependencies already installed" -ForegroundColor Green
        }
    }
    "start" {
        if (-not (Test-PythonPackages)) {
            Write-Host "❌ Missing dependencies. Run with 'install' first." -ForegroundColor Red
            exit 1
        }
        Start-ErrorLearningSystem
    }
    "stop" {
        Stop-ErrorLearningSystem
    }
    "status" {
        Get-SystemStatus
    }
    "update" {
        if (-not (Test-PythonPackages)) {
            Write-Host "❌ Missing dependencies. Run with 'install' first." -ForegroundColor Red
            exit 1
        }
        Update-ErrorSystem
    }
    "reset" {
        Reset-ErrorSystem
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
        Show-Help
        exit 1
    }
}

Write-Host "`n🎉 Done!" -ForegroundColor Green
