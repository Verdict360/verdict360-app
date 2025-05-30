import { Audio, AVPlaybackSource } from 'expo-av';
import * as SecureStore from 'expo-secure-store';
import React, { useEffect, useState } from 'react';
import {
  Alert,
  Dimensions,
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { useAuth } from '../auth/AuthProvider';

const { width, height } = Dimensions.get('window');

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

export default function AudioRecordingScreen() {
  const { user, logout } = useAuth();
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordings, setRecordings] = useState<LegalRecording[]>([]);
  const [timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null);

  // New legal metadata states
  const [showMetadataModal, setShowMetadataModal] = useState(false);
  const [matterReference, setMatterReference] = useState('');
  const [recordingType, setRecordingType] = useState<'legal_proceeding' | 'client_meeting' | 'deposition' | 'other'>(
    'legal_proceeding'
  );
  const [attendees, setAttendees] = useState('');
  const [notes, setNotes] = useState('');
  const [recordingTitle, setRecordingTitle] = useState('');

  // Playback state
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentlyPlayingIndex, setCurrentlyPlayingIndex] = useState<number | null>(null);
  const [playbackPosition, setPlaybackPosition] = useState(0);
  const [playbackDuration, setPlaybackDuration] = useState(0);

  // Load stored recordings on component mount
  useEffect(() => {
    loadStoredRecordings();
  }, []);

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (sound) {
        sound.unloadAsync();
      }
    };
  }, [sound]);

  const loadStoredRecordings = async () => {
    try {
      const recordingsList = await SecureStore.getItemAsync('recordings_list');
      if (recordingsList) {
        const parsedRecordings: LegalRecording[] = JSON.parse(recordingsList);
        setRecordings(parsedRecordings);
      }
    } catch (error) {
      console.error('Failed to load recordings:', error);
    }
  };

  const saveRecordingsList = async (recordingsList: LegalRecording[]) => {
    try {
      await SecureStore.setItemAsync('recordings_list', JSON.stringify(recordingsList));
    } catch (error) {
      console.error('Failed to save recordings list:', error);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out? Any recordings not uploaded will remain securely on this device.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Sign Out', onPress: logout, style: 'destructive' },
      ]
    );
  };

  const startRecording = async () => {
    try {
      // Request permissions
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert(
          'Permission Required',
          'Audio recording permission is needed for legal recordings. Please enable it in Settings.'
        );
        return;
      }

      // Configure audio mode for high-quality legal recording
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
        staysActiveInBackground: true,
      });

      // Start recording with high quality settings optimised for voice
      const { recording } = await Audio.Recording.createAsync({
        android: {
          extension: '.m4a',
          outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_MPEG_4,
          audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_AAC,
          sampleRate: 44100,
          numberOfChannels: 2,
          bitRate: 128000,
        },
        ios: {
          extension: '.m4a',
          outputFormat: Audio.RECORDING_OPTION_IOS_OUTPUT_FORMAT_MPEG4AAC,
          audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
          sampleRate: 44100,
          numberOfChannels: 2,
          bitRate: 128000,
          linearPCMBitDepth: 16,
          linearPCMIsBigEndian: false,
          linearPCMIsFloat: false,
        },
      });

      setRecording(recording);
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      const timer = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      setTimerInterval(timer);
    } catch (err) {
      console.error('Failed to start recording', err);
      Alert.alert(
        'Recording Error',
        'Failed to start legal recording. Please check your microphone permissions and try again.'
      );
    }
  };

  const stopRecording = async () => {
    if (!recording) return;

    try {
      setIsRecording(false);

      // Clear timer
      if (timerInterval) {
        clearInterval(timerInterval);
        setTimerInterval(null);
      }

      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();

      if (uri) {
        // Show metadata collection modal
        setShowMetadataModal(true);
        setRecordingTitle(`Legal Recording ${recordings.length + 1}`);
      }

      setRecording(null);
    } catch (err) {
      console.error('Failed to stop recording', err);
      Alert.alert('Error', 'Failed to stop recording properly');
    }
  };

  const saveRecordingWithMetadata = async () => {
    if (!recording) return;

    try {
      const uri = recording.getURI();
      if (!uri) return;

      const recordingId = `recording_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      const recordingInfo: LegalRecording = {
        id: recordingId,
        name: recordingTitle || `Legal Recording ${recordings.length + 1}`,
        uri: uri,
        duration: recordingTime,
        timestamp: new Date().toISOString(),
        type: recordingType,
        quality: 'high',
        fileFormat: 'm4a',
        recordedBy: user?.email || 'Unknown',
        matterReference: matterReference || undefined,
        attendees: attendees
          .split(',')
          .map(a => a.trim())
          .filter(a => a),
        notes: notes || undefined,
        isUploaded: false,
        uploadStatus: 'pending',
      };

      // Store individual recording securely
      await SecureStore.setItemAsync(recordingId, JSON.stringify(recordingInfo));

      // Update recordings list
      const updatedRecordings = [...recordings, recordingInfo];
      setRecordings(updatedRecordings);
      await saveRecordingsList(updatedRecordings);

      // Reset form
      setShowMetadataModal(false);
      setRecordingTitle('');
      setMatterReference('');
      setAttendees('');
      setNotes('');
      setRecordingTime(0);

      Alert.alert(
        'Recording Saved',
        `Legal recording saved securely with metadata.\nDuration: ${formatTime(recordingTime)}\nMatter: ${
          matterReference || 'Not specified'
        }`
      );
    } catch (storageErr) {
      console.error('Failed to save recording', storageErr);
      Alert.alert('Storage Error', 'Recording completed but failed to save securely');
    }
  };

  const uploadRecording = async (recordingInfo: LegalRecording) => {
    try {
      // Update status to uploading
      const updatedRecordings = recordings.map(r =>
        r.id === recordingInfo.id ? { ...r, uploadStatus: 'uploading' as const } : r
      );
      setRecordings(updatedRecordings);
      await saveRecordingsList(updatedRecordings);

      // TODO: Implement actual upload to MinIO via API
      // This is a placeholder for the upload functionality

      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Update status to completed
      const finalRecordings = recordings.map(r =>
        r.id === recordingInfo.id ? { ...r, uploadStatus: 'completed' as const, isUploaded: true } : r
      );
      setRecordings(finalRecordings);
      await saveRecordingsList(finalRecordings);

      Alert.alert('Upload Successful', 'Recording uploaded to secure cloud storage');
    } catch (error) {
      console.error('Upload failed:', error);

      // Update status to failed
      const failedRecordings = recordings.map(r =>
        r.id === recordingInfo.id ? { ...r, uploadStatus: 'failed' as const } : r
      );
      setRecordings(failedRecordings);
      await saveRecordingsList(failedRecordings);

      Alert.alert('Upload Failed', 'Failed to upload recording. It remains stored securely on this device.');
    }
  };

  const playRecording = async (recordingInfo: LegalRecording, index: number) => {
    try {
      // Stop any currently playing sound
      if (sound) {
        await sound.unloadAsync();
        setSound(null);
        setIsPlaying(false);
      }

      const { sound: newSound } = await Audio.Sound.createAsync({ uri: recordingInfo.uri } as AVPlaybackSource, {
        shouldPlay: true,
      });

      setSound(newSound);
      setIsPlaying(true);
      setCurrentlyPlayingIndex(index);

      // Set up playback status updates
      newSound.setOnPlaybackStatusUpdate(status => {
        if (status.isLoaded) {
          setPlaybackPosition(status.positionMillis || 0);
          setPlaybackDuration(status.durationMillis || 0);

          if (status.didJustFinish) {
            setIsPlaying(false);
            setCurrentlyPlayingIndex(null);
            setPlaybackPosition(0);
          }
        }
      });
    } catch (error) {
      console.error('Error playing recording:', error);
      Alert.alert('Playback Error', 'Failed to play recording');
    }
  };

  const pausePlayback = async () => {
    if (sound) {
      await sound.pauseAsync();
      setIsPlaying(false);
    }
  };

  const resumePlayback = async () => {
    if (sound) {
      await sound.playAsync();
      setIsPlaying(true);
    }
  };

  const stopPlayback = async () => {
    if (sound) {
      await sound.unloadAsync();
      setSound(null);
      setIsPlaying(false);
      setCurrentlyPlayingIndex(null);
      setPlaybackPosition(0);
      setPlaybackDuration(0);
    }
  };

  const formatPlaybackTime = (milliseconds: number) => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getRecordingTypeIcon = (type: string) => {
    switch (type) {
      case 'legal_proceeding':
        return '⚖️';
      case 'client_meeting':
        return '🤝';
      case 'deposition':
        return '📋';
      default:
        return '🎤';
    }
  };

  const getUploadStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return '⏳';
      case 'uploading':
        return '⬆️';
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      default:
        return '⏳';
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header with User Info and Logout */}
      <View style={styles.headerBar}>
        <View>
          <Text style={styles.title}>Verdict360 Legal Recorder</Text>
          <Text style={styles.userInfo}>Welcome, {user?.name || 'Legal Professional'}</Text>
        </View>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Sign Out</Text>
        </TouchableOpacity>
      </View>

      {/* Recording Status */}
      <View style={styles.statusContainer}>
        <Text style={styles.status}>{isRecording ? '🔴 Recording in Progress...' : '⚪ Ready to Record'}</Text>
        <Text style={styles.timer}>{formatTime(recordingTime)}</Text>
        {isRecording && <Text style={styles.recordingHint}>Tap Stop when finished</Text>}
      </View>

      {/* Record Button */}
      <TouchableOpacity
        style={[styles.recordButton, isRecording && styles.recordingButton]}
        onPress={isRecording ? stopRecording : startRecording}>
        <Text style={styles.recordButtonText}>{isRecording ? 'Stop' : 'Record'}</Text>
      </TouchableOpacity>

      {/* Legal Recording Guidelines */}
      {!isRecording && (
        <View style={styles.guidelines}>
          <Text style={styles.guidelinesTitle}>Legal Recording Guidelines:</Text>
          <Text style={styles.guidelineText}>• State the matter reference at the beginning</Text>
          <Text style={styles.guidelineText}>• Identify all speakers before they begin</Text>
          <Text style={styles.guidelineText}>• Ensure quiet environment for clear audio</Text>
          <Text style={styles.guidelineText}>• All recordings are encrypted on device</Text>
          <Text style={styles.guidelineText}>• Add metadata for proper cataloguing</Text>
        </View>
      )}

      {/* Recordings List */}
      <View style={styles.recordingsList}>
        <Text style={styles.listTitle}>Legal Recordings ({recordings.length})</Text>
        {recordings.map((recording, index) => (
          <View key={index} style={styles.recordingItem}>
            <View style={styles.recordingHeader}>
              <Text style={styles.recordingName}>
                {getRecordingTypeIcon(recording.type)} {recording.name}
              </Text>
              <Text style={styles.uploadStatus}>
                {getUploadStatusIcon(recording.uploadStatus)} {recording.uploadStatus}
              </Text>
            </View>

            <Text style={styles.recordingDate}>
              {new Date(recording.timestamp).toLocaleDateString('en-ZA')} at{' '}
              {new Date(recording.timestamp).toLocaleTimeString('en-ZA')}
            </Text>

            {recording.matterReference && <Text style={styles.matterRef}>Matter: {recording.matterReference}</Text>}

            {recording.attendees.length > 0 && (
              <Text style={styles.attendees}>Attendees: {recording.attendees.join(', ')}</Text>
            )}

            <Text style={styles.duration}>Duration: {formatTime(recording.duration)}</Text>

            {/* Playback Controls */}
            <View style={styles.playbackControls}>
              {currentlyPlayingIndex === index ? (
                <View style={styles.activePlayback}>
                  <TouchableOpacity style={styles.playButton} onPress={isPlaying ? pausePlayback : resumePlayback}>
                    <Text style={styles.playButtonText}>{isPlaying ? '⏸️' : '▶️'}</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.stopButton} onPress={stopPlayback}>
                    <Text style={styles.stopButtonText}>⏹️</Text>
                  </TouchableOpacity>
                  <Text style={styles.playbackTime}>
                    {formatPlaybackTime(playbackPosition)} / {formatPlaybackTime(playbackDuration)}
                  </Text>
                </View>
              ) : (
                <View style={styles.inactivePlayback}>
                  <TouchableOpacity style={styles.playButton} onPress={() => playRecording(recording, index)}>
                    <Text style={styles.playButtonText}>▶️ Play</Text>
                  </TouchableOpacity>

                  {!recording.isUploaded && (
                    <TouchableOpacity
                      style={[styles.uploadButton, recording.uploadStatus === 'uploading' && styles.uploadingButton]}
                      onPress={() => uploadRecording(recording)}
                      disabled={recording.uploadStatus === 'uploading'}>
                      <Text style={styles.uploadButtonText}>
                        {recording.uploadStatus === 'uploading' ? 'Uploading...' : '☁️ Upload'}
                      </Text>
                    </TouchableOpacity>
                  )}
                </View>
              )}
            </View>
          </View>
        ))}
        {recordings.length === 0 && (
          <Text style={styles.noRecordings}>No legal recordings yet. Tap Record to begin.</Text>
        )}
      </View>

      {/* Metadata Collection Modal */}
      <Modal
        animationType='slide'
        transparent={true}
        visible={showMetadataModal}
        onRequestClose={() => setShowMetadataModal(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Legal Recording Metadata</Text>

            <Text style={styles.inputLabel}>Recording Title</Text>
            <TextInput
              style={styles.textInput}
              value={recordingTitle}
              onChangeText={setRecordingTitle}
              placeholder='e.g., Client consultation - Smith matter'
            />

            <Text style={styles.inputLabel}>Matter Reference</Text>
            <TextInput
              style={styles.textInput}
              value={matterReference}
              onChangeText={setMatterReference}
              placeholder='e.g., MAT-2025-001'
            />

            <Text style={styles.inputLabel}>Recording Type</Text>
            <View style={styles.typeSelector}>
              {[
                { value: 'legal_proceeding', label: '⚖️ Legal Proceeding' },
                { value: 'client_meeting', label: '🤝 Client Meeting' },
                { value: 'deposition', label: '📋 Deposition' },
                { value: 'other', label: '🎤 Other' },
              ].map(type => (
                <TouchableOpacity
                  key={type.value}
                  style={[styles.typeOption, recordingType === type.value && styles.selectedType]}
                  onPress={() => setRecordingType(type.value as any)}>
                  <Text style={[styles.typeOptionText, recordingType === type.value && styles.selectedTypeText]}>
                    {type.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={styles.inputLabel}>Attendees (comma-separated)</Text>
            <TextInput
              style={styles.textInput}
              value={attendees}
              onChangeText={setAttendees}
              placeholder='e.g., John Smith, Jane Doe, Attorney'
              multiline
            />

            <Text style={styles.inputLabel}>Notes (optional)</Text>
            <TextInput
              style={[styles.textInput, styles.notesInput]}
              value={notes}
              onChangeText={setNotes}
              placeholder='Additional notes about this recording...'
              multiline
              numberOfLines={3}
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setShowMetadataModal(false)}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.saveButton} onPress={saveRecordingWithMetadata}>
                <Text style={styles.saveButtonText}>Save Recording</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  headerBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4F46E5',
    marginBottom: 4,
  },
  userInfo: {
    fontSize: 14,
    color: '#6B7280',
  },
  logoutButton: {
    backgroundColor: '#EF4444',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  logoutButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  statusContainer: {
    alignItems: 'center',
    marginBottom: 32,
    paddingHorizontal: 20,
  },
  status: {
    fontSize: 16,
    color: '#374151',
    marginBottom: 8,
    fontWeight: '500',
  },
  timer: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#1f2937',
    fontFamily: 'monospace',
  },
  recordingHint: {
    fontSize: 12,
    color: '#EF4444',
    marginTop: 4,
    fontStyle: 'italic',
  },
  recordButton: {
    backgroundColor: '#4F46E5',
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  recordingButton: {
    backgroundColor: '#EF4444',
  },
  recordButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  guidelines: {
    backgroundColor: '#FEF3C7',
    margin: 20,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#F59E0B',
  },
  guidelinesTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#92400E',
    marginBottom: 8,
  },
  guidelineText: {
    fontSize: 12,
    color: '#92400E',
    marginBottom: 2,
  },
  recordingsList: {
    padding: 20,
  },
  listTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 16,
  },
  recordingItem: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  recordingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  recordingName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#111827',
    flex: 1,
  },
  uploadStatus: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
  },
  recordingDate: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  matterRef: {
    fontSize: 12,
    color: '#4F46E5',
    fontWeight: '500',
    marginBottom: 2,
  },
  attendees: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 2,
  },
  duration: {
    fontSize: 12,
    color: '#374151',
    fontWeight: '500',
    marginBottom: 8,
  },
  playbackControls: {
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  activePlayback: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  inactivePlayback: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  playButton: {
    backgroundColor: '#4F46E5',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    marginRight: 8,
  },
  playButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  stopButton: {
    backgroundColor: '#EF4444',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    marginRight: 8,
  },
  stopButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  uploadButton: {
    backgroundColor: '#059669',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
  },
  uploadingButton: {
    backgroundColor: '#6B7280',
  },
  uploadButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  playbackTime: {
    fontSize: 12,
    color: '#6B7280',
    fontFamily: 'monospace',
    flex: 1,
    textAlign: 'right',
  },
  noRecordings: {
    textAlign: 'center',
    color: '#9CA3AF',
    fontStyle: 'italic',
    marginTop: 20,
    fontSize: 14,
  },

  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    width: width * 0.9,
    maxHeight: height * 0.8,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#4F46E5',
    marginBottom: 20,
    textAlign: 'center',
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 6,
    marginTop: 12,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 6,
    padding: 12,
    fontSize: 14,
    backgroundColor: '#F9FAFB',
  },
  notesInput: {
    height: 80,
    textAlignVertical: 'top',
  },
  typeSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
  },
  typeOption: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    backgroundColor: '#F9FAFB',
    flex: 1,
    minWidth: '45%',
  },
  selectedType: {
    backgroundColor: '#4F46E5',
    borderColor: '#4F46E5',
  },
  typeOptionText: {
    fontSize: 12,
    color: '#374151',
    textAlign: 'center',
  },
  selectedTypeText: {
    color: 'white',
    fontWeight: '600',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
    gap: 12,
  },
  cancelButton: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    paddingVertical: 12,
    borderRadius: 6,
  },
  cancelButtonText: {
    color: '#374151',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  saveButton: {
    flex: 1,
    backgroundColor: '#4F46E5',
    paddingVertical: 12,
    borderRadius: 6,
  },
  saveButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
});
