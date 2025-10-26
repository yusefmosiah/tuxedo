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

export interface StreamMessage {
  type: 'thinking' | 'llm_response' | 'tool_call_start' | 'tool_result' | 'tool_error' | 'final_response' | 'error' | 'live_summary_start' | 'live_summary_update' | 'live_summary_complete';
  content: string;
  tool_name?: string;
  tool_args?: any;
  iteration?: number;
  id?: string;
  isLive?: boolean;
  isExpanded?: boolean;
  fullContent?: StreamMessage[];
}

export interface HealthResponse {
  status: string;
  stellar_tools_ready: boolean;
  openai_configured: boolean;
  live_summary_ready: boolean;
  defindex_tools_ready: boolean;
}

export interface LiveSummaryChatRequest {
  message: string;
  history: ChatMessage[];
  wallet_address?: string | null;
  enable_summary?: boolean;
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
      console.log('🔍 Sending chat request:', {
        message: request.message,
        hasWalletAddress: !!request.wallet_address,
        walletAddress: request.wallet_address
      });
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
   * Send a streaming chat message using Server-Sent Events
   */
  sendMessageStream(
    request: ChatRequest,
    onMessage: (message: StreamMessage) => void,
    onError: (error: Error) => void,
    onClose: () => void
  ): () => void {
    console.log('🔍 Starting streaming chat request:', {
      message: request.message,
      hasWalletAddress: !!request.wallet_address,
      walletAddress: request.wallet_address
    });

    // Use fetch with streaming response
    const controller = new AbortController();

    fetch(`${API_BASE_URL}/chat-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(request),
      signal: controller.signal
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      function processText(text: string) {
        buffer += text;
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data.trim()) {
              try {
                const message: StreamMessage = JSON.parse(data);
                onMessage(message);
              } catch (e) {
                console.error('Error parsing SSE message:', e, 'Raw data:', data);
              }
            }
          }
        }
      }

      function read() {
        if (!reader) return;
        reader.read().then(({ done, value }) => {
          if (done) {
            processText(''); // Process any remaining data
            onClose();
            return;
          }

          const text = decoder.decode(value, { stream: true });
          processText(text);
          read();
        }).catch(error => {
          if (error.name !== 'AbortError') {
            console.error('Stream read error:', error);
            onError(error);
          }
        });
      }

      read();
    })
    .catch(error => {
      console.error('Stream error:', error);
      onError(error);
    });

    // Return cleanup function
    return () => {
      controller.abort();
    };
  },

  /**
   * Send a streaming chat message with live summaries using Server-Sent Events
   */
  sendMessageWithLiveSummary(
    request: LiveSummaryChatRequest,
    onMessage: (message: StreamMessage) => void,
    onError: (error: Error) => void,
    onClose: () => void
  ): () => void {
    console.log('🔍 Starting live summary streaming chat request:', {
      message: request.message,
      hasWalletAddress: !!request.wallet_address,
      walletAddress: request.wallet_address,
      enableSummary: request.enable_summary
    });

    // Use fetch with streaming response
    const controller = new AbortController();

    fetch(`${API_BASE_URL}/chat-live-summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(request),
      signal: controller.signal
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      function processText(text: string) {
        buffer += text;
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data.trim()) {
              try {
                const message: StreamMessage = JSON.parse(data);
                onMessage(message);
              } catch (e) {
                console.error('Error parsing SSE message:', e, 'Raw data:', data);
              }
            }
          }
        }
      }

      function read() {
        if (!reader) return;
        reader.read().then(({ done, value }) => {
          if (done) {
            processText(''); // Process any remaining data
            onClose();
            return;
          }

          const text = decoder.decode(value, { stream: true });
          processText(text);
          read();
        }).catch(error => {
          if (error.name !== 'AbortError') {
            console.error('Stream read error:', error);
            onError(error);
          }
        });
      }

      read();
    })
    .catch(error => {
      console.error('Live summary stream error:', error);
      onError(error);
    });

    // Return cleanup function
    return () => {
      controller.abort();
    };
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
        openai_configured: false,
        live_summary_ready: false,
        defindex_tools_ready: false
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