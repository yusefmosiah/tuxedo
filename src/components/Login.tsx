import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button, Input, Text } from "@stellar/design-system";
import { useAuth } from "../contexts/AuthContext";
import { passkeyAuth } from "../services/passkeyAuth";

interface LoginProps {
  onLoginSuccess?: () => void;
}

type AuthMode = "signin" | "signup" | "recovery";

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const navigate = useNavigate();
  const { register, login, loginWithRecoveryCode } = useAuth();
  const [mode, setMode] = useState<AuthMode>("signin");
  const [email, setEmail] = useState("");
  const [recoveryCode, setRecoveryCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [recoveryCodes, setRecoveryCodes] = useState<string[] | null>(null);
  const [message, setMessage] = useState<{
    type: "success" | "error" | "info";
    text: string;
  } | null>(null);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      setMessage({ type: "error", text: "Please enter your email address" });
      return;
    }

    if (!passkeyAuth.isSupported()) {
      setMessage({
        type: "error",
        text: "Passkeys are not supported in your browser. Please use a modern browser like Chrome, Edge, Safari, or Firefox.",
      });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      await login(email);

      setMessage({
        type: "success",
        text: "Successfully signed in!",
      });

      // Redirect after short delay
      setTimeout(() => {
        onLoginSuccess?.();
        navigate("/chat");
      }, 500);
    } catch (error: any) {
      console.error("Sign in error:", error);
      setMessage({
        type: "error",
        text: error.message || "Failed to sign in. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      setMessage({ type: "error", text: "Please enter your email address" });
      return;
    }

    if (!passkeyAuth.isSupported()) {
      setMessage({
        type: "error",
        text: "Passkeys are not supported in your browser. Please use a modern browser like Chrome, Edge, Safari, or Firefox.",
      });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const result = await register(email);

      // Show recovery codes
      setRecoveryCodes(result.recovery_codes);
      setMessage({
        type: "success",
        text: "Account created successfully! Please save your recovery codes.",
      });
    } catch (error: any) {
      console.error("Sign up error:", error);
      setMessage({
        type: "error",
        text: error.message || "Failed to create account. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecoveryCodeSignIn = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim() || !recoveryCode.trim()) {
      setMessage({ type: "error", text: "Please enter your email and recovery code" });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const result = await loginWithRecoveryCode(email, recoveryCode);

      setMessage({
        type: "success",
        text: `Successfully signed in! You have ${result.remaining_codes} recovery codes remaining.`,
      });

      // Redirect after short delay
      setTimeout(() => {
        onLoginSuccess?.();
        navigate("/chat");
      }, 500);
    } catch (error: any) {
      console.error("Recovery code sign in error:", error);
      setMessage({
        type: "error",
        text: error.message || "Invalid recovery code. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAcknowledgeRecoveryCodes = async () => {
    try {
      setIsLoading(true);
      // Codes are already acknowledged during registration
      // Just redirect to chat
      onLoginSuccess?.();
      navigate("/chat");
    } catch (error: any) {
      console.error("Acknowledgment error:", error);
      // Still redirect even if acknowledgment fails
      navigate("/chat");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyRecoveryCodes = () => {
    if (recoveryCodes) {
      const codesText = recoveryCodes.map((code, i) => `${i + 1}. ${code}`).join("\n");
      navigator.clipboard.writeText(codesText);
      setMessage({
        type: "info",
        text: "Recovery codes copied to clipboard!",
      });
    }
  };

  // If showing recovery codes, show that UI
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
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>🔑</div>
            <Text as="h1" size="lg" weight="bold" style={{ marginBottom: "8px" }}>
              Save Your Recovery Codes
            </Text>
            <Text
              as="p"
              size="sm"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Store these codes in a safe place. Each code can only be used once.
            </Text>
          </div>

          <div
            style={{
              backgroundColor: "rgba(255, 243, 205, 0.1)",
              border: "1px solid rgba(255, 243, 205, 0.5)",
              borderRadius: "var(--border-radius-md)",
              padding: "20px",
              marginBottom: "20px",
            }}
          >
            <Text
              as="p"
              size="sm"
              weight="bold"
              style={{ marginBottom: "12px", color: "var(--color-warning)" }}
            >
              ⚠️ Important: Save these codes now!
            </Text>
            <div
              style={{
                fontFamily: "monospace",
                fontSize: "12px",
                backgroundColor: "var(--color-bg-primary)",
                padding: "16px",
                borderRadius: "var(--border-radius-sm)",
                marginBottom: "12px",
              }}
            >
              {recoveryCodes.map((code, i) => (
                <div key={i} style={{ padding: "4px 0" }}>
                  {i + 1}. {code}
                </div>
              ))}
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={handleCopyRecoveryCodes}
              isFullWidth
            >
              📋 Copy All Codes
            </Button>
          </div>

          <Button
            variant="primary"
            size="md"
            onClick={handleAcknowledgeRecoveryCodes}
            isLoading={isLoading}
            isFullWidth
          >
            I've Saved My Recovery Codes
          </Button>

          {message && message.type === "info" && (
            <div
              style={{
                marginTop: "16px",
                padding: "8px 12px",
                borderRadius: "var(--border-radius-sm)",
                backgroundColor: "rgba(59, 130, 246, 0.1)",
                border: "1px solid rgba(59, 130, 246, 0.3)",
                textAlign: "center",
              }}
            >
              <Text as="p" size="xs" style={{ color: "var(--color-info)", margin: 0 }}>
                {message.text}
              </Text>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Main login/signup UI
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
            {mode === "signin"
              ? "Sign in with your passkey"
              : mode === "signup"
                ? "Create your account with a passkey"
                : "Sign in with a recovery code"}
          </Text>
          <div style={{ marginTop: "16px" }}>
            <Link
              to="/dashboard"
              style={{
                fontSize: "12px",
                color: "var(--color-stellar-glow-strong)",
                textDecoration: "none",
                opacity: 0.8,
              }}
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Mode switcher */}
        {mode !== "recovery" && (
          <div
            style={{
              display: "flex",
              gap: "8px",
              marginBottom: "24px",
              padding: "4px",
              backgroundColor: "var(--color-bg-primary)",
              borderRadius: "var(--border-radius-md)",
            }}
          >
            <button
              onClick={() => setMode("signin")}
              style={{
                flex: 1,
                padding: "8px",
                border: "none",
                borderRadius: "var(--border-radius-sm)",
                backgroundColor:
                  mode === "signin"
                    ? "var(--color-bg-surface)"
                    : "transparent",
                color:
                  mode === "signin"
                    ? "var(--color-text-primary)"
                    : "var(--color-text-secondary)",
                fontWeight: mode === "signin" ? "bold" : "normal",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              Sign In
            </button>
            <button
              onClick={() => setMode("signup")}
              style={{
                flex: 1,
                padding: "8px",
                border: "none",
                borderRadius: "var(--border-radius-sm)",
                backgroundColor:
                  mode === "signup"
                    ? "var(--color-bg-surface)"
                    : "transparent",
                color:
                  mode === "signup"
                    ? "var(--color-text-primary)"
                    : "var(--color-text-secondary)",
                fontWeight: mode === "signup" ? "bold" : "normal",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              Sign Up
            </button>
          </div>
        )}

        {/* Sign In / Sign Up Form */}
        {mode !== "recovery" && (
          <form onSubmit={mode === "signin" ? handleSignIn : handleSignUp}>
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

            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={isLoading}
              disabled={isLoading || !email.trim()}
              isFullWidth
            >
              {isLoading
                ? mode === "signin"
                  ? "Signing In..."
                  : "Creating Account..."
                : mode === "signin"
                  ? "Sign In with Passkey"
                  : "Create Account"}
            </Button>
          </form>
        )}

        {/* Recovery Code Form */}
        {mode === "recovery" && (
          <form onSubmit={handleRecoveryCodeSignIn}>
            <div style={{ marginBottom: "16px" }}>
              <Input
                id="recovery-email-input"
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

            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={isLoading}
              disabled={isLoading || !email.trim() || !recoveryCode.trim()}
              isFullWidth
            >
              {isLoading ? "Signing In..." : "Sign In with Recovery Code"}
            </Button>

            <Button
              type="button"
              variant="tertiary"
              size="sm"
              onClick={() => {
                setMode("signin");
                setRecoveryCode("");
                setMessage(null);
              }}
              isFullWidth
              style={{ marginTop: "12px" }}
            >
              Back to Passkey Sign In
            </Button>
          </form>
        )}

        {/* Recovery code link */}
        {mode === "signin" && (
          <div style={{ marginTop: "16px", textAlign: "center" }}>
            <button
              onClick={() => {
                setMode("recovery");
                setMessage(null);
              }}
              style={{
                background: "none",
                border: "none",
                color: "var(--color-stellar-glow-strong)",
                fontSize: "12px",
                textDecoration: "underline",
                cursor: "pointer",
                padding: 0,
              }}
            >
              Lost access? Use recovery code
            </button>
          </div>
        )}

        {/* Message display */}
        {message && (
          <div
            style={{
              marginTop: "20px",
              padding: "12px 16px",
              borderRadius: "var(--border-radius-md)",
              backgroundColor:
                message.type === "success"
                  ? "rgba(52, 211, 153, 0.1)"
                  : message.type === "error"
                    ? "rgba(239, 68, 68, 0.1)"
                    : "rgba(59, 130, 246, 0.1)",
              border: `1px solid ${
                message.type === "success"
                  ? "var(--color-positive)"
                  : message.type === "error"
                    ? "var(--color-negative)"
                    : "rgba(59, 130, 246, 0.3)"
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
                    : message.type === "error"
                      ? "var(--color-negative)"
                      : "var(--color-info)",
                margin: 0,
                textAlign: "center",
              }}
            >
              {message.text}
            </Text>
          </div>
        )}

        {/* Info text */}
        <div
          style={{
            marginTop: "32px",
            paddingTop: "20px",
            borderTop: "1px solid var(--color-border)",
          }}
        >
          <Text
            as="p"
            size="xs"
            style={{
              color: "var(--color-text-tertiary)",
              textAlign: "center",
              margin: 0,
              lineHeight: 1.5,
            }}
          >
            {mode === "signin"
              ? "🔐 Sign in securely with your device's biometric authentication (Face ID, Touch ID, Windows Hello) or security key."
              : mode === "signup"
                ? "🔑 Your passkey is stored securely on your device. You'll also receive recovery codes for backup access."
                : "🆘 Use one of your 8 recovery codes to regain access to your account."}
          </Text>
        </div>
      </div>
    </div>
  );
};

export default Login;
