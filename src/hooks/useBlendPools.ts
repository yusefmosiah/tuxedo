import { useState, useEffect, useCallback } from "react";
import { Backstop, PoolV2, Reserve } from "@blend-capital/blend-sdk";
import { BLEND_CONTRACTS } from "../contracts/blend";
import { network } from "../contracts/util";

// Helper to check if URL uses HTTP protocol
const isHttpUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === "http:";
  } catch {
    // Fallback to string check if URL parsing fails
    return url.toLowerCase().startsWith("http://");
  }
};

// Create Blend SDK compatible network object
const blendNetwork = {
  rpc: network.rpcUrl,
  passphrase: network.passphrase,
  networkPassphrase: network.passphrase,
  // Allow HTTP for development and HTTP-based RPC providers
  allowHttp: isHttpUrl(network.rpcUrl) ||
             network.rpcUrl.includes("localhost") ||
             network.rpcUrl.includes("127.0.0.1"),
};
import {
  BlendPoolData,
  PoolReserve,
  UseBlendPoolsResult,
} from "../types/blend";

/**
 * Hook to fetch and monitor all Blend pools
 *
 * This hook:
 * 1. Loads the Backstop contract to get all active pool addresses from rewardZone
 * 2. Loads each pool using PoolV2.load()
 * 3. Transforms reserve data into our interface format
 * 4. Provides loading states and refetch capability
 *
 * Note: We use Backstop.config.rewardZone instead of Pool Factory events
 * because it's simpler, more reliable, and matches the official blend-ui approach.
 */
export function useBlendPools(): UseBlendPoolsResult {
  const [pools, setPools] = useState<BlendPoolData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Transform a Reserve from the SDK into our PoolReserve interface
   */
  const transformReserve = (assetId: string, reserve: Reserve): PoolReserve => {
    // Calculate actual amounts from scaled values
    const scalar = BigInt(10000000); // 1e7 SCALAR used by Blend
    // Use camelCase property names from SDK
    const totalSupplied =
      (BigInt(reserve.data.bSupply) * BigInt(reserve.data.bRate)) / scalar;
    const totalBorrowed =
      (BigInt(reserve.data.dSupply) * BigInt(reserve.data.dRate)) / scalar;
    const availableLiquidity = totalSupplied - totalBorrowed;

    return {
      assetId,
      config: reserve.config,
      data: reserve.data as any, // Type mismatch between SDK versions, safe to bypass

      // Pre-calculated rates from SDK
      borrowApr: reserve.borrowApr,
      estBorrowApy: reserve.estBorrowApy,
      supplyApr: reserve.supplyApr,
      estSupplyApy: reserve.estSupplyApy,

      // Calculated values
      totalSupplied,
      totalBorrowed,
      availableLiquidity,
      utilization: reserve.getUtilizationFloat(),

      // Emissions (if available)
      borrowEmissions: reserve.borrowEmissions as any,
      supplyEmissions: reserve.supplyEmissions as any,
    };
  };

  /**
   * Query the Backstop contract to get all active pools
   *
   * The Backstop contract maintains a rewardZone array which contains
   * all active pool addresses. This is the official approach.
   *
   * Note: If Backstop returns fewer pools than expected, the useBlendPools
   * hook will still try to load the Comet pool as a fallback.
   */
  const discoverPools = async (): Promise<string[]> => {
    try {
      console.log("🔍 Loading Backstop contract to discover pools...");

      // Load the Backstop contract - it contains the list of all active pools
      const backstop = await Backstop.load(
        blendNetwork,
        BLEND_CONTRACTS.backstop,
      );

      console.log(`  📊 Backstop loaded successfully`);
      console.log(`  📊 Backstop config:`, {
        rewardZoneCount: backstop.config.rewardZone.length,
      });

      // Get pool addresses from the reward zone
      // The reward zone contains all pools that earn backstop rewards
      const poolAddresses = backstop.config.rewardZone;

      // Log each discovered pool
      poolAddresses.forEach((address, index) => {
        console.log(`  🏊 Pool ${index + 1}: ${address}`);
      });

      console.log(
        `  ✅ Discovered ${poolAddresses.length} pool(s) from Backstop`,
      );

      return poolAddresses;
    } catch (err) {
      console.error("❌ Failed to discover pools from Backstop:", err);
      // Fall back to known pools
      console.log("⚠️ Falling back to known Comet pool");
      return [BLEND_CONTRACTS.cometPool];
    }
  };

  /**
   * Fetch all pools from the network
   */
  const fetchPools = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      console.log(
        "🔍 Discovering pools from Backstop:",
        BLEND_CONTRACTS.backstop,
      );

      // Discover pools from Backstop's reward zone
      let poolAddresses = await discoverPools();

      // If discovery failed, use known pools
      if (poolAddresses.length === 0) {
        console.log("⚠️ No pools discovered, using known Comet pool");
        poolAddresses = [BLEND_CONTRACTS.cometPool];
      }

      console.log(`📋 Loading ${poolAddresses.length} pool(s)...`);

      const poolDataPromises = poolAddresses.map(async (poolAddress) => {
        try {
          console.log(`  ⏳ Loading pool: ${poolAddress}`);

          // Load the complete pool data
          const pool = await PoolV2.load(blendNetwork, poolAddress);

          console.log(`  ✅ Pool loaded with ${pool.reserves.size} reserves`);
          console.log(`  📊 Pool metadata:`, {
            name: pool.metadata.name,
            status: pool.metadata.status,
            admin: pool.metadata.admin,
            reserves: pool.metadata.reserveList.length,
          });

          // Transform reserves from Map to array with our interface
          const reserves: PoolReserve[] = [];
          pool.reserves.forEach((reserve, assetId) => {
            reserves.push(transformReserve(assetId, reserve));
          });

          // Determine pool status
          // Status 0 = Active, Status 1 = Admin Frozen, Status 2+ = Other frozen states
          const status =
            pool.metadata.status === 0
              ? "active"
              : pool.metadata.status === undefined
                ? "active"
                : "paused";

          // Build pool data object
          const poolData: BlendPoolData = {
            id: poolAddress,
            name: pool.metadata.name || `Pool ${poolAddress.slice(0, 8)}...`,
            metadata: pool.metadata,
            reserves,
            timestamp: Date.now(),
            totalReserves: reserves.length,
            status,
          };

          console.log(`  ✅ Pool "${poolData.name}" is ${status}`);
          return poolData;
        } catch (err) {
          console.error(`  ❌ Failed to load pool ${poolAddress}:`, err);
          // Return a minimal pool data object on error
          return {
            id: poolAddress,
            name: `Pool ${poolAddress.slice(0, 8)}...`,
            reserves: [],
            timestamp: Date.now(),
            totalReserves: 0,
            status: "unknown" as const,
          };
        }
      });

      // Wait for all pools to load
      const loadedPools = await Promise.all(poolDataPromises);

      console.log(`✅ Successfully loaded ${loadedPools.length} pool(s)`);
      setPools(loadedPools);
      setError(null);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to fetch pools";
      console.error("❌ Error fetching pools:", errorMessage, err);
      setError(errorMessage);
      setPools([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch on mount
  useEffect(() => {
    fetchPools();
  }, [fetchPools]);

  return {
    pools,
    loading,
    error,
    refetch: fetchPools,
  };
}
