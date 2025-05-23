#!/bin/bash

echo "Starting full Verdict360 backup (PostgreSQL + MinIO)..."

# Run PostgreSQL backup
echo "=== PostgreSQL Backup ==="
./scripts/backup/postgres-backup.sh

# Run MinIO backup
echo "=== MinIO Backup ==="
./scripts/backup/minio-backup.sh

# Create combined backup manifest
DATE=$(date +%Y%m%d_%H%M%S)
MANIFEST_FILE="./backups/backup_manifest_${DATE}.txt"

cat > "$MANIFEST_FILE" << MANIFEST_EOF
Verdict360 Full Backup Manifest
Generated: $(date)
Backup Date: $DATE

PostgreSQL Backup:
$(ls -la ./backups/postgres/*${DATE}* 2>/dev/null || echo "No PostgreSQL backup found")

MinIO Backup:
$(ls -la ./backups/minio/*${DATE}* 2>/dev/null || echo "No MinIO backup found")

System Information:
Docker Compose Version: $(docker-compose --version)
Docker Version: $(docker --version)
Host OS: $(uname -a)
MANIFEST_EOF

echo "Full backup completed! Manifest: $MANIFEST_FILE"
