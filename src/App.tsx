import { Routes, Route, Outlet, NavLink } from "react-router-dom";
import { useNavigate } from "react-router-dom";
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
    navigate("/dashboard");
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
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
            style={({ isActive }) => ({
              textDecoration: "none",
              color: "var(--color-text-primary)",
              padding: "8px 16px",
              borderRadius: "4px",
              backgroundColor: isActive ? "var(--color-border)" : "transparent",
            })}
          >
            <Text size="sm" as="span">Dashboard</Text>
          </NavLink>

          {isAuthenticated && (
            <NavLink
              to="/chat"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              style={({ isActive }) => ({
                textDecoration: "none",
                color: "var(--color-text-primary)",
                padding: "8px 16px",
                borderRadius: "4px",
                backgroundColor: isActive ? "var(--color-border)" : "transparent",
              })}
            >
              <Text size="sm" as="span">Chat</Text>
            </NavLink>
          )}

          {isAuthenticated && (
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Text size="sm" as="span" style={{ color: "var(--color-text-secondary)" }}>
                {user?.email}
              </Text>
              <Button size="sm" variant="tertiary" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div style={{ padding: "24px" }}>
        <Outlet />
      </div>
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
      </Route>
    </Routes>
  );
}

export default App;