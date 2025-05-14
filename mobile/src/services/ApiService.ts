import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { ENV } from '../utils/environment';
import { authService } from './AuthService';
import { networkService } from './NetworkService';

// Default API URL
const API_URL = ENV.API_URL;

class ApiService {
  private axiosInstance: AxiosInstance;
  private offlineQueue: Array<{
    config: AxiosRequestConfig;
    resolve: (value: any) => void;
    reject: (reason: any) => void;
  }> = [];

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_URL,
      timeout: 30000, // 30 second timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for authentication
    this.axiosInstance.interceptors.request.use(
      async (config) => {
        // Add auth token if available
        const token = authService.getAccessToken();
        if (token) {
          config.headers.Authorization = ;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        // Handle 401 Unauthorized errors
        if (error.response && error.response.status === 401) {
          try {
            // Try to refresh the token
            const refreshed = await authService.refreshAccessToken();
            if (refreshed) {
              // Retry the original request with new token
              const token = authService.getAccessToken();
              error.config.headers.Authorization = ;
              return this.axiosInstance.request(error.config);
            }
          } catch (refreshError) {
            console.error('Token refresh failed', refreshError);
          }
        }

        // Handle offline mode for specific requests
        if (error.message === 'Network Error' && error.config && this.isQueueableRequest(error.config)) {
          return new Promise((resolve, reject) => {
            // Add to offline queue
            this.offlineQueue.push({ config: error.config, resolve, reject });
          });
        }

        return Promise.reject(error);
      }
    );

    // Listen for network status changes
    networkService.addConnectivityChangeListener(this.handleNetworkChange);
  }

  private handleNetworkChange = (isConnected: boolean) => {
    if (isConnected && this.offlineQueue.length > 0) {
      this.processOfflineQueue();
    }
  };

  private async processOfflineQueue() {
    const queue = [...this.offlineQueue];
    this.offlineQueue = [];

    for (const item of queue) {
      try {
        const response = await this.axiosInstance.request(item.config);
        item.resolve(response);
      } catch (error) {
        item.reject(error);
      }
    }
  }

  private isQueueableRequest(config: AxiosRequestConfig): boolean {
    // Define which requests can be queued for offline use
    // Typically, POST/PUT/DELETE requests with idempotent behavior
    const queueableMethods = ['POST', 'PUT'];
    const queueablePaths = ['/recordings', '/documents'];

    return (
      config.method &&
      queueableMethods.includes(config.method.toUpperCase()) &&
      config.url &&
      queueablePaths.some(path => config.url?.includes(path))
    );
  }

  // Upload a recording to the server
  public async uploadRecording(recordingData: any, fileContent: string) {
    return this.axiosInstance.post('/recordings', {
      ...recordingData,
      fileContent,
    });
  }

  // Get transcription status
  public async getTranscriptionStatus(recordingId: string) {
    return this.axiosInstance.get();
  }

  // Get matter list
  public async getMatters() {
    return this.axiosInstance.get('/matters');
  }

  // Basic GET request
  public async get(endpoint: string, params?: any) {
    return this.axiosInstance.get(endpoint, { params });
  }

  // Basic POST request
  public async post(endpoint: string, data: any) {
    return this.axiosInstance.post(endpoint, data);
  }

  // Basic PUT request
  public async put(endpoint: string, data: any) {
    return this.axiosInstance.put(endpoint, data);
  }

  // Basic DELETE request
  public async delete(endpoint: string) {
    return this.axiosInstance.delete(endpoint);
  }
}

// Export singleton instance
export const apiService = new ApiService();
