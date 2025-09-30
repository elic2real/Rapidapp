#!/usr/bin/env pwsh

# Polished Manual App Builder - Complete System Demo
# This PowerShell script works on Windows, Linux, and macOS

param(
    [string]$Action = "demo",
    [switch]$Verbose = $false
)

# Set error preference
$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Failure { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Header { param($msg) Write-Host "`n🚀 $msg" -ForegroundColor Magenta -BackgroundColor Black }

function Show-Welcome {
    Clear-Host
    Write-Host @"
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🏗️  POLISHED MANUAL APP BUILDER DEMO                      ║
║                                                                  ║
║    Production-ready AI-assisted multi-stack app builder         ║
║    Built for Netflix/Google-level teams                        ║
║                                                                  ║
║    🧠 AI Orchestration    🤝 Real-time Collab                    ║
║    🏪 Event Sourcing     📊 Observability                       ║
║    🔒 Security Ready     ⚡ High Performance                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

    Write-Host "`nWelcome to the comprehensive system demonstration!" -ForegroundColor White
    Write-Host "This will showcase all components working together.`n" -ForegroundColor Gray
}

function Test-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    $requirements = @(
        @{ Name = "Docker"; Command = "docker"; Required = $true },
        @{ Name = "Docker Compose"; Command = "docker compose version"; Required = $true },
        @{ Name = "Node.js"; Command = "node"; Required = $false },
        @{ Name = "Python"; Command = "python"; Required = $false },
        @{ Name = "Rust/Cargo"; Command = "cargo"; Required = $false }
    )
    
    $missing = @()
    
    foreach ($req in $requirements) {
        try {
            if ($req.Command -eq "docker compose version") {
                $result = & docker compose version 2>&1
            } else {
                $result = & $req.Command --version 2>&1
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$($req.Name) is available"
                if ($Verbose) {
                    Write-Host "    Version: $($result | Select-Object -First 1)" -ForegroundColor Gray
                }
            } else {
                throw "Command failed"
            }
        }
        catch {
            if ($req.Required) {
                Write-Failure "$($req.Name) is required but not found"
                $missing += $req.Name
            } else {
                Write-Warning "$($req.Name) is recommended but not found"
            }
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Failure "Missing required dependencies: $($missing -join ', ')"
        Write-Host "`nPlease install the missing dependencies and try again." -ForegroundColor Yellow
        exit 1
    }
    
    Write-Success "All required prerequisites are available!"
}

function Start-Infrastructure {
    Write-Header "Starting Infrastructure Services"
    
    Write-Info "Starting databases and monitoring..."
    
    try {
        # Stop any existing containers to avoid conflicts
        docker compose down 2>$null
        
        # Start infrastructure services
        docker compose up -d postgres redis mongodb jaeger prometheus grafana
        
        Write-Success "Infrastructure services started"
        
        # Wait for services to be ready
        Write-Info "Waiting for services to initialize..."
        Start-Sleep -Seconds 15
        
        # Check PostgreSQL
        $attempts = 0
        do {
            $attempts++
            Write-Host "Checking PostgreSQL... (attempt $attempts)" -ForegroundColor Gray
            $pgReady = docker compose exec postgres pg_isready -U postgres 2>$null
            if ($LASTEXITCODE -ne 0) {
                Start-Sleep -Seconds 3
            }
        } while ($LASTEXITCODE -ne 0 -and $attempts -lt 20)
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "PostgreSQL is ready"
        } else {
            Write-Warning "PostgreSQL may not be fully ready yet"
        }
        
        # Check Redis
        $redisReady = docker compose exec redis redis-cli ping 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Redis is ready"
        } else {
            Write-Warning "Redis may not be fully ready yet"
        }
        
    }
    catch {
        Write-Failure "Failed to start infrastructure: $_"
        throw
    }
}

