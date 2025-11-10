/**
 * Export Account Modal
 *
 * Allows users to export their agent-managed account private key
 * for use in external wallets (Freighter, xBull, etc.)
 *
 * Security considerations:
 * - Requires explicit user confirmation
 * - Shows clear security warnings
 * - Displays private key only after export
 * - Provides copy-to-clipboard functionality
 */

import { useState } from "react";
import { Button } from "@stellar/design-system";
import { agentApi, type ExportAccountResponse } from "../../lib/api";

interface ExportAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  accountId: string;
  accountAddress: string;
  accountName?: string;
}

export function ExportAccountModal({
  isOpen,
  onClose,
  accountId,
  accountAddress,
  accountName,
}: ExportAccountModalProps) {
  const [step, setStep] = useState<"confirm" | "exported">("confirm");
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportedData, setExportedData] =
    useState<ExportAccountResponse | null>(null);
  const [showPrivateKey, setShowPrivateKey] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    setError(null);

    try {
      const response = await agentApi.exportAccount({ account_id: accountId });

      console.log("✅ Account exported successfully");
      setExportedData(response);
      setStep("exported");
    } catch (err: any) {
      console.error("❌ Failed to export account:", err);
      setError(err.message || "Failed to export account");
    } finally {
      setIsExporting(false);
    }
  };

  const handleCopy = async () => {
    if (exportedData?.private_key) {
      try {
        await navigator.clipboard.writeText(exportedData.private_key);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error("Failed to copy to clipboard:", err);
      }
    }
  };

  const handleClose = () => {
    if (!isExporting) {
      setStep("confirm");
      setExportedData(null);
      setError(null);
      setShowPrivateKey(false);
      setCopied(false);
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
        className="export-account-modal"
        style={{
          maxWidth: "550px",
          padding: "24px",
          backgroundColor: "var(--color-bg-primary, #fff)",
          borderRadius: "8px",
          maxHeight: "90vh",
          overflowY: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {step === "confirm" ? (
          <>
            <h2 style={{ marginTop: 0, marginBottom: "16px" }}>
              Export Account
            </h2>

            <p
              style={{ marginBottom: "16px", color: "#666", fontSize: "14px" }}
            >
              You are about to export the private key for:
            </p>

            <div
              style={{
                backgroundColor: "#F8F9FA",
                border: "1px solid #DEE2E6",
                borderRadius: "4px",
                padding: "12px",
                marginBottom: "24px",
              }}
            >
              <div style={{ marginBottom: "8px" }}>
                <strong>Name:</strong> {accountName || "Unnamed Account"}
              </div>
              <div style={{ fontFamily: "monospace", fontSize: "12px" }}>
                <strong>Address:</strong> {accountAddress}
              </div>
            </div>

            {/* Security Warning */}
            <div
              style={{
                backgroundColor: "#F8D7DA",
                border: "1px solid #F5C6CB",
                borderRadius: "4px",
                padding: "16px",
                marginBottom: "24px",
              }}
            >
              <strong
                style={{
                  color: "#721C24",
                  display: "block",
                  marginBottom: "8px",
                }}
              >
                🔴 Critical Security Warning
              </strong>
              <ul
                style={{
                  margin: "0",
                  paddingLeft: "20px",
                  color: "#721C24",
                  fontSize: "13px",
                  lineHeight: "1.6",
                }}
              >
                <li>Anyone with your private key can control your funds</li>
                <li>Never share your private key with anyone</li>
                <li>
                  Store it securely offline (not in emails or cloud storage)
                </li>
                <li>Tuxedo cannot recover lost or stolen private keys</li>
                <li>Consider the risks before exporting</li>
              </ul>
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
              style={{
                display: "flex",
                gap: "12px",
                justifyContent: "flex-end",
              }}
            >
              <Button
                variant="secondary"
                size="md"
                onClick={handleClose}
                disabled={isExporting}
              >
                Cancel
              </Button>
              <Button
                variant="error"
                size="md"
                onClick={handleExport}
                disabled={isExporting}
              >
                {isExporting
                  ? "Exporting..."
                  : "I Understand, Export Private Key"}
              </Button>
            </div>
          </>
        ) : (
          <>
            <h2 style={{ marginTop: 0, marginBottom: "16px" }}>
              ✅ Account Exported
            </h2>

            <p
              style={{ marginBottom: "16px", color: "#666", fontSize: "14px" }}
            >
              Your private key has been exported. Store it securely and never
              share it with anyone.
            </p>

            {/* Account Info */}
            <div
              style={{
                backgroundColor: "#F8F9FA",
                border: "1px solid #DEE2E6",
                borderRadius: "4px",
                padding: "12px",
                marginBottom: "16px",
              }}
            >
              <div style={{ marginBottom: "8px" }}>
                <strong>Address:</strong>
              </div>
              <div
                style={{
                  fontFamily: "monospace",
                  fontSize: "12px",
                  wordBreak: "break-all",
                  padding: "8px",
                  backgroundColor: "#fff",
                  borderRadius: "4px",
                }}
              >
                {exportedData?.address}
              </div>
            </div>

            {/* Private Key Display */}
            <div style={{ marginBottom: "24px" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "8px",
                }}
              >
                <strong>Private Key (Secret Key):</strong>
                <button
                  onClick={() => setShowPrivateKey(!showPrivateKey)}
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    fontSize: "14px",
                    color: "#666",
                  }}
                >
                  {showPrivateKey ? "Hide" : "Show"}
                </button>
              </div>

              <div
                style={{
                  backgroundColor: "#FFF3CD",
                  border: "1px solid #FFE69C",
                  borderRadius: "4px",
                  padding: "12px",
                  position: "relative",
                }}
              >
                {showPrivateKey ? (
                  <div
                    style={{
                      fontFamily: "monospace",
                      fontSize: "12px",
                      wordBreak: "break-all",
                      userSelect: "all",
                    }}
                  >
                    {exportedData?.private_key}
                  </div>
                ) : (
                  <div
                    style={{
                      fontSize: "24px",
                      textAlign: "center",
                      color: "#666",
                    }}
                  >
                    ••••••••••••••••••••••••••••
                  </div>
                )}

                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleCopy}
                  style={{ marginTop: "12px", width: "100%" }}
                >
                  {copied ? "✓ Copied!" : "📋 Copy to Clipboard"}
                </Button>
              </div>
            </div>

            {/* Security Reminder */}
            <div
              style={{
                backgroundColor: "#D1ECF1",
                border: "1px solid #BEE5EB",
                borderRadius: "4px",
                padding: "12px",
                marginBottom: "24px",
                fontSize: "13px",
                color: "#0C5460",
              }}
            >
              <strong>Next Steps:</strong>
              <ul style={{ margin: "8px 0 0 0", paddingLeft: "20px" }}>
                <li>
                  Import this key into Freighter or another Stellar wallet
                </li>
                <li>Store a backup copy in a secure location</li>
                <li>Never share this key or store it online</li>
              </ul>
            </div>

            {/* Close Button */}
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <Button variant="primary" size="md" onClick={handleClose}>
                Done
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
