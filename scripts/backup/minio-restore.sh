#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found!"
    exit 1
fi

# Function to list available backups
list_backups() {
    echo "Available MinIO backups:"
    ls -la ./backups/minio/*.tar.gz 2>/dev/null | awk '{print $9, $5, $6, $7, $8}' | column -t
}

# Function to restore MinIO data
restore_minio_data() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        echo "Error: Backup file not found: $backup_file"
        exit 1
    fi
    
    echo "Restoring MinIO data from: $backup_file"
    
    # Verify backup integrity
    if [ -f "$backup_file.md5" ]; then
        cd "$(dirname "$backup_file")"
        if ! md5sum -c "$(basename "$backup_file").md5" >/dev/null 2>&1; then
            echo "Error: Backup integrity check failed!"
            exit 1
        fi
        cd - >/dev/null
        echo "Backup integrity verified."
    fi
    
    # Stop MinIO container
    echo "Stopping MinIO container..."
    docker-compose stop minio
    
    # Remove existing data
    echo "Removing existing MinIO data..."
    docker volume rm verdict360_minio_data 2>/dev/null || true
    
    # Create new volume and restore data
    echo "Restoring MinIO data..."
    docker run --rm \
        -v verdict360_minio_data:/target \
        -v "$(pwd)/$(dirname "$backup_file")":/backup \
        alpine:latest \
        tar xzf "/backup/$(basename "$backup_file")" -C /target
    
    if [ $? -eq 0 ]; then
        echo "MinIO data restore completed successfully!"
        
        # Restart MinIO
        echo "Restarting MinIO container..."
        docker-compose start minio
        
    else
        echo "Error: MinIO data restore failed!"
        exit 1
    fi
}

# Main script logic
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.tar.gz> or $0 list"
    echo ""
    list_backups
    exit 1
elif [ "$1" = "list" ]; then
    list_backups
elif [ "$1" = "latest" ]; then
    # Find the most recent backup
    latest_backup=$(ls -t ./backups/minio/*.tar.gz 2>/dev/null | head -n1)
    if [ -n "$latest_backup" ]; then
        restore_minio_data "$latest_backup"
    else
        echo "No MinIO backups found!"
        exit 1
    fi
else
    restore_minio_data "$1"
fi
