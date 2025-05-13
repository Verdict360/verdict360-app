// mobile/src/services/RecordingSyncService.ts
import { secureStorage, RecordingMetadata } from './SecureStorageService';
import { audioCompression, CompressionQuality } from './AudioCompressionService';
import { networkService } from './NetworkService';
import { MMKV } from 'react-native-mmkv';
import BackgroundFetch from 'react-native-background-fetch';
import { Platform, AppState, AppStateStatus } from 'react-native';

// Storage for sync queue
const syncStorage = new MMKV();

export interface SyncTask {
  id: string;
  recordingId: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  attemptCount: number;
  lastAttempt: number | null;
  error?: string;
}

export type SyncEventListener = (event: 'sync-started' | 'sync-completed' | 'sync-failed' | 'task-updated') => void;

class RecordingSyncService {
  private syncQueue: SyncTask[] = [];
  private isSyncing: boolean = false;
  private networkUnsubscribe: (() => void) | null = null;
  private eventListeners: Set<SyncEventListener> = new Set();
  private appStateSubscription: any = null;
  
  constructor() {
    // Load sync queue from storage
    this.loadSyncQueue();
    
    // Initialize background sync
    this.initBackgroundSync();
    
    // Subscribe to network changes
    this.subscribeToNetworkChanges();
    
    // Subscribe to app state changes
    this.subscribeToAppState();
  }
  
  private loadSyncQueue() {
    const queueData = syncStorage.getString('sync_queue');
    if (queueData) {
      this.syncQueue = JSON.parse(queueData);
    }
  }
  
  private saveSyncQueue() {
    syncStorage.set('sync_queue', JSON.stringify(this.syncQueue));
  }
  
  private initBackgroundSync() {
    // Configure background fetch
    BackgroundFetch.configure(
      {
        minimumFetchInterval: 15, // Fetch at least every 15 minutes
        stopOnTerminate: false,    // Continue after app is terminated
        startOnBoot: true,         // Restart sync when device reboots
        enableHeadless: true,      // Allow background operation
        requiredNetworkType: BackgroundFetch.NETWORK_TYPE_ANY, // Sync on any network
      },
      async (taskId) => {
        console.log('[BackgroundFetch] Task:', taskId);
        
        // Perform sync if we have network
        if (networkService.getIsConnected()) {
          await this.syncAll();
        }
        
        // Required: Signal completion of the task
        BackgroundFetch.finish(taskId);
      },
      (error) => {
        console.error('[BackgroundFetch] Failed to configure:', error);
      }
    );
  }
  
  private subscribeToNetworkChanges() {
    // Clean up any existing subscription
    if (this.networkUnsubscribe) {
      this.networkUnsubscribe();
    }
    
    // Subscribe to network changes
    this.networkUnsubscribe = networkService.addConnectivityChangeListener(
      (isConnected) => {
        if (isConnected) {
          // Network is back - attempt to sync
          this.syncAll();
        }
      }
    );
  }
  
  private subscribeToAppState() {
    // Handle app coming to foreground
    this.appStateSubscription = AppState.addEventListener(
      'change',
      (nextAppState: AppStateStatus) => {
        if (nextAppState === 'active') {
          // App has come to the foreground
          if (networkService.getIsConnected()) {
            this.syncAll();
          }
        }
      }
    );
  }
  
  /**
   * Add a recording to the sync queue
   */
  public addToSyncQueue(recordingId: string): string {
    // Check if recording exists
    const metadata = secureStorage.getMetadata(recordingId);
    if (!metadata) {
      throw new Error('Recording not found');
    }
    
    // Create sync task
    const syncTask: SyncTask = {
      id: `sync_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`,
      recordingId,
      status: 'pending',
      attemptCount: 0,
      lastAttempt: null,
    };
    
    // Add to queue
    this.syncQueue.push(syncTask);
    this.saveSyncQueue();
    
    // Update recording metadata
    const updatedMetadata: RecordingMetadata = {
      ...metadata,
      uploadStatus: 'pending',
    };
    secureStorage.updateMetadata(updatedMetadata);
    
    // Start sync if we're connected
    if (networkService.getIsConnected()) {
      this.syncAll();
    }
    
    return syncTask.id;
  }
  
  /**
   * Attempt to sync all pending recordings
   */
  public async syncAll(): Promise<void> {
    // Skip if already syncing
    if (this.isSyncing) return;
    
    // Skip if no connectivity
    if (!networkService.getIsConnected()) return;
    
    // Skip if no pending tasks
    const pendingTasks = this.syncQueue.filter(task => task.status === 'pending');
    if (pendingTasks.length === 0) return;
    
    this.isSyncing = true;
    this.notifyListeners('sync-started');
    
    try {
      // Process each pending task
      for (const task of pendingTasks) {
        await this.processTask(task);
      }
      
      this.notifyListeners('sync-completed');
    } catch (error) {
      console.error('Sync failed:', error);
      this.notifyListeners('sync-failed');
    } finally {
      this.isSyncing = false;
    }
  }
  
