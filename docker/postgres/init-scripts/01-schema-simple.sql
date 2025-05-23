-- Create tables for users, matters, documents, recordings, etc.
CREATE TABLE IF NOT EXISTS legal_users (
    id SERIAL PRIMARY KEY,
    keycloak_id VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    firm_name VARCHAR(255),
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS legal_matters (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    reference_number VARCHAR(100),
    client_id INTEGER REFERENCES legal_users(id),
    practice_area VARCHAR(100),
    responsible_attorney INTEGER REFERENCES legal_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS legal_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_type VARCHAR(100) NOT NULL,
    jurisdiction VARCHAR(100) NOT NULL DEFAULT 'South Africa',
    matter_id INTEGER REFERENCES legal_matters(id),
    storage_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    created_by INTEGER REFERENCES legal_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    confidentiality_level VARCHAR(50) NOT NULL DEFAULT 'standard'
);

CREATE TABLE IF NOT EXISTS legal_recordings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    matter_id INTEGER REFERENCES legal_matters(id),
    storage_path VARCHAR(500) NOT NULL,
    duration_seconds INTEGER,
    transcription_status VARCHAR(50) DEFAULT 'pending',
    transcription_path VARCHAR(500),
    created_by INTEGER REFERENCES legal_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    recording_date TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS legal_transcriptions (
    id SERIAL PRIMARY KEY,
    recording_id INTEGER REFERENCES legal_recordings(id),
    text_content TEXT NOT NULL,
    language VARCHAR(50) DEFAULT 'en',
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create document chunks table without vector for now (we'll add pgvector later)
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES legal_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create case law reference table
CREATE TABLE IF NOT EXISTS case_law_references (
    id SERIAL PRIMARY KEY,
    citation VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    jurisdiction VARCHAR(100) NOT NULL DEFAULT 'South Africa',
    court VARCHAR(100),
    year INTEGER,
    document_id INTEGER REFERENCES legal_documents(id),
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    relevance_score FLOAT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_document_chunks_metadata ON document_chunks USING GIN (metadata jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_legal_documents_type ON legal_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_legal_documents_jurisdiction ON legal_documents(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_legal_matters_practice_area ON legal_matters(practice_area);
CREATE INDEX IF NOT EXISTS idx_case_law_references_citation ON case_law_references(citation);
CREATE INDEX IF NOT EXISTS idx_case_law_references_court_year ON case_law_references(court, year);
