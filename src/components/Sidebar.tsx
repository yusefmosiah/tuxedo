import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import "./Sidebar.css";

interface Thread {
  id: string;
  title: string;
  agent_id?: string;
  created_at: string;
  updated_at: string;
}

interface Agent {
  id: string;
  agent_name: string;
  stellar_address: string;
  created_at: string;
}

export function Sidebar() {
  const { user, sessionToken } = useAuth();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [metaInput, setMetaInput] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch threads and agents on component mount
  useEffect(() => {
    if (user && sessionToken) {
      fetchThreads();
      fetchAgents();
    }
  }, [user, sessionToken]);

  const fetchThreads = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/threads", {
        headers: {
          Authorization: `Bearer ${sessionToken}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setThreads(data.threads || []);
      }
    } catch (error) {
      console.error("Failed to fetch threads:", error);
    }
  };

  const fetchAgents = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/agents", {
        headers: {
          Authorization: `Bearer ${sessionToken}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAgents(data.agents || []);
      }
    } catch (error) {
      console.error("Failed to fetch agents:", error);
    }
  };

  const handleMetaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!metaInput.trim() || !sessionToken) return;

    setIsCreating(true);
    setError(null);

    try {
      // Create new agent + thread
      const response = await fetch("http://localhost:8000/api/agents/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
        body: JSON.stringify({
          initial_prompt: metaInput,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create agent");
      }

      const { agent, thread } = await response.json();

      // Update local state
      if (agent) {
        setAgents([...agents, agent]);
      }
      if (thread) {
        setThreads([...threads, thread]);
      }

      setMetaInput("");

      // Navigate to new thread
      window.location.href = `/chat/${thread.id}`;
    } catch (error) {
      console.error("Failed to create agent:", error);
      setError(
        error instanceof Error ? error.message : "Failed to create agent",
      );
    } finally {
      setIsCreating(false);
    }
  };

  const formatStellarAddress = (address: string) => {
    return `${address.slice(0, 8)}...${address.slice(-4)}`;
  };

  return (
    <aside className="sidebar">
      {/* User Info */}
      <div className="user-info">
        <div className="user-avatar">{user?.email?.[0]?.toUpperCase()}</div>
        <div className="user-details">
          <p className="user-email">{user?.email}</p>
          {user?.stellar_public_key && (
            <p className="stellar-address">
              Stellar: {formatStellarAddress(user.stellar_public_key)}
            </p>
          )}
        </div>
      </div>

      {/* Meta Chat Box - Hierarchical Top */}
      <div className="meta-chat-box">
        <h3>🤖 Initialize Agent</h3>
        <form onSubmit={handleMetaSubmit}>
          <textarea
            value={metaInput}
            onChange={(e) => setMetaInput(e.target.value)}
            placeholder="Start a new AI agent... (e.g., 'Create a trading bot for XLM/USDC')"
            className="meta-input"
            rows={3}
            disabled={isCreating}
          />
          <button
            type="submit"
            className="spawn-agent-btn"
            disabled={isCreating || !metaInput.trim()}
          >
            {isCreating ? "⏳ Creating..." : "🚀 Spawn Agent"}
          </button>
        </form>
        {error && <div className="error-message">{error}</div>}
      </div>

      {/* Active Agents */}
      <div className="agents-section">
        <h4>🤖 Active Agents ({agents.length})</h4>
        {agents.length === 0 ? (
          <p className="empty-state">No agents created yet</p>
        ) : (
          <div className="agents-list">
            {agents.map((agent) => (
              <div key={agent.id} className="agent-item">
                <div className="agent-info">
                  <span className="agent-name">{agent.agent_name}</span>
                  <span className="agent-address">
                    {formatStellarAddress(agent.stellar_address)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Thread List */}
      <div className="threads-section">
        <h4>💬 Chat Threads ({threads.length})</h4>
        {threads.length === 0 ? (
          <p className="empty-state">No conversations yet</p>
        ) : (
          <div className="thread-list">
            {threads.map((thread) => (
              <div key={thread.id} className="thread-item">
                <a href={`/chat/${thread.id}`} className="thread-link">
                  <div className="thread-title">{thread.title}</div>
                  <div className="thread-time">
                    {new Date(thread.updated_at).toLocaleDateString()}
                  </div>
                </a>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Actions */}
      <div className="sidebar-actions">
        <button
          className="action-btn"
          onClick={() => (window.location.href = "/settings")}
        >
          ⚙️ Settings
        </button>
        <button
          className="action-btn logout-btn"
          onClick={() => (window.location.href = "/logout")}
        >
          🚪 Logout
        </button>
      </div>
    </aside>
  );
}
