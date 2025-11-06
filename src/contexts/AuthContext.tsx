import React, {
  createContext,
  use,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { passkeyAuth, User, RegistrationResult, AuthResult, RecoveryCodeAuthResult } from "../services/passkeyAuth";

// Types
interface AuthContextType {
  user: User | null;
  sessionToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  register: (email: string, friendlyName?: string) => Promise<RegistrationResult>;
  login: (email: string) => Promise<AuthResult>;
  loginWithRecoveryCode: (email: string, code: string) => Promise<RecoveryCodeAuthResult>;
  acknowledgeRecoveryCodes: () => Promise<void>;
  validateSession: (token: string) => Promise<boolean>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const SESSION_TOKEN_KEY = "session_token";
const USER_DATA_KEY = "user_data";

// Provider component
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);

  // Check authentication status
  const checkAuth = async () => {
    setIsLoading(true);

    try {
      const storedToken = localStorage.getItem(SESSION_TOKEN_KEY);
      const storedUserData = localStorage.getItem(USER_DATA_KEY);

      if (storedToken && storedUserData) {
        // Validate session with backend
        const isValid = await validateSession(storedToken);

        if (isValid) {
          setSessionToken(storedToken);
          setUser(JSON.parse(storedUserData));
        } else {
          // Clear invalid session
          logout();
        }
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  // Register with passkey
  const register = async (email: string, friendlyName?: string): Promise<RegistrationResult> => {
    try {
      const result = await passkeyAuth.register(email, friendlyName);

      setSessionToken(result.session_token);
      setUser(result.user);

      return result;
    } catch (error) {
      console.error("Registration failed:", error);
      throw error;
    }
  };

  // Login with passkey
  const login = async (email: string): Promise<AuthResult> => {
    try {
      const result = await passkeyAuth.authenticate(email);

      setSessionToken(result.session_token);
      setUser(result.user);

      return result;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  // Login with recovery code
  const loginWithRecoveryCode = async (email: string, code: string): Promise<RecoveryCodeAuthResult> => {
    try {
      const result = await passkeyAuth.useRecoveryCode(email, code);

      setSessionToken(result.session_token);
      setUser(result.user);

      return result;
    } catch (error) {
      console.error("Recovery code login failed:", error);
      throw error;
    }
  };

  // Acknowledge recovery codes
  const acknowledgeRecoveryCodes = async (): Promise<void> => {
    if (!sessionToken) {
      throw new Error("No active session");
    }

    try {
      await passkeyAuth.acknowledgeRecoveryCodes(sessionToken);
    } catch (error) {
      console.error("Failed to acknowledge recovery codes:", error);
      throw error;
    }
  };

  // Validate session token
  const validateSession = async (token: string): Promise<boolean> => {
    try {
      const validatedUser = await passkeyAuth.validateSession(token);

      if (validatedUser) {
        // Update user data if changed
        setUser(validatedUser);
        localStorage.setItem(USER_DATA_KEY, JSON.stringify(validatedUser));
        return true;
      }

      return false;
    } catch (error) {
      console.error("Session validation failed:", error);
      return false;
    }
  };

  // Logout
  const logout = () => {
    passkeyAuth.logout();
    setUser(null);
    setSessionToken(null);
  };

  // Computed value
  const isAuthenticated = !!user && !!sessionToken;

  const value: AuthContextType = {
    user,
    sessionToken,
    isLoading,
    isAuthenticated,
    register,
    login,
    loginWithRecoveryCode,
    acknowledgeRecoveryCodes,
    validateSession,
    logout,
    checkAuth,
  };

  return <AuthContext value={value}>{children}</AuthContext>;
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = use(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default AuthContext;
