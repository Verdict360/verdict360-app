const express = require('express');
const cors = require('cors');
const config = require('./config/config');
const minioService = require('./services/minioService');

const app = express();

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://10.0.2.2:3000'],
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Import routes
const documentsRouter = require('./routes/documents');

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    service: 'Verdict360 API',
    version: '1.0.0'
  });
});

// Routes
app.use('/api/documents', documentsRouter);

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('API Error:', error);
  
  res.status(500).json({ 
    error: 'Internal server error',
    message: error.message 
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Initialize services and start server
const startServer = async () => {
  try {
    // Initialize MinIO buckets
    await minioService.initializeBuckets();
    
    // Start server
    const PORT = config.port;
    app.listen(PORT, () => {
      console.log(`🚀 Verdict360 API server running on port ${PORT}`);
      console.log(`📄 Document processing: http://localhost:${PORT}/api/documents/`);
      console.log(`🏥 Health check: http://localhost:${PORT}/health`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
};

startServer();

module.exports = app;
