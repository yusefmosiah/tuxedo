/**
 * Passkey Authentication Service
 * Handles WebAuthn passkey operations for user authentication
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

    console.log("🔐 Starting passkey registration with API:", API_BASE_URL);
    console.log("🌐 Current origin:", window.location.origin);

    // Step 1: Start registration
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
      console.error("Network error during registration start:", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server. Please check your internet connection."}`,
      );
    }

    if (!startResponse.ok) {
      // Log detailed response info
      console.error("❌ Registration start failed:", {
        status: startResponse.status,
        statusText: startResponse.statusText,
        headers: Object.fromEntries(startResponse.headers.entries()),
      });

      let errorMessage = "Failed to start registration";
      try {
        const error = await startResponse.json();
        console.error("📄 Error response body:", error);
        errorMessage = error.error?.message || error.message || errorMessage;
      } catch (jsonError) {
        // Response is not JSON, try to get text
        try {
          const errorText = await startResponse.text();
          console.error(
            "📄 Non-JSON error response:",
            errorText.substring(0, 500),
          );
          errorMessage = `Server error (${startResponse.status}): ${startResponse.statusText || "Unknown error"}`;
        } catch (textError) {
          console.error("❌ Could not parse error response:", textError);
        }
      }
      throw new Error(errorMessage);
    }

    let challenge_id: string;
    let options: any;
    try {
      const data = await startResponse.json();
      challenge_id = data.challenge_id;
      options = data.options;
    } catch (error: any) {
      console.error("Failed to parse registration start response:", error);
      throw new Error("Invalid server response. Please try again.");
    }

    // Step 2: Create credential using WebAuthn
    // Convert challenge and user.id from base64url to ArrayBuffer
    const publicKeyOptions: PublicKeyCredentialCreationOptions = {
      ...options,
      challenge: this.base64urlToBuffer(options.challenge),
      user: {
        ...options.user,
        id: this.base64urlToBuffer(options.user.id),
      },
      excludeCredentials: options.excludeCredentials?.map((cred: any) => ({
        ...cred,
        id: this.base64urlToBuffer(cred.id),
      })),
    };

    console.log("🔑 Creating passkey with options:", {
      rp: options.rp,
      user: options.user,
      timeout: options.timeout,
      authenticatorSelection: options.authenticatorSelection,
    });

    let credential: Credential | null;
    try {
      credential = await navigator.credentials.create({
        publicKey: publicKeyOptions,
      });
    } catch (error: any) {
      // Enhanced error logging
      console.error("WebAuthn registration failed:", {
        name: error.name,
        message: error.message,
        code: error.code,
        stack: error.stack,
        fullError: error,
      });
      // Provide more specific error messages based on error type
      if (error.name === "NotAllowedError") {
        throw new Error(
          "Passkey creation was cancelled. Please try again and approve the prompt.",
        );
      } else if (error.name === "InvalidStateError") {
        throw new Error(
          "A passkey already exists for this device. Please try signing in instead.",
        );
      } else if (error.name === "NotSupportedError") {
        throw new Error(
          "Passkeys are not supported on this device or browser.",
        );
      } else if (error.name === "SecurityError") {
        throw new Error(
          "Security error: Please ensure you're accessing the site via HTTPS.",
        );
      }
      throw new Error(
        `Failed to create passkey: ${error.name || "Unknown error"} - ${error.message || "Please try again."}`,
      );
    }

    if (!credential) {
      throw new Error("Failed to create passkey");
    }

    // Step 3: Verify registration with backend
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
      console.error("Network error during registration verification:", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server. Please check your internet connection."}`,
      );
    }

    if (!verifyResponse.ok) {
      let errorMessage = "Failed to complete registration";
      try {
        const error = await verifyResponse.json();
        errorMessage = error.error?.message || error.message || errorMessage;
      } catch (jsonError) {
        // Response is not JSON, try to get text
        try {
          const errorText = await verifyResponse.text();
          console.error(
            "Non-JSON error response:",
            errorText.substring(0, 200),
          );
          errorMessage = `Server error (${verifyResponse.status}): ${verifyResponse.statusText || "Unknown error"}`;
        } catch (textError) {
          console.error("Could not parse error response:", textError);
        }
      }
      throw new Error(errorMessage);
    }

    let result: RegistrationResult;
    try {
      result = await verifyResponse.json();
    } catch (error: any) {
      console.error(
        "Failed to parse registration verification response:",
        error,
      );
      throw new Error("Invalid server response. Please try again.");
    }

    // Store session token
    localStorage.setItem("session_token", result.session_token);
    localStorage.setItem("user_data", JSON.stringify(result.user));

    return result;
  }

  /**
   * Authenticate with a passkey
   */
  async authenticate(email?: string): Promise<AuthResult> {
    if (!this.isSupported()) {
      throw new Error("Passkeys are not supported in this browser");
    }

    if (!email) {
      throw new Error("Email is required for authentication");
    }

    console.log("🔐 Starting passkey authentication with API:", API_BASE_URL);
    console.log("🌐 Current origin:", window.location.origin);

    // Step 1: Start authentication
    let startResponse: Response;
    try {
      startResponse = await fetch(`${API_BASE_URL}/auth/passkey/login/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
    } catch (error: any) {
      console.error("Network error during authentication start:", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server. Please check your internet connection."}`,
      );
    }

    if (!startResponse.ok) {
      let errorMessage = "Failed to start login";
      try {
        const error = await startResponse.json();
        errorMessage = error.error?.message || error.message || errorMessage;
      } catch (jsonError) {
        // Response is not JSON, try to get text
        try {
          const errorText = await startResponse.text();
          console.error(
            "Non-JSON error response:",
            errorText.substring(0, 200),
          );
          errorMessage = `Server error (${startResponse.status}): ${startResponse.statusText || "Unknown error"}`;
        } catch (textError) {
          console.error("Could not parse error response:", textError);
        }
      }
      throw new Error(errorMessage);
    }

    let challenge_id: string;
    let options: any;
    try {
      const data = await startResponse.json();
      challenge_id = data.challenge_id;
      options = data.options;
    } catch (error: any) {
      console.error("Failed to parse authentication start response:", error);
      throw new Error("Invalid server response. Please try again.");
    }

    // Step 2: Get credential using WebAuthn
    const publicKeyOptions: PublicKeyCredentialRequestOptions = {
      ...options,
      challenge: this.base64urlToBuffer(options.challenge),
      allowCredentials: options.allowCredentials?.map((cred: any) => ({
        ...cred,
        id: this.base64urlToBuffer(cred.id),
      })),
    };

    let credential: Credential | null;
    try {
      credential = await navigator.credentials.get({
        publicKey: publicKeyOptions,
      });
    } catch (error: any) {
      console.error("WebAuthn authentication failed:", error);
      // Provide more specific error messages based on error type
      if (error.name === "NotAllowedError") {
        throw new Error(
          "Authentication was cancelled. Please try again and approve the prompt.",
        );
      } else if (error.name === "NotSupportedError") {
        throw new Error(
          "Passkeys are not supported on this device or browser.",
        );
      } else if (error.name === "SecurityError") {
        throw new Error(
          "Security error: Please ensure you're accessing the site via HTTPS.",
        );
      }
      throw new Error(
        `Failed to authenticate: ${error.message || "Please try again."}`,
      );
    }

    if (!credential) {
      throw new Error("Failed to get passkey");
    }

    // Step 3: Verify authentication with backend
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
      console.error("Network error during authentication verification:", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server. Please check your internet connection."}`,
      );
    }

    if (!verifyResponse.ok) {
      let errorMessage = "Failed to verify authentication";
      try {
        const error = await verifyResponse.json();
        errorMessage = error.error?.message || error.message || errorMessage;
      } catch (jsonError) {
        // Response is not JSON, try to get text
        try {
          const errorText = await verifyResponse.text();
          console.error(
            "Non-JSON error response:",
            errorText.substring(0, 200),
          );
          errorMessage = `Server error (${verifyResponse.status}): ${verifyResponse.statusText || "Unknown error"}`;
        } catch (textError) {
          console.error("Could not parse error response:", textError);
        }
      }
      throw new Error(errorMessage);
    }

    let result: AuthResult;
    try {
      result = await verifyResponse.json();
    } catch (error: any) {
      console.error(
        "Failed to parse authentication verification response:",
        error,
      );
      throw new Error("Invalid server response. Please try again.");
    }

    // Store session token
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

    // Store session token
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
        // Update stored user data
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
   * Add a new passkey to the account
   */
  async addPasskey(
    _token: string,
    _friendlyName?: string,
  ): Promise<PasskeyCredential> {
    if (!this.isSupported()) {
      throw new Error("Passkeys are not supported in this browser");
    }

    // For now, this is simplified - in production you'd generate a challenge first
    throw new Error("Add passkey not yet fully implemented");
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
      // Call logout endpoint (fire and forget)
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

    // Clear local storage
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

    // Check if this is a registration or authentication response
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
