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

# Enable versioning on buckets with legal content
echo "Enabling versioning on legal document buckets..."
mc version enable myminio/legal-documents
mc version enable myminio/legal-recordings
mc version enable myminio/matter-resources

# Set retention policies on legal buckets (governance mode - requires special permissions to delete)
echo "Setting retention policies on legal buckets..."
mc retention set --default governance 1y myminio/legal-documents
mc retention set --default governance 1y myminio/legal-recordings

# Set up lifecycle management for transcriptions (auto-delete after 30 days if marked temporary)
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
mc ilm import myminio/legal-transcriptions < /tmp/lifecycle.json

# Set encryption on buckets
echo "Setting up server-side encryption..."
mc encrypt set SSE-S3 myminio/legal-documents
mc encrypt set SSE-S3 myminio/legal-recordings
mc encrypt set SSE-S3 myminio/user-profiles

# Create bucket policies for access
echo "Setting bucket policies..."
# Public read on legal templates
mc anonymous set download myminio/legal-templates

# Create users with specific access
echo "Creating users with specific permissions..."

# Create legal-reader user
mc admin user add myminio legal-reader legal-reader-password

# Create legal-editor user
mc admin user add myminio legal-editor legal-editor-password

# Create backup-operator user
mc admin user add myminio backup-operator backup-operator-password

# Create a policy file for legal-reader
cat > /tmp/legal-reader-policy.json << EOF_POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::legal-documents/*",
        "arn:aws:s3:::legal-documents",
        "arn:aws:s3:::legal-recordings/*",
        "arn:aws:s3:::legal-recordings",
        "arn:aws:s3:::legal-transcriptions/*",
        "arn:aws:s3:::legal-transcriptions",
        "arn:aws:s3:::legal-templates/*",
        "arn:aws:s3:::legal-templates"
      ]
    }
  ]
}
EOF_POLICY

# Create a policy file for legal-editor
cat > /tmp/legal-editor-policy.json << EOF_POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::legal-documents/*",
        "arn:aws:s3:::legal-documents",
        "arn:aws:s3:::legal-recordings/*",
        "arn:aws:s3:::legal-recordings",
        "arn:aws:s3:::legal-transcriptions/*",
        "arn:aws:s3:::legal-transcriptions",
        "arn:aws:s3:::matter-resources/*",
        "arn:aws:s3:::matter-resources"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::legal-templates/*",
        "arn:aws:s3:::legal-templates"
      ]
    }
  ]
}
EOF_POLICY

# Create a policy file for backup-operator
cat > /tmp/backup-policy.json << EOF_POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket",
        "s3:GetBucketVersioning"
      ],
      "Resource": [
        "arn:aws:s3:::*"
      ]
    }
  ]
}
EOF_POLICY

# Add policies to MinIO
mc admin policy add myminio legal-reader /tmp/legal-reader-policy.json
mc admin policy add myminio legal-editor /tmp/legal-editor-policy.json
mc admin policy add myminio backup-operator /tmp/backup-policy.json

# Assign policies to users
mc admin policy set myminio legal-reader user=legal-reader
mc admin policy set myminio legal-editor user=legal-editor
mc admin policy set myminio backup-operator user=backup-operator

# Set up monitoring and notification for large uploads
echo "Setting up event notifications..."
mc event add myminio/legal-documents arn:minio:sqs::primary:webhook --event put --suffix .pdf
mc event add myminio/legal-recordings arn:minio:sqs::primary:webhook --event put --suffix .mp3

echo "MinIO setup complete!"
echo "Credentials:"
echo "  Admin: $MINIO_USER / $MINIO_PASS"
echo "  Legal Reader: legal-reader / legal-reader-password"
echo "  Legal Editor: legal-editor / legal-editor-password"
echo "  Backup Operator: backup-operator / backup-operator-password"
echo ""
echo "Access the MinIO Console at: http://localhost:9001"
