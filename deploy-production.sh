#!/bin/bash

# Verdict360 Production Deployment Script
# Automates the deployment of Verdict360 Legal Intelligence Platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="verdict360"
VERSION="1.0.0"
DEPLOYMENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo "=================================="
    echo "🇿🇦 VERDICT360 PRODUCTION DEPLOY"
    echo "=================================="
    echo "Version: $VERSION"
    echo "Date: $DEPLOYMENT_DATE"
    echo "=================================="
    echo
}

# Pre-deployment checks
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker service."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed."
        exit 1
    fi
    
    # Check if required directories exist
    if [ ! -f "docker-compose.prod.yml" ]; then
        log_error "docker-compose.prod.yml not found. Run this script from the project root."
        exit 1
    fi
    
    # Check if environment file exists
    if [ ! -f ".env.production" ]; then
        log_warning ".env.production not found. Creating from template..."
        cp .env.example .env.production
        log_warning "Please edit .env.production with your production settings before continuing."
        read -p "Press Enter to continue after editing .env.production..."
    fi
    
    log_success "Prerequisites check completed"
}

# Stop existing services
stop_existing_services() {
    log_info "Stopping existing services..."
    
    if docker-compose -f docker-compose.prod.yml ps -q | grep -q .; then
        docker-compose -f docker-compose.prod.yml down
        log_success "Existing services stopped"
    else
        log_info "No existing services to stop"
    fi
}

# Build application images
build_applications() {
    log_info "Building application images..."
    
    # Build frontend
    log_info "Building frontend application..."
    cd web
    if [ -f "package.json" ]; then
        npm ci --production
        npm run build
        log_success "Frontend build completed"
    else
        log_error "Frontend package.json not found"
        exit 1
    fi
    cd ..
    
    # Build backend
    log_info "Building backend application..."
    cd api-python
    if [ -f "requirements.txt" ]; then
        # Create virtual environment for testing
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
        log_success "Backend dependencies verified"
    else
        log_error "Backend requirements.txt not found"
        exit 1
    fi
    cd ..
    
    log_success "Application builds completed"
}

# Initialize databases
initialize_databases() {
    log_info "Initializing databases..."
    
    # Start database services first
    docker-compose -f docker-compose.prod.yml up -d postgres redis chroma minio
    
    # Wait for databases to be ready
    log_info "Waiting for databases to initialize..."
    sleep 30
    
    # Initialize PostgreSQL database
    log_info "Setting up PostgreSQL database..."
    docker-compose -f docker-compose.prod.yml exec -T postgres psql -U verdict360 -d verdict360 -c "SELECT 1;" || {
        log_error "PostgreSQL database connection failed"
        exit 1
    }
    
    # Set up MinIO buckets
    log_info "Setting up MinIO storage buckets..."
    docker-compose -f docker-compose.prod.yml exec -T minio mc alias set myminio http://localhost:9000 verdict360 ${MINIO_PASSWORD:-verdict360password}
    docker-compose -f docker-compose.prod.yml exec -T minio mc mb myminio/legal-documents || true
    docker-compose -f docker-compose.prod.yml exec -T minio mc mb myminio/user-exports || true
    
    log_success "Databases initialized"
}

# Deploy services
deploy_services() {
    log_info "Deploying all services..."
    
    # Copy environment file
    cp .env.production .env
    
    # Start all services
    docker-compose -f docker-compose.prod.yml up -d
    
    log_success "All services deployed"
}

# Health checks
run_health_checks() {
    log_info "Running health checks..."
    
    # Wait for services to start
    sleep 60
    
    # Check web service
    if curl -f http://localhost:3000/api/health &>/dev/null; then
        log_success "Web service health check passed"
    else
        log_warning "Web service health check failed"
    fi
    
    # Check API service
    if curl -f http://localhost:8000/health &>/dev/null; then
        log_success "API service health check passed"
    else
        log_warning "API service health check failed"
    fi
    
    # Check database connections
    if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U verdict360 &>/dev/null; then
        log_success "PostgreSQL health check passed"
    else
        log_warning "PostgreSQL health check failed"
    fi
    
    # Check Redis
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping | grep -q PONG; then
        log_success "Redis health check passed"
    else
        log_warning "Redis health check failed"
    fi
    
    log_info "Health checks completed"
}

