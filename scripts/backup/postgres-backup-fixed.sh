#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found!"
    exit 1
fi

# Use the database name from docker-compose.yml
DB_NAME="Verdict360_legal"
BACKUP_DIR="./backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="verdict360_backup_${DATE}.sql"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to create backup
create_backup() {
    echo "Creating PostgreSQL backup for database: $DB_NAME"
    
    # Create database dump
    docker exec Verdict360-postgres pg_dump \
        -U "Verdict360" \
        -d "$DB_NAME" \
        --clean \
        --if-exists \
        --create \
        --verbose \
        > "$BACKUP_DIR/$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Backup created successfully: $BACKUP_DIR/$BACKUP_FILE"
        
        # Compress the backup
        gzip "$BACKUP_DIR/$BACKUP_FILE"
        echo "Backup compressed: $BACKUP_DIR/$BACKUP_FILE.gz"
        
        # Create checksums for integrity verification
        md5 "$BACKUP_DIR/$BACKUP_FILE.gz" > "$BACKUP_DIR/$BACKUP_FILE.gz.md5"
        
    else
        echo "Error: Backup failed!"
        exit 1
    fi
}

# Function to clean old backups
cleanup_old_backups() {
    echo "Cleaning up backups older than $RETENTION_DAYS days..."
    find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "*.md5" -mtime +$RETENTION_DAYS -delete
    echo "Cleanup completed."
}

# Main execution
echo "Starting Verdict360 PostgreSQL backup process..."
create_backup
cleanup_old_backups

echo "Backup process completed successfully!"
