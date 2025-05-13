// mobile/src/screens/AudioRecordingScreen.tsx
import { Delete, Mic, Pause, Play, Stop, Upload } from 'lucide-react-native';
import React, { useEffect, useState } from 'react';
import { Alert, PermissionsAndroid, Platform, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import AudioRecorderPlayer, {
  AudioEncoderAndroidType,
  AudioSourceAndroidType,
  AVEncoderAudioQualityIOSType,
  AVEncodingOption,
} from 'react-native-audio-recorder-player';

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
  recordingPath: string | null;
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
    recordingPath: null,
  });

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
        ]);

        return (
          grants[PermissionsAndroid.PERMISSIONS.RECORD_AUDIO] === PermissionsAndroid.RESULTS.GRANTED &&
          grants[PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE] === PermissionsAndroid.RESULTS.GRANTED
        );
      } catch (err) {
        console.warn(err);
        return false;
      }
    }
    return true;
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
      };

      const uri = await audioRecorderPlayer.startRecorder(undefined, audioSet);

      audioRecorderPlayer.addRecordBackListener(e => {
        setState(prevState => ({
          ...prevState,
          isRecording: true,
          recordSecs: e.currentPosition,
          recordTime: audioRecorderPlayer.mmssss(Math.floor(e.currentPosition)),
          recordingPath: uri,
        }));
      });
    } catch (err) {
      console.error('Failed to start recording', err);
      Alert.alert('Error', 'Failed to start recording');
    }
  };

  const stopRecording = async () => {
    try {
      const result = await audioRecorderPlayer.stopRecorder();
      audioRecorderPlayer.removeRecordBackListener();
      setState(prevState => ({
        ...prevState,
        isRecording: false,
      }));
      console.log('Recording stopped:', result);
    } catch (err) {
      console.error('Failed to stop recording', err);
    }
  };

  const startPlaying = async () => {
    if (!state.recordingPath) {
      Alert.alert('Error', 'No recording available');
      return;
    }

    try {
      await audioRecorderPlayer.startPlayer(state.recordingPath);

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

  const deleteRecording = () => {
    setState(prevState => ({
      ...prevState,
      recordingPath: null,
      recordSecs: 0,
      recordTime: '00:00:00',
      currentPositionSec: 0,
      currentDurationSec: 0,
      playTime: '00:00:00',
      duration: '00:00:00',
    }));
    Alert.alert('Recording Deleted', 'The recording has been deleted');
  };

  const uploadRecording = () => {
    // We'll implement this in the next sprint with MinIO connection
    Alert.alert('Coming Soon', 'Upload functionality will be added soon');
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Legal Recording</Text>

        <View style={styles.timerContainer}>
          <Text style={styles.timer}>
            {state.isRecording ? state.recordTime : state.recordingPath ? state.duration : '00:00:00'}
          </Text>
          <Text style={styles.status}>
            {state.isRecording ? 'Recording...' : state.isPlaying ? 'Playing...' : 'Ready'}
          </Text>
        </View>

        <View style={styles.controlsContainer}>
          {!state.isRecording && !state.recordingPath && (
            <TouchableOpacity style={styles.recordButton} onPress={startRecording}>
              <Mic size={32} color='#FFFFFF' />
            </TouchableOpacity>
          )}

          {state.isRecording && (
            <TouchableOpacity style={[styles.recordButton, styles.stopButton]} onPress={stopRecording}>
              <Stop size={32} color='#FFFFFF' />
            </TouchableOpacity>
          )}

          {!state.isRecording && state.recordingPath && !state.isPlaying && (
            <TouchableOpacity style={[styles.controlButton, styles.playButton]} onPress={startPlaying}>
              <Play size={24} color='#FFFFFF' />
            </TouchableOpacity>
          )}

          {!state.isRecording && state.recordingPath && state.isPlaying && (
            <TouchableOpacity style={[styles.controlButton, styles.pauseButton]} onPress={stopPlaying}>
              <Pause size={24} color='#FFFFFF' />
            </TouchableOpacity>
          )}

          {!state.isRecording && state.recordingPath && (
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

        {state.recordingPath && (
          <View style={styles.infoContainer}>
            <Text style={styles.infoText}>Recording saved to device storage</Text>
            <Text style={styles.pathText} numberOfLines={1} ellipsizeMode='middle'>
              {state.recordingPath}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.helpContainer}>
        <Text style={styles.helpTitle}>Recording Guidelines</Text>
        <Text style={styles.helpText}>• Ensure a quiet environment for optimal audio quality</Text>
        <Text style={styles.helpText}>• Place the device close to the speaker</Text>
        <Text style={styles.helpText}>• State the matter reference at the beginning</Text>
        <Text style={styles.helpText}>• Identify all speakers before they begin speaking</Text>
      </View>
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
});
