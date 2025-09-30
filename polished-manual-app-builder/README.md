# Rapidapp - Polished Manual App Builder

A sophisticated development platform for building modern applications with real-time collaboration, event sourcing, and comprehensive observability.

## 🚀 Quick Start

### One-Command Setup

```bash
# Clone the repository
git clone <repository-url>
cd polished-manual-app-builder

# Run the automated setup script
./setup.sh
```

The setup script will automatically:
- Install all required dependencies (Docker, Node.js 20+, pnpm, Rust, Python)
- Start infrastructure services (PostgreSQL, Redis, MongoDB, Grafana, Jaeger, Prometheus)
- Install project dependencies
- Create environment configuration files
- Verify all services are running

### Manual Setup (if needed)

If you prefer to set up manually or troubleshoot issues:

1. **Prerequisites:**
   - Docker & Docker Compose
   - Node.js 20+
   - pnpm
   - Rust 1.70+
   - Python 3.11+

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Start infrastructure:**
   ```bash
   make infra
   ```

4. **Start development services:**
   ```bash
   make dev
   ```

## 🏗️ Architecture

### Services

- **Event Store** (Rust): High-performance event sourcing with CQRS
- **Collaboration Engine** (Node.js): Real-time collaboration with Yjs CRDT
- **Orchestrator** (Python): Workflow orchestration and business logic

### Infrastructure

- **PostgreSQL**: Primary database for each service
- **Redis**: Caching and pub/sub messaging
- **MongoDB**: Document storage for orchestrator
- **Grafana**: Observability dashboards
- **Jaeger**: Distributed tracing
- **Prometheus**: Metrics collection

## 🔧 Development

### Available Commands

```bash
make help              # Show all available commands
make dev               # Start all development services
make dev-collab        # Start collaboration engine only
make dev-event         # Start event store only
make dev-orchestrator  # Start orchestrator only
make test              # Run all tests
make quality           # Run linting and type checks
make clean             # Stop all services and clean up
```

### Creating New Applications

Use the CLI tool to scaffold new applications:

```bash
pnpm cli new my-app
```

### Environment Configuration

Each service has its own `.env` file with sensible defaults:
- `services/event-store/.env`
- `services/collab-engine/.env`
- `services/orchestrator/.env`

## 📊 Monitoring & Observability

Access your monitoring stack:

- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger**: http://localhost:16686
- **Prometheus**: http://localhost:9090

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific service tests
cd services/collab-engine && pnpm test
cd services/event-store && cargo test
cd services/orchestrator && python -m pytest
```

## 📖 Documentation

- [Error Monitoring Setup](docs/ERROR_MONITORING_README.md)
- [Error Prevention Guide](docs/ERROR_PREVENTION_GUIDE.md)
- [Error System Integration](docs/ERROR_SYSTEM_INTEGRATION.md)

## 🐛 Troubleshooting

### Common Issues

1. **Docker permission denied**:
   ```bash
   sudo usermod -aG docker $USER
   # Log out and log back in
   ```

2. **Port conflicts**:
   ```bash
   make clean  # Stop all services
   docker ps   # Check for conflicting containers
   ```

3. **Node.js version issues**:
   ```bash
   node --version  # Should be 20+
   # Install Node.js 20+ if needed
   ```

4. **Service health checks**:
   ```bash
   make status  # Check service health
   docker-compose logs <service-name>  # Check logs
   ```

### Getting Help

- Check service logs: `docker-compose logs <service-name>`
- Verify service health: `make status`
- Reset environment: `make clean && ./setup.sh`

## � Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks: `make quality`
5. Submit a pull request

## � License

See [LICENSE](LICENSE) file for details.
