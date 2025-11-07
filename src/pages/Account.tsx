import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext_passkey";

/**
 * Account page - redirects to security settings
 * This provides a landing page for /account that redirects to /account/security
 */
export const Account: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/dashboard");
    } else {
      // Redirect to security settings
      navigate("/account/security", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  return null;
};

export default Account;
