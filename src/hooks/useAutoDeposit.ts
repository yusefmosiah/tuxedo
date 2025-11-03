import { useState, useCallback } from 'react';
import { useWallet } from './useWallet';
import { transactionApi, TransactionResponse } from '../lib/api';

interface UseAutoDepositOptions {
  onTransactionComplete?: (txHash: string) => void;
  onError?: (error: string) => void;
  autoTrigger?: boolean; // Whether to automatically trigger deposits
}

export const useAutoDeposit = (options: UseAutoDepositOptions = {}) => {
  const wallet = useWallet();
  const [isPreparing, setIsPreparing] = useState(false);
  const [transactionData, setTransactionData] = useState<TransactionResponse['transaction'] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    onTransactionComplete,
    onError
  } = options;

  const prepareDeposit = useCallback(async (
    amount: number,
    vaultAddress?: string
  ) => {
    if (!wallet.address) {
      const errorMsg = 'Wallet not connected';
      setError(errorMsg);
      onError?.(errorMsg);
      return null;
    }

    setIsPreparing(true);
    setError(null);

    try {
      console.log('🚀 Preparing deposit transaction:', {
        userAddress: wallet.address,
        amount,
        vaultAddress
      });

      const response: TransactionResponse = await transactionApi.prepareDepositTransaction(
        wallet.address,
        amount,
        vaultAddress
      );

      if (!response.success || !response.transaction) {
        throw new Error(response.error || 'Failed to prepare transaction');
      }

      console.log('✅ Transaction prepared successfully:', response.transaction);
      setTransactionData(response.transaction);
      return response.transaction;

    } catch (err: any) {
      const errorMsg = err.message || 'Failed to prepare deposit transaction';
      setError(errorMsg);
      console.error('❌ Deposit preparation failed:', errorMsg);
      onError?.(errorMsg);
      return null;
    } finally {
      setIsPreparing(false);
    }
  }, [wallet.address, onError]);

  const triggerDeposit = useCallback(async (
    amount: number,
    vaultAddress?: string
  ) => {
    const txData = await prepareDeposit(amount, vaultAddress);
    return txData;
  }, [prepareDeposit]);

  const clearTransaction = useCallback(() => {
    setTransactionData(null);
    setError(null);
  }, []);

  const handleTransactionComplete = useCallback((txHash: string) => {
    console.log('✅ Transaction completed:', txHash);
    onTransactionComplete?.(txHash);
    clearTransaction();
  }, [onTransactionComplete, clearTransaction]);

  const handleError = useCallback((errorMsg: string) => {
    setError(errorMsg);
    onError?.(errorMsg);
  }, [onError]);

  return {
    isPreparing,
    transactionData,
    error,
    prepareDeposit,
    triggerDeposit,
    clearTransaction,
    handleTransactionComplete,
    handleError,
    canDeposit: !!wallet.address && !isPreparing
  };
};