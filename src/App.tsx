import ConnectAccount from "./components/ConnectAccount.tsx";
import { Routes, Route, Outlet, NavLink } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import { TuxMiningDashboard } from "./components/TuxMiningDashboard";
import { Heading, Content } from "@stellar/design-system";

const AppLayout: React.FC = () => (
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
              Pools
            </button>
          )}
        </NavLink>
        <NavLink
          to="/tux-mining"
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
              🪙 Tux Mining
            </button>
          )}
        </NavLink>
        <ConnectAccount />
      </div>
    </header>

    <Outlet />
  </main>
);

const TuxMiningPage: React.FC = () => {
  return (
    <div style={{ padding: "24px" }}>
      <Heading size="lg" spacing="md">
        🪙 Tux Mining - Automatic Wallet Integration
      </Heading>

      <Content>
        <TuxMiningDashboard />
      </Content>
    </div>
  );
};

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/tux-mining" element={<TuxMiningPage />} />
      </Route>
    </Routes>
  );
}

export default App;
