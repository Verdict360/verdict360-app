### Week 3: Natural Language Legal Interface & Export (May 21-27, 2025)

#### Detailed Task Checklist

##### Legal Chat Interface

- [ ] Design legal-focused chat UI with case law citation display
- [ ] Implement message bubbles with legal source attribution
- [ ] Add typing indicators and loading states for legal queries
- [ ] Create specialized legal input area with suggestion chips
- [ ] Implement keyboard shortcuts for legal practitioners
- [ ] Add legal source preview capability within chat
- [ ] Create legal citation highlighting and linking

##### Legal RAG Implementation with Open-Source Models

- [ ] Set up Langchain with Ollama integration
- [ ] Create South African legal prompt templates and system messages
- [ ] Implement vector similarity search with ChromaDB
- [ ] Create legal context window with citation preservation
- [ ] Add South African legal framework system prompts (POPIA, Companies Act, etc.)
- [ ] Implement response filtering for legal accuracy
- [ ] Create simple caching system for frequent legal queries

##### Legal Export Functionality

- [ ] Create rich-text export format for legal documents
- [ ] Implement Word document export with proper legal formatting
- [ ] Add proper legal citation formatting in exports
- [ ] Create PDF export with legal document structure
- [ ] Implement document metadata preservation
- [ ] Add configurable export templates for different legal documents
- [ ] Create mobile-friendly export options

##### Legal Source Citations

- [ ] Implement South African case law reference tracking
- [ ] Create clickable case law citations with preview
- [ ] Add statute and regulation references with verification
- [ ] Implement simple legal authority scoring
- [ ] Create citation management with basic hierarchy
- [ ] Add South African citation formatting standards
- [ ] Implement citation extraction and normalization

##### Heads of Argument Generation

- [ ] Create document structure templates for legal arguments
- [ ] Implement legal reasoning extraction from transcripts
- [ ] Add automatic legal authority suggestion
- [ ] Create legal outline generation with hierarchy
- [ ] Implement human-in-the-loop editing interface
- [ ] Add formatting for court submission
- [ ] Create template-based generation system

##### Mobile App Enhancement

- [ ] Integrate transcription status monitoring
- [ ] Add generated document preview in mobile
- [ ] Create recording organization by matter
- [ ] Implement secure sharing of recordings
- [ ] Add basic editing of recording metadata
- [ ] Create offline recording capability with sync
- [ ] Implement battery-efficient background recording

| Task                       | Owner | Status      | Due    |
| -------------------------- | ----- | ----------- | ------ |
| Legal Chat Interface       |       | Not Started | May 21 |
| Legal RAG Implementation   |       | Not Started | May 22 |
| Legal Export Functionality |       | Not Started | May 23 |
| Legal Source Citations     |       | Not Started | May 24 |
| Heads of Argument Gen      |       | Not Started | May 25 |
| Mobile App Enhancement     |       | Not Started | May 26 |

**Week 3 Milestone**: Functional legal chat interface with case law integration and document generation capabilities

#### Week 3 Technical Implementation Details

