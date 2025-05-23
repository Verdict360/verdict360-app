-- Insert test users (these will be synced with Keycloak)
INSERT INTO legal_users (keycloak_id, email, full_name, firm_name, role) VALUES
    ('admin-keycloak-id', 'admin@verdict360.org', 'Admin User', 'Verdict360', 'admin'),
    ('attorney1-keycloak-id', 'sarah@example.com', 'Sarah Advocate', 'Example Legal Firm', 'attorney'),
    ('paralegal1-keycloak-id', 'james@example.com', 'James Support', 'Example Legal Firm', 'paralegal'),
    ('client1-keycloak-id', 'thomas@example.com', 'Thomas Client', NULL, 'client')
ON CONFLICT (keycloak_id) DO NOTHING;

-- Insert test legal matters
INSERT INTO legal_matters (title, reference_number, practice_area, status) VALUES
    ('Contract Dispute - ABC Corp', 'MAT-2025-001', 'Commercial Law', 'active'),
    ('Employment Termination Case', 'MAT-2025-002', 'Labour Law', 'active'),
    ('Property Transfer Agreement', 'MAT-2025-003', 'Property Law', 'active'),
    ('Compliance Review - XYZ Ltd', 'MAT-2025-004', 'Corporate Law', 'active'),
    ('Personal Injury Claim', 'MAT-2025-005', 'Civil Litigation', 'pending');

-- Insert sample case law references
INSERT INTO case_law_references (citation, title, jurisdiction, court, year, summary) VALUES
    ('2019 (2) SA 343 (SCA)', 'Example Commercial Case v Another Company', 'South Africa', 'Supreme Court of Appeal', 2019, 'Leading case on commercial contract interpretation'),
    ('[2021] ZACC 13', 'Constitutional Rights Case', 'South Africa', 'Constitutional Court', 2021, 'Landmark constitutional interpretation case'),
    ('2020 (5) BCLR 123 (GP)', 'Labour Dispute Example', 'South Africa', 'Gauteng High Court', 2020, 'Employment law precedent'),
    ('2018 (3) SA 456 (WCC)', 'Property Law Case Study', 'South Africa', 'Western Cape High Court', 2018, 'Property transfer and ownership rights'),
    ('[2022] ZASCA 45', 'Corporate Governance Matter', 'South Africa', 'Supreme Court of Appeal', 2022, 'Directors duties and corporate responsibility')
ON CONFLICT (citation) DO NOTHING;

-- Insert document type templates for testing
CREATE TABLE IF NOT EXISTS document_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    template_content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO document_templates (name, document_type, template_content) VALUES
    ('Contract of Sale Template', 'contract', 'This is a template for a basic contract of sale under South African law...'),
    ('Employment Contract Template', 'contract', 'Standard employment contract template compliant with Labour Relations Act...'),
    ('Legal Opinion Template', 'opinion', 'Template for legal opinion documents with proper South African legal structure...'),
    ('Pleading Template', 'pleading', 'Standard pleading template for South African court proceedings...');

-- Insert sample configuration data
CREATE TABLE IF NOT EXISTS system_config (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO system_config (key, value, description) VALUES
    ('default_jurisdiction', 'South Africa', 'Default jurisdiction for legal documents'),
    ('firm_name', 'Example Legal Firm', 'Default firm name for development'),
    ('currency', 'ZAR', 'Default currency (South African Rand)'),
    ('date_format', 'DD/MM/YYYY', 'Default date format for South African locale'),
    ('max_upload_size', '20971520', 'Maximum file upload size in bytes (20MB)'),
    ('retention_period_years', '7', 'Default document retention period in years'),
    ('backup_frequency_hours', '24', 'Backup frequency in hours')
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    updated_at = CURRENT_TIMESTAMP;
