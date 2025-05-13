// mobile/src/services/AudioCompressionService.ts
import { FFmpegKit, FFmpegKitConfig, ReturnCode } from 'react-native-ffmpeg';
import RNFS from 'react-native-fs';
import { Platform } from 'react-native';
import { secureStorage, RecordingMetadata } from './SecureStorageService';

// Define compression quality levels
export enum CompressionQuality {
  HIGH = 'high',      // Good quality, larger file (128kbps)
  MEDIUM = 'medium',  // Medium quality, balanced (64kbps)
  LOW = 'low',        // Lower quality, smaller file (32kbps)
  VOICE = 'voice'     // Optimized for voice (mono, 24kbps)
}

// Define compression result
export interface CompressionResult {
  compressedPath: string;
  originalSize: number;
  compressedSize: number;
  compressionRatio: number;
  duration: number;
}

class AudioCompressionService {
  private readonly tempDir: string;
  
  constructor() {
    // Initialize FFmpeg with appropriate log level
    FFmpegKitConfig.enableLogCallback(log => {
      if (__DEV__) {
        console.log(`FFmpeg: ${log.getMessage()}`);
      }
    });
    
    // Set temp directory for compressed files
    this.tempDir = Platform.OS === 'ios' 
      ? `${RNFS.CachesDirectoryPath}/compressed`
      : `${RNFS.CacheDirPath}/compressed`;
    
    // Ensure directory exists
    this.ensureTempDirExists();
  }
  
  private async ensureTempDirExists(): Promise<void> {
    try {
      const exists = await RNFS.exists(this.tempDir);
      if (!exists) {
        await RNFS.mkdir(this.tempDir);
      }
    } catch (error) {
      console.error('Failed to create compression directory:', error);
    }
  }
  
  /**
   * Compress a recording with the specified quality
   * @param recordingId ID of the recording to compress
   * @param quality Compression quality level
   * @param progressCallback Optional callback for compression progress
   * @returns Promise resolving to compression result
   */
  public async compressRecording(
    recordingId: string,
    quality: CompressionQuality = CompressionQuality.MEDIUM,
    progressCallback?: (progress: number) => void
  ): Promise<CompressionResult> {
    await this.ensureTempDirExists();
    
    // Get recording metadata
    const metadata = secureStorage.getMetadata(recordingId);
    if (!metadata) {
      throw new Error('Recording not found');
    }
    
    // Get decrypted file for compression
    const decryptedPath = await secureStorage.getDecryptedRecording(recordingId);
    
    // Get original file stats
    const originalStats = await RNFS.stat(decryptedPath);
    const originalSize = originalStats.size;
    
    // Create output path
    const outputFilename = `compressed_${Date.now()}.aac`;
    const outputPath = `${this.tempDir}/${outputFilename}`;
    
    // Set compression parameters based on quality
    const bitrateOptions = this.getBitrateOptions(quality);
    
    // Create FFmpeg command
    const command = this.createCompressionCommand(decryptedPath, outputPath, bitrateOptions);
    
    try {
      // Execute FFmpeg command
      const session = await FFmpegKit.execute(command);
      const returnCode = await session.getReturnCode();
      
      if (ReturnCode.isSuccess(returnCode)) {
        // Get compressed file stats
        const compressedStats = await RNFS.stat(outputPath);
        const compressedSize = compressedStats.size;
        
        // Calculate compression ratio
        const compressionRatio = originalSize / compressedSize;
        
        // Clean up the decrypted file
        await RNFS.unlink(decryptedPath);
        
        return {
          compressedPath: outputPath,
          originalSize,
          compressedSize,
          compressionRatio,
          duration: metadata.duration
        };
      } else {
        // Clean up and throw error
        await RNFS.unlink(decryptedPath);
        if (await RNFS.exists(outputPath)) {
          await RNFS.unlink(outputPath);
        }
        throw new Error(`FFmpeg compression failed with return code ${returnCode}`);
      }
    } catch (error) {
      // Clean up on error
      await RNFS.unlink(decryptedPath);
      if (await RNFS.exists(outputPath)) {
        await RNFS.unlink(outputPath);
      }
      throw error;
    }
  }
  
  /**
   * Get bitrate options for the specified quality
   */
  private getBitrateOptions(quality: CompressionQuality): string {
    switch (quality) {
      case CompressionQuality.HIGH:
        return '-b:a 128k -ac 2'; // 128kbps, stereo
      case CompressionQuality.MEDIUM:
        return '-b:a 64k -ac 2';  // 64kbps, stereo
      case CompressionQuality.LOW:
        return '-b:a 32k -ac 2';  // 32kbps, stereo
      case CompressionQuality.VOICE:
        return '-b:a 24k -ac 1';  // 24kbps, mono (optimized for voice)
      default:
        return '-b:a 64k -ac 2';  // Default to medium
    }
  }
  
  /**
   * Create FFmpeg command for audio compression
   */
  private createCompressionCommand(
    inputPath: string,
    outputPath: string,
    bitrateOptions: string
  ): string {
    return `-i ${inputPath} -c:a aac ${bitrateOptions} -ar 44100 -movflags +faststart ${outputPath}`;
  }
  
  /**
   * Prepare a compressed recording for upload
   * This compresses the recording and returns the base64 content for upload
   */
  public async prepareForUpload(
    recordingId: string,
    quality: CompressionQuality = CompressionQuality.MEDIUM,
    progressCallback?: (progress: number) => void
  ): Promise<{
    fileContent: string, 
    metadata: RecordingMetadata,
    compressionStats: CompressionResult
  }> {
    const metadata = secureStorage.getMetadata(recordingId);
    if (!metadata) {
      throw new Error('Recording not found');
    }
    
    // Compress the recording
    const compressionStats = await this.compressRecording(
      recordingId,
      quality,
      progressCallback
    );
    
    // Read the compressed file as base64
    const fileContent = await RNFS.readFile(compressionStats.compressedPath, 'base64');
    
    // Clean up the compressed file
    await RNFS.unlink(compressionStats.compressedPath);
    
    return {
      fileContent,
      metadata,
      compressionStats
    };
  }
  
  /**
   * Clean up temp directory
   */
  public async cleanupTempFiles(): Promise<void> {
    try {
      const files = await RNFS.readDir(this.tempDir);
      
      // Delete all files in the temp directory
      for (const file of files) {
        await RNFS.unlink(file.path);
      }
    } catch (error) {
      console.error('Failed to clean up temp files:', error);
    }
  }
}

export const audioCompression = new AudioCompressionService();
