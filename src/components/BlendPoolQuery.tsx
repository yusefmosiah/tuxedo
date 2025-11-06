import React, { useState } from "react";
import { Button, Card, Text } from "@stellar/design-system";
import { BLEND_CONTRACTS } from "../contracts/blend";

/**
 * BlendPoolQuery - Interactive component for querying Blend pool data
 *
 * Demonstrates how to:
 * 1. Query pool positions
 * 2. Get reserve data
 * 3. Check user positions
 */
export const BlendPoolQuery: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string>("");
  const [queryType, setQueryType] = useState<
    "pool_config" | "positions" | "user_positions"
  >("pool_config");

  const handleQuery = async () => {
    setLoading(true);
    setResult("");

    try {
      // Example queries - these would need proper implementation with:
      // 1. An Account object for simulation
      // 2. RPC server connection
      // 3. Proper error handling

      const queryResults = {
        pool_config: `Pool Address: ${BLEND_CONTRACTS.cometPool}\nNetwork: Testnet\n\nTo query pool config, you need to:\n1. Create an Account object\n2. Call pool methods using stellar-sdk\n3. Parse XDR results`,
        positions: `Pool Reserves Query\n\nAvailable methods:\n- get_positions()\n- get_pool_config()\n- get_reserve_data()\n\nConnect a wallet to query your positions.`,
        user_positions: "Connect your wallet to query user positions.",
      };

      setResult(queryResults[queryType]);
    } catch (error) {
      setResult(
        `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: "20px", padding: "20px" }}>
      <Card>
        <Text as="h3" size="md">
          Interactive Pool Query
        </Text>

        <div style={{ marginTop: "15px" }}>
          <Text as="p" size="sm" style={{ marginBottom: "10px" }}>
            Select query type:
          </Text>
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            <Button
              variant={queryType === "pool_config" ? "primary" : "tertiary"}
              size="sm"
              onClick={() => setQueryType("pool_config")}
            >
              Pool Config
            </Button>
            <Button
              variant={queryType === "positions" ? "primary" : "tertiary"}
              size="sm"
              onClick={() => setQueryType("positions")}
            >
              Pool Positions
            </Button>
            <Button
              variant={queryType === "user_positions" ? "primary" : "tertiary"}
              size="sm"
              onClick={() => setQueryType("user_positions")}
              disabled={true}
            >
              My Positions (Connect Wallet)
            </Button>
          </div>
        </div>

        <Button
          variant="secondary"
          size="md"
          onClick={handleQuery}
          disabled={loading}
          style={{ marginTop: "15px" }}
        >
          {loading ? "Querying..." : "Query Pool"}
        </Button>

        {result && (
          <div
            style={{
              marginTop: "15px",
              padding: "15px",
              backgroundColor: "#f5f5f5",
              borderRadius: "8px",
              fontFamily: "monospace",
              fontSize: "13px",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {result}
          </div>
        )}

        <div
          style={{
            marginTop: "20px",
            padding: "15px",
            backgroundColor: "#e3f2fd",
            borderRadius: "8px",
          }}
        >
          <Text as="p" size="sm" style={{ fontWeight: "bold" }}>
            💡 Implementation Guide
          </Text>
          <div
            style={{ fontSize: "13px", lineHeight: "1.6", marginTop: "8px" }}
          >
            <p>To query real pool data, you need to:</p>
            <ol style={{ marginLeft: "20px", marginTop: "8px" }}>
              <li>
                Create a <code>SorobanRpc.Server</code> instance with the RPC
                URL
              </li>
              <li>
                Build a transaction with the contract method call (e.g.,{" "}
                <code>pool.get_positions()</code>)
              </li>
              <li>
                Use <code>server.simulateTransaction()</code> to execute
                read-only queries
              </li>
              <li>Parse the XDR result to get the data</li>
            </ol>
            <p style={{ marginTop: "10px" }}>
              Example code is in <code>src/hooks/useBlendPool.ts</code>
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
