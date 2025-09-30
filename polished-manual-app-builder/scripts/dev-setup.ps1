# Polished Manual App Builder - Development Setup (PowerShell)
# Complete development environment setup and management

param(
    [string]$Action = "setup",
    [switch]$Help = $false
)

# Colors for console output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-Status {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor $Blue
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $Red
}

function Test-Environment {
    if ($env:OS -eq "Windows_NT") {
        Write-Info "Detected Windows environment"
        
        # Check for WSL
        if (Get-Command wsl -ErrorAction SilentlyContinue) {
            Write-Status "WSL is available"
        } else {
            Write-Warning "WSL not found. Consider installing for better Docker performance."
        }
    }
}

function Install-Dependencies {
    Write-Info "Installing dependencies for all services..."
    
    # Root dependencies
    if (Test-Path "package.json") {
        Write-Info "Installing root Node.js dependencies..."
        npm install
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Root dependencies installed"
        } else {
            Write-Error "Failed to install root dependencies"
        }
    }
    
    # Collaboration Engine (TypeScript/Node.js)
    if (Test-Path "services\collab-engine") {
        Write-Info "Installing Collaboration Engine dependencies..."
        Push-Location "services\collab-engine"
        npm install
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Collaboration Engine dependencies installed"
        } else {
            Write-Error "Failed to install Collaboration Engine dependencies"
        }
        Pop-Location
    }
    
    # AI Orchestrator (Python)
    if (Test-Path "services\orchestrator") {
        Write-Info "Installing AI Orchestrator dependencies..."
        Push-Location "services\orchestrator"
        
        # Create virtual environment if it doesn't exist
        if (!(Test-Path "venv")) {
            python -m venv venv
            if ($LASTEXITCODE -eq 0) {
                Write-Status "Created Python virtual environment"
            } else {
                Write-Error "Failed to create Python virtual environment"
                Pop-Location
                return
            }
        }
        
        # Activate virtual environment and install dependencies
        & "venv\Scripts\Activate.ps1"
        pip install -e .
        if ($LASTEXITCODE -eq 0) {
            Write-Status "AI Orchestrator dependencies installed"
        } else {
            Write-Error "Failed to install AI Orchestrator dependencies"
        }
        deactivate
        
        Pop-Location
    }
    
    # Event Store (Rust)
    if (Test-Path "services\event-store") {
        Write-Info "Building Event Store (Rust)..."
        Push-Location "services\event-store"
        cargo build
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Event Store built successfully"
        } else {
            Write-Error "Event Store build failed"
        }
        Pop-Location
    }
}

function Initialize-Databases {
    Write-Info "Setting up databases..."
    
    # Start only database services
    docker compose up -d postgres redis mongodb
    
    Write-Info "Waiting for databases to be ready..."
    Start-Sleep -Seconds 10
    
    # Wait for PostgreSQL
    do {
        Write-Host "Waiting for PostgreSQL..."
        Start-Sleep -Seconds 2
    } while (!(docker compose exec postgres pg_isready -U postgres 2>$null))
    
    # Initialize databases
    Write-Info "Initializing databases..."
    docker compose exec postgres psql -U postgres -f /docker-entrypoint-initdb.d/init-dbs.sql
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Databases initialized"
    } else {
        Write-Error "Database initialization failed"
    }
}

function Invoke-Tests {
    Write-Info "Running tests for all services..."
    
    $failedTests = @()
    
    # Event Store tests
    if (Test-Path "services\event-store") {
        Write-Info "Running Event Store tests..."
        Push-Location "services\event-store"
        cargo test
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Event Store tests passed"
        } else {
            Write-Error "Event Store tests failed"
            $failedTests += "Event Store"
        }
        Pop-Location
    }
    
    # Collaboration Engine tests
    if (Test-Path "services\collab-engine") {
        Write-Info "Running Collaboration Engine tests..."
        Push-Location "services\collab-engine"
        npm test
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Collaboration Engine tests passed"
        } else {
            Write-Error "Collaboration Engine tests failed"
            $failedTests += "Collaboration Engine"
        }
        Pop-Location
    }
    
    # AI Orchestrator tests
    if (Test-Path "services\orchestrator") {
        Write-Info "Running AI Orchestrator tests..."
        Push-Location "services\orchestrator"
        & "venv\Scripts\Activate.ps1"
        python -m pytest
        if ($LASTEXITCODE -eq 0) {
            Write-Status "AI Orchestrator tests passed"
        } else {
            Write-Error "AI Orchestrator tests failed"
            $failedTests += "AI Orchestrator"
        }
        deactivate
        Pop-Location
    }
    
    if ($failedTests.Count -eq 0) {
        Write-Status "All tests passed!"
        return $true
    } else {
        Write-Error "Some tests failed: $($failedTests -join ', ')"
        return $false
    }
}

