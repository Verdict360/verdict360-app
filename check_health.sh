#!/bin/bash
echo "🏥 VERDICT360 HEALTH CHECK"
echo "========================="
echo ""

# Check if services are running
echo "🐳 Docker Services:"
docker-compose ps 2>/dev/null | grep -E "(postgres|keycloak|minio)" || echo "❌ Docker services not running"

echo ""
echo "🌐 API Health:"
curl -s http://localhost:8001/health 2>/dev/null | grep -o '"status":"[^"]*"' || echo "❌ Python API not responding"

echo ""
echo "📦 MinIO Status:"
curl -s http://localhost:9000/minio/health/live 2>/dev/null && echo "✅ MinIO healthy" || echo "❌ MinIO not responding"

echo ""
echo "🔑 Keycloak Status:"
curl -s http://localhost:8080 2>/dev/null > /dev/null && echo "✅ Keycloak responding" || echo "❌ Keycloak not responding"
