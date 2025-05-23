#!/bin/bash

echo "🔧 Fixing Week 1 Setup Issues..."

# 1. Restart services cleanly
echo "1. Restarting Docker services..."
docker-compose down
docker-compose up -d
sleep 15

# 2. Initialize database properly
echo "2. Setting up database schema..."
docker exec -i Verdict360-postgres psql -U Verdict360 -d Verdict360_legal -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker exec -i Verdict360-postgres psql -U Verdict360 -d Verdict360_legal < docker/postgres/init-scripts/01-schema.sql
docker exec -i Verdict360-postgres psql -U Verdict360 -d Verdict360_legal < docker/postgres/init-scripts/02-seed-data.sql

# 3. Test database
echo "3. Testing database..."
docker exec -it Verdict360-postgres psql -U Verdict360 -d Verdict360_legal -c "SELECT COUNT(*) as users FROM legal_users;"

# 4. Fix MinIO setup
echo "4. Setting up MinIO buckets..."
./scripts/setup-minio-fixed.sh

# 5. Test backup
echo "5. Testing backup system..."
./scripts/backup/postgres-backup-fixed.sh

echo "✅ Week 1 issues fixed! Run './scripts/status-check.sh' to verify."
