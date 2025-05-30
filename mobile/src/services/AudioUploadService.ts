import * as FileSystem from 'expo-file-system';
import { Audio } from 'expo-av';

interface LegalRecording {
  id: string;
  name: string;
  uri: string;
  duration: number;
  timestamp: string;
  type: 'legal_proceeding' | 'client_meeting' | 'deposition' | 'other';
  quality: 'high' | 'medium' | 'low';
  fileFormat: string;
  recordedBy: string;
  matterReference?: string;
  attendees: string[];
  notes?: string;
  isUploaded: boolean;
  uploadStatus: 'pending' | 'uploading' | 'completed' | 'failed';
}

interface UploadProgress {
  totalBytesExpectedToSend: number;
  totalBytesSent: number;
}

export class AudioUploadService {
  private static instance: AudioUploadService;
  private baseUrl = process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8001'\;

  public static getInstance(): AudioUploadService {
    if (!AudioUploadService.instance) {
      AudioUploadService.instance = new AudioUploadService();
    }
    return AudioUploadService.instance;
  }

  async uploadRecording(
    recording: LegalRecording,
    authToken: string,
    onProgress?: (progress: number) => void
  ): Promise<{ success: boolean; error?: string }> {
    try {
      // Get file info
      const fileInfo = await FileSystem.getInfoAsync(recording.uri);
      if (!fileInfo.exists) {
        throw new Error('Recording file not found');
      }

      // Create form data for multipart upload
      const formData = new FormData();
      
      // Add the audio file
      formData.append('file', {
        uri: recording.uri,
        type: 'audio/m4a',
        name: `${recording.id}.m4a`,
      } as any);

      // Add metadata
      formData.append('title', recording.name);
      formData.append('description', recording.notes || '');
      formData.append('duration_seconds', recording.duration.toString());
      
      if (recording.matterReference) {
        formData.append('matter_id', recording.matterReference);
      }

      // Add legal-specific metadata
      formData.append('recording_type', recording.type);
      formData.append('attendees', recording.attendees.join(', '));
      formData.append('recorded_by', recording.recordedBy);
      formData.append('recording_timestamp', recording.timestamp);

      // Create upload task with progress tracking
      const uploadTask = FileSystem.createUploadTask(
        `${this.baseUrl}/recordings/upload`,
        recording.uri,
        {
          fieldName: 'file',
          httpMethod: 'POST',
          uploadType: FileSystem.FileSystemUploadType.MULTIPART,
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'multipart/form-data',
          },
          parameters: {
            title: recording.name,
            description: recording.notes || '',
            duration_seconds: recording.duration.toString(),
            matter_id: recording.matterReference || '',
            recording_type: recording.type,
            attendees: recording.attendees.join(', '),
            recorded_by: recording.recordedBy,
            recording_timestamp: recording.timestamp,
          },
        },
        (progress: UploadProgress) => {
          if (onProgress) {
            const percentComplete = Math.round(
              (progress.totalBytesSent / progress.totalBytesExpectedToSend) * 100
            );
            onProgress(percentComplete);
          }
        }
      );

      // Start upload and wait for completion
      const result = await uploadTask.uploadAsync();

      if (result && result.status === 200) {
        return { success: true };
      } else {
        throw new Error(`Upload failed with status: ${result?.status}`);
      }

    } catch (error) {
      console.error('Upload error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown upload error'
      };
    }
  }

  async uploadMultipleRecordings(
    recordings: LegalRecording[],
    authToken: string,
    onProgress?: (recordingId: string, progress: number) => void,
    onComplete?: (recordingId: string, success: boolean, error?: string) => void
  ): Promise<{ successful: string[]; failed: { id: string; error: string }[] }> {
    const successful: string[] = [];
    const failed: { id: string; error: string }[] = [];

    for (const recording of recordings) {
      try {
        const result = await this.uploadRecording(
          recording,
          authToken,
          (progress) => onProgress?.(recording.id, progress)
        );

        if (result.success) {
          successful.push(recording.id);
          onComplete?.(recording.id, true);
        } else {
          failed.push({ id: recording.id, error: result.error || 'Upload failed' });
          onComplete?.(recording.id, false, result.error);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        failed.push({ id: recording.id, error: errorMessage });
        onComplete?.(recording.id, false, errorMessage);
      }
    }

    return { successful, failed };
  }

  async checkUploadStatus(recordingId: string, authToken: string): Promise<{
    status: 'processing' | 'completed' | 'failed';
    transcription?: string;
    error?: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/recordings/${recordingId}/status`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Status check failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Status check error:', error);
      return {
        status: 'failed',
        error: error instanceof Error ? error.message : 'Status check failed'
      };
    }
  }

  async getRecordingTranscription(recordingId: string, authToken: string): Promise<{
    transcription?: string;
    error?: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/recordings/${recordingId}/transcription`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Transcription fetch failed: ${response.status}`);
      }

      const data = await response.json();
      return { transcription: data.transcription };
    } catch (error) {
      console.error('Transcription fetch error:', error);
      return {
        error: error instanceof Error ? error.message : 'Failed to fetch transcription'
      };
    }
  }
}

export default AudioUploadService;
