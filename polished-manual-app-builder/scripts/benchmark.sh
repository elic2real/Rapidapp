#!/bin/bash

# Polished Manual App Builder - Benchmarking Script
# Comprehensive performance testing and benchmarking

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

# Global variables for results
declare -A BENCHMARK_RESULTS

# Function to record benchmark result
record_result() {
    local test_name=$1
    local result=$2
    BENCHMARK_RESULTS["$test_name"]=$result
    echo "$test_name: $result" >> "benchmark_results_$(date +%Y%m%d_%H%M%S).txt"
}

# Check if services are running
check_services() {
    print_info "Checking if services are running..."
    
    local services=(
        "Event Store:http://localhost:8080/health"
        "AI Orchestrator:http://localhost:8001/health"
        "Collaboration Engine:http://localhost:8003/health"
    )
    
    for service in "${services[@]}"; do
        local name=$(echo "$service" | cut -d: -f1)
        local url=$(echo "$service" | cut -d: -f2-)
        
        if curl -s "$url" > /dev/null 2>&1; then
            print_status "$name is running"
        else
            print_error "$name is not running. Start services first."
            exit 1
        fi
    done
}

# Benchmark event store performance
benchmark_event_store() {
    print_info "Benchmarking Event Store performance..."
    
    local stream_id="benchmark-$(date +%s)"
    local num_events=1000
    local concurrent_clients=10
    
    # Single-threaded append performance
    print_info "Testing single-threaded event append..."
    local start_time=$(date +%s.%N)
    
    for i in $(seq 1 $num_events); do
        curl -s -X POST "http://localhost:8080/events" \
            -H "Content-Type: application/json" \
            -d "{
                \"stream_id\": \"${stream_id}-single\",
                \"event_type\": \"benchmark_event\",
                \"data\": {\"counter\": $i, \"payload\": \"$(head -c 100 < /dev/zero | tr '\\0' 'a')\"}
            }" > /dev/null
    done
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    local throughput=$(echo "scale=2; $num_events / $duration" | bc)
    
    print_status "Single-threaded: $throughput events/sec"
    record_result "event_store_single_threaded" "${throughput} events/sec"
    
    # Multi-threaded append performance
    print_info "Testing multi-threaded event append..."
    local events_per_client=$((num_events / concurrent_clients))
    
    start_time=$(date +%s.%N)
    
    for client in $(seq 1 $concurrent_clients); do
        {
            for i in $(seq 1 $events_per_client); do
                curl -s -X POST "http://localhost:8080/events" \
                    -H "Content-Type: application/json" \
                    -d "{
                        \"stream_id\": \"${stream_id}-multi-${client}\",
                        \"event_type\": \"benchmark_event\",
                        \"data\": {\"client\": $client, \"counter\": $i}
                    }" > /dev/null
            done
        } &
    done
    wait
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    throughput=$(echo "scale=2; $num_events / $duration" | bc)
    
    print_status "Multi-threaded ($concurrent_clients clients): $throughput events/sec"
    record_result "event_store_multi_threaded" "${throughput} events/sec"
    
    # Read performance
    print_info "Testing event read performance..."
    start_time=$(date +%s.%N)
    
    for client in $(seq 1 $concurrent_clients); do
        curl -s "http://localhost:8080/streams/${stream_id}-multi-${client}/events" > /dev/null &
    done
    wait
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    read_throughput=$(echo "scale=2; $concurrent_clients / $duration" | bc)
    
    print_status "Read performance: $read_throughput streams/sec"
    record_result "event_store_read" "${read_throughput} streams/sec"
}

