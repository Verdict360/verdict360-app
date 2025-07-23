#!/bin/bash

echo "🚀 Starting Legal Chatbot Platform Development Environment"
echo "=========================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual values"
fi

# Start all services
echo "📦 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 15

# Check service health
echo "🔍 Checking service health..."

# PostgreSQL
if docker-compose exec -T postgres pg_isready -U Verdict360 > /dev/null 2>&1; then
    echo "- PostgreSQL: ✅ Ready"
else
    echo "- PostgreSQL: ❌ Not ready"
fi

# FastAPI
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "- FastAPI Backend: ✅ Ready"
else
    echo "- FastAPI Backend: ❌ Not ready (may still be starting)"
fi

# Keycloak
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "- Keycloak: ✅ Ready"
else
    echo "- Keycloak: ❌ Not ready (may still be starting)"
fi

# Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "- Redis: ✅ Ready"
else
    echo "- Redis: ❌ Not ready"
fi

# MinIO
if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo "- MinIO: ✅ Ready"
else
    echo "- MinIO: ❌ Not ready"
fi

echo ""
echo "🎯 Access URLs:"
echo "- Legal Chatbot Frontend: http://localhost:5173"
echo "- FastAPI Backend: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
echo "- Keycloak Admin: http://localhost:8080 (admin/admin)"
echo "- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo "- N8N Workflows: http://localhost:5678 (admin/admin123)"
echo ""
echo "📝 Logs:"
echo "- View all logs: docker-compose logs -f"
echo "- View backend logs: docker-compose logs -f api-python"
echo "- View frontend logs: docker-compose logs -f web"
echo ""
echo "✅ Development environment ready!"
echo "📖 Check PROJECT_STRUCTURE.md for architecture details"