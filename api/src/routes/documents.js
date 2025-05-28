const express = require('express');
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');
const minioService = require('../services/minioService');
const documentProcessor = require('../services/documentProcessor');

const router = express.Router();

// Configure multer for document uploads
const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 20 * 1024 * 1024, // 20MB limit for documents
  },
  fileFilter: (req, file, cb) => {
    // Accept only legal document formats
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/plain'
    ];
    
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Only PDF, DOCX, DOC, and TXT files are allowed for legal documents'), false);
    }
  }
});

// Upload legal document endpoint
router.post('/upload', upload.single('document'), async (req, res) => {
  try {
    const file = req.file;
    const { title, documentType, jurisdiction = 'South Africa', matterId, description } = req.body;

    // Validate required fields
    if (!file) {
      return res.status(400).json({ error: 'No document file provided' });
    }
    
    if (!title || !documentType) {
      return res.status(400).json({ error: 'Title and document type are required' });
    }

    // Generate unique document ID
    const documentId = uuidv4();
    const userId = req.user?.id || 'demo_user'; // Will be properly extracted from JWT in later step

    console.log('Processing legal document upload:', {
      documentId,
      filename: file.originalname,
      size: file.size,
      type: documentType,
      jurisdiction
    });

    // Upload to MinIO storage
    const storageResult = await minioService.uploadDocument(
      userId,
      documentId,
      file.buffer,
      file.originalname,
      {
        mimetype: file.mimetype,
        documentType,
        jurisdiction,
        matterId,
        title,
        description
      }
    );

    // Start document processing in background
    documentProcessor.processDocument(documentId, {
      title,
      documentType,
      jurisdiction,
      storagePath: storageResult.storagePath,
      fileType: file.mimetype,
      originalName: file.originalname,
      userId,
      matterId,
      description
    }).catch(error => {
      console.error('Background document processing failed:', error);
    });

    res.json({
      success: true,
      documentId,
      message: 'Legal document uploaded successfully',
      fileInfo: {
        originalName: file.originalname,
        size: file.size,
        type: file.mimetype,
        documentType,
        jurisdiction
      },
      storage: {
        path: storageResult.storagePath,
        bucket: storageResult.bucket
      },
      status: 'processing'
    });

  } catch (error) {
    console.error('Document upload error:', error);
    
    if (error.message.includes('Only PDF, DOCX')) {
      return res.status(400).json({ error: error.message });
    }
    
    res.status(500).json({ 
      error: 'Failed to process document upload',
      details: error.message 
    });
  }
});

// Get document processing status
router.get('/:documentId/status', async (req, res) => {
  try {
    const { documentId } = req.params;
    
    // For now, return mock status - will be replaced with database query
    const status = {
      documentId,
      status: 'processing',
      progress: 75,
      steps: {
        upload: { completed: true, timestamp: new Date().toISOString() },
        textExtraction: { completed: true, timestamp: new Date().toISOString() },
        citationDetection: { completed: false, progress: 75 },
        vectorisation: { completed: false, progress: 0 }
      }
    };
    
    res.json(status);
  } catch (error) {
    console.error('Status check error:', error);
    res.status(500).json({ error: 'Failed to check document status' });
  }
});

module.exports = router;
