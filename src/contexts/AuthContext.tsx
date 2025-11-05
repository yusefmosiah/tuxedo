import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Types
interface User {
  id: string;
  email: string;
  public_key?: string | null;
  last_login?: string | null;
}

interface AuthContextType {
  user: User | null;
  sessionToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string) => Promise<void>;
  requestMagicLink: (email: string) => Promise<{ success: boolean; message: string }>;
  validateSession: (token: string) => Promise<boolean>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const SESSION_TOKEN_KEY = 'session_token';
const USER_DATA_KEY = 'user_data';

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
      console.error('Auth check failed:', error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  // Request magic link
  const requestMagicLink = async (email: string): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch('http://localhost:8000/auth/magic-link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Magic link request failed:', error);
      return {
        success: false,
        message: 'Failed to send magic link. Please try again.'
      };
    }
  };

  // Validate session token
  const validateSession = async (token: string): Promise<boolean> => {
    try {
      const response = await fetch('http://localhost:8000/auth/validate-session', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

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
      console.error('Session validation failed:', error);
      return false;
    }
  };

  // Handle magic link callback (after email redirect)
  const login = async (email: string): Promise<void> => {
    // This will be called after magic link validation
    // The actual login happens via magic link validation redirect
    // For now, we'll trigger a re-check
    await checkAuth();
  };

  // Logout
  const logout = () => {
    setUser(null);
    setSessionToken(null);
    localStorage.removeItem(SESSION_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
  };

  // Computed value
  const isAuthenticated = !!user && !!sessionToken;

  const value: AuthContextType = {
    user,
    sessionToken,
    isLoading,
    isAuthenticated,
    login,
    requestMagicLink,
    validateSession,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;