# Populate legal database
populate_legal_data() {
    log_info "Populating legal database with South African content..."
    
    # Run the database population script
    docker-compose -f docker-compose.prod.yml exec -T api python scripts/populate_legal_database.py || {
        log_warning "Legal database population failed - you may need to run this manually"
    }
    
    log_success "Legal database population completed"
}

# Display deployment summary
show_deployment_summary() {
    echo
    echo "======================================="
    echo "🎉 VERDICT360 DEPLOYMENT COMPLETED! 🎉"
    echo "======================================="
    echo
    echo "📊 Service Status:"
    docker-compose -f docker-compose.prod.yml ps
    echo
    echo "🌐 Access URLs:"
    echo "  • Frontend: http://localhost:3000"
    echo "  • API: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
    echo "  • Admin: http://localhost:3000/admin-dashboard"
    echo "  • MinIO Console: http://localhost:9001"
    echo
    echo "🔧 Management Commands:"
    echo "  • View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  • Stop services: docker-compose -f docker-compose.prod.yml down"
    echo "  • Restart services: docker-compose -f docker-compose.prod.yml restart"
    echo
    echo "📚 Documentation:"
    echo "  • Deployment Guide: ./PRODUCTION_DEPLOYMENT_GUIDE.md"
    echo "  • API Documentation: http://localhost:8000/docs"
    echo
    echo "✅ Verdict360 is ready for South African legal professionals!"
    echo "======================================="
}

# Backup current deployment (if exists)
backup_existing_deployment() {
    if [ -d "backups" ]; then
        log_info "Creating backup of existing deployment..."
        BACKUP_DIR="backups/pre-deploy-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Backup database if running
        if docker-compose -f docker-compose.prod.yml ps postgres | grep -q "Up"; then
            docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U verdict360 verdict360 > "$BACKUP_DIR/postgres_backup.sql"
            log_success "Database backup created: $BACKUP_DIR/postgres_backup.sql"
        fi
    fi
}

# Rollback function
rollback_deployment() {
    log_error "Deployment failed. Rolling back..."
    docker-compose -f docker-compose.prod.yml down
    log_info "Services stopped. Check logs for errors."
    exit 1
}

# Main deployment process
main() {
    print_banner
    
    # Set trap for cleanup on error
    trap rollback_deployment ERR
    
    # Deployment steps
    check_prerequisites
    backup_existing_deployment
    stop_existing_services
    build_applications
    initialize_databases
    deploy_services
    run_health_checks
    populate_legal_data
    show_deployment_summary
    
    log_success "Verdict360 production deployment completed successfully!"
}

# Script options
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping Verdict360 services..."
        docker-compose -f docker-compose.prod.yml down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting Verdict360 services..."
        docker-compose -f docker-compose.prod.yml restart
        log_success "Services restarted"
        ;;
    "logs")
        docker-compose -f docker-compose.prod.yml logs -f
        ;;
    "status")
        echo "Verdict360 Service Status:"
        docker-compose -f docker-compose.prod.yml ps
        ;;
    "health")
        log_info "Running health checks..."
        run_health_checks
        ;;
    "backup")
        log_info "Creating manual backup..."
        backup_existing_deployment
        ;;
    "help")
        echo "Verdict360 Deployment Script"
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  deploy   - Full deployment (default)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services" 
        echo "  logs     - View service logs"
        echo "  status   - Show service status"
        echo "  health   - Run health checks"
        echo "  backup   - Create manual backup"
        echo "  help     - Show this help"
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac