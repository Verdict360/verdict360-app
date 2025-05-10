## 2. Project Instructions (Open-Source Implementation)

### Objective

Create a minimum viable product (MVP) within 3-4 weeks that demonstrates the core value proposition, focusing on web-based access and basic mobile audio recording capability, while minimizing costs through open-source technologies.

### Revised Tech Stack (Open-Source Alternatives)

#### MVP Tech Stack

- **Frontend**: Next.js with TypeScript, Tailwind CSS, shadcn/ui components (free/open-source)
- **Backend**: Python FastAPI for AI/ML components, Next.js API routes for UI operations
- **Authentication**: 
  - **Keycloak** (open-source identity and access management)
  - Alternative: **Lucia Auth** (lightweight auth library for JS)
- **Database**: 
  - **PostgreSQL** (self-hosted)
  - **pgvector** extension for vector operations
- **Storage**: 
  - **MinIO** (self-hosted S3-compatible object storage)
  - Alternative: Local file system storage for early MVP
- **Mobile App**: React Native for iOS/Android with audio recording capabilities
- **AI Components**:
  - **Vector Store**: 
    - **ChromaDB** (embedded vector database)
    - **Qdrant** (self-hosted vector database)
  - **LLM Integration**: 
    - **Ollama** (local model hosting)
    - **LangChain** (open-source framework)
    - Models: Mistral 7B, Llama 3 8B
  - **Speech-to-Text**: 
    - Self-hosted **Whisper** (open-source model)
    - Alternative: **Vosk** for lightweight implementation
  - **Document Processing**: 
    - **PyPDF2**/**pdfminer**
    - **python-docx**
    - **langchain.document_loaders**
- **Legal Integration**:
  - Curated dataset of freely available South African legal documents
  - Custom citation parser and validator
  - Legal document template engine
- **Hosting**:
  - **GitHub Pages** or **Netlify** (free tier for web frontend)
  - **Oracle Cloud Free Tier** or personal server (backend)
  - Self-hosted PostgreSQL and MinIO on the same infrastructure

#### Development Principles (Cost-Conscious Approach)

1. **Legal-First Design**: Optimize for legal workflows and South African legal context
2. **Resource Efficiency**: Design for minimal resource usage with lightweight models
3. **Modular Architecture**: Allow easy replacement of components as project scales
4. **Progressive Enhancement**: Start with core features, add sophistication gradually
5. **South African Context**: Ensure relevance to SA legal framework and terminology
6. **Documentation First**: Document architecture decisions with focus on cost/benefit
7. **Containerization**: Use Docker for consistent development and deployment

### MVP Core Features (Revised for Open-Source Implementation)

1. **Legal Document Intelligence System**

   - Document upload with basic document type detection
   - Text extraction with simple citation pattern matching
   - Custom South African legal context prompts for model
   - Vector embeddings via smaller open-source embedding models
   - Basic semantic search with local vector database
   - Document preview with simple citation highlighting

2. **Legal Database Component**

   - Curated collection of freely available South African legal documents
   - Basic case law retrieval by keyword and citation
   - Simple legal source integration with credibility scores
   - Search across local document collection
   - Export of source lists with proper legal citation format
   - Future path for integration with commercial databases

3. **Audio Recording & Processing**

   - Mobile app for recording legal proceedings
   - Secure audio storage in MinIO or local storage
   - Self-hosted Whisper for speech-to-text transcription
   - Basic speaker separation in transcripts
   - Template-based legal document generation
   - Simple rich-text export formats

4. **Natural Language Legal Interface**

   - Legal query processing with custom-prompted open models
   - Basic case law and statute reference recognition
   - Context-aware responses with South African legal prompts
   - Simple source citation
   - Conversation history with basic categorization
   - Query suggestions for legal clarity

5. **User & Content Management**
   - Keycloak-based authentication and authorization
   - Basic role definitions (attorney, paralegal, staff)
   - Document-level access controls
   - Lightweight usage tracking for system improvement
   - Simple activity logging for basic compliance

### Open-Source Model Considerations

1. **LLM Selection**:
   - **Mistral 7B** - Good balance of performance and resource requirements
   - **Llama 3 8B** - Strong reasoning capabilities for legal contexts
   - **MPT-7B-Instruct** - Alternative option optimized for instruction following

2. **Embedding Models**:
   - **all-MiniLM-L6-v2** - Efficient sentence embeddings from Hugging Face
   - **BGE-small** - Optimized for retrieval tasks, lightweight

3. **Resource Requirements**:
   - Minimum 16GB RAM server for model hosting
   - GPU optional but recommended for transcription processing
   - CPU-only deployment possible with longer processing times

### Data Privacy & Security Considerations

1. **Data Sovereignty**:
   - All data remains on self-hosted infrastructure
   - No dependency on external API services
   - Complete control over sensitive legal information

2. **Authentication**:
   - Self-hosted Keycloak provides enterprise-grade security
   - Multi-factor authentication options
   - Role-based access control

3. **Encryption**:
   - Data encryption at rest in MinIO
   - TLS for all communications
   - Client-side encryption options for highly sensitive documents
