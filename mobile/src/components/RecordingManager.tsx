import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import { Mic, Upload, Play, Trash2, AlertCircle } from 'lucide-react-native';
import { RecordingMetadata, secureStorage } from '../services/SecureStorageService';
import { recordingSync, SyncTask } from '../services/RecordingSyncService';

type RecordingStatus = 'pending' | 'uploading' | 'uploaded' | 'failed' | 'none';

interface RecordingItemProps {
  recording: RecordingMetadata;
  syncTask?: SyncTask;
  onPlay: (recordingId: string) => void;
  onDelete: (recordingId: string) => void;
  onUpload: (recordingId: string) => void;
}

const RecordingItem: React.FC<RecordingItemProps> = ({ recording, syncTask, onPlay, onDelete, onUpload }) => {
  const getStatusColor = () => {
    if (syncTask) {
      switch (syncTask.status) {
        case 'completed':
          return '#10B981'; // green
        case 'in_progress':
          return '#F59E0B'; // amber
        case 'failed':
          return '#EF4444'; // red
        default:
          return '#6B7280'; // gray
      }
    }

    if (recording.uploadStatus === 'uploaded') {
      return '#10B981'; // green
    }

    return '#6B7280'; // gray
  };

  const getStatusText = () => {
    if (syncTask) {
      switch (syncTask.status) {
        case 'completed':
          return 'Uploaded';
        case 'in_progress':
          return 'Uploading...';
        case 'failed':
          return 'Upload Failed';
        default:
          return 'Pending Upload';
      }
    }

    if (recording.uploadStatus === 'uploaded') {
      return 'Uploaded';
    }

    return 'Not Uploaded';
  };

  const formattedDate = new Date(recording.createdAt).toLocaleDateString();
  const formattedTime = new Date(recording.createdAt).toLocaleTimeString();
  const durationMinutes = Math.floor(recording.duration / 60);
  const durationSeconds = Math.floor(recording.duration % 60);

  return (
    <View style={styles.recordingItem}>
      <View style={styles.recordingHeader}>
        <View style={styles.titleContainer}>
          <Text style={styles.recordingTitle}>{recording.title}</Text>
          <View style={[styles.statusDot, { backgroundColor: getStatusColor() }]} />
        </View>
        <Text style={styles.recordingDate}>
          {formattedDate} at {formattedTime}
        </Text>
      </View>
      
      <View style={styles.recordingDetails}>
        <Text style={styles.recordingDetail}>
          {durationMinutes}:{durationSeconds.toString().padStart(2, '0')} min
        </Text>
        <Text style={styles.recordingDetail}>{(recording.size / (1024 * 1024)).toFixed(2)} MB</Text>
        <Text style={styles.recordingDetail}>{getStatusText()}</Text>
      </View>
      
      {recording.description && (
        <Text style={styles.recordingDescription}>{recording.description}</Text>
      )}
      
      <View style={styles.actionButtons}>
        <TouchableOpacity style={[styles.actionButton, styles.playButton]} onPress={() => onPlay(recording.id)}>
          <Play width={18} height={18} color="#FFFFFF" />
        </TouchableOpacity>
        
        {(!recording.uploadStatus || recording.uploadStatus !== 'uploaded') && (
          <TouchableOpacity style={[styles.actionButton, styles.uploadButton]} onPress={() => onUpload(recording.id)}>
            <Upload width={18} height={18} color="#FFFFFF" />
          </TouchableOpacity>
        )}
        
        <TouchableOpacity style={[styles.actionButton, styles.deleteButton]} onPress={() => onDelete(recording.id)}>
          <Trash2 width={18} height={18} color="#FFFFFF" />
        </TouchableOpacity>
      </View>
    </View>
  );
};

interface RecordingManagerProps {
  onPlayRecording: (recordingId: string) => void;
  onNewRecording: () => void;
}

export const RecordingManager: React.FC<RecordingManagerProps> = ({ onPlayRecording, onNewRecording }) => {
  const [recordings, setRecordings] = useState<RecordingMetadata[]>([]);
  const [syncTasks, setSyncTasks] = useState<SyncTask[]>([]);
  
  useEffect(() => {
    // Load recordings
    loadRecordings();
    
    // Set up sync task listener
    const unsubscribe = recordingSync.addEventListener(() => {
      setSyncTasks(recordingSync.getSyncTasks());
    });
    
    return unsubscribe;
  }, []);
  
  const loadRecordings = () => {
    const recordingList = secureStorage.getAllRecordings();
    setRecordings(recordingList.sort((a, b) => b.createdAt - a.createdAt));
    setSyncTasks(recordingSync.getSyncTasks());
  };
  
  const handleDeleteRecording = (recordingId: string) => {
    // Show confirmation dialog
    Alert.alert(
      'Delete Recording',
      'Are you sure you want to delete this recording?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            await secureStorage.deleteRecording(recordingId);
            loadRecordings();
          },
        },
      ]
    );
  };
  
  const handleUploadRecording = (recordingId: string) => {
    recordingSync.addToSyncQueue(recordingId);
    loadRecordings();
  };
  
  const getSyncTaskForRecording = (recordingId: string): SyncTask | undefined => {
    return syncTasks.find(task => task.recordingId === recordingId);
  };
  
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Your Recordings</Text>
        <TouchableOpacity style={styles.newRecordingButton} onPress={onNewRecording}>
          <Mic width={18} height={18} color="#FFFFFF" />
          <Text style={styles.newRecordingText}>New Recording</Text>
        </TouchableOpacity>
      </View>
      
      {recordings.length === 0 ? (
        <View style={styles.emptyState}>
          <Mic width={48} height={48} color="#9CA3AF" />
          <Text style={styles.emptyStateText}>No recordings yet</Text>
          <Text style={styles.emptyStateSubtext}>Tap the "New Recording" button to get started</Text>
        </View>
      ) : (
        <FlatList
          data={recordings}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <RecordingItem
              recording={item}
              syncTask={getSyncTaskForRecording(item.id)}
              onPlay={onPlayRecording}
              onDelete={handleDeleteRecording}
              onUpload={handleUploadRecording}
            />
          )}
          contentContainerStyle={styles.list}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  newRecordingButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4F46E5',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
  },
  newRecordingText: {
    color: '#FFFFFF',
    fontWeight: '500',
    marginLeft: 6,
  },
  list: {
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
  recordingItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    marginTop: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  recordingHeader: {
    marginBottom: 8,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  recordingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  recordingDate: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  recordingDetails: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  recordingDetail: {
    fontSize: 13,
    color: '#4B5563',
    marginRight: 12,
  },
  recordingDescription: {
    fontSize: 14,
    color: '#4B5563',
    marginBottom: 12,
  },
  actionButtons: {
    flexDirection: 'row',
    marginTop: 8,
  },
  actionButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  playButton: {
    backgroundColor: '#4F46E5',
  },
  uploadButton: {
    backgroundColor: '#10B981',
  },
  deleteButton: {
    backgroundColor: '#EF4444',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
    marginTop: 16,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
  },
});
