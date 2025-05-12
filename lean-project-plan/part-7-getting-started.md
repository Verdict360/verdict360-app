# Verdict360 Getting Started Guide

## Immediate First Steps

This guide will help you take the first practical steps to start implementing the Verdict360 project with open-source technologies.

### 1. Development Environment Setup

#### Prerequisites

- **Docker & Docker Compose** - Required for containerized development
- **Git** - For version control and repository management
- **Node.js** (v18+) - For frontend development
- **Python** (v3.10+) - For backend development
- **VS Code** or preferred IDE with appropriate extensions

#### Initial Repository Setup

```bash
# Create GitHub organization and repositories
# Initialize the main repository
mkdir Verdict360
cd Verdict360

# Initialize Git repository
git init
git branch -M main

# Create basic project structure
mkdir -p frontend backend mobile docker/postgres/init-scripts

# Create basic .gitignore file
cat > .gitignore << EOF
# Dependencies
node_modules
.pnp
.pnp.js

# Testing
coverage

# Next.js
.next/
out/

# Production
build
dist

# Misc
.DS_Store
*.pem

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Local env files
.env
.env*.local

# Python
__pycache__/
*.py[cod]
*$py.class
venv
.venv
env
.env
*.so
.Python
env/

# Docker volumes
data

# IDE
.idea
.vscode
EOF

# Add README
cat > README.md << EOF
# Verdict360 - Legal Intelligence Platform

Verdict360 is an AI-powered legal intelligence platform designed specifically for legal firms and HR departments to access, interpret, and utilize South African legal information through natural language interaction.

## Getting Started

See the [documentation](/docs) folder for setup instructions.
EOF

# Create documentation directory
mkdir -p docs
```

### 2. Set Up Development Docker Environment

Create a development Docker Compose file to start building with the core services:

```bash
# Create docker-compose.yml
cat > docker-compose.yml << EOF
services:
  # PostgreSQL Database with pgvector
  postgres:
    image: postgres:15
    container_name: Verdict360-postgres
    restart: always
    environment:
      POSTGRES_USER: Verdict360
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: Verdict360
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "Verdict360"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Keycloak Authentication Server
  keycloak:
    image: quay.io/keycloak/keycloak:21.1.1
    container_name: Verdict360-keycloak
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/Verdict360
      KC_DB_USERNAME: Verdict360
      KC_DB_PASSWORD: devpassword
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
    command: ["start-dev"]

  # MinIO Object Storage
  minio:
    image: minio/minio
    container_name: Verdict360-minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

  # Ollama for Local LLM
  ollama:
    image: ollama/ollama:latest
    container_name: Verdict360-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  minio_data:
  ollama_data:
EOF
```

### 3. Set Up Initial Database Schema

Create the initial database schema for legal documents:

