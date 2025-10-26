import React, { useState, useEffect, useRef } from 'react';
import { Button, Text, Loader } from '@stellar/design-system';
import { chatApi, ChatMessage, type HealthResponse } from '../lib/api';
import { useWallet } from '../hooks/useWallet';

export const ChatInterface: React.FC = () => {
  const { data: wallet } = useWallet();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check API health on mount and setup interval
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health: HealthResponse = await chatApi.healthCheck();

        if (health.status === 'healthy' && health.stellar_tools_ready) {
          setApiStatus('connected');
        } else {
          setApiStatus('disconnected');
        }
      } catch (error) {
        console.error('Health check failed:', error);
        setApiStatus('disconnected');
      }
    };

    // Initial health check
    checkHealth();

    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || apiStatus === 'disconnected') return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: input,
        history: messages,
      });

      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error: any) {
      console.error('Chat error:', error);

      const errorMessage = error.response?.data?.detail ||
                          error.message ||
                          'Sorry, I encountered an error. Please try again.';

      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: errorMessage,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIndicator = () => {
    switch (apiStatus) {
      case 'connected':
        return '🟢';
      case 'disconnected':
        return '🔴';
      case 'checking':
        return '🟡';
    }
  };

  const getStatusText = () => {
    switch (apiStatus) {
      case 'connected':
        return 'Connected to backend';
      case 'disconnected':
        return 'Backend offline - Start FastAPI server';
      case 'checking':
        return 'Checking connection...';
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSend();
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '600px',
        border: '1px solid #e0e0e0',
        borderRadius: '12px',
        overflow: 'hidden',
        backgroundColor: '#fff',
      }}
    >
      {/* Header with status */}
      <div
        style={{
          padding: '16px 20px',
          backgroundColor: '#f8f9fa',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Text as="h3" size="md" weight="semi-bold">
          💬 Tuxedo AI Assistant
        </Text>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px' }}>{getStatusIndicator()}</span>
          <Text as="p" size="sm" style={{ color: '#666' }}>
            {getStatusText()}
          </Text>
        </div>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px',
        }}
      >
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', marginTop: '40px' }}>
            <Text as="p" size="lg" style={{ marginBottom: '16px' }}>
              👋 Hi! I'm Tuxedo
            </Text>
            <Text as="p" size="md" style={{ color: '#666' }}>
              Ask me about Blend lending pools, yields, and DeFi opportunities on Stellar
            </Text>
            {wallet?.address && (
              <Text as="p" size="sm" style={{ color: '#999', marginTop: '8px' }}>
                Connected: {wallet.address.slice(0, 8)}...{wallet.address.slice(-4)}
              </Text>
            )}

            {apiStatus === 'disconnected' && (
              <div style={{
                marginTop: '24px',
                padding: '12px 16px',
                backgroundColor: '#fff3cd',
                border: '1px solid #ffeaa7',
                borderRadius: '8px',
                color: '#856404',
              }}>
                <Text as="p" size="sm">
                  <strong>Backend not connected!</strong><br/>
                  Run: <code style={{ backgroundColor: '#f8f9fa', padding: '2px 4px', borderRadius: '4px' }}>
                    cd backend && source .venv/bin/activate && python main.py
                  </code>
                </Text>
              </div>
            )}

            <div
              style={{
                marginTop: '24px',
                fontSize: '14px',
                color: '#999',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              <p style={{ fontWeight: '600', marginBottom: '4px' }}>Try asking:</p>
              <p>"What yields are available for USDC?"</p>
              <p>"Which pool has the best APY?"</p>
              <p>"Explain how Blend lending works"</p>
              <p>"What are the risks of high APY pools?"</p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '16px',
            }}
          >
            <div
              style={{
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: '12px',
                backgroundColor: msg.role === 'user' ? '#667eea' : '#f0f0f0',
                color: msg.role === 'user' ? '#fff' : '#000',
              }}
            >
              <Text as="p" size="sm" style={{ whiteSpace: 'pre-wrap' }}>
                {msg.content}
              </Text>
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div
              style={{
                padding: '12px 16px',
                borderRadius: '12px',
                backgroundColor: '#f0f0f0',
              }}
            >
              <Loader size="sm" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        style={{
          padding: '16px',
          borderTop: '1px solid #e0e0e0',
          backgroundColor: '#fafafa',
        }}
      >
        <div style={{ display: 'flex', gap: '8px' }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              apiStatus === 'disconnected'
                ? "Backend offline - check console for errors"
                : "Ask about yields, pools, or DeFi concepts..."
            }
            disabled={isLoading || apiStatus === 'disconnected'}
            style={{
              flex: 1,
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              fontSize: '14px',
              fontFamily: 'inherit',
              resize: 'none',
              minHeight: '44px',
              backgroundColor: apiStatus === 'disconnected' ? '#f8f9fa' : '#fff',
              cursor: apiStatus === 'disconnected' ? 'not-allowed' : 'text',
            }}
            rows={1}
          />
          <Button
            variant="primary"
            size="md"
            onClick={handleSend}
            disabled={isLoading || !input.trim() || apiStatus === 'disconnected'}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};