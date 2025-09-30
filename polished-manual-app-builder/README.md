# Polished Manual: AI-Driven Multi-Stack App Builder

🚀 **Production-ready AI-assisted app builder** with event sourcing, real-time collaboration, and multi-stack templates.

## ✨ Features

- **🧠 AI Orchestration**: Local-first with Ollama (Llama 3/Mistral), semantic caching
- **⚡ Event Sourcing**: High-throughput event store with snapshots and stream partitioning
- **🤝 Real-time Collaboration**: Yjs CRDT with presence and offline sync
- **🛡️ Validation Pipeline**: Syntax → lint → type → security → performance gates
- **🏗️ Multi-Stack Templates**: Next.js+Postgres, FastAPI+MongoDB, Rust Axum+Redis
- **🔧 Feature Flags**: Progressive rollouts with expiration and SDKs
- **📊 Observability**: OpenTelemetry, Jaeger, Prometheus, Grafana dashboards
- **🔒 Security & Compliance**: RBAC, audit logs, SAST, secrets management

## 🚀 Quick Start

```bash
# Clone and start infrastructure
git clone <repo-url>
cd polished-manual-app-builder
docker compose up -d

# Start development services
make dev

# Scaffold a new app
pnpm cli new my-saas --stack=nextjs-postgres --features=auth,ai --multi-tenant=shared-schema

# Run quality gates
make quality
```

## 📋 Available Commands

```bash
make dev        # Start development servers
make test       # Run all tests
make lint       # Run linters
make typecheck  # Type checking
make quality    # Run all quality gates
make ship       # Build and deploy
make preview    # Preview deployment
make logs       # View service logs
make doctor     # System health check
make clean      # Clean build artifacts
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Templates  │    │  Validation     │    │  Event Store    │
│                 │────│  Pipeline       │────│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│  Orchestrator   │──────────────┘
                        │                 │
                        └─────────────────┘
                                 │
                   ┌─────────────────┐    ┌─────────────────┐
                   │  Collab Engine  │    │  Feature Flags  │
                   │                 │    │                 │
                   └─────────────────┘    └─────────────────┘
```

## 🎯 Stack Templates

### Next.js + Postgres
- **Auth**: NextAuth.js with OAuth2/OIDC
- **Database**: Prisma ORM with migrations
- **Cache**: Redis with edge caching
- **Tests**: Vitest + Playwright

### FastAPI + MongoDB
- **Auth**: JWT/OIDC with Pydantic validation
- **Database**: Motor async driver with migrations
- **Cache**: Redis with async client
- **Tests**: pytest + httpx

### Rust Axum + Redis
- **Auth**: Tower middleware with JWT
- **Database**: sqlx with compile-time queries
- **Cache**: Redis with connection pooling
- **Tests**: tokio-test + reqwest

## 📊 Local Development URLs

After running `docker compose up -d`:

- **Jaeger UI**: http://localhost:16686
- **SigNoz**: http://localhost:3301
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Event Store**: http://localhost:8080
- **Orchestrator**: http://localhost:8001
- **Feature Flags**: http://localhost:8002

## 🔒 Security Features

- **Secrets Management**: Vault integration with local fallback
- **RBAC**: Role-based access control middleware
- **Audit Logs**: Structured logging for all write operations
- **SAST**: Semgrep, Bandit, cargo-audit in CI
- **Dependency Scanning**: npm audit, pip-audit, cargo-audit
- **Input Validation**: Strong typing and sanitization

## 📈 Trust Dashboard

Monitor key metrics in `docs/TRUST_DASHBOARD.md`:

- **Reliability**: CFR, MTTD, uptime SLA
- **Performance**: P95 latency, cache hit rates
- **Security**: Vulnerability count, SAST findings
- **Quality**: Test coverage, type safety score

## 🏢 Multi-Tenancy Support

Choose your data isolation pattern:

- **Shared Schema**: Single database, tenant_id column
- **Separate Schemas**: Schema per tenant in same database  
- **Database per Tenant**: Complete isolation

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and patterns
- [Security Checklist](docs/SECURITY_CHECKLIST.md) - Compliance guide
- [Trust Dashboard](docs/TRUST_DASHBOARD.md) - KPI monitoring
- [ADRs](docs/ADRs/) - Architecture decision records
- [Runbooks](docs/RUNBOOKS/) - Operational procedures

## 🧪 Demo

Run the complete demo:

```bash
./scripts/demo.sh
```

This will:
1. Start all services
2. Seed demo data
3. Show AI orchestration with cache hits
4. Demonstrate Yjs collaboration
5. Run validation pipeline
6. Display feature flag rollouts

## 📜 License

MIT License - see [LICENSE](LICENSE) file.

---

Built with ❤️ for Netflix/Google-level production teams.
