#!/bin/bash

# Add daily backup cron job (runs at 2 AM daily)
(crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/scripts/backup/postgres-backup.sh >> $(pwd)/logs/backup.log 2>&1") | crontab -

echo "Cron job added for daily PostgreSQL backups at 2 AM"
echo "Logs will be written to: $(pwd)/logs/backup.log"

# Create logs directory
mkdir -p logs
