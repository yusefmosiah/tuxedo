/**
 * TypeScript interfaces for Blend Protocol data structures
 */

/**
 * Reserve configuration data
 */
export interface ReserveConfig {
  decimals: number;
  c_factor: number; // Collateral factor
  l_factor: number; // Liability factor
  util: number; // Target utilization
  max_util: number; // Maximum utilization
  r_base: number; // Base rate
  r_one: number; // Rate at target utilization
  r_two: number; // Rate at max utilization
  r_three: number; // Rate above max utilization
  reactivity: number;
  index: number;
}

/**
 * Reserve data (balances and rates)
 */
export interface ReserveData {
  b_rate: bigint; // Supply rate
  d_rate: bigint; // Borrow rate
  b_supply: bigint; // Total supplied (scaled)
  d_supply: bigint; // Total borrowed (scaled)
  ir_mod: number; // Interest rate modifier
  last_time: bigint; // Last update timestamp
  backstop_credit: bigint;
}

/**
 * Emissions (rewards) data
 */
export interface EmissionsData {
  expiration: bigint;
  eps: bigint; // Emissions per second
}

/**
 * Complete reserve information for a single asset in a pool
 */
export interface PoolReserve {
  assetId: string;
  symbol?: string;
  name?: string;
  decimals?: number;
  config: ReserveConfig;
  data: ReserveData;

  // Pre-calculated rates from SDK
  borrowApr: number;
  estBorrowApy: number;
  supplyApr: number;
  estSupplyApy: number;

  // Calculated values
  totalSupplied: bigint; // Actual amount supplied
  totalBorrowed: bigint; // Actual amount borrowed
  availableLiquidity: bigint;
  utilization: number; // 0-1 float

  // Optional emissions
  borrowEmissions?: EmissionsData;
  supplyEmissions?: EmissionsData;
}

/**
 * Pool metadata
 */
export interface PoolMetadata {
  name?: string;
  description?: string;
}

/**
 * Complete pool information
 */
export interface BlendPoolData {
  id: string; // Pool contract address
  name?: string; // Pool name (if available)
  metadata?: PoolMetadata;
  reserves: PoolReserve[]; // All reserves in the pool
  timestamp: number; // Last update time

  // Aggregate stats
  totalReserves: number; // Number of different assets
  status: "active" | "paused" | "unknown";
}

/**
 * Token metadata for display
 */
export interface TokenMetadata {
  address: string;
  symbol: string;
  name: string;
  decimals: number;
  icon?: string;
}

/**
 * Hook return type for loading pools
 */
export interface UseBlendPoolsResult {
  pools: BlendPoolData[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook return type for single pool
 */
export interface UsePoolDataResult {
  pool: BlendPoolData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}
