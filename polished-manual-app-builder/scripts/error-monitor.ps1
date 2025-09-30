# Polished Manual App Builder - Error Monitor PowerShell Wrapper
# Easy-to-use interface for the Python error monitoring system

param(
    [string]$Action = "monitor",
    [string]$Config = "error_monitor_config.json",
    [switch]$Verbose = $false,
    [switch]$Help = $false
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"
$Magenta = "Magenta"

function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor $Green }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor $Blue }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor $Yellow }
function Write-Failure { param($msg) Write-Host "❌ $msg" -ForegroundColor $Red }
function Write-Header { param($msg) Write-Host "`n🔍 $msg" -ForegroundColor $Magenta }

function Test-PythonDependencies {
    Write-Info "Checking Python dependencies for error monitor..."
    
    $requiredPackages = @(
        "aiohttp",
        "psutil", 
        "docker"
    )
    
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        try {
            $importCmd = "import $package; print('$package" + ": OK')"
            $result = python -c $importCmd 2>$null
            if ($LASTEXITCODE -eq 0) {
                if ($Verbose) { Write-Success $result }
            } else {
                throw "Import failed"
            }
        }
        catch {
            $missingPackages += $package
            Write-Warning "$package is not installed"
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Info "Installing missing packages..."
        pip install $missingPackages
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "All dependencies installed successfully"
        } else {
            Write-Failure "Failed to install some dependencies"
            return $false
        }
    }
    
    return $true
}

function Start-ErrorMonitor {
    Write-Header "Starting Continuous Error Monitoring"
    
    if (-not (Test-PythonDependencies)) {
        Write-Failure "Cannot start error monitor due to missing dependencies"
        return
    }
    
    Write-Info "Starting error monitor with config: $Config"
    Write-Info "Press Ctrl+C to stop monitoring"
    Write-Host ""
    
    try {
        python scripts\error_monitor.py --config $Config
    }
    catch {
        Write-Failure "Error monitor failed: $_"
    }
}

function Get-QuickHealthCheck {
    Write-Header "Quick Health Check"
    
    if (-not (Test-PythonDependencies)) {
        Write-Warning "Using basic health check (Python dependencies missing)"
        Test-BasicHealth
        return
    }
    
    Write-Info "Running comprehensive health check..."
    
    try {
        $result = python scripts\error_monitor.py --config $Config --once
        Write-Host $result
    }
    catch {
        Write-Failure "Health check failed: $_"
        Test-BasicHealth
    }
}

