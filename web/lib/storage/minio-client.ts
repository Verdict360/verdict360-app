import { Client } from 'minio';
import { env } from '@/lib/env';

// Default expiry time for presigned URLs (15 minutes)
const DEFAULT_EXPIRY = 15 * 60;

// Bucket names
export enum Bucket {
  DOCUMENTS = 'legal-documents',
  RECORDINGS = 'legal-recordings',
  TRANSCRIPTIONS = 'legal-transcriptions',
  USER_PROFILES = 'user-profiles',
  MATTER_RESOURCES = 'matter-resources',
  TEMPLATES = 'legal-templates',
}

// Create MinIO client
export const minioClient = new Client({
  endPoint: env.minio.endpoint,
  port: env.minio.port,
  useSSL: env.minio.useSSL,
  accessKey: env.minio.accessKey,
  secretKey: env.minio.secretKey,
});

// Generate a path for storing legal documents
export const generateDocumentPath = (userId: string, documentId: string, filename: string): string => {
  return `${userId}/documents/${documentId}/${filename}`;
};

// Generate a path for storing legal recordings
export const generateRecordingPath = (userId: string, recordingId: string, filename: string): string => {
  return `${userId}/recordings/${recordingId}/${filename}`;
};

// Generate a path for storing transcriptions
export const generateTranscriptionPath = (userId: string, recordingId: string, filename: string): string => {
  return `${userId}/transcriptions/${recordingId}/${filename}`;
};

// Generate a presigned URL for uploading a file
export const getPresignedUploadUrl = async (
  bucket: Bucket,
  objectName: string,
  expirySeconds: number = DEFAULT_EXPIRY
): Promise<string> => {
  try {
    return await minioClient.presignedPutObject(bucket, objectName, expirySeconds);
  } catch (error) {
    console.error('Error generating presigned upload URL', error);
    throw error;
  }
};

// Generate a presigned URL for downloading a file
export const getPresignedDownloadUrl = async (
  bucket: Bucket,
  objectName: string,
  expirySeconds: number = DEFAULT_EXPIRY
): Promise<string> => {
  try {
    return await minioClient.presignedGetObject(bucket, objectName, expirySeconds);
  } catch (error) {
    console.error('Error generating presigned download URL', error);
    throw error;
  }
};

// List objects in a bucket with a prefix
export const listObjects = async (bucket: Bucket, prefix: string = '', recursive: boolean = true) => {
  const objectList: any[] = [];
  
  return new Promise<any[]>((resolve, reject) => {
    const stream = minioClient.listObjects(bucket, prefix, recursive);
    
    stream.on('data', (obj) => {
      objectList.push(obj);
    });
    
    stream.on('error', (err) => {
      reject(err);
    });
    
    stream.on('end', () => {
      resolve(objectList);
    });
  });
};

// Upload a file (for server components)
export const uploadFile = async (
  bucket: Bucket,
  objectName: string,
  filePath: string,
  metadata: Record<string, string> = {}
): Promise<void> => {
  try {
    await minioClient.fPutObject(bucket, objectName, filePath, metadata);
  } catch (error) {
    console.error('Error uploading file', error);
    throw error;
  }
};

// Download a file (for server components)
export const downloadFile = async (
  bucket: Bucket,
  objectName: string,
  filePath: string
): Promise<void> => {
  try {
    await minioClient.fGetObject(bucket, objectName, filePath);
  } catch (error) {
    console.error('Error downloading file', error);
    throw error;
  }
};

// Delete an object
export const deleteObject = async (bucket: Bucket, objectName: string): Promise<void> => {
  try {
    await minioClient.removeObject(bucket, objectName);
  } catch (error) {
    console.error('Error deleting object', error);
    throw error;
  }
};

// Check if a bucket exists
export const bucketExists = async (bucket: Bucket): Promise<boolean> => {
  try {
    return await minioClient.bucketExists(bucket);
  } catch (error) {
    console.error('Error checking bucket existence', error);
    throw error;
  }
};

// Get object metadata
export const getObjectMetadata = async (bucket: Bucket, objectName: string): Promise<any> => {
  try {
    return await minioClient.statObject(bucket, objectName);
  } catch (error) {
    console.error('Error getting object metadata', error);
    throw error;
  }
};
