# Polished Manual App Builder - Development Scripts

This directory contains essential scripts for developing, testing, and running the Polished Manual App Builder.

## Scripts Overview

### `dev-setup.sh` - Development Environment Setup
Complete development environment setup and management.

**Usage:**
```bash
# Full setup for new developers
./dev-setup.sh setup

# Install dependencies only
./dev-setup.sh deps

# Run all tests
./dev-setup.sh test

# Lint all code
./dev-setup.sh lint

# Format all code
./dev-setup.sh format

# Setup databases only
./dev-setup.sh db

# Start development environment
./dev-setup.sh dev

# Clean all build artifacts
./dev-setup.sh clean
```

**Features:**
- Multi-language dependency management (Rust, Node.js, Python)
- Database initialization and setup
- Development tools configuration (VS Code, pre-commit hooks)
- Code linting and formatting
- Test execution across all services

### `demo.sh` - Interactive System Demo
Comprehensive demonstration of all system capabilities.

**Usage:**
```bash
# Run full demo
./demo.sh

# Clean up demo resources
./demo.sh --cleanup
```

**Demo Flow:**
1. **Infrastructure Startup:** PostgreSQL, Redis, MongoDB, monitoring
2. **Service Health Checks:** Validates all services are operational
3. **Event Store Demo:** Event append/read operations and statistics
4. **AI Orchestration Demo:** Semantic caching and model routing
5. **Collaboration Demo:** Real-time collaborative editing
6. **Performance Test:** Basic throughput testing
7. **Monitoring Dashboards:** Links to Grafana, Prometheus, Jaeger

**Endpoints Demonstrated:**
- Event Store: `http://localhost:8080`
- AI Orchestrator: `http://localhost:8001`
- Collaboration Engine: `http://localhost:8003`
- Grafana: `http://localhost:3000` (admin/admin)
- Prometheus: `http://localhost:9090`
- Jaeger: `http://localhost:16686`

### `benchmark.sh` - Performance Benchmarking
Comprehensive performance testing and analysis suite.

**Usage:**
```bash
# Quick performance check
./benchmark.sh quick

# Comprehensive benchmark suite
./benchmark.sh full

# Individual service benchmarks
./benchmark.sh event-store
./benchmark.sh ai
./benchmark.sh collab

# Resource analysis
./benchmark.sh memory
./benchmark.sh cpu
./benchmark.sh latency
```

**Benchmark Categories:**

#### Event Store Performance
- **Single-threaded throughput:** Sequential event append performance
- **Multi-threaded throughput:** Concurrent client performance
- **Read performance:** Stream retrieval speed
- **Target:** >10,000 events/sec for production

#### AI Orchestration Performance
- **Semantic cache throughput:** Cache hit/miss performance
- **Model routing latency:** Request routing overhead
- **Target:** >100 requests/sec, <50ms routing latency

#### Collaboration Engine Performance
- **WebSocket connections:** Concurrent connection handling
- **Room operations:** Room creation/management speed
- **Target:** >100 concurrent users per instance

#### Resource Analysis
- **Memory usage:** Per-service memory consumption
- **CPU usage:** Load testing impact
- **Latency percentiles:** P50/P95/P99 response times

**Output:**
- Real-time performance metrics
- Detailed markdown reports
- Historical benchmark data
- Recommendations for optimization

## Prerequisites

### Windows (PowerShell)
```powershell
# Enable WSL2 for better Docker performance
wsl --install

# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Install Git Bash for shell script execution
# Download from: https://git-scm.com/download/win
```

### Linux/macOS
```bash
# Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Development tools
sudo apt update
sudo apt install -y curl jq bc
```

## Running Scripts on Windows

### Option 1: Git Bash (Recommended)
```bash
# Open Git Bash terminal
cd /c/Users/mawil/tooRapidShip/polished-manual-app-builder/scripts
./dev-setup.sh setup
./demo.sh
```

