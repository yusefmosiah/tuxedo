import React, { useState, useEffect } from 'react';
import { Button, Text } from '@stellar/design-system';
import { useWallet } from '../hooks/useWallet';
import { useSubmitRpcTx } from '../debug/hooks/useSubmitRpcTx';
import { transactionApi, TransactionResponse } from '../lib/api';

interface AutoTransactionCardProps {
  transactionData: TransactionResponse['transaction'];
  onTransactionComplete?: (txHash: string) => void;
  onError?: (error: string) => void;
}

export const AutoTransactionCard: React.FC<AutoTransactionCardProps> = ({
  transactionData,
  onTransactionComplete,
  onError
}) => {
  const wallet = useWallet();
  const submitTx = useSubmitRpcTx();
  const [status, setStatus] = useState<'pending' | 'signing' | 'submitting' | 'success' | 'error'>('pending');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [txHash, setTxHash] = useState<string>('');
  const autoTriggerAttempted = React.useRef(false);

  console.log('🚀 AutoTransactionCard rendered:', {
    hasTransactionData: !!transactionData,
    hasWalletAddress: !!wallet.address,
    hasSignFunction: !!wallet.signTransaction,
    walletIsPending: wallet.isPending,
    status,
    autoTriggerAttempted: autoTriggerAttempted.current
  });

  const handleSign = async () => {
    if (!wallet.address) {
      setStatus('error');
      setErrorMessage('Please connect your wallet first');
      onError?.('Please connect your wallet first');
      return;
    }

    if (!wallet.signTransaction) {
      setStatus('error');
      setErrorMessage('Wallet does not support transaction signing');
      onError?.('Wallet does not support transaction signing');
      return;
    }

    if (!transactionData) {
      setStatus('error');
      setErrorMessage('No transaction data available');
      onError?.('No transaction data available');
      return;
    }

    try {
      setStatus('signing');
      setErrorMessage('');

      // Sign the transaction using the wallet
      const { signedTxXdr } = await wallet.signTransaction(transactionData.xdr, {
        networkPassphrase: wallet.networkPassphrase,
        address: wallet.address,
      });

      setStatus('submitting');

      // Determine RPC URL based on network
      const network = transactionData.network || 'testnet';
      const rpcUrl = network === 'testnet'
        ? 'https://soroban-testnet.stellar.org'
        : 'https://soroban-rpc.stellar.org';

      const networkPassphrase = wallet.networkPassphrase ||
        (network === 'testnet'
          ? 'Test SDF Network ; September 2015'
          : 'Public Global Stellar Network ; September 2015');

      // Submit the signed transaction
      const result = await submitTx.mutateAsync({
        rpcUrl,
        transactionXdr: signedTxXdr,
        networkPassphrase,
        headers: {},
      });

      setStatus('success');
      setTxHash(result.hash);
      onTransactionComplete?.(result.hash);

      // Simulate mining completion for demo
      if (transactionData.tux_rewards > 0) {
        try {
          await transactionApi.simulateMiningCompletion(
            wallet.address,
            transactionData.amount
          );
        } catch (error) {
          console.error('Failed to simulate mining completion:', error);
        }
      }

    } catch (error: any) {
      console.error('Transaction error:', error);
      setStatus('error');
      setErrorMessage(error.message || 'Failed to sign or submit transaction');
      onError?.(error.message || 'Failed to sign or submit transaction');
    }
  };

  // Auto-trigger wallet signing when component mounts
  useEffect(() => {
    console.log('🚀 Auto-trigger useEffect fired:', {
      autoTriggerAttempted: autoTriggerAttempted.current,
      hasWalletAddress: !!wallet.address,
      hasSignFunction: !!wallet.signTransaction,
      walletIsPending: wallet.isPending,
      status,
      hasTransactionData: !!transactionData,
      allConditionsMet: !autoTriggerAttempted.current &&
        !!wallet.address &&
        !!wallet.signTransaction &&
        !wallet.isPending &&
        status === 'pending' &&
        !!transactionData
    });

    // Only auto-trigger once, when wallet is connected and loaded, transaction data is available, and status is pending
    if (
      !autoTriggerAttempted.current &&
      wallet.address &&
      wallet.signTransaction &&
      !wallet.isPending && // Wait for wallet to finish loading
      status === 'pending' &&
      transactionData
    ) {
      autoTriggerAttempted.current = true;
      console.log('✅ Auto-triggering wallet signature request in 1000ms...');

      // Small delay to let the UI render first
      const timer = setTimeout(() => {
        console.log('🚀 Calling handleSign()...');
        handleSign();
      }, 1000);

      return () => clearTimeout(timer);
    } else {
      console.log('❌ Auto-trigger conditions not met:', {
        attempted: autoTriggerAttempted.current,
        hasAddress: !!wallet.address,
        hasSignFn: !!wallet.signTransaction,
        notPending: !wallet.isPending,
        isPending: status === 'pending',
        hasTxData: !!transactionData
      });
    }
  }, [wallet.address, wallet.signTransaction, wallet.isPending, status, transactionData]); // eslint-disable-line react-hooks/exhaustive-deps

  const getExplorerUrl = () => {
    const network = transactionData?.network || 'testnet';
    const base = network === 'testnet'
      ? 'https://stellar.expert/explorer/testnet'
      : 'https://stellar.expert/explorer/public';
    return `${base}/tx/${txHash}`;
  };

  if (!transactionData) {
    return (
      <div
        style={{
          marginTop: '12px',
          padding: '16px',
          borderRadius: '8px',
          backgroundColor: '#fff3cd',
          border: '2px solid #ffc107',
        }}
      >
        <Text as="div" size="sm" style={{ color: '#856404' }}>
          ⚠️ No transaction data available
        </Text>
      </div>
    );
  }

  return (
    <div
      style={{
        marginTop: '12px',
        padding: '16px',
        borderRadius: '8px',
        backgroundColor: '#f0f4ff',
        border: '2px solid #667eea',
      }}
    >
      <div style={{ marginBottom: '12px' }}>
        <Text as="div" size="sm" style={{ fontWeight: 'bold', color: '#667eea', marginBottom: '8px' }}>
          🚀 Auto Transaction Ready - Wallet Opening
        </Text>
        <Text as="div" size="sm" style={{ marginBottom: '8px' }}>
          {transactionData.description}
        </Text>

        <Text as="div" size="xs" style={{ color: '#666', marginBottom: '4px' }}>
          Amount: {transactionData.amount} XLM
        </Text>

        {transactionData.tux_rewards && transactionData.tux_rewards > 0 && (
          <Text as="div" size="xs" style={{ color: '#4caf50', marginBottom: '4px' }}>
            🪙 Mining: {transactionData.tux_rewards.toFixed(2)} TUX
          </Text>
        )}

        {transactionData.estimated_shares && (
          <Text as="div" size="xs" style={{ color: '#666', marginBottom: '4px' }}>
            Estimated shares: {transactionData.estimated_shares}
          </Text>
        )}

        {transactionData.note && (
          <Text as="div" size="xs" style={{ color: '#666', fontStyle: 'italic', marginBottom: '4px' }}>
            {transactionData.note}
          </Text>
        )}

        <Text as="div" size="xs" style={{ color: '#666' }}>
          Network: {transactionData.network || 'testnet'}
        </Text>
      </div>

      {status === 'pending' && (
        <>
          {wallet.address ? (
            <div style={{ textAlign: 'center', padding: '8px' }}>
              <Text as="div" size="sm" style={{ color: '#667eea', marginBottom: '8px' }}>
                🔄 Opening wallet for signature...
              </Text>
              <Text as="div" size="xs" style={{ color: '#666' }}>
                Check your wallet extension
              </Text>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleSign}
                style={{ width: '100%', marginTop: '8px' }}
              >
                Retry
              </Button>
            </div>
          ) : (
            <Button
              variant="primary"
              size="md"
              onClick={handleSign}
              disabled={true}
              style={{ width: '100%' }}
            >
              ⚠️ Connect Wallet First
            </Button>
          )}
        </>
      )}

      {status === 'signing' && (
        <div style={{ textAlign: 'center', padding: '8px' }}>
          <Text as="div" size="sm" style={{ color: '#667eea' }}>
            🔄 Waiting for signature...
          </Text>
          <Text as="div" size="xs" style={{ color: '#666', marginTop: '4px' }}>
            Check your wallet extension
          </Text>
        </div>
      )}

      {status === 'submitting' && (
        <div style={{ textAlign: 'center', padding: '8px' }}>
          <Text as="div" size="sm" style={{ color: '#667eea' }}>
            📡 Submitting to network...
          </Text>
        </div>
      )}

      {status === 'success' && (
        <div style={{ textAlign: 'center', padding: '8px', backgroundColor: '#e8f5e9', borderRadius: '4px' }}>
          <Text as="div" size="sm" style={{ color: '#2e7d32', fontWeight: 'bold', marginBottom: '8px' }}>
            ✅ Transaction Successful!
          </Text>
          {transactionData.tux_rewards && transactionData.tux_rewards > 0 && (
            <Text as="div" size="xs" style={{ color: '#4caf50', marginBottom: '8px' }}>
              🪙 {transactionData.tux_rewards.toFixed(2)} TUX mined!
            </Text>
          )}
          <a
            href={getExplorerUrl()}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: '#667eea',
              textDecoration: 'underline',
              fontSize: '12px',
            }}
          >
            View on Stellar Expert →
          </a>
        </div>
      )}

      {status === 'error' && (
        <div style={{ padding: '8px', backgroundColor: '#ffebee', borderRadius: '4px' }}>
          <Text as="div" size="sm" style={{ color: '#c62828', marginBottom: '8px' }}>
            ❌ Error: {errorMessage}
          </Text>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleSign}
            style={{ width: '100%' }}
          >
            Try Again
          </Button>
        </div>
      )}
    </div>
  );
};