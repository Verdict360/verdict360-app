#!/bin/bash

# Generate a secure random string
generate_secure_string() {
  openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32
}

# Generate values
DB_PASSWORD=$(generate_secure_string)
KEYCLOAK_PASSWORD=$(generate_secure_string)
MINIO_PASSWORD=$(generate_secure_string)
JWT_SECRET=$(generate_secure_string)
COOKIE_SECRET=$(generate_secure_string)
ENCRYPTION_KEY=$(generate_secure_string)
NEXTAUTH_SECRET=$(generate_secure_string)

# Output the generated values
echo "Generated secure values:"
echo "-----------------------"
echo "POSTGRES_PASSWORD=$DB_PASSWORD"
echo "KEYCLOAK_ADMIN_PASSWORD=$KEYCLOAK_PASSWORD"
echo "MINIO_ROOT_PASSWORD=$MINIO_PASSWORD"
echo "API_JWT_SECRET=$JWT_SECRET"
echo "COOKIE_SECRET=$COOKIE_SECRET"
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY"
echo "NEXTAUTH_SECRET=$NEXTAUTH_SECRET"
echo "-----------------------"
echo "Please copy these values to your respective .env files."
echo "IMPORTANT: Do not commit these values to version control."
