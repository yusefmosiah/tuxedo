import React, { useState } from "react";
import { Button, Card, Text, Loader } from "@stellar/design-system";
import { BLEND_CONTRACTS } from "../contracts/blend";
import { shortenContractId } from "../util/contract";
import { useBlendPool } from "../hooks/useBlendPool";

/**
 * BlendPoolViewer - Example component for interacting with Blend Protocol
 *
 * This component demonstrates:
 * 1. Displaying Blend contract addresses
 * 2. How to query pool information (read-only)
 * 3. Structure for write operations (supply, borrow, etc.)
 *
 * Note: To interact with Blend contracts, you'll need to:
 * - Generate TypeScript bindings using stellar CLI
 * - Or use the Blend SDK (@blend-capital/blend-sdk)
 * - Or manually construct contract calls using stellar-sdk
 */
export const BlendPoolViewer: React.FC = () => {
  const [selectedPool] = useState(BLEND_CONTRACTS.cometPool);
  const poolData = useBlendPool(selectedPool);

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
      <Text as="h2" size="lg">
        Blend Protocol - Testnet
      </Text>

      <div style={{ marginTop: "20px", padding: "20px" }}>
        <Card>
          <Text as="h3" size="md">
            Core Contracts
          </Text>
          <div style={{ marginTop: "10px" }}>
            <ContractRow
              name="Pool Factory"
              address={BLEND_CONTRACTS.poolFactory}
            />
            <ContractRow name="Backstop" address={BLEND_CONTRACTS.backstop} />
            <ContractRow name="Emitter" address={BLEND_CONTRACTS.emitter} />
          </div>
        </Card>
      </div>

      <div style={{ marginTop: "20px", padding: "20px" }}>
        <Card>
          <Text as="h3" size="md">
            Tokens
          </Text>
          <div style={{ marginTop: "10px" }}>
            <ContractRow
              name="BLND Token"
              address={BLEND_CONTRACTS.blndToken}
            />
            <ContractRow
              name="USDC Token"
              address={BLEND_CONTRACTS.usdcToken}
            />
            <ContractRow name="XLM Token" address={BLEND_CONTRACTS.xlmToken} />
          </div>
        </Card>
      </div>

      <div style={{ marginTop: "20px", padding: "20px" }}>
        <Card>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Text as="h3" size="md">
              Comet Pool (BLND:USDC)
            </Text>
            {poolData.loading && (
              <div
                style={{ display: "flex", alignItems: "center", gap: "8px" }}
              >
                <Loader size="sm" />
                <Text as="span" size="sm" style={{ color: "#666" }}>
                  Connecting...
                </Text>
              </div>
            )}
            {poolData.error && (
              <Text as="span" size="sm" style={{ color: "#d32f2f" }}>
                Connection failed
              </Text>
            )}
            {!poolData.loading && !poolData.error && (
              <Text as="span" size="sm" style={{ color: "#2e7d32" }}>
                ✓ Connected to Testnet
              </Text>
            )}
          </div>

          <ContractRow
            name="Pool Address"
            address={BLEND_CONTRACTS.cometPool}
          />

          <div style={{ marginTop: "20px" }}>
            <Text as="p" size="sm">
              To interact with this pool, you can:
            </Text>
            <ul style={{ fontSize: "14px", lineHeight: "1.6" }}>
              <li>
                <strong>View pool data:</strong> Query reserves, rates, and
                positions
              </li>
              <li>
                <strong>Supply assets:</strong> Deposit USDC or other supported
                tokens
              </li>
              <li>
                <strong>Borrow:</strong> Take loans against your collateral
              </li>
              <li>
                <strong>Manage positions:</strong> Withdraw, repay, or liquidate
              </li>
            </ul>
          </div>

          <div
            style={{
              marginTop: "20px",
              padding: "15px",
              backgroundColor: "#f5f5f5",
              borderRadius: "8px",
            }}
          >
            <Text as="p" size="sm" style={{ fontWeight: "bold" }}>
              Next Steps:
            </Text>
            <ol
              style={{ fontSize: "14px", lineHeight: "1.8", marginTop: "10px" }}
            >
              <li>
                Install Blend SDK:{" "}
                <code style={{ background: "#e0e0e0", padding: "2px 6px" }}>
                  npm install @blend-capital/blend-sdk
                </code>
              </li>
              <li>Or generate TypeScript bindings using Stellar CLI</li>
              <li>Connect your wallet using the WalletProvider</li>
              <li>Fund your testnet account using Friendbot</li>
              <li>Build transactions to interact with the pool contracts</li>
            </ol>
          </div>

          <Button
            variant="tertiary"
            size="md"
            style={{ marginTop: "15px" }}
            onClick={() => {
              window.open(
                "https://docs.blend.capital/tech-docs/integrations/integrate-pool",
                "_blank",
              );
            }}
          >
            View Blend Integration Docs
          </Button>
        </Card>
      </div>
    </div>
  );
};

const ContractRow: React.FC<{ name: string; address: string }> = ({
  name,
  address,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "10px 0",
        borderBottom: "1px solid #eee",
      }}
    >
      <div>
        <Text as="span" size="sm" style={{ fontWeight: "500" }}>
          {name}
        </Text>
        <br />
        <code
          style={{
            fontSize: "12px",
            color: "#666",
            fontFamily: "monospace",
          }}
          title={address}
        >
          {shortenContractId(address, 8, 6)}
        </code>
      </div>
      <Button variant="tertiary" size="sm" onClick={handleCopy}>
        {copied ? "Copied!" : "Copy"}
      </Button>
    </div>
  );
};
