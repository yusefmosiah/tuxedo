import { Routes, Route, Outlet, NavLink } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./contexts/AuthContext";
import { Button, Text } from "@stellar/design-system";

const AppLayout: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/dashboard');
  };

  return (
    <main style={{
      backgroundColor: 'var(--color-bg-primary)',
      minHeight: '100vh',
      color: 'var(--color-text-primary)'
    }}>
      {/* Custom Header */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '12px 24px',
        backgroundColor: 'var(--color-bg-surface)',
        borderBottom: '1px solid var(--color-border)',
        height: '60px'
      }}>
        <div style={{
          fontFamily: 'var(--font-primary-serif)',
          fontSize: '20px',
          fontWeight: 'bold',
          color: 'var(--color-text-primary)'
        }}>
          🤖 Tuxedo AI
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <NavLink
            to="/dashboard"
            style={{ textDecoration: "none" }}
          >
            {({ isActive }) => (
              <button
                className={isActive ? "btn-stellar" : "btn-secondary"}
                style={{
                  fontSize: '12px',
                  fontFamily: 'var(--font-tertiary-mono)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  padding: '8px 16px'
                }}
              >
                Dashboard
              </button>
            )}
          </NavLink>
          <NavLink
            to="/chat"
            style={{ textDecoration: "none" }}
          >
            {({ isActive }) => (
              <button
                className={isActive ? "btn-stellar" : "btn-secondary"}
                style={{
                  fontSize: '12px',
                  fontFamily: 'var(--font-tertiary-mono)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  padding: '8px 16px'
                }}
              >
                AI Chat
              </button>
            )}
          </NavLink>

          {isAuthenticated && user && (
            <>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '4px 12px',
                backgroundColor: 'var(--color-bg-primary)',
                borderRadius: 'var(--border-radius-md)',
                border: '1px solid var(--color-border)'
              }}>
                <div style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-stellar-glow-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px'
                }}>
                  👤
                </div>
                <Text size="sm" style={{ margin: 0 }}>
                  {user.email}
                </Text>
              </div>
              <Button
                variant="tertiary"
                size="sm"
                onClick={handleLogout}
                style={{
                  fontSize: '12px',
                  fontFamily: 'var(--font-tertiary-mono)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  padding: '8px 16px'
                }}
              >
                Logout
              </Button>
            </>
          )}
        </div>
      </header>

      <Outlet />
    </main>
  );
};

// Magic Link Validation Component
const MagicLinkValidation: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const validateMagicLink = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');

      if (!token) {
        navigate('/chat');
        return;
      }

      try {
        // Validate the magic link token with the backend
        const response = await fetch(`http://localhost:8000/auth/magic-link/validate?token=${token}`);

        if (response.ok) {
          // Get session token from backend
          const validateResponse = await fetch('http://localhost:8000/auth/validate-session', {
            method: 'POST',
            credentials: 'include',
          });

          if (validateResponse.ok) {
            const data = await validateResponse.json();
            if (data.success && data.session_token) {
              // Store session data
              localStorage.setItem('session_token', data.session_token);
              localStorage.setItem('user_data', JSON.stringify(data.user));
            }
          }
        }

        // Redirect to chat after validation (success or failure)
        navigate('/chat');
      } catch (error) {
        console.error('Error validating magic link:', error);
        navigate('/chat');
      }
    };

    validateMagicLink();
  }, [navigate]);

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
          Validating your magic link...
        </p>
      </div>
    </div>
  );
};

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/chat" element={
          <ProtectedRoute>
            <Home />
          </ProtectedRoute>
        } />
        </Route>
      {/* Magic Link Validation Route (outside main layout) */}
      <Route path="/auth/magic-link" element={<MagicLinkValidation />} />
    </Routes>
  );
}

export default App;
