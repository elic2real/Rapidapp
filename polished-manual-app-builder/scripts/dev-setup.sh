#!/bin/bash

# Polished Manual App Builder - Development Setup Script
# Sets up the development environment for all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running in WSL/Linux
check_environment() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        print_warning "Detected Windows environment. Some features may require WSL."
    fi
}

# Install dependencies for each service
install_dependencies() {
    print_info "Installing dependencies for all services..."
    
    # Root dependencies
    if [ -f "package.json" ]; then
        print_info "Installing root Node.js dependencies..."
        npm install
        print_status "Root dependencies installed"
    fi
    
    # Collaboration Engine (TypeScript/Node.js)
    if [ -d "services/collab-engine" ]; then
        print_info "Installing Collaboration Engine dependencies..."
        cd services/collab-engine
        npm install
        cd ../..
        print_status "Collaboration Engine dependencies installed"
    fi
    
    # AI Orchestrator (Python)
    if [ -d "services/orchestrator" ]; then
        print_info "Installing AI Orchestrator dependencies..."
        cd services/orchestrator
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            print_status "Created Python virtual environment"
        fi
        
        # Activate virtual environment
        source venv/bin/activate || {
            print_warning "Failed to activate venv, trying alternative..."
            . venv/bin/activate
        }
        
        # Install dependencies
        pip install -e .
        print_status "AI Orchestrator dependencies installed"
        
        cd ../..
    fi
    
    # Event Store (Rust)
    if [ -d "services/event-store" ]; then
        print_info "Building Event Store (Rust)..."
        cd services/event-store
        cargo build
        print_status "Event Store built successfully"
        cd ../..
    fi
}

# Setup databases
setup_databases() {
    print_info "Setting up databases..."
    
    # Start only database services
    docker compose up -d postgres redis mongodb
    
    print_info "Waiting for databases to be ready..."
    sleep 10
    
    # Wait for PostgreSQL
    while ! docker compose exec postgres pg_isready -U postgres > /dev/null 2>&1; do
        echo "Waiting for PostgreSQL..."
        sleep 2
    done
    
    # Initialize databases
    print_info "Initializing databases..."
    docker compose exec postgres psql -U postgres -f /docker-entrypoint-initdb.d/init-dbs.sql
    
    print_status "Databases initialized"
}

