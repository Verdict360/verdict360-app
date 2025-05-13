// mobile/src/screens/AudioRecordingScreen.tsx
import { Delete, Mic, Pause, Play, Stop, Upload } from 'lucide-react-native';
import React, { useEffect, useState } from 'react';
import {
  Alert,
  Modal,
  PermissionsAndroid,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import AudioRecorderPlayer, {
  AudioEncoderAndroidType,
  AudioSourceAndroidType,
  AVEncoderAudioQualityIOSType,
  AVEncodingOption,
} from 'react-native-audio-recorder-player';
import { audioCompression, CompressionQuality } from '../services/AudioCompressionService';
import { RecordingMetadata, secureStorage } from '../services/SecureStorageService';
import { recordingSync, SyncTask } from '../services/RecordingSyncService';
import { networkService } from '../services/NetworkService';

const audioRecorderPlayer = new AudioRecorderPlayer();

interface RecordingState {
  isRecording: boolean;
  recordSecs: number;
  recordTime: string;
  isPlaying: boolean;
  currentPositionSec: number;
  currentDurationSec: number;
  playTime: string;
  duration: string;
  tempRecordingPath: string | null;
  savedRecording: RecordingMetadata | null;
}

export const AudioRecordingScreen: React.FC = () => {
  const [state, setState] = useState<RecordingState>({
    isRecording: false,
    recordSecs: 0,
    recordTime: '00:00:00',
    isPlaying: false,
    currentPositionSec: 0,
    currentDurationSec: 0,
    playTime: '00:00:00',
    duration: '00:00:00',
    tempRecordingPath: null,
    savedRecording: null,
  });

  const [showSaveModal, setShowSaveModal] = useState(false);
  const [recordingTitle, setRecordingTitle] = useState('Legal Recording');
  const [recordingDescription, setRecordingDescription] = useState('');
  const [matterId, setMatterId] = useState('');
  const [compressionProgress, setCompressionProgress] = useState(0);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedQuality, setSelectedQuality] = useState<CompressionQuality>(CompressionQuality.MEDIUM);
  const [isCompressing, setIsCompressing] = useState(false);
  const [syncTasks, setSyncTasks] = useState<SyncTask[]>([]);
  const [isConnected, setIsConnected] = useState(networkService.getIsConnected());

  // useEffect for sync status
  useEffect(() => {
    // Initial state
    setSyncTasks(recordingSync.getSyncTasks());
    setIsConnected(networkService.getIsConnected());

    // Listen for network changes
    const networkUnsubscribe = networkService.addConnectivityChangeListener(connected => {
      setIsConnected(connected);
    });

    // Listen for sync events
    const syncUnsubscribe = recordingSync.addEventListener(event => {
      if (event === 'task-updated' || event === 'sync-completed') {
        setSyncTasks(recordingSync.getSyncTasks());
      }
    });

    return () => {
      networkUnsubscribe();
      syncUnsubscribe();
    };
  }, []);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      if (state.isRecording) {
        stopRecording();
      }
      if (state.isPlaying) {
        stopPlaying();
      }
    };
  }, []);

  const requestPermissions = async (): Promise<boolean> => {
    if (Platform.OS === 'android') {
      try {
        const grants = await PermissionsAndroid.requestMultiple([
          PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
          PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
          PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
        ]);

        return (
          grants[PermissionsAndroid.PERMISSIONS.RECORD_AUDIO] === PermissionsAndroid.RESULTS.GRANTED &&
          grants[PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE] === PermissionsAndroid.RESULTS.GRANTED &&
          grants[PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE] === PermissionsAndroid.RESULTS.GRANTED
        );
      } catch (err) {
        console.warn(err);
        return false;
      }
    }
    return true; // iOS handles permissions differently
  };

  const startRecording = async () => {
    const hasPermissions = await requestPermissions();
    if (!hasPermissions) {
      Alert.alert('Permissions Required', 'Recording requires microphone and storage permissions');
      return;
    }

    try {
      const audioSet = {
        AudioEncoderAndroid: AudioEncoderAndroidType.AAC,
        AudioSourceAndroid: AudioSourceAndroidType.MIC,
        AVEncoderAudioQualityKeyIOS: AVEncoderAudioQualityIOSType.high,
        AVNumberOfChannelsKeyIOS: 2,
        AVFormatIDKeyIOS: AVEncodingOption.aac,
        OutputFormatAndroid: 2, // AAC_ADTS
        AudioSamplingRateAndroid: 44100,
        AudioBitRateAndroid: 128000,
      };

      // Get secure temporary path
      const tempPath = secureStorage.getTempRecordingPath();

      const uri = await audioRecorderPlayer.startRecorder(tempPath, audioSet);

      audioRecorderPlayer.addRecordBackListener(e => {
        setState(prevState => ({
          ...prevState,
          isRecording: true,
          recordSecs: e.currentPosition,
          recordTime: audioRecorderPlayer.mmssss(Math.floor(e.currentPosition)),
          tempRecordingPath: uri,
        }));
      });
    } catch (err) {
      console.error('Failed to start recording', err);
      Alert.alert('Error', 'Failed to start recording');
    }
  };

  const stopRecording = async () => {
    try {
      await audioRecorderPlayer.stopRecorder();
      audioRecorderPlayer.removeRecordBackListener();

      setState(prevState => ({
        ...prevState,
        isRecording: false,
      }));

      // Show save dialog if we have a recording
      if (state.tempRecordingPath) {
        setShowSaveModal(true);
      }
    } catch (err) {
      console.error('Failed to stop recording', err);
      Alert.alert('Error', 'Failed to stop recording');
    }
  };

  const saveRecording = async () => {
    if (!state.tempRecordingPath) {
      setShowSaveModal(false);
      return;
    }

    try {
      const savedRecording = await secureStorage.saveRecording(
        state.tempRecordingPath,
        recordingTitle,
        state.recordSecs / 1000, // Convert to seconds
        matterId || undefined,
        recordingDescription || undefined
      );

      setState(prevState => ({
        ...prevState,
        savedRecording,
        tempRecordingPath: null,
      }));

      setShowSaveModal(false);
      Alert.alert('Recording Saved', 'The recording has been saved securely on your device.');
    } catch (error) {
      console.error('Failed to save recording:', error);
      Alert.alert('Error', 'Failed to save recording');
      setShowSaveModal(false);
    }
  };

  const cancelSave = () => {
    // Discard the recording
    if (state.tempRecordingPath) {
      // Clean up temp file if needed
    }

    setState(prevState => ({
      ...prevState,
      tempRecordingPath: null,
    }));

    setShowSaveModal(false);
  };

  const startPlaying = async () => {
    if (!state.savedRecording) {
      Alert.alert('Error', 'No recording available');
      return;
    }

    try {
      // Get decrypted path for playback
      const decryptedPath = await secureStorage.getDecryptedRecording(state.savedRecording.id);

      await audioRecorderPlayer.startPlayer(decryptedPath);

      audioRecorderPlayer.addPlayBackListener(e => {
        if (e.currentPosition === e.duration) {
          stopPlaying();
          return;
        }

        setState(prevState => ({
          ...prevState,
          isPlaying: true,
          currentPositionSec: e.currentPosition,
          currentDurationSec: e.duration,
          playTime: audioRecorderPlayer.mmssss(Math.floor(e.currentPosition)),
          duration: audioRecorderPlayer.mmssss(Math.floor(e.duration)),
        }));
      });
    } catch (err) {
      console.error('Failed to start playback', err);
      Alert.alert('Error', 'Failed to play recording');
    }
  };

  const stopPlaying = async () => {
    try {
      await audioRecorderPlayer.stopPlayer();
      audioRecorderPlayer.removePlayBackListener();
      setState(prevState => ({
        ...prevState,
        isPlaying: false,
      }));
    } catch (err) {
      console.error('Failed to stop playback', err);
    }
  };

  const deleteRecording = async () => {
    if (!state.savedRecording) return;

    Alert.alert('Delete Recording', 'Are you sure you want to delete this recording? This cannot be undone.', [
      {
        text: 'Cancel',
        style: 'cancel',
      },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          try {
            await secureStorage.deleteRecording(state.savedRecording!.id);
            setState(prevState => ({
              ...prevState,
              savedRecording: null,
              recordSecs: 0,
              recordTime: '00:00:00',
              currentPositionSec: 0,
              currentDurationSec: 0,
              playTime: '00:00:00',
              duration: '00:00:00',
            }));
            Alert.alert('Recording Deleted', 'The recording has been deleted');
          } catch (error) {
            console.error('Failed to delete recording:', error);
            Alert.alert('Error', 'Failed to delete recording');
          }
        },
      },
    ]);
  };

  const uploadRecording = () => {
    if (!state.savedRecording) return;

    if (!isConnected) {
      // Offline mode - add to sync queue
      Alert.alert(
        'Offline Mode',
        'You appear to be offline. The recording will be queued for upload when your device is online.',
        [
          {
            text: 'Cancel',
            style: 'cancel',
          },
          {
            text: 'Queue for Upload',
            onPress: () => {
              try {
                recordingSync.addToSyncQueue(state.savedRecording!.id);
                Alert.alert(
                  'Added to Queue',
                  'The recording will be uploaded automatically when your device is online.'
                );

                // Refresh sync tasks
                setSyncTasks(recordingSync.getSyncTasks());
              } catch (error) {
                console.error('Failed to queue recording:', error);
                Alert.alert('Error', 'Failed to queue recording for upload');
              }
            },
          },
        ]
      );
    } else {
      // Online mode - show compression options
      setShowUploadModal(true);
    }
  };

  const handleCompressionAndUpload = async () => {
    if (!state.savedRecording) {
      setShowUploadModal(false);
      return;
    }

    try {
      setIsCompressing(true);

      // Compress the recording with progress updates
      const result = await audioCompression.prepareForUpload(state.savedRecording.id, selectedQuality, progress => {
        setCompressionProgress(progress);
      });

      // Log compression stats
      console.log('Compression complete:', result.compressionStats);
      console.log(`Original size: ${(result.compressionStats.originalSize / 1024 / 1024).toFixed(2)} MB`);
      console.log(`Compressed size: ${(result.compressionStats.compressedSize / 1024 / 1024).toFixed(2)} MB`);
      console.log(`Compression ratio: ${result.compressionStats.compressionRatio.toFixed(2)}x`);

      setIsCompressing(false);
      setShowUploadModal(false);

      // In a real implementation, you would upload to the server here
      Alert.alert(
        'Compression Complete',
        `File compressed from ${(result.compressionStats.originalSize / 1024 / 1024).toFixed(2)} MB to ${(
          result.compressionStats.compressedSize /
          1024 /
          1024
        ).toFixed(2)} MB (${result.compressionStats.compressionRatio.toFixed(
          2
        )}x reduction).\n\nUpload functionality will be available in the next build.`
      );
    } catch (error) {
      console.error('Compression failed:', error);
      setIsCompressing(false);
      setShowUploadModal(false);
      Alert.alert('Error', 'Failed to compress recording');
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>{state.savedRecording ? state.savedRecording.title : 'Legal Recording'}</Text>

        <View style={styles.timerContainer}>
          <Text style={styles.timer}>
            {state.isRecording
              ? state.recordTime
              : state.isPlaying
              ? state.playTime
              : state.savedRecording
              ? audioRecorderPlayer.mmssss(Math.floor(state.savedRecording.duration * 1000))
              : '00:00:00'}
          </Text>
          <Text style={styles.status}>
            {state.isRecording
              ? 'Recording...'
              : state.isPlaying
              ? 'Playing...'
              : state.savedRecording
              ? 'Ready'
              : 'Ready to Record'}
          </Text>
        </View>

        <View style={styles.controlsContainer}>
          {!state.isRecording && !state.savedRecording && (
            <TouchableOpacity style={styles.recordButton} onPress={startRecording}>
              <Mic size={32} color='#FFFFFF' />
            </TouchableOpacity>
          )}

          {state.isRecording && (
            <TouchableOpacity style={[styles.recordButton, styles.stopButton]} onPress={stopRecording}>
              <Stop size={32} color='#FFFFFF' />
            </TouchableOpacity>
          )}

          {!state.isRecording && state.savedRecording && !state.isPlaying && (
            <TouchableOpacity style={[styles.controlButton, styles.playButton]} onPress={startPlaying}>
              <Play size={24} color='#FFFFFF' />
            </TouchableOpacity>
          )}

          {!state.isRecording && state.savedRecording && state.isPlaying && (
            <TouchableOpacity style={[styles.controlButton, styles.pauseButton]} onPress={stopPlaying}>
              <Pause size={24} color='#FFFFFF' />
            </TouchableOpacity>
          )}

          {!state.isRecording && state.savedRecording && (
            <>
              <TouchableOpacity style={[styles.controlButton, styles.uploadButton]} onPress={uploadRecording}>
                <Upload size={24} color='#FFFFFF' />
              </TouchableOpacity>

              <TouchableOpacity style={[styles.controlButton, styles.deleteButton]} onPress={deleteRecording}>
                <Delete size={24} color='#FFFFFF' />
              </TouchableOpacity>
            </>
          )}
        </View>

        {state.savedRecording && (
          <View style={styles.infoContainer}>
            <Text style={styles.infoLabel}>Recording Details:</Text>
            <Text style={styles.infoText}>Title: {state.savedRecording.title}</Text>
            {state.savedRecording.description && (
              <Text style={styles.infoText}>Description: {state.savedRecording.description}</Text>
            )}
            {state.savedRecording.matterId && (
              <Text style={styles.infoText}>Matter ID: {state.savedRecording.matterId}</Text>
            )}
            <Text style={styles.infoText}>
              Created: {new Date(state.savedRecording.createdAt).toLocaleDateString()} at{' '}
              {new Date(state.savedRecording.createdAt).toLocaleTimeString()}
            </Text>
            <Text style={styles.infoText}>Duration: {Math.floor(state.savedRecording.duration)} seconds</Text>
            <Text style={styles.infoText}>Size: {(state.savedRecording.size / (1024 * 1024)).toFixed(2)} MB</Text>
          </View>
        )}
      </View>

      <View style={styles.helpContainer}>
        <Text style={styles.helpTitle}>Recording Guidelines</Text>
        <Text style={styles.helpText}>• Ensure a quiet environment for optimal audio quality</Text>
        <Text style={styles.helpText}>• Place the device close to the speaker</Text>
        <Text style={styles.helpText}>• State the matter reference at the beginning</Text>
        <Text style={styles.helpText}>• Identify all speakers before they begin speaking</Text>
        <Text style={styles.helpText}>• All recordings are encrypted on your device</Text>
      </View>

      {syncTasks.length > 0 && (
        <View style={styles.syncStatus}>
          <Text style={styles.syncTitle}>Upload Queue</Text>

          {syncTasks.map(task => {
            const metadata = secureStorage.getMetadata(task.recordingId);
            const title = metadata ? metadata.title : 'Unknown recording';

            let statusColor = '#4F46E5'; // Default (pending)
            if (task.status === 'in_progress') statusColor = '#F59E0B';
            else if (task.status === 'completed') statusColor = '#10B981';
            else if (task.status === 'failed') statusColor = '#EF4444';

            return (
              <View key={task.id} style={styles.syncItem}>
                <View style={styles.syncItemHeader}>
                  <Text style={styles.syncItemTitle}>{title}</Text>
                  <View style={[styles.statusDot, { backgroundColor: statusColor }]} />
                </View>

                <Text style={styles.syncItemStatus}>
                  {task.status === 'pending' && 'Waiting to upload...'}
                  {task.status === 'in_progress' && 'Uploading...'}
                  {task.status === 'completed' && 'Upload complete'}
                  {task.status === 'failed' && `Failed (${task.error || 'Unknown error'})`}
                </Text>

                {task.status === 'failed' && (
                  <TouchableOpacity style={styles.retryButton} onPress={() => recordingSync.retryTask(task.id)}>
                    <Text style={styles.retryText}>Retry</Text>
                  </TouchableOpacity>
                )}
              </View>
            );
          })}

          <View style={styles.syncFooter}>
            <Text style={styles.syncFooterText}>
              {isConnected ? 'Connected - Uploads in progress' : 'Offline - Uploads will resume when connected'}
            </Text>
          </View>
        </View>
      )}

      {/* Save Recording Modal */}
      <Modal
        visible={showSaveModal}
        transparent={true}
        animationType='slide'
        onRequestClose={() => setShowSaveModal(false)}>
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Save Recording</Text>

            <View style={styles.formGroup}>
              <Text style={styles.label}>Title*</Text>
              <TextInput
                style={styles.input}
                value={recordingTitle}
                onChangeText={setRecordingTitle}
                placeholder='Enter recording title'
              />
            </View>

            <View style={styles.formGroup}>
              <Text style={styles.label}>Description</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={recordingDescription}
                onChangeText={setRecordingDescription}
                placeholder='Enter optional description'
                multiline
                numberOfLines={3}
              />
            </View>

            <View style={styles.formGroup}>
              <Text style={styles.label}>Matter ID</Text>
              <TextInput
                style={styles.input}
                value={matterId}
                onChangeText={setMatterId}
                placeholder='Enter matter ID (optional)'
              />
            </View>

            <View style={styles.modalActions}>
              <TouchableOpacity style={styles.cancelButton} onPress={cancelSave}>
                <Text style={styles.buttonText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.saveButton, !recordingTitle && styles.disabledButton]}
                onPress={saveRecording}
                disabled={!recordingTitle}>
                <Text style={styles.buttonText}>Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Upload Modal */}
      <Modal
        visible={showUploadModal}
        transparent={true}
        animationType='slide'
        onRequestClose={() => setShowUploadModal(false)}>
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Upload Recording</Text>

            {isCompressing ? (
              <View style={styles.compressionProgress}>
                <Text style={styles.compressionText}>Compressing recording...</Text>
                <View style={styles.progressBarContainer}>
                  <View style={[styles.progressBar, { width: `${compressionProgress}%` }]} />
                </View>
                <Text style={styles.compressionPercent}>{Math.round(compressionProgress)}%</Text>
              </View>
            ) : (
              <>
                <Text style={styles.modalSubtitle}>Select compression quality for upload</Text>

                <View style={styles.qualityOptions}>
                  <TouchableOpacity
                    style={[styles.qualityOption, selectedQuality === CompressionQuality.HIGH && styles.selectedQuality]}
                    onPress={() => setSelectedQuality(CompressionQuality.HIGH)}>
                    <Text style={styles.qualityTitle}>High</Text>
                    <Text style={styles.qualityDesc}>Better quality, larger file</Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[
                      styles.qualityOption,
                      selectedQuality === CompressionQuality.MEDIUM && styles.selectedQuality,
                    ]}
                    onPress={() => setSelectedQuality(CompressionQuality.MEDIUM)}>
                    <Text style={styles.qualityTitle}>Medium</Text>
                    <Text style={styles.qualityDesc}>Balanced quality & size</Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[
                      styles.qualityOption,
                      selectedQuality === CompressionQuality.VOICE && styles.selectedQuality,
                    ]}
                    onPress={() => setSelectedQuality(CompressionQuality.VOICE)}>
                    <Text style={styles.qualityTitle}>Voice</Text>
                    <Text style={styles.qualityDesc}>Optimized for voice</Text>
                  </TouchableOpacity>
                </View>

                <View style={styles.modalActions}>
                  <TouchableOpacity style={styles.cancelButton} onPress={() => setShowUploadModal(false)}>
                    <Text style={styles.buttonText}>Cancel</Text>
                  </TouchableOpacity>

                  <TouchableOpacity style={styles.uploadButton} onPress={handleCompressionAndUpload}>
                    <Text style={styles.buttonText}>Compress & Upload</Text>
                  </TouchableOpacity>
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#F9FAFB',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 24,
    textAlign: 'center',
    color: '#4F46E5', // Primary color
  },
  timerContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  timer: {
    fontSize: 48,
    fontWeight: '700',
    color: '#1E293B', // Secondary color
    fontVariant: ['tabular-nums'],
  },
  status: {
    marginTop: 8,
    fontSize: 16,
    color: '#64748B',
  },
  controlsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  recordButton: {
    backgroundColor: '#4F46E5', // Primary color
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  stopButton: {
    backgroundColor: '#EF4444', // Red color
  },
  controlButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 8,
  },
  playButton: {
    backgroundColor: '#4F46E5', // Primary color
  },
  pauseButton: {
    backgroundColor: '#F59E0B', // Amber color
  },
  uploadButton: {
    backgroundColor: '#10B981', // Green color
  },
  deleteButton: {
    backgroundColor: '#EF4444', // Red color
  },
  infoContainer: {
    backgroundColor: '#F3F4F6',
    padding: 12,
    borderRadius: 8,
  },
  infoLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4B5563',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#64748B',
    marginBottom: 4,
  },
  pathText: {
    fontSize: 12,
    color: '#94A3B8',
  },
  helpContainer: {
    marginTop: 24,
  },
  helpTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#1E293B', // Secondary color
  },
  helpText: {
    fontSize: 14,
    color: '#64748B',
    marginBottom: 6,
  },
  // Modal styles
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    width: '100%',
    maxWidth: 400,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 16,
    color: '#1E293B',
    textAlign: 'center',
  },
  formGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
    color: '#4B5563',
  },
  input: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 6,
    padding: 12,
    fontSize: 16,
    color: '#1E293B',
    backgroundColor: '#F9FAFB',
  },
  textArea: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
  },
  cancelButton: {
    backgroundColor: '#6B7280',
    borderRadius: 6,
    padding: 12,
    flex: 1,
    marginRight: 8,
    alignItems: 'center',
  },
  saveButton: {
    backgroundColor: '#4F46E5',
    borderRadius: 6,
    padding: 12,
    flex: 1,
    marginLeft: 8,
    alignItems: 'center',
  },
  disabledButton: {
    backgroundColor: '#A5B4FC',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '500',
  },
  // Compression styles
  compressionProgress: {
    alignItems: 'center',
    padding: 20,
  },
  compressionText: {
    fontSize: 16,
    marginBottom: 16,
    color: '#4B5563',
  },
  progressBarContainer: {
    width: '100%',
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#4F46E5',
    borderRadius: 4,
  },
  compressionPercent: {
    fontSize: 14,
    color: '#6B7280',
  },
  modalSubtitle: {
    fontSize: 16,
    color: '#4B5563',
    marginBottom: 16,
    textAlign: 'center',
  },
  qualityOptions: {
    marginBottom: 20,
  },
  qualityOption: {
    padding: 16,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    marginBottom: 8,
  },
  selectedQuality: {
    borderColor: '#4F46E5',
    backgroundColor: 'rgba(79, 70, 229, 0.05)',
  },
  qualityTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 4,
  },
  qualityDesc: {
    fontSize: 14,
    color: '#6B7280',
  },
  // Sync Status styles
  syncStatus: {
    marginTop: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  syncTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 12,
  },
  syncItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  syncItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  syncItemTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#334155',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  syncItemStatus: {
    fontSize: 14,
    color: '#64748B',
  },
  retryButton: {
    alignSelf: 'flex-start',
    marginTop: 8,
    paddingVertical: 4,
    paddingHorizontal: 12,
    backgroundColor: '#F1F5F9',
    borderRadius: 4,
  },
  retryText: {
    fontSize: 14,
    color: '#4F46E5',
    fontWeight: '500',
  },
  syncFooter: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  syncFooterText: {
    fontSize: 14,
    color: '#64748B',
    textAlign: 'center',
  },
});
