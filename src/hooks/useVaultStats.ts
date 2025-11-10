import { useQuery } from "@tanstack/react-query";
import { useWallet } from "./useWallet";

/**
 * Vault statistics interface
 */
export interface VaultStats {
  tvl: number; // Total Value Locked in USDC
  shareValue: number; // Current TUX0 share value in USDC
  totalShares: number; // Total TUX0 shares issued
  apy: number; // Current APY percentage
  initialDeposits: number; // Total initial deposits
}

/**
 * Hook to fetch and manage vault statistics
 *
 * Features:
 * - Fetches vault TVL, share value, APY
 * - Fetches user's share balance
 * - Auto-refreshes every 30 seconds
 * - Error handling and retry logic
 *
 * @returns Vault stats, user shares, loading state, error, and refetch function
 */
export function useVaultStats() {
  const { address: walletAddress } = useWallet();

  // Fetch vault statistics
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    refetch: refetchStats,
  } = useQuery<VaultStats>({
    queryKey: ["vaultStats"],
    queryFn: async () => {
      const response = await fetch("/api/vault/stats");

      if (!response.ok) {
        throw new Error(`Failed to fetch vault stats: ${response.statusText}`);
      }

      const data = await response.json();

      return {
        tvl: data.tvl || 0,
        shareValue: data.share_value || 1.0,
        totalShares: data.total_shares || 0,
        apy: data.apy || 0,
        initialDeposits: data.initial_deposits || 0,
      };
    },
    refetchInterval: 30_000, // Refresh every 30 seconds
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // Fetch user's share balance
  const {
    data: userShares,
    isLoading: sharesLoading,
    error: sharesError,
    refetch: refetchShares,
  } = useQuery<number>({
    queryKey: ["userVaultShares", walletAddress],
    queryFn: async () => {
      if (!walletAddress) return 0;

      const response = await fetch(
        `/api/vault/user/${walletAddress}/shares`
      );

      if (!response.ok) {
        throw new Error(
          `Failed to fetch user shares: ${response.statusText}`
        );
      }

      const data = await response.json();
      return data.shares || 0;
    },
    enabled: !!walletAddress, // Only fetch if wallet is connected
    refetchInterval: 30_000,
    retry: 3,
  });

  // Refetch both stats and user shares
  const refetch = () => {
    refetchStats();
    if (walletAddress) {
      refetchShares();
    }
  };

  return {
    stats: stats || {
      tvl: 0,
      shareValue: 1.0,
      totalShares: 0,
      apy: 0,
      initialDeposits: 0,
    },
    userShares: userShares || 0,
    loading: statsLoading || sharesLoading,
    error: statsError?.message || sharesError?.message || null,
    refetch,
  };
}
