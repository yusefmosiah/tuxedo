import React from "react";
import { Button, Text, Loader } from "@stellar/design-system";
import { useBlendPools } from "../../hooks/useBlendPools";
import { PoolCard } from "./PoolCard";

/**
 * PoolsDashboard - Main dashboard component showing all Blend pools
 *
 * Features:
 * - Displays all active pools on the network
 * - Shows loading state while fetching
 * - Error handling with retry
 * - Refresh capability
 * - Summary statistics
 */
export const PoolsDashboard: React.FC = () => {
  const { pools, loading, error, refetch } = useBlendPools();

  // Calculate aggregate stats
  const totalPools = pools.length;
  const totalReserves = pools.reduce((sum, pool) => sum + pool.totalReserves, 0);
  const activePools = pools.filter((p) => p.status === "active").length;

  return (
    <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "20px" }}>
      {/* Dashboard Header */}
      <div
        style={{
          marginBottom: "32px",
          padding: "32px",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          borderRadius: "16px",
          color: "white",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
          <div>
            <Text
              as="h1"
              size="xl"
              style={{ margin: 0, marginBottom: "8px", color: "white", fontWeight: "800" }}
            >
              Blend Pools Dashboard
            </Text>
            <Text as="p" size="md" style={{ margin: 0, opacity: 0.9, color: "white" }}>
              Real-time statistics for all Blend lending pools on Stellar Testnet
            </Text>
          </div>

          <Button
            variant="secondary"
            size="md"
            onClick={refetch}
            disabled={loading}
            style={{
              backgroundColor: "rgba(255, 255, 255, 0.2)",
              color: "white",
              border: "1px solid rgba(255, 255, 255, 0.3)",
            }}
          >
            {loading ? "Refreshing..." : "🔄 Refresh"}
          </Button>
        </div>

        {/* Summary Stats */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "20px",
            marginTop: "24px",
          }}
        >
          <div
            style={{
              padding: "20px",
              backgroundColor: "rgba(255, 255, 255, 0.15)",
              borderRadius: "12px",
              backdropFilter: "blur(10px)",
            }}
          >
            <div style={{ fontSize: "14px", opacity: 0.9, marginBottom: "8px" }}>
              Total Pools
            </div>
            <div style={{ fontSize: "36px", fontWeight: "800" }}>{totalPools}</div>
            <div style={{ fontSize: "12px", opacity: 0.8, marginTop: "4px" }}>
              {activePools} active
            </div>
          </div>

          <div
            style={{
              padding: "20px",
              backgroundColor: "rgba(255, 255, 255, 0.15)",
              borderRadius: "12px",
              backdropFilter: "blur(10px)",
            }}
          >
            <div style={{ fontSize: "14px", opacity: 0.9, marginBottom: "8px" }}>
              Total Reserves
            </div>
            <div style={{ fontSize: "36px", fontWeight: "800" }}>{totalReserves}</div>
            <div style={{ fontSize: "12px", opacity: 0.8, marginTop: "4px" }}>
              Across all pools
            </div>
          </div>

          <div
            style={{
              padding: "20px",
              backgroundColor: "rgba(255, 255, 255, 0.15)",
              borderRadius: "12px",
              backdropFilter: "blur(10px)",
            }}
          >
            <div style={{ fontSize: "14px", opacity: 0.9, marginBottom: "8px" }}>Network</div>
            <div style={{ fontSize: "36px", fontWeight: "800" }}>Testnet</div>
            <div style={{ fontSize: "12px", opacity: 0.8, marginTop: "4px" }}>Stellar</div>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && pools.length === 0 && (
        <div
          style={{
            padding: "80px 20px",
            textAlign: "center",
            backgroundColor: "#f8f9fa",
            borderRadius: "12px",
          }}
        >
          <Loader size="lg" />
          <Text as="p" size="md" style={{ marginTop: "20px", color: "#666" }}>
            Loading pools from the network...
          </Text>
          <Text as="p" size="sm" style={{ marginTop: "8px", color: "#999" }}>
            This may take a few seconds
          </Text>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            backgroundColor: "#fff3f3",
            border: "2px solid #ffcdd2",
            borderRadius: "12px",
          }}
        >
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>⚠️</div>
          <Text as="h3" size="lg" style={{ color: "#d32f2f", marginBottom: "12px" }}>
            Failed to Load Pools
          </Text>
          <Text as="p" size="md" style={{ color: "#666", marginBottom: "20px" }}>
            {error}
          </Text>
          <Button variant="primary" size="md" onClick={refetch}>
            Try Again
          </Button>
        </div>
      )}

      {/* Pools List */}
      {!error && pools.length > 0 && (
        <div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "20px",
            }}
          >
            <Text as="h2" size="lg" style={{ margin: 0, fontWeight: "700" }}>
              Active Pools ({pools.length})
            </Text>
          </div>

          {pools.map((pool) => (
            <PoolCard key={pool.id} pool={pool} />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && pools.length === 0 && (
        <div
          style={{
            padding: "80px 20px",
            textAlign: "center",
            backgroundColor: "#f8f9fa",
            borderRadius: "12px",
          }}
        >
          <div style={{ fontSize: "64px", marginBottom: "16px" }}>🏊</div>
          <Text as="h3" size="lg" style={{ marginBottom: "12px" }}>
            No Pools Found
          </Text>
          <Text as="p" size="md" style={{ color: "#666" }}>
            There are no active pools on this network yet.
          </Text>
        </div>
      )}
    </div>
  );
};
