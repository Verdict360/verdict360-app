import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Switch, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { Settings, HardDrive, Upload, Moon, RefreshCw, AlertCircle } from 'lucide-react-native';
import { CompressionQuality } from '../services/AudioCompressionService';
import { settingsService } from '../services/SettingsService';
import { useAuth } from './AuthProvider';

export const SettingsScreen: React.FC = () => {
  const { user, logout } = useAuth();
  
  const [recordingQuality, setRecordingQuality] = useState(settingsService.getRecordingQuality());
  const [autoUpload, setAutoUpload] = useState(settingsService.getAutoUpload());
  const [darkMode, setDarkMode] = useState(settingsService.getDarkMode());
  
  useEffect(() => {
    const unsubscribe = settingsService.addSettingsChangeListener(() => {
      setRecordingQuality(settingsService.getRecordingQuality());
      setAutoUpload(settingsService.getAutoUpload());
      setDarkMode(settingsService.getDarkMode());
    });
    
    return unsubscribe;
  }, []);
  
  const handleQualityChange = (quality: CompressionQuality) => {
    settingsService.setRecordingQuality(quality);
  };
  
  const handleAutoUploadChange = (value: boolean) => {
    settingsService.setAutoUpload(value);
  };
  
  const handleDarkModeChange = (value: boolean) => {
    settingsService.setDarkMode(value);
  };
  
  const handleResetSettings = () => {
    Alert.alert(
      'Reset Settings',
      'Are you sure you want to reset all settings to their default values?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Reset',
          onPress: () => {
            settingsService.resetToDefaults();
          },
        },
      ]
    );
  };
  
  const handleLogout = () => {
    Alert.alert(
      'Log Out',
      'Are you sure you want to log out?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Log Out',
          onPress: () => {
            logout();
          },
        },
      ]
    );
  };
  
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Settings width={24} height={24} color="#4F46E5" />
        <Text style={styles.headerTitle}>App Settings</Text>
      </View>
      
      {user && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Account</Text>
          <View style={styles.userInfo}>
            <Text style={styles.userName}>{user.name || user.email || 'User'}</Text>
            <Text style={styles.userEmail}>{user.email || ''}</Text>
          </View>
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Text style={styles.logoutText}>Log Out</Text>
          </TouchableOpacity>
        </View>
      )}
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recording Quality</Text>
        <Text style={styles.sectionDescription}>
          Higher quality recordings use more storage space. Voice quality is optimized for speech.
        </Text>
        
        <View style={styles.qualityOptions}>
          <TouchableOpacity
            style={[
              styles.qualityOption,
              recordingQuality === CompressionQuality.HIGH && styles.qualityOptionSelected,
            ]}
            onPress={() => handleQualityChange(CompressionQuality.HIGH)}>
            <View style={styles.qualityHeader}>
              <HardDrive width={18} height={18} color="#4F46E5" />
              <Text style={styles.qualityTitle}>High</Text>
            </View>
            <Text style={styles.qualityDescription}>Better quality, larger files</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[
              styles.qualityOption,
              recordingQuality === CompressionQuality.MEDIUM && styles.qualityOptionSelected,
            ]}
            onPress={() => handleQualityChange(CompressionQuality.MEDIUM)}>
            <View style={styles.qualityHeader}>
              <HardDrive width={18} height={18} color="#4F46E5" />
              <Text style={styles.qualityTitle}>Medium</Text>
            </View>
            <Text style={styles.qualityDescription}>Balanced quality and size</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[
              styles.qualityOption,
              recordingQuality === CompressionQuality.VOICE && styles.qualityOptionSelected,
            ]}
            onPress={() => handleQualityChange(CompressionQuality.VOICE)}>
            <View style={styles.qualityHeader}>
              <HardDrive width={18} height={18} color="#4F46E5" />
              <Text style={styles.qualityTitle}>Voice</Text>
            </View>
            <Text style={styles.qualityDescription}>Optimized for speech, smallest files</Text>
          </TouchableOpacity>
        </View>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Upload Settings</Text>
        
        <View style={styles.settingRow}>
          <View style={styles.settingTextContainer}>
            <Text style={styles.settingLabel}>Auto-upload recordings</Text>
            <Text style={styles.settingDescription}>
              Automatically upload recordings when connected to Wi-Fi
            </Text>
          </View>
          <Switch
            value={autoUpload}
            onValueChange={handleAutoUploadChange}
            trackColor={{ false: '#D1D5DB', true: '#818CF8' }}
            thumbColor={autoUpload ? '#4F46E5' : '#F9FAFB'}
          />
        </View>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Display</Text>
        
        <View style={styles.settingRow}>
          <View style={styles.settingTextContainer}>
            <Text style={styles.settingLabel}>Dark Mode</Text>
            <Text style={styles.settingDescription}>
              Use dark color scheme (requires app restart)
            </Text>
          </View>
          <Switch
            value={darkMode}
            onValueChange={handleDarkModeChange}
            trackColor={{ false: '#D1D5DB', true: '#818CF8' }}
            thumbColor={darkMode ? '#4F46E5' : '#F9FAFB'}
          />
        </View>
      </View>
      
      <View style={styles.resetSection}>
        <TouchableOpacity style={styles.resetButton} onPress={handleResetSettings}>
          <RefreshCw width={18} height={18} color="#6B7280" />
          <Text style={styles.resetText}>Reset to Defaults</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.footer}>
        <Text style={styles.versionText}>Verdict360 v1.0.0</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    backgroundColor: '#FFFFFF',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginLeft: 8,
  },
  section: {
    marginTop: 16,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#E5E7EB',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  sectionDescription: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 16,
  },
  userInfo: {
    marginBottom: 16,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  userEmail: {
    fontSize: 14,
    color: '#6B7280',
  },
  logoutButton: {
    backgroundColor: '#EF4444',
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  logoutText: {
    color: '#FFFFFF',
    fontWeight: '500',
  },
  qualityOptions: {
    marginTop: 12,
  },
  qualityOption: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    backgroundColor: '#FFFFFF',
  },
  qualityOptionSelected: {
    borderColor: '#4F46E5',
    backgroundColor: 'rgba(79, 70, 229, 0.05)',
  },
  qualityHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  qualityTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#111827',
    marginLeft: 8,
  },
  qualityDescription: {
    fontSize: 13,
    color: '#6B7280',
    marginLeft: 26,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  settingTextContainer: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    fontSize: 15,
    fontWeight: '500',
    color: '#111827',
  },
  settingDescription: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 2,
  },
  resetSection: {
    padding: 16,
    alignItems: 'center',
  },
  resetButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 6,
    backgroundColor: '#FFFFFF',
  },
  resetText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 8,
  },
  footer: {
    padding: 24,
    alignItems: 'center',
  },
  versionText: {
    fontSize: 12,
    color: '#9CA3AF',
  },
});
