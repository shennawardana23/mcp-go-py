# MCP-PBA-TUNNEL Development Makefile

.PHONY: help install dev-install test test-cov lint format type-check clean docker-build docker-run pre-commit

# Default target
help:
	@echo "MCP-PBA-TUNNEL Development Commands"
	@echo "=================================="
	@echo ""
	@echo "Installation:"
	@echo "  install       Install in development mode"
	@echo "  dev-install   Install with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  dev           Start development server with hot reload"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run linter (ruff)"
	@echo "  format        Format code (ruff)"
	@echo "  type-check    Run type checking (mypy)"
	@echo "  pre-commit    Run all pre-commit checks"
	@echo ""
	@echo "Database:"
	@echo "  db-init       Initialize database"
	@echo "  db-migrate    Run database migrations"
	@echo "  db-reset      Reset database"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Run Docker container"
	@echo "  docker-dev    Run development container"
	@echo ""
	@echo "Documentation:"
	@echo "  docs-serve    Serve documentation locally"
	@echo "  docs-build    Build documentation"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean         Clean up cache files"
	@echo "  update-deps   Update dependencies"

# Installation
install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"
	pre-commit install

# Development
dev:
	uvicorn mcp_pba_tunnel.server.fastapi_mcp_server:create_app --reload --host 0.0.0.0 --port 9000

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=server --cov=data --cov-report=html --cov-report=term-missing

# Code Quality
lint:
	ruff check .

format:
	ruff format .
	ruff check . --fix

type-check:
	mypy mcp_pba_tunnel/ --ignore-missing-imports

pre-commit: lint type-check test

# Database
db-init:
	python -c "from mcp_pba_tunnel.data.project_manager import DatabaseManager; db = DatabaseManager('postgresql://postgres:password@localhost:5432/mcp_pba_tunnel'); print('✅ PostgreSQL database initialized')"

db-migrate:
	@echo "Run database migrations (if using Alembic)"
	# alembic upgrade head

db-reset:
	@echo "Reset database"
	# alembic downgrade base && alembic upgrade head

# Docker
docker-build:
	docker build -t mcp-pba-tunnel:latest .

docker-run:
	docker run -p 9001:9001 mcp-pba-tunnel:latest

docker-dev:
	docker run -p 9001:9001 -v $(PWD):/app mcp-pba-tunnel:latest

# Documentation
docs-serve:
	mkdocs serve

docs-build:
	mkdocs build

# Maintenance
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage coverage.xml htmlcov/
	rm -rf .pytest_cache/
	rm -rf dist/ build/
	rm -rf *.db

update-deps:
	pip list --outdated
	@echo "Update dependencies manually using:"
	@echo "  pip install -U package-name"

# Environment setup
setup-dev:
	@echo "Setting up development environment..."
	python -m venv venv
	@echo "Activate with: source venv/bin/activate"
	@echo "Then run: make dev-install"

# Health check
health:
	curl -f http://localhost:9001/health || echo "❌ Server not running"

# Test MCP protocol
test-mcp:
	curl -X POST http://localhost:9001/mcp/prompts/list \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": "test", "method": "prompts/list", "params": {}}'

# Production deployment
deploy-prod:
	@echo "🚀 Deploying to production..."
	gunicorn mcp_pba_tunnel.server.fastapi_mcp_server:create_app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:9001

# Development with environment variables
dev-env:
	@echo "Starting server with environment variables..."
	@echo "Make sure to set: DATABASE_URL, REDIS_URL, OPENAI_API_KEY, etc."
	uvicorn mcp_pba_tunnel.server.fastapi_mcp_server:create_app --reload --host 0.0.0.0 --port 9001

# Show logs
logs:
	@echo "Server logs:"
	tail -f logs/mcp_server.log 2>/dev/null || echo "No log file found. Start server first."

# Quick test
quick-test: format lint type-check test

# Full quality check
quality: clean quick-test
	@echo "✅ All quality checks passed!"

# Install development dependencies
install-dev-deps:
	pip install ruff mypy pytest pytest-asyncio pytest-cov bandit safety pre-commit

# Security check
security:
	bandit -r server/ data/ -f json -o bandit-report.json || true
	@echo "Security report generated: bandit-report.json"

# Performance profiling
profile:
	@echo "Run performance profiling..."
	@echo "Use: python -m cProfile -s time server/fastapi_mcp_server.py"

# Show project info
info:
	@echo "MCP-PBA-TUNNEL Project Information"
	@echo "=================================="
	@echo "Python version: $(shell python --version)"
	@echo "Project root: $(PWD)"
	@echo "Server location: mcp_pba_tunnel/server/fastapi_mcp_server.py"
	@echo "Database: PostgreSQL (required)"
	@echo "Tests: $(shell find tests/ -name "*.py" | wc -l) test files"
	@echo ""

# Default target when just running 'make'
.DEFAULT_GOAL := help
