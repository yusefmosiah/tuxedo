import React, { useState } from "react";
import { Button, Input, Text } from "@stellar/design-system";
import { useAuth } from "../contexts/AuthContext";

interface LoginProps {
  onLoginSuccess?: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);
  const [isRegistering, setIsRegistering] = useState(false);

  const {
    registerWithPasskey,
    authenticateWithPasskey,
    useRecoveryCode,
    isPasskeySupported
  } = useAuth();

  // Check passkey support on mount
  React.useEffect(() => {
    if (!isPasskeySupported) {
      setMessage({
        type: "error",
        text: "Passkeys are not supported on this device/browser. Please use a modern browser.",
      });
    }
  }, [isPasskeySupported]);

  const handleLogin = async (e?: React.FormEvent) => {
    e?.preventDefault();

    if (!isPasskeySupported) {
      setMessage({
        type: "error",
        text: "Passkeys are not supported on this device/browser.",
      });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const result = await authenticateWithPasskey(email || undefined);

      if (result.success) {
        setMessage({
          type: "success",
          text: "Successfully authenticated!",
        });
        setEmail(""); // Clear the form
        onLoginSuccess?.();
      } else {
        setMessage({
          type: "error",
          text: result.error || "Authentication failed",
        });
      }
    } catch (error) {
      setMessage({
        type: "error",
        text: error instanceof Error ? error.message : "Authentication failed",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      setMessage({ type: "error", text: "Please enter your email address" });
      return;
    }

    if (!isPasskeySupported) {
      setMessage({
        type: "error",
        text: "Passkeys are not supported on this device/browser.",
      });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const result = await registerWithPasskey(email);

      if (result.success) {
        setMessage({
          type: "success",
          text: "Registration successful! You are now logged in.",
        });
        setEmail(""); // Clear the form
        onLoginSuccess?.();
      } else {
        setMessage({
          type: "error",
          text: result.error || "Registration failed",
        });
      }
    } catch (error) {
      setMessage({
        type: "error",
        text: error instanceof Error ? error.message : "Registration failed",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecoveryCode = async (code: string) => {
    if (!code.trim()) {
      setMessage({ type: "error", text: "Please enter a recovery code" });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const result = await useRecoveryCode(code);

      if (result.success) {
        setMessage({
          type: "success",
          text: "Recovery code accepted! You are now logged in.",
        });
        onLoginSuccess?.();
      } else {
        setMessage({
          type: "error",
          text: result.error || "Invalid recovery code",
        });
      }
    } catch (error) {
      setMessage({
        type: "error",
        text: error instanceof Error ? error.message : "Recovery code validation failed",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="Login">
      <div className="Login-card">
        <div className="Login-header">
          <Text size="md" as="h2" style={{ fontWeight: 500 }}>
            {isRegistering ? "Create Account" : "Sign In"}
          </Text>
        </div>

        {message && (
          <div className={`Login-message Login-message--${message.type}`}>
            <Text size="sm" as="p">{message.text}</Text>
          </div>
        )}

        {!isRegistering ? (
          <>
            <form onSubmit={handleLogin} className="Login-form">
              <div className="Login-field">
                <Input
                  id="login-email"
                  label="Email (optional)"
                  type="email"
                  placeholder="Enter your email (optional)"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  fieldSize="md"
                />
                <Text size="sm" as="p" style={{ marginTop: '4px', color: 'var(--color-text-secondary)' }}>
                  Leave empty to use username-less authentication
                </Text>
              </div>

              <div className="Login-actions">
                <Button
                  size="md"
                  variant={isPasskeySupported ? "primary" : "secondary"}
                  isLoading={isLoading}
                  disabled={!isPasskeySupported}
                  onClick={() => handleLogin()}
                  isFullWidth
                >
                  {isLoading ? "Authenticating..." : "Sign In with Passkey"}
                </Button>
              </div>
            </form>

            <div className="Login-alternatives">
              <Button
                size="sm"
                variant="tertiary"
                onClick={() => setIsRegistering(true)}
                isFullWidth
              >
                Create New Account
              </Button>

              <Button
                size="sm"
                variant="tertiary"
                onClick={() => {
                  const code = window.prompt("Enter your recovery code:");
                  if (code) handleRecoveryCode(code);
                }}
                isFullWidth
              >
                Use Recovery Code
              </Button>
            </div>
          </>
        ) : (
          <>
            <form onSubmit={handleRegister} className="Login-form">
              <div className="Login-field">
                <Input
                  id="register-email"
                  label="Email"
                  type="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  required
                  fieldSize="md"
                />
              </div>

              <div className="Login-actions">
                <Button
                  size="md"
                  variant="primary"
                  isLoading={isLoading}
                  disabled={!isPasskeySupported || !email.trim()}
                  type="submit"
                  isFullWidth
                >
                  {isLoading ? "Creating Account..." : "Create Account with Passkey"}
                </Button>
              </div>
            </form>

            <div className="Login-alternatives">
              <Button
                size="sm"
                variant="tertiary"
                onClick={() => setIsRegistering(false)}
                isFullWidth
              >
                Back to Sign In
              </Button>
            </div>
          </>
        )}

        <div className="Login-help">
          <Text size="sm" as="p">
            Passkeys provide secure, passwordless authentication using your device's
            biometric or PIN security.
          </Text>
          <Text size="sm" as="p">
            Your recovery codes will be shown once during registration. Save them
            securely to recover your account if needed.
          </Text>
        </div>
      </div>
    </div>
  );
};