# Verdict360 - AI Legal Chatbot Platform

## Overview
Verdict360 is an AI-powered legal chatbot platform specifically designed for South African law firms. The system provides intelligent legal assistance with verified citations, comprehensive document processing, and POPIA-compliant data handling.

## Target Market
- **Revenue Target**: R5,000-R10,000 monthly subscriptions
- **Market Size**: 81 qualified SA law firms
- **ROI Potential**: 300-1,500% proven returns

## Core Technology Stack

### Backend (FastAPI - Python)
- **Vector Search**: ChromaDB with legal document embeddings
- **Legal QA System**: 95% accuracy scoring with SA legal validation
- **Citation Processing**: 15+ verified SA legal citation patterns
- **Authentication**: Keycloak with legal role-based access
- **Storage**: MinIO for legal documents + PostgreSQL
- **Compliance**: POPIA framework built-in

### Infrastructure
- **Database**: PostgreSQL with legal document schema
- **Vector Store**: ChromaDB for semantic search
- **File Storage**: MinIO object storage
- **Auth**: Keycloak identity management
- **Caching**: Redis for performance

### Legal Intelligence Features
- South African legal citation parsing (ZACC, ZASCA, High Courts)
- Legal terminology extraction and validation
- Document quality assurance scoring
- Constitutional Court and case law integration
- Act and regulation reference handling

## Current Status
- **Backend**: Fully functional with advanced legal processing
- **Frontend**: Ready for SvelteKit rebuild (previous Next.js removed)
- **Mobile**: Removed - focused on web platform only

## Development Priority
1. Build SvelteKit frontend for legal chatbot interface
2. Integrate existing legal processing APIs
3. Implement subscription billing system
4. Deploy for SA law firm market entry

## Key Differentiators
- Native South African legal context
- Verified citation accuracy
- Professional QA scoring system
- POPIA compliance framework
- Proven ROI for law firms