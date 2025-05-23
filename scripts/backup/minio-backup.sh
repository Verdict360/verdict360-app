#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found!"
    exit 1
fi

# Configuration
BACKUP_DIR="./backups/minio"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to backup MinIO data
backup_minio_data() {
    echo "Creating MinIO data backup..."
    
    # Create tarball of MinIO data volume
    docker run --rm \
        -v verdict360_minio_data:/source:ro \
        -v "$(pwd)/$BACKUP_DIR":/backup \
        alpine:latest \
        tar czf "/backup/minio_data_${DATE}.tar.gz" -C /source .
    
    if [ $? -eq 0 ]; then
        echo "MinIO data backup created: $BACKUP_DIR/minio_data_${DATE}.tar.gz"
        
        # Create checksum
        md5sum "$BACKUP_DIR/minio_data_${DATE}.tar.gz" > "$BACKUP_DIR/minio_data_${DATE}.tar.gz.md5"
        
    else
        echo "Error: MinIO data backup failed!"
        return 1
    fi
}

# Function to backup MinIO configuration using mc
backup_minio_config() {
    echo "Creating MinIO configuration backup..."
    
    # Use mc (MinIO Client) to backup policies, users, etc.
    docker run --rm \
        --network host \
        -v "$(pwd)/$BACKUP_DIR":/backup \
        minio/mc:latest \
        /bin/sh -c "
        mc alias set local http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD;
        mc admin policy list local > /backup/policies_${DATE}.json;
        mc admin user list local > /backup/users_${DATE}.txt;
        mc admin config get local > /backup/config_${DATE}.txt;
        "
    
    if [ $? -eq 0 ]; then
        echo "MinIO configuration backup completed"
    else
        echo "Warning: MinIO configuration backup failed (this is normal if MinIO is not running)"
    fi
}

# Function to clean old backups
cleanup_old_backups() {
    echo "Cleaning up MinIO backups older than $RETENTION_DAYS days..."
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "*.md5" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "*.json" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "*.txt" -mtime +$RETENTION_DAYS -delete
    echo "MinIO backup cleanup completed."
}

# Main execution
echo "Starting Verdict360 MinIO backup process..."
backup_minio_data
backup_minio_config
cleanup_old_backups

echo "MinIO backup process completed!"
