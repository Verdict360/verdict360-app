-- Verdict360 Legal Chatbot Database Schema Extensions
-- Conversations, Consultations, and Voice Integration Tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Conversations table for chat session management
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    legal_matter_context TEXT,
    legal_area VARCHAR(100),
    jurisdiction VARCHAR(100) DEFAULT 'South Africa',
    status VARCHAR(50) DEFAULT 'active',
    escalation_reason TEXT,
    escalated_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    last_message_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_conversations_session_id (session_id),
    INDEX idx_conversations_user_id (user_id),
    INDEX idx_conversations_status (status),
    INDEX idx_conversations_legal_area (legal_area),
    INDEX idx_conversations_created_at (created_at)
);

-- Messages table for individual chat messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'assistant')),
    metadata JSONB DEFAULT '{}',
    qa_score FLOAT DEFAULT 0.0,
    qa_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_messages_conversation_id (conversation_id),
    INDEX idx_messages_type (message_type),
    INDEX idx_messages_created_at (created_at),
    INDEX idx_messages_qa_score (qa_score)
);

-- Consultations table for appointment booking
CREATE TABLE consultations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_name VARCHAR(255) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    client_phone VARCHAR(50),
    legal_area VARCHAR(100) NOT NULL,
    urgency_level VARCHAR(20) DEFAULT 'normal' CHECK (urgency_level IN ('low', 'normal', 'high', 'critical')),
    matter_description TEXT NOT NULL,
    matter_priority VARCHAR(20) DEFAULT 'normal',
    consultation_type VARCHAR(50) DEFAULT 'consultation',
    
    -- Scheduling details
    preferred_date DATE,
    preferred_time TIME,
    scheduled_date DATE,
    scheduled_time TIME,
    estimated_duration_minutes INTEGER DEFAULT 60,
    estimated_cost DECIMAL(10, 2),
    
    -- Assignment and status
    status VARCHAR(50) DEFAULT 'pending_assignment',
    assigned_lawyer_id VARCHAR(255),
    assigned_lawyer_name VARCHAR(255),
    
    -- Metadata
    matter_analysis JSONB DEFAULT '{}',
    preparation_notes TEXT,
    cancellation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_consultations_client_email (client_email),
    INDEX idx_consultations_legal_area (legal_area),
    INDEX idx_consultations_status (status),
    INDEX idx_consultations_urgency (urgency_level),
    INDEX idx_consultations_scheduled_date (scheduled_date),
    INDEX idx_consultations_created_at (created_at)
);

-- Voice calls table for call session management
CREATE TABLE voice_calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consultation_id UUID REFERENCES consultations(id) ON DELETE SET NULL,
    retell_call_id VARCHAR(255),
    client_phone VARCHAR(50) NOT NULL,
    call_type VARCHAR(50) DEFAULT 'consultation',
    
    -- Call details
    status VARCHAR(50) DEFAULT 'initiated',
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    
    -- Legal context
    legal_context JSONB DEFAULT '{}',
    legal_summary TEXT,
    escalation_reason TEXT,
    escalated_at TIMESTAMP,
    
    -- Voice settings
    voice_settings JSONB DEFAULT '{}',
    
    -- Metadata
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_voice_calls_consultation_id (consultation_id),
    INDEX idx_voice_calls_retell_id (retell_call_id),
    INDEX idx_voice_calls_status (status),
    INDEX idx_voice_calls_started_at (started_at)
);

-- Voice call transcripts table
CREATE TABLE voice_transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    voice_call_id UUID NOT NULL REFERENCES voice_calls(id) ON DELETE CASCADE,
    speaker VARCHAR(20) NOT NULL,
    text TEXT NOT NULL,
    timestamp_seconds FLOAT,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_voice_transcripts_call_id (voice_call_id),
    INDEX idx_voice_transcripts_speaker (speaker),
    INDEX idx_voice_transcripts_timestamp (timestamp_seconds)
);

