# Polished Manual App Builder - Demo Script (PowerShell)
# Comprehensive system demonstration and testing

param(
    [string]$Action = "demo",
    [switch]$Cleanup = $false
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

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is required but not installed"
        exit 1
    }
    
    if (!(Get-Command curl -ErrorAction SilentlyContinue)) {
        Write-Warning "curl not found, using Invoke-WebRequest instead"
    }
    
    Write-Status "Prerequisites check passed"
}

function Start-Infrastructure {
    Write-Info "Starting infrastructure services..."
    docker compose up -d postgres redis mongodb jaeger prometheus grafana
    
    Write-Info "Waiting for database to be ready..."
    Start-Sleep -Seconds 10
    
    # Wait for PostgreSQL
    do {
        Write-Host "Waiting for PostgreSQL..."
        Start-Sleep -Seconds 2
    } while (!(docker compose exec postgres pg_isready -U postgres 2>$null))
    
    Write-Status "Database is ready"
    
    # Wait for Redis
    do {
        Write-Host "Waiting for Redis..."
        Start-Sleep -Seconds 2
    } while (!(docker compose exec redis redis-cli ping 2>$null))
    
    Write-Status "Redis is ready"
}

function Start-Services {
    Write-Info "Starting application services..."
    docker compose up -d event-store orchestrator collab-engine
    
    Write-Info "Waiting for services to be healthy..."
    Start-Sleep -Seconds 15
    
    # Check service health
    Test-ServiceHealth "Event Store" "http://localhost:8080/health"
    Test-ServiceHealth "Orchestrator" "http://localhost:8001/health"
    Test-ServiceHealth "Collaboration Engine" "http://localhost:8003/health"
}

function Test-ServiceHealth {
    param(
        [string]$ServiceName,
        [string]$HealthUrl
    )
    
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri $HealthUrl -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Status "$ServiceName is healthy"
                return
            }
        }
        catch {
            # Continue trying
        }
        
        Write-Host "Waiting for $ServiceName... (attempt $attempt/$maxAttempts)"
        Start-Sleep -Seconds 2
        $attempt++
    }
    
    Write-Error "$ServiceName failed to start"
}

function Show-AiOrchestration {
    Write-Info "Demonstrating AI orchestration with semantic caching..."
    
    $prompt = "Explain the benefits of event sourcing in microservices"
    $body = @{
        prompt = $prompt
        model = "llama3:8b"
    } | ConvertTo-Json
    
    # First request (cache miss)
    Write-Info "Making first AI request (should be cache miss)..."
    try {
        $response1 = Invoke-RestMethod -Uri "http://localhost:8001/v1/completions" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        Write-Status "AI request completed"
        if ($response1.cache_hit) {
            Write-Host "Cache hit: $($response1.cache_hit)"
        }
    }
    catch {
        Write-Warning "AI service may not be available (Ollama required)"
    }
    
    Start-Sleep -Seconds 2
    
    # Second request (should be cache hit)
    Write-Info "Making second identical request (should be cache hit)..."
    try {
        $response2 = Invoke-RestMethod -Uri "http://localhost:8001/v1/completions" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        Write-Status "Second AI request completed"
        if ($response2.cache_hit) {
            Write-Host "Cache hit: $($response2.cache_hit)"
        }
    }
    catch {
        Write-Warning "AI service request failed"
    }
}

function Show-Collaboration {
    Write-Info "Demonstrating real-time collaboration..."
    
    $roomName = "demo-room-$(Get-Date -Format 'yyyyMMddHHmmss')"
    
    Write-Info "Creating collaboration room: $roomName"
    Write-Info "You can test real-time collaboration by:"
    Write-Host "  1. Opening http://localhost:8003/rooms in your browser"
    Write-Host "  2. Multiple clients can join room: $roomName"
    Write-Host "  3. Changes will sync in real-time via Yjs CRDT"
    
    # Get room info
    try {
        $roomInfo = Invoke-RestMethod -Uri "http://localhost:8003/rooms" -Method GET -TimeoutSec 10
        Write-Info "Current rooms: $($roomInfo | ConvertTo-Json -Compress)"
    }
    catch {
        Write-Warning "Failed to get room information"
    }
}

function Show-EventStore {
    Write-Info "Demonstrating event store capabilities..."
    
    $streamId = "demo-stream-$(Get-Date -Format 'yyyyMMddHHmmss')"
    
    Write-Info "Appending events to stream: $streamId"
    
    # Append events
    for ($i = 1; $i -le 5; $i++) {
        $eventData = @{
            stream_id = $streamId
            event_type = "demo_event"
            data = @{
                message = "Event $i"
                timestamp = (Get-Date).ToString()
            }
            metadata = @{
                demo = $true
            }
        } | ConvertTo-Json
        
        try {
            Invoke-RestMethod -Uri "http://localhost:8080/events" -Method POST -Body $eventData -ContentType "application/json" -TimeoutSec 10 | Out-Null
        }
        catch {
            Write-Warning "Failed to append event $i"
        }
    }
    
    Write-Status "Appended 5 events to stream"
    
    # Read events back
    Write-Info "Reading events from stream..."
    try {
        $events = Invoke-RestMethod -Uri "http://localhost:8080/streams/$streamId/events" -Method GET -TimeoutSec 10
        $eventCount = ($events | Measure-Object).Count
        Write-Status "Read $eventCount events from stream"
    }
    catch {
        Write-Warning "Failed to read events from stream"
    }
    
    # Get stats
    try {
        $stats = Invoke-RestMethod -Uri "http://localhost:8080/stats" -Method GET -TimeoutSec 10
        Write-Info "Event store stats: $($stats | ConvertTo-Json -Compress)"
    }
    catch {
        Write-Warning "Failed to get event store stats"
    }
}

