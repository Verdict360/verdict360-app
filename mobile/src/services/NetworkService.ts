// mobile/src/services/NetworkService.ts
import NetInfo, { NetInfoState, NetInfoSubscription } from '@react-native-community/netinfo';

type ConnectivityChangeCallback = (isConnected: boolean) => void;

class NetworkService {
  private isConnected: boolean = false;
  private listeners: Set<ConnectivityChangeCallback> = new Set();
  private unsubscribe: NetInfoSubscription | null = null;
  
  constructor() {
    this.initialize();
  }
  
  private initialize() {
    // Get initial network state
    NetInfo.fetch().then(state => {
      this.isConnected = state.isConnected ?? false;
    });
    
    // Subscribe to network changes
    this.unsubscribe = NetInfo.addEventListener(this.handleConnectivityChange);
  }
  
  private handleConnectivityChange = (state: NetInfoState) => {
    const newConnectedState = state.isConnected ?? false;
    
    // Only notify if state has changed
    if (this.isConnected !== newConnectedState) {
      this.isConnected = newConnectedState;
      
      // Notify all listeners
      this.listeners.forEach(listener => listener(this.isConnected));
    }
  };
  
  /**
   * Check if device is currently connected to the internet
   */
  public getIsConnected(): boolean {
    return this.isConnected;
  }
  
  /**
   * Add a listener for connectivity changes
   */
  public addConnectivityChangeListener(callback: ConnectivityChangeCallback): () => void {
    this.listeners.add(callback);
    
    // Return a function to remove this listener
    return () => {
      this.listeners.delete(callback);
    };
  }
  
  /**
   * Clean up and remove listener
   */
  public cleanup() {
    if (this.unsubscribe) {
      this.unsubscribe();
      this.unsubscribe = null;
    }
    this.listeners.clear();
  }
}

export const networkService = new NetworkService();