# Run tests for all services
run_tests() {
    print_info "Running tests for all services..."
    
    local failed_tests=()
    
    # Event Store tests
    if [ -d "services/event-store" ]; then
        print_info "Running Event Store tests..."
        cd services/event-store
        if cargo test; then
            print_status "Event Store tests passed"
        else
            print_error "Event Store tests failed"
            failed_tests+=("Event Store")
        fi
        cd ../..
    fi
    
    # Collaboration Engine tests
    if [ -d "services/collab-engine" ]; then
        print_info "Running Collaboration Engine tests..."
        cd services/collab-engine
        if npm test; then
            print_status "Collaboration Engine tests passed"
        else
            print_error "Collaboration Engine tests failed"
            failed_tests+=("Collaboration Engine")
        fi
        cd ../..
    fi
    
    # AI Orchestrator tests
    if [ -d "services/orchestrator" ]; then
        print_info "Running AI Orchestrator tests..."
        cd services/orchestrator
        source venv/bin/activate || . venv/bin/activate
        if python -m pytest; then
            print_status "AI Orchestrator tests passed"
        else
            print_error "AI Orchestrator tests failed"
            failed_tests+=("AI Orchestrator")
        fi
        cd ../..
    fi
    
    if [ ${#failed_tests[@]} -eq 0 ]; then
        print_status "All tests passed!"
    else
        print_error "Some tests failed: ${failed_tests[*]}"
        return 1
    fi
}

# Setup development tools
setup_dev_tools() {
    print_info "Setting up development tools..."
    
    # Check if pre-commit is available
    if command -v pre-commit &> /dev/null; then
        print_info "Installing pre-commit hooks..."
        pre-commit install
        print_status "Pre-commit hooks installed"
    else
        print_warning "pre-commit not found. Install with: pip install pre-commit"
    fi
    
    # Setup IDE configurations
    if [ ! -d ".vscode" ]; then
        mkdir -p .vscode
        cat > .vscode/settings.json << 'EOF'
{
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": true
    },
    "rust-analyzer.cargo.allFeatures": true,
    "python.defaultInterpreterPath": "./services/orchestrator/venv/bin/python",
    "typescript.preferences.importModuleSpecifier": "relative",
    "files.exclude": {
        "**/target": true,
        "**/node_modules": true,
        "**/__pycache__": true,
        "**/venv": true
    }
}
EOF
        print_status "VS Code settings configured"
    fi
}

# Start development environment
start_dev_environment() {
    print_info "Starting development environment..."
    
    # Start infrastructure services
    docker compose up -d postgres redis mongodb jaeger prometheus grafana
    
    print_info "Infrastructure services started. You can now:"
    echo ""
    echo "  📊 View Grafana dashboards: http://localhost:3000 (admin/admin)"
    echo "  📈 View Prometheus metrics: http://localhost:9090"
    echo "  🔍 View Jaeger traces: http://localhost:16686"
    echo ""
    echo "To start application services individually:"
    echo ""
    echo "  Event Store (Rust):"
    echo "    cd services/event-store && cargo run"
    echo ""
    echo "  AI Orchestrator (Python):"
    echo "    cd services/orchestrator && source venv/bin/activate && python -m app.main"
    echo ""
    echo "  Collaboration Engine (Node.js):"
    echo "    cd services/collab-engine && npm run dev"
    echo ""
    print_status "Development environment ready!"
}

# Lint all code
lint_code() {
    print_info "Linting all code..."
    
    local failed_lints=()
    
    # Rust code
    if [ -d "services/event-store" ]; then
        print_info "Linting Rust code..."
        cd services/event-store
        if cargo clippy -- -D warnings; then
            print_status "Rust code lint passed"
        else
            print_error "Rust code lint failed"
            failed_lints+=("Rust")
        fi
        cd ../..
    fi
    
    # TypeScript code
    if [ -d "services/collab-engine" ]; then
        print_info "Linting TypeScript code..."
        cd services/collab-engine
        if npm run lint; then
            print_status "TypeScript code lint passed"
        else
            print_error "TypeScript code lint failed"
            failed_lints+=("TypeScript")
        fi
        cd ../..
    fi
    
    # Python code
    if [ -d "services/orchestrator" ]; then
        print_info "Linting Python code..."
        cd services/orchestrator
        source venv/bin/activate || . venv/bin/activate
        
        # Run multiple Python linters
        local python_lint_passed=true
        
        if ! python -m flake8 app/; then
            print_error "flake8 failed"
            python_lint_passed=false
        fi
        
        if ! python -m black --check app/; then
            print_error "black formatting check failed"
            python_lint_passed=false
        fi
        
        if ! python -m mypy app/; then
            print_warning "mypy type checking failed (non-blocking)"
        fi
        
        if [ "$python_lint_passed" = true ]; then
            print_status "Python code lint passed"
        else
            failed_lints+=("Python")
        fi
        
        cd ../..
    fi
    
    if [ ${#failed_lints[@]} -eq 0 ]; then
        print_status "All linting passed!"
    else
        print_error "Some linting failed: ${failed_lints[*]}"
        return 1
    fi
}

# Format all code
format_code() {
    print_info "Formatting all code..."
    
    # Rust code
    if [ -d "services/event-store" ]; then
        print_info "Formatting Rust code..."
        cd services/event-store
        cargo fmt
        print_status "Rust code formatted"
        cd ../..
    fi
    
    # TypeScript code
    if [ -d "services/collab-engine" ]; then
        print_info "Formatting TypeScript code..."
        cd services/collab-engine
        npm run format
        print_status "TypeScript code formatted"
        cd ../..
    fi
    
    # Python code
    if [ -d "services/orchestrator" ]; then
        print_info "Formatting Python code..."
        cd services/orchestrator
        source venv/bin/activate || . venv/bin/activate
        python -m black app/
        python -m isort app/
        print_status "Python code formatted"
        cd ../..
    fi
}

# Show help
show_help() {
    echo "Polished Manual App Builder - Development Setup"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup        Full development environment setup"
    echo "  deps         Install dependencies only"
    echo "  test         Run all tests"
    echo "  lint         Lint all code"
    echo "  format       Format all code"
    echo "  db           Setup databases only"
    echo "  dev          Start development environment"
    echo "  clean        Clean all build artifacts"
    echo "  help         Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 setup     # Full setup for new developers"
    echo "  $0 test      # Run all tests"
    echo "  $0 dev       # Start development environment"
}

# Clean build artifacts
clean_artifacts() {
    print_info "Cleaning build artifacts..."
    
    # Rust artifacts
    if [ -d "services/event-store/target" ]; then
        rm -rf services/event-store/target
        print_status "Rust artifacts cleaned"
    fi
    
    # Node.js artifacts
    find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
    print_status "Node.js artifacts cleaned"
    
    # Python artifacts
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    if [ -d "services/orchestrator/venv" ]; then
        rm -rf services/orchestrator/venv
        print_status "Python virtual environment cleaned"
    fi
    
    print_status "All build artifacts cleaned"
}

# Main function
main() {
    local command=${1:-setup}
    
    check_environment
    
    case $command in
        setup)
            print_info "Running full development environment setup..."
            install_dependencies
            setup_databases
            setup_dev_tools
            run_tests
            start_dev_environment
            ;;
        deps)
            install_dependencies
            ;;
        test)
            run_tests
            ;;
        lint)
            lint_code
            ;;
        format)
            format_code
            ;;
        db)
            setup_databases
            ;;
        dev)
            start_dev_environment
            ;;
        clean)
            clean_artifacts
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run with all arguments
main "$@"
