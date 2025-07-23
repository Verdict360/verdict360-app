import { env } from '$env/dynamic/public';

const API_BASE_URL = env.VITE_API_URL || 'http://localhost:8000';

export class APIService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}/api/v1${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // Legal chatbot endpoints
  async sendChatMessage(message: string, sessionId?: string) {
    return this.request('/chat/', {
      method: 'POST',
      body: JSON.stringify({ 
        message: message.trim(),
        session_id: sessionId,
        legal_context: 'south_african_law',
        include_sources: true
      })
    });
  }

  // Consultation booking
  async bookConsultation(consultationData: any) {
    return this.request('/consultations/', {
      method: 'POST',
      body: JSON.stringify(consultationData)
    });
  }

  // Voice call initiation
  async initiateVoiceCall(phoneNumber: string) {
    return this.request('/voice/initiate-call', {
      method: 'POST',
      body: JSON.stringify({ phone_number: phoneNumber })
    });
  }

  // Legal document search
  async searchDocuments(query: string) {
    return this.request('/search/', {
      method: 'POST',
      body: JSON.stringify({ 
        query: query.trim(),
        jurisdiction: 'south_africa'
      })
    });
  }

  // Analytics endpoints
  async getAnalytics(firmId?: string) {
    const endpoint = firmId ? `/analytics/?firm_id=${firmId}` : '/analytics/';
    return this.request(endpoint);
  }

  // Calendar integration
  async getAvailableSlots(date: string) {
    return this.request(`/calendar/available-slots?date=${date}`);
  }

  // Health check
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const api = new APIService();