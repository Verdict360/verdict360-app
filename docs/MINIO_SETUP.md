# MinIO Storage Setup

This document outlines the MinIO setup for Verdict360 and provides instructions for configuration.

## Bucket Structure

The application uses the following buckets:

- **legal-documents**: For storing all legal documents (PDF, DOCX, etc.)
- **legal-recordings**: For storing audio recordings
- **legal-transcriptions**: For storing transcriptions of audio recordings
- **user-profiles**: For storing user profile information and avatars
- **matter-resources**: For storing matter-specific resources
- **legal-templates**: For storing legal document templates (publicly readable)

## Security Considerations

- Server-side encryption is enabled for all sensitive buckets
- Versioning is enabled to maintain document history
- Retention policies are set to maintain legal compliance
- Access is controlled through MinIO's policy system

## User Roles

- **legal-reader**: Can read legal documents but not modify them
- **legal-editor**: Can read and write legal documents
- **backup-operator**: Can read all data for backup purposes

## Setup Instructions

1. Run the MinIO setup script to configure the server:

```bash
# Ensure MinIO is running
docker-compose up -d minio

# Run the setup script
./scripts/setup-minio.sh
```

2. Access the MinIO Console:
   - URL: http://localhost:9001
   - Username: from .env file (MINIO_ROOT_USER)
   - Password: from .env file (MINIO_ROOT_PASSWORD)

3. Verify buckets and policies are correctly set up

## API Usage

The application interacts with MinIO through the S3-compatible API. Key functions include:

- Generating presigned URLs for direct upload/download
- Listing objects with specific prefixes
- Managing object metadata and tags

See `web/lib/storage/minio-client.ts` for the client implementation.

## For Production

In production environments, consider:

- Using a load balancer in front of MinIO
- Setting up replication for disaster recovery
- Implementing a regular backup strategy
- Using a proper certificate for SSL
