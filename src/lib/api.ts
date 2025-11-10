import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API Configuration - Environment-based with fallbacks
export const API_BASE_URL = import.meta.env.VITE_API_URL ||
                            import.meta.env.PUBLIC_API_URL ||
                            (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tuxedo-backend.onrender.com');

// API Interfaces
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
  wallet_address?: string | null;
  wallet_mode?: string | null;
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
  summary?: string;
}

export interface HealthResponse {
  status: string;
  stellar_tools_ready: boolean;
  openai_configured: boolean;
  live_summary_ready: boolean;
  defindex_tools_ready: boolean;
  database_ready: boolean;
}

export interface LiveSummaryChatRequest {
  message: string;
  history: ChatMessage[];
  wallet_address?: string | null;
  wallet_mode?: string | null;
  enable_summary?: boolean;
}

export interface StellarToolsStatus {
  available: boolean;
  tools_count: number;
  tools: string[];
  last_check: string;
}

// Thread Management Interfaces
export interface Thread {
  id: string;
  title: string;
  wallet_address?: string | null;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

export interface ThreadCreate {
  title: string;
  wallet_address?: string | null;
}

export interface ThreadUpdate {
  title?: string;
}

export interface MessageWithMetadata {
  id: string;
  thread_id: string;
  role: string;
  content: string;
  metadata?: {
    type?: string;
    toolName?: string;
    iteration?: number;
    isStreaming?: boolean;
    summary?: string;
  } | null;
  created_at: string;
}

// Transaction API Interfaces
export interface TransactionRequest {
  action: string; // 'deposit', 'mining', 'claim'
  user_address: string;
  amount?: number;
  vault_address?: string;
}

export interface TransactionResponse {
  success: boolean;
  transaction?: {
    xdr: string;
    network: string;
    description: string;
    amount: number;
    tux_rewards: number;
    estimated_shares: string;
    note: string;
    mining_duration?: number;
    vault_address?: string;
  };
  error?: string;
  message?: string;
}

export interface MiningStatus {
  user_address: string;
  total_tux_mined: number;
  active_mining_sessions: number;
  last_mining?: string;
  mining_power: number;
  next_reward_estimate: number;
  error?: string;
}

// Create Axios instance with default configuration
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    // Add session token if available
    const sessionToken = localStorage.getItem('session_token');
    if (sessionToken) {
      config.headers.Authorization = `Bearer ${sessionToken}`;
    }
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptors for debugging

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

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    };

    // Add session token if available
    const sessionToken = localStorage.getItem('session_token');
    if (sessionToken) {
      headers.Authorization = `Bearer ${sessionToken}`;
    }

    fetch(`${API_BASE_URL}/chat-stream`, {
      method: 'POST',
      headers,
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

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    };

    // Add session token if available
    const sessionToken = localStorage.getItem('session_token');
    if (sessionToken) {
      headers.Authorization = `Bearer ${sessionToken}`;
    }

    fetch(`${API_BASE_URL}/chat-live-summary`, {
      method: 'POST',
      headers,
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
        defindex_tools_ready: false,
        database_ready: false
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

// Transaction API for automatic wallet triggering
export const transactionApi = {
  /**
   * Prepare a deposit transaction with tux mining
   */
  async prepareDepositTransaction(
    userAddress: string,
    amount: number,
    vaultAddress?: string
  ): Promise<TransactionResponse> {
    try {
      const response = await api.post('/prepare-transaction', {
        action: 'deposit',
        user_address: userAddress,
        amount: amount,
        vault_address: vaultAddress
      });
      return response.data;
    } catch (error: any) {
      console.error('Prepare Transaction Error:', error);
      throw error;
    }
  },

  /**
   * Get mining status for a user
   */
  async getMiningStatus(userAddress: string): Promise<MiningStatus> {
    try {
      const response = await api.get(`/mining-status/${userAddress}`);
      return response.data;
    } catch (error: any) {
      console.error('Get Mining Status Error:', error);
      throw error;
    }
  },

  /**
   * Simulate mining completion for demo purposes
   */
  async simulateMiningCompletion(
    userAddress: string,
    depositAmount: number
  ): Promise<any> {
    try {
      const response = await api.post('/simulate-mining-completion', {
        user_address: userAddress,
        deposit_amount: depositAmount
      });
      return response.data;
    } catch (error: any) {
      console.error('Simulate Mining Completion Error:', error);
      throw error;
    }
  }
};

// Thread Management API
export const threadsApi = {
  /**
   * Create a new chat thread
   */
  async createThread(threadData: ThreadCreate): Promise<Thread> {
    try {
      const response = await api.post('/threads', threadData);
      return response.data;
    } catch (error: any) {
      console.error('Create Thread Error:', error);
      throw error;
    }
  },

  /**
   * Get all threads for a wallet
   */
  async getThreads(walletAddress?: string | null, limit: number = 50): Promise<Thread[]> {
    try {
      const params: any = { limit };
      if (walletAddress) {
        params.wallet_address = walletAddress;
      }
      const response = await api.get('/threads', { params });
      return response.data;
    } catch (error: any) {
      console.error('Get Threads Error:', error);
      throw error;
    }
  },

  /**
   * Get a specific thread
   */
  async getThread(threadId: string): Promise<Thread> {
    try {
      const response = await api.get(`/threads/${threadId}`);
      return response.data;
    } catch (error: any) {
      console.error('Get Thread Error:', error);
      throw error;
    }
  },

  /**
   * Update a thread title
   */
  async updateThread(threadId: string, threadData: ThreadUpdate): Promise<Thread> {
    try {
      const response = await api.put(`/threads/${threadId}`, threadData);
      return response.data;
    } catch (error: any) {
      console.error('Update Thread Error:', error);
      throw error;
    }
  },

  /**
   * Delete a thread
   */
  async deleteThread(threadId: string): Promise<{ message: string }> {
    try {
      const response = await api.delete(`/threads/${threadId}`);
      return response.data;
    } catch (error: any) {
      console.error('Delete Thread Error:', error);
      throw error;
    }
  },

  /**
   * Archive a thread
   */
  async archiveThread(threadId: string): Promise<{ message: string }> {
    try {
      const response = await api.post(`/threads/${threadId}/archive`);
      return response.data;
    } catch (error: any) {
      console.error('Archive Thread Error:', error);
      throw error;
    }
  },

  /**
   * Get all messages for a thread
   */
  async getThreadMessages(threadId: string): Promise<MessageWithMetadata[]> {
    try {
      const response = await api.get(`/threads/${threadId}/messages`);
      return response.data;
    } catch (error: any) {
      console.error('Get Thread Messages Error:', error);
      throw error;
    }
  },

  /**
   * Save messages to a thread
   */
  async saveThreadMessages(threadId: string, messages: any[]): Promise<{ message: string }> {
    try {
      const response = await api.post(`/threads/${threadId}/messages`, messages);
      return response.data;
    } catch (error: any) {
      console.error('Save Thread Messages Error:', error);
      throw error;
    }
  }
};

// Agent Account Management API
export interface ImportWalletRequest {
  private_key: string;
  name?: string;
  chain?: string;
}

export interface ImportWalletResponse {
  success: boolean;
  account_id: string;
  address: string;
  name: string;
  chain: string;
  network: string;
  message: string;
}

export interface ExportAccountRequest {
  account_id: string;
}

export interface ExportAccountResponse {
  chain: string;
  address: string;
  private_key: string;
  export_format: string;
  warning: string;
  success: boolean;
}

export const agentApi = {
  /**
   * Import external wallet into agent management
   */
  async importWallet(request: ImportWalletRequest): Promise<ImportWalletResponse> {
    try {
      const response = await api.post('/api/agent/import-wallet', {
        private_key: request.private_key,
        name: request.name,
        chain: request.chain || 'stellar'
      });
      return response.data;
    } catch (error: any) {
      console.error('Import Wallet Error:', error);
      const errorMessage = error.response?.data?.detail ||
                         error.response?.data?.error ||
                         error.message ||
                         'Failed to import wallet';
      throw new Error(errorMessage);
    }
  },

  /**
   * Export agent account private key
   */
  async exportAccount(request: ExportAccountRequest): Promise<ExportAccountResponse> {
    try {
      const response = await api.post('/api/agent/export-account', {
        account_id: request.account_id
      });
      return response.data;
    } catch (error: any) {
      console.error('Export Account Error:', error);
      const errorMessage = error.response?.data?.detail ||
                         error.response?.data?.error ||
                         error.message ||
                         'Failed to export account';
      throw new Error(errorMessage);
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