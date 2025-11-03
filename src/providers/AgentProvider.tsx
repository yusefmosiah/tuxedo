import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AgentAccount {
  address: string;
  name: string;
  balance: number;
  network: string;
  created_at: string;
}

interface AgentContextType {
  accounts: AgentAccount[];
  activeAccount: string;
  setActiveAccount: (address: string) => void;
  createAccount: (name?: string) => Promise<string>;
  isLoading: boolean;
  error: string | null;
}

const AgentContext = createContext<AgentContextType>({
  accounts: [],
  activeAccount: '',
  setActiveAccount: () => {},
  createAccount: async () => '',
  isLoading: false,
  error: null,
});

export const useAgent = () => useContext(AgentContext);

interface AgentProviderProps {
  children: ReactNode;
}

export const AgentProvider: React.FC<AgentProviderProps> = ({ children }) => {
  const [accounts, setAccounts] = useState<AgentAccount[]>([]);
  const [activeAccount, setActiveAccount] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createAccount = async (name?: string): Promise<string> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/agent/create-account', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });

      if (!response.ok) throw new Error('Failed to create account');

      const newAccount = await response.json();
      setAccounts(prev => [...prev, newAccount]);
      setActiveAccount(newAccount.address);

      return newAccount.address;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Load existing accounts on mount
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const response = await fetch('/api/agent/accounts');
      if (response.ok) {
        const accounts = await response.json();
        setAccounts(accounts);
        if (accounts.length > 0 && !activeAccount) {
          setActiveAccount(accounts[0].address);
        }
      }
    } catch (err) {
      console.error('Failed to load accounts:', err);
    }
  };

  return (
    <AgentContext.Provider value={{
      accounts,
      activeAccount,
      setActiveAccount,
      createAccount,
      isLoading,
      error
    }}>
      {children}
    </AgentContext.Provider>
  );
};