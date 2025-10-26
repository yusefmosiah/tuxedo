import React, { useState, useEffect, useRef } from 'react';
import { Button, Text } from '@stellar/design-system';
import { chatApi, ChatMessage, StreamMessage, type HealthResponse } from '../lib/api';
import { useWallet } from '../hooks/useWallet';
import '../App.module.css';

// Extended message type that includes streaming information
interface ExtendedChatMessage extends ChatMessage {
  id?: string;
  type?: StreamMessage['type'];
  toolName?: string;
  iteration?: number;
  isStreaming?: boolean;
  summary?: string;
}

export const ChatInterface: React.FC = () => {
  const wallet = useWallet();
  const [messages, setMessages] = useState<ExtendedChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agentThinking, setAgentThinking] = useState(false);
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [collapsedToolCalls, setCollapsedToolCalls] = useState<Set<string>>(new Set());
  const [useLiveSummary, setUseLiveSummary] = useState(true); // User preference
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check API health on mount and setup interval
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health: HealthResponse = await chatApi.healthCheck();

        if (health.status === 'healthy' && health.stellar_tools_ready) {
          setApiStatus('connected');
          // Update live summary preference based on backend availability
          if (!health.live_summary_ready) {
            setUseLiveSummary(false);
          }
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

  // Auto-collapse tool call results by default
  useEffect(() => {
    const newCollapsed = new Set<string>();
    messages.forEach(msg => {
      if (msg.type === 'tool_result' && msg.id) {
        newCollapsed.add(msg.id);
      }
    });
    setCollapsedToolCalls(newCollapsed);
  }, [messages]);

  // Auto-scroll to bottom - more reliable implementation
  useEffect(() => {
    const scrollToBottom = () => {
      const messagesContainer = messagesEndRef.current?.parentElement;
      if (messagesContainer) {
        // Use setTimeout to ensure DOM has updated
        setTimeout(() => {
          messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 50);
      }
    };

    scrollToBottom();
  }, [messages, agentThinking]); // Also scroll when thinking state changes

  
  // Toggle tool call expansion
  const toggleToolCallExpansion = (toolCallId: string) => {
    setCollapsedToolCalls(prev => {
      const newSet = new Set(prev);
      if (newSet.has(toolCallId)) {
        newSet.delete(toolCallId);
      } else {
        newSet.add(toolCallId);
      }
      return newSet;
    });
  };

  // Helper function to handle regular stream messages
  const handleRegularStreamMessage = (streamMessage: StreamMessage, streamId: string) => {
    // Handle thinking states for loading indicator
    if (streamMessage.type === 'thinking' || streamMessage.type === 'tool_call_start') {
      setAgentThinking(true);
      return; // Don't add these as visible messages when using live summary
    }

    // Clear thinking state when we get real content
    setAgentThinking(false);

    // Handle each streaming message
    const extendedMessage: ExtendedChatMessage = {
      role: 'assistant',
      content: streamMessage.content,
      id: `stream-${streamId}-${streamMessage.type}-${streamMessage.iteration || 0}`,
      type: streamMessage.type,
      toolName: streamMessage.tool_name,
      iteration: streamMessage.iteration,
      isStreaming: streamMessage.type !== 'final_response' && streamMessage.type !== 'error',
      summary: streamMessage.summary,
    };

    setMessages((prev) => {
      // Check if we already have this exact message (by ID) to avoid duplicates
      const existingMessageIndex = prev.findIndex(m => m.id === extendedMessage.id);

      if (existingMessageIndex >= 0) {
        // Update existing message if found
        const updated = [...prev];
        updated[existingMessageIndex] = extendedMessage;
        return updated;
      } else {
        // Add new message
        return [...prev, extendedMessage];
      }
    });
  };

  
  const handleSend = async () => {
    if (!input.trim() || isLoading || apiStatus === 'disconnected') return;

    console.log('🔍 Wallet state:', {
      wallet: wallet,
      address: wallet.address,
      isConnected: !!wallet.address
    });

    const streamId = Date.now().toString();

    const userMessage: ExtendedChatMessage = {
      role: 'user',
      content: input,
      id: `user-${streamId}`,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setAgentThinking(false); // Reset thinking state for new message

    try {
      // Choose API based on live summary preference and availability
      const useLiveSummaryApi = useLiveSummary;

      console.log('🔍 Debug: useLiveSummaryApi =', useLiveSummaryApi);
      console.log('🔍 Debug: useLiveSummary state =', useLiveSummary);

      if (useLiveSummaryApi) {
        console.log('🔍 Using live summary API...');
        // Use live summary streaming API
        const cleanup = chatApi.sendMessageWithLiveSummary(
          {
            message: input,
            history: messages.filter(m => m.role !== 'user' || m.id !== `user-${streamId}`), // Filter out current user message
            wallet_address: wallet.address || null,
            enable_summary: true,
          },
          (streamMessage: StreamMessage) => {
            
            // Handle other message types normally
            handleRegularStreamMessage(streamMessage, streamId);
          },
          (error: Error) => {
            console.error('Live summary streaming error:', error);
            setAgentThinking(false);
            const errorMessage: ExtendedChatMessage = {
              role: 'assistant',
              content: `Live summary streaming error: ${error.message}`,
              id: `error-${streamId}`,
              type: 'error',
              isStreaming: false,
            };
            setMessages((prev) => [...prev, errorMessage]);
            setIsLoading(false);
          },
          () => {
            setAgentThinking(false);
            setIsLoading(false);
          }
        );

        return () => {
          cleanup();
        };
      } else {
        // Use regular streaming API
        const cleanup = chatApi.sendMessageStream(
          {
            message: input,
            history: messages.filter(m => m.role !== 'user' || m.id !== `user-${streamId}`), // Filter out current user message
            wallet_address: wallet.address || null,
          },
          (streamMessage: StreamMessage) => {
            // Handle thinking states for loading indicator
            if (streamMessage.type === 'thinking' || streamMessage.type === 'tool_call_start') {
              setAgentThinking(true);
              return; // Don't add these as visible messages
            }

            // Clear thinking state when we get real content
            setAgentThinking(false);

            // Handle each streaming message
            const extendedMessage: ExtendedChatMessage = {
              role: 'assistant',
              content: streamMessage.content,
              id: `stream-${streamId}-${streamMessage.type}-${streamMessage.iteration || 0}`,
              type: streamMessage.type,
              toolName: streamMessage.tool_name,
              iteration: streamMessage.iteration,
              isStreaming: streamMessage.type !== 'final_response' && streamMessage.type !== 'error',
              summary: streamMessage.summary,
            };

            setMessages((prev) => {
              // Check if we already have this exact message (by ID) to avoid duplicates
              const existingMessageIndex = prev.findIndex(m => m.id === extendedMessage.id);

              if (existingMessageIndex >= 0) {
                // Update existing message if found
                const updated = [...prev];
                updated[existingMessageIndex] = extendedMessage;
                return updated;
              } else {
                // Add new message
                return [...prev, extendedMessage];
              }
            });
          },
          (error: Error) => {
            console.error('Streaming chat error:', error);
            setAgentThinking(false); // Clear thinking state on error
            const errorMessage: ExtendedChatMessage = {
              role: 'assistant',
              content: `Streaming error: ${error.message}`,
              id: `error-${streamId}`,
              type: 'error',
              isStreaming: false,
            };
            setMessages((prev) => [...prev, errorMessage]);
            setIsLoading(false);
          },
          () => {
            // Stream closed
            setAgentThinking(false); // Clear thinking state on close
            setIsLoading(false);
          }
        );

      // Store cleanup function
      return () => {
        cleanup();
      };
      }
    } catch (error: any) {
      console.error('Chat error:', error);
      const errorMessage: ExtendedChatMessage = {
        role: 'assistant',
        content: error.message || 'Sorry, I encountered an error. Please try again.',
        id: `error-${streamId}`,
        type: 'error',
        isStreaming: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 60px)', // Account for app header
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
              🤖 Hi! I'm Tuxedo AI Agent
            </Text>
            <Text as="p" size="md" style={{ color: '#666' }}>
              I can help you with Stellar blockchain operations, account management, trading, market data, and smart contracts
            </Text>
            {wallet.address && (
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
              <p>"What's the current Stellar network status?"</p>
              <p>"Create a new testnet account and fund it"</p>
              <p>"Check the XLM/USDC orderbook on Stellar DEX"</p>
              <p>"What's in my wallet?" (connect wallet first)</p>
              <p>"Show me recent network transactions"</p>
              <p>"Explain Stellar transaction fees"</p>
            </div>
          </div>
        )}

              {messages.map((msg, idx) => {
          // Show user messages
          if (msg.role === 'user') {
            return (
              <div
                key={msg.id || idx}
                style={{
                  display: 'flex',
                  justifyContent: 'flex-end',
                  marginBottom: '12px',
                  alignItems: 'flex-start',
                }}
                onMouseEnter={(e) => {
                  const copyButton = e.currentTarget.querySelector('[data-user-copy-button]');
                  if (copyButton) {
                    (copyButton as HTMLElement).style.opacity = '1';
                  }
                }}
                onMouseLeave={(e) => {
                  const copyButton = e.currentTarget.querySelector('[data-user-copy-button]');
                  if (copyButton) {
                    (copyButton as HTMLElement).style.opacity = '0';
                  }
                }}
              >
                <div
                  style={{
                    maxWidth: '75%',
                    padding: '10px 14px',
                    borderRadius: '12px',
                    backgroundColor: '#667eea',
                    color: '#fff',
                    border: 'none',
                    position: 'relative',
                    transition: 'all 0.2s ease-in-out',
                    cursor: 'default',
                    transform: 'scale(1)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.01)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  {/* Copy button for user messages */}
                  <div
                    data-user-copy-button
                    style={{
                      position: 'absolute',
                      top: '6px',
                      right: '6px',
                      opacity: 0,
                      transition: 'opacity 0.2s',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.opacity = '1';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.opacity = '0';
                    }}
                  >
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(msg.content).then(() => {
                          console.log('Message copied to clipboard');
                        });
                      }}
                      style={{
                        background: 'rgba(255,255,255,0.9)',
                        border: '1px solid rgba(0,0,0,0.1)',
                        cursor: 'pointer',
                        padding: '4px 6px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        transition: 'all 0.2s',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'rgba(255,255,255,1)';
                        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.9)';
                        e.currentTarget.style.boxShadow = 'none';
                      }}
                      title="Copy message"
                    >
                      📋
                    </button>
                  </div>

                  <Text
                    as="p"
                    size="sm"
                    style={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.4,
                      margin: 0,
                    }}
                  >
                    {msg.content}
                  </Text>
                </div>
              </div>
            );
          }

          // Show all assistant messages as full conversation
          if (msg.role === 'assistant') {
            // AI Responses
            if (msg.type === 'llm_response') {
              return (
                <div
                  key={msg.id || idx}
                  style={{
                    marginBottom: '12px',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    backgroundColor: '#e3f2fd',
                    border: '1px solid #90caf9',
                    borderLeft: '4px solid #2196f3',
                  }}
                >
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '8px'
                  }}>
                    <Text as="div" size="sm" style={{ fontWeight: 'bold', color: '#1565c0' }}>
                      💭 AI Response
                    </Text>
                    {msg.iteration && (
                      <Text as="div" size="xs" style={{ color: '#666' }}>
                        Step {msg.iteration}
                      </Text>
                    )}
                  </div>
                  <Text
                    as="p"
                    size="sm"
                    style={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.4,
                      margin: 0,
                      color: '#1565c0',
                    }}
                  >
                    {msg.content}
                  </Text>
                </div>
              );
            }

            // Tool Results - collapsible with LLM-generated summary
            if (msg.type === 'tool_result') {
              const isCollapsed = msg.id ? collapsedToolCalls.has(msg.id) : false;
              // Use LLM-generated summary if available, otherwise fall back to truncation
              const summary = msg.summary || (msg.content.split('\n')[0].substring(0, 100) + (msg.content.length > 100 ? '...' : ''));

              return (
                <div
                  key={msg.id || idx}
                  style={{
                    marginBottom: '8px',
                    border: '1px solid #81c784',
                    borderRadius: '6px',
                    backgroundColor: '#e8f5e8',
                  }}
                >
                  <div
                    onClick={() => msg.id && toggleToolCallExpansion(msg.id)}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      borderBottom: isCollapsed ? 'none' : '1px solid #c8e6c9',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#f1f8e9';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#e8f5e8';
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Text as="div" size="sm" style={{ fontWeight: 'bold', color: '#2e7d32' }}>
                        ✅ {msg.toolName || 'Tool'}
                      </Text>
                      <Text as="div" size="xs" style={{ color: '#666', fontStyle: 'italic' }}>
                        {summary}
                      </Text>
                    </div>
                    <Text as="div" size="xs" style={{ color: '#666' }}>
                      {isCollapsed ? '▶' : '▼'}
                    </Text>
                  </div>

                  {!isCollapsed && (
                    <div style={{
                      padding: '12px',
                      borderTop: '1px solid #c8e6c9',
                      backgroundColor: '#f1f8e9',
                    }}>
                      <Text
                        as="div"
                        size="xs"
                        style={{
                          fontFamily: 'monospace',
                          whiteSpace: 'pre-wrap',
                          margin: 0,
                          color: '#2e7d32',
                          maxHeight: '200px',
                          overflowY: 'auto',
                        }}
                      >
                        {msg.content}
                      </Text>
                    </div>
                  )}
                </div>
              );
            }

            // Tool Errors
            if (msg.type === 'tool_error') {
              return (
                <div
                  key={msg.id || idx}
                  style={{
                    marginBottom: '12px',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    backgroundColor: '#ffebee',
                    border: '1px solid #ef5350',
                    borderLeft: '4px solid #f44336',
                  }}
                >
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '8px'
                  }}>
                    <Text as="div" size="sm" style={{ fontWeight: 'bold', color: '#c62828' }}>
                      ❌ Tool Error: {msg.toolName}
                    </Text>
                    {msg.iteration && (
                      <Text as="div" size="xs" style={{ color: '#666' }}>
                        Step {msg.iteration}
                      </Text>
                    )}
                  </div>
                  <Text
                    as="p"
                    size="sm"
                    style={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.4,
                      margin: 0,
                      color: '#c62828',
                    }}
                  >
                    {msg.content}
                  </Text>
                </div>
              );
            }

            // Final Responses - plain text, left-aligned, no bubble
            if (msg.type === 'final_response') {
              return (
                <div
                  key={msg.id || idx}
                  style={{
                    textAlign: 'left',
                    margin: '24px 0',
                    padding: '0 20px',
                  }}
                >
                  <Text
                    as="p"
                    size="md"
                    style={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.6,
                      margin: 0,
                      color: '#333',
                      fontSize: '16px',
                      fontWeight: '400',
                    }}
                  >
                    {msg.content}
                  </Text>
                </div>
              );
            }

            // Generic error messages
            if (msg.type === 'error') {
              return (
                <div
                  key={msg.id || idx}
                  style={{
                    marginBottom: '12px',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    backgroundColor: '#ffebee',
                    border: '1px solid #ef5350',
                    borderLeft: '4px solid #f44336',
                  }}
                >
                  <Text
                    as="p"
                    size="sm"
                    style={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.4,
                      margin: 0,
                      color: '#c62828',
                    }}
                  >
                    ⚠️ {msg.content}
                  </Text>
                </div>
              );
            }
          }

          return null;
        })}

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
            onKeyDown={handleKeyDown}
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