-- Workflow triggers table for N8N integration tracking
CREATE TABLE workflow_triggers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trigger_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    webhook_url TEXT,
    trigger_data JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    response_data JSONB DEFAULT '{}',
    error_message TEXT,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_workflow_triggers_type (trigger_type),
    INDEX idx_workflow_triggers_entity (entity_type, entity_id),
    INDEX idx_workflow_triggers_status (status),
    INDEX idx_workflow_triggers_triggered_at (triggered_at)
);

-- Consultation availability table for lawyer scheduling
CREATE TABLE lawyer_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lawyer_id VARCHAR(255) NOT NULL,
    lawyer_name VARCHAR(255) NOT NULL,
    legal_areas TEXT[] NOT NULL, -- Array of legal practice areas
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    consultation_id UUID REFERENCES consultations(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_lawyer_availability_lawyer_id (lawyer_id),
    INDEX idx_lawyer_availability_date (date),
    INDEX idx_lawyer_availability_available (is_available),
    UNIQUE INDEX idx_lawyer_availability_unique (lawyer_id, date, start_time)
);

-- Legal matter urgency classification table
CREATE TABLE legal_matter_classifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    matter_description TEXT NOT NULL,
    predicted_urgency VARCHAR(20) NOT NULL,
    predicted_legal_area VARCHAR(100) NOT NULL,
    confidence_score FLOAT NOT NULL,
    classification_metadata JSONB DEFAULT '{}',
    human_validated BOOLEAN DEFAULT FALSE,
    actual_urgency VARCHAR(20),
    actual_legal_area VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_matter_classifications_urgency (predicted_urgency),
    INDEX idx_matter_classifications_legal_area (predicted_legal_area),
    INDEX idx_matter_classifications_confidence (confidence_score),
    INDEX idx_matter_classifications_validated (human_validated)
);

-- Create triggers for updating timestamps
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conversations_modtime BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_consultations_modtime BEFORE UPDATE ON consultations FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_voice_calls_modtime BEFORE UPDATE ON voice_calls FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Insert sample data for testing

-- Sample lawyer availability
INSERT INTO lawyer_availability (lawyer_id, lawyer_name, legal_areas, date, start_time, end_time) VALUES
('lawyer_001', 'Advocate Sarah Mthembu', ARRAY['criminal', 'constitutional'], CURRENT_DATE + INTERVAL '1 day', '09:00', '12:00'),
('lawyer_001', 'Advocate Sarah Mthembu', ARRAY['criminal', 'constitutional'], CURRENT_DATE + INTERVAL '1 day', '14:00', '17:00'),
('lawyer_002', 'Attorney Johan van der Merwe', ARRAY['commercial', 'civil'], CURRENT_DATE + INTERVAL '1 day', '08:00', '12:00'),
('lawyer_003', 'Attorney Nomsa Radebe', ARRAY['family', 'property'], CURRENT_DATE + INTERVAL '2 days', '09:00', '16:00');

-- Sample legal matter classifications for training data
INSERT INTO legal_matter_classifications (matter_description, predicted_urgency, predicted_legal_area, confidence_score) VALUES
('I need help with a divorce and child custody', 'normal', 'family', 0.92),
('Police arrested me this morning', 'critical', 'criminal', 0.98),
('Contract dispute with business partner', 'normal', 'commercial', 0.85),
('Property transfer not completed', 'normal', 'property', 0.88),
('Constitutional rights violation by government', 'high', 'constitutional', 0.94);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO Verdict360;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO Verdict360;

-- Add comments for documentation
COMMENT ON TABLE conversations IS 'Chat conversation sessions with legal context';
COMMENT ON TABLE messages IS 'Individual messages within chat conversations';
COMMENT ON TABLE consultations IS 'Legal consultation booking requests and scheduling';
COMMENT ON TABLE voice_calls IS 'Voice consultation call sessions via Retell AI';
COMMENT ON TABLE voice_transcripts IS 'Transcription segments from voice calls';
COMMENT ON TABLE workflow_triggers IS 'N8N workflow trigger tracking and status';
COMMENT ON TABLE lawyer_availability IS 'Lawyer scheduling and availability management';
COMMENT ON TABLE legal_matter_classifications IS 'ML training data for legal matter classification';