#!/bin/bash

echo "🎯 VERDICT360 SYSTEM STATUS"
echo "=========================="
echo ""

echo "📦 DOCKER CONTAINERS:"
docker-compose ps

echo ""
echo "🗄️  DATABASE STATUS:"
docker exec Verdict360-postgres psql -U Verdict360 -d Verdict360_legal -c "SELECT COUNT(*) as total_users FROM legal_users;" 2>/dev/null || echo "❌ Database connection failed"

echo ""
echo "�� KEYCLOAK STATUS:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8080 2>/dev/null || echo "❌ Keycloak not accessible"

echo ""
echo "📁 MINIO STATUS:"  
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:9000/minio/health/live 2>/dev/null || echo "❌ MinIO not accessible"

echo ""
echo "💾 BACKUP SYSTEM:"
if [ -d "backups" ]; then
    echo "✅ Backup directory exists"
    echo "Recent backups:"
    find backups -name "*.gz" -o -name "*.sql" | head -5 | xargs ls -la 2>/dev/null || echo "No recent backups found"
else
    echo "❌ Backup system not initialized"
fi

echo ""
echo "🔧 NEXT STEPS:"
echo "- Access Keycloak: http://localhost:8080"
echo "- Access MinIO: http://localhost:9001"  
echo "- Run backup test: ./scripts/backup/full-backup.sh"
echo "- Start Week 2 development tasks"
