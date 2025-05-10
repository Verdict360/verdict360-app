#!/bin/bash

# Check if .env file exists
if [ -f .env ]; then
    echo "Warning: .env file already exists. Backing it up to .env.backup"
    cp .env .env.backup
fi

# Generate secure passwords
DB_PASSWORD=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32)
KEYCLOAK_PASSWORD=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32)
MINIO_PASSWORD=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32)
JWT_SECRET=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32)
COOKIE_SECRET=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32)
ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32)

# Create development .env file
cat > .env << EOL
# Application Environment
NODE_ENV=development

# PostgreSQL Configuration
POSTGRES_USER=Verdict360
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=Verdict360_legal
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Keycloak Configuration
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_PASSWORD}
KEYCLOAK_REALM=Verdict360
KEYCLOAK_CLIENT_ID_WEB=Verdict360-web
KEYCLOAK_CLIENT_ID_MOBILE=Verdict360-mobile
KEYCLOAK_URL=http://localhost:8080

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
MINIO_ENDPOINT=localhost
MINIO_PORT=9000
MINIO_USE_SSL=false
MINIO_BUCKET_DOCUMENTS=Verdict360-documents
MINIO_BUCKET_RECORDINGS=Verdict360-recordings
MINIO_BUCKET_TRANSCRIPTIONS=Verdict360-transcriptions

# API Configuration
API_PORT=3001
API_URL=http://localhost:3001
API_JWT_SECRET=${JWT_SECRET}

# Next.js Web Configuration
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_KEYCLOAK_URL=http://localhost:8080
NEXT_PUBLIC_KEYCLOAK_REALM=Verdict360
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=Verdict360-web

# Mobile App Configuration
MOBILE_API_URL=http://10.0.2.2:3001
MOBILE_KEYCLOAK_URL=http://10.0.2.2:8080

# Currency Configuration
DEFAULT_CURRENCY=ZAR
DEFAULT_LOCALE=en-ZA

# Security Keys
COOKIE_SECRET=${COOKIE_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
EOL

echo "Development environment file created."
echo "Starting Docker services..."

# Start Docker services
docker-compose up -d

echo "Creating component-specific .env files..."

# Create web/.env.local
mkdir -p web
cat > web/.env.local << EOL
# Public variables (available in browser)
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_KEYCLOAK_URL=http://localhost:8080
NEXT_PUBLIC_KEYCLOAK_REALM=Verdict360
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=Verdict360-web
NEXT_PUBLIC_DEFAULT_CURRENCY=ZAR
NEXT_PUBLIC_DEFAULT_LOCALE=en-ZA

# Server-only variables (not exposed to browser)
COOKIE_SECRET=${COOKIE_SECRET}
NEXTAUTH_SECRET=${JWT_SECRET}
NEXTAUTH_URL=http://localhost:3000
EOL

# Create api/.env
mkdir -p api
cat > api/.env << EOL
# API Server Configuration
PORT=3001
NODE_ENV=development

# Database Connection
DB_HOST=localhost
DB_PORT=5432
DB_USER=Verdict360
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=Verdict360_legal

# Authentication
JWT_SECRET=${JWT_SECRET}
JWT_EXPIRATION=24h
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=Verdict360
KEYCLOAK_CLIENT_ID=Verdict360-api

# MinIO Storage
MINIO_ENDPOINT=localhost
MINIO_PORT=9000
MINIO_USE_SSL=false
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=${MINIO_PASSWORD}
MINIO_BUCKET_DOCUMENTS=Verdict360-documents
MINIO_BUCKET_RECORDINGS=Verdict360-recordings
MINIO_BUCKET_TRANSCRIPTIONS=Verdict360-transcriptions

# Rate Limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=100

# Logging
LOG_LEVEL=debug
EOL

# Create mobile/.env
mkdir -p mobile
cat > mobile/.env << EOL
# API Configuration
API_URL=http://10.0.2.2:3001

# Authentication
KEYCLOAK_URL=http://10.0.2.2:8080
KEYCLOAK_REALM=Verdict360
KEYCLOAK_CLIENT_ID=Verdict360-mobile

# Storage Configuration
MINIO_ENDPOINT=10.0.2.2
MINIO_PORT=9000
MINIO_USE_SSL=false
EOL

echo "Setup complete! Your local development environment is ready."
echo ""
echo "IMPORTANT: These credentials are for local development only."
echo "DO NOT use these in production environments."
echo ""
echo "Next steps:"
echo "1. Check if Docker services are running: docker-compose ps"
echo "2. Configure Keycloak at http://localhost:8080"
echo "3. Set up MinIO buckets at http://localhost:9001"
echo "4. Start the API server: cd api && npm run dev"
echo "5. Start the Next.js app: cd web && npm run dev"
