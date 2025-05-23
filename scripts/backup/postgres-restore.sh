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
    echo "Available backups:"
    ls -la ./backups/postgres/*.gz 2>/dev/null | awk '{print $9, $5, $6, $7, $8}' | column -t
}

# Function to restore from backup
restore_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        echo "Error: Backup file not found: $backup_file"
        exit 1
    fi
    
    echo "Restoring from backup: $backup_file"
    
    # Verify backup integrity first
    if [ -f "$backup_file.md5" ]; then
        cd "$(dirname "$backup_file")"
        if ! md5sum -c "$(basename "$backup_file").md5" >/dev/null 2>&1; then
            echo "Error: Backup integrity check failed!"
            exit 1
        fi
        cd - >/dev/null
        echo "Backup integrity verified."
    fi
    
    # Stop the application containers to prevent interference
    echo "Stopping application containers..."
    docker-compose stop web api
    
    # Restore the database
    echo "Restoring database..."
    zcat "$backup_file" | docker exec -i Verdict360-postgres psql -U "$POSTGRES_USER" -d postgres
    
    if [ $? -eq 0 ]; then
        echo "Database restore completed successfully!"
        
        # Restart application containers
        echo "Restarting application containers..."
        docker-compose start web api
        
    else
        echo "Error: Database restore failed!"
        exit 1
    fi
}

# Main script logic
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.gz> or $0 list"
    echo ""
    list_backups
    exit 1
elif [ "$1" = "list" ]; then
    list_backups
elif [ "$1" = "latest" ]; then
    # Find the most recent backup
    latest_backup=$(ls -t ./backups/postgres/*.gz 2>/dev/null | head -n1)
    if [ -n "$latest_backup" ]; then
        restore_backup "$latest_backup"
    else
        echo "No backups found!"
        exit 1
    fi
else
    restore_backup "$1"
fi
