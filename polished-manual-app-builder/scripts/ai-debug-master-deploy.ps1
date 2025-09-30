# 🚀 AI Debug Master Deployment Script
# Next-Generation AI-Powered Debugging System
# Comprehensive setup and deployment automation

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("setup", "deploy", "test", "monitor", "update", "all")]
    [string]$Action = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipDependencies,
    
    [Parameter(Mandatory=$false)]
    [switch]$LocalOnly,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

# Set execution policy and error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Global configuration
$Script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$Script:LogFile = Join-Path $ProjectRoot "logs\deployment_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$Script:ConfigFile = Join-Path $ProjectRoot "scripts\ai_debug_config.json"

# Ensure log directory exists
$LogDir = Split-Path -Parent $Script:LogFile
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Logging function
function Write-Log {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    
    # Console output with colors
    switch ($Level) {
        "INFO"    { Write-Host $LogEntry -ForegroundColor White }
        "WARN"    { Write-Host $LogEntry -ForegroundColor Yellow }
        "ERROR"   { Write-Host $LogEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $LogEntry -ForegroundColor Green }
    }
    
    # File output
    Add-Content -Path $Script:LogFile -Value $LogEntry
}

# Banner
function Show-Banner {
    Write-Host @"
████████████████████████████████████████████████████████████
█                                                          █
█    🤖 AI DEBUG MASTER DEPLOYMENT SYSTEM v3.0             █
█                                                          █
█    Next-Generation AI-Powered Debugging Platform        █
█    ✨ Tree of Thoughts ✨ ReAct ✨ Intelligent Routing  █
█                                                          █
████████████████████████████████████████████████████████████
"@ -ForegroundColor Cyan
    Write-Host ""
}

# Check prerequisites
function Test-Prerequisites {
    Write-Log "Checking system prerequisites..." "INFO"
    
    $Prerequisites = @{
        "Python 3.8+" = { python --version 2>$null }
        "Node.js 16+" = { node --version 2>$null }
        "Rust/Cargo" = { cargo --version 2>$null }
        "Docker" = { docker --version 2>$null }
        "Git" = { git --version 2>$null }
    }
    
    $MissingPrereqs = @()
    
    foreach ($Prereq in $Prerequisites.GetEnumerator()) {
        try {
            $Version = & $Prereq.Value
            if ($Version) {
                Write-Log "✅ $($Prereq.Name): $($Version[0])" "SUCCESS"
            } else {
                $MissingPrereqs += $Prereq.Name
                Write-Log "❌ $($Prereq.Name): Not found" "ERROR"
            }
        } catch {
            $MissingPrereqs += $Prereq.Name
            Write-Log "❌ $($Prereq.Name): Not found" "ERROR"
        }
    }
    
    if ($MissingPrereqs.Count -gt 0) {
        Write-Log "Missing prerequisites: $($MissingPrereqs -join ', ')" "ERROR"
        Write-Log "Please install missing components before continuing." "ERROR"
        exit 1
    }
    
    Write-Log "All prerequisites satisfied!" "SUCCESS"
}

# Setup dependencies
function Install-Dependencies {
    if ($SkipDependencies) {
        Write-Log "Skipping dependency installation (--SkipDependencies)" "WARN"
        return
    }
    
    Write-Log "Installing project dependencies..." "INFO"
    
    # Python dependencies
    Write-Log "Installing Python dependencies..." "INFO"
    try {
        & python -m pip install --upgrade pip
        & python -m pip install -r "$ProjectRoot\requirements.txt"
        
        # Additional AI/ML packages
        $AiPackages = @(
            "ollama",
            "openai",
            "anthropic",
            "transformers",
            "torch",
            "psutil",
            "aiohttp",
            "fastapi",
            "uvicorn",
            "websockets"
        )
        
        foreach ($Package in $AiPackages) {
            Write-Log "Installing $Package..." "INFO"
            & python -m pip install $Package
        }
        
        Write-Log "Python dependencies installed successfully" "SUCCESS"
    } catch {
        Write-Log "Failed to install Python dependencies: $($_.Exception.Message)" "ERROR"
        throw
    }
    
    # Node.js dependencies for VS Code extension
    Write-Log "Installing Node.js dependencies..." "INFO"
    try {
        Set-Location "$ProjectRoot\vscode-extension"
        & npm install
        & npm run compile
        Set-Location $ProjectRoot
        Write-Log "Node.js dependencies installed successfully" "SUCCESS"
    } catch {
        Write-Log "Failed to install Node.js dependencies: $_" "ERROR"
        Set-Location $ProjectRoot
        throw
    }
    
    # Rust dependencies
    Write-Log "Building Rust components..." "INFO"
    try {
        Set-Location "$ProjectRoot\services\event-store"
        & cargo build --release
        Set-Location $ProjectRoot
        Write-Log "Rust components built successfully" "SUCCESS"
    } catch {
        Write-Log "Failed to build Rust components: $_" "ERROR"
        Set-Location $ProjectRoot
        throw
    }
}

