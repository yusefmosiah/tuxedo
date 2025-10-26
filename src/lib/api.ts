import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8002';

// API Interfaces
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
  wallet_address?: string | null;
}

export interface ChatResponse {
  response: string;
  success: boolean;
  error?: string | null;
}

export interface HealthResponse {
  status: string;
  stellar_tools_ready: boolean;
  openai_configured: boolean;
}

export interface StellarToolsStatus {
  available: boolean;
  tools_count: number;
  tools: string[];
  last_check: string;
}

// Create Axios instance with default configuration
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request/Response interceptors for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Methods
export const chatApi = {
  /**
   * Send a chat message to the AI assistant
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await api.post('/chat', request);
      return response.data;
    } catch (error: any) {
      console.error('Chat API Error:', error);

      // Extract error message from Axios error
      const errorMessage = error.response?.data?.detail ||
                         error.response?.data?.error ||
                         error.message ||
                         'Unknown error occurred';

      throw new Error(errorMessage);
    }
  },

  /**
   * Get backend health status
   */
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error: any) {
      console.error('Health Check Error:', error);

      // Return degraded status on error
      return {
        status: 'unhealthy',
        stellar_tools_ready: false,
        openai_configured: false
      };
    }
  },

  /**
   * Get Stellar tools status and available functions
   */
  async getStellarToolsStatus(): Promise<StellarToolsStatus> {
    try {
      const response = await api.get('/stellar-tools/status');
      return response.data;
    } catch (error: any) {
      console.error('Stellar Tools Status Error:', error);

      // Return unavailable status on error
      return {
        available: false,
        tools_count: 0,
        tools: [],
        last_check: new Date().toISOString()
      };
    }
  },

  /**
   * Call a Stellar tool directly
   */
  async callStellarTool(toolName: string, args: any = {}): Promise<any> {
    try {
      const response = await api.post(`/stellar-tool/${toolName}`, args);
      return response.data;
    } catch (error: any) {
      console.error('Stellar Tool Call Error:', error);
      throw error;
    }
  }
};

// Utility functions
export const apiUtils = {
  /**
   * Check if the API is reachable
   */
  async isApiAvailable(): Promise<boolean> {
    try {
      await chatApi.healthCheck();
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Format error message for user display
   */
  formatError(error: Error): string {
    if (error.message.includes('Network Error')) {
      return 'Unable to connect to backend. Please check your connection and try again.';
    }

    if (error.message.includes('timeout')) {
      return 'Request timed out. The backend may be overloaded, please try again.';
    }

    return error.message || 'An unexpected error occurred. Please try again.';
  }
};

export default api;