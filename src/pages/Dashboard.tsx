import React from "react";
import { Link } from "react-router-dom";
import { Heading } from "@stellar/design-system";

const Dashboard: React.FC = () => {
  return (
    <div
      style={{
        padding: "24px",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div style={{ maxWidth: "600px", width: "100%", textAlign: "center" }}>
        <Heading as="h1" size="lg" style={{ marginBottom: "16px" }}>
          🤖 Tuxedo AI - Your DeFi Agent
        </Heading>

        <div
          style={{
            backgroundColor: "var(--color-stellar-glow-subtle)",
            border: "1px solid var(--color-stellar-glow-strong)",
            borderRadius: "var(--border-radius-lg)",
            padding: "32px",
            marginBottom: "32px",
          }}
        >
          <Heading
            as="h2"
            size="md"
            style={{
              marginBottom: "16px",
              color: "var(--color-stellar-glow-strong)",
            }}
          >
            💬 Access Your Personal DeFi Agent Chat
          </Heading>
          <p
            style={{
              fontSize: "16px",
              lineHeight: "1.6",
              margin: "0 0 24px 0",
              color: "var(--color-text-primary)",
            }}
          >
            Get instant help with Stellar DeFi operations, account management,
            trading strategies, and smart contract interactions. Our AI agent
            operates on mainnet and provides real-time, actionable guidance with
            real funds and real yields.
          </p>
          <div
            style={{ display: "flex", justifyContent: "center", gap: "12px" }}
          >
            <Link
              to="/chat"
              style={{
                display: "inline-block",
                padding: "14px 28px",
                backgroundColor: "var(--color-stellar-glow-strong)",
                color: "white",
                textDecoration: "none",
                borderRadius: "var(--border-radius-md)",
                fontWeight: "bold",
                fontSize: "16px",
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
              margin: "16px 0 0 0",
              fontStyle: "italic",
            }}
          >
            🔐 Secure email-based authentication required • No wallet
            installation needed
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
