import { env } from '$env/dynamic/public';

export interface ChatMessage {
  id: string;
  content: string;
  type: 'user' | 'assistant';
  timestamp: Date;
  sources?: LegalSource[];
}

export interface LegalSource {
  id: string;
  title: string;
  citation: string;
  url?: string;
  excerpt: string;
}

export interface ChatResponse {
  response: string;
  sources?: LegalSource[];
  confidence?: number;
  legal_context?: string;
}

class ChatbotService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = env.VITE_API_URL || 'http://localhost:8000';
  }

  async sendMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message.trim(),
          session_id: sessionId || this.generateSessionId(),
          legal_context: 'south_african_law',
          include_sources: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();
      return this.processChatResponse(data);
    } catch (error) {
      console.error('Chatbot service error:', error);
      throw new Error('Failed to get legal assistance. Please try again.');
    }
  }

  async getLegalDocument(documentId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/documents/${documentId}`);
      return await response.json();
    } catch (error) {
      console.error('Legal document fetch error:', error);
      throw error;
    }
  }

  async searchLegalCases(query: string): Promise<LegalSource[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/search/cases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          jurisdiction: 'south_africa',
          limit: 10,
        }),
      });

      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error('Legal case search error:', error);
      return [];
    }
  }

  private processChatResponse(data: any): ChatResponse {
    return {
      response: data.response || data.message || 'I apologize, but I cannot process your request at this time.',
      sources: data.sources?.map((source: any) => ({
        id: source.id || '',
        title: source.title || source.name || 'Unknown Source',
        citation: source.citation || '',
        url: source.url,
        excerpt: source.excerpt || source.content || '',
      })) || [],
      confidence: data.confidence || 0,
      legal_context: data.legal_context || 'general',
    };
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substring(2)}`;
  }

  // Health check for the legal API
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const chatbotService = new ChatbotService();