# Setup Ollama and AI models
function Setup-AiModels {
    Write-Log "Setting up AI models..." "INFO"
    
    # Check if Ollama is running
    try {
        $OllamaStatus = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 5
        Write-Log "Ollama is running" "SUCCESS"
    } catch {
        Write-Log "Ollama not running. Please start Ollama service." "WARN"
        Write-Log "Download from: https://ollama.ai" "INFO"
        
        if (-not $LocalOnly) {
            return
        }
    }
    
    # Pull required models
    $RequiredModels = @(
        "llama3.2",
        "mixtral",
        "phi3",
        "codellama"
    )
    
    foreach ($Model in $RequiredModels) {
        Write-Log "Pulling model: $Model..." "INFO"
        try {
            & ollama pull $Model
            Write-Log "Model $Model pulled successfully" "SUCCESS"
        } catch {
            Write-Log "Failed to pull model $Model`: $($_.Exception.Message)" "WARN"
        }
    }
}

# Deploy AI debugging system
function Deploy-AiDebugSystem {
    Write-Log "Deploying AI debugging system..." "INFO"
    
    # Create necessary directories
    $Directories = @(
        "logs",
        "data",
        "models",
        "cache"
    )
    
    foreach ($Dir in $Directories) {
        $DirPath = Join-Path $ProjectRoot $Dir
        if (-not (Test-Path $DirPath)) {
            New-Item -ItemType Directory -Path $DirPath -Force | Out-Null
            Write-Log "Created directory: $Dir" "INFO"
        }
    }
    
    # Copy configuration files
    Write-Log "Setting up configuration..." "INFO"
    
    # Generate AI debug configuration if it doesn't exist
    if (-not (Test-Path $Script:ConfigFile)) {
        Write-Log "Generating AI debug configuration..." "INFO"
        
        $Config = @{
            ai_debug_config = @{
                providers = @{
                    ollama = @{
                        endpoint = "http://localhost:11434"
                        models = @("llama3.2", "mixtral", "phi3", "codellama")
                        default_model = "llama3.2"
                    }
                    openai = @{
                        endpoint = "https://api.openai.com/v1"
                        models = @("gpt-4", "gpt-3.5-turbo")
                        api_key_env = "OPENAI_API_KEY"
                    }
                    anthropic = @{
                        endpoint = "https://api.anthropic.com"
                        models = @("claude-3-opus", "claude-3-sonnet")
                        api_key_env = "ANTHROPIC_API_KEY"
                    }
                }
                routing = @{
                    strategy = "intelligent"
                    fallback_provider = "ollama"
                    performance_monitoring = $true
                }
                debugging_modes = @{
                    standard = @{ enabled = $true }
                    tree_of_thoughts = @{ enabled = $true; max_depth = 3 }
                    react = @{ enabled = $true; max_cycles = 10 }
                    intelligent = @{ enabled = $true; auto_select = $true }
                }
                security = @{
                    privacy_mode = $true
                    data_retention_days = 30
                    anonymize_code = $true
                }
            }
        }
        
        $Config | ConvertTo-Json -Depth 10 | Set-Content -Path $Script:ConfigFile
        Write-Log "Configuration generated: $Script:ConfigFile" "SUCCESS"
    }
    
    # Set up services
    Write-Log "Starting AI debugging services..." "INFO"
    
    # Start error monitoring service
    try {
        Start-Process -FilePath "python" -ArgumentList "$ProjectRoot\scripts\error_monitor_server.py" -WindowStyle Hidden
        Write-Log "Error monitor service started" "SUCCESS"
    } catch {
        Write-Log "Failed to start error monitor service: $_" "WARN"
    }
    
    # Start AI debug system service
    try {
        Start-Process -FilePath "python" -ArgumentList "$ProjectRoot\scripts\ai_debug_system.py", "--daemon" -WindowStyle Hidden
        Write-Log "AI debug system service started" "SUCCESS"
    } catch {
        Write-Log "Failed to start AI debug system service: $_" "WARN"
    }
}

# Run comprehensive tests
function Run-Tests {
    Write-Log "Running comprehensive test suite..." "INFO"
    
    # Unit tests
    Write-Log "Running unit tests..." "INFO"
    try {
        & python -m pytest "$ProjectRoot\tests" -v
        Write-Log "Unit tests completed" "SUCCESS"
    } catch {
        Write-Log "Unit tests failed: $_" "WARN"
    }
    
    # Integration tests
    Write-Log "Running integration tests..." "INFO"
    try {
        & python "$ProjectRoot\scripts\ai_debug_integration.py"
        Write-Log "Integration tests completed" "SUCCESS"
    } catch {
        Write-Log "Integration tests failed: $_" "ERROR"
    }
    
    # Performance tests
    Write-Log "Running performance benchmarks..." "INFO"
    try {
        & python "$ProjectRoot\scripts\benchmark.py"
        Write-Log "Performance benchmarks completed" "SUCCESS"
    } catch {
        Write-Log "Performance benchmarks failed: $_" "WARN"
    }
}