### Option 2: WSL2
```bash
# In WSL2 terminal
cd /mnt/c/Users/mawil/tooRapidShip/polished-manual-app-builder/scripts
./dev-setup.sh setup
./demo.sh
```

### Option 3: PowerShell (Limited)
```powershell
# Some functionality may be limited in PowerShell
# Use Docker commands directly for basic operations
docker compose up -d
```

## Development Workflow

### New Developer Setup
```bash
# 1. Clone repository and navigate to scripts
cd polished-manual-app-builder/scripts

# 2. Run complete development setup
./dev-setup.sh setup

# 3. Verify with demo
./demo.sh

# 4. Run benchmarks to establish baseline
./benchmark.sh quick
```

### Daily Development
```bash
# Start development environment
./dev-setup.sh dev

# Run tests after changes
./dev-setup.sh test

# Lint and format code
./dev-setup.sh lint
./dev-setup.sh format

# Performance regression testing
./benchmark.sh quick
```

### CI/CD Integration
These scripts are designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Setup Development Environment
  run: ./scripts/dev-setup.sh setup

- name: Run Tests
  run: ./scripts/dev-setup.sh test

- name: Run Benchmarks
  run: ./scripts/benchmark.sh quick

- name: Generate Demo
  run: ./scripts/demo.sh --cleanup
```

## Troubleshooting

### Common Issues

#### Docker Not Running
```bash
# Check Docker status
docker ps

# Start Docker Desktop (Windows)
# Or start Docker daemon (Linux)
sudo systemctl start docker
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8080

# Stop conflicting services
docker compose down
```

#### Permission Issues (Linux/macOS)
```bash
# Make scripts executable
chmod +x *.sh

# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

#### WSL2 Path Issues (Windows)
```bash
# Use WSL2 paths, not Windows paths
cd /mnt/c/Users/mawil/tooRapidShip/polished-manual-app-builder
```

### Performance Issues

#### Slow Docker on Windows
- Enable WSL2 backend in Docker Desktop
- Allocate more memory to Docker (8GB+ recommended)
- Use WSL2 terminal for better performance

#### Database Connection Issues
```bash
# Check database health
docker compose exec postgres pg_isready -U postgres
docker compose exec redis redis-cli ping

# Restart databases
docker compose restart postgres redis mongodb
```

## Script Customization

### Environment Variables
```bash
# Customize ports (optional)
export EVENT_STORE_PORT=8080
export ORCHESTRATOR_PORT=8001
export COLLAB_ENGINE_PORT=8003

# Customize benchmark parameters
export BENCHMARK_EVENTS=1000
export BENCHMARK_CLIENTS=10
```

### Configuration Files
- `docker-compose.yml`: Service configuration
- `rapidship.config.yml`: Project settings
- `.vscode/settings.json`: IDE configuration

## Monitoring and Observability

All scripts integrate with the monitoring stack:

- **Metrics:** Prometheus scrapes service metrics
- **Logging:** Structured JSON logs with request IDs
- **Tracing:** OpenTelemetry spans exported to Jaeger
- **Dashboards:** Grafana dashboards for all services

Access monitoring during demos:
```bash
# Start demo with monitoring
./demo.sh

# Access dashboards
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus
open http://localhost:16686 # Jaeger
```

## Contributing

When adding new scripts:

1. Follow the existing patterns for argument parsing
2. Include comprehensive help text
3. Add error handling and status reporting
4. Use colored output for better UX
5. Integrate with monitoring and logging
6. Add to this README with usage examples

### Script Template
```bash
#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✓${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

show_help() {
    echo "Script description"
    echo "Usage: $0 [command]"
}

main() {
    local command=${1:-default}
    case $command in
        help|--help|-h) show_help ;;
        *) print_error "Unknown command: $command"; show_help; exit 1 ;;
    esac
}

main "$@"
```

This script collection provides a complete development experience for the Polished Manual App Builder, from initial setup to production benchmarking.