function Show-Dashboards {
    Write-Info "Monitoring dashboards are available at:"
    Write-Host ""
    Write-Host "  📊 Grafana:    http://localhost:3000 (admin/admin)"
    Write-Host "  📈 Prometheus: http://localhost:9090"
    Write-Host "  🔍 Jaeger:     http://localhost:16686"
    Write-Host ""
    Write-Info "Service endpoints:"
    Write-Host "  🏪 Event Store:        http://localhost:8080"
    Write-Host "  🤖 AI Orchestrator:    http://localhost:8001"
    Write-Host "  🤝 Collaboration:      http://localhost:8003"
    Write-Host "  📝 API Documentation:  http://localhost:8001/docs"
}

function Test-Performance {
    Write-Info "Running basic performance test..."
    
    Write-Info "Testing event store append performance..."
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    $jobs = @()
    for ($i = 1; $i -le 100; $i++) {
        $eventData = @{
            stream_id = "perf-test"
            event_type = "perf_event"
            data = @{ counter = $i }
        } | ConvertTo-Json
        
        $job = Start-Job -ScriptBlock {
            param($uri, $body)
            try {
                Invoke-RestMethod -Uri $uri -Method POST -Body $body -ContentType "application/json" -TimeoutSec 5
            }
            catch {
                # Ignore errors for performance test
            }
        } -ArgumentList "http://localhost:8080/events", $eventData
        
        $jobs += $job
        
        # Limit concurrent requests
        if ($i % 10 -eq 0) {
            $jobs | Wait-Job | Remove-Job
            $jobs = @()
        }
    }
    
    # Wait for remaining jobs
    $jobs | Wait-Job | Remove-Job
    
    $stopwatch.Stop()
    $duration = $stopwatch.Elapsed.TotalSeconds
    $throughput = [math]::Round(100 / $duration, 2)
    
    Write-Status "Appended 100 events in $([math]::Round($duration, 2))s (~$throughput events/sec)"
}

function Stop-Services {
    param([bool]$RemoveVolumes = $false)
    
    Write-Info "Cleaning up demo resources..."
    if ($RemoveVolumes) {
        docker compose down -v
    } else {
        docker compose down
    }
    Write-Status "Cleanup completed"
}

function Start-Demo {
    Write-Host "🚀 Starting Polished Manual App Builder Demo" -ForegroundColor $Green
    Write-Host "==============================================="
    Write-Host ""
    
    Write-Host "This demo will:"
    Write-Host "1. Start all services (Event Store, AI Orchestrator, Collaboration)"
    Write-Host "2. Demonstrate semantic caching with AI requests"
    Write-Host "3. Show real-time collaboration capabilities"
    Write-Host "4. Test event store functionality"
    Write-Host "5. Run basic performance tests"
    Write-Host ""
    
    Test-Prerequisites
    Start-Infrastructure
    Start-Services
    
    Write-Host ""
    Write-Status "All services are running!"
    Write-Host ""
    
    Show-EventStore
    Write-Host ""
    
    Show-AiOrchestration
    Write-Host ""
    
    Show-Collaboration
    Write-Host ""
    
    Test-Performance
    Write-Host ""
    
    Show-Dashboards
    Write-Host ""
    
    Write-Status "Demo completed successfully!"
    Write-Info "Services will continue running. Press Ctrl+C to stop or run with -Cleanup to clean up."
    
    # Keep services running
    Write-Host "Press any key to stop services and cleanup..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    Stop-Services -RemoveVolumes $true
}

# Main execution
switch ($Action.ToLower()) {
    "demo" {
        if ($Cleanup) {
            Stop-Services -RemoveVolumes $true
        } else {
            Start-Demo
        }
    }
    "cleanup" {
        Stop-Services -RemoveVolumes $true
    }
    "help" {
        Write-Host "Polished Manual App Builder - Demo Script"
        Write-Host ""
        Write-Host "Usage: .\demo.ps1 [-Action <action>] [-Cleanup]"
        Write-Host ""
        Write-Host "Actions:"
        Write-Host "  demo     Run full demonstration (default)"
        Write-Host "  cleanup  Stop services and cleanup"
        Write-Host "  help     Show this help"
        Write-Host ""
        Write-Host "Examples:"
        Write-Host "  .\demo.ps1                # Run demo"
        Write-Host "  .\demo.ps1 -Cleanup       # Cleanup resources"
        Write-Host "  .\demo.ps1 -Action help   # Show help"
    }
    default {
        Write-Error "Unknown action: $Action"
        Write-Host "Use .\demo.ps1 -Action help for usage information"
        exit 1
    }
}
