import React, { useState } from "react";
import { useVaultStats } from "../../hooks/useVaultStats";
import { useWallet } from "../../hooks/useWallet";

/**
 * VaultDashboard - TUX0 Vault interface
 *
 * Features:
 * - Displays vault TVL, share value, and APY
 * - User deposit interface
 * - User withdrawal interface
 * - Shows user's current position
 * - Real-time stats updates
 */
export const VaultDashboard: React.FC = () => {
  const { stats, userShares, loading, error, refetch } = useVaultStats();
  const { address: walletAddress } = useWallet();

  const [depositAmount, setDepositAmount] = useState("");
  const [withdrawShares, setWithdrawShares] = useState("");
  const [activeTab, setActiveTab] = useState<"deposit" | "withdraw">("deposit");

  const handleDeposit = async () => {
    if (!depositAmount || !walletAddress) return;

    // TODO: Implement actual deposit via backend API
    const response = await fetch("/api/vault/deposit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount: parseFloat(depositAmount),
        asset: "USDC",
        walletAddress,
      }),
    });

    const result = await response.json();
    alert(result.message);
    setDepositAmount("");
    refetch();
  };

  const handleWithdraw = async () => {
    if (!withdrawShares || !walletAddress) return;

    // TODO: Implement actual withdrawal via backend API
    const response = await fetch("/api/vault/withdraw", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        shares: parseFloat(withdrawShares),
        walletAddress,
      }),
    });

    const result = await response.json();
    alert(result.message);
    setWithdrawShares("");
    refetch();
  };

  // Calculate user position value
  const userPositionValue = userShares * stats.shareValue;
  const userYield = userPositionValue - userShares;
  const userYieldPercent =
    userShares > 0 ? (userYield / userShares) * 100 : 0;

  return (
    <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "20px" }}>
      {/* Dashboard Header */}
      <div
        className="card"
        style={{
          marginBottom: "32px",
          padding: "32px",
          backgroundColor: "var(--color-bg-surface)",
          border: "1px solid var(--color-border)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "start",
          }}
        >
          <div>
            <h1
              style={{
                fontFamily: "var(--font-primary-sans)",
                fontSize: "32px",
                margin: "0 0 8px 0",
                color: "var(--color-text-primary)",
                fontWeight: "500",
              }}
            >
              🎩 TUX0 Vault
            </h1>
            <p
              style={{
                fontFamily: "var(--font-secondary-serif)",
                fontSize: "16px",
                margin: "0",
                color: "var(--color-text-secondary)",
                fontStyle: "italic",
                lineHeight: "1.5",
              }}
            >
              Non-custodial yield vault powered by Blend Capital • 2% platform
              fee, 98% to users
            </p>
          </div>

          <button
            className="btn-stellar"
            onClick={refetch}
            disabled={loading}
            style={{
              fontSize: "12px",
              fontFamily: "var(--font-tertiary-mono)",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              padding: "12px 20px",
            }}
          >
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        {/* Vault Stats */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "20px",
            marginTop: "32px",
          }}
        >
          {/* TVL */}
          <div
            className="card"
            style={{
              padding: "24px",
              backgroundColor: "var(--color-bg-primary)",
              border: "1px solid var(--color-border)",
            }}
          >
            <div
              style={{
                fontFamily: "var(--font-tertiary-mono)",
                fontSize: "12px",
                color: "var(--color-text-tertiary)",
                marginBottom: "12px",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                fontWeight: "bold",
              }}
            >
              Total Value Locked
            </div>
            <div
              style={{
                fontFamily: "var(--font-primary-sans)",
                fontSize: "28px",
                color: "var(--color-text-primary)",
                fontWeight: "500",
              }}
            >
              ${stats.tvl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          </div>

          {/* Share Value */}
          <div
            className="card"
            style={{
              padding: "24px",
              backgroundColor: "var(--color-bg-primary)",
              border: "1px solid var(--color-border)",
            }}
          >
            <div
              style={{
                fontFamily: "var(--font-tertiary-mono)",
                fontSize: "12px",
                color: "var(--color-text-tertiary)",
                marginBottom: "12px",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                fontWeight: "bold",
              }}
            >
              TUX0 Share Value
            </div>
            <div
              style={{
                fontFamily: "var(--font-primary-sans)",
                fontSize: "28px",
                color: "var(--color-text-primary)",
                fontWeight: "500",
              }}
            >
              ${stats.shareValue.toFixed(7)}
            </div>
          </div>

          {/* APY */}
          <div
            className="card"
            style={{
              padding: "24px",
              backgroundColor: "var(--color-bg-primary)",
              border: "1px solid var(--color-border)",
            }}
          >
            <div
              style={{
                fontFamily: "var(--font-tertiary-mono)",
                fontSize: "12px",
                color: "var(--color-text-tertiary)",
                marginBottom: "12px",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                fontWeight: "bold",
              }}
            >
              Current APY
            </div>
            <div
              style={{
                fontFamily: "var(--font-primary-sans)",
                fontSize: "28px",
                color: "var(--color-accent-green)",
                fontWeight: "500",
              }}
            >
              {stats.apy.toFixed(2)}%
            </div>
          </div>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "32px",
        }}
      >
        {/* Deposit/Withdraw Interface */}
        <div
          className="card"
          style={{
            padding: "32px",
            backgroundColor: "var(--color-bg-surface)",
            border: "1px solid var(--color-border)",
          }}
        >
          <h2
            style={{
              fontFamily: "var(--font-primary-sans)",
              fontSize: "24px",
              margin: "0 0 24px 0",
              color: "var(--color-text-primary)",
              fontWeight: "500",
            }}
          >
            Vault Actions
          </h2>

          {/* Tabs */}
          <div
            style={{
              display: "flex",
              gap: "16px",
              marginBottom: "24px",
              borderBottom: "1px solid var(--color-border)",
            }}
          >
            <button
              onClick={() => setActiveTab("deposit")}
              style={{
                fontFamily: "var(--font-tertiary-mono)",
                fontSize: "14px",
                padding: "12px 24px",
                background: "none",
                border: "none",
                borderBottom:
                  activeTab === "deposit"
                    ? "2px solid var(--color-accent-blue)"
                    : "2px solid transparent",
                color:
                  activeTab === "deposit"
                    ? "var(--color-accent-blue)"
                    : "var(--color-text-secondary)",
                cursor: "pointer",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                fontWeight: "bold",
              }}
            >
              Deposit
            </button>
            <button
              onClick={() => setActiveTab("withdraw")}
              style={{
                fontFamily: "var(--font-tertiary-mono)",
                fontSize: "14px",
                padding: "12px 24px",
                background: "none",
                border: "none",
                borderBottom:
                  activeTab === "withdraw"
                    ? "2px solid var(--color-accent-blue)"
                    : "2px solid transparent",
                color:
                  activeTab === "withdraw"
                    ? "var(--color-accent-blue)"
                    : "var(--color-text-secondary)",
                cursor: "pointer",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                fontWeight: "bold",
              }}
            >
              Withdraw
            </button>
          </div>

          {/* Deposit Form */}
          {activeTab === "deposit" && (
            <div>
              <label
                style={{
                  display: "block",
                  fontFamily: "var(--font-tertiary-mono)",
                  fontSize: "12px",
                  color: "var(--color-text-tertiary)",
                  marginBottom: "8px",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  fontWeight: "bold",
                }}
              >
                Deposit Amount (USDC)
              </label>
              <input
                type="number"
                value={depositAmount}
                onChange={(e) => setDepositAmount(e.target.value)}
                placeholder="100.00"
                style={{
                  width: "100%",
                  padding: "12px",
                  fontFamily: "var(--font-primary-sans)",
                  fontSize: "16px",
                  border: "1px solid var(--color-border)",
                  borderRadius: "4px",
                  backgroundColor: "var(--color-bg-primary)",
                  color: "var(--color-text-primary)",
                  marginBottom: "16px",
                }}
              />
              <p
                style={{
                  fontFamily: "var(--font-secondary-serif)",
                  fontSize: "14px",
                  color: "var(--color-text-secondary)",
                  fontStyle: "italic",
                  marginBottom: "24px",
                }}
              >
                You will receive approximately{" "}
                {depositAmount
                  ? (parseFloat(depositAmount) / stats.shareValue).toFixed(7)
                  : "0.0000000"}{" "}
                TUX0 shares
              </p>
              <button
                className="btn-stellar"
                onClick={handleDeposit}
                disabled={!depositAmount || !walletAddress || loading}
                style={{
                  width: "100%",
                  fontFamily: "var(--font-tertiary-mono)",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                }}
              >
                {walletAddress ? "Deposit to Vault" : "Connect Wallet"}
              </button>
            </div>
          )}

          {/* Withdraw Form */}
          {activeTab === "withdraw" && (
            <div>
              <label
                style={{
                  display: "block",
                  fontFamily: "var(--font-tertiary-mono)",
                  fontSize: "12px",
                  color: "var(--color-text-tertiary)",
                  marginBottom: "8px",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  fontWeight: "bold",
                }}
              >
                Shares to Withdraw
              </label>
              <input
                type="number"
                value={withdrawShares}
                onChange={(e) => setWithdrawShares(e.target.value)}
                placeholder="50.00"
                style={{
                  width: "100%",
                  padding: "12px",
                  fontFamily: "var(--font-primary-sans)",
                  fontSize: "16px",
                  border: "1px solid var(--color-border)",
                  borderRadius: "4px",
                  backgroundColor: "var(--color-bg-primary)",
                  color: "var(--color-text-primary)",
                  marginBottom: "16px",
                }}
              />
              <p
                style={{
                  fontFamily: "var(--font-secondary-serif)",
                  fontSize: "14px",
                  color: "var(--color-text-secondary)",
                  fontStyle: "italic",
                  marginBottom: "24px",
                }}
              >
                You will receive approximately $
                {withdrawShares
                  ? (parseFloat(withdrawShares) * stats.shareValue).toFixed(2)
                  : "0.00"}{" "}
                USDC
              </p>
              <button
                className="btn-stellar"
                onClick={handleWithdraw}
                disabled={!withdrawShares || !walletAddress || loading}
                style={{
                  width: "100%",
                  fontFamily: "var(--font-tertiary-mono)",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                }}
              >
                {walletAddress ? "Withdraw from Vault" : "Connect Wallet"}
              </button>
            </div>
          )}
        </div>

        {/* User Position */}
        <div
          className="card"
          style={{
            padding: "32px",
            backgroundColor: "var(--color-bg-surface)",
            border: "1px solid var(--color-border)",
          }}
        >
          <h2
            style={{
              fontFamily: "var(--font-primary-sans)",
              fontSize: "24px",
              margin: "0 0 24px 0",
              color: "var(--color-text-primary)",
              fontWeight: "500",
            }}
          >
            Your Position
          </h2>

          {walletAddress ? (
            <div>
              {/* User Shares */}
              <div style={{ marginBottom: "24px" }}>
                <div
                  style={{
                    fontFamily: "var(--font-tertiary-mono)",
                    fontSize: "12px",
                    color: "var(--color-text-tertiary)",
                    marginBottom: "8px",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    fontWeight: "bold",
                  }}
                >
                  TUX0 Shares
                </div>
                <div
                  style={{
                    fontFamily: "var(--font-primary-sans)",
                    fontSize: "24px",
                    color: "var(--color-text-primary)",
                    fontWeight: "500",
                  }}
                >
                  {userShares.toFixed(7)}
                </div>
              </div>

              {/* Position Value */}
              <div style={{ marginBottom: "24px" }}>
                <div
                  style={{
                    fontFamily: "var(--font-tertiary-mono)",
                    fontSize: "12px",
                    color: "var(--color-text-tertiary)",
                    marginBottom: "8px",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    fontWeight: "bold",
                  }}
                >
                  Current Value
                </div>
                <div
                  style={{
                    fontFamily: "var(--font-primary-sans)",
                    fontSize: "24px",
                    color: "var(--color-text-primary)",
                    fontWeight: "500",
                  }}
                >
                  ${userPositionValue.toFixed(2)}
                </div>
              </div>

              {/* Yield Earned */}
              <div
                className="card"
                style={{
                  padding: "20px",
                  backgroundColor: "var(--color-bg-primary)",
                  border: "1px solid var(--color-border)",
                }}
              >
                <div
                  style={{
                    fontFamily: "var(--font-tertiary-mono)",
                    fontSize: "12px",
                    color: "var(--color-text-tertiary)",
                    marginBottom: "8px",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    fontWeight: "bold",
                  }}
                >
                  Yield Earned
                </div>
                <div
                  style={{
                    fontFamily: "var(--font-primary-sans)",
                    fontSize: "20px",
                    color:
                      userYield >= 0
                        ? "var(--color-accent-green)"
                        : "var(--color-accent-red)",
                    fontWeight: "500",
                  }}
                >
                  ${userYield.toFixed(2)} ({userYieldPercent >= 0 ? "+" : ""}
                  {userYieldPercent.toFixed(2)}%)
                </div>
              </div>

              <p
                style={{
                  fontFamily: "var(--font-secondary-serif)",
                  fontSize: "14px",
                  color: "var(--color-text-secondary)",
                  fontStyle: "italic",
                  marginTop: "24px",
                  lineHeight: "1.6",
                }}
              >
                Your TUX0 shares automatically earn yield as the agent manages
                vault funds across Blend Capital pools. Share value increases
                as yield accumulates.
              </p>
            </div>
          ) : (
            <p
              style={{
                fontFamily: "var(--font-secondary-serif)",
                fontSize: "16px",
                color: "var(--color-text-secondary)",
                fontStyle: "italic",
                textAlign: "center",
                padding: "40px 20px",
              }}
            >
              Connect your wallet to view your vault position
            </p>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div
          style={{
            marginTop: "24px",
            padding: "16px",
            backgroundColor: "var(--color-accent-red)",
            color: "white",
            borderRadius: "4px",
            fontFamily: "var(--font-tertiary-mono)",
            fontSize: "14px",
          }}
        >
          Error: {error}
        </div>
      )}
    </div>
  );
};
