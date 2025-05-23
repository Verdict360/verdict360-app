#!/bin/bash

echo "🔧 VERDICT360 COMPLETE FIX SCRIPT"
echo "================================"

# 1. Stop all containers and clean up
echo "1. Cleaning up existing containers..."
docker-compose down --volumes
docker system prune -f

# 2. Restart with fixed configuration
echo "2. Starting services with fixed configuration..."
docker-compose up -d

# 3. Wait for PostgreSQL to be ready
echo "3. Waiting for PostgreSQL to start..."
sleep 10

# 4. Apply the simplified schema
echo "4. Setting up database schema..."
docker exec -i Verdict360-postgres psql -U Verdict360 -d Verdict360_legal < docker/postgres/init-scripts/01-schema-simple.sql
docker exec -i Verdict360-postgres psql -U Verdict360 -d Verdict360_legal < docker/postgres/init-scripts/02-seed-data-simple.sql

# 5. Wait for Keycloak to start
echo "5. Waiting for Keycloak to start..."
sleep 20

# 6. Test database connection
echo "6. Testing database..."
docker exec -it Verdict360-postgres psql -U Verdict360 -d Verdict360_legal -c "SELECT COUNT(*) as users FROM legal_users;"
docker exec -it Verdict360-postgres psql -U Verdict360 -d Verdict360_legal -c "SELECT COUNT(*) as matters FROM legal_matters;"
docker exec -it Verdict360-postgres psql -U Verdict360 -d Verdict360_legal -c "SELECT COUNT(*) as case_law FROM case_law_references;"

# 7. Set up MinIO
echo "7. Setting up MinIO..."
./scripts/setup-minio-fixed.sh

# 8. Test services
echo "8. Testing all services..."
echo "PostgreSQL:"
docker exec Verdict360-postgres pg_isready -U Verdict360 && echo "  ✅ PostgreSQL ready" || echo "  ❌ PostgreSQL not ready"

echo "Keycloak:"
curl -s -o /dev/null -w "  HTTP %{http_code}\n" http://localhost:8080 && echo "  ✅ Keycloak responding" || echo "  ❌ Keycloak not responding"

echo "MinIO:"
curl -s -o /dev/null -w "  HTTP %{http_code}\n" http://localhost:9000/minio/health/live && echo "  ✅ MinIO healthy" || echo "  ❌ MinIO not healthy"

# 9. Final status
echo ""
echo "🎯 FINAL STATUS:"
docker-compose ps

echo ""
echo "✅ SETUP COMPLETE!"
echo "Access points:"
echo "- Keycloak Admin: http://localhost:8080 (admin / check your .env file)"
echo "- MinIO Console: http://localhost:9001 (minioadmin / check your .env file)"
echo "- PostgreSQL: localhost:5432 (Verdict360 / check your .env file)"
