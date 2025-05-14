## 3. 4-Week Roadmap with Open-Source Implementation

### Week 1: Foundation & Open-Source Setup (May 7-13, 2025)

#### Detailed Task Checklist

##### P### Project Repository

- [x] Create GitHub organization "Verdict360"
- [x] Initialize repositories (web, api, mobile)
- [x] Set up branch protection rules with legal compliance emphasis
- [x] Configure GitHub project board with legal workflow labels
- [x] Create issue templates for legal document features
- [x] Set up CI/CD workflow files (GitHub Actions)
- [x] Add Docker configurations for development consistency

### Next.js Setup & Legal UI Framework

- [x] Initialize Next.js project with TypeScript
- [x] Install and configure Tailwind CSS with legal color scheme
- [x] Add shadcn/ui components with legal-themed customizations
- [x] Set up ESLint and Prettier with team standards
- [x] Configure TypeScript paths and aliases
- [x] Add legal-specific folder structure (legal-docs, case-law, audio)
- [x] Create responsive design system with mobile-first approach

### Mobile App Foundation (React Native)

- [x] Initialize React Native project with TypeScript
- [x] Configure native audio recording capabilities
- [x] Set up secure file storage mechanisms
- [x] Create basic UI components for recording
- [x] Implement audio compression for efficient upload
- [x] Add offline capability for recording without connectivity
- [x] Configure authentication integration

### Open-Source Authentication Setup (Keycloak)

- [x] Set up Keycloak Docker container for development
- [x] Configure realms for legal application
- [x] Create client configurations for web and mobile apps
- [x] Set up user roles and permissions structure
- [ ] Configure email templates for legal workflow
- [x] Add group mappings for firm structure
- [x] Create test user accounts for development

### PostgreSQL Database Setup

- [x] Configure PostgreSQL Docker container
- [x] Install pgvector extension for vector operations
- [x] Create legal database schema with proper relations
- [x] Set up user permissions and security
- [ ] Configure backups and recovery procedures
- [ ] Create seed data for development
- [x] Implement migration system for schema changes

### MinIO Storage Configuration

- [x] Set up MinIO Docker container
- [x] Configure storage buckets for legal documents
- [x] Create storage buckets for audio recordings
- [x] Set up access policies and permissions
- [ ] Configure TLS for secure connections
- [ ] Implement backup strategies
- [x] Create integration endpoints for applications

### Basic Legal UI Layout

- [x] Design navigation with legal workflow organization
- [x] Create responsive header with practice switcher
- [x] Build sidebar with legal document categorization
- [x] Implement dark/light mode toggle with legal-themed colors
- [x] Create legal-focused landing page
- [x] Add footer with legal compliance information
- [x] Build responsive components for mobile compatibility

| Task                          | Owner | Status      | Due    |
| ----------------------------- | ----- | ----------- | ------ |
| Project Repository Setup      |       | Not Started | May 7  |
| Next.js & Legal UI Setup      |       | Not Started | May 8  |
| Mobile App Foundation         |       | Not Started | May 8  |
| Keycloak Authentication Setup |       | Not Started | May 9  |
| PostgreSQL Database Setup     |       | Not Started | May 9  |
| MinIO Storage Configuration   |       | Not Started | May 10 |
| Legal UI Layout               |       | Not Started | May 13 |

**Week 1 Milestone**: Working application shell with open-source authentication, storage, database, and basic mobile recording capability

#### Week 1 Technical Implementation Details

```yaml
# docker-compose.yml for development environment
services:
  # PostgreSQL Database with pgvector
  postgres:
    image: postgres:15
    container_name: Verdict360-postgres
    restart: always
    environment:
      POSTGRES_USER: Verdict360
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: Verdict360
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ['CMD', 'pg_isready', '-U', 'Verdict360']
      interval: 5s
      timeout: 5s
      retries: 5

  # Keycloak Authentication Server
  keycloak:
    image: quay.io/keycloak/keycloak:21.1.1
    container_name: Verdict360-keycloak
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/Verdict360
      KC_DB_USERNAME: Verdict360
      KC_DB_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - '8080:8080'
    depends_on:
      postgres:
        condition: service_healthy
    command: ['start-dev']

  # MinIO Object Storage
  minio:
    image: minio/minio
    container_name: Verdict360-minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    ports:
      - '9000:9000'
      - '9001:9001'
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:9000/minio/health/live']
      interval: 5s
      timeout: 5s
      retries: 3

volumes:
  postgres_data:
  minio_data:
```

```typescript
// Legal Database Schema (PostgreSQL)
// init-scripts/01-schema.sql

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
```

```typescript
// Authentication integration with Keycloak
// lib/auth.ts

import { useRouter } from 'next/router';
import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import Keycloak from 'keycloak-js';

interface AuthContextType {
  keycloak: Keycloak | null;
  initialized: boolean;
  isAuthenticated: boolean;
  token: string | undefined;
  userInfo: any | null;
  login: () => void;
  logout: () => void;
  hasRole: (role: string) => boolean;
}

const keycloakConfig = {
  url: process.env.NEXT_PUBLIC_KEYCLOAK_URL || 'http://localhost:8080',
  realm: process.env.NEXT_PUBLIC_KEYCLOAK_REALM || 'Verdict360',
  clientId: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID || 'Verdict360-web',
};

const AuthContext = createContext<AuthContextType>({
  keycloak: null,
  initialized: false,
  isAuthenticated: false,
  token: undefined,
  userInfo: null,
  login: () => {},
  logout: () => {},
  hasRole: () => false,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [keycloak, setKeycloak] = useState<Keycloak | null>(null);
  const [initialized, setInitialized] = useState(false);
  const [userInfo, setUserInfo] = useState<any | null>(null);
  const router = useRouter();

  useEffect(() => {
    const initKeycloak = async () => {
      try {
        const keycloakInstance = new Keycloak(keycloakConfig);

        const auth = await keycloakInstance.init({
          onLoad: 'check-sso',
          silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
          pkceMethod: 'S256',
        });

        setKeycloak(keycloakInstance);
        setInitialized(true);

        if (auth && keycloakInstance.token) {
          // Fetch user info when authenticated
          const userInfo = await keycloakInstance.loadUserInfo();
          setUserInfo(userInfo);

          // Refresh token periodically
          setInterval(() => {
            keycloakInstance.updateToken(70).catch(() => {
              console.error('Failed to refresh token');
              keycloakInstance.logout();
            });
          }, 60000);
        }
      } catch (error) {
        console.error('Failed to initialize Keycloak', error);
        setInitialized(true);
      }
    };

    initKeycloak();
  }, []);

  const login = () => {
    if (keycloak) {
      keycloak.login();
    }
  };

  const logout = () => {
    if (keycloak) {
      keycloak.logout({ redirectUri: window.location.origin });
    }
  };

  const hasRole = (role: string): boolean => {
    return keycloak?.hasRealmRole(role) || false;
  };

  const value = {
    keycloak,
    initialized,
    isAuthenticated: !!keycloak?.authenticated,
    token: keycloak?.token,
    userInfo,
    login,
    logout,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
```