# Benchmark AI orchestration
benchmark_ai_orchestration() {
    print_info "Benchmarking AI Orchestration performance..."
    
    # Test semantic cache performance
    print_info "Testing semantic cache performance..."
    local cache_requests=100
    local start_time=$(date +%s.%N)
    
    # First, populate cache with some entries
    for i in $(seq 1 10); do
        curl -s -X POST "http://localhost:8001/v1/completions" \
            -H "Content-Type: application/json" \
            -d "{\"prompt\": \"Test prompt $i for caching\", \"model\": \"test\"}" > /dev/null
    done
    
    # Test cache hit performance
    for i in $(seq 1 $cache_requests); do
        local prompt_num=$((i % 10 + 1))
        curl -s -X POST "http://localhost:8001/v1/completions" \
            -H "Content-Type: application/json" \
            -d "{\"prompt\": \"Test prompt $prompt_num for caching\", \"model\": \"test\"}" > /dev/null &
        
        # Limit concurrent requests
        if (( i % 20 == 0 )); then
            wait
        fi
    done
    wait
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    local cache_throughput=$(echo "scale=2; $cache_requests / $duration" | bc)
    
    print_status "Semantic cache: $cache_throughput requests/sec"
    record_result "ai_semantic_cache" "${cache_throughput} requests/sec"
    
    # Test model routing latency
    print_info "Testing model routing latency..."
    local routing_tests=50
    local total_latency=0
    
    for i in $(seq 1 $routing_tests); do
        local start_request=$(date +%s.%N)
        curl -s -X POST "http://localhost:8001/v1/completions" \
            -H "Content-Type: application/json" \
            -d "{\"prompt\": \"Quick test $i\", \"model\": \"test\"}" > /dev/null
        local end_request=$(date +%s.%N)
        
        local request_latency=$(echo "$end_request - $start_request" | bc)
        total_latency=$(echo "$total_latency + $request_latency" | bc)
    done
    
    local avg_latency=$(echo "scale=3; $total_latency / $routing_tests" | bc)
    local avg_latency_ms=$(echo "scale=1; $avg_latency * 1000" | bc)
    
    print_status "Average routing latency: ${avg_latency_ms}ms"
    record_result "ai_routing_latency" "${avg_latency_ms}ms"
}

# Benchmark collaboration engine
benchmark_collaboration() {
    print_info "Benchmarking Collaboration Engine performance..."
    
    # Test WebSocket connection handling
    print_info "Testing WebSocket connection capacity..."
    
    # This would require a WebSocket client, simplified version
    local connections_test=20
    local start_time=$(date +%s.%N)
    
    for i in $(seq 1 $connections_test); do
        curl -s "http://localhost:8003/rooms" > /dev/null &
    done
    wait
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    local connection_throughput=$(echo "scale=2; $connections_test / $duration" | bc)
    
    print_status "Connection handling: $connection_throughput connections/sec"
    record_result "collab_connections" "${connection_throughput} connections/sec"
    
    # Test room operations
    print_info "Testing room operations performance..."
    local room_ops=100
    start_time=$(date +%s.%N)
    
    for i in $(seq 1 $room_ops); do
        # Create and query rooms
        curl -s -X POST "http://localhost:8003/rooms" \
            -H "Content-Type: application/json" \
            -d "{\"name\": \"benchmark-room-$i\"}" > /dev/null &
        
        if (( i % 10 == 0 )); then
            wait
        fi
    done
    wait
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    local room_throughput=$(echo "scale=2; $room_ops / $duration" | bc)
    
    print_status "Room operations: $room_throughput ops/sec"
    record_result "collab_room_ops" "${room_throughput} ops/sec"
}

# Memory usage benchmark
benchmark_memory_usage() {
    print_info "Analyzing memory usage..."
    
    # Get memory usage for each service
    local services=("event-store" "orchestrator" "collab-engine")
    
    for service in "${services[@]}"; do
        local container_name="polished-manual-app-builder-${service}-1"
        
        if docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}" | grep -q "$container_name"; then
            local mem_usage=$(docker stats --no-stream --format "{{.MemUsage}}" "$container_name" | head -1)
            print_status "$service memory: $mem_usage"
            record_result "${service}_memory" "$mem_usage"
        else
            print_warning "Container $container_name not found"
        fi
    done
}

