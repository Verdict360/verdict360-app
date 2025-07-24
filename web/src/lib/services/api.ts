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

  // Voice call endpoints - matches backend
  async initiateVoiceCall(callData: {
    consultation_id?: string;
    client_phone: string;
    legal_context: any;
    call_type: string;
  }) {
    return this.request('/voice/initiate-call', {
      method: 'POST',
      body: JSON.stringify(callData)
    });
  }

  async getVoiceCall(callId: string) {
    return this.request(`/voice/calls/${callId}`);
  }

  async getVoiceTranscript(callId: string) {
    return this.request(`/voice/transcripts/${callId}`);
  }

  async endVoiceCall(callId: string) {
    return this.request('/voice/end-call', {
      method: 'POST',
      body: JSON.stringify({ call_id: callId })
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

  // Dashboard analytics - matches backend endpoints
  async getDashboardSummary(period: string = '30d') {
    return this.request(`/analytics/dashboard/summary?period=${period}`);
  }

  async getTrendingKeywords(limit: number = 10) {
    return this.request(`/analytics/keywords/trending?limit=${limit}`);
  }

  async getPerformanceMetrics(period: string = '30d') {
    return this.request(`/analytics/performance/metrics?period=${period}`);
  }

  async getLegalAreaBreakdown(period: string = '30d') {
    return this.request(`/analytics/legal-areas/breakdown?period=${period}`);
  }

  async getConversationAnalytics(limit: number = 50) {
    return this.request(`/analytics/conversations/recent?limit=${limit}`);
  }

  async getConversionFunnel(period: string = '30d') {
    return this.request(`/analytics/conversion/funnel?period=${period}`);
  }

  // Calendar integration - matches backend endpoints
  async checkAvailability(availabilityData: {
    legal_area: string;
    preferred_date: string;
    preferred_time?: string;
    duration_minutes?: number;
    urgency_level?: string;
  }) {
    return this.request('/calendar/availability/check', {
      method: 'POST',
      body: JSON.stringify(availabilityData)
    });
  }

  async bookConsultationSlot(bookingData: {
    client_name: string;
    client_email: string;
    client_phone?: string;
    legal_area: string;
    matter_description: string;
    preferred_date: string;
    preferred_time: string;
    duration_minutes?: number;
    urgency_level?: string;
  }) {
    return this.request('/calendar/consultations/book', {
      method: 'POST',
      body: JSON.stringify(bookingData)
    });
  }

  async getDailySchedule(date: string, lawyerId?: string) {
    const endpoint = lawyerId 
      ? `/calendar/schedule/daily?date=${date}&lawyer_id=${lawyerId}`
      : `/calendar/schedule/daily?date=${date}`;
    return this.request(endpoint);
  }

  async getAvailableLawyers(legalArea: string) {
    return this.request(`/calendar/availability/lawyers?legal_area=${legalArea}`);
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