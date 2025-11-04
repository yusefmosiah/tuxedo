import { Routes, Route, Outlet, NavLink } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";

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
              Dashboard
            </button>
          )}
        </NavLink>
      </div>
    </header>

    <Outlet />
  </main>
);


function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        </Route>
    </Routes>
  );
}

export default App;
