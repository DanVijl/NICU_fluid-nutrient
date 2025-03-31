#!/bin/bash

# Backup script for NICU Fluid Management App
# This script creates a backup of the database and logs

# Configuration
BACKUP_DIR="/app/backups"
DB_FILE="/app/nicu_app.db"
LOGS_DIR="/app/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="nicu_app_backup_${TIMESTAMP}"

# Ensure backup directory exists
mkdir -p ${BACKUP_DIR}

# Create backup directory for this backup
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

# Backup database
if [ -f "$DB_FILE" ]; then
    echo "Backing up database..."
    sqlite3 ${DB_FILE} ".backup '${BACKUP_DIR}/${BACKUP_NAME}/nicu_app.db'"
    
    # Verify backup
    if [ -f "${BACKUP_DIR}/${BACKUP_NAME}/nicu_app.db" ]; then
        echo "Database backup successful."
    else
        echo "Database backup failed!"
        exit 1
    fi
else
    echo "Database file not found at ${DB_FILE}"
fi

# Backup logs
if [ -d "$LOGS_DIR" ]; then
    echo "Backing up logs..."
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}/logs.tar.gz" -C $(dirname ${LOGS_DIR}) $(basename ${LOGS_DIR})
    
    # Verify backup
    if [ -f "${BACKUP_DIR}/${BACKUP_NAME}/logs.tar.gz" ]; then
        echo "Logs backup successful."
    else
        echo "Logs backup failed!"
        exit 1
    fi
else
    echo "Logs directory not found at ${LOGS_DIR}"
fi

# Create backup info file
cat > "${BACKUP_DIR}/${BACKUP_NAME}/backup_info.txt" << EOF
Backup created: $(date)
Application: NICU Fluid Management App
Database: $(ls -lh ${BACKUP_DIR}/${BACKUP_NAME}/nicu_app.db 2>/dev/null || echo "Not backed up")
Logs: $(ls -lh ${BACKUP_DIR}/${BACKUP_NAME}/logs.tar.gz 2>/dev/null || echo "Not backed up")
EOF

# Create archive of the entire backup
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" -C ${BACKUP_DIR} ${BACKUP_NAME}

# Clean up temporary directory
rm -rf "${BACKUP_DIR}/${BACKUP_NAME}"

# Keep only the 10 most recent backups
cd ${BACKUP_DIR}
ls -t *.tar.gz | tail -n +11 | xargs -r rm

echo "Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
