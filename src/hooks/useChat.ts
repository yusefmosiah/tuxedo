import { useState, useCallback } from "react";
import { ChatRequest, ChatResponse, chatApi } from "../lib/api";

export interface UseChatReturn {
  message: string | null;
  loading: boolean;
  error: string | null;
  sendMessage: (message: string, walletAddress?: string) => Promise<void>;
  clearMessage: () => void;
}

export const useChat = (): UseChatReturn => {
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (content: string, walletAddress?: string) => {
      setMessage(null);
      setError(null);
      setLoading(true);

      try {
        const request: ChatRequest = {
          message: content,
          history: [], // Simple chat with no history for dashboard
          wallet_address: walletAddress || null,
        };

        const response: ChatResponse = await chatApi.sendMessage(request);

        if (response.success) {
          setMessage(response.response);
        } else {
          setError(response.error || "Unknown error occurred");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to send message");
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const clearMessage = useCallback(() => {
    setMessage(null);
    setError(null);
  }, []);

  return {
    message,
    loading,
    error,
    sendMessage,
    clearMessage,
  };
};
