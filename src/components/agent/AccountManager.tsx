import React from 'react';
import { useAgent } from '../../providers/AgentProvider';

export const AccountManager: React.FC = () => {
  const { accounts, activeAccount, createAccount, setActiveAccount, isLoading, error } = useAgent();

  const handleCreateAccount = async () => {
    try {
      await createAccount();
    } catch (err) {
      console.error('Failed to create account:', err);
    }
  };

  return (
    <div className="account-manager" style={{
      padding: '20px',
      backgroundColor: 'var(--color-bg-surface)',
      borderRadius: '8px',
      border: '1px solid var(--color-border)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <h3 style={{
          margin: 0,
          fontSize: '18px',
          fontWeight: 'bold',
          color: 'var(--color-text-primary)'
        }}>
          Agent Accounts
        </h3>

        <button
          onClick={handleCreateAccount}
          disabled={isLoading}
          className="btn-stellar"
          style={{
            fontSize: '12px',
            fontFamily: 'var(--font-tertiary-mono)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            padding: '8px 16px'
          }}
        >
          {isLoading ? 'Creating...' : 'Create New Account'}
        </button>
      </div>

      {error && (
        <div style={{
          color: 'var(--color-error)',
          fontSize: '14px',
          marginBottom: '16px',
          padding: '8px 12px',
          backgroundColor: 'var(--color-error-bg)',
          border: '1px solid var(--color-error-border)',
          borderRadius: '4px'
        }}>
          Error: {error}
        </div>
      )}

      <div className="account-list">
        <h4 style={{
          margin: '0 0 12px 0',
          fontSize: '14px',
          fontWeight: '600',
          color: 'var(--color-text-secondary)'
        }}>
          Your Agent Accounts ({accounts.length}):
        </h4>

        {accounts.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '24px',
            color: 'var(--color-text-secondary)',
            fontSize: '14px'
          }}>
            No agent accounts yet. Create your first account to get started!
          </div>
        ) : (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            {accounts.map(account => (
              <div
                key={account.address}
                className={`account-item ${account.address === activeAccount ? 'active' : ''}`}
                onClick={() => setActiveAccount(account.address)}
                style={{
                  padding: '12px',
                  border: '1px solid var(--color-border)',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  backgroundColor: account.address === activeAccount
                    ? 'var(--color-primary-bg)'
                    : 'var(--color-bg-primary)',
                  borderColor: account.address === activeAccount
                    ? 'var(--color-primary)'
                    : 'var(--color-border)',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '4px'
                }}>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: 'var(--color-text-primary)'
                  }}>
                    {account.name}
                  </div>
                  {account.address === activeAccount && (
                    <div style={{
                      fontSize: '10px',
                      backgroundColor: 'var(--color-primary)',
                      color: 'white',
                      padding: '2px 6px',
                      borderRadius: '3px',
                      fontFamily: 'var(--font-tertiary-mono)',
                      textTransform: 'uppercase'
                    }}>
                      Active
                    </div>
                  )}
                </div>

                <div style={{
                  fontSize: '12px',
                  color: 'var(--color-text-secondary)',
                  fontFamily: 'var(--font-tertiary-mono)',
                  marginBottom: '4px'
                }}>
                  {account.address.slice(0, 12)}...{account.address.slice(-12)}
                </div>

                <div style={{
                  fontSize: '12px',
                  color: 'var(--color-text-secondary)'
                }}>
                  Balance: {account.balance.toFixed(2)} XLM
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {activeAccount && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          backgroundColor: 'var(--color-bg-primary)',
          border: '1px solid var(--color-border)',
          borderRadius: '6px'
        }}>
          <div style={{
            fontSize: '12px',
            color: 'var(--color-text-secondary)',
            marginBottom: '4px'
          }}>
            Currently Active Account:
          </div>
          <div style={{
            fontSize: '13px',
            fontFamily: 'var(--font-tertiary-mono)',
            color: 'var(--color-text-primary)'
          }}>
            {activeAccount}
          </div>
        </div>
      )}
    </div>
  );
};