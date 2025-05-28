### Week 2: Core Open-Source Functionality (May 14-20, 2025)

#### Detailed Task Checklist

##### Legal Document Upload & Processing

- [x] Create drag & drop interface for legal documents
- [x] Implement document type validation (statutes, judgments, contracts)
- [x] Add progress indicators for uploads with size estimation
- [x] Set up direct upload to MinIO storage with client-matter tagging
- [x] Handle multiple file uploads with batch processing
- [x] Add document validation and error handling
- [x] Implement MinIO client for document retrieval

##### Audio Recording Integration (Mobile)

- [ ] Implement secure audio recording in React Native
- [ ] Create recording interface with legal proceeding metadata
- [ ] Add pause/resume/stop functionality
- [ ] Implement background recording capability
- [ ] Create audio review before upload feature
- [ ] Add upload to MinIO storage when connectivity available
- [ ] Implement offline storage with sync capabilities

##### Python FastAPI Backend Setup

- [ ] Set up Python virtual environment with legal NLP packages
- [ ] Initialize FastAPI project with legal processing endpoints
- [ ] Create document and audio processing routes
- [ ] Set up Keycloak client for authentication validation
- [ ] Implement JWT validation for legal data security
- [ ] Create Docker configuration for deployment
- [ ] Configure Ollama integration for LLM access

##### Legal Text Extraction & Citation Detection

- [x] Implement PDF text extraction with PyPDF2/pdfminer.six
- [x] Add DOCX parsing with python-docx
- [x] Create TXT file processing with legal structure detection
- [x] Implement regex-based citation recognition for South African cases
- [ ] Add South African case law reference detection
- [ ] Create extraction job queue with background workers
- [ ] Implement language detection for multilingual support

##### Self-Hosted Whisper Transcription

- [ ] Set up self-hosted Whisper model (CPU version)
- [ ] Create audio preprocessing pipeline for optimal results
- [ ] Implement chunking for large audio files
- [ ] Add automatic language detection
- [ ] Create asynchronous processing with progress reporting
- [ ] Implement webhook callbacks on completion
- [ ] Add basic speaker diarization capabilities

##### Vector Processing for Legal Content

- [ ] Set up sentence-transformers with all-MiniLM-L6-v2
- [ ] Implement legal document chunking with context preservation
- [ ] Create embedding generation pipeline
- [ ] Add South African legal context metadata
- [ ] Implement document classification with lightweight models
- [ ] Configure ChromaDB for vector storage and retrieval
- [ ] Create search API for semantic similarity

##### Legal Database Curation

- [ ] Create script for harvesting freely available South African legal documents
- [ ] Implement citation parser and normalizer
- [ ] Add document categorization by legal domain
- [ ] Create storage structure for efficient retrieval
- [ ] Implement basic search functionality
- [ ] Add citation validation against curated dataset
- [ ] Create API for legal document retrieval

| Task                             | Owner | Status      | Due    |
| -------------------------------- | ----- | ----------- | ------ |
| Legal Document Upload Processing |       | Not Started | May 14 |
| Audio Recording Integration      |       | Not Started | May 15 |
| Python FastAPI Backend           |       | Not Started | May 16 |
| Legal Text Extraction            |       | Not Started | May 17 |
| Self-Hosted Whisper              |       | Not Started | May 18 |
| Vector Processing Setup          |       | Not Started | May 19 |
| Legal Database Curation          |       | Not Started | May 20 |

**Week 2 Milestone**: Functional legal document processing pipeline and audio recording/transcription capability, all using open-source technologies

#### Week 2 Technical Implementation Details