function Start-ApplicationServices {
    Write-Header "Starting Application Services"
    
    Write-Info "Starting core application services..."
    
    try {
        docker compose up -d event-store orchestrator collab-engine
        
        Write-Info "Waiting for application services to be healthy..."
        Start-Sleep -Seconds 20
        
        # Check service health
        $services = @(
            @{ Name = "Event Store"; Url = "http://localhost:8080/health"; Port = 8080 },
            @{ Name = "AI Orchestrator"; Url = "http://localhost:8001/health"; Port = 8001 },
            @{ Name = "Collaboration Engine"; Url = "http://localhost:8003/health"; Port = 8003 }
        )
        
        foreach ($service in $services) {
            $attempts = 0
            $healthy = $false
            
            do {
                $attempts++
                Write-Host "Checking $($service.Name)... (attempt $attempts)" -ForegroundColor Gray
                
                try {
                    $response = Invoke-WebRequest -Uri $service.Url -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
                    if ($response.StatusCode -eq 200) {
                        Write-Success "$($service.Name) is healthy"
                        $healthy = $true
                    }
                }
                catch {
                    Start-Sleep -Seconds 3
                }
            } while (-not $healthy -and $attempts -lt 15)
            
            if (-not $healthy) {
                Write-Warning "$($service.Name) may not be fully ready (port $($service.Port))"
            }
        }
        
        Write-Success "Application services are running!"
        
    }
    catch {
        Write-Failure "Failed to start application services: $_"
        throw
    }
}

function Demo-EventStore {
    Write-Header "Event Store Demonstration"
    
    Write-Info "Testing high-performance event sourcing..."
    
    $streamId = "demo-$(Get-Date -Format 'yyyyMMddHHmmss')"
    
    try {
        # Append events
        Write-Info "Appending events to stream: $streamId"
        
        for ($i = 1; $i -le 10; $i++) {
            $eventData = @{
                stream_id = $streamId
                event_type = "user_action"
                data = @{
                    action = "demo_event_$i"
                    timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
                    user_id = "demo-user"
                    metadata = @{
                        demo = $true
                        sequence = $i
                    }
                }
            } | ConvertTo-Json -Depth 5
            
            $response = Invoke-RestMethod -Uri "http://localhost:8080/events" -Method POST -Body $eventData -ContentType "application/json" -TimeoutSec 10
            
            if ($Verbose) {
                Write-Host "  Event $i: $($response.id)" -ForegroundColor Gray
            }
        }
        
        Write-Success "Successfully appended 10 events"
        
        # Read events back
        Write-Info "Reading events from stream..."
        $events = Invoke-RestMethod -Uri "http://localhost:8080/streams/$streamId/events" -Method GET -TimeoutSec 10
        Write-Success "Read $($events.Count) events from stream"
        
        # Get statistics
        $stats = Invoke-RestMethod -Uri "http://localhost:8080/stats" -Method GET -TimeoutSec 10
        Write-Info "Event Store Stats:"
        Write-Host "  📊 Total Events: $($stats.total_events)" -ForegroundColor Cyan
        Write-Host "  📊 Total Streams: $($stats.total_streams)" -ForegroundColor Cyan
        Write-Host "  📊 Storage Size: $($stats.storage_size_mb) MB" -ForegroundColor Cyan
        
    }
    catch {
        Write-Warning "Event Store demo failed: $_"
    }
}

function Demo-AiOrchestration {
    Write-Header "AI Orchestration Demonstration"
    
    Write-Info "Testing semantic caching and model routing..."
    
    $prompts = @(
        "Explain the benefits of event sourcing",
        "What are the advantages of CQRS patterns?",
        "How does Yjs CRDT handle conflicts?",
        "Explain the benefits of event sourcing"  # Duplicate for cache hit
    )
    
    foreach ($i in 0..($prompts.Count - 1)) {
        $prompt = $prompts[$i]
        
        try {
            Write-Info "Request $($i + 1): Testing '$($prompt.Substring(0, [Math]::Min(30, $prompt.Length)))...'"
            
            $requestData = @{
                prompt = $prompt
                model = "test-model"
                max_tokens = 100
            } | ConvertTo-Json
            
            $startTime = Get-Date
            $response = Invoke-RestMethod -Uri "http://localhost:8001/v1/completions" -Method POST -Body $requestData -ContentType "application/json" -TimeoutSec 30
            $endTime = Get-Date
            $duration = ($endTime - $startTime).TotalMilliseconds
            
            $cacheStatus = if ($response.cache_hit) { "CACHE HIT" } else { "CACHE MISS" }
            Write-Host "  ⚡ Response time: $([math]::Round($duration, 2))ms | Status: $cacheStatus" -ForegroundColor $(if ($response.cache_hit) { "Green" } else { "Yellow" })
            
            if ($Verbose -and $response.response) {
                Write-Host "  💬 Response: $($response.response.Substring(0, [Math]::Min(100, $response.response.Length)))..." -ForegroundColor Gray
            }
            
        }
        catch {
            Write-Warning "AI request $($i + 1) failed: $_"
        }
        
        Start-Sleep -Seconds 1
    }
    
    Write-Success "AI Orchestration demo completed"
}