function Get-HealthReport {
    Write-Header "Generating Comprehensive Health Report"
    
    if (-not (Test-PythonDependencies)) {
        Write-Failure "Cannot generate detailed health report without Python dependencies"
        return
    }
    
    try {
        $report = python scripts\error_monitor.py --config $Config --report | ConvertFrom-Json
        
        Write-Host ""
        Write-Host "📊 SYSTEM HEALTH REPORT" -ForegroundColor $Magenta
        Write-Host "Generated: $($report.timestamp)" -ForegroundColor $Blue
        Write-Host ""
        
        # Overall status
        $statusColor = switch ($report.overall_status) {
            "healthy" { $Green }
            "degraded" { $Yellow }
            "critical" { $Red }
            default { $Blue }
        }
        Write-Host "Overall Status: $($report.overall_status.ToUpper())" -ForegroundColor $statusColor
        Write-Host ""
        
        # Service health
        Write-Host "🔧 SERVICE HEALTH:" -ForegroundColor $Blue
        foreach ($service in $report.services.PSObject.Properties) {
            $name = $service.Name
            $health = $service.Value
            
            $serviceColor = switch ($health.status) {
                "healthy" { $Green }
                "degraded" { $Yellow }
                "down" { $Red }
                default { $Blue }
            }
            
            $responseTime = if ($health.response_time) { " ($([math]::Round($health.response_time * 1000, 2))ms)" } else { "" }
            Write-Host "  $name`: $($health.status)$responseTime" -ForegroundColor $serviceColor
            
            if ($health.error_message) {
                Write-Host "    Error: $($health.error_message)" -ForegroundColor $Red
            }
        }
        
        Write-Host ""
        
        # System resources
        Write-Host "💻 SYSTEM RESOURCES:" -ForegroundColor $Blue
        $resources = $report.system_resources
        Write-Host "  Memory: $([math]::Round($resources.memory_percent, 1))% used ($(([math]::Round($resources.memory_available_gb, 2))) GB available)" -ForegroundColor $(if ($resources.memory_percent -gt 80) { $Red } elseif ($resources.memory_percent -gt 60) { $Yellow } else { $Green })
        Write-Host "  CPU: $([math]::Round($resources.cpu_percent, 1))% used" -ForegroundColor $(if ($resources.cpu_percent -gt 80) { $Red } elseif ($resources.cpu_percent -gt 60) { $Yellow } else { $Green })
        Write-Host "  Disk: $([math]::Round($resources.disk_percent, 1))% used ($(([math]::Round($resources.disk_free_gb, 2))) GB free)" -ForegroundColor $(if ($resources.disk_percent -gt 90) { $Red } elseif ($resources.disk_percent -gt 75) { $Yellow } else { $Green })
        
        Write-Host ""
        
        # Recent errors
        if ($report.recent_errors -and $report.recent_errors.Count -gt 0) {
            Write-Host "⚠️  RECENT ERRORS (Last 24 hours):" -ForegroundColor $Yellow
            foreach ($errorItem in $report.recent_errors) {
                $errorColor = switch ($errorItem.severity) {
                    "critical" { $Red }
                    "high" { $Yellow }
                    default { $Blue }
                }
                Write-Host "  [$($errorItem.severity.ToUpper())] $($errorItem.service): $($errorItem.message)" -ForegroundColor $errorColor
            }
            Write-Host ""
        }
        
        # Recommendations
        if ($report.recommendations -and $report.recommendations.Count -gt 0) {
            Write-Host "💡 RECOMMENDATIONS:" -ForegroundColor $Blue
            foreach ($rec in $report.recommendations) {
                Write-Host "  • $rec" -ForegroundColor $Yellow
            }
            Write-Host ""
        }
        
        Write-Success "Health report generated successfully"
        Write-Info "Detailed report saved to: health_report.json"
        
    }
    catch {
        Write-Failure "Failed to generate health report: $_"
    }
}

function Test-BasicHealth {
    Write-Info "Running basic health checks..."
    
    $services = @(
        @{ Name = "Event Store"; Url = "http://localhost:8080/health" },
        @{ Name = "AI Orchestrator"; Url = "http://localhost:8001/health" },
        @{ Name = "Collaboration Engine"; Url = "http://localhost:8003/health" }
    )
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.Url -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "$($service.Name) is healthy"
            } else {
                Write-Warning "$($service.Name) returned status $($response.StatusCode)"
            }
        }
        catch {
            Write-Failure "$($service.Name) is not responding"
        }
    }
    
    # Check Docker containers
    try {
        $containers = docker ps --filter "name=polished-manual-app-builder" --format "table {{.Names}}\t{{.Status}}"
        if ($containers) {
            Write-Info "Docker container status:"
            Write-Host $containers -ForegroundColor $Blue
        } else {
            Write-Warning "No polished-manual-app-builder containers found"
        }
    }
    catch {
        Write-Warning "Could not check Docker container status"
    }
}

