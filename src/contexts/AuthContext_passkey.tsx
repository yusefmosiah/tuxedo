import React, {
  createContext,
  use,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { passkeyAuthService, type User } from "../services/passkeyAuth";

// Types
interface AuthContextType {
  user: User | null;
  sessionToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  register: (email: string) => Promise<{
    user: User;
    recovery_codes: string[];
    recovery_codes_message: string;
  }>;
  login: (email: string) => Promise<void>;
  loginWithRecoveryCode: (email: string, code: string) => Promise<void>;
  acknowledgeRecoveryCodes: () => Promise<void>;
  validateSession: (token: string) => Promise<boolean>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  isPasskeySupported: boolean;
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

  // Check if passkeys are supported (with error handling)
  const isPasskeySupported = (() => {
    try {
      return passkeyAuthService.isSupported();
    } catch (error) {
      console.error("Error checking passkey support:", error);
      return false;
    }
  })();

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
        // Validate session with backend (with timeout and error handling)
        try {
          const validatedUser =
            await passkeyAuthService.validateSession(storedToken);

          if (validatedUser) {
            setSessionToken(storedToken);
            setUser(validatedUser);
          } else {
            // Clear invalid session
            console.warn("Session validation failed, clearing session");
            logout();
          }
        } catch (validationError) {
          // If validation fails (e.g., backend is down), keep the stored session
          // but log the error for debugging
          console.warn(
            "Could not validate session with backend:",
            validationError,
          );

          // Try to parse stored user data to maintain session
          try {
            const parsedUser = JSON.parse(storedUserData);
            setSessionToken(storedToken);
            setUser(parsedUser);
            console.info("Using cached session data (backend unavailable)");
          } catch (parseError) {
            console.error("Failed to parse stored user data:", parseError);
            logout();
          }
        }
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      // Don't throw - just clear auth state
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  // Register new user with passkey
  const register = async (
    email: string,
  ): Promise<{
    user: User;
    recovery_codes: string[];
    recovery_codes_message: string;
  }> => {
    try {
      const result = await passkeyAuthService.register(email);

      // Set auth state
      setUser(result.user);
      setSessionToken(result.session_token);

      return {
        user: result.user,
        recovery_codes: result.recovery_codes,
        recovery_codes_message: result.recovery_codes_message,
      };
    } catch (error) {
      console.error("Registration failed:", error);
      throw error;
    }
  };

  // Login with passkey
  const login = async (email: string): Promise<void> => {
    try {
      const result = await passkeyAuthService.authenticate(email);

      // Set auth state
      setUser(result.user);
      setSessionToken(result.session_token);
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  // Login with recovery code
  const loginWithRecoveryCode = async (
    email: string,
    code: string,
  ): Promise<void> => {
    try {
      const result = await passkeyAuthService.useRecoveryCode(email, code);

      // Set auth state
      setUser(result.user);
      setSessionToken(result.session_token);
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
      await passkeyAuthService.acknowledgeRecoveryCodes(sessionToken);
    } catch (error) {
      console.error("Failed to acknowledge recovery codes:", error);
      throw error;
    }
  };

  // Validate session token
  const validateSession = async (token: string): Promise<boolean> => {
    try {
      const validatedUser = await passkeyAuthService.validateSession(token);

      if (validatedUser) {
        // Update user data if changed
        setUser(validatedUser);
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
    passkeyAuthService.logout();
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
    isPasskeySupported,
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