# CPU usage benchmark
benchmark_cpu_usage() {
    print_info "Analyzing CPU usage during load..."
    
    # Start monitoring CPU usage
    local monitor_duration=30
    print_info "Monitoring CPU usage for ${monitor_duration}s during load test..."
    
    # Start load generation in background
    {
        for i in $(seq 1 200); do
            curl -s -X POST "http://localhost:8080/events" \
                -H "Content-Type: application/json" \
                -d "{\"stream_id\": \"cpu-test\", \"event_type\": \"load_test\", \"data\": {\"i\": $i}}" > /dev/null &
            
            curl -s -X POST "http://localhost:8001/v1/completions" \
                -H "Content-Type: application/json" \
                -d "{\"prompt\": \"CPU test $i\", \"model\": \"test\"}" > /dev/null &
            
            if (( i % 10 == 0 )); then
                wait
                sleep 0.1
            fi
        done
        wait
    } &
    
    local load_pid=$!
    
    # Monitor CPU for the duration
    local services=("event-store" "orchestrator" "collab-engine")
    sleep 5  # Let load stabilize
    
    for service in "${services[@]}"; do
        local container_name="polished-manual-app-builder-${service}-1"
        
        if docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}" | grep -q "$container_name"; then
            local cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" "$container_name" | head -1)
            print_status "$service CPU under load: $cpu_usage"
            record_result "${service}_cpu_load" "$cpu_usage"
        fi
    done
    
    # Wait for load test to complete
    wait $load_pid
    print_status "Load test completed"
}

# Latency percentile analysis
benchmark_latency_percentiles() {
    print_info "Analyzing latency percentiles..."
    
    local test_requests=1000
    local latency_file="/tmp/latencies_$(date +%s).txt"
    
    print_info "Collecting $test_requests latency samples..."
    
    > "$latency_file"  # Clear file
    
    for i in $(seq 1 $test_requests); do
        local start_time=$(date +%s.%N)
        curl -s -X POST "http://localhost:8080/events" \
            -H "Content-Type: application/json" \
            -d "{\"stream_id\": \"latency-test\", \"event_type\": \"latency_test\", \"data\": {\"i\": $i}}" > /dev/null
        local end_time=$(date +%s.%N)
        
        local latency=$(echo "($end_time - $start_time) * 1000" | bc)
        echo "$latency" >> "$latency_file"
        
        if (( i % 100 == 0 )); then
            echo "Collected $i samples..."
        fi
    done
    
    # Calculate percentiles
    sort -n "$latency_file" > "${latency_file}.sorted"
    
    local p50_line=$((test_requests * 50 / 100))
    local p95_line=$((test_requests * 95 / 100))
    local p99_line=$((test_requests * 99 / 100))
    
    local p50=$(sed -n "${p50_line}p" "${latency_file}.sorted")
    local p95=$(sed -n "${p95_line}p" "${latency_file}.sorted")
    local p99=$(sed -n "${p99_line}p" "${latency_file}.sorted")
    
    print_status "Latency P50: ${p50}ms"
    print_status "Latency P95: ${p95}ms"
    print_status "Latency P99: ${p99}ms"
    
    record_result "latency_p50" "${p50}ms"
    record_result "latency_p95" "${p95}ms"
    record_result "latency_p99" "${p99}ms"
    
    # Cleanup
    rm -f "$latency_file" "${latency_file}.sorted"
}