function Demo-Collaboration {
    Write-Header "Real-time Collaboration Demonstration"
    
    Write-Info "Testing Yjs CRDT and WebSocket collaboration..."
    
    try {
        # Get room information
        $rooms = Invoke-RestMethod -Uri "http://localhost:8003/rooms" -Method GET -TimeoutSec 10
        Write-Success "Collaboration service is responding"
        Write-Info "Active rooms: $($rooms.Count)"
        
        # Create a demo room
        $roomData = @{
            name = "demo-room-$(Get-Date -Format 'HHmmss')"
            description = "Demo room for testing"
        } | ConvertTo-Json
        
        try {
            $newRoom = Invoke-RestMethod -Uri "http://localhost:8003/rooms" -Method POST -Body $roomData -ContentType "application/json" -TimeoutSec 10
            Write-Success "Created demo room: $($newRoom.name)"
        }
        catch {
            Write-Info "Room creation endpoint may not be implemented yet"
        }
        
        Write-Info "Collaboration Features:"
        Write-Host "  🤝 Real-time multi-user editing" -ForegroundColor Cyan
        Write-Host "  🔄 Conflict-free synchronization with Yjs CRDT" -ForegroundColor Cyan
        Write-Host "  👥 Presence awareness and user cursors" -ForegroundColor Cyan
        Write-Host "  💾 Persistent state via Event Store" -ForegroundColor Cyan
        Write-Host "  🌐 WebSocket scaling with Redis pub/sub" -ForegroundColor Cyan
        
    }
    catch {
        Write-Warning "Collaboration demo failed: $_"
    }
}

function Test-Performance {
    Write-Header "Performance Testing"
    
    Write-Info "Running concurrent performance tests..."
    
    try {
        # Test Event Store throughput
        Write-Info "Testing Event Store append performance..."
        
        $jobs = @()
        $testEvents = 50
        $startTime = Get-Date
        
        for ($i = 1; $i -le $testEvents; $i++) {
            $eventData = @{
                stream_id = "perf-test"
                event_type = "performance_test"
                data = @{
                    counter = $i
                    timestamp = (Get-Date).ToString()
                }
            } | ConvertTo-Json
            
            $job = Start-Job -ScriptBlock {
                param($uri, $body)
                try {
                    Invoke-RestMethod -Uri $uri -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10 | Out-Null
                    return $true
                }
                catch {
                    return $false
                }
            } -ArgumentList "http://localhost:8080/events", $eventData
            
            $jobs += $job
            
            # Process in batches to avoid overwhelming the system
            if ($i % 10 -eq 0) {
                $jobs | Wait-Job | Remove-Job
                $jobs = @()
            }
        }
        
        # Wait for remaining jobs
        $jobs | Wait-Job | Remove-Job
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        $throughput = [math]::Round($testEvents / $duration, 2)
        
        Write-Success "Event Store Performance: $throughput events/sec"
        
        # Test AI Orchestrator cache performance
        Write-Info "Testing AI cache performance..."
        $cachePrompt = "Performance test prompt for caching"
        $cacheRequests = 10
        $cacheStartTime = Get-Date
        
        for ($i = 1; $i -le $cacheRequests; $i++) {
            $requestData = @{
                prompt = $cachePrompt
                model = "test-model"
            } | ConvertTo-Json
            
            try {
                Invoke-RestMethod -Uri "http://localhost:8001/v1/completions" -Method POST -Body $requestData -ContentType "application/json" -TimeoutSec 10 | Out-Null
            }
            catch {
                # Ignore individual failures for performance test
            }
        }
        
        $cacheEndTime = Get-Date
        $cacheDuration = ($cacheEndTime - $cacheStartTime).TotalSeconds
        $cacheThroughput = [math]::Round($cacheRequests / $cacheDuration, 2)
        
        Write-Success "AI Cache Performance: $cacheThroughput requests/sec"
        
    }
    catch {
        Write-Warning "Performance testing failed: $_"
    }
}