```typescript
// Legal Chat Interface Component
// components/legal/LegalChatInterface.tsx

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Send, MoreHorizontal, Copy, Download, Bookmark, FileText, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/lib/auth';
import { exportToPdf, exportToWord, copyToClipboard } from '@/lib/utils/export';
import { useToast } from '@/components/ui/use-toast';
import axios from 'axios';

type MessageType = 'user' | 'assistant';

interface Message {
  id: string;
  content: string;
  type: MessageType;
  timestamp: Date;
  sources?: Source[];
  isLoading?: boolean;
}

interface Source {
  id: string;
  title: string;
  citation?: string;
  documentType?: string;
}

export default function LegalChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { token } = useAuth();
  const { toast } = useToast();
  const router = useRouter();
  const { matterId } = router.query;

  useEffect(() => {
    // Scroll to bottom on new messages
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isProcessing) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      type: 'user',
      timestamp: new Date(),
    };

    const tempAssistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: '',
      type: 'assistant',
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages([...messages, userMessage, tempAssistantMessage]);
    setInput('');
    setIsProcessing(true);

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/legal-query/`,
        {
          query: userMessage.content,
          jurisdiction: 'South Africa',
          matterId: matterId || null,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const assistantMessage: Message = {
        id: tempAssistantMessage.id,
        content: response.data.response,
        type: 'assistant',
        timestamp: new Date(),
        sources: response.data.sources,
      };

      setMessages(prev => prev.map(msg => (msg.id === tempAssistantMessage.id ? assistantMessage : msg)));
    } catch (error) {
      console.error('Error processing legal query:', error);

      // Replace temp message with error
      setMessages(prev =>
        prev.map(msg =>
          msg.id === tempAssistantMessage.id
            ? {
                ...msg,
                content: 'I apologize, but I encountered an error processing your query. Please try again.',
                isLoading: false,
              }
            : msg
        )
      );

      toast({
        title: 'Error',
        description: 'Failed to process legal query. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExport = (format: 'pdf' | 'docx') => {
    const content = messages
      .map(
        msg =>
          `${msg.type === 'user' ? 'You' : 'Verdict360'} (${new Date(msg.timestamp).toLocaleTimeString()}):\n${
            msg.content
          }\n\n`
      )
      .join('');

    const title = `Legal Conversation - ${new Date().toLocaleDateString()}`;

    if (format === 'pdf') {
      exportToPdf(content, title);
    } else {
      exportToWord(content, title);
    }
  };

  const highlightCitations = (text: string) => {
    // Basic South African citation patterns
    const citationPatterns = [
      /\d{4}\s+\(\d+\)\s+SA\s+\d+\s+\([A-Z]+\)/g, // 2019 (2) SA 343 (SCA)
      /\[\d{4}\]\s+ZACC\s+\d+/g, // [2021] ZACC 13
      /\[\d{4}\]\s+ZASCA\s+\d+/g, // [2020] ZASCA 99
      /\d{4}\s+\(\d+\)\s+BCLR\s+\d+/g, // 2018 (7) BCLR 844
      /Act\s+No\.\s+\d+\s+of\s+\d{4}/g, // Act No. 71 of 2008
      /Act\s+\d+\s+of\s+\d{4}/g, // Act 71 of 2008
    ];

    let highlightedText = text;

    citationPatterns.forEach(pattern => {
      highlightedText = highlightedText.replace(
        pattern,
        match =>
          `<span class="bg-primary/10 text-primary px-1 rounded cursor-pointer hover:bg-primary/20">${match}</span>`
      );
    });

    return highlightedText;
  };

  return (
    <div className='flex flex-col h-[calc(100vh-10rem)] border rounded-md'>
      {/* Chat Header */}
      <div className='p-4 border-b flex justify-between items-center bg-card'>
        <h2 className='text-lg font-semibold text-primary'>Legal Assistant</h2>
        <div className='flex space-x-2'>
          <Button variant='outline' size='sm' onClick={() => handleExport('pdf')} title='Export as PDF'>
            <Download className='h-4 w-4 mr-2' />
            Export
          </Button>

          <Button variant='outline' size='sm' onClick={() => setMessages([])} title='New Conversation'>
            <FileText className='h-4 w-4 mr-2' />
            New
          </Button>
        </div>
      </div>

      {/* Messages Container */}
      <div className='flex-1 p-4 overflow-y-auto space-y-4 bg-muted/30'>
        {messages.length === 0 ? (
          <div className='text-center p-8 text-muted-foreground'>
            <p>Start a new legal conversation</p>
            <p className='text-sm mt-2'>Ask questions about South African law, case analysis, or legal research</p>
          </div>
        ) : (
          messages.map(message => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-card border'
                }`}>
                {message.isLoading ? (
                  <div className='flex items-center justify-center py-2'>
                    <Loader2 className='h-4 w-4 animate-spin mr-2' />
                    <span className='text-sm'>Researching legal context...</span>
                  </div>
                ) : (
                  <>
                    <div
                      className='prose prose-sm max-w-none'
                      dangerouslySetInnerHTML={{
                        __html: message.type === 'assistant' ? highlightCitations(message.content) : message.content,
                      }}
                    />

                    {message.sources && message.sources.length > 0 && (
                      <div className='mt-3 pt-3 border-t text-xs text-muted-foreground'>
                        <p className='font-semibold mb-1'>Sources:</p>
                        <ul className='list-disc pl-4'>
                          {message.sources.map(source => (
                            <li key={source.id}>
                              {source.title}
                              {source.citation && <span className='ml-1 font-mono'>{source.citation}</span>}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className='mt-2 flex justify-end'>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant='ghost' size='sm' className='h-6 w-6 p-0'>
                            <MoreHorizontal className='h-4 w-4' />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align='end'>
                          <DropdownMenuItem onClick={() => copyToClipboard(message.content)}>
                            <Copy className='h-4 w-4 mr-2' />
                            Copy
                          </DropdownMenuItem>
                          {message.type === 'assistant' && (
                            <>
                              <DropdownMenuItem onClick={() => handleExport('pdf')}>
                                <Download className='h-4 w-4 mr-2' />
                                Export as PDF
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleExport('docx')}>
                                <FileText className='h-4 w-4 mr-2' />
                                Export as Word
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Bookmark className='h-4 w-4 mr-2' />
                                Save to Matter
                              </DropdownMenuItem>
                            </>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className='p-4 border-t bg-card'>
        <div className='flex space-x-2'>
          <Textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder='Type your legal query here...'
            className='flex-1 resize-none'
            rows={2}
            disabled={isProcessing}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <Button type='submit' size='icon' disabled={isProcessing}>
            {isProcessing ? <Loader2 className='h-4 w-4 animate-spin' /> : <Send className='h-4 w-4' />}
          </Button>
        </div>
        <div className='mt-2'>
          <span className='text-xs text-muted-foreground'>
            Integrated with South African legal framework. Press Enter to send, Shift+Enter for new line.
          </span>
        </div>
      </form>
    </div>
  );
}
```

```python
# Legal RAG Implementation with LangChain and Ollama
# app/services/legal_rag.py

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from langchain.llms import Ollama
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from app.models import LegalQuery, Document, DocumentChunk

# Configure embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# Configure Ollama
ollama_llm = Ollama(
    base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    model=os.getenv("OLLAMA_MODEL", "mistral:7b-instruct-v0.2"),
    temperature=0.1
)

# South African Legal System Prompt
SA_LEGAL_SYSTEM_PROMPT = """You are Verdict360, a specialized South African legal assistant. You provide accurate
information based on South African law, case precedents, and legal principles.

Follow these guidelines in all your responses:
1. Always cite specific cases, statutes, or regulations that support your answers using proper South African legal citation format
2. Focus on South African law and jurisdiction
3. Be precise about legal concepts and terminology
4. If you're unsure about a specific legal point, acknowledge the limitations
5. Format citations correctly according to South African legal practice

Important South African Legal Context:
- The Constitution of the Republic of South Africa is the supreme law
- South Africa has a mixed legal system (Roman-Dutch civil law and English common law)
- The court hierarchy: Constitutional Court > Supreme Court of Appeal > High Courts > Magistrates' Courts
- Key legislation includes: Companies Act 71 of 2008, POPIA of 2013, Labour Relations Act 66 of 1995

NEVER make up case citations or legal provisions that do not exist in South African law.
"""

# South African Legal RAG Template
SA_LEGAL_RAG_TEMPLATE = """
{system_prompt}

Use the following pieces of context to answer the user's question about South African law.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

CONTEXT:
{context}

CHAT HISTORY:
{chat_history}

USER QUESTION:
{question}

ANSWER (with proper South African legal citations):
"""

async def initialize_vector_store(persist_directory: str = "./chroma_db"):
    """Initialize vector store for legal documents"""
    return Chroma(
        collection_name="legal_documents",
        embedding_function=embedding_model,
        persist_directory=persist_directory
    )

async def split_document(document_text: str) -> List[Dict[str, Any]]:
    """Split document into chunks with legal context preservation"""
    # Create text splitter optimized for legal documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""],
        keep_separator=True
    )

    # Split document
    chunks = text_splitter.split_text(document_text)

    # Process chunks to extract citations
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        # Extract citations using regex (simplified here)
        citations = extract_legal_citations(chunk)

        processed_chunks.append({
            "content": chunk,
            "chunk_index": i,
            "citations": citations
        })

    return processed_chunks

def extract_legal_citations(text: str) -> List[str]:
    """Extract South African legal citations from text (simplified implementation)"""
    # This would be more sophisticated in a full implementation
    import re

    citation_patterns = [
        r'\d{4}\s+\(\d+\)\s+SA\s+\d+\s+\([A-Z]+\)',  # 2019 (2) SA 343 (SCA)
        r'\[\d{4}\]\s+ZACC\s+\d+',                   # [2021] ZACC 13
        r'\[\d{4}\]\s+ZASCA\s+\d+',                  # [2020] ZASCA 99
        r'\d{4}\s+\(\d+\)\s+BCLR\s+\d+',             # 2018 (7) BCLR 844
    ]

    citations = []
    for pattern in citation_patterns:
        found = re.findall(pattern, text)
        citations.extend(found)

    return citations

async def process_legal_query(
    query_text: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    jurisdiction: str = "South Africa"
) -> Dict[str, Any]:
    """Process legal query using RAG approach with Ollama"""
    try:
        # Initialize vector store
        vector_store = await initialize_vector_store()

        # Create retriever
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )

        # Format conversation history if available
        chat_history = ""
        if conversation_history:
            chat_history = "\n".join([
                f"{'USER' if msg['role'] == 'user' else 'ASSISTANT'}: {msg['content']}"
                for msg in conversation_history[-5:]  # Keep last 5 messages for context
            ])

        # Create prompt
        prompt = PromptTemplate(
            template=SA_LEGAL_RAG_TEMPLATE,
            input_variables=["context", "question", "chat_history"],
            partial_variables={"system_prompt": SA_LEGAL_SYSTEM_PROMPT}
        )

        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=ollama_llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": prompt,
            }
        )

        # Execute query
        result = qa_chain({"query": query_text, "chat_history": chat_history})

        # Extract sources from result
        sources = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                source = {
                    "id": doc.metadata.get("id", ""),
                    "title": doc.metadata.get("title", "Unknown Document"),
                    "document_type": doc.metadata.get("document_type", ""),
                    "jurisdiction": doc.metadata.get("jurisdiction", "South Africa"),
                }

                # Add citations if available
                if "citations" in doc.metadata:
                    source["citations"] = doc.metadata["citations"]

                sources.append(source)

        # Filter out duplicates while preserving order
        unique_sources = []
        seen_ids = set()
        for source in sources:
            if source["id"] not in seen_ids:
                seen_ids.add(source["id"])
                unique_sources.append(source)

        return {
            "response": result["result"],
            "sources": unique_sources[:3],  # Limit to top 3 sources
            "query": query_text
        }

    except Exception as e:
        print(f"Error processing legal query: {str(e)}")
        return {
            "response": "I encountered an error while processing your legal query. Please try again.",
            "sources": [],
            "query": query_text,
            "error": str(e)
        }
```

### Week 4: Polish, Testing & Launch (May 28-June 3, 2025)

#### Detailed Task Checklist

##### Legal Admin Dashboard

- [ ] Create usage statistics dashboard for legal firms
- [ ] Implement document analytics by practice area
- [ ] Add user activity monitoring with legal matter context
- [ ] Create system health indicators for legal operations
- [ ] Implement API usage tracking with cost estimation
- [ ] Add resource allocation visualization for self-hosted deployment
- [ ] Create storage utilization monitoring

##### Legal Quality Assurance

- [ ] Implement legal response verification against sources
- [ ] Create test suite for South African legal queries
- [ ] Add citation accuracy verification
- [ ] Implement legal domain classification validation
- [ ] Create confidence scoring for legal responses
- [ ] Add legal compliance checks for outputs
- [ ] Implement automated model evaluation

##### Performance Optimization

- [ ] Optimize vector search with improved indexing
- [ ] Implement caching for frequent legal queries
- [ ] Add batch processing for document ingestion
- [ ] Optimize mobile app for bandwidth efficiency
- [ ] Implement progressive loading of legal documents
- [ ] Add background processing for transcription jobs
- [ ] Create resource usage monitoring for self-hosted deployment

##### Legal Professional Testing

- [ ] Create testing script with South African legal scenarios
- [ ] Set up test environment with South African legal datasets
- [ ] Recruit 3-5 South African legal professionals for testing
- [ ] Conduct structured testing sessions with attorneys
- [ ] Document feedback from legal practitioners
- [ ] Implement critical fixes based on legal expertise
- [ ] Create benchmark comparison with baseline performance

##### Responsive Design & User Experience

- [ ] Test UI across desktop, tablet, and mobile devices
- [ ] Optimize legal document viewing on mobile
- [ ] Ensure audio playback works across devices
- [ ] Fix touch interaction issues for court settings
- [ ] Optimize loading performance for legal documents
- [ ] Create legal-specific mobile layouts
- [ ] Ensure accessibility compliance

##### Deployment & Launch Preparation

- [ ] Create Docker Compose for production deployment
- [ ] Configure automatic backup systems
- [ ] Implement monitoring and alerting
- [ ] Create deployment documentation for self-hosting
- [ ] Perform security audit with legal data considerations
- [ ] Set up demonstration instance for initial users
- [ ] Create user onboarding guide and tutorials

| Task                       | Owner | Status      | Due    |
| -------------------------- | ----- | ----------- | ------ |
| Legal Admin Dashboard      |       | Not Started | May 28 |
| Legal Quality Assurance    |       | Not Started | May 29 |
| Performance Optimization   |       | Not Started | May 30 |
| Legal Professional Testing |       | Not Started | May 31 |
| Responsive Design & UX     |       | Not Started | June 2 |
| Deployment & Launch        |       | Not Started | June 3 |

**Week 4 Milestone**: Production-ready open-source MVP deployed for initial legal firm testing with full legal citation and document generation functionality

#### Week 4 Technical Implementation Details

```yaml
# docker-compose.production.yml
services:
  # Web Frontend (Next.js)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.production
    container_name: Verdict360-frontend
    restart: always
    ports:
      - '3000:3000'
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=${API_URL}
      - NEXT_PUBLIC_KEYCLOAK_URL=${KEYCLOAK_URL}
      - NEXT_PUBLIC_KEYCLOAK_REALM=${KEYCLOAK_REALM}
      - NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=${KEYCLOAK_CLIENT_ID}
    depends_on:
      - api
    networks:
      - Verdict360-network

  # API Backend (FastAPI)
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    container_name: Verdict360-api
    restart: always
    ports:
      - '8000:8000'
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_HOST=postgres
      - KEYCLOAK_URL=${KEYCLOAK_URL}
      - KEYCLOAK_REALM=${KEYCLOAK_REALM}
      - KEYCLOAK_CLIENT_ID=${KEYCLOAK_API_CLIENT_ID}
      - KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_API_CLIENT_SECRET}
      - OLLAMA_URL=http://ollama:11434
      - OLLAMA_MODEL=${OLLAMA_MODEL}
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
      - MINIO_URL=minio:9000
    volumes:
      - ./backend:/app
      - chroma_data:/app/chroma_db
    depends_on:
      - postgres
      - minio
      - ollama
      - keycloak
    networks:
      - Verdict360-network

  # PostgreSQL Database
  postgres:
    image: postgres:15
    container_name: Verdict360-postgres
    restart: always
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-scripts:/docker-entrypoint-initdb.d
    networks:
      - Verdict360-network
    healthcheck:
      test: ['CMD', 'pg_isready', '-U', '${POSTGRES_USER}']
      interval: 10s
      timeout: 5s
      retries: 5

  # Keycloak Authentication
  keycloak:
    image: quay.io/keycloak/keycloak:21.1.1
    container_name: Verdict360-keycloak
    command: ['start']
    environment:
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres/${POSTGRES_DB}
      - KC_DB_USERNAME=${POSTGRES_USER}
      - KC_DB_PASSWORD=${POSTGRES_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
      - KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN}
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_HTTP_RELATIVE_PATH=/auth
      - KC_PROXY=edge
    volumes:
      - keycloak_data:/opt/keycloak/data
      - ./docker/keycloak/themes:/opt/keycloak/themes
      - ./docker/keycloak/import:/opt/keycloak/data/import
    ports:
      - '8080:8080'
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - Verdict360-network

  # MinIO Object Storage
  minio:
    image: quay.io/minio/minio
    container_name: Verdict360-minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
    volumes:
      - minio_data:/data
    ports:
      - '9000:9000'
      - '9001:9001'
    networks:
      - Verdict360-network
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:9000/minio/health/live']
      interval: 10s
      timeout: 5s
      retries: 3

  # MinIO Setup Service
  minio-setup:
    image: minio/mc
    container_name: Verdict360-minio-setup
    depends_on:
      minio:
        condition: service_healthy
    entrypoint: >
      /bin/sh -c "
      mc alias set myminio http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD};
      mc mb myminio/legal-documents;
      mc mb myminio/legal-recordings;
      mc mb myminio/legal-transcriptions;
      mc policy set download myminio/legal-documents;
      mc policy set download myminio/legal-recordings;
      mc policy set download myminio/legal-transcriptions;
      exit 0;
      "
    networks:
      - Verdict360-network

  # Ollama LLM Service
  ollama:
    image: ollama/ollama:latest
    container_name: Verdict360-ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - '11434:11434'
    networks:
      - Verdict360-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Monitoring (Prometheus & Grafana)
  prometheus:
    image: prom/prometheus
    container_name: Verdict360-prometheus
    volumes:
      - ./docker/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    ports:
      - '9090:9090'
    networks:
      - Verdict360-network

  grafana:
    image: grafana/grafana
    container_name: Verdict360-grafana
    volumes:
      - ./docker/grafana/provisioning:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - '3001:3000'
    depends_on:
      - prometheus
    networks:
      - Verdict360-network

  # Backup Service
  backup:
    image: postgres:15
    container_name: Verdict360-backup
    restart: always
    volumes:
      - ./backups:/backups
      - ./docker/backup/backup.sh:/backup.sh
    environment:
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - BACKUP_SCHEDULE=${BACKUP_SCHEDULE}
    entrypoint: ['/bin/bash', '/backup.sh']
    depends_on:
      - postgres
    networks:
      - Verdict360-network

networks:
  Verdict360-network:
    driver: bridge

volumes:
  postgres_data:
  minio_data:
  ollama_data:
  keycloak_data:
  chroma_data:
  prometheus_data:
  grafana_data:
```

```python
# Legal Quality Assurance Tools
# app/utils/legal_qa.py

import re
import json
import asyncio
from typing import Dict, List, Any, Tuple
from app.services.legal_rag import extract_legal_citations
from app.database import get_async_session
from app.models import Document, CaseLawReference
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Standard South African legal citation patterns
SA_CITATION_PATTERNS = {
    'case_law': [
        r'\d{4}\s+\(\d+\)\s+SA\s+\d+\s+\([A-Z]+\)',  # 2019 (2) SA 343 (SCA)
        r'\[\d{4}\]\s+ZACC\s+\d+',                   # [2021] ZACC 13
        r'\[\d{4}\]\s+ZASCA\s+\d+',                  # [2020] ZASCA 99
        r'\d{4}\s+\(\d+\)\s+BCLR\s+\d+',             # 2018 (7) BCLR 844
    ],
    'statutes': [
        r'Act\s+No\.\s+\d+\s+of\s+\d{4}',            # Act No. 71 of 2008
        r'Act\s+\d+\s+of\s+\d{4}',                   # Act 71 of 2008
    ],
    'regulations': [
        r'GN\s+R\s+\d+',                             # GN R 1234
        r'GG\s+\d+',                                 # GG 43834
    ]
}

# Primary South African legal authorities for validation
PRIMARY_AUTHORITIES = {
    'constitution': [
        'Constitution of the Republic of South Africa, 1996',
        'Constitutional',
        'Constitution',
        'Bill of Rights'
    ],
    'key_statutes': [
        'Companies Act 71 of 2008',
        'Protection of Personal Information Act 4 of 2013',
        'POPIA',
        'Labour Relations Act 66 of 1995',
        'Consumer Protection Act 68 of 2008',
        'National Credit Act 34 of 2005'
    ]
}

async def validate_legal_response(query: str, response: str) -> Dict[str, Any]:
    """Validate a legal response for quality and accuracy"""
    # Extract citations from response
    citations = extract_legal_citations(response)

    # Check for citation validity
    citation_validity = await check_citation_validity(citations)

    # Check for legal terminology usage
    legal_terminology_score = check_legal_terminology(response)

    # Check for answer relevance to query
    relevance_score = calculate_relevance_score(query, response)

    # Check for hedging language (unwanted in legal opinions)
    hedging_score = check_hedging_language(response)

    # Calculate overall quality score
    quality_score = (
        citation_validity['validity_score'] * 0.4 +
        legal_terminology_score * 0.3 +
        relevance_score * 0.2 +
        hedging_score * 0.1
    )

    return {
        "quality_score": quality_score,
        "citation_analysis": citation_validity,
        "legal_terminology_score": legal_terminology_score,
        "relevance_score": relevance_score,
        "hedging_score": hedging_score,
        "quality_level": get_quality_level(quality_score),
        "improvement_suggestions": generate_improvement_suggestions(
            citation_validity,
            legal_terminology_score,
            relevance_score,
            hedging_score
        )
    }

async def check_citation_validity(citations: List[str]) -> Dict[str, Any]:
    """Check if the citations are valid in the database"""
    valid_citations = 0
    invalid_citations = []

    async with get_async_session() as session:
        for citation in citations:
            # Check case law references
            result = await session.execute(
                select(CaseLawReference).where(CaseLawReference.citation == citation)
            )
            reference = result.scalars().first()

            if reference:
                valid_citations += 1
            else:
                invalid_citations.append(citation)

    # Calculate validity score (0-1)
    validity_score = valid_citations / max(len(citations), 1)

    return {
        "total_citations": len(citations),
        "valid_citations": valid_citations,
        "invalid_citations": invalid_citations,
        "validity_score": validity_score
    }

def check_legal_terminology(text: str) -> float:
    """Check for South African legal terminology usage (0-1 score)"""
    legal_terms = [
        'constitutional', 'supreme court', 'high court', 'magistrates\' court',
        'roman-dutch', 'common law', 'delict', 'ubuntu', 'stare decisis',
        'constitutional democracy', 'reasonable person', 'boni mores',
        'juristic person', 'prescription', 'doctrine', 'judicial precedent',
        'contempt of court', 'plaintiff', 'defendant', 'appellant', 'respondent',
        'rule of law', 'public interest', 'justice', 'equity', 'statute', 'regulation'
    ]

    # Count legal terms
    term_count = sum(1 for term in legal_terms if term.lower() in text.lower())

    # Normalize score (0-1)
    max_expected_terms = 10  # Adjust based on expected density
    score = min(term_count / max_expected_terms, 1.0)

    return score

def calculate_relevance_score(query: str, response: str) -> float:
    """Calculate relevance of response to query (simplified implementation)"""
    # This would use more sophisticated NLP in production
    query_keywords = set(query.lower().split())
    response_words = set(response.lower().split())

    # Calculate overlap
    overlap = query_keywords.intersection(response_words)
    relevance_score = len(overlap) / max(len(query_keywords), 1)

    return relevance_score

def check_hedging_language(text: str) -> float:
    """Check for hedging language (unwanted in legal opinions) - returns 0-1 score
    where 1 = minimal hedging (good)"""
    hedging_terms = [
        'might be', 'could be', 'perhaps', 'possibly', 'maybe',
        'I think', 'probably', 'seems like', 'appears to be', 'kind of',
        'sort of', 'somewhat', 'relatively', 'potentially', 'conceivably'
    ]

    # Count hedging terms
    hedging_count = sum(1 for term in hedging_terms if term.lower() in text.lower())

    # Calculate score (1 = no hedging, 0 = lots of hedging)
    # Allow up to 3 hedging terms without penalty
    score = max(0, 1 - ((hedging_count - 3) / 10))

    return max(min(score, 1.0), 0.0)  # Clamp between 0-1

def get_quality_level(score: float) -> str:
    """Get quality level based on score"""
    if score >= 0.9:
        return "Excellent"
    elif score >= 0.8:
        return "Very Good"
    elif score >= 0.7:
        return "Good"
    elif score >= 0.6:
        return "Satisfactory"
    elif score >= 0.5:
        return "Needs Improvement"
    else:
        return "Insufficient"

def generate_improvement_suggestions(
    citation_validity: Dict[str, Any],
    legal_terminology_score: float,
    relevance_score: float,
    hedging_score: float
) -> List[str]:
    """Generate improvement suggestions based on quality analysis"""
    suggestions = []

    # Citation suggestions
    if citation_validity['validity_score'] < 0.7:
        suggestions.append(
            "Include more valid legal citations to support the response."
        )
        if citation_validity['invalid_citations']:
            suggestions.append(
                f"Check the accuracy of these citations: {', '.join(citation_validity['invalid_citations'][:3])}"
            )

    # Legal terminology suggestions
    if legal_terminology_score < 0.6:
        suggestions.append(
            "Use more South African legal terminology to improve accuracy."
        )

    # Relevance suggestions
    if relevance_score < 0.6:
        suggestions.append(
            "Make the response more directly relevant to the query."
        )

    # Hedging language suggestions
    if hedging_score < 0.7:
        suggestions.append(
            "Reduce hedging language for a more authoritative legal opinion."
        )

    # Default suggestion if all scores are good
    if not suggestions:
        suggestions.append(
            "Response quality is good. Continue maintaining citation accuracy."
        )

    return suggestions
```

## 5. South African Context Considerations (Open-Source Implementation)

### South African Legal Framework Integration

#### Key Legislation for Initial Focus

- **Constitution of the Republic of South Africa, 1996**
  - Bill of Rights (Chapter 2)
  - Constitutional principles and interpretation
  - Constitutional Court judgments
- **Companies Act 71 of 2008**
  - Company formation and governance
  - Director duties and liabilities
  - Business rescue and liquidation
- **Protection of Personal Information Act 4 of 2013 (POPIA)**
  - Data protection principles
  - Processing limitations
  - Responsible party obligations
- **Labour Relations Act 66 of 1995**
  - Employment contracts
  - Dismissal procedures
  - Dispute resolution mechanisms
- **Consumer Protection Act 68 of 2008**
  - Consumer rights
  - Unfair business practices
  - Product liability

### Open-Source Data Sources for Legal Content

1. **Freely Available Legal Resources**

   - **SAFLII (South African Legal Information Institute)** - Public legal information
   - **Government Gazettes** - Publicly accessible legal records
   - **Open Government Data Portal** - Public sector information
   - **Parliament of South Africa website** - Legislative information
   - **South African Government website** - Policy documents

2. **Legal Citation Standards**

   - South African Law Reports (SALR) citation format
   - South African Law Journal (SALJ) referencing style
   - Jutastat citation methodologies

3. **Data Gathering Methodology**
   - Web scraping with proper respect for terms of service
   - Bulk downloads where available
   - Manual curation and verification
   - Community contribution system for legal professionals

### South African Legal Terminology

- Roman-Dutch law terminology
- South African legal Latin expressions
- Indigenous legal concepts (e.g., Ubuntu)
- Specialized regulatory terminology

### Custom Prompt Engineering for South African Context

- Creating legal system prompts with South African legal principles
- Developing citation formatting specific to South African style
- Training retrieval systems on South African legal vocabulary
- Including jurisdictional context in all responses
- Implementing legal hierarchy understanding in search algorithms

### Target Legal Practitioners

1. **Attorneys**

   - Corporate/commercial attorneys
   - Labour law specialists
   - Litigation attorneys
   - Compliance officers

2. **Legal Consultants**

   - Legal researchers
   - Law firm knowledge managers
   - Legal tech specialists
   - Paralegals

3. **HR Professionals**
   - HR managers
   - Employee relations specialists
   - Compliance officers
   - Industrial relations practitioners

### Industry-Specific Focus (Priority Order)

1. Law firms (primary focus)
   - Corporate/commercial practices
   - Litigation departments
   - Employment law specialists
2. Corporate legal departments (secondary)
   - In-house legal teams
   - Compliance departments
   - Corporate secretarial functions
3. HR departments (tertiary)
   - Employee relations teams
   - Compliance specialists
   - Policy administrators

### Language Considerations

- **MVP**: English only (South African English spelling variations)
- **Legal Terminology**: South African legal English with appropriate legal Latin phrases
- **Future Expansion**: Consider official South African languages based on user demand and priorities

## 6. Open-Source Maintenance & Contribution

### Community Development Model

1. **Open-Source Repository Structure**

   - GitHub organization with public repositories
   - Comprehensive documentation and examples
   - Contribution guidelines and code of conduct
   - Issue templates for legal enhancements

2. **Legal Data Contribution**

   - Process for legal professionals to contribute documents
   - Citation verification workflows
   - Legal domain tagging system
   - Quality control for submitted content

3. **Model Improvements**
   - Fine-tuning guides for legal domain adaptation
   - Benchmark datasets for South African legal tasks
   - Performance evaluation methodology
   - Model versioning and compatibility

### Sustainable Open-Source Strategy

1. **Community Building**

   - Legal technology meetups and events
   - Academic partnerships with law faculties
   - Legal practitioner user groups
   - Technical education and knowledge sharing

2. **Long-term Maintenance**

   - Regular security updates
   - Performance optimizations
   - Compatibility updates for ecosystem changes
   - Documentation improvements

3. **Optional Commercial Services**
   - Professional support subscriptions
   - Custom implementation assistance
   - Specialized legal data integration
   - Training and onboarding services
