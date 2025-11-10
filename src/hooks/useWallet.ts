/**
 * Legacy Wallet Hook - Agent-First Architecture
 *
 * This file provides backward compatibility for components that still expect
 * a wallet interface. In our new agent-first architecture, AI agents manage
 * their own accounts autonomously.
 */

import { useState, useEffect } from "react";
import { API_BASE_URL } from "../lib/api";

export interface WalletState {
  address: string | null;
  isConnected: boolean;
  network: string;
  signTransaction?: (tx: any) => Promise<any>;
  isPending?: boolean;
  networkPassphrase?: string;
}

/**
 * Legacy useWallet hook for agent-first architecture
 * Returns a simplified wallet-like interface for backward compatibility
 */
export function useWallet(): WalletState {
  const [agentAddress, setAgentAddress] = useState<string | null>(null);

  useEffect(() => {
    // Fetch agent accounts on mount
    const fetchAgentAccounts = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/agent/accounts`);
        if (response.ok) {
          const accounts = await response.json();
          if (accounts.length > 0) {
            setAgentAddress(accounts[0].address);
          }
        }
      } catch (error) {
        console.log("No agent accounts available, agent works autonomously");
      }
    };

    fetchAgentAccounts();
  }, []);

  return {
    address: agentAddress,
    isConnected: !!agentAddress,
    network: "testnet",
    signTransaction: async (xdr: any, _options?: any) => {
      // In agent-first architecture, agents sign their own transactions
      // This is a no-op for backward compatibility
      console.log("Agent manages transaction signing autonomously");
      return { signedTxXdr: xdr };
    },
    isPending: false,
    networkPassphrase: "Public Global Stellar Network ; September 2015",
  };
}

/**
 * Legacy wallet balance hook for agent-first architecture
 */
export function useWalletBalance() {
  const [balance, setBalance] = useState<string>("0");

  useEffect(() => {
    const fetchBalance = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/agent/accounts`);
        if (response.ok) {
          const accounts = await response.json();
          if (accounts.length > 0 && accounts[0].balance !== undefined) {
            setBalance(accounts[0].balance.toString());
          }
        }
      } catch (error) {
        console.log("Could not fetch balance");
      }
    };

    fetchBalance();
  }, []);

  return { balance, nativeBalance: balance };
}
