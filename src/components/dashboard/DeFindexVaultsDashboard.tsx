import React, { useState } from "react";
import { useChat } from "../../hooks/useChat";

/**
 * DeFindexVaultsDashboard - Dashboard for DeFindex vaults
 *
 * Features:
 * - Shows available DeFindex vaults on testnet
 * - AI-powered vault discovery
 * - Manual payment deposit instructions
 * - Real-time vault information
 */

interface Vault {
  name: string;
  address: string;
  apy: number;
  tvl: number;
  asset: string;
  strategy: string;
  risk_level: string;
}

export const DeFindexVaultsDashboard: React.FC = () => {
  const [selectedVault, setSelectedVault] = useState<Vault | null>(null);
  const [depositAmount, setDepositAmount] = useState<string>("5.0");
  const [userAddress, setUserAddress] = useState<string>("");
  const { message, sendMessage, loading } = useChat();

  // Mock vault data based on our working testnet vaults
  const vaults: Vault[] = [
    {
      name: "XLM HODL 1",
      address: "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA",
      apy: 0.0,
      tvl: 0,
      asset: "XLM",
      strategy: "HODL (hold XLM)",
      risk_level: "Medium"
    },
    {
      name: "XLM HODL 2",
      address: "CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE",
      apy: 0.0,
      tvl: 0,
      asset: "XLM",
      strategy: "HODL (hold XLM)",
      risk_level: "Medium"
    },
    {
      name: "XLM HODL 3",
      address: "CBLXUUHUL7TA3LF3U5G6ZTU7EACBBOSJLR4AYOM5YJKJ4APZ7O547R5T",
      apy: 0.0,
      tvl: 0,
      asset: "XLM",
      strategy: "HODL (hold XLM)",
      risk_level: "Medium"
    },
    {
      name: "XLM HODL 4",
      address: "CCGKL6U2DHSNFJ3NU4UPRUKYE2EUGYR4ZFZDYA7KDJLP3TKSPHD5C4UP",
      apy: 0.0,
      tvl: 0,
      asset: "XLM",
      strategy: "HODL (hold XLM)",
      risk_level: "Medium"
    }
  ];

  const handleDiscoverVaults = () => {
    const query = "Show me available DeFindex vaults on testnet with their current APY rates";
    sendMessage(query);
  };

  const handlePrepareDeposit = () => {
    if (!selectedVault || !userAddress) {
      alert("Please select a vault and enter your Stellar address");
      return;
    }

    const query = `I want to deposit ${depositAmount} XLM to vault ${selectedVault.address}. My address is ${userAddress}`;
    sendMessage(query);
  };

  const getRiskEmoji = (level: string) => {
    switch (level) {
      case "Low": return "🟢";
      case "Medium": return "🟡";
      case "High": return "🔴";
      default: return "⚪";
    }
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 8)}...${address.slice(-8)}`;
  };

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
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
          <div>
            <h1 style={{
              fontFamily: 'var(--font-primary-sans)',
              fontSize: '32px',
              margin: '0 0 8px 0',
              color: 'var(--color-text-primary)',
              fontWeight: '500'
            }}>
              DeFindex Vaults Dashboard
            </h1>
            <p style={{
              fontFamily: 'var(--font-secondary-serif)',
              fontSize: '16px',
              margin: '0',
              color: 'var(--color-text-secondary)',
              fontStyle: 'italic',
              lineHeight: '1.5'
            }}>
              Yield-generating vaults on Stellar Testnet powered by AI assistant
            </p>
          </div>

          <button
            className="btn-stellar"
            onClick={handleDiscoverVaults}
            disabled={loading}
            style={{
              fontSize: '12px',
              fontFamily: 'var(--font-tertiary-mono)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              padding: '12px 20px'
            }}
          >
            {loading ? "Discovering..." : "Discover Vaults"}
          </button>
        </div>

        {/* Summary Stats */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "20px",
            marginTop: "32px",
          }}
        >
          <div className="card" style={{
            padding: "24px",
            backgroundColor: "var(--color-bg-primary)",
            border: "1px solid var(--color-border)",
          }}>
            <div style={{
              fontFamily: 'var(--font-tertiary-mono)',
              fontSize: "12px",
              color: 'var(--color-text-tertiary)',
              marginBottom: "12px",
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontWeight: 'bold'
            }}>
              Available Vaults
            </div>
            <div style={{
              fontFamily: 'var(--font-primary-sans)',
              fontSize: '28px',
              fontWeight: '600',
              color: 'var(--color-text-primary)',
              margin: '0'
            }}>
              {vaults.length}
            </div>
          </div>

          <div className="card" style={{
            padding: "24px",
            backgroundColor: "var(--color-bg-primary)",
            border: "1px solid var(--color-border)",
          }}>
            <div style={{
              fontFamily: 'var(--font-tertiary-mono)',
              fontSize: "12px",
              color: 'var(--color-text-tertiary)',
              marginBottom: "12px",
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontWeight: 'bold'
            }}>
              Network
            </div>
            <div style={{
              fontFamily: 'var(--font-primary-sans)',
              fontSize: '28px',
              fontWeight: '600',
              color: 'var(--color-text-primary)',
              margin: '0'
            }}>
              🧪 Testnet
            </div>
          </div>

          <div className="card" style={{
            padding: "24px",
            backgroundColor: "var(--color-bg-primary)",
            border: "1px solid var(--color-border)",
          }}>
            <div style={{
              fontFamily: 'var(--font-tertiary-mono)',
              fontSize: "12px",
              color: 'var(--color-text-tertiary)',
              marginBottom: "12px",
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontWeight: 'bold'
            }}>
              Deposit Method
            </div>
            <div style={{
              fontFamily: 'var(--font-primary-sans)',
              fontSize: '20px',
              fontWeight: '600',
              color: 'var(--color-text-primary)',
              margin: '0'
            }}>
              Manual Payment ✅
            </div>
          </div>
        </div>
      </div>

      {/* Vault List */}
      <div style={{ marginBottom: "32px" }}>
        <h2 style={{
          fontFamily: 'var(--font-primary-sans)',
          fontSize: '24px',
          margin: '0 0 24px 0',
          color: 'var(--color-text-primary)',
          fontWeight: '500'
        }}>
          Available Vaults
        </h2>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
          gap: "20px"
        }}>
          {vaults.map((vault) => (
            <div
              key={vault.address}
              className="card"
              onClick={() => setSelectedVault(vault)}
              style={{
                padding: "24px",
                backgroundColor: "var(--color-bg-surface)",
                border: selectedVault?.address === vault.address
                  ? "2px solid var(--color-primary)"
                  : "1px solid var(--color-border)",
                cursor: "pointer",
                transition: "all 0.2s ease",
                transform: selectedVault?.address === vault.address ? "scale(1.02)" : "scale(1)"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "16px" }}>
                <div>
                  <h3 style={{
                    fontFamily: 'var(--font-primary-sans)',
                    fontSize: '18px',
                    margin: '0 0 4px 0',
                    color: 'var(--color-text-primary)',
                    fontWeight: '600'
                  }}>
                    {vault.name} {getRiskEmoji(vault.risk_level)}
                  </h3>
                  <p style={{
                    fontFamily: 'var(--font-secondary-serif)',
                    fontSize: '14px',
                    margin: '0',
                    color: 'var(--color-text-secondary)',
                    fontStyle: 'italic'
                  }}>
                    {vault.strategy}
                  </p>
                </div>
                <div style={{
                  fontSize: '20px',
                  fontWeight: 'bold',
                  color: 'var(--color-primary)'
                }}>
                  {vault.apy.toFixed(1)}%
                </div>
              </div>

              <div style={{
                fontFamily: 'var(--font-tertiary-mono)',
                fontSize: '12px',
                color: 'var(--color-text-tertiary)',
                marginBottom: '8px'
              }}>
                Address: {formatAddress(vault.address)}
              </div>

              <div style={{
                fontFamily: 'var(--font-tertiary-mono)',
                fontSize: '12px',
                color: 'var(--color-text-tertiary)',
                marginBottom: '16px'
              }}>
                TVL: ${vault.tvl.toLocaleString()} | Asset: {vault.asset}
              </div>

              <div style={{
                padding: '8px 12px',
                backgroundColor: 'var(--color-bg-primary)',
                borderRadius: '4px',
                fontSize: '11px',
                fontFamily: 'var(--font-tertiary-mono)',
                color: 'var(--color-text-secondary)',
                textAlign: 'center'
              }}>
                {selectedVault?.address === vault.address ? '✅ Selected' : 'Click to select'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Deposit Section */}
      {selectedVault && (
        <div
          className="card"
          style={{
            padding: "32px",
            backgroundColor: "var(--color-bg-surface)",
            border: "1px solid var(--color-border)",
          }}
        >
          <h2 style={{
            fontFamily: 'var(--font-primary-sans)',
            fontSize: '24px',
            margin: '0 0 24px 0',
            color: 'var(--color-text-primary)',
            fontWeight: '500'
          }}>
            Deposit to {selectedVault.name}
          </h2>

          <div style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "24px",
            marginBottom: "24px"
          }}>
            <div>
              <label style={{
                display: "block",
                fontFamily: 'var(--font-tertiary-mono)',
                fontSize: '12px',
                color: 'var(--color-text-tertiary)',
                marginBottom: '8px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontWeight: 'bold'
              }}>
                Deposit Amount (XLM)
              </label>
              <input
                type="number"
                value={depositAmount}
                onChange={(e) => setDepositAmount(e.target.value)}
                step="0.1"
                min="0.1"
                style={{
                  width: "100%",
                  padding: "12px",
                  fontFamily: 'var(--font-primary-sans)',
                  fontSize: '16px',
                  border: "1px solid var(--color-border)",
                  borderRadius: "4px",
                  backgroundColor: "var(--color-bg-primary)",
                  color: 'var(--color-text-primary)'
                }}
              />
            </div>

            <div>
              <label style={{
                display: "block",
                fontFamily: 'var(--font-tertiary-mono)',
                fontSize: '12px',
                color: 'var(--color-text-tertiary)',
                marginBottom: '8px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontWeight: 'bold'
              }}>
                Your Stellar Address
              </label>
              <input
                type="text"
                value={userAddress}
                onChange={(e) => setUserAddress(e.target.value)}
                placeholder="G..."
                style={{
                  width: "100%",
                  padding: "12px",
                  fontFamily: 'var(--font-tertiary-mono)',
                  fontSize: '14px',
                  border: "1px solid var(--color-border)",
                  borderRadius: "4px",
                  backgroundColor: "var(--color-bg-primary)",
                  color: 'var(--color-text-primary)'
                }}
              />
            </div>
          </div>

          <button
            className="btn-stellar"
            onClick={handlePrepareDeposit}
            disabled={loading || !userAddress}
            style={{
              fontSize: '14px',
              fontFamily: 'var(--font-primary-sans)',
              fontWeight: '600',
              padding: '16px 32px'
            }}
          >
            {loading ? "Preparing..." : "Get Deposit Instructions"}
          </button>

          <div style={{
            marginTop: '16px',
            padding: '16px',
            backgroundColor: 'var(--color-bg-primary)',
            borderRadius: '4px',
            fontSize: '13px',
            fontFamily: 'var(--font-secondary-serif)',
            color: 'var(--color-text-secondary)',
            lineHeight: '1.5'
          }}>
            <strong>💡 How it works:</strong> The AI assistant will provide manual payment instructions.
            You'll send XLM directly to the vault contract address, and it will automatically recognize
            the payment as a deposit. No API dependencies - just pure Stellar blockchain transactions!
          </div>
        </div>
      )}

      {/* AI Response */}
      {message && (
        <div
          className="card"
          style={{
            marginTop: "32px",
            padding: "24px",
            backgroundColor: "var(--color-bg-surface)",
            border: "1px solid var(--color-border)",
          }}
        >
          <h3 style={{
            fontFamily: 'var(--font-primary-sans)',
            fontSize: '18px',
            margin: '0 0 16px 0',
            color: 'var(--color-text-primary)',
            fontWeight: '600'
          }}>
            🤖 AI Assistant Response
          </h3>
          <div style={{
            fontFamily: 'var(--font-secondary-serif)',
            fontSize: '15px',
            lineHeight: '1.6',
            color: 'var(--color-text-primary)',
            whiteSpace: 'pre-wrap'
          }}>
            {message}
          </div>
        </div>
      )}
    </div>
  );
};