# Generate benchmark report
generate_report() {
    print_info "Generating benchmark report..."
    
    local report_file="benchmark_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Polished Manual App Builder - Benchmark Report

**Generated:** $(date)
**Environment:** $(uname -a)
**Docker Version:** $(docker --version)

## Performance Summary

### Event Store Performance
- **Single-threaded throughput:** ${BENCHMARK_RESULTS["event_store_single_threaded"]:-"N/A"}
- **Multi-threaded throughput:** ${BENCHMARK_RESULTS["event_store_multi_threaded"]:-"N/A"}
- **Read throughput:** ${BENCHMARK_RESULTS["event_store_read"]:-"N/A"}

### AI Orchestration Performance
- **Semantic cache throughput:** ${BENCHMARK_RESULTS["ai_semantic_cache"]:-"N/A"}
- **Routing latency:** ${BENCHMARK_RESULTS["ai_routing_latency"]:-"N/A"}

### Collaboration Engine Performance
- **Connection handling:** ${BENCHMARK_RESULTS["collab_connections"]:-"N/A"}
- **Room operations:** ${BENCHMARK_RESULTS["collab_room_ops"]:-"N/A"}

### Resource Usage
- **Event Store memory:** ${BENCHMARK_RESULTS["event-store_memory"]:-"N/A"}
- **AI Orchestrator memory:** ${BENCHMARK_RESULTS["orchestrator_memory"]:-"N/A"}
- **Collaboration Engine memory:** ${BENCHMARK_RESULTS["collab-engine_memory"]:-"N/A"}

### Latency Analysis
- **P50 Latency:** ${BENCHMARK_RESULTS["latency_p50"]:-"N/A"}
- **P95 Latency:** ${BENCHMARK_RESULTS["latency_p95"]:-"N/A"}
- **P99 Latency:** ${BENCHMARK_RESULTS["latency_p99"]:-"N/A"}

## Recommendations

Based on the benchmark results:

1. **Event Store:** Target >10,000 events/sec for production workloads
2. **AI Orchestration:** Semantic cache should handle >100 requests/sec
3. **Memory Usage:** Monitor for growth under sustained load
4. **Latency:** P95 should be <100ms for good user experience

## Notes

- Tests run against local Docker environment
- Production performance may vary based on hardware and network
- Consider load testing with realistic data volumes
- Monitor resource usage during peak traffic

EOF

    print_status "Benchmark report saved to: $report_file"
}

# Quick benchmark (subset of tests)
quick_benchmark() {
    print_info "Running quick benchmark..."
    
    benchmark_event_store
    benchmark_ai_orchestration
    benchmark_memory_usage
    
    print_status "Quick benchmark completed"
}

# Full benchmark suite
full_benchmark() {
    print_info "Running full benchmark suite..."
    
    benchmark_event_store
    benchmark_ai_orchestration
    benchmark_collaboration
    benchmark_memory_usage
    benchmark_cpu_usage
    benchmark_latency_percentiles
    
    generate_report
    print_status "Full benchmark completed"
}

# Show help
show_help() {
    echo "Polished Manual App Builder - Benchmark Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  quick        Run quick benchmark (essential tests)"
    echo "  full         Run full benchmark suite"
    echo "  event-store  Benchmark event store only"
    echo "  ai           Benchmark AI orchestration only"
    echo "  collab       Benchmark collaboration engine only"
    echo "  memory       Check memory usage"
    echo "  cpu          Check CPU usage under load"
    echo "  latency      Analyze latency percentiles"
    echo "  help         Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 quick       # Quick performance check"
    echo "  $0 full        # Comprehensive benchmark"
    echo "  $0 event-store # Test event store performance"
}

# Main function
main() {
    local command=${1:-quick}
    
    echo "🔥 Polished Manual App Builder - Benchmarking"
    echo "=============================================="
    
    check_services
    
    case $command in
        quick)
            quick_benchmark
            ;;
        full)
            full_benchmark
            ;;
        event-store)
            benchmark_event_store
            ;;
        ai)
            benchmark_ai_orchestration
            ;;
        collab)
            benchmark_collaboration
            ;;
        memory)
            benchmark_memory_usage
            ;;
        cpu)
            benchmark_cpu_usage
            ;;
        latency)
            benchmark_latency_percentiles
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
    
    print_status "Benchmark completed successfully!"
}

# Run with all arguments
main "$@"
