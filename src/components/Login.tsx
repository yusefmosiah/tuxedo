import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Button, Input, Text } from "@stellar/design-system";
import { useAuth } from "../contexts/AuthContext_passkey";

interface LoginProps {
  onLoginSuccess?: () => void;
}

type AuthMode = "signin" | "signup" | "recovery";

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState("");
  const [recoveryCode, setRecoveryCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [authMode, setAuthMode] = useState<AuthMode>("signin");
  const [recoveryCodes, setRecoveryCodes] = useState<string[] | null>(null);
  const [message, setMessage] = useState<{
    type: "success" | "error" | "info";
    text: string;
  } | null>(null);
  const {
    register,
    login,
    loginWithRecoveryCode,
    acknowledgeRecoveryCodes,
    isPasskeySupported,
  } = useAuth();

  // Log passkey support status on component mount
  React.useEffect(() => {
    console.log("Login component mounted");
    console.log("Passkey supported:", isPasskeySupported);
    console.log("Current auth mode:", authMode);
  }, []);

  const handlePasskeyAuth = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      setMessage({ type: "error", text: "Please enter your email address" });
      return;
    }

    if (!isPasskeySupported) {
      setMessage({
        type: "error",
        text: "Passkeys are not supported in your browser. Please use a modern browser like Chrome, Safari, or Edge.",
      });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      if (authMode === "signup") {
        // Register new user
        const result = await register(email);
        setRecoveryCodes(result.recovery_codes);
        setMessage({
          type: "success",
          text: "Registration successful! Please save your recovery codes.",
        });
      } else {
        // Authenticate existing user
        await login(email);
        setMessage({
          type: "success",
          text: "Successfully signed in!",
        });
        onLoginSuccess?.();
      }
    } catch (error: any) {
      console.error("Authentication error:", error);

      // Check if error indicates user doesn't exist (should register)
      if (authMode === "signin" && error.message?.includes("not found")) {
        setMessage({
          type: "info",
          text: "No account found. Please sign up first.",
        });
        setAuthMode("signup");
      } else if (
        authMode === "signup" &&
        error.message?.includes("already exists")
      ) {
        setMessage({
          type: "info",
          text: "Account already exists. Please sign in.",
        });
        setAuthMode("signin");
      } else {
        setMessage({
          type: "error",
          text: error.message || "Authentication failed. Please try again.",
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecoveryAuth = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim() || !recoveryCode.trim()) {
      setMessage({
        type: "error",
        text: "Please enter both email and recovery code",
      });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      await loginWithRecoveryCode(email, recoveryCode);
      setMessage({
        type: "success",
        text: "Successfully signed in with recovery code!",
      });
      onLoginSuccess?.();
    } catch (error: any) {
      console.error("Recovery code error:", error);
      setMessage({
        type: "error",
        text: error.message || "Invalid recovery code. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAcknowledgeCodes = async () => {
    try {
      await acknowledgeRecoveryCodes();
      onLoginSuccess?.();
    } catch (error) {
      console.error("Failed to acknowledge codes:", error);
      // Still proceed to success
      onLoginSuccess?.();
    }
  };

  const downloadRecoveryCodes = () => {
    if (!recoveryCodes) return;

    const content = `Tuxedo AI - Recovery Codes\n\nEmail: ${email}\nGenerated: ${new Date().toLocaleString()}\n\n${recoveryCodes.join("\n")}\n\nIMPORTANT: Store these codes securely. You can use them to access your account if you lose your passkey.`;

    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `tuxedo-recovery-codes-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Show recovery codes after registration
  if (recoveryCodes) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
          backgroundColor: "var(--color-bg-primary)",
          padding: "20px",
        }}
      >
        <div
          style={{
            maxWidth: "500px",
            width: "100%",
            padding: "40px",
            backgroundColor: "var(--color-bg-surface)",
            borderRadius: "var(--border-radius-lg)",
            border: "1px solid var(--color-border)",
            boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
          }}
        >
          <div style={{ textAlign: "center", marginBottom: "24px" }}>
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>🔐</div>
            <Text
              as="h1"
              size="lg"
              weight="bold"
              style={{ marginBottom: "8px" }}
            >
              Save Your Recovery Codes
            </Text>
            <Text
              as="p"
              size="sm"
              style={{ color: "var(--color-text-secondary)" }}
            >
              These codes can be used to access your account if you lose your
              passkey
            </Text>
          </div>

          <div
            style={{
              padding: "20px",
              backgroundColor: "var(--color-bg-primary)",
              borderRadius: "var(--border-radius-md)",
              border: "1px solid var(--color-border)",
              marginBottom: "20px",
            }}
          >
            {recoveryCodes.map((code, index) => (
              <div
                key={index}
                style={{
                  fontFamily: "var(--font-tertiary-mono)",
                  fontSize: "14px",
                  padding: "8px",
                  backgroundColor:
                    index % 2 === 0 ? "var(--color-bg-surface)" : "transparent",
                  borderRadius: "var(--border-radius-sm)",
                }}
              >
                {code}
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: "12px", marginBottom: "20px" }}>
            <Button
              variant="secondary"
              size="md"
              onClick={downloadRecoveryCodes}
              isFullWidth
            >
              📥 Download Codes
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={handleAcknowledgeCodes}
              isFullWidth
            >
              I've Saved My Codes
            </Button>
          </div>

          <div
            style={{
              padding: "16px",
              backgroundColor: "rgba(239, 68, 68, 0.1)",
              border: "1px solid var(--color-negative)",
              borderRadius: "var(--border-radius-md)",
            }}
          >
            <Text
              as="p"
              size="xs"
              style={{
                color: "var(--color-negative)",
                margin: 0,
                textAlign: "center",
              }}
            >
              ⚠️ Important: Store these codes in a secure location. They cannot
              be recovered if lost.
            </Text>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        backgroundColor: "var(--color-bg-primary)",
        padding: "20px",
      }}
    >
      <div
        style={{
          maxWidth: "400px",
          width: "100%",
          padding: "40px",
          backgroundColor: "var(--color-bg-surface)",
          borderRadius: "var(--border-radius-lg)",
          border: "1px solid var(--color-border)",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>🤖</div>
          <Text as="h1" size="lg" weight="bold" style={{ marginBottom: "8px" }}>
            Welcome to Tuxedo AI
          </Text>
          <Text
            as="p"
            size="sm"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {authMode === "recovery"
              ? "Sign in with your recovery code"
              : authMode === "signup"
                ? "Create your account with a passkey"
                : "Sign in with your passkey"}
          </Text>
          <div style={{ marginTop: "16px" }}>
            <Link
              to="/dashboard"
              style={{
                fontSize: "12px",
                color: "var(--color-stellar-glow-strong)",
                textDecoration: "none",
                opacity: 0.8,
                transition: "opacity 0.2s ease",
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.opacity = "1";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.opacity = "0.8";
              }}
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>

        {!isPasskeySupported && (
          <div
            style={{
              marginBottom: "20px",
              padding: "12px 16px",
              borderRadius: "var(--border-radius-md)",
              backgroundColor: "rgba(239, 68, 68, 0.1)",
              border: "1px solid var(--color-negative)",
            }}
          >
            <Text
              as="p"
              size="sm"
              style={{
                color: "var(--color-negative)",
                margin: 0,
              }}
            >
              ⚠️ Your browser doesn't support passkeys. Please use a modern
              browser like Chrome, Safari, or Edge.
            </Text>
          </div>
        )}

        <form
          onSubmit={
            authMode === "recovery" ? handleRecoveryAuth : handlePasskeyAuth
          }
        >
          <div style={{ marginBottom: "20px" }}>
            <Input
              id="email-input"
              fieldSize="md"
              type="email"
              label="Email Address"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              required
            />
          </div>

          {authMode === "recovery" && (
            <div style={{ marginBottom: "20px" }}>
              <Input
                id="recovery-code-input"
                fieldSize="md"
                type="text"
                label="Recovery Code"
                placeholder="Enter your recovery code"
                value={recoveryCode}
                onChange={(e) => setRecoveryCode(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>
          )}

          <Button
            type="submit"
            variant="primary"
            size="md"
            isLoading={isLoading}
            disabled={
              isLoading ||
              !email.trim() ||
              (authMode === "recovery" && !recoveryCode.trim()) ||
              !isPasskeySupported
            }
            isFullWidth
          >
            {isLoading
              ? authMode === "recovery"
                ? "Verifying..."
                : authMode === "signup"
                  ? "Creating Account..."
                  : "Signing In..."
              : authMode === "recovery"
                ? "Sign In with Recovery Code"
                : authMode === "signup"
                  ? "Sign Up with Passkey"
                  : "Sign In with Passkey"}
          </Button>
        </form>

        {message && (
          <div
            style={{
              marginTop: "20px",
              padding: "12px 16px",
              borderRadius: "var(--border-radius-md)",
              backgroundColor:
                message.type === "success"
                  ? "rgba(52, 211, 153, 0.1)"
                  : message.type === "info"
                    ? "rgba(59, 130, 246, 0.1)"
                    : "rgba(239, 68, 68, 0.1)",
              border: `1px solid ${
                message.type === "success"
                  ? "var(--color-positive)"
                  : message.type === "info"
                    ? "var(--color-stellar-glow-strong)"
                    : "var(--color-negative)"
              }`,
            }}
          >
            <Text
              as="p"
              size="sm"
              style={{
                color:
                  message.type === "success"
                    ? "var(--color-positive)"
                    : message.type === "info"
                      ? "var(--color-stellar-glow-strong)"
                      : "var(--color-negative)",
                margin: 0,
                textAlign: "center",
              }}
            >
              {message.text}
            </Text>
          </div>
        )}

        <div
          style={{
            marginTop: "32px",
            paddingTop: "20px",
            borderTop: "1px solid var(--color-border)",
            display: "flex",
            flexDirection: "column",
            gap: "12px",
          }}
        >
          {authMode !== "recovery" && (
            <>
              <button
                type="button"
                onClick={() =>
                  setAuthMode(authMode === "signin" ? "signup" : "signin")
                }
                disabled={isLoading}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--color-stellar-glow-strong)",
                  fontSize: "14px",
                  cursor: isLoading ? "not-allowed" : "pointer",
                  textDecoration: "underline",
                  padding: 0,
                  opacity: isLoading ? 0.5 : 1,
                }}
              >
                {authMode === "signin"
                  ? "Don't have an account? Sign up"
                  : "Already have an account? Sign in"}
              </button>
              <button
                type="button"
                onClick={() => setAuthMode("recovery")}
                disabled={isLoading}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--color-text-tertiary)",
                  fontSize: "12px",
                  cursor: isLoading ? "not-allowed" : "pointer",
                  textDecoration: "underline",
                  padding: 0,
                  opacity: isLoading ? 0.5 : 1,
                }}
              >
                Lost your passkey? Use recovery code
              </button>
            </>
          )}
          {authMode === "recovery" && (
            <button
              type="button"
              onClick={() => {
                setAuthMode("signin");
                setRecoveryCode("");
              }}
              disabled={isLoading}
              style={{
                background: "none",
                border: "none",
                color: "var(--color-stellar-glow-strong)",
                fontSize: "14px",
                cursor: isLoading ? "not-allowed" : "pointer",
                textDecoration: "underline",
                padding: 0,
                opacity: isLoading ? 0.5 : 1,
              }}
            >
              ← Back to passkey sign in
            </button>
          )}

          <Text
            as="p"
            size="xs"
            style={{
              color: "var(--color-text-tertiary)",
              textAlign: "center",
              margin: "8px 0 0 0",
              lineHeight: 1.5,
            }}
          >
            {authMode === "recovery"
              ? "🔑 Use one of your backup recovery codes to access your account"
              : "🔐 Passkeys provide secure, passwordless authentication using your device's biometrics or PIN"}
          </Text>
        </div>
      </div>
    </div>
  );
};

export default Login;
