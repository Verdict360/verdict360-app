'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, File, X, Loader2, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '@/lib/auth/auth-provider';
import { getPresignedUploadUrl, Bucket, generateDocumentPath } from '@/lib/storage/minio-client';
import { cn } from '@/lib/utils';

interface FileUploaderProps {
  onUploadComplete?: (fileInfo: { name: string; size: number; path: string }) => void;
  allowedFileTypes?: string[];
  maxFiles?: number;
  maxSize?: number;
  matterId?: string;
}

export function FileUploader({
  onUploadComplete,
  allowedFileTypes = ['.pdf', '.docx', '.doc', '.txt'],
  maxFiles = 1,
  maxSize = 10 * 1024 * 1024, // 10MB
  matterId,
}: FileUploaderProps) {
  const { user } = useAuth();
  const [files, setFiles] = useState<Array<File & { preview?: string }>>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const [uploadErrors, setUploadErrors] = useState<Record<string, string>>({});
  const [uploadSuccess, setUploadSuccess] = useState<Record<string, boolean>>({});

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Limit number of files if needed
      const filesToProcess = acceptedFiles.slice(0, maxFiles);

      setFiles(
        filesToProcess.map(file =>
          Object.assign(file, {
            preview: URL.createObjectURL(file),
          })
        )
      );

      // Reset states for new files
      setUploadProgress({});
      setUploadErrors({});
      setUploadSuccess({});
    },
    [maxFiles]
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles,
    maxSize,
  });

  const uploadFiles = async () => {
    if (!files.length || !user) return;

    setUploading(true);

    for (const file of files) {
      try {
        // Create a unique ID for the document
        const documentId = `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Generate object path
        const objectPath = generateDocumentPath(user.sub, documentId, file.name);
        
        // Get presigned URL for upload
        const presignedUrl = await getPresignedUploadUrl(Bucket.DOCUMENTS, objectPath);
        
        // Upload file with progress tracking
        await uploadToPresignedUrl(presignedUrl, file, progress => {
          setUploadProgress(prev => ({ ...prev, [file.name]: progress }));
        });
        
        // Mark as successful
        setUploadSuccess(prev => ({ ...prev, [file.name]: true }));
        
        // Call callback if provided
        if (onUploadComplete) {
          onUploadComplete({
            name: file.name,
            size: file.size,
            path: objectPath,
          });
        }
      } catch (error) {
        console.error('Upload failed for file', file.name, error);
        setUploadErrors(prev => ({ ...prev, [file.name]: 'Upload failed' }));
      }
    }

    setUploading(false);
  };

  const uploadToPresignedUrl = (url: string, file: File, onProgress: (progress: number) => void): Promise<void> => {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', event => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded * 100) / event.total);
          onProgress(percentComplete);
        }
      });
      
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve();
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      });
      
      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'));
      });
      
      xhr.open('PUT', url);
      xhr.send(file);
    });
  };

  const removeFile = (name: string) => {
    setFiles(prev => prev.filter(file => file.name !== name));
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[name];
      return newProgress;
    });
    setUploadErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[name];
      return newErrors;
    });
    setUploadSuccess(prev => {
      const newSuccess = { ...prev };
      delete newSuccess[name];
      return newSuccess;
    });
  };

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-md p-6 cursor-pointer transition-colors',
          isDragActive ? 'border-primary bg-primary/5' : 'border-input',
          uploading && 'pointer-events-none opacity-60'
        )}>
        <input {...getInputProps()} disabled={uploading} />

        <div className="flex flex-col items-center text-center">
          <UploadCloud className="h-10 w-10 text-muted-foreground mb-2" />
          <p className="text-sm font-medium">Drag and drop legal document here, or click to browse</p>
          <p className="text-xs text-muted-foreground mt-1">
            Supported formats: {allowedFileTypes.join(', ')} (Max {maxSize / (1024 * 1024)}MB)
          </p>
        </div>
      </div>

      {fileRejections.length > 0 && (
        <div className="bg-destructive/10 p-3 rounded-md">
          <p className="text-sm font-medium text-destructive">The following files were rejected:</p>
          <ul className="text-xs text-destructive mt-1 list-disc list-inside">
            {fileRejections.map(({ file, errors }) => (
              <li key={file.name}>
                {file.name} - {errors.map(e => e.message).join(', ')}
              </li>
            ))}
          </ul>
        </div>
      )}

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map(file => (
            <div key={file.name} className="border rounded-md p-3">
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <File className="h-5 w-5 text-muted-foreground mr-2" />
                  <div>
                    <p className="text-sm font-medium truncate max-w-[200px]">{file.name}</p>
                    <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <div className="flex items-center">
                  {uploadSuccess[file.name] ? (
                    <Check className="h-5 w-5 text-green-500" />
                  ) : uploadErrors[file.name] ? (
                    <span className="text-xs text-destructive">{uploadErrors[file.name]}</span>
                  ) : uploading && uploadProgress[file.name] !== undefined ? (
                    <Loader2 className="h-5 w-5 text-primary animate-spin" />
                  ) : (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={e => {
                        e.stopPropagation();
                        removeFile(file.name);
                      }}>
                      <X className="h-4 w-4" />
                      <span className="sr-only">Remove</span>
                    </Button>
                  )}
                </div>
              </div>
              {uploading && uploadProgress[file.name] !== undefined && (
                <Progress value={uploadProgress[file.name]} className="h-1 mt-2" />
              )}
            </div>
          ))}

          <Button
            className="w-full mt-2"
            onClick={uploadFiles}
            disabled={uploading || files.length === 0 || Object.keys(uploadSuccess).length === files.length}>
            {uploading ? 'Uploading...' : 'Upload Files'}
          </Button>
        </div>
      )}
    </div>
  );
}
