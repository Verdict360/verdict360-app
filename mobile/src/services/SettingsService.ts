import AsyncStorage from '@react-native-async-storage/async-storage';
import { CompressionQuality } from './AudioCompressionService';

// Settings keys
const RECORDING_QUALITY_KEY = 'recording_quality';
const AUTO_UPLOAD_KEY = 'auto_upload';
const DEFAULT_MATTER_ID_KEY = 'default_matter_id';
const DARK_MODE_KEY = 'dark_mode';

// Default settings
const DEFAULT_SETTINGS = {
  recordingQuality: CompressionQuality.VOICE,
  autoUpload: true,
  defaultMatterId: null,
  darkMode: false,
};

class SettingsService {
  private settings: {
    recordingQuality: CompressionQuality;
    autoUpload: boolean;
    defaultMatterId: string | null;
    darkMode: boolean;
  };

  private listeners: Set<() => void> = new Set();

  constructor() {
    this.settings = { ...DEFAULT_SETTINGS };
    this.loadSettings();
  }

  private async loadSettings() {
    try {
      // Load recording quality
      const qualityValue = await AsyncStorage.getItem(RECORDING_QUALITY_KEY);
      if (qualityValue) {
        this.settings.recordingQuality = qualityValue as CompressionQuality;
      }

      // Load auto upload setting
      const autoUploadValue = await AsyncStorage.getItem(AUTO_UPLOAD_KEY);
      if (autoUploadValue !== null) {
        this.settings.autoUpload = autoUploadValue === 'true';
      }

      // Load default matter ID
      const defaultMatterId = await AsyncStorage.getItem(DEFAULT_MATTER_ID_KEY);
      this.settings.defaultMatterId = defaultMatterId;

      // Load dark mode setting
      const darkModeValue = await AsyncStorage.getItem(DARK_MODE_KEY);
      if (darkModeValue !== null) {
        this.settings.darkMode = darkModeValue === 'true';
      }

      this.notifyListeners();
    } catch (error) {
      console.error('Failed to load settings', error);
    }
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener());
  }

  public addSettingsChangeListener(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  public async setRecordingQuality(quality: CompressionQuality) {
    this.settings.recordingQuality = quality;
    await AsyncStorage.setItem(RECORDING_QUALITY_KEY, quality);
    this.notifyListeners();
  }

  public getRecordingQuality(): CompressionQuality {
    return this.settings.recordingQuality;
  }

  public async setAutoUpload(enabled: boolean) {
    this.settings.autoUpload = enabled;
    await AsyncStorage.setItem(AUTO_UPLOAD_KEY, String(enabled));
    this.notifyListeners();
  }

  public getAutoUpload(): boolean {
    return this.settings.autoUpload;
  }

  public async setDefaultMatterId(matterId: string | null) {
    this.settings.defaultMatterId = matterId;
    if (matterId) {
      await AsyncStorage.setItem(DEFAULT_MATTER_ID_KEY, matterId);
    } else {
      await AsyncStorage.removeItem(DEFAULT_MATTER_ID_KEY);
    }
    this.notifyListeners();
  }

  public getDefaultMatterId(): string | null {
    return this.settings.defaultMatterId;
  }

  public async setDarkMode(enabled: boolean) {
    this.settings.darkMode = enabled;
    await AsyncStorage.setItem(DARK_MODE_KEY, String(enabled));
    this.notifyListeners();
  }

  public getDarkMode(): boolean {
    return this.settings.darkMode;
  }

  public async resetToDefaults() {
    this.settings = { ...DEFAULT_SETTINGS };
    await AsyncStorage.multiRemove([
      RECORDING_QUALITY_KEY,
      AUTO_UPLOAD_KEY,
      DEFAULT_MATTER_ID_KEY,
      DARK_MODE_KEY,
    ]);
    this.notifyListeners();
  }
}

// Export singleton instance
export const settingsService = new SettingsService();
