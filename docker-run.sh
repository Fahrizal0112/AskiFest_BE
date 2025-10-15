#!/bin/bash

# Script untuk menjalankan aplikasi dengan Docker

set -e

echo "🐳 QR Scanner Docker Setup"
echo "=========================="

# Function untuk menampilkan help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev      - Jalankan dalam mode development"
    echo "  prod     - Jalankan dalam mode production"
    echo "  build    - Build ulang images"
    echo "  stop     - Stop semua containers"
    echo "  clean    - Stop dan hapus containers + volumes"
    echo "  logs     - Lihat logs aplikasi"
    echo "  db       - Akses database PostgreSQL"
    echo "  test     - Jalankan tests"
    echo "  help     - Tampilkan help ini"
    echo ""
}

# Function untuk development
run_dev() {
    echo "🚀 Starting development environment..."
    docker-compose -f docker-compose.dev.yml up --build -d
    echo "✅ Development environment started!"
    echo "📱 API: http://localhost:5001"
    echo "🗄️  Database: localhost:5433"
    echo ""
    echo "📋 Useful commands:"
    echo "  ./docker-run.sh logs  - View logs"
    echo "  ./docker-run.sh stop  - Stop containers"
}

# Function untuk production
run_prod() {
    echo "🚀 Starting production environment..."
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        echo "⚠️  .env file not found. Creating from template..."
        cp .env.example .env
        echo "📝 Please edit .env file with your production settings"
        return 1
    fi
    
    docker-compose up --build -d
    echo "✅ Production environment started!"
    echo "📱 API: http://localhost:5000"
    echo "🌐 Nginx: http://localhost:80"
    echo "🗄️  Database: localhost:5432"
}

# Function untuk build
build_images() {
    echo "🔨 Building Docker images..."
    docker-compose build --no-cache
    echo "✅ Images built successfully!"
}

# Function untuk stop
stop_containers() {
    echo "🛑 Stopping containers..."
    docker-compose -f docker-compose.yml down
    docker-compose -f docker-compose.dev.yml down
    echo "✅ Containers stopped!"
}

# Function untuk clean
clean_all() {
    echo "🧹 Cleaning up containers and volumes..."
    docker-compose -f docker-compose.yml down -v --remove-orphans
    docker-compose -f docker-compose.dev.yml down -v --remove-orphans
    docker system prune -f
    echo "✅ Cleanup completed!"
}

# Function untuk logs
show_logs() {
    echo "📋 Showing application logs..."
    if docker ps | grep -q "qr_scanner_app_dev"; then
        docker-compose -f docker-compose.dev.yml logs -f app
    elif docker ps | grep -q "qr_scanner_app"; then
        docker-compose logs -f app
    else
        echo "❌ No running containers found"
    fi
}

# Function untuk database access
access_db() {
    echo "🗄️  Accessing database..."
    if docker ps | grep -q "qr_scanner_db_dev"; then
        docker exec -it qr_scanner_db_dev psql -U postgres -d aski_scan_dev
    elif docker ps | grep -q "qr_scanner_db"; then
        docker exec -it qr_scanner_db psql -U postgres -d aski_scan
    else
        echo "❌ No database container found"
    fi
}

# Function untuk testing
run_tests() {
    echo "🧪 Running tests..."
    if docker ps | grep -q "qr_scanner_app_dev"; then
        docker exec qr_scanner_app_dev python test_api.py
    elif docker ps | grep -q "qr_scanner_app"; then
        docker exec qr_scanner_app python test_api.py
    else
        echo "❌ No application container found"
        echo "💡 Start the application first with: ./docker-run.sh dev"
    fi
}

# Main script logic
case "${1:-help}" in
    "dev")
        run_dev
        ;;
    "prod")
        run_prod
        ;;
    "build")
        build_images
        ;;
    "stop")
        stop_containers
        ;;
    "clean")
        clean_all
        ;;
    "logs")
        show_logs
        ;;
    "db")
        access_db
        ;;
    "test")
        run_tests
        ;;
    "help"|*)
        show_help
        ;;
esac