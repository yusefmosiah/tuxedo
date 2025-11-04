import React from 'react';
import { useAgent } from '../../providers/AgentProvider';

/**
 * AgentMetrics Component - Shows performance and earnings data
 *
 * Displays agent performance metrics, earnings, and efficiency statistics
 */
export const AgentMetrics: React.FC = () => {
  const agent = useAgent();

  // Calculate basic metrics from available data
  const totalBalance = agent.accounts.reduce((sum, account) => sum + account.balance, 0);
  const activeAccounts = agent.accounts.length;

  return (
    <div style={{
      padding: '20px',
      backgroundColor: 'var(--color-bg-surface)',
      border: '1px solid var(--color-border)',
      borderRadius: 'var(--border-radius-lg)'
    }}>
      <h3 style={{
        margin: '0 0 16px 0',
        color: 'var(--color-text-primary)',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        📈 Agent Performance Metrics
      </h3>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '16px'
      }}>
        {/* Total Balance */}
        <div style={{
          padding: '16px',
          backgroundColor: 'var(--color-bg-primary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: '#2ED06E',
            marginBottom: '4px'
          }}>
            {totalBalance.toFixed(2)} XLM
          </div>
          <div style={{
            fontSize: '12px',
            color: 'var(--color-text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Total Balance
          </div>
        </div>

        {/* Active Accounts */}
        <div style={{
          padding: '16px',
          backgroundColor: 'var(--color-bg-primary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: '#0066FF',
            marginBottom: '4px'
          }}>
            {activeAccounts}
          </div>
          <div style={{
            fontSize: '12px',
            color: 'var(--color-text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Active Accounts
          </div>
        </div>

        {/* Agent Status */}
        <div style={{
          padding: '16px',
          backgroundColor: 'var(--color-bg-primary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: agent.status === 'active' ? '#2ED06E' :
                   agent.status === 'error' ? '#FF3B30' : '#FFB800',
            marginBottom: '4px'
          }}>
            {agent.status === 'active' ? '🤖' : agent.status === 'error' ? '❌' : '⏸️'}
          </div>
          <div style={{
            fontSize: '12px',
            color: 'var(--color-text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Status
          </div>
        </div>
      </div>

      {/* Usage Note */}
      <div style={{
        marginTop: '20px',
        padding: '16px',
        backgroundColor: 'rgba(46, 208, 110, 0.1)',
        border: '1px solid rgba(46, 208, 110, 0.3)',
        borderRadius: '8px',
        fontSize: '14px'
      }}>
        <div style={{
          fontWeight: 'bold',
          color: 'var(--color-text-primary)',
          marginBottom: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          💡 Agent-First Architecture
        </div>

        <div style={{ color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
          {agent.status === 'active' ? (
            <> 🤖 Agent is <strong>actively managing</strong> {activeAccounts} account(s) with a total balance of {totalBalance.toFixed(2)} XLM.</>
          ) : agent.status === 'idle' ? (
            <> 🔄 Agent is <strong>idle</strong> and ready for new tasks. Start a conversation to activate the agent.</>
          ) : (
            <> ⚠️ Agent is in <strong>error state</strong>. Please check the error message and try refreshing.</>
          )}
          <br /><br />
          All activity is shown in real-time through the chat interface.
        </div>
      </div>
    </div>
  );
};