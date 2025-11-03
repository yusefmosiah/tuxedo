/**
 * Legacy Wallet Button - Agent-First Architecture
 *
 * Provides backward compatibility for components expecting a WalletButton
 * In our agent-first architecture, this shows agent account status
 */

import React from 'react';
import { Button } from '@stellar/design-system';

export const WalletButton: React.FC = () => {
  const [agentAccountCount, setAgentAccountCount] = React.useState(0);

  React.useEffect(() => {
    const fetchAgentAccounts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/agent/accounts');
        if (response.ok) {
          const accounts = await response.json();
          setAgentAccountCount(accounts.length);
        }
      } catch (error) {
        console.log('Agent accounts not available');
      }
    };

    fetchAgentAccounts();
  }, []);

  return (
    <Button variant="tertiary" size="sm" disabled>
      🤖 Agent Mode ({agentAccountCount} accounts)
    </Button>
  );
};