```bash
# Create initial PostgreSQL schema
mkdir -p docker/postgres/init-scripts
cat > docker/postgres/init-scripts/01-schema.sql << EOF
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Legal users table with role specifications
CREATE TABLE legal_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  keycloak_id VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  full_name VARCHAR(255) NOT NULL,
  firm_name VARCHAR(255),
  role VARCHAR(50) NOT NULL, -- attorney, paralegal, staff, hr
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create legal matters table for organization
CREATE TABLE legal_matters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  reference_number VARCHAR(100),
  client_id UUID REFERENCES legal_users(id),
  practice_area VARCHAR(100),
  responsible_attorney UUID REFERENCES legal_users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  status VARCHAR(50) NOT NULL DEFAULT 'active'
);

-- Create legal documents table with jurisdiction fields
CREATE TABLE legal_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  document_type VARCHAR(100) NOT NULL, -- contract, judgment, statute, etc.
  jurisdiction VARCHAR(100) NOT NULL DEFAULT 'South Africa',
  matter_id UUID REFERENCES legal_matters(id),
  storage_path VARCHAR(500) NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  created_by UUID REFERENCES legal_users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  confidentiality_level VARCHAR(50) NOT NULL DEFAULT 'standard'
);

-- Create recordings table with transcription status
CREATE TABLE legal_recordings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  matter_id UUID REFERENCES legal_matters(id),
  storage_path VARCHAR(500) NOT NULL,
  duration_seconds INTEGER,
  transcription_status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed
  transcription_path VARCHAR(500),
  created_by UUID REFERENCES legal_users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  recording_date TIMESTAMP WITH TIME ZONE
);

-- Create document chunks table for vector search
CREATE TABLE document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID REFERENCES legal_documents(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding vector(384), -- Using all-MiniLM-L6-v2 dimension
  metadata JSONB, -- Store citation info, legal domain, etc.
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create case law reference table
CREATE TABLE case_law_references (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  citation VARCHAR(255) NOT NULL UNIQUE,
  title VARCHAR(255) NOT NULL,
  jurisdiction VARCHAR(100) NOT NULL DEFAULT 'South Africa',
  court VARCHAR(100),
  year INTEGER,
  document_id UUID REFERENCES legal_documents(id),
  summary TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  relevance_score FLOAT
);

-- Create indexes for performance
CREATE INDEX ON document_chunks USING GIN (metadata jsonb_path_ops);
CREATE INDEX ON legal_documents(document_type);
CREATE INDEX ON legal_documents(jurisdiction);
CREATE INDEX ON legal_matters(practice_area);
CREATE INDEX ON case_law_references(citation);
CREATE INDEX ON case_law_references(court, year);
EOF
```

### 4. Initialize Next.js Frontend Project

Set up the Next.js frontend with TypeScript and Tailwind CSS:

```bash
# Navigate to frontend directory
cd frontend

# Initialize Next.js project
npx create-next-app@latest . --typescript --tailwind --eslint

# Install additional dependencies
npm install @radix-ui/react-icons lucide-react next-themes class-variance-authority clsx tailwind-merge
npm install keycloak-js axios date-fns next-mdx-remote react-dropzone react-hook-form zod @hookform/resolvers

# Install developer dependencies
npm install -D prettier prettier-plugin-tailwindcss

# Create a simple shadcn/ui setup (components folder)
mkdir -p components/ui

# Set up basic application structure
mkdir -p app/(auth) app/legal-chat app/legal-documents app/matters app/recordings app/dashboard
mkdir -p lib/utils lib/auth lib/hooks

# Create basic app layout
cat > app/layout.tsx << EOF
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Verdict360 - Legal Intelligence Platform",
  description: "AI-powered legal intelligence for South African professionals",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={cn(inter.className, "min-h-screen bg-background antialiased")}>
        {children}
      </body>
    </html>
  );
}
EOF

# Create simple utils module
cat > lib/utils.ts << EOF
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
EOF

cd ..
```

### 5. Set Up FastAPI Backend

Initialize the Python FastAPI backend:

```bash
# Navigate to backend directory
cd backend

# Create a requirements.txt file
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn==0.23.2
pydantic==2.4.2
python-multipart==0.0.6
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.0.1
sqlalchemy==2.0.22
asyncpg==0.28.0
alembic==1.12.0
langchain==0.0.335
sentence-transformers==2.2.2
chromadb==0.4.18
pdfminer.six==20221105
python-docx==0.8.11
openai-whisper==20231117
minio==7.1.17
httpx==0.25.0
EOF

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create project structure
mkdir -p app/{api,models,services,utils,database}
touch app/__init__.py app/api/__init__.py app/models/__init__.py app/services/__init__.py app/utils/__init__.py app/database/__init__.py

# Create main FastAPI application
cat > app/main.py << EOF
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Verdict360 Legal API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Verdict360 Legal API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
EOF

# Create database connection module
cat > app/database/__init__.py << EOF
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://Verdict360:devpassword@localhost:5432/Verdict360"
)

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session
EOF

# Create simple Dockerfile
cat > Dockerfile << EOF
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cd ..
```

### 6. Initialize React Native Mobile App

