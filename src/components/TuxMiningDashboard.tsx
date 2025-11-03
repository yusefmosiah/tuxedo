import React, { useState, useEffect } from 'react';
import { Button, Text, Input } from '@stellar/design-system';
import { useWallet } from '../hooks/useWallet';
import { useAutoDeposit } from '../hooks/useAutoDeposit';
import { AutoTransactionCard } from './AutoTransactionCard';
import { transactionApi } from '../lib/api';

interface MiningStatus {
  user_address: string;
  total_tux_mined: number;
  active_mining_sessions: number;
  last_mining?: string;
  mining_power: number;
  next_reward_estimate: number;
}

export const TuxMiningDashboard: React.FC = () => {
  const wallet = useWallet();
  const [depositAmount, setDepositAmount] = useState<string>('10');
  const [miningStatus, setMiningStatus] = useState<MiningStatus | null>(null);

  const {
    isPreparing,
    transactionData,
    error,
    triggerDeposit,
    clearTransaction,
    handleTransactionComplete,
    handleError,
    canDeposit
  } = useAutoDeposit({
    onTransactionComplete: (txHash: string) => {
      console.log('✅ Deposit transaction completed:', txHash);
      // Refresh mining status after successful transaction
      fetchMiningStatus();
    },
    onError: (errorMsg: string) => {
      console.error('❌ Transaction failed:', errorMsg);
    }
  });

  // Fetch mining status when wallet connects
  useEffect(() => {
    if (wallet.address) {
      fetchMiningStatus();
    }
  }, [wallet.address]);

  const fetchMiningStatus = async () => {
    if (!wallet.address) return;

    // setLoadingStatus(true);
    try {
      const status = await transactionApi.getMiningStatus(wallet.address);
      setMiningStatus(status);
    } catch (error) {
      console.error('Failed to fetch mining status:', error);
    } finally {
      // setLoadingStatus(false);
    }
  };

  const handleDepositClick = async () => {
    const amount = parseFloat(depositAmount);
    if (isNaN(amount) || amount <= 0) {
      handleError('Please enter a valid deposit amount');
      return;
    }

    // Trigger the deposit - this will automatically prepare and show the transaction card
    await triggerDeposit(amount);
  };

  const handleClearTransaction = () => {
    clearTransaction();
  };

  const getEstimatedTuxRewards = () => {
    const amount = parseFloat(depositAmount);
    if (isNaN(amount) || amount <= 0) return 0;
    return amount * 1.0; // 1:1 ratio
  };

  if (!wallet.address) {
    return (
      <div
        style={{
          padding: '24px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #dee2e6',
          textAlign: 'center'
        }}
      >
        <Text as="h3" size="lg" weight="semi-bold" style={{ marginBottom: '16px' }}>
          🪙 Tux Mining Dashboard
        </Text>
        <Text as="p" size="md" style={{ color: '#666', marginBottom: '16px' }}>
          Connect your wallet to start mining TUX tokens by depositing XLM
        </Text>
        <Text as="p" size="sm" style={{ color: '#999' }}>
          Testnet deposits earn TUX rewards at 1:1 ratio
        </Text>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: '24px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        border: '1px solid #dee2e6'
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <Text as="h3" size="lg" weight="semi-bold" style={{ marginBottom: '8px' }}>
          🪙 Tux Mining Dashboard
        </Text>
        <Text as="p" size="md" style={{ color: '#666' }}>
          Deposit testnet XLM to mine TUX tokens automatically
        </Text>
      </div>

      {/* Mining Status */}
      {miningStatus && (
        <div
          style={{
            marginBottom: '24px',
            padding: '16px',
            backgroundColor: '#e8f5e9',
            borderRadius: '6px',
            border: '1px solid #c8e6c9'
          }}
        >
          <Text as="h4" size="md" weight="semi-bold" style={{ marginBottom: '12px' }}>
            📊 Mining Status
          </Text>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
            <div>
              <Text as="div" size="xs" style={{ color: '#666' }}>Total TUX Mined</Text>
              <Text as="div" size="lg" weight="bold" style={{ color: '#2e7d32' }}>
                {miningStatus.total_tux_mined.toFixed(2)} TUX
              </Text>
            </div>
            <div>
              <Text as="div" size="xs" style={{ color: '#666' }}>Active Sessions</Text>
              <Text as="div" size="lg" weight="bold" style={{ color: '#1976d2' }}>
                {miningStatus.active_mining_sessions}
              </Text>
            </div>
            <div>
              <Text as="div" size="xs" style={{ color: '#666' }}>Mining Power</Text>
              <Text as="div" size="lg" weight="bold" style={{ color: '#f57c00' }}>
                {miningStatus.mining_power.toFixed(1)}X
              </Text>
            </div>
          </div>
        </div>
      )}

      {/* Deposit Controls */}
      {!transactionData && (
        <div style={{ marginBottom: '24px' }}>
          <Text as="h4" size="md" weight="semi-bold" style={{ marginBottom: '12px' }}>
            💰 Make a Deposit
          </Text>

          <div style={{ display: 'flex', gap: '12px', alignItems: 'end', marginBottom: '12px' }}>
            <div style={{ flex: 1 }}>
              <Input
                id="deposit-amount"
                label="Deposit Amount (XLM)"
                type="number"
                value={depositAmount}
                onChange={(e) => setDepositAmount(e.target.value)}
                placeholder="10"
                min="1"
                step="0.1"
                fieldSize="md"
              />
              <Text as="div" size="xs" style={{ color: '#666', marginTop: '4px' }}>
                Estimated TUX rewards: {getEstimatedTuxRewards().toFixed(2)} TUX
              </Text>
            </div>

            <Button
              variant="primary"
              size="md"
              onClick={handleDepositClick}
              disabled={!canDeposit || isPreparing}
            >
              {isPreparing ? 'Preparing...' : 'Deposit & Mine TUX'}
            </Button>
          </div>

          {/* Error Display */}
          {error && (
            <div style={{
              padding: '12px',
              backgroundColor: '#ffebee',
              borderRadius: '4px',
              border: '1px solid #ffcdd2',
              marginBottom: '12px'
            }}>
              <Text as="p" size="sm" style={{ color: '#c62828', margin: 0 }}>
                ❌ {error}
              </Text>
            </div>
          )}

          <Text as="p" size="xs" style={{ color: '#999' }}>
            ⚠️ This is a testnet demo. Real TUX tokens are simulated for demonstration purposes.
          </Text>
        </div>
      )}

      {/* Transaction Card */}
      {transactionData && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <Text as="h4" size="md" weight="semi-bold">
              🚀 Transaction Ready
            </Text>
            <Button
              variant="tertiary"
              size="sm"
              onClick={handleClearTransaction}
            >
              Cancel
            </Button>
          </div>

          <AutoTransactionCard
            transactionData={transactionData}
            onTransactionComplete={handleTransactionComplete}
            onError={handleError}
          />
        </div>
      )}

      {/* Instructions */}
      <div
        style={{
          padding: '16px',
          backgroundColor: '#fff3cd',
          borderRadius: '6px',
          border: '1px solid #ffeaa7',
          marginTop: '16px'
        }}
      >
        <Text as="h4" size="sm" weight="semi-bold" style={{ marginBottom: '8px', color: '#856404' }}>
          💡 How It Works
        </Text>
        <Text as="div" size="xs" style={{ color: '#856404', margin: 0, paddingLeft: '16px' }}>
          <li>Enter XLM amount for testnet deposit</li>
          <li>Click "Deposit & Mine TUX" to prepare transaction</li>
          <li>Wallet opens automatically for signature</li>
          <li>Transaction submits to testnet network</li>
          <li>TUX rewards calculated at 1:1 ratio</li>
          <li>Mining status updates automatically</li>
        </Text>
      </div>
    </div>
  );
};