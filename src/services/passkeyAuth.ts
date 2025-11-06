/**
 * Passkey Authentication Service
 * Simplified WebAuthn implementation with comprehensive error handling
 */

import { API_BASE_URL } from "../lib/api";

export interface User {
  id: string;
  email: string;
}

export interface PasskeyCredential {
  id: string;
  friendly_name: string;
  created_at: string;
  last_used_at: string | null;
  backup_eligible: boolean;
}

export interface RegistrationResult {
  user: User;
  session_token: string;
  recovery_codes: string[];
  recovery_codes_message: string;
  must_acknowledge: boolean;
}

export interface AuthResult {
  user: User;
  session_token: string;
  remaining_codes?: number;
}

/**
 * Enhanced error logging that preserves all error details
 */
function logWebAuthnError(context: string, error: any): void {
  console.error(`❌ ${context}:`, {
    name: error?.name,
    message: error?.message,
    code: error?.code,
    stack: error?.stack,
    // Log ALL properties of the error object
    ...Object.getOwnPropertyNames(error || {}).reduce((acc, key) => {
      acc[key] = error[key];
      return acc;
    }, {} as Record<string, any>),
  });

  // Also log the raw error object for inspection
  console.error("Full error object:", error);
}

/**
 * Creates a user-friendly error message based on WebAuthn error type
 */
function getWebAuthnErrorMessage(error: any, operation: "registration" | "login"): string {
  const errorName = error?.name || "";

  switch (errorName) {
    case "NotAllowedError":
      return `${operation === "registration" ? "Passkey creation" : "Authentication"} was cancelled or timed out. Please try again.`;

    case "InvalidStateError":
      return operation === "registration"
        ? "A passkey already exists for this device. Please try signing in instead."
        : "Invalid authentication state. Please refresh and try again.";

    case "NotSupportedError":
      return "Passkeys are not supported on this device or browser. Please use a modern browser like Chrome, Safari, or Edge.";

    case "SecurityError":
      return "Security error: Please ensure you're accessing the site via HTTPS.";

    case "AbortError":
      return "Operation was aborted. Please try again.";

    case "ConstraintError":
      return "The authenticator doesn't meet the required constraints. Please try a different device or browser.";

    case "NetworkError":
      return "Network error occurred. Please check your connection and try again.";

    default:
      // Return the original error message if it's informative, otherwise provide a generic one
      const originalMessage = error?.message || "";
      return originalMessage.length > 0 && originalMessage.length < 200
        ? originalMessage
        : `${operation === "registration" ? "Registration" : "Login"} failed. Please try again.`;
  }
}

class PasskeyAuthService {
  /**
   * Check if WebAuthn is supported in the current browser
   */
  isSupported(): boolean {
    return (
      window.PublicKeyCredential !== undefined &&
      typeof window.PublicKeyCredential === "function"
    );
  }

  /**
   * Register a new user with a passkey
   */
  async register(email: string): Promise<RegistrationResult> {
    if (!this.isSupported()) {
      throw new Error("Passkeys are not supported in this browser");
    }

    console.log("🔐 Starting passkey registration");
    console.log("📧 Email:", email);
    console.log("🌐 Origin:", window.location.origin);
    console.log("🔒 Protocol:", window.location.protocol);

    // Step 1: Get challenge from backend
    let startResponse: Response;
    try {
      startResponse = await fetch(
        `${API_BASE_URL}/auth/passkey/register/start`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        },
      );
    } catch (error: any) {
      logWebAuthnError("Network error during registration start", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server"}`,
      );
    }

    if (!startResponse.ok) {
      console.error("❌ Registration start failed:", {
        status: startResponse.status,
        statusText: startResponse.statusText,
      });

      let errorMessage = "Failed to start registration";
      try {
        const error = await startResponse.json();
        console.error("📄 Error response:", error);
        errorMessage =
          error.detail?.message || error.error?.message || error.message;

        if (startResponse.status === 409) {
          errorMessage =
            error.detail?.message ||
            "An account with this email already exists. Please sign in instead.";
        }
      } catch {
        errorMessage = `Server error (${startResponse.status}): ${startResponse.statusText}`;
      }
      throw new Error(errorMessage);
    }

    const { challenge_id, options } = await startResponse.json();
    console.log("✅ Challenge received:", challenge_id);

    // Step 2: Create credential using WebAuthn
    const publicKeyOptions: PublicKeyCredentialCreationOptions = {
      challenge: this.base64urlToBuffer(options.challenge),
      rp: {
        name: options.rp.name,
        id: options.rp.id,
      },
      user: {
        id: this.base64urlToBuffer(options.user.id),
        name: options.user.name,
        displayName: options.user.displayName,
      },
      pubKeyCredParams: options.pubKeyCredParams,
      timeout: options.timeout,
      attestation: options.attestation,
      authenticatorSelection: options.authenticatorSelection,
      excludeCredentials: options.excludeCredentials?.map((cred: any) => ({
        type: cred.type,
        id: this.base64urlToBuffer(cred.id),
        transports: cred.transports,
      })),
    };

