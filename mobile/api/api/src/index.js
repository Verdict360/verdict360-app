const express = require('express');
const cors = require('cors');
const multer = require('multer');
const config = require('./config/config');
const { uploadRecording, uploadDocument, initializeBuckets } = require('./services/minioService');

const app = express();

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://10.0.2.2:3000'], // Allow both web and mobile
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Configure multer for file uploads (in memory for MinIO)
const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit for audio files
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    service: 'Verdict360 API',
    version: '1.0.0'
  });
});

// Mobile recording upload endpoint with MinIO integration
app.post('/api/recordings/upload', upload.single('recording'), async (req, res) => {
  try {
    const file = req.file;
    const metadata = req.body;

    if (!file) {
      return res.status(400).json({ error: 'No recording file provided' });
    }

    // Extract user ID from metadata or auth token
    const userId = metadata.userId || 'user_001'; // In Week 2, extract from JWT token
    const recordingId = `rec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    console.log('Processing recording upload:', {
      filename: file.originalname,
      size: file.size,
      mimetype: file.mimetype,
      userId: userId,
      recordingId: recordingId
    });

    // Upload to MinIO
    const uploadResult = await uploadRecording(
      userId,
      recordingId,
      file.buffer,
      file.originalname,
      {
        mimetype: file.mimetype,
        recordingType: metadata.recordingType || 'legal_proceeding',
        matterId: metadata.matterId,
        duration: metadata.duration,
        recordingDate: metadata.recordingDate,
        deviceInfo: metadata.deviceInfo
      }
    );

    res.json({
      success: true,
      recordingId: recordingId,
      message: 'Recording uploaded successfully to secure storage',
      fileInfo: {
        originalName: file.originalname,
        size: file.size,
        type: file.mimetype,
      },
      storage: {
        bucket: uploadResult.bucket,
        path: uploadResult.storagePath,
        etag: uploadResult.etag
      },
      metadata: metadata,
      status: 'stored',
      transcriptionStatus: 'pending'
    });

  } catch (error) {
    console.error('Recording upload error:', error);
    res.status(500).json({ 
      error: 'Failed to process recording upload',
      details: error.message 
    });
  }
});

// Mobile document upload endpoint with MinIO integration
app.post('/api/documents/upload', upload.single('document'), async (req, res) => {
  try {
    const file = req.file;
    const metadata = req.body;

    if (!file) {
      return res.status(400).json({ error: 'No document file provided' });
    }

    const userId = metadata.userId || 'user_001';
    const documentId = `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    console.log('Processing document upload:', {
      filename: file.originalname,
      size: file.size,
      mimetype: file.mimetype,
      userId: userId,
      documentId: documentId
    });

    // Upload to MinIO
    const uploadResult = await uploadDocument(
      userId,
      documentId,
      file.buffer,
      file.originalname,
      {
        mimetype: file.mimetype,
        documentType: metadata.documentType || 'legal_document',
        matterId: metadata.matterId,
        jurisdiction: metadata.jurisdiction || 'South Africa',
        title: metadata.title,
        description: metadata.description
      }
    );

    res.json({
      success: true,
      documentId: documentId,
      message: 'Document uploaded successfully to secure storage',
      fileInfo: {
        originalName: file.originalname,
        size: file.size,
        type: file.mimetype,
      },
      storage: {
        bucket: uploadResult.bucket,
        path: uploadResult.storagePath,
        etag: uploadResult.etag
      },
      metadata: metadata,
      status: 'stored',
      processingStatus: 'pending'
    });

  } catch (error) {
    console.error('Document upload error:', error);
    res.status(500).json({ 
      error: 'Failed to process document upload',
      details: error.message 
    });
  }
});

// Mobile sync endpoint - get user's recordings
app.get('/api/recordings/sync/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    // For now, return mock data that shows MinIO integration
    const recordings = [
      {
        id: 'rec_001',
        title: 'Client Meeting - Smith vs Jones',
        duration: 1847,
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        status: 'stored',
        transcriptionStatus: 'completed',
        transcriptionAvailable: true,
        storagePath: `${userId}/recordings/rec_001/meeting_audio.m4a`,
        fileSize: 2048000
      },
      {
        id: 'rec_002', 
        title: 'Court Hearing Prep',
        duration: 2156,
        createdAt: new Date(Date.now() - 172800000).toISOString(),
        status: 'stored',
        transcriptionStatus: 'processing',
        transcriptionAvailable: false,
        storagePath: `${userId}/recordings/rec_002/court_prep.m4a`,
        fileSize: 3072000
      }
    ];

    res.json({
      success: true,
      recordings: recordings,
      totalCount: recordings.length,
      lastSyncTime: new Date().toISOString(),
      storageInfo: {
        totalStorageUsed: recordings.reduce((total, rec) => total + rec.fileSize, 0),
        availableStorage: '50GB' // Mock data
      }
    });

  } catch (error) {
    console.error('Sync error:', error);
    res.status(500).json({ 
      error: 'Failed to sync recordings',
      details: error.message 
    });
  }
});

// Authentication validation endpoint
app.post('/api/auth/validate', (req, res) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    // For now, accept any token
    // In Week 2, we'll integrate proper Keycloak validation
    res.json({
      valid: true,
      user: {
        id: 'user_001',
        email: 'user@verdict360.org',
        name: 'Legal Professional',
        role: 'attorney',
        firm: 'Example Legal Firm'
      }
    });

  } catch (error) {
    console.error('Auth validation error:', error);
    res.status(500).json({ 
      error: 'Authentication validation failed',
      details: error.message 
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('API Error:', error);
  
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'File too large. Maximum size is 50MB.' });
    }
  }
  
  res.status(500).json({ 
    error: 'Internal server error',
    message: error.message 
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Initialize MinIO and start server
const startServer = async () => {
  try {
    // Initialize MinIO buckets
    await initializeBuckets();
    
    // Start server
    const PORT = config.port;
    app.listen(PORT, () => {
      console.log(`🚀 Verdict360 API server running on port ${PORT}`);
      console.log(`�� Mobile endpoints available at http://localhost:${PORT}/api/`);
      console.log(`🏥 Health check: http://localhost:${PORT}/health`);
      console.log(`📁 MinIO integration: ACTIVE`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
};

startServer();

module.exports = app;
