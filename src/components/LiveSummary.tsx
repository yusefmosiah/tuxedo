import React, { useState } from 'react';
import { StreamMessage } from '../lib/api';

interface LiveSummaryProps {
  message: StreamMessage;
  onToggleExpand: () => void;
  isExpanded: boolean;
}

/**
 * LiveSummary component for displaying evolving summaries of AI conversations.
 * Shows a single line summary that can be expanded to show full details.
 */
export const LiveSummary: React.FC<LiveSummaryProps> = ({
  message,
  onToggleExpand,
  isExpanded
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [currentSummary, setCurrentSummary] = useState(message.content);
  const [isFading, setIsFading] = useState(false);

  // Handle summary changes with smooth fade transitions
  React.useEffect(() => {
    if (currentSummary !== message.content) {
      setIsFading(true);
      const timer = setTimeout(() => {
        setCurrentSummary(message.content);
        setIsFading(false);
      }, 200); // Fade out duration

      return () => clearTimeout(timer);
    }
  }, [message.content, currentSummary]);

  if (!message.type?.startsWith('live_summary')) {
    return null;
  }

  const isLive = message.isLive ?? false;
  const fullContent = message.fullContent || [];

  // Determine status icon
  const getStatusIcon = () => {
    if (isLive) {
      return '🔄';
    }
    return '📄';
  };

  const getToolCount = () => {
    const toolMessages = fullContent.filter(msg =>
      msg.type === 'tool_result' || msg.type === 'tool_error'
    );
    return toolMessages.length;
  };

  const getTimestamp = () => {
    // For now, return a relative time - could be enhanced with actual timestamps
    return 'just now';
  };

  return (
    <div className="live-summary-container">
      {/* Plain text summary with smooth fade transition */}
      <div
        onClick={onToggleExpand}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        style={{
          padding: '8px 0',
          margin: '4px 0',
          cursor: 'pointer',
          transition: 'opacity 0.3s ease-in-out',
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          opacity: isFading ? 0 : (isLive ? 1 : 0.9),
          transform: isFading ? 'translateY(2px)' : 'translateY(0)',
        }}
      >
        <span className="status-icon" style={{
          fontSize: '14px',
          opacity: 0.7,
          minWidth: '20px'
        }}>
          {getStatusIcon()}
        </span>

        <span className="summary-text" style={{
          flex: 1,
          color: '#666',
          fontStyle: isLive ? 'italic' : 'normal'
        }}>
          {currentSummary}
        </span>

        {!isExpanded && (
          <span
            className="expand-hint"
            style={{
              fontSize: '11px',
              opacity: isHovered ? 0.7 : 0.5,
              fontStyle: 'italic',
              color: '#999',
              transition: 'opacity 0.2s ease',
            }}
          >
            [details]
          </span>
        )}

        {isExpanded && (
          <span
            className="collapse-hint"
            style={{
              fontSize: '11px',
              opacity: 0.7,
              fontStyle: 'italic',
              color: '#999',
            }}
          >
            [hide]
          </span>
        )}
      </div>

      {/* Add global styles for fade animations */}
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeOut {
          from { opacity: 1; transform: translateY(0); }
          to { opacity: 0; transform: translateY(-4px); }
        }
      `}</style>

      {/* Expanded content */}
      {isExpanded && fullContent.length > 0 && (
        <div
          className="expanded-content"
          style={{
            background: '#ffffff',
            border: '1px solid #e0e0e0',
            borderRadius: '6px',
            marginTop: '8px',
            padding: '12px',
            maxHeight: '400px',
            overflowY: 'auto',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          }}
        >
          <div
            className="expanded-header"
            style={{
              borderBottom: '1px solid #f0f0f0',
              paddingBottom: '8px',
              marginBottom: '12px',
              fontSize: '12px',
              color: '#666',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <span>Full Conversation Details</span>
            <span style={{ fontSize: '11px' }}>
              {getToolCount() > 0 && `🔧 ${getToolCount()} tools • `}
              {getTimestamp()}
            </span>
          </div>

          {fullContent.map((contentMessage, index) => (
            <div key={index} style={{ marginBottom: '8px' }}>
              {contentMessage.type === 'llm_response' && (
                <div style={{
                  background: '#e3f2fd',
                  padding: '8px',
                  borderRadius: '4px',
                  borderLeft: '3px solid #2196f3'
                }}>
                  <div style={{
                    fontSize: '11px',
                    color: '#666',
                    marginBottom: '4px',
                    fontWeight: 'bold'
                  }}>
                    💭 AI Response
                  </div>
                  <div style={{ fontSize: '13px', whiteSpace: 'pre-wrap' }}>
                    {contentMessage.content}
                  </div>
                </div>
              )}

              {contentMessage.type === 'tool_result' && (
                <div style={{
                  background: '#e8f5e8',
                  padding: '8px',
                  borderRadius: '4px',
                  borderLeft: '3px solid #4caf50'
                }}>
                  <div style={{
                    fontSize: '11px',
                    color: '#666',
                    marginBottom: '4px',
                    fontWeight: 'bold'
                  }}>
                    ✅ Tool Result: {contentMessage.tool_name}
                  </div>
                  <div style={{
                    fontSize: '12px',
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap',
                    maxHeight: '150px',
                    overflowY: 'auto'
                  }}>
                    {contentMessage.content}
                  </div>
                </div>
              )}

              {contentMessage.type === 'tool_error' && (
                <div style={{
                  background: '#ffebee',
                  padding: '8px',
                  borderRadius: '4px',
                  borderLeft: '3px solid #f44336'
                }}>
                  <div style={{
                    fontSize: '11px',
                    color: '#666',
                    marginBottom: '4px',
                    fontWeight: 'bold'
                  }}>
                    ❌ Tool Error: {contentMessage.tool_name}
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: '#c62828',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {contentMessage.content}
                  </div>
                </div>
              )}

              {contentMessage.type === 'final_response' && (
                <div style={{
                  background: '#f3e5f5',
                  padding: '8px',
                  borderRadius: '4px',
                  borderLeft: '3px solid #9c27b0'
                }}>
                  <div style={{
                    fontSize: '11px',
                    color: '#666',
                    marginBottom: '4px',
                    fontWeight: 'bold'
                  }}>
                    🎯 Final Response
                  </div>
                  <div style={{ fontSize: '13px', whiteSpace: 'pre-wrap' }}>
                    {contentMessage.content}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};