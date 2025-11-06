import React from "react";
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
  const totalReserves = pools.reduce(
    (sum, pool) => sum + pool.totalReserves,
    0,
  );
  const activePools = pools.filter((p) => p.status === "active").length;

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
              Blend Pools Dashboard
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
              Real-time statistics for all Blend lending pools on Stellar
              Testnet
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

        {/* Summary Stats */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "20px",
            marginTop: "32px",
          }}
        >
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
              Total Pools
            </div>
            <div
              style={{
                fontFamily: "var(--font-primary-sans)",
                fontSize: "36px",
                color: "var(--color-text-primary)",
                fontWeight: "bold",
                marginBottom: "8px",
              }}
            >
              {totalPools}
            </div>
            <div
              style={{
                fontFamily: "var(--font-secondary-serif)",
                fontSize: "14px",
                color: "var(--color-text-secondary)",
                fontStyle: "italic",
              }}
            >
              {activePools} active
            </div>
          </div>

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
              Total Reserves
            </div>
            <div
              style={{
                fontFamily: "var(--font-primary-sans)",
                fontSize: "36px",
                color: "var(--color-text-primary)",
                fontWeight: "bold",
                marginBottom: "8px",
              }}
            >
              {totalReserves}
            </div>
            <div
              style={{
                fontFamily: "var(--font-secondary-serif)",
                fontSize: "14px",
                color: "var(--color-text-secondary)",
                fontStyle: "italic",
              }}
            >
              Across all pools
            </div>
          </div>

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
              Network
            </div>
            <div
              style={{
                fontFamily: "var(--font-primary-sans)",
                fontSize: "36px",
                color: "var(--color-text-primary)",
                fontWeight: "bold",
                marginBottom: "8px",
              }}
            >
              Testnet
            </div>
            <div
              style={{
                fontFamily: "var(--font-secondary-serif)",
                fontSize: "14px",
                color: "var(--color-text-secondary)",
                fontStyle: "italic",
              }}
            >
              Stellar
            </div>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && pools.length === 0 && (
        <div
          className="card"
          style={{
            padding: "80px 20px",
            textAlign: "center",
            backgroundColor: "var(--color-bg-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--border-radius-lg)",
          }}
        >
          <div
            style={{
              fontSize: "48px",
              marginBottom: "20px",
              color: "var(--color-stellar-glow-strong)",
            }}
          >
            ⏳
          </div>
          <p
            style={{
              fontFamily: "var(--font-primary-sans)",
              fontSize: "18px",
              margin: "0 0 8px 0",
              color: "var(--color-text-primary)",
            }}
          >
            Loading pools from the network...
          </p>
          <p
            style={{
              fontFamily: "var(--font-secondary-serif)",
              fontSize: "14px",
              color: "var(--color-text-secondary)",
              fontStyle: "italic",
              margin: "0",
            }}
          >
            This may take a few seconds
          </p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div
          className="card"
          style={{
            padding: "40px",
            textAlign: "center",
            backgroundColor: "rgba(239, 68, 68, 0.1)",
            border: "1px solid var(--color-negative)",
            borderRadius: "var(--border-radius-lg)",
          }}
        >
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>⚠️</div>
          <h3
            style={{
              fontFamily: "var(--font-primary-sans)",
              fontSize: "24px",
              color: "var(--color-negative)",
              margin: "0 0 12px 0",
              fontWeight: "bold",
            }}
          >
            Failed to Load Pools
          </h3>
          <p
            style={{
              fontFamily: "var(--font-secondary-serif)",
              fontSize: "16px",
              color: "var(--color-text-secondary)",
              fontStyle: "italic",
              margin: "0 0 20px 0",
            }}
          >
            {error}
          </p>
          <button
            className="btn-stellar"
            onClick={refetch}
            style={{
              fontSize: "12px",
              fontFamily: "var(--font-tertiary-mono)",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              padding: "12px 20px",
            }}
          >
            Try Again
          </button>
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
              marginBottom: "24px",
            }}
          >
            <h2
              style={{
                fontFamily: "var(--font-primary-serif)",
                fontSize: "24px",
                margin: "0",
                color: "var(--color-text-primary)",
                fontWeight: "bold",
              }}
            >
              Active Pools ({pools.length})
            </h2>
          </div>

          {pools.map((pool) => (
            <PoolCard key={pool.id} pool={pool} />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && pools.length === 0 && (
        <div
          className="card"
          style={{
            padding: "80px 20px",
            textAlign: "center",
            backgroundColor: "var(--color-bg-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--border-radius-lg)",
          }}
        >
          <div
            style={{
              fontSize: "64px",
              marginBottom: "16px",
              color: "var(--color-stellar-glow-strong)",
            }}
          >
            🏊
          </div>
          <h3
            style={{
              fontFamily: "var(--font-primary-serif)",
              fontSize: "24px",
              margin: "0 0 12px 0",
              color: "var(--color-text-primary)",
              fontWeight: "bold",
            }}
          >
            No Pools Found
          </h3>
          <p
            style={{
              fontFamily: "var(--font-secondary-sans)",
              fontSize: "16px",
              color: "var(--color-text-secondary)",
              fontStyle: "italic",
              margin: "0",
            }}
          >
            There are no active pools on this network yet.
          </p>
        </div>
      )}
    </div>
  );
};

export default PoolsDashboard;
