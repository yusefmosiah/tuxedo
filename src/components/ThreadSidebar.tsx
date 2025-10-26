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
            borderBottom: '1px solid #e0e0e0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >
          <Text as="h3" size="md" weight="semi-bold">
            Chat History
          </Text>
          <Button
            variant="tertiary"
            size="sm"
            onClick={onToggle}
            style={{
              padding: '4px',
              minWidth: 'auto',
              color: '#666'
            }}
          >
            ✕
          </Button>
        </div>

        {/* New Thread Button */}
        <div
          style={{
            padding: '12px 16px',
            borderBottom: '1px solid #e0e0e0'
          }}
        >
          <Button
            variant="primary"
            size="md"
            onClick={handleNewThread}
            style={{
              width: '100%',
              justifyContent: 'flex-start',
              gap: '8px'
            }}
          >
            + New Chat
          </Button>
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
              <Text as="p" size="sm" style={{ color: '#666' }}>
                Loading threads...
              </Text>
            </div>
          ) : threads.length === 0 ? (
            <div style={{ padding: '16px', textAlign: 'center' }}>
              <Text as="p" size="sm" style={{ color: '#999' }}>
                No chat history yet
              </Text>
            </div>
          ) : (
            threads.map((thread) => (
              <div
                key={thread.id}
                style={{
                  margin: '0 12px 4px',
                  padding: '12px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  backgroundColor: currentThreadId === thread.id ? '#f0f4ff' : 'transparent',
                  border: currentThreadId === thread.id ? '1px solid #2196f3' : '1px solid transparent',
                  transition: 'all 0.2s ease',
                  position: 'relative'
                }}
                onMouseEnter={(e) => {
                  if (currentThreadId !== thread.id) {
                    e.currentTarget.style.backgroundColor = '#f8f9fa';
                  }
                }}
                onMouseLeave={(e) => {
                  if (currentThreadId !== thread.id) {
                    e.currentTarget.style.backgroundColor = 'transparent';
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
                      style={{
                        width: '100%',
                        padding: '4px 8px',
                        border: '1px solid #2196f3',
                        borderRadius: '4px',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                      autoFocus
                    />
                  </div>
                ) : (
                  <>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Text
                        as="div"
                        size="sm"
                        weight={currentThreadId === thread.id ? 'semi-bold' : 'medium'}
                        style={{
                          flex: 1,
                          color: currentThreadId === thread.id ? '#1565c0' : '#333',
                          lineHeight: 1.4,
                          marginBottom: '4px'
                        }}
                      >
                        {truncateTitle(thread.title)}
                      </Text>

                      {/* Action buttons */}
                      <div
                        style={{
                          display: 'flex',
                          gap: '4px',
                          opacity: 0,
                          transition: 'opacity 0.2s'
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
                            startEditingThread(thread.id, thread.title);
                          }}
                          style={{
                            padding: '2px 6px',
                            backgroundColor: 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            color: '#666',
                            fontSize: '12px',
                            borderRadius: '3px'
                          }}
                          title="Edit title"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteThread(thread.id);
                          }}
                          disabled={deletingThreadId === thread.id}
                          style={{
                            padding: '2px 6px',
                            backgroundColor: 'transparent',
                            border: 'none',
                            cursor: deletingThreadId === thread.id ? 'not-allowed' : 'pointer',
                            color: deletingThreadId === thread.id ? '#ccc' : '#666',
                            fontSize: '12px',
                            borderRadius: '3px'
                          }}
                          title="Delete thread"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>

                    <Text
                      as="div"
                      size="xs"
                      style={{
                        color: '#999',
                        fontSize: '11px'
                      }}
                    >
                      {formatDate(thread.updated_at)}
                    </Text>
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
            borderTop: '1px solid #e0e0e0',
            backgroundColor: '#f8f9fa'
          }}
        >
          <Text as="p" size="xs" style={{ color: '#999', textAlign: 'center' }}>
            {wallet.address ? `Connected: ${wallet.address.slice(0, 6)}...` : 'Not connected'}
          </Text>
        </div>
      </div>
    </>
  );
};