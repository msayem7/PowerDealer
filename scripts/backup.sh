#!/bin/bash
# Backup Script for Powerdealer
# Creates backups of database and media files
# Usage: bash backup.sh

set -e

BACKUP_DIR="/opt/powerdealer/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "=== Powerdealer Backup ==="

cd /opt/powerdealer

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U powerdealer powerdealer | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup media files
echo "Backing up media files..."
docker run --rm -v powerdealer_media_files:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/media_$DATE.tar.gz -C /data .

# Keep only last 7 days of backups
echo "Cleaning old backups..."
find $BACKUP_DIR -type f -mtime +7 -delete

echo ""
echo "=== Backup Complete ==="
echo "Database backup: $BACKUP_DIR/db_$DATE.sql.gz"
echo "Media backup: $BACKUP_DIR/media_$DATE.tar.gz"
