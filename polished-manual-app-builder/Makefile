# Polished Manual App Builder - Makefile
# Production-ready AI-assisted app builder

.PHONY: help setup dev test lint typecheck quality ship preview logs doctor clean db-up db-down db-reset update

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[1;34m
GREEN := \033[1;32m
YELLOW := \033[1;33m
RED := \033[1;31m
NC := \033[0m # No Color

# Help
help: ## Show this help message
	@echo "$(BLUE)Polished Manual App Builder$(NC)"
	@echo "$(BLUE)=============================$(NC)"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Setup
setup: ## Initial setup for development
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)Error: Docker is required$(NC)"; exit 1; }
	@command -v pnpm >/dev/null 2>&1 || npm install -g pnpm
	@command -v cargo >/dev/null 2>&1 || { echo "$(RED)Error: Rust is required$(NC)"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)Error: Python 3.11+ is required$(NC)"; exit 1; }
	pnpm install
	@echo "$(GREEN)Setup complete!$(NC)"

# Development
dev: ## Start development servers
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker compose up -d
	@echo "$(YELLOW)Waiting for services to be healthy...$(NC)"
	@sleep 10
	pnpm run dev

# Testing
test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	pnpm run test
	@echo "$(GREEN)All tests passed!$(NC)"

test-coverage: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pnpm run test:coverage

# Code Quality
lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	pnpm run lint

lint-fix: ## Fix linting issues
	@echo "$(BLUE)Fixing linting issues...$(NC)"
	pnpm run lint:fix

typecheck: ## Run type checking
	@echo "$(BLUE)Running type checking...$(NC)"
	pnpm run typecheck

# Quality Gates
quality: ## Run all quality gates (lint + typecheck + test)
	@echo "$(BLUE)Running quality gates...$(NC)"
	@$(MAKE) lint
	@$(MAKE) typecheck
	@$(MAKE) test
	@echo "$(GREEN)All quality gates passed!$(NC)"

# Security
security-scan: ## Run security scans
	@echo "$(BLUE)Running security scans...$(NC)"
	@echo "$(YELLOW)Scanning Node.js dependencies...$(NC)"
	pnpm audit --audit-level moderate
	@echo "$(YELLOW)Scanning Python dependencies...$(NC)"
	@cd services/orchestrator && pip-audit
	@echo "$(YELLOW)Scanning Rust dependencies...$(NC)"
	@cd services/event-store && cargo audit
	@echo "$(GREEN)Security scan complete!$(NC)"

# Build and Deploy
build: ## Build all services
	@echo "$(BLUE)Building all services...$(NC)"
	pnpm run build
	docker compose build

ship: ## Build and deploy to production
	@echo "$(BLUE)Shipping to production...$(NC)"
	@$(MAKE) quality
	@$(MAKE) build
	docker compose up -d --build
	@echo "$(GREEN)Deployment complete!$(NC)"

preview: ## Preview deployment locally
	@echo "$(BLUE)Starting preview environment...$(NC)"
	docker compose -f docker-compose.yml up -d
	@echo "$(GREEN)Preview environment started!$(NC)"
	@echo "$(YELLOW)Access URLs:$(NC)"
	@echo "  • Main App: http://localhost:3001"
	@echo "  • Jaeger UI: http://localhost:16686"
	@echo "  • Prometheus: http://localhost:9090"
	@echo "  • Grafana: http://localhost:3000 (admin/admin)"

# Monitoring and Logs
logs: ## View service logs
	@echo "$(BLUE)Viewing service logs...$(NC)"
	docker compose logs -f

logs-service: ## View logs for specific service (usage: make logs-service SERVICE=orchestrator)
	@echo "$(BLUE)Viewing logs for $(SERVICE)...$(NC)"
	docker compose logs -f $(SERVICE)

# Database Management
db-up: ## Start database services only
	@echo "$(BLUE)Starting database services...$(NC)"
	docker compose up -d postgres redis mongodb

db-down: ## Stop database services
	@echo "$(BLUE)Stopping database services...$(NC)"
	docker compose stop postgres redis mongodb

db-reset: ## Reset all databases (WARNING: Data loss!)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	docker compose down -v
	docker volume prune -f
	@$(MAKE) db-up

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	@cd services/orchestrator && python -m alembic upgrade head
	@cd services/feature-flags && go run cmd/migrate/main.go

# Health and Diagnostics
doctor: ## Run system health checks
	@echo "$(BLUE)Running system health checks...$(NC)"
	@echo "$(YELLOW)Checking Docker...$(NC)"
	@docker --version
	@echo "$(YELLOW)Checking Node.js...$(NC)"
	@node --version
	@echo "$(YELLOW)Checking Python...$(NC)"
	@python3 --version
	@echo "$(YELLOW)Checking Rust...$(NC)"
	@rustc --version
	@echo "$(YELLOW)Checking pnpm...$(NC)"
	@pnpm --version
	@echo "$(YELLOW)Checking service health...$(NC)"
	@curl -f http://localhost:8080/health >/dev/null 2>&1 && echo "✓ Event Store: Healthy" || echo "✗ Event Store: Unhealthy"
	@curl -f http://localhost:8001/health >/dev/null 2>&1 && echo "✓ Orchestrator: Healthy" || echo "✗ Orchestrator: Unhealthy"
	@curl -f http://localhost:8002/health >/dev/null 2>&1 && echo "✓ Feature Flags: Healthy" || echo "✗ Feature Flags: Unhealthy"
	@curl -f http://localhost:8003/health >/dev/null 2>&1 && echo "✓ Collab Engine: Healthy" || echo "✗ Collab Engine: Unhealthy"
	@curl -f http://localhost:8004/health >/dev/null 2>&1 && echo "✓ Validation Pipeline: Healthy" || echo "✗ Validation Pipeline: Unhealthy"
	@echo "$(GREEN)Health check complete!$(NC)"

# Cleanup
clean: ## Clean build artifacts and containers
	@echo "$(BLUE)Cleaning up...$(NC)"
	pnpm run clean
	docker compose down --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-all: ## Clean everything including volumes and images
	@echo "$(RED)WARNING: This will remove all containers, volumes, and images!$(NC)"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	docker compose down -v --remove-orphans
	docker system prune -af --volumes
	@echo "$(GREEN)Complete cleanup finished!$(NC)"

# Updates
update: ## Update dependencies and tools
	@echo "$(BLUE)Updating dependencies...$(NC)"
	pnpm update --latest
	@cd services/orchestrator && pip install --upgrade -r requirements.txt
	@cd services/event-store && cargo update
	@echo "$(GREEN)Dependencies updated!$(NC)"

# Demo
demo: ## Run the complete demo
	@echo "$(BLUE)Starting complete demo...$(NC)"
	@$(MAKE) preview
	@echo "$(YELLOW)Waiting for services to start...$(NC)"
	@sleep 15
	@echo "$(YELLOW)Running demo script...$(NC)"
	@bash scripts/demo.sh
	@echo "$(GREEN)Demo complete!$(NC)"

# CLI Tools
cli-new: ## Create new project (usage: make cli-new PROJECT=my-app STACK=nextjs-postgres)
	@echo "$(BLUE)Creating new project: $(PROJECT)$(NC)"
	pnpm cli new $(PROJECT) --stack=$(STACK) --features=auth,ai --multi-tenant=shared-schema
