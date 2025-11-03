/**
 * Legacy Wallet Balance Hook - Agent-First Architecture
 *
 * Provides backward compatibility for components expecting wallet balance functionality
 */

import { useState, useEffect } from 'react';

export interface WalletBalanceState {
  balance: string;
  nativeBalance: string;
  loading: boolean;
  isFunded?: boolean;
  isLoading?: boolean;
}

/**
 * Legacy useWalletBalance hook for agent-first architecture
 */
export function useWalletBalance(): WalletBalanceState {
  const [balance, setBalance] = useState<string>('0');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchBalance = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/agent/accounts');
        if (response.ok) {
          const accounts = await response.json();
          if (accounts.length > 0 && accounts[0].balance !== undefined) {
            setBalance(accounts[0].balance.toString());
          }
        }
      } catch (error) {
        console.log('Could not fetch balance');
        setBalance('0');
      } finally {
        setLoading(false);
      }
    };

    fetchBalance();
  }, []);

  return {
    balance,
    nativeBalance: balance,
    loading,
    isFunded: parseFloat(balance) > 0,
    isLoading: loading
  };
}