# Monitor system health
function Monitor-System {
    Write-Log "Starting system monitoring..." "INFO"
    
    # Check service health
    $Services = @{
        "Ollama" = "http://localhost:11434/api/tags"
        "Error Monitor" = "http://localhost:8001/health"
        "AI Debug System" = "http://localhost:8002/health"
    }
    
    foreach ($Service in $Services.GetEnumerator()) {
        try {
            $Response = Invoke-RestMethod -Uri $Service.Value -Method Get -TimeoutSec 5
            Write-Log "✅ $($Service.Name): Healthy" "SUCCESS"
        } catch {
            Write-Log "❌ $($Service.Name): Unhealthy" "ERROR"
        }
    }
    
    # System resources
    try {
        $Memory = Get-CimInstance -ClassName Win32_OperatingSystem
        $MemoryUsage = [math]::Round(($Memory.TotalVisibleMemorySize - $Memory.FreePhysicalMemory) / $Memory.TotalVisibleMemorySize * 100, 2)
        Write-Log "Memory Usage: $MemoryUsage%" "INFO"
        
        $Disk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'"
        $DiskUsage = [math]::Round(($Disk.Size - $Disk.FreeSpace) / $Disk.Size * 100, 2)
        Write-Log "Disk Usage: $DiskUsage%" "INFO"
    } catch {
        Write-Log "Failed to get system metrics: $_" "WARN"
    }
}

# Update system
function Update-System {
    Write-Log "Updating AI debugging system..." "INFO"
    
    # Pull latest changes
    try {
        & git pull origin main
        Write-Log "Code updated from repository" "SUCCESS"
    } catch {
        Write-Log "Failed to pull updates: $_" "WARN"
    }
    
    # Update dependencies
    Install-Dependencies
    
    # Update AI models
    Setup-AiModels
    
    # Restart services
    Write-Log "Restarting services..." "INFO"
    # Add service restart logic here
}

# VS Code extension setup
function Setup-VsCodeExtension {
    Write-Log "Setting up VS Code extension..." "INFO"
    
    $ExtensionPath = Join-Path $ProjectRoot "vscode-extension"
    
    if (Test-Path $ExtensionPath) {
        try {
            Set-Location $ExtensionPath
            & npm run compile
            
            # Package extension
            & npx vsce package
            
            # Install extension
            $PackageFile = Get-ChildItem -Path . -Filter "*.vsix" | Select-Object -First 1
            if ($PackageFile) {
                & code --install-extension $PackageFile.FullName
                Write-Log "VS Code extension installed successfully" "SUCCESS"
            }
            
            Set-Location $ProjectRoot
        } catch {
            Write-Log "Failed to setup VS Code extension: $_" "ERROR"
            Set-Location $ProjectRoot
        }
    }
}

# Main execution
function Main {
    try {
        Show-Banner
        Write-Log "Starting AI Debug Master Deployment..." "INFO"
        Write-Log "Action: $Action" "INFO"
        Write-Log "Project Root: $ProjectRoot" "INFO"
        
        switch ($Action) {
            "setup" {
                Test-Prerequisites
                Install-Dependencies
                Setup-AiModels
            }
            "deploy" {
                Deploy-AiDebugSystem
                Setup-VsCodeExtension
            }
            "test" {
                Run-Tests
            }
            "monitor" {
                Monitor-System
            }
            "update" {
                Update-System
            }
            "all" {
                Test-Prerequisites
                Install-Dependencies
                Setup-AiModels
                Deploy-AiDebugSystem
                Setup-VsCodeExtension
                Run-Tests
                Monitor-System
            }
        }
        
        Write-Log "Deployment completed successfully! 🎉" "SUCCESS"
        Write-Log "Log file: $Script:LogFile" "INFO"
        
        # Display next steps
        Write-Host @"

🚀 AI DEBUGGING SYSTEM READY!

Next Steps:
1. 📝 Open VS Code and enable the AI Debug Assistant extension
2. 🔧 Configure your preferred AI models in settings
3. 🐛 Start coding - the AI will automatically analyze errors!
4. 📊 View the dashboard: http://localhost:8002/dashboard
5. 📚 Check the error guide: docs/ERROR_PREVENTION_GUIDE.md

Key Features Enabled:
✅ Real-time error analysis
✅ Tree of Thoughts debugging
✅ ReAct autonomous debugging  
✅ Intelligent model routing
✅ Multi-provider AI support
✅ Privacy-first local processing
✅ Automated learning system

Happy debugging! 🤖✨

"@ -ForegroundColor Green
        
    } catch {
        Write-Log "Deployment failed: $_" "ERROR"
        Write-Log "Check the log file for details: $Script:LogFile" "ERROR"
        exit 1
    }
}

# Execute main function
Main
