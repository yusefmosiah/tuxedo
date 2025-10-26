import React, { useState, useEffect, useRef } from 'react';
import { Button, Text } from '@stellar/design-system';
import { useWallet } from '../hooks/useWallet';
import { useSubmitRpcTx } from '../debug/hooks/useSubmitRpcTx';
import { EmbeddedTransaction } from '../utils/transactionParser';

interface TransactionCardProps {
  transaction: EmbeddedTransaction;
}

export const TransactionCard: React.FC<TransactionCardProps> = ({ transaction }) => {
  const wallet = useWallet();
  const submitTx = useSubmitRpcTx();
  const [status, setStatus] = useState<'pending' | 'signing' | 'submitting' | 'success' | 'error'>('pending');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [txHash, setTxHash] = useState<string>('');
  const autoTriggerAttempted = useRef(false);

  const handleSign = async () => {
    if (!wallet.address) {
      setStatus('error');
      setErrorMessage('Please connect your wallet first');
      return;
    }

    if (!wallet.signTransaction) {
      setStatus('error');
      setErrorMessage('Wallet does not support transaction signing');
      return;
    }

    try {
      setStatus('signing');
      setErrorMessage('');

      // Sign the transaction using the wallet
      const { signedTxXdr } = await wallet.signTransaction(transaction.xdr, {
        networkPassphrase: wallet.networkPassphrase,
        address: wallet.address,
      });

      setStatus('submitting');

      // Determine RPC URL based on network
      const network = transaction.network || 'testnet';
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
    } catch (error: any) {
      console.error('Transaction error:', error);
      setStatus('error');
      setErrorMessage(error.message || 'Failed to sign or submit transaction');
    }
  };

  // Auto-trigger wallet signing when component mounts
  useEffect(() => {
    // Only auto-trigger once, when wallet is connected, and status is pending
    if (
      !autoTriggerAttempted.current &&
      wallet.address &&
      wallet.signTransaction &&
      status === 'pending'
    ) {
      autoTriggerAttempted.current = true;
      console.log('🔐 Auto-triggering wallet signature request...');

      // Small delay to let the UI render first
      const timer = setTimeout(() => {
        handleSign();
      }, 500);

      return () => clearTimeout(timer);
    }
  }, [wallet.address, wallet.signTransaction, status]); // eslint-disable-line react-hooks/exhaustive-deps

  const getExplorerUrl = () => {
    const network = transaction.network || 'testnet';
    const base = network === 'testnet'
      ? 'https://stellar.expert/explorer/testnet'
      : 'https://stellar.expert/explorer/public';
    return `${base}/tx/${txHash}`;
  };

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
          🔐 Transaction Ready to Sign
        </Text>
        <Text as="div" size="sm" style={{ marginBottom: '8px' }}>
          {transaction.description}
        </Text>

        {transaction.amount && (
          <Text as="div" size="xs" style={{ color: '#666', marginBottom: '4px' }}>
            Amount: {transaction.amount} XLM
          </Text>
        )}

        {transaction.estimated_shares && (
          <Text as="div" size="xs" style={{ color: '#666', marginBottom: '4px' }}>
            Estimated shares: {transaction.estimated_shares}
          </Text>
        )}

        {transaction.note && (
          <Text as="div" size="xs" style={{ color: '#666', fontStyle: 'italic', marginBottom: '4px' }}>
            {transaction.note}
          </Text>
        )}

        <Text as="div" size="xs" style={{ color: '#666' }}>
          Network: {transaction.network || 'testnet'}
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
