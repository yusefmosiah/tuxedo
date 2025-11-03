import { useState, useEffect, useCallback } from 'react';
import { useWallet } from './useWallet';

interface PoolInfo {
  pool_id: string;
  staking_token: string;
  total_staked: number;
  apy: number;
  is_active: boolean;
  user_staked?: number;
  pending_rewards?: number;
  formatted_pending_rewards?: string;
}

interface FarmingOverview {
  token_info: {
    name: string;
    symbol: string;
    total_supply: number;
    contract_address: string;
  };
  pools: PoolInfo[];
  totals?: {
    total_pending_rewards: number;
    formatted_total_pending: string;
  };
}

interface UserPosition {
  pool_id: string;
  staking_token: string;
  amount_staked: number;
  stake_start_time: number;
  last_claim_time: number;
  pending_rewards: number;
  formatted_pending_rewards: string;
  apy: number;
}

interface UserPositions {
  user_address: string;
  positions: UserPosition[];
  total_pending_rewards: number;
  formatted_total_pending: string;
  active_positions: number;
  timestamp: number;
}

export interface UseTuxFarmingReturn {
  overview: FarmingOverview | null;
  userPositions: UserPositions | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
  getPoolDetails: (poolId: string) => Promise<any>;
}

/**
 * Hook for fetching and managing TUX farming data
 */
export const useTuxFarming = (): UseTuxFarmingReturn => {
  const { address: walletAddress } = useWallet();
  const [overview, setOverview] = useState<FarmingOverview | null>(null);
  const [userPositions, setUserPositions] = useState<UserPositions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOverview = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/tux-farming/overview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: walletAddress
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setOverview(data);

      // If we have a wallet address, also fetch user positions
      if (walletAddress) {
        fetchUserPositions();
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch farming overview');
    } finally {
      setLoading(false);
    }
  }, [walletAddress]);

  const fetchUserPositions = useCallback(async () => {
    if (!walletAddress) return;

    try {
      const response = await fetch('/api/tux-farming/user-positions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: walletAddress
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setUserPositions(data);

    } catch (err) {
      console.error('Error fetching user positions:', err);
      // Don't set error state here as it's not critical
    }
  }, [walletAddress]);

  const getPoolDetails = useCallback(async (poolId: string): Promise<any> => {
    try {
      const response = await fetch('/api/tux-farming/pool-details', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pool_id: poolId,
          wallet_address: walletAddress
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();

    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to fetch pool details');
    }
  }, [walletAddress]);

  const refetch = useCallback(() => {
    fetchOverview();
  }, [fetchOverview]);

  useEffect(() => {
    fetchOverview();
  }, [fetchOverview]);

  useEffect(() => {
    if (walletAddress) {
      fetchUserPositions();
    } else {
      setUserPositions(null);
    }
  }, [walletAddress, fetchUserPositions]);

  return {
    overview,
    userPositions,
    loading,
    error,
    refetch,
    getPoolDetails,
  };
};