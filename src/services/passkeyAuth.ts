/**
 * Passkey Authentication Service
 * Handles WebAuthn-based passkey authentication with recovery codes
 */

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Types
export interface User {
  id: string;
  email: string;
  created_at?: string;
  last_login?: string;
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
}

export interface RecoveryCodeAuthResult extends AuthResult {
  remaining_codes: number;
}

export interface Passkey {
  id: string;
  friendly_name: string | null;
  created_at: string;
  last_used_at: string | null;
  backup_eligible: boolean;
}

export interface ApiError {
  code: string;
  message: string;
  details?: any;
}

// Helper functions
function base64UrlToUint8Array(base64url: string): Uint8Array {
  // Add padding if needed
  const base64 = base64url.replace(/-/g, "+").replace(/_/g, "/");
  const padLen = (4 - (base64.length % 4)) % 4;
  const padded = base64 + "=".repeat(padLen);

  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

function uint8ArrayToBase64Url(array: Uint8Array): string {
  const binary = String.fromCharCode(...Array.from(array));
  const base64 = btoa(binary);
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

// Convert PublicKeyCredentialCreationOptions from server to client format
function convertRegistrationOptions(options: any): PublicKeyCredentialCreationOptions {
  return {
    ...options,
    challenge: base64UrlToUint8Array(options.challenge),
    user: {
      ...options.user,
      id: base64UrlToUint8Array(options.user.id),
    },
    excludeCredentials: options.excludeCredentials?.map((cred: any) => ({
      ...cred,
      id: base64UrlToUint8Array(cred.id),
    })) || [],
  };
}

// Convert PublicKeyCredentialRequestOptions from server to client format
function convertAuthenticationOptions(options: any): PublicKeyCredentialRequestOptions {
  return {
    ...options,
    challenge: base64UrlToUint8Array(options.challenge),
    allowCredentials: options.allowCredentials?.map((cred: any) => ({
      ...cred,
      id: base64UrlToUint8Array(cred.id),
    })) || [],
  };
}

// Convert credential from client to server format
function credentialToJSON(credential: PublicKeyCredential): any {
  const response = credential.response as AuthenticatorAttestationResponse | AuthenticatorAssertionResponse;

  const result: any = {
    id: credential.id,
    rawId: uint8ArrayToBase64Url(new Uint8Array(credential.rawId)),
    type: credential.type,
    response: {},
  };

  if ("attestationObject" in response) {
    // Registration response
    result.response = {
      clientDataJSON: uint8ArrayToBase64Url(new Uint8Array(response.clientDataJSON)),
      attestationObject: uint8ArrayToBase64Url(new Uint8Array(response.attestationObject)),
    };
    if ((response as any).transports) {
      result.response.transports = (response as any).transports;
    }
  } else {
    // Authentication response
    result.response = {
      clientDataJSON: uint8ArrayToBase64Url(new Uint8Array(response.clientDataJSON)),
      authenticatorData: uint8ArrayToBase64Url(new Uint8Array((response as AuthenticatorAssertionResponse).authenticatorData)),
      signature: uint8ArrayToBase64Url(new Uint8Array((response as AuthenticatorAssertionResponse).signature)),
      userHandle: (response as AuthenticatorAssertionResponse).userHandle
        ? uint8ArrayToBase64Url(new Uint8Array((response as AuthenticatorAssertionResponse).userHandle!))
        : null,
    };
  }

  return result;
}

export class PasskeyAuthService {
  /**
   * Check if WebAuthn is supported by the browser
   */
  isSupported(): boolean {
    return (
      window.PublicKeyCredential !== undefined &&
      typeof window.PublicKeyCredential === "function"
    );
  }

  /**
   * Register a new user with passkey
   */
  async register(email: string, friendlyName?: string): Promise<RegistrationResult> {
    if (!this.isSupported()) {
      throw new Error("Passkeys are not supported in this browser");
    }

    try {
      // Step 1: Start registration
      const startResponse = await fetch(`${API_URL}/auth/passkey/register/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!startResponse.ok) {
        const error = await startResponse.json();
        throw new Error(error.detail?.message || error.detail || "Registration failed");
      }

      const { challenge_id, options } = await startResponse.json();

      // Step 2: Create credential
      const credentialOptions = convertRegistrationOptions(options);
      const credential = await navigator.credentials.create({
        publicKey: credentialOptions,
      }) as PublicKeyCredential;

      if (!credential) {
        throw new Error("Failed to create passkey");
      }

      // Step 3: Verify registration
      const verifyResponse = await fetch(`${API_URL}/auth/passkey/register/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          challenge_id,
          credential: credentialToJSON(credential),
          friendly_name: friendlyName,
        }),
      });

      if (!verifyResponse.ok) {
        const error = await verifyResponse.json();
        throw new Error(error.detail?.message || error.detail || "Registration verification failed");
      }

      const result: RegistrationResult = await verifyResponse.json();

      // Store session token
      localStorage.setItem("session_token", result.session_token);
      localStorage.setItem("user_data", JSON.stringify(result.user));

      return result;
    } catch (error: any) {
      console.error("Passkey registration error:", error);
      throw error;
    }
  }

  /**
   * Authenticate with passkey
   */
  async authenticate(email: string): Promise<AuthResult> {
    if (!this.isSupported()) {
      throw new Error("Passkeys are not supported in this browser");
    }

    try {
      // Step 1: Start authentication
      const startResponse = await fetch(`${API_URL}/auth/passkey/login/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!startResponse.ok) {
        const error = await startResponse.json();
        throw new Error(error.detail?.message || error.detail || "Login failed");
      }

      const { challenge_id, options } = await startResponse.json();

      // Step 2: Get credential
      const credentialOptions = convertAuthenticationOptions(options);
      const credential = await navigator.credentials.get({
        publicKey: credentialOptions,
      }) as PublicKeyCredential;

      if (!credential) {
        throw new Error("Failed to get passkey");
      }

      // Step 3: Verify authentication
      const verifyResponse = await fetch(`${API_URL}/auth/passkey/login/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          challenge_id,
          credential: credentialToJSON(credential),
        }),
      });

      if (!verifyResponse.ok) {
        const error = await verifyResponse.json();
        throw new Error(error.detail?.message || error.detail || "Login verification failed");
      }

      const result: AuthResult = await verifyResponse.json();

      // Store session token
      localStorage.setItem("session_token", result.session_token);
      localStorage.setItem("user_data", JSON.stringify(result.user));

      return result;
    } catch (error: any) {
      console.error("Passkey authentication error:", error);
      throw error;
    }
  }

  /**
   * Authenticate using a recovery code
   */
  async useRecoveryCode(email: string, code: string): Promise<RecoveryCodeAuthResult> {
    try {
      const response = await fetch(`${API_URL}/auth/passkey/recovery/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail?.message || error.detail || "Recovery code verification failed");
      }

      const result: RecoveryCodeAuthResult = await response.json();

      // Store session token
      localStorage.setItem("session_token", result.session_token);
      localStorage.setItem("user_data", JSON.stringify(result.user));

      return result;
    } catch (error: any) {
      console.error("Recovery code authentication error:", error);
      throw error;
    }
  }

  /**
   * Acknowledge that recovery codes have been saved
   */
  async acknowledgeRecoveryCodes(token: string): Promise<void> {
    try {
      const response = await fetch(`${API_URL}/auth/passkey/recovery-codes/acknowledge`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to acknowledge recovery codes");
      }
    } catch (error: any) {
      console.error("Recovery code acknowledgment error:", error);
      throw error;
    }
  }

  /**
   * Request email recovery link
   */
  async requestEmailRecovery(email: string): Promise<void> {
    try {
      const response = await fetch(`${API_URL}/auth/passkey/email-recovery/request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error("Failed to request recovery link");
      }
    } catch (error: any) {
      console.error("Email recovery request error:", error);
      throw error;
    }
  }

  /**
   * Validate session token
   */
  async validateSession(token: string): Promise<User | null> {
    try {
      const response = await fetch(`${API_URL}/auth/validate-passkey-session`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      if (data.valid) {
        return data.user;
      }

      return null;
    } catch (error: any) {
      console.error("Session validation error:", error);
      return null;
    }
  }

  /**
   * List all passkeys for the current user
   */
  async listPasskeys(token: string): Promise<Passkey[]> {
    try {
      const response = await fetch(`${API_URL}/auth/passkey/credentials`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to list passkeys");
      }

      const data = await response.json();
      return data.credentials;
    } catch (error: any) {
      console.error("List passkeys error:", error);
      throw error;
    }
  }

  /**
   * Remove a passkey
   */
  async removePasskey(token: string, passkeyId: string): Promise<void> {
    try {
      const response = await fetch(`${API_URL}/auth/passkey/credentials/${passkeyId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail?.message || error.detail || "Failed to remove passkey");
      }
    } catch (error: any) {
      console.error("Remove passkey error:", error);
      throw error;
    }
  }

  /**
   * Logout (clear session)
   */
  async logout(): Promise<void> {
    const token = localStorage.getItem("session_token");

    if (token) {
      try {
        await fetch(`${API_URL}/auth/logout`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.error("Logout error:", error);
      }
    }

    // Clear local storage
    localStorage.removeItem("session_token");
    localStorage.removeItem("user_data");
  }
}

// Export singleton instance
export const passkeyAuth = new PasskeyAuthService();
