// Browser-safe MinIO operations (using API endpoints instead of direct client)

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

// Generate a presigned URL for uploading a file (via API)
export const getPresignedUploadUrl = async (
  bucket: Bucket,
  objectName: string,
  expirySeconds: number = DEFAULT_EXPIRY
): Promise<string> => {
  try {
    const response = await fetch('/api/storage/presigned-upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        bucket,
        objectName,
        expirySeconds,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to get presigned URL');
    }
    
    const data = await response.json();
    return data.url;
  } catch (error) {
    console.error('Error generating presigned upload URL', error);
    throw error;
  }
};

// Generate a presigned URL for downloading a file (via API)
export const getPresignedDownloadUrl = async (
  bucket: Bucket,
  objectName: string,
  expirySeconds: number = DEFAULT_EXPIRY
): Promise<string> => {
  try {
    const response = await fetch('/api/storage/presigned-download', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        bucket,
        objectName,
        expirySeconds,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to get presigned URL');
    }
    
    const data = await response.json();
    return data.url;
  } catch (error) {
    console.error('Error generating presigned download URL', error);
    throw error;
  }
};
