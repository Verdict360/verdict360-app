#!/bin/bash

# Source the .env file to get credentials
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found!"
    exit 1
fi

# Use the credentials from .env, fallback to defaults if not set
MINIO_USER=${MINIO_ROOT_USER:-minioadmin}
MINIO_PASS=${MINIO_ROOT_PASSWORD:-minioadmin}

echo "Using MinIO credentials from .env"

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
sleep 5

# Clear any existing aliases to avoid conflicts
mc alias remove myminio 2>/dev/null || true

# Set up MinIO client with credentials from .env
echo "Setting up MinIO alias with user: $MINIO_USER"
mc alias set myminio http://localhost:9000 "$MINIO_USER" "$MINIO_PASS"

# Create buckets with versioning enabled
echo "Creating legal document buckets..."
mc mb myminio/legal-documents --quiet || echo "Bucket already exists"
mc mb myminio/legal-recordings --quiet || echo "Bucket already exists"
mc mb myminio/legal-transcriptions --quiet || echo "Bucket already exists"
mc mb myminio/user-profiles --quiet || echo "Bucket already exists"
mc mb myminio/matter-resources --quiet || echo "Bucket already exists"
mc mb myminio/legal-templates --quiet || echo "Bucket already exists"

# Enable versioning on buckets with legal content (skip locking errors for now)
echo "Enabling versioning on legal document buckets..."
mc version enable myminio/legal-documents 2>/dev/null || echo "Versioning: already enabled or not supported"
mc version enable myminio/legal-recordings 2>/dev/null || echo "Versioning: already enabled or not supported"
mc version enable myminio/matter-resources 2>/dev/null || echo "Versioning: already enabled or not supported"

# Set up lifecycle management for transcriptions
echo "Setting up lifecycle management rules..."
cat > /tmp/lifecycle.json << LIFECYCLE
{
  "Rules": [
    {
      "ID": "Expire-temp-transcriptions",
      "Status": "Enabled",
      "Filter": {
        "Tag": {
          "Key": "status",
          "Value": "temporary"
        }
      },
      "Expiration": {
        "Days": 30
      }
    }
  ]
}
LIFECYCLE
mc ilm import myminio/legal-transcriptions < /tmp/lifecycle.json 2>/dev/null || echo "Lifecycle: import failed or not supported"

# Set public read on legal templates
echo "Setting bucket policies..."
mc anonymous set download myminio/legal-templates

# Create users with specific access (skip advanced policies for now in development)
echo "Creating basic users..."
mc admin user add myminio legal-reader legal-reader-password 2>/dev/null || echo "User already exists: legal-reader"
mc admin user add myminio legal-editor legal-editor-password 2>/dev/null || echo "User already exists: legal-editor"
mc admin user add myminio backup-operator backup-operator-password 2>/dev/null || echo "User already exists: backup-operator"

echo "MinIO basic setup complete!"
echo "Credentials:"
echo "  Admin: $MINIO_USER / $MINIO_PASS"
echo "  Legal Reader: legal-reader / legal-reader-password"
echo "  Legal Editor: legal-editor / legal-editor-password"
echo "  Backup Operator: backup-operator / backup-operator-password"
echo ""
echo "Access the MinIO Console at: http://localhost:9001"