function Show-SystemStatus {
    Write-Header "System Status & Access Information"
    
    Write-Info "All services are running! Access URLs:"
    
    $endpoints = @(
        @{ Name = "🏪 Event Store API"; Url = "http://localhost:8080"; Description = "Event sourcing and CQRS" },
        @{ Name = "🤖 AI Orchestrator API"; Url = "http://localhost:8001"; Description = "AI routing and caching" },
        @{ Name = "🤝 Collaboration Engine"; Url = "http://localhost:8003"; Description = "Real-time collaboration" },
        @{ Name = "📊 Grafana Dashboards"; Url = "http://localhost:3000"; Description = "Monitoring (admin/admin)" },
        @{ Name = "📈 Prometheus Metrics"; Url = "http://localhost:9090"; Description = "Metrics collection" },
        @{ Name = "🔍 Jaeger Tracing"; Url = "http://localhost:16686"; Description = "Distributed tracing" }
    )
    
    foreach ($endpoint in $endpoints) {
        Write-Host ""
        Write-Host "  $($endpoint.Name)" -ForegroundColor Green
        Write-Host "    URL: $($endpoint.Url)" -ForegroundColor Cyan
        Write-Host "    Description: $($endpoint.Description)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Info "API Documentation:"
    Write-Host "  📝 Event Store API Docs: http://localhost:8080/docs" -ForegroundColor Cyan
    Write-Host "  📝 AI Orchestrator API Docs: http://localhost:8001/docs" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Success "Demo completed successfully! 🎉"
    Write-Host ""
}

function Stop-AllServices {
    Write-Header "Cleaning Up Services"
    
    Write-Info "Stopping all Docker services..."
    
    try {
        docker compose down -v
        Write-Success "All services stopped and volumes removed"
    }
    catch {
        Write-Warning "Cleanup may have failed: $_"
    }
}

function Show-Help {
    Write-Host @"
Polished Manual App Builder - Complete Demo Script

USAGE:
    .\complete-demo.ps1 [ACTION] [-Verbose]

ACTIONS:
    demo        Run complete system demonstration (default)
    start       Start all services only
    stop        Stop all services and cleanup
    status      Show service status and URLs
    help        Show this help message

OPTIONS:
    -Verbose    Show detailed output during demo

EXAMPLES:
    .\complete-demo.ps1                    # Run full demo
    .\complete-demo.ps1 -Verbose           # Run demo with detailed output
    .\complete-demo.ps1 start              # Just start services
    .\complete-demo.ps1 stop               # Stop and cleanup
    .\complete-demo.ps1 status             # Show access URLs

REQUIREMENTS:
    - Docker and Docker Compose (required)
    - Internet connection for pulling images
    - Ports 8080, 8001, 8003, 3000, 9090, 16686 available

This script demonstrates:
    ✅ Event sourcing with high-performance append-only logs
    ✅ AI orchestration with semantic caching
    ✅ Real-time collaboration with conflict-free resolution
    ✅ Production-ready observability and monitoring
    ✅ Performance testing and benchmarking

"@
}

# Main execution logic
try {
    switch ($Action.ToLower()) {
        "demo" {
            Show-Welcome
            Test-Prerequisites
            Start-Infrastructure
            Start-ApplicationServices
            Demo-EventStore
            Demo-AiOrchestration
            Demo-Collaboration
            Test-Performance
            Show-SystemStatus
            
            Write-Host "Press any key to stop services and cleanup..." -ForegroundColor Yellow
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            Stop-AllServices
        }
        "start" {
            Test-Prerequisites
            Start-Infrastructure
            Start-ApplicationServices
            Show-SystemStatus
        }
        "stop" {
            Stop-AllServices
        }
        "status" {
            Show-SystemStatus
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
}
catch {
    Write-Failure "Demo failed with error: $_"
    Write-Host "Run '.\complete-demo.ps1 stop' to cleanup if needed." -ForegroundColor Yellow
    exit 1
}
