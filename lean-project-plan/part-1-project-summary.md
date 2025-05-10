# Verdict360 Revised Project Plan

## 1. Project Summary (Open-Source Implementation)

Verdict360 is an AI-powered legal intelligence platform designed specifically for legal firms and HR departments to access, interpret, and utilize South African legal information through natural language interaction, implemented with a lean, cost-effective approach using open-source technologies.

### Core Value Proposition

Verdict360 makes complex legal knowledge effortless to access - users can intuitively navigate through legal documents, case law, HR policies, and regulatory information without specialized legal research training.

#### Key Benefits

- **Instant Legal Information Access**: Transform document search into natural conversation
- **South African Legal Context**: Responses that understand South African legal framework, terminology, and precedents
- **Legal Source Integration**: Curated collection of freely available South African legal information
- **Audio Recording & Processing**: Capture hearings and meetings via mobile and generate formatted legal documents
- **Seamless Export**: Convert AI-generated content into rich-text format compatible with word processors

### Target Users

- **Primary**: Legal professionals (attorneys, advocates, paralegals)
- **Secondary**: HR professionals (managers, specialists, consultants)

### Revised Technical Architecture (Open-Source MVP)

```
┌────────────────┐     ┌───────────────────┐
│  Web UI        │ ←→  │  Python FastAPI   │
│  (Next.js)     │     │  Backend          │
└────────────────┘     └───────────────────┘
          ↑                      ↑
          │                      │
          ↓                      ↓
┌────────────────┐     ┌───────────────────┐
│  PostgreSQL +  │     │  MinIO Storage    │
│  Keycloak      │     │  (Self-hosted)    │
└────────────────┘     └───────────────────┘
                              ↑
                              │
                              ↓
                       ┌───────────────────┐
                       │  LangChain +      │
                       │  Ollama + Whisper │
                       └───────────────────┘
          ↑                      ↑
          │                      │
          ↓                      ↓
┌────────────────┐     ┌───────────────────┐
│  Mobile App    │     │  Curated Legal    │
│  (React Native)│     │  Database         │
└────────────────┘     └───────────────────┘
```

### Core Feature Set (Leaner Implementation)

1. **Document Intelligence System**

   - Legal document upload and processing (PDF, DOCX, TXT)
   - Curated South African legal reference collection
   - Text extraction with basic citation recognition
   - Local vector database for semantic search (ChromaDB)

2. **Audio Processing System**

   - Mobile recording of legal proceedings/meetings
   - Self-hosted Whisper for speech-to-text transcription
   - Legal document generation with predefined templates
   - Rich-text export for word processors

3. **Natural Language Legal Interface**

   - Context-aware legal query processing with open-source LLMs
   - South African legal framework knowledge via custom prompts
   - Source citation with basic verification
   - Basic case law reference and retrieval

4. **User & Content Management**
   - Role-based access with Keycloak authentication
   - Simple document version control
   - Generated document management and export
   - Basic usage tracking

Verdict360/
├── web/               # Next.js frontend
├── api/               # Backend API services
├── mobile/            # React Native mobile app
├── docker/            # Docker configuration files
│   └── postgres/
│       └── init-scripts/
│           └── 01-schema.sql
├── docker-compose.yml             # Combined services
├── docker-compose.keycloak.yml    # Keycloak service
├── docker-compose.postgres.yml    # PostgreSQL service
├── docker-compose.minio.yml       # MinIO service
└── .env                           # Environment variables
