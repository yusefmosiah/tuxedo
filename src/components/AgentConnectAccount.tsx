import React from "react";
import { stellarNetwork } from "../contracts/util";
import { useAgent } from "../providers/AgentProvider";
import NetworkPill from "./NetworkPill";

const AgentConnectAccount: React.FC = () => {
  const { accounts, activeAccount, createAccount, isLoading, error } = useAgent();

  const handleCreateAccount = async () => {
    try {
      await createAccount();
    } catch (err) {
      console.error('Failed to create account:', err);
    }
  };

  if (accounts.length === 0) {
    return (
      <div style={{
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        gap: "10px",
        verticalAlign: "middle",
      }}>
        <button
          onClick={handleCreateAccount}
          disabled={isLoading}
          className="btn-stellar"
          style={{
            fontSize: '12px',
            fontFamily: 'var(--font-tertiary-mono)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            padding: '8px 16px'
          }}
        >
          {isLoading ? 'Creating...' : 'Create Agent Account'}
        </button>
        <NetworkPill />
        {error && (
          <div style={{
            color: 'var(--color-error)',
            fontSize: '12px',
            maxWidth: '200px'
          }}>
            {error}
          </div>
        )}
      </div>
    );
  }

  // Show active account
  return (
    <div style={{
      display: "flex",
      flexDirection: "row",
      alignItems: "center",
      gap: "10px",
      verticalAlign: "middle",
    }}>
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-end",
        gap: "2px"
      }}>
        <div style={{
          fontSize: '12px',
          fontFamily: 'var(--font-tertiary-mono)',
          color: 'var(--color-text-secondary)'
        }}>
          Agent Account
        </div>
        <div style={{
          fontSize: '11px',
          fontFamily: 'var(--font-tertiary-mono)',
          color: 'var(--color-text-primary)',
          background: 'var(--color-bg-surface)',
          padding: '4px 8px',
          borderRadius: '4px',
          border: '1px solid var(--color-border)'
        }}>
          {activeAccount.slice(0, 8)}...{activeAccount.slice(-8)}
        </div>
      </div>

      <button
        onClick={handleCreateAccount}
        disabled={isLoading}
        className="btn-secondary"
        style={{
          fontSize: '10px',
          fontFamily: 'var(--font-tertiary-mono)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          padding: '6px 12px'
        }}
      >
        + New
      </button>

      <NetworkPill />

      {error && (
        <div style={{
          color: 'var(--color-error)',
          fontSize: '12px',
          maxWidth: '200px'
        }}>
          {error}
        </div>
      )}
    </div>
  );
};

export default AgentConnectAccount;