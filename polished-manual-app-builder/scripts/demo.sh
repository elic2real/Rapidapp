#!/bin/bash

# Polished Manual App Builder - Demo Script
# This script demonstrates the complete system functionality

set -e

echo "🚀 Starting Polished Manual App Builder Demo"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        print_error "curl is required but not installed"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Start infrastructure
start_infrastructure() {
    print_info "Starting infrastructure services..."
    docker compose up -d postgres redis mongodb jaeger prometheus grafana
    
    print_info "Waiting for database to be ready..."
    sleep 10
    
    # Wait for PostgreSQL
    while ! docker compose exec postgres pg_isready -U postgres > /dev/null 2>&1; do
        echo "Waiting for PostgreSQL..."
        sleep 2
    done
    print_status "Database is ready"
    
    # Wait for Redis
    while ! docker compose exec redis redis-cli ping > /dev/null 2>&1; do
        echo "Waiting for Redis..."
        sleep 2
    done
    print_status "Redis is ready"
}

# Start application services
start_services() {
    print_info "Starting application services..."
    docker compose up -d event-store orchestrator collab-engine
    
    print_info "Waiting for services to be healthy..."
    sleep 15
    
    # Check service health
    check_service_health "Event Store" "http://localhost:8080/health"
    check_service_health "Orchestrator" "http://localhost:8001/health"
    check_service_health "Collaboration Engine" "http://localhost:8003/health"
}

# Check service health
check_service_health() {
    local service_name=$1
    local health_url=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$health_url" > /dev/null 2>&1; then
            print_status "$service_name is healthy"
            return 0
        fi
        
        echo "Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to start"
    return 1
}

# Demonstrate AI orchestration
demo_ai_orchestration() {
    print_info "Demonstrating AI orchestration with semantic caching..."
    
    # First request (cache miss)
    print_info "Making first AI request (should be cache miss)..."
    local prompt="Explain the benefits of event sourcing in microservices"
    
    local response1=$(curl -s -X POST "http://localhost:8001/v1/completions" \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"$prompt\", \"model\": \"llama3:8b\"}" || echo "Request failed")
    
    if [[ "$response1" == *"cache_hit"* ]]; then
        print_status "AI request completed"
        echo "Cache hit: $(echo "$response1" | grep -o '"cache_hit":[^,]*')"
    else
        print_warning "AI service may not be available (Ollama required)"
    fi
    
    sleep 2
    
    # Second request (should be cache hit)
    print_info "Making second identical request (should be cache hit)..."
    local response2=$(curl -s -X POST "http://localhost:8001/v1/completions" \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"$prompt\", \"model\": \"llama3:8b\"}" || echo "Request failed")
    
    if [[ "$response2" == *"cache_hit"* ]]; then
        print_status "Second AI request completed"
        echo "Cache hit: $(echo "$response2" | grep -o '"cache_hit":[^,]*')"
    fi
}

# Demonstrate collaboration
demo_collaboration() {
    print_info "Demonstrating real-time collaboration..."
    
    # Create a test room
    local room_name="demo-room-$(date +%s)"
    
    print_info "Creating collaboration room: $room_name"
    print_info "You can test real-time collaboration by:"
    echo "  1. Opening http://localhost:8003/rooms in your browser"
    echo "  2. Multiple clients can join room: $room_name"
    echo "  3. Changes will sync in real-time via Yjs CRDT"
    
    # Get room info
    local room_info=$(curl -s "http://localhost:8003/rooms" || echo "Failed to get rooms")
    print_info "Current rooms: $room_info"
}

# Demonstrate event store
demo_event_store() {
    print_info "Demonstrating event store capabilities..."
    
    # Append some events
    local stream_id="demo-stream-$(date +%s)"
    
    print_info "Appending events to stream: $stream_id"
    
    for i in {1..5}; do
        curl -s -X POST "http://localhost:8080/events" \
            -H "Content-Type: application/json" \
            -d "{
                \"stream_id\": \"$stream_id\",
                \"event_type\": \"demo_event\",
                \"data\": {\"message\": \"Event $i\", \"timestamp\": \"$(date)\"},
                \"metadata\": {\"demo\": true}
            }" > /dev/null
    done
    
    print_status "Appended 5 events to stream"
    
    # Read events back
    print_info "Reading events from stream..."
    local events=$(curl -s "http://localhost:8080/streams/$stream_id/events")
    local event_count=$(echo "$events" | grep -o '"id"' | wc -l)
    print_status "Read $event_count events from stream"
    
    # Get stats
    local stats=$(curl -s "http://localhost:8080/stats")
    print_info "Event store stats: $stats"
}

# Show monitoring dashboards
show_dashboards() {
    print_info "Monitoring dashboards are available at:"
    echo ""
    echo "  📊 Grafana:    http://localhost:3000 (admin/admin)"
    echo "  📈 Prometheus: http://localhost:9090"
    echo "  🔍 Jaeger:     http://localhost:16686"
    echo ""
    print_info "Service endpoints:"
    echo "  🏪 Event Store:        http://localhost:8080"
    echo "  🤖 AI Orchestrator:    http://localhost:8001"
    echo "  🤝 Collaboration:      http://localhost:8003"
    echo "  📝 API Documentation:  http://localhost:8001/docs"
}

# Performance test
run_performance_test() {
    print_info "Running basic performance test..."
    
    # Test event store throughput
    print_info "Testing event store append performance..."
    local start_time=$(date +%s)
    
    for i in {1..100}; do
        curl -s -X POST "http://localhost:8080/events" \
            -H "Content-Type: application/json" \
            -d "{
                \"stream_id\": \"perf-test\",
                \"event_type\": \"perf_event\",
                \"data\": {\"counter\": $i}
            }" > /dev/null &
        
        # Limit concurrent requests
        if (( i % 10 == 0 )); then
            wait
        fi
    done
    wait
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local throughput=$((100 / duration))
    
    print_status "Appended 100 events in ${duration}s (~${throughput} events/sec)"
}

# Cleanup function
cleanup() {
    if [[ "${1:-}" == "--cleanup" ]]; then
        print_info "Cleaning up demo resources..."
        docker compose down -v
        print_status "Cleanup completed"
    else
        print_info "Demo completed. To cleanup, run: $0 --cleanup"
    fi
}

# Main demo flow
main() {
    if [[ "${1:-}" == "--cleanup" ]]; then
        cleanup --cleanup
        exit 0
    fi
    
    echo "This demo will:"
    echo "1. Start all services (Event Store, AI Orchestrator, Collaboration)"
    echo "2. Demonstrate semantic caching with AI requests"
    echo "3. Show real-time collaboration capabilities"
    echo "4. Test event store functionality"
    echo "5. Run basic performance tests"
    echo ""
    
    # Trap cleanup on exit
    trap cleanup EXIT
    
    check_prerequisites
    start_infrastructure
    start_services
    
    echo ""
    print_status "All services are running!"
    echo ""
    
    demo_event_store
    echo ""
    
    demo_ai_orchestration
    echo ""
    
    demo_collaboration
    echo ""
    
    run_performance_test
    echo ""
    
    show_dashboards
    echo ""
    
    print_status "Demo completed successfully!"
    print_info "Services will continue running. Press Ctrl+C to stop or run '$0 --cleanup' to clean up."
    
    # Keep services running
    while true; do
        sleep 30
        # Basic health check
        if ! curl -s http://localhost:8080/health > /dev/null; then
            print_warning "Some services may have stopped"
        fi
    done
}

# Run main function with all arguments
main "$@"
