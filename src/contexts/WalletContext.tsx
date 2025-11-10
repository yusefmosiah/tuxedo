import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import {
  StellarWalletsKit,
  WalletNetwork,
  ISupportedWallet,
} from "@creit.tech/stellar-wallets-kit";
import { FREIGHTER_ID } from "@creit.tech/stellar-wallets-kit/modules/freighter";
import { API_BASE_URL } from "../lib/api";

export type AccountMode = "agent" | "external" | "imported";

interface AgentAccount {
  id: string;
  address: string;
  balance: string;
  name?: string;
}

interface WalletContextType {
  // Wallet connection
  kit: StellarWalletsKit | null;
  address: string | null;
  isConnected: boolean;

  // Account mode
  mode: AccountMode;
  setMode: (mode: AccountMode) => void;

  // Actions
  connectWallet: () => Promise<void>;
  disconnectWallet: () => void;
  signTransaction: (xdr: string) => Promise<string>;

  // Agent accounts
  agentAccounts: AgentAccount[];
  selectedAgentAccount: AgentAccount | null;
  setSelectedAgentAccount: (account: AgentAccount | null) => void;
  refreshAgentAccounts: () => Promise<void>;

  // Loading states
  isInitializing: boolean;
  isLoading: boolean;
}

const WalletContext = createContext<WalletContextType | undefined>(undefined);

export function WalletProvider({ children }: { children: ReactNode }) {
  const [kit, setKit] = useState<StellarWalletsKit | null>(null);
  const [address, setAddress] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [mode, setMode] = useState<AccountMode>("agent");
  const [agentAccounts, setAgentAccounts] = useState<AgentAccount[]>([]);
  const [selectedAgentAccount, setSelectedAgentAccount] =
    useState<AgentAccount | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  // Initialize stellar-wallets-kit
  useEffect(() => {
    const initKit = async () => {
      try {
        const walletKit = new StellarWalletsKit({
          network: WalletNetwork.PUBLIC, // mainnet
          selectedWalletId: FREIGHTER_ID,
          modules: await import("@creit.tech/stellar-wallets-kit").then(
            (mod) => mod.allowAllModules()
          ),
        });
        setKit(walletKit);
        console.log("✅ Stellar Wallets Kit initialized");
      } catch (error) {
        console.error("❌ Failed to initialize Stellar Wallets Kit:", error);
      } finally {
        setIsInitializing(false);
      }
    };
    initKit();
  }, []);

  // Fetch agent accounts from backend
  const refreshAgentAccounts = async () => {
    try {
      setIsLoading(true);
      const sessionToken = localStorage.getItem("session_token");
      if (!sessionToken) {
        console.log("No session token - skipping agent accounts fetch");
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/agent/accounts`, {
        headers: {
          Authorization: `Bearer ${sessionToken}`,
        },
      });

      if (response.ok) {
        const accounts = await response.json();
        setAgentAccounts(accounts);

        // If in agent mode and we have accounts, set first as active if none selected
        if (mode === "agent" && accounts.length > 0 && !address) {
          const firstAccount = accounts[0];
          setSelectedAgentAccount(firstAccount);
          setAddress(firstAccount.address);
          setIsConnected(true);
        }

        console.log(`✅ Loaded ${accounts.length} agent accounts`);
      } else if (response.status === 401) {
        console.log("Not authenticated - clearing agent accounts");
        setAgentAccounts([]);
        setSelectedAgentAccount(null);
      }
    } catch (error) {
      console.error("Failed to fetch agent accounts:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch agent accounts on mount and when mode changes
  useEffect(() => {
    if (mode === "agent") {
      refreshAgentAccounts();
    }
  }, [mode]);

  // Update address when selected agent account changes
  useEffect(() => {
    if (mode === "agent" && selectedAgentAccount) {
      setAddress(selectedAgentAccount.address);
      setIsConnected(true);
    }
  }, [selectedAgentAccount, mode]);

  const connectWallet = async () => {
    if (!kit) {
      throw new Error("Wallet kit not initialized");
    }

    setIsLoading(true);
    try {
      await kit.openModal({
        onWalletSelected: async (option: ISupportedWallet) => {
          try {
            kit.setWallet(option.id);
            const { address: walletAddress } = await kit.getAddress();
            setAddress(walletAddress);
            setIsConnected(true);
            setMode("external");
            console.log(
              `✅ Connected to ${option.name}: ${walletAddress.slice(0, 8)}...`
            );
          } catch (error) {
            console.error("Failed to get wallet address:", error);
            throw error;
          }
        },
      });
    } finally {
      setIsLoading(false);
    }
  };

  const disconnectWallet = () => {
    setAddress(null);
    setIsConnected(false);
    setMode("agent");
    console.log("🔌 Wallet disconnected");

    // Restore agent account if available
    if (agentAccounts.length > 0) {
      const firstAccount = agentAccounts[0];
      setSelectedAgentAccount(firstAccount);
      setAddress(firstAccount.address);
      setIsConnected(true);
    }
  };

  const signTransaction = async (xdr: string): Promise<string> => {
    if (mode === "external" && kit) {
      // Use external wallet to sign
      try {
        const { signedTxXdr } = await kit.signTransaction(xdr, {
          networkPassphrase: "Public Global Stellar Network ; September 2015",
          address: address!,
        });
        console.log("✅ Transaction signed by external wallet");
        return signedTxXdr;
      } catch (error) {
        console.error("❌ Failed to sign transaction:", error);
        throw new Error("User rejected transaction or signing failed");
      }
    } else if (mode === "agent") {
      // Agent signs server-side (no user action needed)
      // Transaction will be signed by backend using AccountManager
      console.log("🤖 Transaction will be signed by agent backend");
      return xdr; // Backend will sign
    } else {
      throw new Error("Invalid account mode for signing");
    }
  };

  const value: WalletContextType = {
    kit,
    address,
    isConnected,
    mode,
    setMode,
    connectWallet,
    disconnectWallet,
    signTransaction,
    agentAccounts,
    selectedAgentAccount,
    setSelectedAgentAccount,
    refreshAgentAccounts,
    isInitializing,
    isLoading,
  };

  return (
    <WalletContext.Provider value={value}>{children}</WalletContext.Provider>
  );
}

export function useWalletContext() {
  const context = useContext(WalletContext);
  if (!context) {
    throw new Error("useWalletContext must be used within WalletProvider");
  }
  return context;
}
