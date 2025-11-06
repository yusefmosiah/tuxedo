import React from "react";
import { useAgent } from "../../providers/AgentProvider";

/**
 * AgentAccounts Component - Shows agent account information
 *
 * Displays all accounts managed by the AI agent with their balances
 * and basic account information
 */
export const AgentAccounts: React.FC = () => {
  const agent = useAgent();

  if (agent.accounts.length === 0) {
    return (
      <div
        style={{
          padding: "20px",
          backgroundColor: "var(--color-bg-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--border-radius-lg)",
          textAlign: "center",
        }}
      >
        <h3
          style={{ margin: "0 0 12px 0", color: "var(--color-text-primary)" }}
        >
          🤖 Agent Accounts
        </h3>
        <p
          style={{
            margin: 0,
            color: "var(--color-text-secondary)",
            fontStyle: "italic",
            fontSize: "14px",
          }}
        >
          No agent accounts yet. The agent will create accounts automatically as
          needed.
        </p>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: "20px",
        backgroundColor: "var(--color-bg-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--border-radius-lg)",
      }}
    >
      <h3
        style={{
          margin: "0 0 16px 0",
          color: "var(--color-text-primary)",
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}
      >
        🤖 Agent Accounts ({agent.accounts.length})
      </h3>

      <div
        style={{
          display: "grid",
          gap: "12px",
          maxHeight: "300px",
          overflowY: "auto",
        }}
      >
        {agent.accounts.map((account, index) => (
          <div
            key={account.address}
            style={{
              padding: "12px",
              backgroundColor: "var(--color-bg-primary)",
              border: "1px solid var(--color-border)",
              borderRadius: "8px",
              fontFamily: "monospace",
              fontSize: "13px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <span
                style={{
                  fontWeight: "bold",
                  color: "var(--color-text-primary)",
                  fontFamily: "var(--font-primary)",
                }}
              >
                {account.name || `Account ${index + 1}`}
              </span>
              <span
                style={{
                  color: "var(--color-text-secondary)",
                  fontSize: "12px",
                }}
              >
                {account.address.slice(0, 8)}...{account.address.slice(-8)}
              </span>
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                fontSize: "12px",
                color: "var(--color-text-secondary)",
              }}
            >
              <span>Balance: {account.balance} XLM</span>
              <span>Network: {account.network}</span>
            </div>

            {account.created_at && (
              <div
                style={{
                  marginTop: "6px",
                  fontSize: "11px",
                  color: "var(--color-text-secondary)",
                  borderTop: "1px solid var(--color-border)",
                  paddingTop: "6px",
                }}
              >
                Created: {new Date(account.created_at).toLocaleDateString()}
              </div>
            )}
          </div>
        ))}
      </div>

      <div
        style={{
          marginTop: "16px",
          padding: "12px",
          backgroundColor: "rgba(46, 208, 110, 0.1)",
          border: "1px solid rgba(46, 208, 110, 0.3)",
          borderRadius: "8px",
          fontSize: "13px",
          color: "var(--color-text-secondary)",
        }}
      >
        💡 <strong>Agent-First Architecture:</strong> The AI agent manages these
        accounts autonomously. All transactions are handled by the agent without
        user intervention.
      </div>
    </div>
  );
};
