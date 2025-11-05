import {
  startRegistration,
  startAuthentication,
} from "@simplewebauthn/browser";

const API_URL = "http://localhost:8000";

export interface PasskeyRegistrationResult {
  success: boolean;
  user?: {
    id: string;
    email: string;
    stellar_public_key?: string;
  };
  recovery_codes?: string[];
  has_prf?: boolean;
  recovery_codes_message?: string;
  session_token?: string;
  error?: string;
}

export interface PasskeyAuthenticationResult {
  success: boolean;
  user?: {
    id: string;
    email: string;
    stellar_public_key?: string;
  };
  session_token?: string;
  error?: string;
}

export class PasskeyAuthService {
  async register(email: string): Promise<PasskeyRegistrationResult> {
    try {
      // 1. Start registration
      const optionsRes = await fetch(`${API_URL}/auth/passkey/register/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!optionsRes.ok) {
        const error = await optionsRes.json();
        throw new Error(error.detail || "Registration failed");
      }

      const { challenge_id, options } = await optionsRes.json();

      // 2. Create passkey
      const credential = await startRegistration(options);

      // 3. Verify registration
      const verifyRes = await fetch(`${API_URL}/auth/passkey/register/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, challenge_id, credential }),
      });

      if (!verifyRes.ok) {
        const error = await verifyRes.json();
        throw new Error(error.detail || "Verification failed");
      }

      const result = await verifyRes.json();

      // Store session
      localStorage.setItem("session_token", result.session_token);
      localStorage.setItem("user", JSON.stringify(result.user));

      // Show recovery codes (only shown once)
      if (result.recovery_codes) {
        console.log("RECOVERY CODES - SAVE THESE SECURELY:");
        console.log(result.recovery_codes_message);
        alert(
          "Save your recovery codes! They have been printed to the console.",
        );
      }

      return {
        success: true,
        user: result.user,
        recovery_codes: result.recovery_codes,
        has_prf: result.has_prf,
        recovery_codes_message: result.recovery_codes_message,
        session_token: result.session_token,
      };
    } catch (error) {
      console.error("Passkey registration failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Registration failed",
      };
    }
  }

  async authenticate(email?: string): Promise<PasskeyAuthenticationResult> {
    try {
      // 1. Start authentication
      const optionsRes = await fetch(`${API_URL}/auth/passkey/login/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!optionsRes.ok) {
        throw new Error("Failed to get authentication options");
      }

      const { challenge_id, options } = await optionsRes.json();

      // 2. Authenticate with passkey
      const credential = await startAuthentication(options);

      // 3. Verify authentication
      const verifyRes = await fetch(`${API_URL}/auth/passkey/login/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ challenge_id, credential }),
      });

      if (!verifyRes.ok) {
        throw new Error("Authentication failed");
      }

      const result = await verifyRes.json();

      // Store session
      localStorage.setItem("session_token", result.session_token);
      localStorage.setItem("user", JSON.stringify(result.user));

      return {
        success: true,
        user: result.user,
        session_token: result.session_token,
      };
    } catch (error) {
      console.error("Passkey authentication failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Authentication failed",
      };
    }
  }

  async validateSession(token: string): Promise<any> {
    try {
      const res = await fetch(`${API_URL}/auth/validate-passkey-session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) return null;

      const result = await res.json();
      return result.user;
    } catch {
      return null;
    }
  }

  async useRecoveryCode(code: string): Promise<PasskeyAuthenticationResult> {
    try {
      const res = await fetch(`${API_URL}/auth/passkey/recovery/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Invalid recovery code");
      }

      const result = await res.json();

      // Store session
      localStorage.setItem("session_token", result.session_token);
      localStorage.setItem("user", JSON.stringify(result.user));

      return {
        success: true,
        user: result.user,
        session_token: result.session_token,
      };
    } catch (error) {
      console.error("Recovery code authentication failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Recovery code invalid",
      };
    }
  }

  logout() {
    localStorage.removeItem("session_token");
    localStorage.removeItem("user");
  }

  isSupported(): boolean {
    // Check if WebAuthn is supported
    return !!(
      window.PublicKeyCredential &&
      navigator.credentials &&
      "create" in navigator.credentials &&
      "get" in navigator.credentials
    );
  }
}

export const passkeyService = new PasskeyAuthService();
