import React, { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext_passkey";
import { passkeyAuthService, PasskeyCredential } from "../services/passkeyAuth";
import { Button, Text } from "@stellar/design-system";
import { useNavigate } from "react-router-dom";

export const AccountSecurity: React.FC = () => {
  const { user, sessionToken, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [passkeys, setPasskeys] = useState<PasskeyCredential[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/dashboard");
      return;
    }

    loadPasskeys();
  }, [isAuthenticated, navigate]);

  const loadPasskeys = async () => {
    if (!sessionToken) return;

    try {
      setIsLoading(true);
      setError(null);
      const credentials = await passkeyAuthService.listPasskeys(sessionToken);
      setPasskeys(credentials);
    } catch (err: any) {
      console.error("Failed to load passkeys:", err);
      setError(err.message || "Failed to load passkeys");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemovePasskey = async (passkeyId: string) => {
    if (!sessionToken) return;

    if (passkeys.length === 1) {
      alert(
        "Cannot remove your only passkey. Add another passkey before removing this one.",
      );
      return;
    }

    if (!confirm("Are you sure you want to remove this passkey?")) {
      return;
    }

    try {
      await passkeyAuthService.removePasskey(sessionToken, passkeyId);
      await loadPasskeys(); // Reload the list
    } catch (err: any) {
      console.error("Failed to remove passkey:", err);
      alert(err.message || "Failed to remove passkey");
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    return new Date(dateString).toLocaleString();
  };

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "0 auto",
        padding: "40px 24px",
        color: "var(--color-text-primary)",
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: "32px" }}>
        <Text
          as="h1"
          size="lg"
          style={{
            fontSize: "28px",
            fontWeight: "bold",
            marginBottom: "8px",
          }}
        >
          Security Settings
        </Text>
        <Text as="p" size="md" style={{ color: "var(--color-text-secondary)" }}>
          Manage your account security and authentication methods
        </Text>
      </div>

      {/* Account Info */}
      <section
        style={{
          backgroundColor: "var(--color-bg-surface)",
          borderRadius: "var(--border-radius-md)",
          padding: "24px",
          marginBottom: "24px",
          border: "1px solid var(--color-border)",
        }}
      >
        <Text
          as="h2"
          size="md"
          style={{
            fontSize: "18px",
            fontWeight: "600",
            marginBottom: "16px",
          }}
        >
          Account Information
        </Text>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Text
              as="span"
              size="sm"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Email
            </Text>
            <Text as="span" size="sm" style={{ fontWeight: "500" }}>
              {user.email}
            </Text>
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Text
              as="span"
              size="sm"
              style={{ color: "var(--color-text-secondary)" }}
            >
              User ID
            </Text>
            <Text
              as="span"
              size="xs"
              style={{
                fontFamily: "var(--font-tertiary-mono)",
                fontSize: "12px",
                color: "var(--color-text-secondary)",
              }}
            >
              {user.id}
            </Text>
          </div>
        </div>
      </section>

      {/* Passkeys Section */}
      <section
        style={{
          backgroundColor: "var(--color-bg-surface)",
          borderRadius: "var(--border-radius-md)",
          padding: "24px",
          marginBottom: "24px",
          border: "1px solid var(--color-border)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "16px",
          }}
        >
          <div>
            <Text
              as="h2"
              size="md"
              style={{
                fontSize: "18px",
                fontWeight: "600",
                marginBottom: "4px",
              }}
            >
              Passkeys
            </Text>
            <Text
              as="p"
              size="sm"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Manage your passkeys for secure authentication
            </Text>
          </div>
        </div>

        {isLoading ? (
          <div style={{ textAlign: "center", padding: "32px" }}>
            <Text
              as="p"
              size="sm"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Loading passkeys...
            </Text>
          </div>
        ) : error ? (
          <div
            style={{
              padding: "16px",
              backgroundColor: "var(--color-bg-primary)",
              borderRadius: "var(--border-radius-sm)",
              border: "1px solid var(--color-border)",
            }}
          >
            <Text
              as="p"
              size="sm"
              style={{ color: "var(--color-stellar-error)" }}
            >
              {error}
            </Text>
            <Button
              variant="tertiary"
              size="sm"
              onClick={loadPasskeys}
              style={{ marginTop: "12px" }}
            >
              Retry
            </Button>
          </div>
        ) : passkeys.length === 0 ? (
          <div
            style={{
              padding: "16px",
              backgroundColor: "var(--color-bg-primary)",
              borderRadius: "var(--border-radius-sm)",
              border: "1px solid var(--color-border)",
            }}
          >
            <Text
              as="p"
              size="sm"
              style={{ color: "var(--color-text-secondary)" }}
            >
              No passkeys found
            </Text>
          </div>
        ) : (
          <div
            style={{ display: "flex", flexDirection: "column", gap: "12px" }}
          >
            {passkeys.map((passkey) => (
              <div
                key={passkey.id}
                style={{
                  padding: "16px",
                  backgroundColor: "var(--color-bg-primary)",
                  borderRadius: "var(--border-radius-sm)",
                  border: "1px solid var(--color-border)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                }}
              >
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      marginBottom: "8px",
                    }}
                  >
                    <span style={{ fontSize: "20px" }}>🔑</span>
                    <Text
                      as="h3"
                      size="sm"
                      style={{
                        fontSize: "14px",
                        fontWeight: "600",
                      }}
                    >
                      {passkey.friendly_name}
                    </Text>
                  </div>
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "auto 1fr",
                      gap: "4px 12px",
                      fontSize: "12px",
                    }}
                  >
                    <Text
                      as="span"
                      size="xs"
                      style={{ color: "var(--color-text-secondary)" }}
                    >
                      Created:
                    </Text>
                    <Text as="span" size="xs">
                      {formatDate(passkey.created_at)}
                    </Text>
                    <Text
                      as="span"
                      size="xs"
                      style={{ color: "var(--color-text-secondary)" }}
                    >
                      Last used:
                    </Text>
                    <Text as="span" size="xs">
                      {formatDate(passkey.last_used_at)}
                    </Text>
                    <Text
                      as="span"
                      size="xs"
                      style={{ color: "var(--color-text-secondary)" }}
                    >
                      Backup:
                    </Text>
                    <Text as="span" size="xs">
                      {passkey.backup_eligible ? "Eligible" : "Not eligible"}
                    </Text>
                  </div>
                </div>
                <Button
                  variant="tertiary"
                  size="sm"
                  onClick={() => handleRemovePasskey(passkey.id)}
                  style={{
                    color: "var(--color-stellar-error)",
                    marginLeft: "16px",
                  }}
                >
                  Remove
                </Button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Recovery Information */}
      <section
        style={{
          backgroundColor: "var(--color-bg-surface)",
          borderRadius: "var(--border-radius-md)",
          padding: "24px",
          marginBottom: "24px",
          border: "1px solid var(--color-border)",
        }}
      >
        <Text
          as="h2"
          size="md"
          style={{
            fontSize: "18px",
            fontWeight: "600",
            marginBottom: "8px",
          }}
        >
          Account Recovery
        </Text>
        <Text
          as="p"
          size="sm"
          style={{
            color: "var(--color-text-secondary)",
            marginBottom: "16px",
          }}
        >
          Recovery codes allow you to access your account if you lose access to
          your passkeys. You received 8 recovery codes when you created your
          account.
        </Text>
        <div
          style={{
            padding: "12px",
            backgroundColor: "var(--color-bg-primary)",
            borderRadius: "var(--border-radius-sm)",
            border: "1px solid var(--color-border)",
          }}
        >
          <Text
            as="p"
            size="sm"
            style={{ color: "var(--color-text-secondary)" }}
          >
            ⚠️ Make sure to keep your recovery codes in a safe place. Each code
            can only be used once.
          </Text>
        </div>
      </section>

      {/* Danger Zone */}
      <section
        style={{
          backgroundColor: "var(--color-bg-surface)",
          borderRadius: "var(--border-radius-md)",
          padding: "24px",
          border: "1px solid var(--color-stellar-error)",
        }}
      >
        <Text
          as="h2"
          size="md"
          style={{
            fontSize: "18px",
            fontWeight: "600",
            marginBottom: "8px",
            color: "var(--color-stellar-error)",
          }}
        >
          Danger Zone
        </Text>
        <Text
          as="p"
          size="sm"
          style={{
            color: "var(--color-text-secondary)",
            marginBottom: "16px",
          }}
        >
          These actions are permanent and cannot be undone.
        </Text>
        <Button
          variant="tertiary"
          size="sm"
          onClick={() => {
            if (
              confirm(
                "Are you sure you want to logout? You will need your passkey to sign in again.",
              )
            ) {
              logout();
              navigate("/dashboard");
            }
          }}
          style={{
            color: "var(--color-stellar-error)",
            borderColor: "var(--color-stellar-error)",
          }}
        >
          Logout
        </Button>
      </section>
    </div>
  );
};

export default AccountSecurity;
