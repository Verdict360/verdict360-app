export interface LegalDocument {
  id: string;
  title: string;
  documentType: 'judgment' | 'statute' | 'contract' | 'pleading' | 'opinion' | 'article' | 'other';
  jurisdiction: string;
  fileType: string;
  storagePath: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  confidentialityLevel: 'standard' | 'confidential' | 'privileged';
  matterId?: string;
}

export interface DocumentChunk {
  id: string;
  documentId: string;
  chunkIndex: number;
  content: string;
  metadata: {
    citations?: string[];
    documentType?: string;
    jurisdiction?: string;
  };
}

export interface Citation {
  id: string;
  citation: string;
  title?: string;
  court?: string;
  year?: number;
  jurisdiction: string;
}
