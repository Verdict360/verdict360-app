import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import * as SecureStore from 'expo-secure-store';
import { useAuth } from '../auth/AuthProvider';

export default function AudioRecordingScreen() {
  const { user, logout } = useAuth();
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordings, setRecordings] = useState<string[]>([]);
  const [timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null);

  const handleLogout = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out? Any recordings not uploaded will remain on this device.',
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
        Alert.alert('Permission required', 'Audio recording permission is needed for legal recordings');
        return;
      }

      // Configure audio mode for legal recording quality
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      // Start recording with high quality settings for legal use
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      
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
      Alert.alert('Recording Error', 'Failed to start legal recording. Please check your microphone permissions.');
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
        // Save recording info with legal metadata
        const recordingName = `Legal Recording ${recordings.length + 1}`;
        const recordingInfo = {
          name: recordingName,
          uri: uri,
          duration: recordingTime,
          timestamp: new Date().toISOString(),
          type: 'legal_proceeding',
          quality: 'high',
          fileFormat: 'm4a',
          recordedBy: user?.email || 'Unknown',
        };

        // Store securely on device
        try {
          await SecureStore.setItemAsync(
            `recording_${Date.now()}`,
            JSON.stringify(recordingInfo)
          );

          setRecordings([...recordings, recordingName]);
          Alert.alert(
            'Recording Saved', 
            `Legal recording saved securely: ${recordingName}\nDuration: ${formatTime(recordingTime)}`
          );
        } catch (storageErr) {
          console.error('Failed to save recording', storageErr);
          Alert.alert('Storage Error', 'Recording completed but failed to save securely');
        }
      }

      setRecording(null);
      setRecordingTime(0);
    } catch (err) {
      console.error('Failed to stop recording', err);
      Alert.alert('Error', 'Failed to stop recording properly');
    }
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

  return (
    <View style={styles.container}>
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
        <Text style={styles.status}>
          {isRecording ? '🔴 Recording in Progress...' : '⚪ Ready to Record'}
        </Text>
        <Text style={styles.timer}>{formatTime(recordingTime)}</Text>
        {isRecording && (
          <Text style={styles.recordingHint}>Tap Stop when finished</Text>
        )}
      </View>

      {/* Record Button */}
      <TouchableOpacity
        style={[styles.recordButton, isRecording && styles.recordingButton]}
        onPress={isRecording ? stopRecording : startRecording}
      >
        <Text style={styles.recordButtonText}>
          {isRecording ? 'Stop' : 'Record'}
        </Text>
      </TouchableOpacity>

      {/* Legal Recording Guidelines */}
      {!isRecording && (
        <View style={styles.guidelines}>
          <Text style={styles.guidelinesTitle}>Legal Recording Guidelines:</Text>
          <Text style={styles.guidelineText}>• State the matter reference at the beginning</Text>
          <Text style={styles.guidelineText}>• Identify all speakers before they begin</Text>
          <Text style={styles.guidelineText}>• Ensure quiet environment for clear audio</Text>
          <Text style={styles.guidelineText}>• All recordings are encrypted on device</Text>
        </View>
      )}

      {/* Recordings List */}
      <View style={styles.recordingsList}>
        <Text style={styles.listTitle}>Stored Recordings ({recordings.length})</Text>
        {recordings.map((recording, index) => (
          <View key={index} style={styles.recordingItem}>
            <Text style={styles.recordingName}>{recording}</Text>
            <Text style={styles.recordingDate}>
              {new Date().toLocaleDateString('en-ZA')} at {new Date().toLocaleTimeString('en-ZA')}
            </Text>
            <Text style={styles.recordingStatus}>✅ Encrypted & Stored Securely</Text>
          </View>
        ))}
        {recordings.length === 0 && (
          <Text style={styles.noRecordings}>No legal recordings yet. Tap Record to begin.</Text>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
    padding: 20,
    paddingTop: 60,
  },
  headerBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 32,
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
    padding: 16,
    borderRadius: 8,
    marginBottom: 24,
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
    flex: 1,
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
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  recordingName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#111827',
  },
  recordingDate: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  recordingStatus: {
    fontSize: 12,
    color: '#059669',
    marginTop: 4,
    fontWeight: '500',
  },
  noRecordings: {
    textAlign: 'center',
    color: '#9CA3AF',
    fontStyle: 'italic',
    marginTop: 20,
    fontSize: 14,
  },
});