function Initialize-DevTools {
    Write-Info "Setting up development tools..."
    
    # Check if pre-commit is available
    if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
        Write-Info "Installing pre-commit hooks..."
        pre-commit install
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Pre-commit hooks installed"
        }
    } else {
        Write-Warning "pre-commit not found. Install with: pip install pre-commit"
    }
    
    # Setup IDE configurations
    if (!(Test-Path ".vscode")) {
        New-Item -ItemType Directory -Path ".vscode" | Out-Null
        
        $vsCodeSettings = @{
            "editor.formatOnSave" = $true
            "editor.codeActionsOnSave" = @{
                "source.fixAll" = $true
            }
            "rust-analyzer.cargo.allFeatures" = $true
            "python.defaultInterpreterPath" = "./services/orchestrator/venv/Scripts/python.exe"
            "typescript.preferences.importModuleSpecifier" = "relative"
            "files.exclude" = @{
                "**/target" = $true
                "**/node_modules" = $true
                "**/__pycache__" = $true
                "**/venv" = $true
            }
        } | ConvertTo-Json -Depth 10
        
        $vsCodeSettings | Out-File -FilePath ".vscode\settings.json" -Encoding UTF8
        Write-Status "VS Code settings configured"
    }
}

function Start-DevEnvironment {
    Write-Info "Starting development environment..."
    
    # Start infrastructure services
    docker compose up -d postgres redis mongodb jaeger prometheus grafana
    
    Write-Info "Infrastructure services started. You can now:"
    Write-Host ""
    Write-Host "  📊 View Grafana dashboards: http://localhost:3000 (admin/admin)"
    Write-Host "  📈 View Prometheus metrics: http://localhost:9090"
    Write-Host "  🔍 View Jaeger traces: http://localhost:16686"
    Write-Host ""
    Write-Host "To start application services individually:"
    Write-Host ""
    Write-Host "  Event Store (Rust):"
    Write-Host "    cd services\event-store && cargo run"
    Write-Host ""
    Write-Host "  AI Orchestrator (Python):"
    Write-Host "    cd services\orchestrator && venv\Scripts\Activate.ps1 && python -m app.main"
    Write-Host ""
    Write-Host "  Collaboration Engine (Node.js):"
    Write-Host "    cd services\collab-engine && npm run dev"
    Write-Host ""
    Write-Status "Development environment ready!"
}

function Invoke-Linting {
    Write-Info "Linting all code..."
    
    $failedLints = @()
    
    # Rust code
    if (Test-Path "services\event-store") {
        Write-Info "Linting Rust code..."
        Push-Location "services\event-store"
        cargo clippy -- -D warnings
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Rust code lint passed"
        } else {
            Write-Error "Rust code lint failed"
            $failedLints += "Rust"
        }
        Pop-Location
    }
    
    # TypeScript code
    if (Test-Path "services\collab-engine") {
        Write-Info "Linting TypeScript code..."
        Push-Location "services\collab-engine"
        npm run lint
        if ($LASTEXITCODE -eq 0) {
            Write-Status "TypeScript code lint passed"
        } else {
            Write-Error "TypeScript code lint failed"
            $failedLints += "TypeScript"
        }
        Pop-Location
    }
    
    # Python code
    if (Test-Path "services\orchestrator") {
        Write-Info "Linting Python code..."
        Push-Location "services\orchestrator"
        & "venv\Scripts\Activate.ps1"
        
        $pythonLintPassed = $true
        
        python -m flake8 app\
        if ($LASTEXITCODE -ne 0) {
            Write-Error "flake8 failed"
            $pythonLintPassed = $false
        }
        
        python -m black --check app\
        if ($LASTEXITCODE -ne 0) {
            Write-Error "black formatting check failed"
            $pythonLintPassed = $false
        }
        
        python -m mypy app\
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "mypy type checking failed (non-blocking)"
        }
        
        if ($pythonLintPassed) {
            Write-Status "Python code lint passed"
        } else {
            $failedLints += "Python"
        }
        
        deactivate
        Pop-Location
    }
    
    if ($failedLints.Count -eq 0) {
        Write-Status "All linting passed!"
        return $true
    } else {
        Write-Error "Some linting failed: $($failedLints -join ', ')"
        return $false
    }
}