    console.log("🔑 Calling navigator.credentials.create() with options:", {
      rp: options.rp,
      user: { name: options.user.name, displayName: options.user.displayName },
      timeout: options.timeout,
      authenticatorSelection: options.authenticatorSelection,
    });

    let credential: Credential | null;
    try {
      credential = await navigator.credentials.create({
        publicKey: publicKeyOptions,
      });
      console.log("✅ Credential created successfully");
    } catch (error: any) {
      logWebAuthnError("WebAuthn registration failed", error);
      throw new Error(getWebAuthnErrorMessage(error, "registration"));
    }

    if (!credential) {
      throw new Error("Failed to create passkey - no credential returned");
    }

    // Step 3: Verify with backend
    const credentialData = this.credentialToJSON(
      credential as PublicKeyCredential,
    );

    let verifyResponse: Response;
    try {
      verifyResponse = await fetch(
        `${API_BASE_URL}/auth/passkey/register/verify`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            challenge_id,
            credential: credentialData,
          }),
        },
      );
    } catch (error: any) {
      logWebAuthnError("Network error during registration verification", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server"}`,
      );
    }

    if (!verifyResponse.ok) {
      console.error("❌ Registration verification failed:", {
        status: verifyResponse.status,
        statusText: verifyResponse.statusText,
      });

      let errorMessage = "Failed to complete registration";
      try {
        const error = await verifyResponse.json();
        console.error("📄 Verification error:", error);
        errorMessage = error.error?.message || error.message || errorMessage;
      } catch {
        errorMessage = `Server error (${verifyResponse.status}): ${verifyResponse.statusText}`;
      }
      throw new Error(errorMessage);
    }

    const result: RegistrationResult = await verifyResponse.json();
    console.log("✅ Registration completed successfully");

    // Store session
    localStorage.setItem("session_token", result.session_token);
    localStorage.setItem("user_data", JSON.stringify(result.user));

    return result;
  }

  /**
   * Authenticate with a passkey
   */
  async login(email?: string): Promise<AuthResult> {
    if (!this.isSupported()) {
      throw new Error("Passkeys are not supported in this browser");
    }

    console.log("🔐 Starting passkey login");
    console.log("📧 Email:", email || "none (discoverable)");
    console.log("🌐 Origin:", window.location.origin);
    console.log("🔒 Protocol:", window.location.protocol);

    // Step 1: Get challenge from backend
    let startResponse: Response;
    try {
      startResponse = await fetch(`${API_BASE_URL}/auth/passkey/login/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
    } catch (error: any) {
      logWebAuthnError("Network error during login start", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server"}`,
      );
    }

    if (!startResponse.ok) {
      console.error("❌ Login start failed:", {
        status: startResponse.status,
        statusText: startResponse.statusText,
      });

      let errorMessage = "Failed to start login";
      try {
        const error = await startResponse.json();
        console.error("📄 Error response:", error);
        errorMessage = error.error?.message || error.message || errorMessage;
      } catch {
        errorMessage = `Server error (${startResponse.status}): ${startResponse.statusText}`;
      }
      throw new Error(errorMessage);
    }

    const { challenge_id, options } = await startResponse.json();
    console.log("✅ Challenge received:", challenge_id);

    // Step 2: Get credential using WebAuthn
    const publicKeyOptions: PublicKeyCredentialRequestOptions = {
      challenge: this.base64urlToBuffer(options.challenge),
      rpId: options.rpId,
      allowCredentials: options.allowCredentials?.map((cred: any) => ({
        type: cred.type,
        id: this.base64urlToBuffer(cred.id),
        transports: cred.transports,
      })),
      userVerification: options.userVerification,
      timeout: options.timeout,
    };

    console.log("🔑 Calling navigator.credentials.get() with options:", {
      rpId: options.rpId,
      timeout: options.timeout,
      allowCredentials: options.allowCredentials?.length || 0,
      userVerification: options.userVerification,
    });

    let credential: Credential | null;
    try {
      credential = await navigator.credentials.get({
        publicKey: publicKeyOptions,
      });
      console.log("✅ Credential retrieved successfully");
    } catch (error: any) {
      logWebAuthnError("WebAuthn login failed", error);
      throw new Error(getWebAuthnErrorMessage(error, "login"));
    }

    if (!credential) {
      throw new Error("Failed to authenticate - no credential returned");
    }

    // Step 3: Verify with backend
    const credentialData = this.credentialToJSON(
      credential as PublicKeyCredential,
    );

    let verifyResponse: Response;
    try {
      verifyResponse = await fetch(
        `${API_BASE_URL}/auth/passkey/login/verify`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            challenge_id,
            credential: credentialData,
          }),
        },
      );
    } catch (error: any) {
      logWebAuthnError("Network error during login verification", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server"}`,
      );
    }

    if (!verifyResponse.ok) {
      console.error("❌ Login verification failed:", {
        status: verifyResponse.status,
        statusText: verifyResponse.statusText,
      });

      let errorMessage = "Failed to verify authentication";
      try {
        const error = await verifyResponse.json();
        console.error("📄 Verification error:", error);
        errorMessage = error.error?.message || error.message || errorMessage;
      } catch {
        errorMessage = `Server error (${verifyResponse.status}): ${verifyResponse.statusText}`;
      }
      throw new Error(errorMessage);
    }

    const result: AuthResult = await verifyResponse.json();
    console.log("✅ Login completed successfully");

    // Store session
    localStorage.setItem("session_token", result.session_token);
    localStorage.setItem("user_data", JSON.stringify(result.user));

    return result;
  }

  /**
   * Authenticate using a recovery code
   */
  async useRecoveryCode(email: string, code: string): Promise<AuthResult> {
    const response = await fetch(
      `${API_BASE_URL}/auth/passkey/recovery/verify`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code }),
      },
    );

    if (!response.ok) {
      const error = await response.json();
      if (response.status === 429) {
        throw new Error(
          error.error?.message ||
            "Too many failed attempts. Please try again later.",
        );
      }
      throw new Error(error.error?.message || "Invalid recovery code");
    }

    const result: AuthResult = await response.json();

    // Store session
    localStorage.setItem("session_token", result.session_token);
    localStorage.setItem("user_data", JSON.stringify(result.user));

    return result;
  }

  /**
   * Acknowledge saving recovery codes
   */
  async acknowledgeRecoveryCodes(token: string): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/auth/passkey/recovery-codes/acknowledge`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || "Failed to acknowledge");
    }
  }

  /**
   * Validate session token
   */
  async validateSession(token: string): Promise<User | null> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/auth/validate-passkey-session`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        },
      );

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      if (data.valid) {
        localStorage.setItem("user_data", JSON.stringify(data.user));
        return data.user;
      }

      return null;
    } catch (error) {
      console.error("Session validation failed:", error);
      return null;
    }
  }

  /**
   * List user's passkeys
   */
  async listPasskeys(token: string): Promise<PasskeyCredential[]> {
    const response = await fetch(`${API_BASE_URL}/auth/passkey/credentials`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || "Failed to list passkeys");
    }

    const data = await response.json();
    return data.credentials;
  }

  /**
   * Remove a passkey from the account
   */
  async removePasskey(token: string, passkeyId: string): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/auth/passkey/credentials/${passkeyId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || "Failed to remove passkey");
    }
  }

  /**
   * Request email recovery link
   */
  async requestEmailRecovery(email: string): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/auth/passkey/email-recovery/request`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || "Failed to send recovery link");
    }
  }

  /**
   * Logout user
   */
  logout(): void {
    const token = localStorage.getItem("session_token");

    if (token) {
      fetch(`${API_BASE_URL}/auth/logout`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }).catch((error) => {
        console.error("Logout API call failed:", error);
      });
    }

    localStorage.removeItem("session_token");
    localStorage.removeItem("user_data");
  }

  // Helper methods for WebAuthn data conversion

  /**
   * Convert base64url string to ArrayBuffer
   */
  private base64urlToBuffer(base64url: string): ArrayBuffer {
    const padding = "=".repeat((4 - (base64url.length % 4)) % 4);
    const base64 = base64url.replace(/-/g, "+").replace(/_/g, "/") + padding;
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }

  /**
   * Convert ArrayBuffer to base64url string
   */
  private bufferToBase64url(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = "";
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary)
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=/g, "");
  }

  /**
   * Convert WebAuthn credential to JSON-serializable format
   */
  private credentialToJSON(credential: PublicKeyCredential): any {
    const response = credential.response;
    const isRegistration = "attestationObject" in response;

    if (isRegistration) {
      const attestationResponse = response as AuthenticatorAttestationResponse;
      return {
        id: credential.id,
        rawId: this.bufferToBase64url(credential.rawId),
        type: credential.type,
        response: {
          clientDataJSON: this.bufferToBase64url(
            attestationResponse.clientDataJSON,
          ),
          attestationObject: this.bufferToBase64url(
            attestationResponse.attestationObject,
          ),
          transports: (credential as any).response?.getTransports
            ? (credential as any).response.getTransports()
            : [],
        },
      };
    } else {
      const assertionResponse = response as AuthenticatorAssertionResponse;
      return {
        id: credential.id,
        rawId: this.bufferToBase64url(credential.rawId),
        type: credential.type,
        response: {
          clientDataJSON: this.bufferToBase64url(
            assertionResponse.clientDataJSON,
          ),
          authenticatorData: this.bufferToBase64url(
            assertionResponse.authenticatorData,
          ),
          signature: this.bufferToBase64url(assertionResponse.signature),
          userHandle: assertionResponse.userHandle
            ? this.bufferToBase64url(assertionResponse.userHandle)
            : undefined,
        },
      };
    }
  }
}

// Export singleton instance
export const passkeyAuthService = new PasskeyAuthService();
