const express = require('express');
const cors = require('cors');
const multer = require('multer');
const config = require('./config/config');

const app = express();

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://10.0.2.2:3000'], // Allow both web and mobile
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Configure multer for file uploads (in memory for now)
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

// Mobile recording upload endpoint
app.post('/api/recordings/upload', upload.single('recording'), async (req, res) => {
  try {
    const file = req.file;
    const metadata = req.body;

    if (!file) {
      return res.status(400).json({ error: 'No recording file provided' });
    }

    console.log('Received recording upload:', {
      filename: file.originalname,
      size: file.size,
      mimetype: file.mimetype,
      metadata: metadata
    });

    // For now, just acknowledge receipt
    // In Week 2, we'll integrate with MinIO and transcription
    const recordingId = `rec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    res.json({
      success: true,
      recordingId: recordingId,
      message: 'Recording uploaded successfully',
      fileInfo: {
        originalName: file.originalname,
        size: file.size,
        type: file.mimetype,
      },
      metadata: metadata,
      status: 'processing'
    });

  } catch (error) {
    console.error('Recording upload error:', error);
    res.status(500).json({ 
      error: 'Failed to process recording upload',
      details: error.message 
    });
  }
});

// Mobile sync endpoint - get user's recordings
app.get('/api/recordings/sync/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    // For now, return mock data
    // In Week 2, we'll query the actual database
    const recordings = [
      {
        id: 'rec_001',
        title: 'Client Meeting - Smith vs Jones',
        duration: 1847, // seconds
        createdAt: new Date(Date.now() - 86400000).toISOString(), // Yesterday
        status: 'transcribed',
        transcriptionAvailable: true
      },
      {
        id: 'rec_002', 
        title: 'Court Hearing Prep',
        duration: 2156,
        createdAt: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
        status: 'processing',
        transcriptionAvailable: false
      }
    ];

    res.json({
      success: true,
      recordings: recordings,
      totalCount: recordings.length,
      lastSyncTime: new Date().toISOString()
    });

  } catch (error) {
    console.error('Sync error:', error);
    res.status(500).json({ 
      error: 'Failed to sync recordings',
      details: error.message 
    });
  }
});

// Document upload endpoint for mobile
app.post('/api/documents/upload', upload.single('document'), async (req, res) => {
  try {
    const file = req.file;
    const metadata = req.body;

    if (!file) {
      return res.status(400).json({ error: 'No document file provided' });
    }

    console.log('Received document upload:', {
      filename: file.originalname,
      size: file.size,
      mimetype: file.mimetype,
      metadata: metadata
    });

    const documentId = `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    res.json({
      success: true,
      documentId: documentId,
      message: 'Document uploaded successfully',
      fileInfo: {
        originalName: file.originalname,
        size: file.size,
        type: file.mimetype,
      },
      metadata: metadata,
      status: 'processing'
    });

  } catch (error) {
    console.error('Document upload error:', error);
    res.status(500).json({ 
      error: 'Failed to process document upload',
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
        role: 'attorney'
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

// Start server
const PORT = config.port;
app.listen(PORT, () => {
  console.log(`🚀 Verdict360 API server running on port ${PORT}`);
  console.log(`📱 Mobile endpoints available at http://localhost:${PORT}/api/`);
  console.log(`🏥 Health check: http://localhost:${PORT}/health`);
});

module.exports = app;
