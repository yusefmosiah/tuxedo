import { useState, useEffect } from "react";
import { PoolContract } from "@blend-capital/blend-sdk";
import { BLEND_CONTRACTS } from "../contracts/blend";
import { rpcUrl, networkPassphrase } from "../contracts/util";

export interface PoolReserve {
  assetId: string;
  symbol?: string;
  supplyApy: number;
  borrowApy: number;
  totalSupply: bigint;
  totalBorrow: bigint;
  availableLiquidity: bigint;
}

export interface PoolData {
  poolId: string;
  reserves: PoolReserve[];
  totalValueLocked: bigint;
  loading: boolean;
  error: string | null;
}

/**
 * Hook to query Blend pool data
 *
 * @param poolAddress - The Blend pool contract address
 * @returns Pool data including reserves, APYs, and TVL
 */
export function useBlendPool(poolAddress: string = BLEND_CONTRACTS.cometPool) {
  const [poolData, setPoolData] = useState<PoolData>({
    poolId: poolAddress,
    reserves: [],
    totalValueLocked: BigInt(0),
    loading: true,
    error: null,
  });

  useEffect(() => {
    let mounted = true;

    async function fetchPoolData() {
      try {
        setPoolData((prev) => ({ ...prev, loading: true, error: null }));

        // Initialize the Pool contract
        const pool = new PoolContract(poolAddress);

        // Query pool positions
        // Note: This is a simplified example. Real implementation needs:
        // 1. An Account object to simulate from
        // 2. Proper error handling
        // 3. Parsing of XDR results

        // For now, we'll just set the pool ID and show it's attempting to connect
        if (mounted) {
          setPoolData({
            poolId: poolAddress,
            reserves: [],
            totalValueLocked: BigInt(0),
            loading: false,
            error: null,
          });
        }
      } catch (error) {
        console.error("Error fetching pool data:", error);
        if (mounted) {
          setPoolData((prev) => ({
            ...prev,
            loading: false,
            error: error instanceof Error ? error.message : "Unknown error",
          }));
        }
      }
    }

    fetchPoolData();

    return () => {
      mounted = false;
    };
  }, [poolAddress]);

  return poolData;
}

/**
 * Hook to query multiple Blend pools
 */
export function useBlendPools(poolAddresses: string[]) {
  const [poolsData, setPoolsData] = useState<Record<string, PoolData>>({});

  useEffect(() => {
    poolAddresses.forEach((address) => {
      setPoolsData((prev) => ({
        ...prev,
        [address]: {
          poolId: address,
          reserves: [],
          totalValueLocked: BigInt(0),
          loading: true,
          error: null,
        },
      }));
    });
  }, [poolAddresses.join(",")]);

  return poolsData;
}
