import { Layout, Button } from "@stellar/design-system";
import "./App.module.css";
import ConnectAccount from "./components/ConnectAccount.tsx";
import { Routes, Route, Outlet, NavLink } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";

const AppLayout: React.FC = () => (
  <main>
    <Layout.Header
      projectId="Tuxedo AI"
      projectTitle="Tuxedo AI"
      contentRight={
        <>
          <NavLink
            to="/dashboard"
            style={{ textDecoration: "none", marginRight: "12px" }}
          >
            {({ isActive }) => (
              <Button
                variant={isActive ? "primary" : "tertiary"}
                size="md"
                onClick={() => (window.location.href = "/dashboard")}
              >
                📊 Dashboard
              </Button>
            )}
          </NavLink>
          <ConnectAccount />
        </>
      }
    />
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
