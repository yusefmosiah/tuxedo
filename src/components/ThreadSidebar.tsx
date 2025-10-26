import React, { useState, useEffect } from 'react';
import { Button, Text } from '@stellar/design-system';
import { threadsApi, Thread } from '../lib/api';
import { useWallet } from '../hooks/useWallet';
import styles from './ThreadSidebar.module.css';

interface ThreadSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onThreadSelect: (threadId: string) => void;
  currentThreadId?: string | null;
  onNewThread: () => void;
}

export const ThreadSidebar: React.FC<ThreadSidebarProps> = ({
  isOpen,
  onToggle,
  onThreadSelect,
  currentThreadId,
  onNewThread
}) => {
  const wallet = useWallet();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [editingThreadId, setEditingThreadId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [deletingThreadId, setDeletingThreadId] = useState<string | null>(null);

  // Load threads when wallet changes
  useEffect(() => {
    if (wallet.address) {
      loadThreads();
    }
  }, [wallet.address]);

  const loadThreads = async () => {
    setIsLoading(true);
    try {
      const fetchedThreads = await threadsApi.getThreads(wallet.address || null);
      setThreads(fetchedThreads);
    } catch (error) {
      console.error('Error loading threads:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleThreadClick = (threadId: string) => {
    onThreadSelect(threadId);
  };

  const handleNewThread = () => {
    onNewThread();
  };

  const startEditingThread = (threadId: string, currentTitle: string) => {
    setEditingThreadId(threadId);
    setEditingTitle(currentTitle);
  };

  const saveThreadTitle = async (threadId: string) => {
    try {
      await threadsApi.updateThread(threadId, { title: editingTitle });
      setThreads(threads.map(thread =>
        thread.id === threadId ? { ...thread, title: editingTitle } : thread
      ));
      setEditingThreadId(null);
      setEditingTitle('');
    } catch (error) {
      console.error('Error updating thread title:', error);
    }
  };

  const cancelEditing = () => {
    setEditingThreadId(null);
    setEditingTitle('');
  };

  const deleteThread = async (threadId: string) => {
    if (!confirm('Are you sure you want to delete this thread?')) {
      return;
    }

    setDeletingThreadId(threadId);
    try {
      await threadsApi.deleteThread(threadId);
      setThreads(threads.filter(thread => thread.id !== threadId));

      // If deleted thread was current thread, create new thread
      if (threadId === currentThreadId) {
        onNewThread();
      }
    } catch (error) {
      console.error('Error deleting thread:', error);
    } finally {
      setDeletingThreadId(null);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInHours < 24 * 7) {
      return `${Math.floor(diffInHours / 24)}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const truncateTitle = (title: string, maxLength: number = 30) => {
    return title.length > maxLength ? title.substring(0, maxLength) + '...' : title;
  };

  return (
    <>
      {/* Backdrop for mobile */}
      {isOpen && (
        <div
          className={styles.sidebarBackdrop}
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div
        className={`${styles.sidebar} ${isOpen ? styles.open : ''}`}
      >
        {/* Header */}
        <div
          style={{
            padding: '16px',
            borderBottom: '1px solid var(--color-border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: 'var(--color-bg-surface)'
          }}
        >
          <h3 style={{
            fontFamily: 'var(--font-primary-sans)',
            fontSize: '16px',
            margin: '0',
            color: 'var(--color-text-primary)',
            fontWeight: '500'
          }}>
            Chat History
          </h3>
          <button
            className="btn-secondary"
            onClick={onToggle}
            style={{
              padding: '4px 8px',
              minWidth: 'auto',
              fontSize: '12px',
              fontFamily: 'var(--font-tertiary-mono)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}
          >
            ✕
          </button>
        </div>

        {/* New Thread Button */}
        <div
          style={{
            padding: '12px 16px',
            borderBottom: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-bg-surface)'
          }}
        >
          <button
            className="btn-stellar"
            onClick={handleNewThread}
            style={{
              width: '100%',
              justifyContent: 'flex-start',
              padding: '12px 16px',
              fontSize: '12px',
              fontFamily: 'var(--font-tertiary-mono)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}
          >
            + New Chat
          </button>
        </div>

        {/* Threads List */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '8px 0'
          }}
        >
          {isLoading ? (
            <div style={{ padding: '16px', textAlign: 'center' }}>
              <p style={{
                fontFamily: 'var(--font-secondary-serif)',
                fontSize: '14px',
                color: 'var(--color-text-secondary)',
                fontStyle: 'italic',
                margin: '0'
              }}>
                Loading threads...
              </p>
            </div>
          ) : threads.length === 0 ? (
            <div style={{ padding: '16px', textAlign: 'center' }}>
              <p style={{
                fontFamily: 'var(--font-secondary-serif)',
                fontSize: '14px',
                color: 'var(--color-text-secondary)',
                fontStyle: 'italic',
                margin: '0'
              }}>
                No chat history yet
              </p>
            </div>
          ) : (
            threads.map((thread) => (
              <div
                key={thread.id}
                className="card-minimal"
                style={{
                  margin: '0 12px 4px',
                  padding: '12px',
                  borderRadius: 'var(--border-radius-lg)',
                  cursor: 'pointer',
                  backgroundColor: currentThreadId === thread.id ? 'var(--color-stellar-glow-subtle)' : 'transparent',
                  border: currentThreadId === thread.id ? '1px solid var(--color-stellar-glow-strong)' : '1px solid var(--color-border)',
                  transition: 'var(--transition-fast)',
                  position: 'relative'
                }}
                onMouseEnter={(e) => {
                  if (currentThreadId !== thread.id) {
                    e.currentTarget.style.backgroundColor = 'var(--color-bg-surface)';
                    e.currentTarget.style.borderColor = 'var(--color-stellar-glow-strong)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (currentThreadId !== thread.id) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }
                }}
                onClick={() => handleThreadClick(thread.id)}
              >
                {editingThreadId === thread.id ? (
                  <div onClick={(e) => e.stopPropagation()}>
                    <input
                      type="text"
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onBlur={() => saveThreadTitle(thread.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          saveThreadTitle(thread.id);
                        } else if (e.key === 'Escape') {
                          cancelEditing();
                        }
                      }}
                      className="input-stellar"
                      style={{
                        width: '100%',
                        padding: '4px 8px',
                        border: '1px solid var(--color-stellar-glow-strong)',
                        borderRadius: 'var(--border-radius-sm)',
                        fontSize: '14px',
                        outline: 'none',
                        backgroundColor: 'var(--color-bg-primary)',
                        color: 'var(--color-text-primary)',
                        fontFamily: 'var(--font-primary-sans)'
                      }}
                      autoFocus
                    />
                  </div>
                ) : (
                  <>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div
                        style={{
                          flex: 1,
                          color: currentThreadId === thread.id ? 'var(--color-stellar-glow-strong)' : 'var(--color-text-primary)',
                          lineHeight: 1.6,
                          marginBottom: '8px',
                          fontFamily: 'var(--font-primary-sans)',
                          fontSize: '14px',
                          fontWeight: currentThreadId === thread.id ? '600' : '400'
                        }}
                      >
                        {truncateTitle(thread.title)}
                      </div>

                      {/* Action buttons */}
                      <div
                        style={{
                          display: 'flex',
                          gap: '4px',
                          opacity: 0,
                          transition: 'var(--transition-fast)'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.opacity = '1';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.opacity = '0';
                        }}
                      >
                        <button
                          className="btn-secondary"
                          onClick={(e) => {
                            e.stopPropagation();
                            startEditingThread(thread.id, thread.title);
                          }}
                          style={{
                            padding: '2px 6px',
                            backgroundColor: 'transparent',
                            border: '1px solid var(--color-border)',
                            cursor: 'pointer',
                            color: 'var(--color-text-tertiary)',
                            fontSize: '12px',
                            borderRadius: 'var(--border-radius-sm)',
                            fontFamily: 'var(--font-tertiary-mono)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em'
                          }}
                          title="Edit title"
                        >
                          ✏️
                        </button>
                        <button
                          className="btn-secondary"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteThread(thread.id);
                          }}
                          disabled={deletingThreadId === thread.id}
                          style={{
                            padding: '2px 6px',
                            backgroundColor: 'transparent',
                            border: '1px solid var(--color-border)',
                            cursor: deletingThreadId === thread.id ? 'not-allowed' : 'pointer',
                            color: deletingThreadId === thread.id ? 'var(--color-text-tertiary)' : 'var(--color-negative)',
                            fontSize: '12px',
                            borderRadius: 'var(--border-radius-sm)',
                            fontFamily: 'var(--font-tertiary-mono)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                            opacity: deletingThreadId === thread.id ? 0.6 : 1
                          }}
                          title="Delete thread"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>

                    <div
                      style={{
                        fontFamily: 'var(--font-tertiary-mono)',
                        fontSize: '11px',
                        color: 'var(--color-text-tertiary)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        fontWeight: 'bold'
                      }}
                    >
                      {formatDate(thread.updated_at)}
                    </div>
                  </>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: '12px 16px',
            borderTop: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-bg-surface)'
          }}
        >
          <p style={{
            fontFamily: 'var(--font-tertiary-mono)',
            fontSize: '11px',
            color: 'var(--color-text-tertiary)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            fontWeight: 'bold',
            margin: '0',
            textAlign: 'center'
          }}>
            {wallet.address ? `Connected: ${wallet.address.slice(0, 6)}...` : 'Not connected'}
          </p>
        </div>
      </div>
    </>
  );
};