```python
# FastAPI Backend with Ollama LLM Integration
# app/main.py

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import asyncio
from app.dependencies import get_current_user
from app.services import document_processor, audio_processor, vector_store
from app.models import DocumentCreate, RecordingCreate, LegalQuery

app = FastAPI(title="Verdict360 Legal API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama API Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct-v0.2")

# API routes for legal document processing
@app.post("/documents/", response_model=dict)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    matter_id: Optional[str] = Form(None),
    jurisdiction: str = Form("South Africa"),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process a legal document"""
    try:
        # Save file to MinIO
        storage_path = await document_processor.save_document(file, current_user["id"])

        # Create document record
        document = DocumentCreate(
            title=title,
            document_type=document_type,
            jurisdiction=jurisdiction,
            matter_id=matter_id,
            storage_path=storage_path,
            file_type=file.content_type,
            created_by=current_user["id"]
        )

        document_id = await document_processor.create_document(document)

        # Process document in background
        background_tasks.add_task(
            document_processor.process_document,
            document_id,
            storage_path
        )

        return {"document_id": document_id, "status": "processing"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API routes for audio recording processing
@app.post("/recordings/", response_model=dict)
async def upload_recording(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    matter_id: Optional[str] = Form(None),
    duration_seconds: int = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process a legal audio recording"""
    try:
        # Save audio to MinIO
        storage_path = await audio_processor.save_recording(file, current_user["id"])

        # Create recording record
        recording = RecordingCreate(
            title=title,
            description=description,
            matter_id=matter_id,
            storage_path=storage_path,
            duration_seconds=duration_seconds,
            created_by=current_user["id"]
        )

        recording_id = await audio_processor.create_recording(recording)

        # Start transcription in background
        background_tasks.add_task(
            audio_processor.transcribe_recording,
            recording_id,
            storage_path
        )

        return {"recording_id": recording_id, "status": "transcribing"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API route for legal queries using Ollama
@app.post("/legal-query/", response_model=dict)
async def process_legal_query(
    query: LegalQuery,
    current_user: dict = Depends(get_current_user)
):
    """Process legal query with RAG and LLM"""
    try:
        # Retrieve relevant documents
        relevant_docs = await vector_store.search_documents(
            query.query,
            filter={"jurisdiction": query.jurisdiction}
        )

        # Format context from retrieved documents
        context = "\n\n".join([doc.content for doc in relevant_docs])

        # Create prompt with South African legal context
        prompt = f"""You are Verdict360, a specialized South African legal assistant.
        Answer the following question based on the provided context.

        SOUTH AFRICAN LEGAL CONTEXT:
        - South Africa has a mixed legal system (Roman-Dutch civil law and English common law)
        - The Constitution of the Republic of South Africa is the supreme law
        - Courts: Constitutional Court > Supreme Court of Appeal > High Courts > Magistrates' Courts

        CONTEXT:
        {context}

        QUESTION:
        {query.query}

        Answer the question based on the context provided. If you cannot answer from the context, say so.
        Cite specific case law or statutes if relevant.
        """

        # Query Ollama
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": "You are a helpful South African legal assistant specialized in legal research and analysis.",
                    "stream": False
                }
            )

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="LLM processing failed")

            result = response.json()

        # Record query for analytics
        await document_processor.log_query(query.query, current_user["id"])

        return {
            "response": result["response"],
            "sources": [{"id": doc.id, "title": doc.title} for doc in relevant_docs[:3]]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Startup event to initialize services
@app.on_event("startup")
async def startup_event():
    # Initialize vector store
    await vector_store.initialize()

    # Ensure Ollama is running with required models
    async with httpx.AsyncClient() as client:
        try:
            # Check if model exists
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            models = response.json().get("models", [])

            # Pull model if needed
            if not any(model["name"] == OLLAMA_MODEL for model in models):
                print(f"Pulling {OLLAMA_MODEL} model...")
                await client.post(
                    f"{OLLAMA_URL}/api/pull",
                    json={"name": OLLAMA_MODEL}
                )
        except Exception as e:
            print(f"Warning: Ollama service check failed: {e}")
            print("Please ensure Ollama is running with required models")
```

