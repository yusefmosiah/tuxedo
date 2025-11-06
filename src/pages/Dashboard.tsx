import React from "react";
import { Link } from "react-router-dom";
import { Heading, Card, Content } from "@stellar/design-system";
import { useAgent } from "../providers/AgentProvider";
import PoolsDashboard from "../components/dashboard/PoolsDashboard";
import { DeFindexVaultsDashboard } from "../components/dashboard/DeFindexVaultsDashboard";

const Dashboard: React.FC = () => {
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

  const getStatusText = (status: string) => {
    switch (status) {
      case "active":
        return "🤖 Active";
      case "idle":
        return "⏸️ Idle";
      case "error":
        return "❌ Error";
      default:
        return "❓ Unknown";
    }
  };

  return (
    <div style={{ padding: "24px" }}>
      <div style={{ marginBottom: "32px", textAlign: "center" }}>
        <Heading as="h1" size="lg" style={{ marginBottom: "16px" }}>
          🤖 Tuxedo AI - Your DeFi Agent
        </Heading>
        <div
          style={{
            backgroundColor: "var(--color-stellar-glow-subtle)",
            border: "1px solid var(--color-stellar-glow-strong)",
            borderRadius: "var(--border-radius-lg)",
            padding: "24px",
            marginBottom: "24px",
          }}
        >
          <Heading
            as="h2"
            size="md"
            style={{
              marginBottom: "12px",
              color: "var(--color-stellar-glow-strong)",
            }}
          >
            💬 Access Your Personal DeFi Agent Chat
          </Heading>
          <p
            style={{
              fontSize: "16px",
              lineHeight: "1.6",
              margin: "0 0 16px 0",
              color: "var(--color-text-primary)",
            }}
          >
            Get instant help with Stellar DeFi operations, account management,
            trading strategies, and smart contract interactions. Our AI agent
            manages its own testnet accounts and provides real-time, actionable
            guidance.
          </p>
          <div
            style={{ display: "flex", justifyContent: "center", gap: "12px" }}
          >
            <Link
              to="/chat"
              style={{
                display: "inline-block",
                padding: "12px 24px",
                backgroundColor: "var(--color-stellar-glow-strong)",
                color: "white",
                textDecoration: "none",
                borderRadius: "var(--border-radius-md)",
                fontWeight: "bold",
                fontSize: "14px",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                transition: "all 0.2s ease",
                border: "none",
                cursor: "pointer",
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor =
                  "var(--color-stellar-glow-deep)";
                e.currentTarget.style.transform = "translateY(-1px)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor =
                  "var(--color-stellar-glow-strong)";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              🚀 Start Chatting with AI Agent
            </Link>
          </div>
          <p
            style={{
              fontSize: "12px",
              color: "var(--color-text-tertiary)",
              margin: "12px 0 0 0",
              fontStyle: "italic",
            }}
          >
            🔐 Secure email-based authentication required • No wallet
            installation needed
          </p>
        </div>
      </div>

      {/* Separator */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          margin: "32px 0",
          gap: "16px",
        }}
      >
        <div
          style={{
            flex: 1,
            height: "1px",
            background:
              "linear-gradient(to right, transparent, var(--color-border), transparent)",
          }}
        />
        <span
          style={{
            color: "var(--color-text-tertiary)",
            fontSize: "12px",
            textTransform: "uppercase",
            letterSpacing: "0.1em",
            fontWeight: "bold",
            fontFamily: "var(--font-tertiary-mono)",
          }}
        >
          Agent Activity Dashboard
        </span>
        <div
          style={{
            flex: 1,
            height: "1px",
            background:
              "linear-gradient(to right, transparent, var(--color-border), transparent)",
          }}
        />
      </div>

      {/* Agent Status Section */}
      <Card>
        <Content>
          <div style={{ marginBottom: "20px" }}>
            <Heading as="h2" size="md">
              Agent Status
            </Heading>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              marginBottom: "20px",
              padding: "16px",
              backgroundColor: "var(--color-bg-surface)",
              borderRadius: "8px",
              border: `1px solid ${getStatusColor(agent.status)}`,
            }}
          >
            <div
              style={{
                width: "12px",
                height: "12px",
                borderRadius: "50%",
                backgroundColor: getStatusColor(agent.status),
              }}
            />
            <span
              style={{
                fontSize: "16px",
                fontWeight: "bold",
                color: getStatusColor(agent.status),
              }}
            >
              {getStatusText(agent.status)}
            </span>
          </div>

          {agent.error && (
            <div
              style={{
                padding: "12px",
                backgroundColor: "#ffebee",
                border: "1px solid #ef5350",
                borderRadius: "8px",
                marginBottom: "20px",
              }}
            >
              <p style={{ margin: 0, color: "#c62828" }}>
                Error: {agent.error}
              </p>
            </div>
          )}

          {/* Agent Accounts */}
          <div style={{ marginBottom: "20px" }}>
            <Heading as="h3" size="sm">
              Agent Accounts ({agent.accounts.length})
            </Heading>
            {agent.accounts.length > 0 ? (
              <div
                style={{
                  display: "grid",
                  gap: "12px",
                  marginTop: "12px",
                }}
              >
                {agent.accounts.map((account) => (
                  <div
                    key={account.address}
                    style={{
                      padding: "12px",
                      backgroundColor: "var(--color-bg-surface)",
                      border: "1px solid var(--color-border)",
                      borderRadius: "8px",
                      fontFamily: "monospace",
                      fontSize: "14px",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <span>{account.name}</span>
                      <span style={{ color: "var(--color-text-secondary)" }}>
                        {account.address.slice(0, 8)}...
                        {account.address.slice(-8)}
                      </span>
                    </div>
                    <div
                      style={{
                        marginTop: "4px",
                        color: "var(--color-text-secondary)",
                      }}
                    >
                      Balance: {account.balance} XLM
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p
                style={{
                  color: "var(--color-text-secondary)",
                  fontStyle: "italic",
                }}
              >
                No agent accounts yet. The agent will create accounts
                automatically as needed.
              </p>
            )}
          </div>

          {/* Note about Activity */}
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
            💡 <strong>Real-time Activity:</strong> View agent activity in the
            chat interface where responses are streamed live.
          </div>
        </Content>
      </Card>

      {/* DeFindex Vaults Section */}
      <Card>
        <Content>
          <div style={{ marginBottom: "20px" }}>
            <Heading as="h2" size="md">
              🏛️ DeFindex Vaults
            </Heading>
            <p
              style={{ color: "var(--color-text-secondary)", margin: "8px 0" }}
            >
              Yield-generating vaults with AI-powered deposit instructions
            </p>
          </div>
          <DeFindexVaultsDashboard />
        </Content>
      </Card>

      {/* Pools Section - Agent View */}
      <Card>
        <Content>
          <div style={{ marginBottom: "20px" }}>
            <Heading as="h2" size="md">
              📊 Blend Protocol Overview
            </Heading>
            <p
              style={{ color: "var(--color-text-secondary)", margin: "8px 0" }}
            >
              Market data for agent decision-making
            </p>
          </div>
          <PoolsDashboard />
        </Content>
      </Card>
    </div>
  );
};

export default Dashboard;
