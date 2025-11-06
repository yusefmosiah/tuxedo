import React, {
  createContext,
  use,
  useState,
  useEffect,
  ReactNode,
} from "react";
import api from "../lib/api";

interface AgentAccount {
  address: string;
  name: string;
  balance: number;
  network: string;
  created_at: string;
}

interface AgentContextType {
  status: "active" | "idle" | "error";
  accounts: AgentAccount[]; // Read-only
  activeAccount: string; // Read-only
  isLoading: boolean;
  error: string | null;
}

const AgentContext = createContext<AgentContextType>({
  status: "idle",
  accounts: [],
  activeAccount: "",
  isLoading: false,
  error: null,
});

export const useAgent = () => use(AgentContext);

interface AgentProviderProps {
  children: ReactNode;
}

export const AgentProvider: React.FC<AgentProviderProps> = ({ children }) => {
  const [accounts, setAccounts] = useState<AgentAccount[]>([]);
  const [activeAccount, setActiveAccount] = useState<string>("");
  const [status, setStatus] = useState<"active" | "idle" | "error">("idle");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load existing accounts on mount
    loadAgentAccounts();
    // Only refresh occasionally, not continuously
    const interval = setInterval(loadAgentAccounts, 30000); // Poll every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadAgentAccounts = async () => {
    try {
      setIsLoading(true);

      const response = await api.get("/api/agent/accounts");
      if (response.data) {
        setAccounts(response.data);
        if (response.data.length > 0 && !activeAccount) {
          setActiveAccount(response.data[0].address);
        }
        setStatus("active");
      } else {
        setStatus("idle");
      }
      setError(null);
    } catch (err) {
      console.error("Failed to load agent accounts:", err);
      setStatus("error");
      setError(
        err instanceof Error ? err.message : "Failed to load agent accounts",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AgentContext
      value={{
        status,
        accounts, // Read-only
        activeAccount, // Read-only
        isLoading,
        error,
      }}
    >
      {children}
    </AgentContext>
  );
};
