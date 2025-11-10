import { useState } from "react";
import { useWallet } from "../hooks/useWallet";
import { Button } from "@stellar/design-system";
import { ImportWalletModal } from "./modals/ImportWalletModal";
import { ExportAccountModal } from "./modals/ExportAccountModal";

/**
 * WalletSelector Component
 *
 * Allows users to switch between agent mode and external wallet mode,
 * and manage their connected accounts.
 */
export function WalletSelector() {
  const [showImportModal, setShowImportModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportingAccount, setExportingAccount] = useState<{
    id: string;
    address: string;
    name?: string;
  } | null>(null);
  const {
    address,
    isConnected,
    mode,
    setMode,
    connectWallet,
    disconnectWallet,
    agentAccounts,
    selectedAgentAccount,
    setSelectedAgentAccount,
    isPending,
  } = useWallet();

  const formatAddress = (addr: string) =>
    `${addr.slice(0, 4)}...${addr.slice(-4)}`;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        padding: "16px",
        backgroundColor: "var(--color-bg-surface)",
        borderRadius: "var(--border-radius-md)",
        border: "1px solid var(--color-border)",
      }}
    >
      {/* Mode Selector Tabs */}
      <div
        style={{
          display: "flex",
          gap: "8px",
          borderBottom: "1px solid var(--color-border)",
          paddingBottom: "8px",
        }}
      >
        <button
          onClick={() => setMode && setMode("agent")}
          disabled={isPending}
          style={{
            flex: 1,
            padding: "8px 16px",
            fontSize: "12px",
            fontFamily: "var(--font-tertiary-mono)",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            backgroundColor:
              mode === "agent"
                ? "var(--color-stellar-glow-subtle)"
                : "var(--color-bg-primary)",
            color:
              mode === "agent"
                ? "var(--color-text-primary)"
                : "var(--color-text-secondary)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--border-radius-sm)",
            cursor: isPending ? "not-allowed" : "pointer",
            fontWeight: mode === "agent" ? "bold" : "normal",
          }}
        >
          🤖 Agent Mode
        </button>
        <button
          onClick={() => setMode && setMode("external")}
          disabled={isPending}
          style={{
            flex: 1,
            padding: "8px 16px",
            fontSize: "12px",
            fontFamily: "var(--font-tertiary-mono)",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            backgroundColor:
              mode === "external"
                ? "var(--color-stellar-glow-subtle)"
                : "var(--color-bg-primary)",
            color:
              mode === "external"
                ? "var(--color-text-primary)"
                : "var(--color-text-secondary)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--border-radius-sm)",
            cursor: isPending ? "not-allowed" : "pointer",
            fontWeight: mode === "external" ? "bold" : "normal",
          }}
        >
          🔐 My Wallet
        </button>
      </div>

      {/* Agent Mode Content */}
      {mode === "agent" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div
            style={{
              fontSize: "12px",
              color: "var(--color-text-secondary)",
              fontFamily: "var(--font-tertiary-mono)",
            }}
          >
            Agent manages transactions autonomously
          </div>

          {agentAccounts && agentAccounts.length > 0 ? (
            <div
              style={{ display: "flex", flexDirection: "column", gap: "8px" }}
            >
              <label
                htmlFor="agent-account-select"
                style={{
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "var(--color-text-primary)",
                }}
              >
                Select Account:
              </label>
              <select
                id="agent-account-select"
                value={selectedAgentAccount?.id || ""}
                onChange={(e) => {
                  const account = agentAccounts.find(
                    (acc) => acc.id === e.target.value,
                  );
                  if (account && setSelectedAgentAccount) {
                    setSelectedAgentAccount(account);
                  }
                }}
                style={{
                  padding: "8px 12px",
                  fontSize: "13px",
                  fontFamily: "var(--font-tertiary-mono)",
                  backgroundColor: "var(--color-bg-primary)",
                  color: "var(--color-text-primary)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "var(--border-radius-sm)",
                  cursor: "pointer",
                }}
              >
                {agentAccounts.map((acc) => (
                  <option key={acc.id} value={acc.id}>
                    {formatAddress(acc.address)} ({acc.balance || "0"} XLM)
                    {acc.name ? ` - ${acc.name}` : ""}
                  </option>
                ))}
              </select>

              {selectedAgentAccount && (
                <div
                  style={{
                    padding: "12px",
                    backgroundColor: "var(--color-bg-primary)",
                    borderRadius: "var(--border-radius-sm)",
                    fontSize: "12px",
                    fontFamily: "var(--font-tertiary-mono)",
                  }}
                >
                  <div style={{ marginBottom: "4px" }}>
                    <strong>Address:</strong>{" "}
                    <code style={{ fontSize: "11px" }}>
                      {selectedAgentAccount.address}
                    </code>
                  </div>
                  <div>
                    <strong>Balance:</strong>{" "}
                    {selectedAgentAccount.balance || "0"} XLM
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div
              style={{
                padding: "12px",
                textAlign: "center",
                color: "var(--color-text-secondary)",
                fontSize: "13px",
              }}
            >
              No agent accounts found. Ask the agent to create one!
            </div>
          )}

          {/* Agent Mode Actions */}
          <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
            <Button
              onClick={() => setShowImportModal(true)}
              size="sm"
              variant="secondary"
              style={{ flex: 1 }}
            >
              ⬇️ Import Wallet
            </Button>
            {selectedAgentAccount && (
              <Button
                onClick={() => {
                  setExportingAccount({
                    id: selectedAgentAccount.id,
                    address: selectedAgentAccount.address,
                    name: selectedAgentAccount.name,
                  });
                  setShowExportModal(true);
                }}
                size="sm"
                variant="secondary"
                style={{ flex: 1 }}
              >
                ⬆️ Export Account
              </Button>
            )}
          </div>
        </div>
      )}

      {/* External Wallet Mode Content */}
      {mode === "external" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div
            style={{
              fontSize: "12px",
              color: "var(--color-text-secondary)",
              fontFamily: "var(--font-tertiary-mono)",
            }}
          >
            You approve each transaction in your wallet
          </div>

          {isConnected && address ? (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "12px",
                backgroundColor: "var(--color-bg-primary)",
                borderRadius: "var(--border-radius-sm)",
              }}
            >
              <div
                style={{ display: "flex", flexDirection: "column", gap: "4px" }}
              >
                <span
                  style={{
                    fontSize: "11px",
                    color: "var(--color-text-secondary)",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                  }}
                >
                  Connected
                </span>
                <code
                  style={{
                    fontSize: "12px",
                    fontFamily: "var(--font-tertiary-mono)",
                  }}
                >
                  {address}
                </code>
              </div>
              <Button
                onClick={disconnectWallet}
                size="sm"
                variant="secondary"
                disabled={isPending}
              >
                Disconnect
              </Button>
            </div>
          ) : (
            <Button
              onClick={connectWallet}
              size="md"
              variant="primary"
              disabled={isPending}
            >
              {isPending ? "Connecting..." : "Connect Wallet"}
            </Button>
          )}

          {/* External Wallet Mode Actions */}
          {isConnected && address && (
            <div style={{ marginTop: "8px" }}>
              <Button
                onClick={() => setShowImportModal(true)}
                size="sm"
                variant="secondary"
                style={{ width: "100%" }}
              >
                ⬇️ Import to Agent
              </Button>
              <p
                style={{
                  fontSize: "11px",
                  color: "var(--color-text-secondary)",
                  marginTop: "8px",
                  textAlign: "center",
                }}
              >
                Import this wallet for autonomous agent signing
              </p>
            </div>
          )}
        </div>
      )}

      {/* Current Status Footer */}
      <div
        style={{
          marginTop: "8px",
          paddingTop: "12px",
          borderTop: "1px solid var(--color-border)",
          fontSize: "11px",
          color: "var(--color-text-secondary)",
          fontFamily: "var(--font-tertiary-mono)",
          textAlign: "center",
        }}
      >
        {mode === "agent" && "🤖 Agent signing enabled"}
        {mode === "external" && "🔐 Manual approval required"}
        {mode === "imported" && "🔄 Imported wallet - agent signing"}
      </div>

      {/* Import Wallet Modal */}
      <ImportWalletModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onSuccess={() => {
          console.log("Wallet imported successfully!");
        }}
      />

      {/* Export Account Modal */}
      {exportingAccount && (
        <ExportAccountModal
          isOpen={showExportModal}
          onClose={() => {
            setShowExportModal(false);
            setExportingAccount(null);
          }}
          accountId={exportingAccount.id}
          accountAddress={exportingAccount.address}
          accountName={exportingAccount.name}
        />
      )}
    </div>
  );
}
