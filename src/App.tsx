import { Routes, Route, Outlet, NavLink } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Account from "./pages/Account";
import AccountSecurity from "./pages/AccountSecurity";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./contexts/AuthContext_passkey";
import { useWalletContext } from "./contexts/WalletContext";
import { Button, Text } from "@stellar/design-system";
import { DebugPanel } from "./components/DebugPanel";

const AppLayout: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const wallet = useWalletContext();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/dashboard");
  };

  const handleWalletConnect = async () => {
    try {
      await wallet.connectWallet();
    } catch (error) {
      console.error("Failed to connect wallet:", error);
    }
  };

  return (
    <main
      style={{
        backgroundColor: "var(--color-bg-primary)",
        minHeight: "100vh",
        color: "var(--color-text-primary)",
      }}
    >
      {/* Custom Header */}
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "12px 24px",
          backgroundColor: "var(--color-bg-surface)",
          borderBottom: "1px solid var(--color-border)",
          height: "60px",
        }}
      >
        <div
          style={{
            fontFamily: "var(--font-primary-serif)",
            fontSize: "20px",
            fontWeight: "bold",
            color: "var(--color-text-primary)",
          }}
        >
          🤖 Tuxedo AI
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <NavLink to="/dashboard" style={{ textDecoration: "none" }}>
            {({ isActive }) => (
              <button
                className={isActive ? "btn-stellar" : "btn-secondary"}
                style={{
                  fontSize: "12px",
                  fontFamily: "var(--font-tertiary-mono)",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  padding: "8px 16px",
                }}
              >
                Dashboard
              </button>
            )}
          </NavLink>
          <NavLink to="/chat" style={{ textDecoration: "none" }}>
            {({ isActive }) => (
              <button
                className={isActive ? "btn-stellar" : "btn-secondary"}
                style={{
                  fontSize: "12px",
                  fontFamily: "var(--font-tertiary-mono)",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  padding: "8px 16px",
                }}
              >
                AI Chat
              </button>
            )}
          </NavLink>

          {/* Wallet Connection Button */}
          {wallet.isConnected && wallet.address ? (
            <div
              onClick={wallet.disconnectWallet}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "4px 12px",
                backgroundColor: "var(--color-bg-primary)",
                borderRadius: "var(--border-radius-md)",
                border: "1px solid var(--color-border)",
                cursor: "pointer",
              }}
              title="Click to disconnect wallet"
            >
              <div
                style={{
                  width: "24px",
                  height: "24px",
                  borderRadius: "50%",
                  backgroundColor: "var(--color-stellar-glow-subtle)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "12px",
                }}
              >
                {wallet.mode === 'external' ? '👛' : '🤖'}
              </div>
              <Text as="span" size="sm" style={{ margin: 0 }}>
                {wallet.address.slice(0, 6)}...{wallet.address.slice(-4)}
              </Text>
            </div>
          ) : (
            <Button
              variant="secondary"
              size="sm"
              onClick={handleWalletConnect}
              style={{
                fontSize: "12px",
                fontFamily: "var(--font-tertiary-mono)",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                padding: "8px 16px",
              }}
            >
              👛 Connect Wallet
            </Button>
          )}

          {isAuthenticated && user && (
            <>
              <NavLink to="/account/security" style={{ textDecoration: "none" }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "4px 12px",
                    backgroundColor: "var(--color-bg-primary)",
                    borderRadius: "var(--border-radius-md)",
                    border: "1px solid var(--color-border)",
                    cursor: "pointer",
                  }}
                >
                  <div
                    style={{
                      width: "24px",
                      height: "24px",
                      borderRadius: "50%",
                      backgroundColor: "var(--color-stellar-glow-subtle)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "12px",
                    }}
                  >
                    👤
                  </div>
                  <Text as="span" size="sm" style={{ margin: 0 }}>
                    {user.email}
                  </Text>
                </div>
              </NavLink>
              <Button
                variant="tertiary"
                size="sm"
                onClick={handleLogout}
                style={{
                  fontSize: "12px",
                  fontFamily: "var(--font-tertiary-mono)",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  padding: "8px 16px",
                }}
              >
                Logout
              </Button>
            </>
          )}
        </div>
      </header>

      <Outlet />

      {/* Debug Panel for Passkey Authentication */}
      <DebugPanel />
    </main>
  );
};

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route
          path="/account"
          element={
            <ProtectedRoute>
              <Account />
            </ProtectedRoute>
          }
        />
        <Route
          path="/account/security"
          element={
            <ProtectedRoute>
              <AccountSecurity />
            </ProtectedRoute>
          }
        />
      </Route>
    </Routes>
  );
}

export default App;
