/**
 * Wallet Hook - Hybrid Architecture with stellar-wallets-kit
 *
 * This hook provides a unified interface for both agent-managed accounts
 * and external wallet connections (Freighter, xBull, etc.).
 *
 * Supports three modes:
 * - agent: Agent-managed accounts with autonomous signing
 * - external: External wallet (Freighter/xBull) with user approval
 * - imported: External wallet imported into agent management
 */

import { useWalletContext } from "../contexts/WalletContext";

export interface WalletState {
  address: string | null;
  isConnected: boolean;
  network: string;
  mode: "agent" | "external" | "imported";
  signTransaction: (xdr: string) => Promise<string>;
  isPending: boolean;
  networkPassphrase: string;

  // Extended properties
  connectWallet?: () => Promise<void>;
  disconnectWallet?: () => void;
  agentAccounts?: any[];
  selectedAgentAccount?: any;
  setSelectedAgentAccount?: (account: any) => void;
  refreshAgentAccounts?: () => Promise<void>;
  setMode?: (mode: "agent" | "external" | "imported") => void;
}

/**
 * Modern useWallet hook with stellar-wallets-kit integration
 * Provides backward compatibility while adding new wallet connection features
 */
export function useWallet(): WalletState {
  const {
    address,
    isConnected,
    mode,
    signTransaction,
    isLoading,
    connectWallet,
    disconnectWallet,
    agentAccounts,
    selectedAgentAccount,
    setSelectedAgentAccount,
    refreshAgentAccounts,
    setMode,
  } = useWalletContext();

  return {
    address,
    isConnected,
    network: "mainnet",
    mode,
    signTransaction,
    isPending: isLoading,
    networkPassphrase: "Public Global Stellar Network ; September 2015",

    // Extended properties for new functionality
    connectWallet,
    disconnectWallet,
    agentAccounts,
    selectedAgentAccount,
    setSelectedAgentAccount,
    refreshAgentAccounts,
    setMode,
  };
}

/**
 * Hook for accessing wallet balance
 */
export function useWalletBalance() {
  const { selectedAgentAccount, mode } = useWalletContext();

  const balance = mode === "agent" && selectedAgentAccount
    ? selectedAgentAccount.balance?.toString() || "0"
    : "0";

  return {
    balance,
    nativeBalance: balance
  };
}
