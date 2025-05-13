// mobile/src/services/SecureStorageService.ts
import CryptoJS from 'crypto-js';
import { Platform } from 'react-native';
import RNFS from 'react-native-fs';
import { MMKV } from 'react-native-mmkv';
import { ENV } from '../utils/environment';

// Storage for metadata about recordings
const storage = new MMKV();

// Encryption key - in production would come from secure storage
const ENCRYPTION_KEY = ENV.ENCRYPTION_KEY || 'verdict360-secure-storage-key';

export interface RecordingMetadata {
  id: string;
  title: string;
  filePath: string;
  encryptionIV: string;
  duration: number;
  size: number;
  createdAt: number;
  matterId?: string;
  description?: string;
  transcriptionStatus?: 'pending' | 'in_progress' | 'completed' | 'failed';
  uploadStatus?: 'pending' | 'uploading' | 'uploaded' | 'failed';
  remotePath?: string;
}

class SecureStorageService {
  private readonly baseDir: string;

  constructor() {
    // Use app-specific directory based on platform
    this.baseDir =
      Platform.OS === 'ios' ? `${RNFS.DocumentDirectoryPath}/recordings` : `${RNFS.ExternalDirectoryPath}/recordings`;

    // Create directory if it doesn't exist
    this.ensureDirectoryExists();
  }

  private async ensureDirectoryExists(): Promise<void> {
    try {
      const exists = await RNFS.exists(this.baseDir);
      if (!exists) {
        await RNFS.mkdir(this.baseDir);
      }
    } catch (error) {
      console.error('Failed to create recordings directory:', error);
    }
  }

  // Generate secure temporary path for recording
  public getTempRecordingPath(): string {
    const timestamp = Date.now();
    const filename = `recording_${timestamp}.aac`;
    return Platform.OS === 'ios' ? `${RNFS.DocumentDirectoryPath}/${filename}` : `${RNFS.CacheDirPath}/${filename}`;
  }

  // Save and encrypt a recording file
  public async saveRecording(
    tempFilePath: string,
    title: string,
    duration: number,
    matterId?: string,
    description?: string
  ): Promise<RecordingMetadata> {
    await this.ensureDirectoryExists();

    const id = `recording_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;
    const targetFilename = `${id}.enc`;
    const targetPath = `${this.baseDir}/${targetFilename}`;

    // Read the file as base64
    const fileContent = await RNFS.readFile(tempFilePath, 'base64');

    // Generate random IV for encryption
    const iv = CryptoJS.lib.WordArray.random(16).toString();

    // Encrypt the file content
    const encrypted = CryptoJS.AES.encrypt(fileContent, ENCRYPTION_KEY, { iv: CryptoJS.enc.Hex.parse(iv) }).toString();

    // Write encrypted content to the target path
    await RNFS.writeFile(targetPath, encrypted, 'utf8');

    // Get file stats
    const fileStats = await RNFS.stat(targetPath);

    // Create metadata
    const metadata: RecordingMetadata = {
      id,
      title,
      filePath: targetPath,
      encryptionIV: iv,
      duration,
      size: fileStats.size,
      createdAt: Date.now(),
      matterId,
      description,
      transcriptionStatus: 'pending',
      uploadStatus: 'pending',
    };

    // Store metadata
    this.saveMetadata(metadata);

    // Delete the temporary file
    await RNFS.unlink(tempFilePath);

    return metadata;
  }

  // Decrypt and get recording for playback
  public async getDecryptedRecording(id: string): Promise<string> {
    const metadata = this.getMetadata(id);
    if (!metadata) {
      throw new Error('Recording not found');
    }

    // Read encrypted content
    const encryptedContent = await RNFS.readFile(metadata.filePath, 'utf8');

    // Decrypt the content
    const decrypted = CryptoJS.AES.decrypt(encryptedContent, ENCRYPTION_KEY, {
      iv: CryptoJS.enc.Hex.parse(metadata.encryptionIV),
    }).toString(CryptoJS.enc.Base64);

    // Write decrypted content to a temporary file
    const tempPath = `${RNFS.CacheDirPath}/temp_${id}.aac`;
    await RNFS.writeFile(tempPath, decrypted, 'base64');

    return tempPath;
  }

  // Save recording metadata
  private saveMetadata(metadata: RecordingMetadata): void {
    storage.set(`recording_${metadata.id}`, JSON.stringify(metadata));

    // Update the recording list
    const recordingIds = this.getRecordingIds();
    if (!recordingIds.includes(metadata.id)) {
      recordingIds.push(metadata.id);
      storage.set('recording_ids', JSON.stringify(recordingIds));
    }
  }

  // Get recording metadata by ID
  public getMetadata(id: string): RecordingMetadata | null {
    const data = storage.getString(`recording_${id}`);
    return data ? JSON.parse(data) : null;
  }

  // Get all recording IDs
  public getRecordingIds(): string[] {
    const data = storage.getString('recording_ids');
    return data ? JSON.parse(data) : [];
  }

  // Get all recordings metadata
  public getAllRecordings(): RecordingMetadata[] {
    const ids = this.getRecordingIds();
    return ids.map(id => this.getMetadata(id)).filter(metadata => metadata !== null) as RecordingMetadata[];
  }

  // Delete a recording
  public async deleteRecording(id: string): Promise<void> {
    const metadata = this.getMetadata(id);
    if (metadata) {
      // Delete the file
      await RNFS.unlink(metadata.filePath);

      // Remove metadata
      storage.delete(`recording_${id}`);

      // Update recording list
      const recordingIds = this.getRecordingIds().filter(rid => rid !== id);
      storage.set('recording_ids', JSON.stringify(recordingIds));
    }
  }

  // Prepare a recording for upload
  public async prepareForUpload(id: string): Promise<{
    fileContent: string;
    metadata: RecordingMetadata;
  }> {
    const metadata = this.getMetadata(id);
    if (!metadata) {
      throw new Error('Recording not found');
    }

    // Get the decrypted temporary file
    const decryptedPath = await this.getDecryptedRecording(id);

    // Read as base64 for upload
    const fileContent = await RNFS.readFile(decryptedPath, 'base64');

    // Clean up temporary file
    await RNFS.unlink(decryptedPath);

    return { fileContent, metadata };
  }

  /**
   * Update recording metadata
   */
  public updateMetadata(metadata: RecordingMetadata): void {
    storage.set(`recording_${metadata.id}`, JSON.stringify(metadata));
  }
}

export const secureStorage = new SecureStorageService();