Set up the basic React Native mobile app:

```bash
# Navigate to mobile directory
cd mobile

# Initialize React Native project
npx react-native init Verdict360Mobile --template react-native-template-typescript

# Install additional dependencies
cd Verdict360Mobile
npm install @react-navigation/native @react-navigation/native-stack react-native-safe-area-context react-native-screens
npm install react-native-audio-recorder-player react-native-permissions react-native-fs
npm install axios react-native-mmkv @react-native-async-storage/async-storage

cd ../..
```

### 7. Start the Development Environment

Start the Docker containers and check if they're running correctly:

```bash
# Start Docker containers
docker-compose up -d

# Check if containers are running
docker ps

# For PostgreSQL:
docker exec -it Verdict360-postgres psql -U Verdict360 -d Verdict360 -c "\dt"

# For MinIO, open in browser:
# http://localhost:9001
# Login with minioadmin:minioadmin

# For Keycloak, open in browser:
# http://localhost:8080
# Login with admin:admin
```

### 8. Pull Required Ollama Models

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull Mistral model
curl -X POST http://localhost:11434/api/pull -d '{"name": "mistral:7b-instruct-v0.2"}'

# This will take some time as it downloads the model
```

### 9. Set Up Initial Legal Document Collection

Begin collecting freely available South African legal documents:

1. Create a script to download documents from SAFLII (South African Legal Information Institute):

```bash
mkdir -p scripts
cat > scripts/fetch_saflii_documents.py << EOF
import requests
from bs4 import BeautifulSoup
import os
import time

# Create directory for documents
os.makedirs('legal_documents', exist_ok=True)

# Base URL for SAFLII
base_url = 'http://www.saflii.org'

# Example: Constitutional Court judgments
url = f'{base_url}/za/cases/ZACC/'

# Fetch the index page
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find and process links to judgments
# This is a simplified example - actual implementation would be more robust
for link in soup.find_all('a'):
    href = link.get('href')
    if href and href.endswith('.html') and '/za/cases/ZACC/' in href:
        # Construct full URL if needed
        if not href.startswith('http'):
            href = base_url + href

        print(f"Downloading: {href}")

        # Fetch the document
        doc_response = requests.get(href)

        # Extract filename from URL
        filename = os.path.basename(href)

        # Save the document
        with open(f'legal_documents/{filename}', 'w', encoding='utf-8') as f:
            f.write(doc_response.text)

        # Be nice to the server
        time.sleep(1)

print("Download complete.")
EOF
```

> Note: Be sure to respect the terms of service of any website you scrape. Some legal resources may have specific requirements for automated access.

### 10. Begin Implementing Core Features

Start with the most critical features:

1. Document upload and processing
2. Basic authentication with Keycloak
3. Legal chat interface with Ollama integration

These first steps will give you a functional foundation to build upon, with all core open-source technologies in place.

## Next Steps After Initial Setup

Once you have the basic environment running:

1. **Establish development workflow** - Set up GitHub Actions for CI/CD
2. **Configure Keycloak properly** - Create realms, clients, and roles
3. **Implement authentication flow** - Connect frontend and mobile app to Keycloak
4. **Set up MinIO buckets** - Create and configure storage for documents
5. **Develop document processing pipeline** - Implement text extraction and embedding
6. **Create basic mobile recording functionality** - Implement audio recording in the mobile app

## Resource Requirements

For the initial development environment:

- **Minimum**: 8GB RAM, 4 CPU cores, 40GB storage
- **Recommended**: 16GB RAM, 8 CPU cores, 100GB storage (especially for running Ollama models)

## Cost Estimation

For the initial MVP with this open-source stack:

- **Development Environment**: Standard developer machines + local Docker environment - $0 additional cost
- **Testing Environment**: Basic VPS with 8GB RAM, 4 CPUs - ~$40/month
- **Initial Production**: Server with 16GB RAM, 8 CPUs - ~$80-120/month

This represents significant savings compared to commercial API-based alternatives, especially as usage scales.
