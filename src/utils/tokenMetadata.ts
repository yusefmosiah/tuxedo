import { TokenMetadata } from "../types/blend";
import { BLEND_CONTRACTS } from "../contracts/blend";

/**
 * Token metadata cache
 * Maps contract address to token metadata
 */
const TOKEN_METADATA: Record<string, TokenMetadata> = {
  // Known testnet tokens
  [BLEND_CONTRACTS.blndToken]: {
    address: BLEND_CONTRACTS.blndToken,
    symbol: "BLND",
    name: "Blend Token",
    decimals: 7,
  },
  [BLEND_CONTRACTS.usdcToken]: {
    address: BLEND_CONTRACTS.usdcToken,
    symbol: "USDC",
    name: "USD Coin",
    decimals: 7,
  },
  [BLEND_CONTRACTS.xlmToken]: {
    address: BLEND_CONTRACTS.xlmToken,
    symbol: "XLM",
    name: "Stellar Lumens",
    decimals: 7,
  },
};

/**
 * Get token metadata by contract address
 * Returns metadata if found, otherwise returns a default with shortened address
 */
export function getTokenMetadata(address: string): TokenMetadata {
  // Check cache first
  if (TOKEN_METADATA[address]) {
    return TOKEN_METADATA[address];
  }

  // Return default metadata for unknown tokens
  return {
    address,
    symbol: `${address.slice(0, 4)}...${address.slice(-4)}`,
    name: "Unknown Token",
    decimals: 7, // Default to 7 decimals (Stellar standard)
  };
}

/**
 * Add or update token metadata in the cache
 */
export function setTokenMetadata(metadata: TokenMetadata): void {
  TOKEN_METADATA[metadata.address] = metadata;
}

/**
 * Format token amount using decimals
 */
export function formatTokenAmount(
  amount: bigint,
  decimals: number = 7,
  maxDecimals: number = 2
): string {
  const divisor = BigInt(10 ** decimals);
  const whole = amount / divisor;
  const fraction = amount % divisor;

  if (fraction === BigInt(0)) {
    return whole.toString();
  }

  // Convert fraction to decimal string
  const fractionStr = fraction.toString().padStart(decimals, "0");
  const trimmedFraction = fractionStr.slice(0, maxDecimals);

  return `${whole}.${trimmedFraction}`;
}

/**
 * Format large numbers with K, M, B suffixes
 */
export function formatCompactNumber(value: number | bigint): string {
  const num = typeof value === "bigint" ? Number(value) : value;

  if (num >= 1_000_000_000) {
    return `${(num / 1_000_000_000).toFixed(2)}B`;
  }
  if (num >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(2)}M`;
  }
  if (num >= 1_000) {
    return `${(num / 1_000).toFixed(2)}K`;
  }

  return num.toFixed(2);
}

/**
 * Format APY percentage
 */
export function formatApy(apy: number): string {
  return `${(apy * 100).toFixed(2)}%`;
}

/**
 * Format utilization percentage
 */
export function formatUtilization(utilization: number): string {
  return `${(utilization * 100).toFixed(1)}%`;
}

/**
 * Get color for APY value (for UI)
 */
export function getApyColor(apy: number, type: "supply" | "borrow"): string {
  if (type === "supply") {
    // Green shades for supply APY
    if (apy > 0.1) return "#2e7d32"; // High APY - dark green
    if (apy > 0.05) return "#43a047"; // Medium APY - green
    return "#66bb6a"; // Low APY - light green
  } else {
    // Orange/red shades for borrow APY
    if (apy > 0.15) return "#d32f2f"; // High APY - red
    if (apy > 0.08) return "#f57c00"; // Medium APY - orange
    return "#ff9800"; // Low APY - light orange
  }
}

/**
 * Get color for utilization (for progress bars)
 */
export function getUtilizationColor(utilization: number): string {
  if (utilization > 0.9) return "#d32f2f"; // Critical - red
  if (utilization > 0.75) return "#f57c00"; // High - orange
  if (utilization > 0.5) return "#fbc02d"; // Medium - yellow
  return "#43a047"; // Low - green
}
