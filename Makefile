# Makefile untuk QR Scanner Backend

.PHONY: help dev prod build stop clean logs db test

# Default target
help:
	@echo "QR Scanner Backend - Docker Commands"
	@echo "===================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make dev     - Start development environment"
	@echo "  make prod    - Start production environment"
	@echo "  make build   - Build Docker images"
	@echo "  make stop    - Stop all containers"
	@echo "  make clean   - Clean containers and volumes"
	@echo "  make logs    - Show application logs"
	@echo "  make db      - Access database shell"
	@echo "  make test    - Run tests"
	@echo ""

# Development environment
dev:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up --build -d
	@echo "✅ Development started at http://localhost:5001"

# Production environment
prod:
	@echo "🚀 Starting production environment..."
	@if [ ! -f .env ]; then \
		echo "⚠️  Creating .env from template..."; \
		cp .env.docker .env; \
		echo "📝 Please edit .env file before running again"; \
		exit 1; \
	fi
	docker-compose up --build -d
	@echo "✅ Production started at http://localhost:5000"

# Build images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build --no-cache
	docker-compose -f docker-compose.dev.yml build --no-cache

# Stop containers
stop:
	@echo "🛑 Stopping containers..."
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Clean everything
clean:
	@echo "🧹 Cleaning containers and volumes..."
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f

# Show logs
logs:
	@if docker ps | grep -q qr_scanner_app_dev; then \
		docker-compose -f docker-compose.dev.yml logs -f app; \
	elif docker ps | grep -q qr_scanner_app; then \
		docker-compose logs -f app; \
	else \
		echo "❌ No running containers found"; \
	fi

# Database access
db:
	@if docker ps | grep -q qr_scanner_db_dev; then \
		docker exec -it qr_scanner_db_dev psql -U postgres -d aski_scan_dev; \
	elif docker ps | grep -q qr_scanner_db; then \
		docker exec -it qr_scanner_db psql -U postgres -d aski_scan; \
	else \
		echo "❌ No database container found"; \
	fi

# Run tests
test:
	@if docker ps | grep -q qr_scanner_app_dev; then \
		docker exec qr_scanner_app_dev python test_api.py; \
	elif docker ps | grep -q qr_scanner_app; then \
		docker exec qr_scanner_app python test_api.py; \
	else \
		echo "❌ No application container found. Start with 'make dev' first"; \
	fi

# Install Docker (macOS)
install-docker:
	@echo "📦 Installing Docker Desktop for macOS..."
	@if ! command -v docker &> /dev/null; then \
		echo "Please download and install Docker Desktop from:"; \
		echo "https://www.docker.com/products/docker-desktop"; \
	else \
		echo "✅ Docker is already installed"; \
	fi