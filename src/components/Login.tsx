import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button, Input, Text } from '@stellar/design-system';
import { useAuth } from '../contexts/AuthContext';

interface LoginProps {
  onLoginSuccess?: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const { requestMagicLink } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      setMessage({ type: 'error', text: 'Please enter your email address' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const result = await requestMagicLink(email);

      if (result.success) {
        setMessage({
          type: 'success',
          text: 'Magic link sent! Check your email and click the link to sign in.'
        });
        setEmail(''); // Clear the form

        // Poll for authentication status
        const checkAuthStatus = setInterval(async () => {
          // Check URL for magic link token
          const urlParams = new URLSearchParams(window.location.search);
          const token = urlParams.get('token');

          if (token) {
            // Magic link detected, redirect will happen automatically
            clearInterval(checkAuthStatus);
            return;
          }

          // Check if user is now authenticated (in case they opened link in another tab)
          const storedToken = localStorage.getItem('session_token');
          if (storedToken) {
            clearInterval(checkAuthStatus);
            onLoginSuccess?.();
          }
        }, 2000);

        // Stop polling after 5 minutes
        setTimeout(() => clearInterval(checkAuthStatus), 300000);
      } else {
        setMessage({ type: 'error', text: result.message || 'Failed to send magic link' });
      }
    } catch (error) {
      console.error('Login error:', error);
      setMessage({ type: 'error', text: 'Something went wrong. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: 'var(--color-bg-primary)',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '400px',
        width: '100%',
        padding: '40px',
        backgroundColor: 'var(--color-bg-surface)',
        borderRadius: 'var(--border-radius-lg)',
        border: '1px solid var(--color-border)',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            fontSize: '48px',
            marginBottom: '16px'
          }}>
            🤖
          </div>
          <Text as="h1" size="lg" weight="bold" style={{ marginBottom: '8px' }}>
            Welcome to Tuxedo AI
          </Text>
          <Text as="p" size="sm" style={{ color: 'var(--color-text-secondary)' }}>
            Sign in with your email to access the AI assistant
          </Text>
          <div style={{ marginTop: '16px' }}>
            <Link
              to="/dashboard"
              style={{
                fontSize: '12px',
                color: 'var(--color-stellar-glow-strong)',
                textDecoration: 'none',
                opacity: 0.8,
                transition: 'opacity 0.2s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.opacity = '1';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.opacity = '0.8';
              }}
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <Input
              type="email"
              label="Email Address"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              required
            />
          </div>

          <Button
            type="submit"
            variant="primary"
            size="md"
            isLoading={isLoading}
            disabled={isLoading || !email.trim()}
            fullWidth
          >
            {isLoading ? 'Sending Magic Link...' : 'Send Magic Link'}
          </Button>
        </form>

        {message && (
          <div style={{
            marginTop: '20px',
            padding: '12px 16px',
            borderRadius: 'var(--border-radius-md)',
            backgroundColor: message.type === 'success'
              ? 'rgba(52, 211, 153, 0.1)'
              : 'rgba(239, 68, 68, 0.1)',
            border: `1px solid ${message.type === 'success'
              ? 'var(--color-positive)'
              : 'var(--color-negative)'}`,
          }}>
            <Text
              as="p"
              size="sm"
              style={{
                color: message.type === 'success'
                  ? 'var(--color-positive)'
                  : 'var(--color-negative)',
                margin: 0,
                textAlign: 'center'
              }}
            >
              {message.text}
            </Text>
            {message.type === 'success' && (
              <Text
                as="p"
                size="xs"
                style={{
                  color: 'var(--color-text-secondary)',
                  margin: '8px 0 0 0',
                  textAlign: 'center',
                  fontStyle: 'italic'
                }}
              >
                📧 Don't see the email? Check your spam folder and mark "Not Spam" to ensure delivery.
              </Text>
            )}
          </div>
        )}

        <div style={{
          marginTop: '32px',
          paddingTop: '20px',
          borderTop: '1px solid var(--color-border)'
        }}>
          <Text as="p" size="xs" style={{
            color: 'var(--color-text-tertiary)',
            textAlign: 'center',
            margin: '0 0 8px 0',
            lineHeight: 1.5
          }}>
            We'll send you a magic link that signs you in instantly.
            No password needed!
          </Text>
          <Text as="p" size="xs" style={{
            color: 'var(--color-text-tertiary)',
            textAlign: 'center',
            margin: 0,
            lineHeight: 1.4,
            fontStyle: 'italic'
          }}>
            📧 Pro tip: Check your spam folder if you don't see the email within 30 seconds
          </Text>
        </div>
      </div>
    </div>
  );
};

export default Login;