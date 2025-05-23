#!/bin/bash

CERT_DIR="docker/minio/certs"
mkdir -p "$CERT_DIR"

# Generate private key
openssl genrsa -out "$CERT_DIR/private.key" 2048

# Create certificate signing request
cat > "$CERT_DIR/cert.conf" << CERT_EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=ZA
ST=Gauteng
L=Johannesburg
O=Verdict360
OU=Legal Technology
CN=localhost

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = minio
DNS.3 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
CERT_EOF

# Generate certificate
openssl req -new -x509 -key "$CERT_DIR/private.key" -out "$CERT_DIR/public.crt" -days 365 -config "$CERT_DIR/cert.conf" -extensions v3_req

echo "SSL certificates created for MinIO in $CERT_DIR"
echo "Note: These are self-signed certificates for development only."
echo "For production, use certificates from a trusted CA."
