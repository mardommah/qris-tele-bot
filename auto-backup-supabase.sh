#!/bin/bash

# Auto Backup Script for QRIS Telegram Bot Database to Supabase

echo "🗄️ Starting database backup to Supabase..."

# Check if required tools are available
if ! command -v sqlite3 &> /dev/null; then
    echo "❌ Error: sqlite3 is not installed"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo "❌ Error: curl is not installed"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
else
    echo "❌ Error: .env file not found"
    exit 1
fi

# Check if Supabase credentials are available
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file"
    exit 1
fi

# Database file path (relative to script location)
DB_FILE="./qris_bot.db"

# Check if database file exists
if [ ! -f "$DB_FILE" ]; then
    echo "❌ Error: Database file not found at $DB_FILE"
    exit 1
fi

# Create backup directory if it doesn't exist
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

# Create timestamp for backup file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/qris_bot_backup_$TIMESTAMP.sql"

# Export database to SQL file
echo "📤 Exporting database to SQL file..."
sqlite3 "$DB_FILE" .dump > "$BACKUP_FILE"

# Check if export was successful
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to export database"
    exit 1
fi

echo "✅ Database exported successfully to $BACKUP_FILE"

# Upload to Supabase Storage
echo "☁️ Uploading backup to Supabase Storage..."

# Using curl to upload file to Supabase Storage
HTTP_CODE=$(curl -s -w "%{http_code}" -o /tmp/curl_response.txt -X POST "${SUPABASE_URL}/storage/v1/object/${STORAGE_NAME}/qris_bot_backup_$TIMESTAMP.sql" \
  -H "Authorization: Bearer ${SUPABASE_KEY}" \
  -H "Content-Type: application/sql" \
  -T "$BACKUP_FILE")

RESPONSE_BODY=$(cat /tmp/curl_response.txt)
rm -f /tmp/curl_response.txt

echo "HTTP Code: $HTTP_CODE"
# Only show response body if it's not too long
if [ ${#RESPONSE_BODY} -lt 200 ]; then
    echo "Response Body: $RESPONSE_BODY"
else
    echo "Response Body: [Response body too long to display]"
fi

# Check if upload was successful (HTTP 200 indicates success)
if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ Backup uploaded successfully to Supabase"
elif [ "$HTTP_CODE" -eq 401 ]; then
    echo "❌ Error uploading to Supabase: Unauthorized. Check your SUPABASE_KEY."
    exit 1
elif [ "$HTTP_CODE" -eq 400 ]; then
    echo "❌ Error uploading to Supabase: Bad Request. Check your request format."
    exit 1
elif [ "$HTTP_CODE" -eq 000 ]; then
    echo "❌ Error uploading to Supabase: Connection failed. Check your SUPABASE_URL."
    exit 1
else
    echo "❌ Error uploading to Supabase (HTTP $HTTP_CODE)"
    exit 1
fi

# Keep only last 7 backups locally to save space
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -name "qris_bot_backup_*.sql" -type f -mtime +7 -delete

echo "✅ Database backup to Supabase completed successfully!"