```python
# Self-hosted Whisper Transcription Service
# app/services/audio_processor.py

import os
import tempfile
import asyncio
import aiofiles
import whisper
from datetime import datetime
from app.database import get_async_session
from app.storage import get_minio_client
from app.models import RecordingCreate, Recording, Transcription
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

# Load Whisper model (base model for efficiency)
# Use "tiny", "base", "small", "medium" depending on resources
model = whisper.load_model("base")

async def save_recording(file, user_id):
    """Save recording to MinIO storage"""
    client = get_minio_client()

    # Generate storage path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    storage_path = f"recordings/{user_id}/{filename}"

    # Create temporary file
    async with aiofiles.tempfile.NamedTemporaryFile("wb", delete=False) as temp:
        content = await file.read()
        await temp.write(content)
        temp_path = temp.name

    try:
        # Upload to MinIO
        client.fput_object(
            "legal-recordings",
            storage_path,
            temp_path,
            content_type=file.content_type
        )

        return storage_path
    finally:
        os.unlink(temp_path)  # Clean up temp file

async def create_recording(recording: RecordingCreate):
    """Create recording record in database"""
    async with get_async_session() as session:
        db_recording = Recording(
            title=recording.title,
            description=recording.description,
            matter_id=recording.matter_id,
            storage_path=recording.storage_path,
            duration_seconds=recording.duration_seconds,
            created_by=recording.created_by,
            transcription_status="pending"
        )

        session.add(db_recording)
        await session.commit()
        await session.refresh(db_recording)

        return str(db_recording.id)

async def transcribe_recording(recording_id: str, storage_path: str):
    """Transcribe recording using self-hosted Whisper"""
    client = get_minio_client()

    try:
        # Update status to in_progress
        async with get_async_session() as session:
            await session.execute(
                update(Recording)
                .where(Recording.id == recording_id)
                .values(transcription_status="in_progress")
            )
            await session.commit()

        # Download recording to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
            client.fget_object("legal-recordings", storage_path, temp.name)
            temp_path = temp.name

        try:
            # Transcribe using Whisper
            result = model.transcribe(temp_path)

            # Format transcription with timestamps
            transcription_text = ""
            for segment in result["segments"]:
                start_time = format_timestamp(segment["start"])
                end_time = format_timestamp(segment["end"])
                text = segment["text"].strip()
                transcription_text += f"[{start_time} - {end_time}] {text}\n\n"

            # Save transcription file
            transcription_filename = f"{os.path.basename(storage_path)}.txt"
            transcription_path = f"transcriptions/{os.path.dirname(storage_path)}/{transcription_filename}"

            # Upload transcription to MinIO
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as trans_file:
                trans_file.write(transcription_text)
                trans_file.flush()

                client.fput_object(
                    "legal-documents",
                    transcription_path,
                    trans_file.name,
                    content_type="text/plain"
                )

            # Update database with transcription info
            async with get_async_session() as session:
                await session.execute(
                    update(Recording)
                    .where(Recording.id == recording_id)
                    .values(
                        transcription_status="completed",
                        transcription_path=transcription_path
                    )
                )
                await session.commit()

            return transcription_path

        finally:
            os.unlink(temp_path)  # Clean up temp audio file

    except Exception as e:
        # Update status to failed
        async with get_async_session() as session:
            await session.execute(
                update(Recording)
                .where(Recording.id == recording_id)
                .values(transcription_status="failed")
            )
            await session.commit()

        print(f"Transcription failed: {str(e)}")
        raise

def format_timestamp(seconds):
    """Format seconds to HH:MM:SS"""
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
```

```python
# Vector Store with ChromaDB
# app/services/vector_store.py

import os
import tempfile
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from app.database import get_async_session
from app.storage import get_minio_client
from app.models import DocumentChunk, Document
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
collection = None

async def initialize():
    """Initialize the vector store"""
    global collection

    # Create or get collection
    collection = client.get_or_create_collection(
        name="legal_documents",
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"}
    )

    print(f"Vector store initialized with {collection.count()} documents")

async def add_document_chunks(
    document_id: str,
    chunks: List[Dict[str, Any]]
):
    """Add document chunks to vector store"""
    # Prepare data for ChromaDB
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    texts = [chunk["content"] for chunk in chunks]
    metadatas = [
        {
            "document_id": document_id,
            "chunk_index": i,
            "document_type": chunks[i].get("document_type", "unknown"),
            "jurisdiction": chunks[i].get("jurisdiction", "South Africa"),
            "legal_citations": str(chunks[i].get("citations", [])),
        }
        for i in range(len(chunks))
    ]

    # Add to ChromaDB
    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )

    # Also store in PostgreSQL for backup and complex queries
    async with get_async_session() as session:
        # Generate embeddings
        embeddings = embedding_model.encode(texts)

        # Create database records
        for i, chunk in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=i,
                content=chunk["content"],
                embedding=embeddings[i].tolist(),
                metadata={
                    "citations": chunk.get("citations", []),
                    "document_type": chunk.get("document_type", "unknown"),
                    "jurisdiction": chunk.get("jurisdiction", "South Africa"),
                }
            )
            session.add(db_chunk)

        await session.commit()

    return ids

async def search_documents(
    query: str,
    limit: int = 5,
    filter: Optional[Dict[str, Any]] = None
):
    """Search for documents similar to query"""
    # Search in ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=limit,
        where=filter or {}
    )

    # Get document details from database
    doc_ids = set()
    for metadata in results["metadatas"][0]:
        doc_ids.add(metadata["document_id"])

    # Fetch documents from database
    async with get_async_session() as session:
        documents = []
        for doc_id in doc_ids:
            result = await session.execute(
                select(Document).where(Document.id == doc_id)
            )
            document = result.scalars().first()
            if document:
                documents.append(document)

    return documents

async def delete_document(document_id: str):
    """Delete document chunks from vector store"""
    # Delete from ChromaDB
    collection.delete(
        where={"document_id": document_id}
    )

    # Delete from PostgreSQL
    async with get_async_session() as session:
        await session.execute(
            DocumentChunk.__table__.delete().where(DocumentChunk.document_id == document_id)
        )
        await session.commit()
```

