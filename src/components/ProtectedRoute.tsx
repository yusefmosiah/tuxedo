import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Login } from './Login';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/chat'
}) => {
  const { isAuthenticated, isLoading, checkAuth } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Check for magic link token in URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (token) {
      // Magic link detected, validate it
      const validateMagicLink = async () => {
        try {
          const response = await fetch(`http://localhost:8000/auth/magic-link/validate?token=${token}`);

          if (response.ok) {
            // The backend will set a cookie and redirect to frontend
            // For now, we'll manually handle the validation
            const validateResponse = await fetch('http://localhost:8000/auth/validate-session', {
              method: 'POST',
              credentials: 'include', // Include cookies
            });

            if (validateResponse.ok) {
              const data = await validateResponse.json();
              if (data.success && data.session_token) {
                // Store session data
                localStorage.setItem('session_token', data.session_token);
                localStorage.setItem('user_data', JSON.stringify(data.user));

                // Clean URL
                window.history.replaceState({}, '', window.location.pathname);

                // Re-check authentication and redirect
                await checkAuth();
                navigate(redirectTo);
              }
            }
          } else {
            console.error('Magic link validation failed');
            // Clean URL on failure
            window.history.replaceState({}, '', window.location.pathname);
          }
        } catch (error) {
          console.error('Error validating magic link:', error);
          // Clean URL on error
          window.history.replaceState({}, '', window.location.pathname);
        }
      };

      validateMagicLink();
    }
  }, [checkAuth, navigate, redirectTo]);

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: 'var(--color-bg-primary)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontSize: '48px',
            marginBottom: '16px'
          }}>
            🤖
          </div>
          <p style={{
            fontFamily: 'var(--font-primary-sans)',
            fontSize: '18px',
            color: 'var(--color-text-secondary)',
            margin: 0
          }}>
            Checking authentication...
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => navigate(redirectTo)} />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;