import React from "react";
import { Text } from "@stellar/design-system";
import { PoolReserve } from "../../types/blend";
import {
  getTokenMetadata,
  formatApy,
  formatUtilization,
  formatTokenAmount,
  getApyColor,
  getUtilizationColor,
} from "../../utils/tokenMetadata";

interface ReserveRowProps {
  reserve: PoolReserve;
}

/**
 * ReserveRow - Displays a single asset's information in a pool
 *
 * Shows:
 * - Asset symbol
 * - Supply APY (green)
 * - Borrow APY (orange/red)
 * - Utilization bar
 * - Available liquidity
 */
export const ReserveRow: React.FC<ReserveRowProps> = ({ reserve }) => {
  const token = getTokenMetadata(reserve.assetId);
  const utilColor = getUtilizationColor(reserve.utilization);
  const supplyColor = getApyColor(reserve.estSupplyApy, "supply");
  const borrowColor = getApyColor(reserve.estBorrowApy, "borrow");

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr 2fr 1.5fr",
        gap: "12px",
        alignItems: "center",
        padding: "12px 16px",
        borderBottom: "1px solid #e0e0e0",
        fontSize: "14px",
      }}
    >
      {/* Asset Symbol */}
      <div style={{ fontWeight: "600", display: "flex", alignItems: "center", gap: "8px" }}>
        <div
          style={{
            width: "32px",
            height: "32px",
            borderRadius: "50%",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontSize: "12px",
            fontWeight: "bold",
          }}
        >
          {token.symbol.slice(0, 2)}
        </div>
        <div>
          <div>{token.symbol}</div>
          <div style={{ fontSize: "11px", color: "#666", fontWeight: "normal" }}>
            {token.name}
          </div>
        </div>
      </div>

      {/* Supply APY */}
      <div style={{ textAlign: "center" }}>
        <Text
          as="span"
          size="sm"
          style={{ color: supplyColor, fontWeight: "600", fontSize: "15px" }}
        >
          {formatApy(reserve.estSupplyApy)}
        </Text>
        <div style={{ fontSize: "11px", color: "#888", marginTop: "2px" }}>Supply</div>
      </div>

      {/* Borrow APY */}
      <div style={{ textAlign: "center" }}>
        <Text
          as="span"
          size="sm"
          style={{ color: borrowColor, fontWeight: "600", fontSize: "15px" }}
        >
          {formatApy(reserve.estBorrowApy)}
        </Text>
        <div style={{ fontSize: "11px", color: "#888", marginTop: "2px" }}>Borrow</div>
      </div>

      {/* Utilization Bar */}
      <div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "4px",
            fontSize: "12px",
          }}
        >
          <span style={{ color: "#666" }}>Utilization</span>
          <span style={{ fontWeight: "600", color: utilColor }}>
            {formatUtilization(reserve.utilization)}
          </span>
        </div>
        <div
          style={{
            width: "100%",
            height: "8px",
            backgroundColor: "#e0e0e0",
            borderRadius: "4px",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${Math.min(reserve.utilization * 100, 100)}%`,
              height: "100%",
              backgroundColor: utilColor,
              transition: "width 0.3s ease",
            }}
          />
        </div>
      </div>

      {/* Available Liquidity */}
      <div style={{ textAlign: "right" }}>
        <div style={{ fontWeight: "600", fontSize: "14px" }}>
          {formatTokenAmount(reserve.availableLiquidity, token.decimals, 2)}
        </div>
        <div style={{ fontSize: "11px", color: "#888", marginTop: "2px" }}>Available</div>
      </div>
    </div>
  );
};
