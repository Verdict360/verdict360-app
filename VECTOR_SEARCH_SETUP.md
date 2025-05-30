# Verdict360 Vector Search Setup

## Overview
This document outlines the vector search functionality added to Verdict360, enabling semantic search across legal documents using ChromaDB and sentence transformers.

## Features Added

### 1. Vector Storage Service (`api-python/app/services/vector_store.py`)
- ChromaDB integration for persistent vector storage
- Sentence transformer embeddings (`all-MiniLM-L6-v2`)
- Legal metadata handling (citations, legal terms, jurisdiction)
- Document chunking optimised for legal content
- Semantic similarity search

### 2. Enhanced Document Processor
- Automatic vector embedding generation during document upload
- South African legal citation detection
- Legal term extraction
- Document structure analysis
- Integration with existing MinIO storage

### 3. Search API Endpoints
- `POST /documents/search` - Semantic document search
- `GET /documents/vector-stats` - Vector database statistics
- `GET /documents/{id}/similar` - Find similar documents

### 4. Web Interface
- Legal Search page with advanced filters
- Document type and jurisdiction filtering
- Similarity score display
- Citation and legal term highlighting
- Responsive design with your brand colours

## Installation & Setup

### 1. Install Python Dependencies
```bash
cd api-python
pip install -r requirements-week2-enhanced.txt
