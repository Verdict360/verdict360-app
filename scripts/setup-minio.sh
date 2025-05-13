#!/bin/bash

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
sleep 5

# Clear any existing aliases to avoid conflicts
mc alias remove myminio 2>/dev/null || true

# Set up MinIO client with correct credentials
# Note: for local development, default credentials are often minioadmin/minioadmin
mc alias set myminio http://localhost:9000 minioadmin minioadmin

# Create buckets
echo "Creating legal document buckets..."
mc mb myminio/legal-documents --quiet || echo "Bucket already exists"
mc mb myminio/legal-recordings --quiet || echo "Bucket already exists"
mc mb myminio/legal-transcriptions --quiet || echo "Bucket already exists"

# Set bucket policies using the new 'anonymous' command
echo "Setting bucket policies..."
mc anonymous set download myminio/legal-documents
mc anonymous set download myminio/legal-recordings
mc anonymous set download myminio/legal-transcriptions

echo "MinIO setup complete!"
