/**
 * Passkey Authentication Service
 * Simplified WebAuthn implementation with comprehensive error handling and debugging
 */

import { API_BASE_URL } from "../lib/api";

// Global debug log storage for UI display
export const debugLogs: string[] = [];

/**
 * Add a debug log entry with timestamp
 */
function addDebugLog(message: string, data?: any): void {
  const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
  const logEntry = `[${timestamp}] ${message}`;
  console.log(logEntry, data || '');
  debugLogs.push(data ? `${logEntry} ${JSON.stringify(data, null, 2)}` : logEntry);

  // Keep only last 100 logs
  if (debugLogs.length > 100) {
    debugLogs.shift();
  }
}

/**
 * Clear all debug logs
 */
export function clearDebugLogs(): void {
  debugLogs.length = 0;
  console.log('🧹 Debug logs cleared');
}

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
    addDebugLog("🔐 STARTING PASSKEY REGISTRATION");
    addDebugLog("📧 Email", { email });
    addDebugLog("🌐 Environment", {
      origin: window.location.origin,
      protocol: window.location.protocol,
      hostname: window.location.hostname,
      href: window.location.href,
      apiBaseUrl: API_BASE_URL,
    });

    if (!this.isSupported()) {
      addDebugLog("❌ Passkeys not supported in this browser");
      throw new Error("Passkeys are not supported in this browser");
    }
    addDebugLog("✅ WebAuthn is supported");

    // Step 1: Get challenge from backend
    addDebugLog("📡 Step 1: Requesting registration challenge from backend");
    const registerStartUrl = `${API_BASE_URL}/auth/passkey/register/start`;
    addDebugLog("🔗 URL", { url: registerStartUrl });

    let startResponse: Response;
    try {
      const startTime = performance.now();
      startResponse = await fetch(registerStartUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const endTime = performance.now();
      addDebugLog(`⏱️  Request completed in ${(endTime - startTime).toFixed(2)}ms`);
      addDebugLog("📊 Response status", {
        status: startResponse.status,
        statusText: startResponse.statusText,
        ok: startResponse.ok,
        headers: Object.fromEntries(startResponse.headers.entries()),
      });
    } catch (error: any) {
      addDebugLog("❌ Network error during registration start", {
        errorName: error?.name,
        errorMessage: error?.message,
        errorStack: error?.stack,
      });
      logWebAuthnError("Network error during registration start", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server"}`,
      );
    }

    if (!startResponse.ok) {
      addDebugLog("❌ Registration start failed", {
        status: startResponse.status,
        statusText: startResponse.statusText,
      });

      let errorMessage = "Failed to start registration";
      try {
        const error = await startResponse.json();
        addDebugLog("📄 Error response body", error);
        errorMessage =
          error.detail?.message || error.error?.message || error.message;

        if (startResponse.status === 409) {
          errorMessage =
            error.detail?.message ||
            "An account with this email already exists. Please sign in instead.";
        }
      } catch (parseError) {
        addDebugLog("⚠️  Failed to parse error response", { parseError });
        errorMessage = `Server error (${startResponse.status}): ${startResponse.statusText}`;
      }
      throw new Error(errorMessage);
    }

    const responseData = await startResponse.json();
    const { challenge_id, options } = responseData;
    addDebugLog("✅ Challenge received", {
      challenge_id,
      options: {
        rp: options.rp,
        user: { name: options.user?.name, displayName: options.user?.displayName },
        timeout: options.timeout,
        authenticatorSelection: options.authenticatorSelection,
        excludeCredentialsCount: options.excludeCredentials?.length || 0,
      },
    });

    // Step 2: Create credential using WebAuthn
    addDebugLog("📡 Step 2: Creating passkey credential");
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

    addDebugLog("🔑 Calling navigator.credentials.create()", {
      rp: options.rp,
      user: { name: options.user.name, displayName: options.user.displayName },
      timeout: options.timeout,
      authenticatorSelection: options.authenticatorSelection,
      pubKeyCredParamsCount: options.pubKeyCredParams?.length || 0,
    });

    let credential: Credential | null;
    try {
      const createStartTime = performance.now();
      credential = await navigator.credentials.create({
        publicKey: publicKeyOptions,
      });
      const createEndTime = performance.now();
      addDebugLog(`✅ Credential created in ${(createEndTime - createStartTime).toFixed(2)}ms`);

      if (credential) {
        addDebugLog("🔍 Credential details", {
          id: credential.id,
          type: credential.type,
        });
      }
    } catch (error: any) {
      addDebugLog("❌ WebAuthn credential creation failed", {
        errorName: error?.name,
        errorMessage: error?.message,
        errorCode: error?.code,
      });
      logWebAuthnError("WebAuthn registration failed", error);
      throw new Error(getWebAuthnErrorMessage(error, "registration"));
    }

    if (!credential) {
      addDebugLog("❌ No credential returned from navigator.credentials.create()");
      throw new Error("Failed to create passkey - no credential returned");
    }
    addDebugLog("✅ Passkey credential created successfully");

    // Step 3: Verify with backend
    addDebugLog("📡 Step 3: Verifying credential with backend");
    const credentialData = this.credentialToJSON(
      credential as PublicKeyCredential,
    );
    addDebugLog("🔍 Serialized credential", {
      id: credentialData.id,
      type: credentialData.type,
      hasResponse: !!credentialData.response,
      transportsCount: credentialData.response?.transports?.length || 0,
    });

    const registerVerifyUrl = `${API_BASE_URL}/auth/passkey/register/verify`;
    addDebugLog("🔗 Verification URL", { url: registerVerifyUrl });

    let verifyResponse: Response;
    try {
      const verifyStartTime = performance.now();
      verifyResponse = await fetch(registerVerifyUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          challenge_id,
          credential: credentialData,
        }),
      });
      const verifyEndTime = performance.now();
      addDebugLog(`⏱️  Verification request completed in ${(verifyEndTime - verifyStartTime).toFixed(2)}ms`);
      addDebugLog("📊 Verification response status", {
        status: verifyResponse.status,
        statusText: verifyResponse.statusText,
        ok: verifyResponse.ok,
        headers: Object.fromEntries(verifyResponse.headers.entries()),
      });
    } catch (error: any) {
      addDebugLog("❌ Network error during verification", {
        errorName: error?.name,
        errorMessage: error?.message,
        errorStack: error?.stack,
      });
      logWebAuthnError("Network error during registration verification", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server"}`,
      );
    }

    if (!verifyResponse.ok) {
      addDebugLog("❌ Registration verification failed", {
        status: verifyResponse.status,
        statusText: verifyResponse.statusText,
      });

      let errorMessage = "Failed to complete registration";
      try {
        const error = await verifyResponse.json();
        addDebugLog("📄 Verification error response", error);
        errorMessage = error.error?.message || error.detail?.message || error.message || errorMessage;
      } catch (parseError) {
        addDebugLog("⚠️  Failed to parse verification error response", { parseError });
        errorMessage = `Server error (${verifyResponse.status}): ${verifyResponse.statusText}`;
      }
      throw new Error(errorMessage);
    }

    const result: RegistrationResult = await verifyResponse.json();
    addDebugLog("✅ REGISTRATION COMPLETED SUCCESSFULLY", {
      userId: result.user.id,
      email: result.user.email,
      recoveryCodesCount: result.recovery_codes.length,
    });

    // Store session
    localStorage.setItem("session_token", result.session_token);
    localStorage.setItem("user_data", JSON.stringify(result.user));

    return result;
  }

  /**
   * Authenticate with a passkey
   */
  async login(email?: string): Promise<AuthResult> {
    addDebugLog("🔐 STARTING PASSKEY LOGIN");
    addDebugLog("📧 Email", { email: email || "none (discoverable)" });
    addDebugLog("🌐 Environment", {
      origin: window.location.origin,
      protocol: window.location.protocol,
      hostname: window.location.hostname,
      apiBaseUrl: API_BASE_URL,
    });

    if (!this.isSupported()) {
      addDebugLog("❌ Passkeys not supported in this browser");
      throw new Error("Passkeys are not supported in this browser");
    }
    addDebugLog("✅ WebAuthn is supported");

    // Step 1: Get challenge from backend
    addDebugLog("📡 Step 1: Requesting login challenge from backend");
    const loginStartUrl = `${API_BASE_URL}/auth/passkey/login/start`;
    addDebugLog("🔗 URL", { url: loginStartUrl });

    let startResponse: Response;
    try {
      const startTime = performance.now();
      startResponse = await fetch(loginStartUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const endTime = performance.now();
      addDebugLog(`⏱️  Request completed in ${(endTime - startTime).toFixed(2)}ms`);
      addDebugLog("📊 Response status", {
        status: startResponse.status,
        statusText: startResponse.statusText,
        ok: startResponse.ok,
        headers: Object.fromEntries(startResponse.headers.entries()),
      });
    } catch (error: any) {
      addDebugLog("❌ Network error during login start", {
        errorName: error?.name,
        errorMessage: error?.message,
        errorStack: error?.stack,
      });
      logWebAuthnError("Network error during login start", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server"}`,
      );
    }

    if (!startResponse.ok) {
      addDebugLog("❌ Login start failed", {
        status: startResponse.status,
        statusText: startResponse.statusText,
      });

      let errorMessage = "Failed to start login";
      try {
        const error = await startResponse.json();
        addDebugLog("📄 Error response body", error);
        errorMessage = error.error?.message || error.detail?.message || error.message || errorMessage;
      } catch (parseError) {
        addDebugLog("⚠️  Failed to parse error response", { parseError });
        errorMessage = `Server error (${startResponse.status}): ${startResponse.statusText}`;
      }
      throw new Error(errorMessage);
    }

    const responseData = await startResponse.json();
    const { challenge_id, options } = responseData;
    addDebugLog("✅ Challenge received", {
      challenge_id,
      options: {
        rpId: options.rpId,
        timeout: options.timeout,
        allowCredentialsCount: options.allowCredentials?.length || 0,
        userVerification: options.userVerification,
      },
    });

    // Step 2: Get credential using WebAuthn
    addDebugLog("📡 Step 2: Getting passkey credential");
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

    addDebugLog("🔑 Calling navigator.credentials.get()", {
      rpId: options.rpId,
      timeout: options.timeout,
      allowCredentialsCount: options.allowCredentials?.length || 0,
      userVerification: options.userVerification,
    });

    let credential: Credential | null;
    try {
      const getStartTime = performance.now();
      credential = await navigator.credentials.get({
        publicKey: publicKeyOptions,
      });
      const getEndTime = performance.now();
      addDebugLog(`✅ Credential retrieved in ${(getEndTime - getStartTime).toFixed(2)}ms`);

      if (credential) {
        addDebugLog("🔍 Credential details", {
          id: credential.id,
          type: credential.type,
        });
      }
    } catch (error: any) {
      addDebugLog("❌ WebAuthn authentication failed", {
        errorName: error?.name,
        errorMessage: error?.message,
        errorCode: error?.code,
      });
      logWebAuthnError("WebAuthn login failed", error);
      throw new Error(getWebAuthnErrorMessage(error, "login"));
    }

    if (!credential) {
      addDebugLog("❌ No credential returned from navigator.credentials.get()");
      throw new Error("Failed to authenticate - no credential returned");
    }
    addDebugLog("✅ Passkey credential retrieved successfully");

    // Step 3: Verify with backend
    addDebugLog("📡 Step 3: Verifying credential with backend");
    const credentialData = this.credentialToJSON(
      credential as PublicKeyCredential,
    );
    addDebugLog("🔍 Serialized credential", {
      id: credentialData.id,
      type: credentialData.type,
      hasResponse: !!credentialData.response,
    });

    const loginVerifyUrl = `${API_BASE_URL}/auth/passkey/login/verify`;
    addDebugLog("🔗 Verification URL", { url: loginVerifyUrl });

    let verifyResponse: Response;
    try {
      const verifyStartTime = performance.now();
      verifyResponse = await fetch(loginVerifyUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          challenge_id,
          credential: credentialData,
        }),
      });
      const verifyEndTime = performance.now();
      addDebugLog(`⏱️  Verification request completed in ${(verifyEndTime - verifyStartTime).toFixed(2)}ms`);
      addDebugLog("📊 Verification response status", {
        status: verifyResponse.status,
        statusText: verifyResponse.statusText,
        ok: verifyResponse.ok,
        headers: Object.fromEntries(verifyResponse.headers.entries()),
      });
    } catch (error: any) {
      addDebugLog("❌ Network error during verification", {
        errorName: error?.name,
        errorMessage: error?.message,
        errorStack: error?.stack,
      });
      logWebAuthnError("Network error during login verification", error);
      throw new Error(
        `Network error: ${error.message || "Could not connect to server"}`,
      );
    }

    if (!verifyResponse.ok) {
      addDebugLog("❌ Login verification failed", {
        status: verifyResponse.status,
        statusText: verifyResponse.statusText,
      });

      let errorMessage = "Failed to verify authentication";
      try {
        const error = await verifyResponse.json();
        addDebugLog("📄 Verification error response", error);
        errorMessage = error.error?.message || error.detail?.message || error.message || errorMessage;
      } catch (parseError) {
        addDebugLog("⚠️  Failed to parse verification error response", { parseError });
        errorMessage = `Server error (${verifyResponse.status}): ${verifyResponse.statusText}`;
      }
      throw new Error(errorMessage);
    }

    const result: AuthResult = await verifyResponse.json();
    addDebugLog("✅ LOGIN COMPLETED SUCCESSFULLY", {
      userId: result.user.id,
      email: result.user.email,
    });

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