function Show-ErrorLog {
    Write-Header "Recent Error Log"
    
    $logFile = "error_log.json"
    if (Test-Path $logFile) {
        try {
            $errors = Get-Content $logFile | ConvertFrom-Json
            
            if ($errors.Count -eq 0) {
                Write-Success "No errors found in log"
                return
            }
            
            Write-Info "Showing last 10 errors:"
            Write-Host ""
            
            $recentErrors = $errors | Sort-Object timestamp -Descending | Select-Object -First 10
            
            foreach ($errorItem in $recentErrors) {
                $errorColor = switch ($errorItem.severity) {
                    "critical" { $Red }
                    "high" { $Yellow }
                    "medium" { $Blue }
                    default { $Green }
                }
                
                Write-Host "[$($errorItem.severity.ToUpper())] $($errorItem.timestamp)" -ForegroundColor $errorColor
                Write-Host "Service: $($errorItem.service)" -ForegroundColor $Blue
                Write-Host "Type: $($errorItem.error_type)" -ForegroundColor $Blue
                Write-Host "Message: $($errorItem.message)" -ForegroundColor $White
                
                if ($errorItem.resolution_steps) {
                    Write-Host "Resolution:" -ForegroundColor $Green
                    foreach ($step in $errorItem.resolution_steps) {
                        Write-Host "  • $step" -ForegroundColor $Green
                    }
                }
                
                Write-Host ""
            }
            
        }
        catch {
            Write-Failure "Failed to read error log: $_"
        }
    } else {
        Write-Info "No error log file found. Run monitoring first to generate logs."
    }
}

function Install-ErrorMonitor {
    Write-Header "Installing Error Monitor Dependencies"
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
        } else {
            throw "Python check failed"
        }
    }
    catch {
        Write-Failure "Python is not installed or not in PATH"
        Write-Info "Please install Python 3.9+ from https://python.org"
        return $false
    }
    
    # Install Python packages
    Write-Info "Installing required Python packages..."
    $packages = @("aiohttp", "psutil", "docker")
    
    foreach ($package in $packages) {
        Write-Info "Installing $package..."
        pip install $package
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "$package installed successfully"
        } else {
            Write-Failure "Failed to install $package"
            return $false
        }
    }
    
    Write-Success "Error monitor dependencies installed successfully"
    return $true
}

function Show-Help {
    Write-Host @"
Polished Manual App Builder - Error Monitor

USAGE:
    .\error-monitor.ps1 [ACTION] [-Config <path>] [-Verbose] [-Help]

ACTIONS:
    monitor      Start continuous error monitoring (default)
    check        Run quick health check once
    report       Generate comprehensive health report
    log          Show recent error log entries
    install      Install error monitor dependencies
    help         Show this help message

OPTIONS:
    -Config <path>   Path to configuration file (default: error_monitor_config.json)
    -Verbose         Show detailed output
    -Help           Show this help message

EXAMPLES:
    .\error-monitor.ps1                    # Start continuous monitoring
    .\error-monitor.ps1 check              # Quick health check
    .\error-monitor.ps1 report             # Detailed health report
    .\error-monitor.ps1 log                # View recent errors
    .\error-monitor.ps1 install            # Install dependencies

MONITORING FEATURES:
    ✅ Service health checks (HTTP endpoints + containers)
    ✅ System resource monitoring (CPU, memory, disk)
    ✅ Docker container status and resource usage
    ✅ Automated error detection and logging
    ✅ Performance threshold monitoring
    ✅ Comprehensive health reporting

ERROR DETECTION:
    • Service downtime and degradation
    • High resource usage (CPU, memory, disk)
    • Container failures and restarts
    • Database connection issues
    • Performance threshold violations

REQUIREMENTS:
    • Python 3.9+ with aiohttp, psutil, docker packages
    • Docker Desktop running
    • Services running (use .\complete-demo.ps1 to start)

ACCESS LOGS:
    • Error log: error_log.json
    • Health reports: health_report.json
    • Monitor log: error_monitor.log

"@
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

# Ensure we're in the right directory
if (-not (Test-Path "scripts")) {
    Write-Warning "Not in project root directory. Changing to parent directory..."
    Set-Location ..
    
    if (-not (Test-Path "scripts")) {
        Write-Failure "Cannot find scripts directory. Please run from project root."
        exit 1
    }
}

switch ($Action.ToLower()) {
    "monitor" {
        Start-ErrorMonitor
    }
    "check" {
        Get-QuickHealthCheck
    }
    "report" {
        Get-HealthReport
    }
    "log" {
        Show-ErrorLog
    }
    "install" {
        Install-ErrorMonitor
    }
    "help" {
        Show-Help
    }
    default {
        Write-Failure "Unknown action: $Action"
        Show-Help
        exit 1
    }
}
