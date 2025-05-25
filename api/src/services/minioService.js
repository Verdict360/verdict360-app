const { Client } = require('minio');
const config = require('../config/config');

// Create MinIO client
const minioClient = new Client({
  endPoint: config.minio.endpoint,
  port: config.minio.port,
  useSSL: config.minio.useSSL,
  accessKey: config.minio.accessKey,
  secretKey: config.minio.secretKey,
});

// Upload recording to MinIO
const uploadRecording = async (userId, recordingId, fileBuffer, originalName, metadata = {}) => {
  try {
    const bucketName = config.minio.buckets.recordings;
    
    // Create object path: userId/recordings/recordingId/filename
    const objectPath = `${userId}/recordings/${recordingId}/${originalName}`;
    
    // Add metadata for legal compliance
    const objectMetadata = {
      'Content-Type': metadata.mimetype || 'audio/m4a',
      'X-Legal-Matter': metadata.matterId || 'unassigned',
      'X-Recording-Type': metadata.recordingType || 'legal_proceeding',
      'X-Created-By': userId,
      'X-Original-Name': originalName,
      'X-Upload-Time': new Date().toISOString(),
      'X-Device-Type': 'mobile',
      ...metadata
    };

    // Upload to MinIO
    const result = await minioClient.putObject(
      bucketName,
      objectPath,
      fileBuffer,
      fileBuffer.length,
      objectMetadata
    );

    console.log('Recording uploaded to MinIO:', {
      bucket: bucketName,
      path: objectPath,
      size: fileBuffer.length,
      etag: result.etag
    });

    return {
      success: true,
      storagePath: objectPath,
      bucket: bucketName,
      etag: result.etag,
      size: fileBuffer.length
    };

  } catch (error) {
    console.error('MinIO upload error:', error);
    throw new Error(`Failed to upload recording to storage: ${error.message}`);
  }
};

// Upload document to MinIO
const uploadDocument = async (userId, documentId, fileBuffer, originalName, metadata = {}) => {
  try {
    const bucketName = config.minio.buckets.documents;
    
    // Create object path: userId/documents/documentId/filename
    const objectPath = `${userId}/documents/${documentId}/${originalName}`;
    
    // Add metadata for legal compliance
    const objectMetadata = {
      'Content-Type': metadata.mimetype || 'application/pdf',
      'X-Legal-Matter': metadata.matterId || 'unassigned',
      'X-Document-Type': metadata.documentType || 'legal_document',
      'X-Created-By': userId,
      'X-Original-Name': originalName,
      'X-Upload-Time': new Date().toISOString(),
      'X-Device-Type': 'mobile',
      'X-Jurisdiction': metadata.jurisdiction || 'South Africa',
      ...metadata
    };

    // Upload to MinIO
    const result = await minioClient.putObject(
      bucketName,
      objectPath,
      fileBuffer,
      fileBuffer.length,
      objectMetadata
    );

    console.log('Document uploaded to MinIO:', {
      bucket: bucketName,
      path: objectPath,
      size: fileBuffer.length,
      etag: result.etag
    });

    return {
      success: true,
      storagePath: objectPath,
      bucket: bucketName,
      etag: result.etag,
      size: fileBuffer.length
    };

  } catch (error) {
    console.error('MinIO document upload error:', error);
    throw new Error(`Failed to upload document to storage: ${error.message}`);
  }
};

// Generate presigned URL for download
const getDownloadUrl = async (bucketName, objectPath, expirySeconds = 3600) => {
  try {
    const url = await minioClient.presignedGetObject(bucketName, objectPath, expirySeconds);
    return url;
  } catch (error) {
    console.error('Error generating download URL:', error);
    throw new Error(`Failed to generate download URL: ${error.message}`);
  }
};

// Check if bucket exists and create if needed
const ensureBucketExists = async (bucketName) => {
  try {
    const exists = await minioClient.bucketExists(bucketName);
    if (!exists) {
      await minioClient.makeBucket(bucketName);
      console.log(`Created bucket: ${bucketName}`);
    }
    return true;
  } catch (error) {
    console.error(`Error with bucket ${bucketName}:`, error);
    throw error;
  }
};

// Initialize buckets on startup
const initializeBuckets = async () => {
  try {
    await ensureBucketExists(config.minio.buckets.documents);
    await ensureBucketExists(config.minio.buckets.recordings);
    await ensureBucketExists(config.minio.buckets.transcriptions);
    console.log('✅ All MinIO buckets initialized');
  } catch (error) {
    console.error('❌ Failed to initialize MinIO buckets:', error);
    throw error;
  }
};

module.exports = {
  uploadRecording,
  uploadDocument,
  getDownloadUrl,
  ensureBucketExists,
  initializeBuckets,
  minioClient
};
