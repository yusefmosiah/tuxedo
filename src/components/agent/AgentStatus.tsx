import React from "react";
import { useAgent } from "../../providers/AgentProvider";

/**
 * AgentStatus Component - Displays current agent state
 *
 * Shows whether the AI agent is active, idle, or in error state
 * with appropriate visual indicators
 */
export const AgentStatus: React.FC = () => {
  const agent = useAgent();

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "#2ED06E";
      case "idle":
        return "#FFB800";
      case "error":
        return "#FF3B30";
      default:
        return "#C1C7D0";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return "🤖";
      case "idle":
        return "⏸️";
      case "error":
        return "❌";
      default:
        return "❓";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "active":
        return "Active";
      case "idle":
        return "Idle";
      case "error":
        return "Error";
      default:
        return "Unknown";
    }
  };

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
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "12px",
          marginBottom: "16px",
        }}
      >
        <div
          style={{
            width: "16px",
            height: "16px",
            borderRadius: "50%",
            backgroundColor: getStatusColor(agent.status),
            animation: agent.status === "active" ? "pulse 2s infinite" : "none",
          }}
        />
        <span
          style={{
            fontSize: "24px",
            fontWeight: "bold",
            color: getStatusColor(agent.status),
          }}
        >
          {getStatusIcon(agent.status)} Agent {getStatusText(agent.status)}
        </span>
      </div>

      {agent.error && (
        <div
          style={{
            padding: "12px",
            backgroundColor: "#ffebee",
            border: "1px solid #ef5350",
            borderRadius: "8px",
            marginTop: "12px",
            fontSize: "14px",
            color: "#c62828",
          }}
        >
          Error: {agent.error}
        </div>
      )}

      {agent.isLoading && (
        <div
          style={{
            marginTop: "12px",
            fontSize: "14px",
            color: "var(--color-text-secondary)",
          }}
        >
          Loading agent data...
        </div>
      )}

      <style>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `}</style>
    </div>
  );
};