  /**
   * Process a single sync task
   */
  private async processTask(task: SyncTask): Promise<void> {
    // Skip if not pending
    if (task.status !== 'pending') return;
    
    // Update task status
    this.updateTaskStatus(task.id, 'in_progress');
    
    try {
      // Get recording metadata
      const metadata = secureStorage.getMetadata(task.recordingId);
      if (!metadata) {
        // Recording no longer exists
        this.updateTaskStatus(task.id, 'failed', 'Recording not found');
        return;
      }
      
      // Compress the recording (optimized for voice by default)
      const result = await audioCompression.prepareForUpload(
        task.recordingId,
        CompressionQuality.VOICE
      );
      
      // In a real implementation, we would upload to the server here
      // For now, we'll simulate a successful upload
      const simulatedUpload = await this.simulateUpload(result.fileContent);
      
      if (simulatedUpload.success) {
        // Update recording metadata
        const updatedMetadata: RecordingMetadata = {
          ...metadata,
          uploadStatus: 'uploaded',
          remotePath: simulatedUpload.remotePath
        };
        secureStorage.updateMetadata(updatedMetadata);
        
        // Mark task as completed
        this.updateTaskStatus(task.id, 'completed');
      } else {
        throw new Error(simulatedUpload.error);
      }
    } catch (error) {
      // Update attempt count
      task.attemptCount += 1;
      task.lastAttempt = Date.now();
      
      // If we've tried too many times, mark as failed
      if (task.attemptCount >= 3) {
        this.updateTaskStatus(task.id, 'failed', error.message);
      } else {
        // Otherwise, reset to pending for retry
        this.updateTaskStatus(task.id, 'pending', error.message);
      }
    }
  }
  
  /**
   * Update task status and save to storage
   */
  private updateTaskStatus(taskId: string, status: SyncTask['status'], error?: string) {
    const taskIndex = this.syncQueue.findIndex(t => t.id === taskId);
    if (taskIndex >= 0) {
      this.syncQueue[taskIndex] = {
        ...this.syncQueue[taskIndex],
        status,
        lastAttempt: Date.now(),
        error
      };
      
      this.saveSyncQueue();
      this.notifyListeners('task-updated');
    }
  }
  
  /**
   * Simulate uploading to the server
   * In a real implementation, this would make an API request
   */
  private async simulateUpload(fileContent: string): Promise<{
    success: boolean;
    remotePath?: string;
    error?: string;
  }> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 90% chance of success
    const success = Math.random() > 0.1;
    
    if (success) {
      return {
        success: true,
        remotePath: `recordings/${Date.now()}.aac`
      };
    } else {
      return {
        success: false,
        error: 'Simulated upload failure'
      };
    }
  }
  
  /**
   * Get all sync tasks
   */
  public getSyncTasks(): SyncTask[] {
    return [...this.syncQueue];
  }
  
  /**
   * Get pending sync tasks
   */
  public getPendingSyncTasks(): SyncTask[] {
    return this.syncQueue.filter(task => task.status === 'pending');
  }
  
  /**
   * Remove a completed task from the queue
   */
  public removeTask(taskId: string): boolean {
    const taskIndex = this.syncQueue.findIndex(t => t.id === taskId);
    if (taskIndex >= 0 && this.syncQueue[taskIndex].status === 'completed') {
      this.syncQueue.splice(taskIndex, 1);
      this.saveSyncQueue();
      return true;
    }
    return false;
  }
  
  /**
   * Retry a failed task
   */
  public retryTask(taskId: string): boolean {
    const taskIndex = this.syncQueue.findIndex(t => t.id === taskId);
    if (taskIndex >= 0 && this.syncQueue[taskIndex].status === 'failed') {
      this.syncQueue[taskIndex] = {
        ...this.syncQueue[taskIndex],
        status: 'pending',
        error: undefined
      };
      this.saveSyncQueue();
      
      // Attempt to sync if we're connected
      if (networkService.getIsConnected()) {
        this.syncAll();
      }
      
      return true;
    }
    return false;
  }
  
  /**
   * Register event listener
   */
  public addEventListener(listener: SyncEventListener): () => void {
    this.eventListeners.add(listener);
    return () => {
      this.eventListeners.delete(listener);
    };
  }
  
  /**
   * Notify all listeners of an event
   */
  private notifyListeners(event: Parameters<SyncEventListener>[0]) {
    this.eventListeners.forEach(listener => listener(event));
  }
  
  /**
   * Clean up resources
   */
  public cleanup() {
    if (this.networkUnsubscribe) {
      this.networkUnsubscribe();
      this.networkUnsubscribe = null;
    }
    
    if (this.appStateSubscription) {
      this.appStateSubscription.remove();
      this.appStateSubscription = null;
    }
    
    // Stop background fetch
    BackgroundFetch.stop();
    
    this.eventListeners.clear();
  }
}

// Export singleton instance
export const recordingSync = new RecordingSyncService();
