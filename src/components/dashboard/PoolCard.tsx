import React, { useState } from "react";
import { Card, Text, Button } from "@stellar/design-system";
import { BlendPoolData } from "../../types/blend";
import { ReserveRow } from "./ReserveRow";
import { shortenContractId } from "../../util/contract";

interface PoolCardProps {
  pool: BlendPoolData;
}

/**
 * PoolCard - Displays a single Blend pool with all its reserves
 *
 * Shows:
 * - Pool name and status
 * - Contract address
 * - Number of reserves
 * - All reserve details (via ReserveRow)
 */
export const PoolCard: React.FC<PoolCardProps> = ({ pool }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(pool.id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Get status badge color
  const statusColor =
    pool.status === "active" ? "#2e7d32" : pool.status === "paused" ? "#f57c00" : "#666";

  // Calculate total supplied and borrowed across all reserves
  const totalSupplied = pool.reserves.reduce(
    (sum, r) => sum + r.totalSupplied,
    BigInt(0)
  );
  const totalBorrowed = pool.reserves.reduce(
    (sum, r) => sum + r.totalBorrowed,
    BigInt(0)
  );

  return (
    <div
      style={{
        marginBottom: "24px",
        padding: "0",
        overflow: "hidden",
        border: "1px solid #e5e7eb",
        borderRadius: "8px",
      }}
    >
      <Card>
      {/* Pool Header */}
      <div
        style={{
          padding: "20px 24px",
          borderBottom: "2px solid #f5f5f5",
          background: "linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <Text as="h3" size="lg" style={{ margin: 0, fontWeight: "700" }}>
                {pool.name}
              </Text>
              <span
                style={{
                  display: "inline-block",
                  padding: "4px 10px",
                  borderRadius: "12px",
                  backgroundColor: statusColor,
                  color: "white",
                  fontSize: "11px",
                  fontWeight: "600",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                }}
              >
                {pool.status}
              </span>
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginTop: "8px",
              }}
            >
              <code
                style={{
                  fontSize: "12px",
                  color: "#666",
                  fontFamily: "monospace",
                  backgroundColor: "#f5f5f5",
                  padding: "4px 8px",
                  borderRadius: "4px",
                }}
                title={pool.id}
              >
                {shortenContractId(pool.id, 8, 6)}
              </code>
              <Button
                variant="tertiary"
                size="sm"
                onClick={handleCopy}
                style={{ padding: "2px 8px", fontSize: "11px" }}
              >
                {copied ? "✓ Copied" : "Copy"}
              </Button>
            </div>
          </div>

          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "13px", color: "#666", marginBottom: "4px" }}>
              Total Reserves
            </div>
            <div style={{ fontSize: "28px", fontWeight: "700", color: "#333" }}>
              {pool.totalReserves}
            </div>
            <div style={{ fontSize: "12px", color: "#888", marginTop: "2px" }}>
              {pool.totalReserves === 1 ? "Asset" : "Assets"}
            </div>
          </div>
        </div>

        {/* Pool Stats Summary */}
        {pool.reserves.length > 0 && (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: "16px",
              marginTop: "20px",
              padding: "16px",
              backgroundColor: "#ffffff",
              borderRadius: "8px",
              border: "1px solid #e0e0e0",
            }}
          >
            <div>
              <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
                Total Supplied
              </div>
              <div style={{ fontSize: "18px", fontWeight: "600", color: "#2e7d32" }}>
                {Number(totalSupplied).toLocaleString()} units
              </div>
            </div>
            <div>
              <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
                Total Borrowed
              </div>
              <div style={{ fontSize: "18px", fontWeight: "600", color: "#d32f2f" }}>
                {Number(totalBorrowed).toLocaleString()} units
              </div>
            </div>
            <div>
              <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
                Net Available
              </div>
              <div style={{ fontSize: "18px", fontWeight: "600", color: "#1976d2" }}>
                {Number(totalSupplied - totalBorrowed).toLocaleString()} units
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Toggle Button */}
      <div
        style={{
          padding: "12px 24px",
          backgroundColor: "#f8f9fa",
          borderBottom: isExpanded ? "1px solid #e0e0e0" : "none",
        }}
      >
        <Button
          variant="tertiary"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          style={{ width: "100%", justifyContent: "space-between" }}
        >
          <span style={{ fontWeight: "600" }}>
            {isExpanded ? "Hide" : "Show"} Reserve Details
          </span>
          <span style={{ fontSize: "16px" }}>{isExpanded ? "▲" : "▼"}</span>
        </Button>
      </div>

      {/* Reserves List */}
      {isExpanded && (
        <div>
          {pool.reserves.length === 0 ? (
            <div
              style={{
                padding: "40px 24px",
                textAlign: "center",
                color: "#999",
              }}
            >
              <Text as="p" size="sm">
                No reserves found in this pool
              </Text>
            </div>
          ) : (
            <>
              {/* Column Headers */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr 1fr 2fr 1.5fr",
                  gap: "12px",
                  padding: "12px 16px",
                  backgroundColor: "#f8f9fa",
                  borderBottom: "2px solid #e0e0e0",
                  fontSize: "12px",
                  fontWeight: "600",
                  color: "#666",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                }}
              >
                <div>Asset</div>
                <div style={{ textAlign: "center" }}>Supply APY</div>
                <div style={{ textAlign: "center" }}>Borrow APY</div>
                <div>Utilization</div>
                <div style={{ textAlign: "right" }}>Available</div>
              </div>

              {/* Reserve Rows */}
              {pool.reserves.map((reserve) => (
                <ReserveRow key={reserve.assetId} reserve={reserve} />
              ))}
            </>
          )}
        </div>
      )}

      {/* Footer */}
      <div
        style={{
          padding: "12px 24px",
          backgroundColor: "#f8f9fa",
          borderTop: "1px solid #e0e0e0",
          fontSize: "11px",
          color: "#999",
          textAlign: "center",
        }}
      >
        Last updated: {new Date(pool.timestamp).toLocaleString()}
      </div>
      </Card>
    </div>
  );
};
