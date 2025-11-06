import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext_passkey";
import { Login } from "./Login";

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = "/chat",
}) => {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
          backgroundColor: "var(--color-bg-primary)",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div
            style={{
              fontSize: "48px",
              marginBottom: "16px",
            }}
          >
            🤖
          </div>
          <p
            style={{
              fontFamily: "var(--font-primary-sans)",
              fontSize: "18px",
              color: "var(--color-text-secondary)",
              margin: 0,
            }}
          >
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
