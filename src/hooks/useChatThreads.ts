import { useState, useEffect, useCallback } from "react";
import { Thread, threadsApi } from "../lib/api";
import { useWallet } from "./useWallet";

// Extended message type that includes streaming information
export interface ExtendedChatMessage {
  role: "user" | "assistant";
  content: string;
  id?: string;
  type?: string;
  toolName?: string;
  iteration?: number;
  isStreaming?: boolean;
  summary?: string;
}

interface UseChatThreadsReturn {
  threads: Thread[];
  currentThreadId: string | null;
  currentThreadTitle: string;
  messages: ExtendedChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ExtendedChatMessage[]>>;
  isLoading: boolean;
  createNewThread: () => string;
  loadThread: (threadId: string) => Promise<void>;
  saveCurrentThread: (messages: ExtendedChatMessage[]) => Promise<void>;
  updateThreadTitle: (title: string) => void;
  updateThread: (threadId: string, title: string) => Promise<void>;
  deleteThread: (threadId: string) => Promise<void>;
  refreshThreads: () => Promise<void>;
}

export const useChatThreads = (): UseChatThreadsReturn => {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const [currentThreadTitle, setCurrentThreadTitle] =
    useState<string>("New Chat");
  const [messages, setMessages] = useState<ExtendedChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const wallet = useWallet();

  // Initialize with a temporary thread if no threads exist
  useEffect(() => {
    const initializeThreads = async () => {
      try {
        const fetchedThreads = await threadsApi.getThreads(
          wallet.address || null,
        );
        setThreads(fetchedThreads);

        if (fetchedThreads.length === 0) {
          // Start with a temporary thread
          setCurrentThreadId(null);
          setCurrentThreadTitle("New Chat");
          setMessages([]);
        } else {
          // Load the most recent thread
          const mostRecentThread = fetchedThreads[0];
          await loadThread(mostRecentThread.id);
        }
      } catch (error) {
        console.error("Error initializing threads:", error);
      }
    };

    initializeThreads();
  }, [wallet.address]);

  const createNewThread = useCallback((): string => {
    // Create a temporary thread ID until we save it
    const tempThreadId = `temp_${Date.now()}`;
    setCurrentThreadId(tempThreadId);
    setCurrentThreadTitle("New Chat");
    setMessages([]);
    return tempThreadId;
  }, []);

  const loadThread = useCallback(
    async (threadId: string): Promise<void> => {
      setIsLoading(true);
      try {
        const [threadData, threadMessages] = await Promise.all([
          threadsApi.getThread(threadId),
          threadsApi.getThreadMessages(threadId),
        ]);

        setCurrentThreadId(threadId);
        setCurrentThreadTitle(threadData.title);

        // Convert database messages back to ExtendedChatMessage format
        const extendedMessages: ExtendedChatMessage[] = threadMessages.map(
          (msg) => ({
            role: msg.role as "user" | "assistant",
            content: msg.content,
            id: msg.id,
            type: msg.metadata?.type,
            toolName: msg.metadata?.toolName,
            iteration: msg.metadata?.iteration,
            isStreaming: msg.metadata?.isStreaming || false,
            summary: msg.metadata?.summary,
          }),
        );

        setMessages(extendedMessages);
      } catch (error) {
        console.error("Error loading thread:", error);
        // If loading fails, create a new thread
        createNewThread();
      } finally {
        setIsLoading(false);
      }
    },
    [createNewThread],
  );

  const saveCurrentThread = useCallback(
    async (currentMessages: ExtendedChatMessage[]): Promise<void> => {
      if (currentMessages.length === 0) {
        return; // Don't save empty conversations
      }

      try {
        let threadIdToUse = currentThreadId;

        // If we have a temporary thread, create a real one
        if (!threadIdToUse || threadIdToUse.startsWith("temp_")) {
          const title =
            currentMessages[0]?.content?.substring(0, 50) || "New Chat";
          const cleanTitle = title.replace(/[^\w\s-]/gi, "").trim();
          const finalTitle = cleanTitle.length > 0 ? cleanTitle : "New Chat";

          const newThread = await threadsApi.createThread({
            title: finalTitle,
            wallet_address: wallet.address || null,
          });

          threadIdToUse = newThread.id;
          setCurrentThreadId(threadIdToUse);
          setCurrentThreadTitle(finalTitle);

          // Update threads list
          setThreads((prev) => [newThread, ...prev]);
        }

        // Save messages to thread
        await threadsApi.saveThreadMessages(threadIdToUse, currentMessages);

        // Update thread's last activity timestamp
        setThreads((prev) =>
          prev.map((thread) =>
            thread.id === threadIdToUse
              ? { ...thread, updated_at: new Date().toISOString() }
              : thread,
          ),
        );
      } catch (error) {
        console.error("Error saving thread:", error);
      }
    },
    [currentThreadId],
  );

  const updateThreadTitle = useCallback(
    (title: string) => {
      setCurrentThreadTitle(title);

      // If we have a real thread, update it in the database
      if (currentThreadId && !currentThreadId.startsWith("temp_")) {
        threadsApi
          .updateThread(currentThreadId, { title })
          .then(() => {
            setThreads((prev) =>
              prev.map((thread) =>
                thread.id === currentThreadId ? { ...thread, title } : thread,
              ),
            );
          })
          .catch((error) => {
            console.error("Error updating thread title:", error);
          });
      }
    },
    [currentThreadId],
  );

  const updateThread = useCallback(
    async (threadId: string, title: string) => {
      try {
        await threadsApi.updateThread(threadId, { title });
        setThreads((prev) =>
          prev.map((thread) =>
            thread.id === threadId ? { ...thread, title } : thread,
          ),
        );
        // Also update current thread title if this is the current thread
        if (threadId === currentThreadId) {
          setCurrentThreadTitle(title);
        }
      } catch (error) {
        console.error("Error updating thread:", error);
        throw error;
      }
    },
    [currentThreadId],
  );

  const deleteThread = useCallback(async (threadId: string) => {
    try {
      await threadsApi.deleteThread(threadId);
      setThreads((prev) => prev.filter((thread) => thread.id !== threadId));
    } catch (error) {
      console.error("Error deleting thread:", error);
      throw error;
    }
  }, []);

  const refreshThreads = useCallback(async () => {
    try {
      const fetchedThreads = await threadsApi.getThreads(
        wallet.address || null,
      );
      setThreads(fetchedThreads);
    } catch (error) {
      console.error("Error refreshing threads:", error);
    }
  }, [wallet.address]);

  return {
    threads,
    currentThreadId,
    currentThreadTitle,
    messages,
    isLoading,
    setMessages,
    createNewThread,
    loadThread,
    saveCurrentThread,
    updateThreadTitle,
    updateThread,
    deleteThread,
    refreshThreads,
  };
};