```typescript
// Legal Document Upload Component (React)
// components/documents/DocumentUploader.tsx

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { UploadCloud, File, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import axios from 'axios';

interface FileWithPreview extends File {
  preview: string;
}

const documentTypes = [
  { value: 'judgment', label: 'Court Judgment' },
  { value: 'statute', label: 'Statute or Act' },
  { value: 'contract', label: 'Legal Contract' },
  { value: 'pleading', label: 'Pleading Document' },
  { value: 'opinion', label: 'Legal Opinion' },
  { value: 'article', label: 'Legal Article' },
  { value: 'other', label: 'Other Legal Document' },
];

export default function DocumentUploader({ matterId }: { matterId?: string }) {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [documentType, setDocumentType] = useState('');
  const [title, setTitle] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const { token } = useAuth();

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      setError(null);
      setSuccess(false);

      // Validate file types
      const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
      ];
      const invalidFiles = acceptedFiles.filter(file => !validTypes.includes(file.type));

      if (invalidFiles.length > 0) {
        setError('Only PDF, DOCX, and TXT files are accepted');
        return;
      }

      // Create previews
      const filesWithPreview = acceptedFiles.map(file =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
        })
      );

      setFiles(filesWithPreview);

      // Generate title from filename if empty
      if (!title && filesWithPreview.length === 1) {
        const fileName = filesWithPreview[0].name.split('.')[0];
        setTitle(fileName);
      }
    },
    [title]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!files.length || !documentType || !title) {
      setError('Please select a file, document type, and title');
      return;
    }

    setError(null);
    setSuccess(false);
    setUploading(true);
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', files[0]);
      formData.append('title', title);
      formData.append('document_type', documentType);

      if (matterId) {
        formData.append('matter_id', matterId);
      }

      formData.append('jurisdiction', 'South Africa');

      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/documents/`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: progressEvent => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 100));
          setProgress(percentCompleted);
        },
      });

      setSuccess(true);
      console.log('Upload successful:', response.data);

      // Reset form after success
      setTimeout(() => {
        setFiles([]);
        setTitle('');
        setDocumentType('');
        setProgress(0);
        setUploading(false);
      }, 2000);
    } catch (err: any) {
      console.error('Upload failed:', err);
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      setUploading(false);
    }
  };

  return (
    <Card className='w-full max-w-md mx-auto'>
      <CardHeader>
        <CardTitle className='text-primary'>Upload Legal Document</CardTitle>
      </CardHeader>

      <CardContent className='space-y-4'>
        {error && (
          <div className='bg-destructive/10 p-3 rounded-md flex items-center text-sm'>
            <AlertCircle className='h-4 w-4 mr-2 text-destructive' />
            <span className='text-destructive'>{error}</span>
          </div>
        )}

        {success && (
          <div className='bg-green-100 p-3 rounded-md flex items-center text-sm'>
            <CheckCircle className='h-4 w-4 mr-2 text-green-600' />
            <span className='text-green-600'>Document uploaded successfully!</span>
          </div>
        )}

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-md p-6 cursor-pointer transition-colors ${
            isDragActive ? 'border-primary bg-primary/5' : 'border-input'
          }`}>
          <input {...getInputProps()} />

          {files.length > 0 ? (
            <div className='flex flex-col items-center'>
              <File className='h-10 w-10 text-primary mb-2' />
              <p className='text-sm font-medium'>{files[0].name}</p>
              <p className='text-xs text-muted-foreground'>{(files[0].size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          ) : (
            <div className='flex flex-col items-center'>
              <UploadCloud className='h-10 w-10 text-muted-foreground mb-2' />
              <p className='text-sm font-medium'>Drag and drop file here, or click to select</p>
              <p className='text-xs text-muted-foreground mt-1'>Supports PDF, DOCX, and TXT (Max 10MB)</p>
            </div>
          )}
        </div>

        <div className='space-y-2'>
          <Label htmlFor='title'>Document Title</Label>
          <Input
            id='title'
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder='Enter document title'
            disabled={uploading}
          />
        </div>

        <div className='space-y-2'>
          <Label htmlFor='documentType'>Document Type</Label>
          <Select value={documentType} onValueChange={setDocumentType} disabled={uploading}>
            <SelectTrigger id='documentType'>
              <SelectValue placeholder='Select document type' />
            </SelectTrigger>
            <SelectContent>
              {documentTypes.map(type => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {uploading && (
          <div className='space-y-2'>
            <Progress value={progress} />
            <p className='text-xs text-center text-muted-foreground'>Processing document: {progress}%</p>
          </div>
        )}
      </CardContent>

      <CardFooter>
        <Button
          className='w-full'
          onClick={handleUpload}
          disabled={uploading || !files.length || !documentType || !title}>
          {uploading ? 'Uploading...' : 'Upload Document'}
        </Button>
      </CardFooter>
    </Card>
  );
}
```
