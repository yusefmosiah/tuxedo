/**
 * Import Wallet Modal
 *
 * Allows users to import their external wallet (Freighter, xBull, etc.)
 * into Tuxedo for autonomous agent signing.
 *
 * Security considerations:
 * - Private key is encrypted on backend with user-specific key
 * - Clear security warnings displayed
 * - HTTPS required for production
 */

import { useState } from "react";
import { Button } from "@stellar/design-system";
import { agentApi, type ImportWalletRequest } from "../../lib/api";
import { useWalletContext } from "../../contexts/WalletContext";

interface ImportWalletModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function ImportWalletModal({
  isOpen,
  onClose,
  onSuccess,
}: ImportWalletModalProps) {
  const [privateKey, setPrivateKey] = useState("");
  const [accountName, setAccountName] = useState("");
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPrivateKey, setShowPrivateKey] = useState(false);

  const { refreshAgentAccounts } = useWalletContext();

  const handleImport = async () => {
    if (!privateKey.trim()) {
      setError("Please enter a private key");
      return;
    }

    // Basic validation for Stellar secret key format
    if (!privateKey.startsWith("S") || privateKey.length !== 56) {
      setError(
        "Invalid Stellar private key format. Should start with 'S' and be 56 characters long.",
      );
      return;
    }

    setIsImporting(true);
    setError(null);

    try {
      const request: ImportWalletRequest = {
        private_key: privateKey,
        name: accountName || undefined,
        chain: "stellar",
      };

      const response = await agentApi.importWallet(request);

      console.log("✅ Wallet imported successfully:", response);

      // Refresh agent accounts to show the new imported account
      await refreshAgentAccounts();

      // Clear form
      setPrivateKey("");
      setAccountName("");

      // Call success callback
      if (onSuccess) {
        onSuccess();
      }

      // Close modal
      onClose();
    } catch (err: any) {
      console.error("❌ Failed to import wallet:", err);
      setError(
        err.message ||
          "Failed to import wallet. Please check your private key.",
      );
    } finally {
      setIsImporting(false);
    }
  };

  const handleClose = () => {
    if (!isImporting) {
      setPrivateKey("");
      setAccountName("");
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
      onClick={handleClose}
    >
      <div
        className="import-wallet-modal"
        style={{
          maxWidth: "500px",
          padding: "24px",
          backgroundColor: "var(--color-bg-primary, #fff)",
          borderRadius: "8px",
          maxHeight: "90vh",
          overflowY: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ marginTop: 0, marginBottom: "16px" }}>
          Import External Wallet
        </h2>

        <p style={{ marginBottom: "24px", color: "#666", fontSize: "14px" }}>
          Import your Freighter or other Stellar wallet into Tuxedo for
          autonomous agent signing. Your private key will be encrypted and
          stored securely.
        </p>

        {/* Security Warning */}
        <div
          style={{
            backgroundColor: "#FFF3CD",
            border: "1px solid #FFE69C",
            borderRadius: "4px",
            padding: "12px",
            marginBottom: "24px",
          }}
        >
          <strong style={{ color: "#856404" }}>⚠️ Security Warning:</strong>
          <ul
            style={{
              margin: "8px 0 0 0",
              paddingLeft: "20px",
              color: "#856404",
              fontSize: "13px",
            }}
          >
            <li>Only import wallets you own and trust</li>
            <li>Your private key will be encrypted on our servers</li>
            <li>Once imported, the agent can sign transactions autonomously</li>
            <li>Never share your private key with anyone else</li>
          </ul>
        </div>

        {/* Account Name Input */}
        <div style={{ marginBottom: "16px" }}>
          <label
            style={{ display: "block", marginBottom: "8px", fontWeight: "500" }}
          >
            Account Name (optional)
          </label>
          <input
            type="text"
            value={accountName}
            onChange={(e) => setAccountName(e.target.value)}
            placeholder="e.g., My Trading Account"
            disabled={isImporting}
            style={{
              width: "100%",
              padding: "8px 12px",
              fontSize: "14px",
              border: "1px solid #ccc",
              borderRadius: "4px",
            }}
          />
        </div>

        {/* Private Key Input */}
        <div style={{ marginBottom: "24px" }}>
          <label
            style={{ display: "block", marginBottom: "8px", fontWeight: "500" }}
          >
            Private Key (Secret Key) *
          </label>
          <div style={{ position: "relative" }}>
            <input
              type={showPrivateKey ? "text" : "password"}
              value={privateKey}
              onChange={(e) => setPrivateKey(e.target.value)}
              placeholder="SXXX..."
              disabled={isImporting}
              style={{
                width: "100%",
                fontFamily: "monospace",
                padding: "8px 40px 8px 12px",
                fontSize: "14px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
            />
            <button
              type="button"
              onClick={() => setShowPrivateKey(!showPrivateKey)}
              style={{
                position: "absolute",
                right: "8px",
                top: "50%",
                transform: "translateY(-50%)",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontSize: "14px",
                color: "#666",
              }}
            >
              {showPrivateKey ? "👁️" : "👁️‍🗨️"}
            </button>
          </div>
          <p style={{ fontSize: "12px", color: "#666", marginTop: "4px" }}>
            Stellar secret keys start with 'S' and are 56 characters long
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div
            style={{
              backgroundColor: "#F8D7DA",
              border: "1px solid #F5C6CB",
              borderRadius: "4px",
              padding: "12px",
              marginBottom: "16px",
              color: "#721C24",
              fontSize: "14px",
            }}
          >
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div
          style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}
        >
          <Button
            variant="secondary"
            size="md"
            onClick={handleClose}
            disabled={isImporting}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={handleImport}
            disabled={isImporting || !privateKey.trim()}
          >
            {isImporting ? "Importing..." : "Import Wallet"}
          </Button>
        </div>
      </div>
    </div>
  );
}