function Format-Code {
    Write-Info "Formatting all code..."
    
    # Rust code
    if (Test-Path "services\event-store") {
        Write-Info "Formatting Rust code..."
        Push-Location "services\event-store"
        cargo fmt
        Write-Status "Rust code formatted"
        Pop-Location
    }
    
    # TypeScript code
    if (Test-Path "services\collab-engine") {
        Write-Info "Formatting TypeScript code..."
        Push-Location "services\collab-engine"
        npm run format
        if ($LASTEXITCODE -eq 0) {
            Write-Status "TypeScript code formatted"
        }
        Pop-Location
    }
    
    # Python code
    if (Test-Path "services\orchestrator") {
        Write-Info "Formatting Python code..."
        Push-Location "services\orchestrator"
        & "venv\Scripts\Activate.ps1"
        python -m black app\
        python -m isort app\
        Write-Status "Python code formatted"
        deactivate
        Pop-Location
    }
}

function Clear-Artifacts {
    Write-Info "Cleaning build artifacts..."
    
    # Rust artifacts
    if (Test-Path "services\event-store\target") {
        Remove-Item -Recurse -Force "services\event-store\target"
        Write-Status "Rust artifacts cleaned"
    }
    
    # Node.js artifacts
    Get-ChildItem -Recurse -Directory -Name "node_modules" | ForEach-Object {
        Remove-Item -Recurse -Force $_
    }
    Get-ChildItem -Recurse -Directory -Name "dist" | ForEach-Object {
        Remove-Item -Recurse -Force $_
    }
    Write-Status "Node.js artifacts cleaned"
    
    # Python artifacts
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        Remove-Item -Recurse -Force $_
    }
    Get-ChildItem -Recurse -File -Name "*.pyc" | ForEach-Object {
        Remove-Item -Force $_
    }
    if (Test-Path "services\orchestrator\venv") {
        Remove-Item -Recurse -Force "services\orchestrator\venv"
        Write-Status "Python virtual environment cleaned"
    }
    
    Write-Status "All build artifacts cleaned"
}

function Show-Help {
    Write-Host "Polished Manual App Builder - Development Setup" -ForegroundColor $Green
    Write-Host ""
    Write-Host "Usage: .\dev-setup.ps1 [-Action <command>] [-Help]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  setup        Full development environment setup"
    Write-Host "  deps         Install dependencies only"
    Write-Host "  test         Run all tests"
    Write-Host "  lint         Lint all code"
    Write-Host "  format       Format all code"
    Write-Host "  db           Setup databases only"
    Write-Host "  dev          Start development environment"
    Write-Host "  clean        Clean all build artifacts"
    Write-Host "  help         Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\dev-setup.ps1 -Action setup     # Full setup for new developers"
    Write-Host "  .\dev-setup.ps1 -Action test      # Run all tests"
    Write-Host "  .\dev-setup.ps1 -Action dev       # Start development environment"
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Test-Environment

switch ($Action.ToLower()) {
    "setup" {
        Write-Info "Running full development environment setup..."
        Install-Dependencies
        Initialize-Databases
        Initialize-DevTools
        $testsPass = Invoke-Tests
        Start-DevEnvironment
        if ($testsPass) {
            Write-Status "Development environment setup completed successfully!"
        } else {
            Write-Warning "Setup completed with test failures. Check the logs above."
        }
    }
    "deps" {
        Install-Dependencies
    }
    "test" {
        Invoke-Tests
    }
    "lint" {
        Invoke-Linting
    }
    "format" {
        Format-Code
    }
    "db" {
        Initialize-Databases
    }
    "dev" {
        Start-DevEnvironment
    }
    "clean" {
        Clear-Artifacts
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Action"
        Show-Help
        exit 1
    }
}
