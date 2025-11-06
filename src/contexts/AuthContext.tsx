import React, {
  createContext,
  use,
  useState,
  useEffect,
  ReactNode,
} from "react";
import {
  passkeyService,
  type PasskeyRegistrationResult,
  type PasskeyAuthenticationResult,
} from "../services/passkeyAuth";

// Types
interface User {
  id: string;
  email: string;
  public_key?: string | null;
  stellar_public_key?: string | null;
  last_login?: string | null;
}

interface AuthContextType {
  user: User | null;
  sessionToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email?: string) => Promise<void>;
  validateSession: (token: string) => Promise<boolean>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  // Passkey methods
  registerWithPasskey: (email: string) => Promise<PasskeyRegistrationResult>;
  authenticateWithPasskey: (
    email?: string,
  ) => Promise<PasskeyAuthenticationResult>;
  useRecoveryCode: (code: string) => Promise<PasskeyAuthenticationResult>;
  isPasskeySupported: boolean;
  // Deprecated magic link method (for backward compatibility)
  requestMagicLink: (email: string) => Promise<{ success: boolean; message?: string }>;
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

  // Check if passkey is supported
  const isPasskeySupported = passkeyService.isSupported();

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
        // Try passkey session validation first
        let user = await passkeyService.validateSession(storedToken);

        // Fallback to magic link validation if passkey validation fails
        if (!user) {
          const isValid = await validateSession(storedToken);
          if (isValid) {
            user = JSON.parse(storedUserData);
          }
        }

        if (user) {
          setSessionToken(storedToken);
          setUser(user);
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

  // Magic link functionality removed - now using passkey authentication

  // Validate session token
  const validateSession = async (token: string): Promise<boolean> => {
    try {
      const response = await fetch(
        "http://localhost:8000/auth/validate-passkey-session",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ session_token: token }),
        },
      );

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Update user data if changed
          setUser(data.user);
          localStorage.setItem(USER_DATA_KEY, JSON.stringify(data.user));
          return true;
        }
      }
      return false;
    } catch (error) {
      console.error("Session validation failed:", error);
      return false;
    }
  };

  // Handle magic link callback (after email redirect)
  const login = async (email?: string): Promise<void> => {
    // Use passkey authentication
    setIsLoading(true);
    try {
      const result = await passkeyService.authenticate(email);
      if (result.success && result.user) {
        setUser(result.user);
        setSessionToken(result.session_token || null);
        localStorage.setItem(USER_DATA_KEY, JSON.stringify(result.user));
      } else {
        throw new Error(result.error || 'Authentication failed');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Logout
  const logout = () => {
    setUser(null);
    setSessionToken(null);
    localStorage.removeItem(SESSION_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
    passkeyService.logout();
  };

  // Passkey registration
  const registerWithPasskey = async (
    email: string,
  ): Promise<PasskeyRegistrationResult> => {
    setIsLoading(true);
    try {
      const result = await passkeyService.register(email);
      if (result.success && result.user) {
        setUser(result.user);
        setSessionToken(result.session_token || null);
      }
      return result;
    } finally {
      setIsLoading(false);
    }
  };

  // Passkey authentication
  const authenticateWithPasskey = async (
    email?: string,
  ): Promise<PasskeyAuthenticationResult> => {
    setIsLoading(true);
    try {
      const result = await passkeyService.authenticate(email);
      if (result.success && result.user) {
        setUser(result.user);
        setSessionToken(result.session_token || null);
      }
      return result;
    } finally {
      setIsLoading(false);
    }
  };

  // Recovery code authentication
  const useRecoveryCode = async (
    code: string,
  ): Promise<PasskeyAuthenticationResult> => {
    setIsLoading(true);
    try {
      const result = await passkeyService.useRecoveryCode(code);
      if (result.success && result.user) {
        setUser(result.user);
        setSessionToken(result.session_token || null);
      }
      return result;
    } finally {
      setIsLoading(false);
    }
  };

  // Deprecated magic link method (for backward compatibility)
  const requestMagicLink = async (_email: string): Promise<{ success: boolean; message?: string }> => {
    // Magic links have been replaced with passkey authentication
    // This method is kept for backward compatibility with old components
    return {
      success: false,
      message: "Magic links have been deprecated. Please use the new passkey authentication system."
    };
  };

  // Computed value
  const isAuthenticated = !!user && !!sessionToken;

  const value: AuthContextType = {
    user,
    sessionToken,
    isLoading,
    isAuthenticated,
    login,
    validateSession,
    logout,
    checkAuth,
    registerWithPasskey,
    authenticateWithPasskey,
    useRecoveryCode,
    isPasskeySupported,
    requestMagicLink,
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
