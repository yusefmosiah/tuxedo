/**
 * Pre-load WebAuthn challenge options to maintain user gesture chain
 *
 * This hook fetches challenge options BEFORE user interaction to avoid
 * breaking the user gesture chain required by iOS Safari for WebAuthn.
 *
 * Background: Safari requires navigator.credentials.create() to be called
 * directly within a user-activated event (click, touch). If we fetch the
 * challenge asynchronously AFTER the click, the gesture chain is broken
 * and iOS Safari will reject the WebAuthn call.
 */

import { useState, useEffect, useCallback } from "react";
import { API_BASE_URL } from "../lib/api";

export interface ChallengeOptions {
  challenge_id: string;
  options: any;
  preloadedAt: number; // Timestamp for expiration tracking
}

interface UseChallengePreloadResult {
  options: ChallengeOptions | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
  clear: () => void;
}

/**
 * Validates email format (basic check)
 */
function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Pre-loads WebAuthn challenge options for passkey registration
 *
 * @param email - User's email address
 * @param enabled - Whether to enable pre-loading (default: true)
 * @param debounceMs - Debounce delay in milliseconds (default: 500)
 *
 * @returns Object containing preloaded options, loading state, error, and utility functions
 *
 * @example
 * const { options, loading, error } = useChallengePreload(email);
 *
 * // When user clicks "Sign Up", options are already loaded
 * if (options) {
 *   const result = await passkeyAuthService.registerWithPreloadedOptions(email, options);
 * }
 */
export function useChallengePreload(
  email: string,
  enabled: boolean = true,
  debounceMs: number = 500,
): UseChallengePreloadResult {
  const [options, setOptions] = useState<ChallengeOptions | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Clear options manually
  const clear = useCallback(() => {
    setOptions(null);
    setError(null);
  }, []);

  // Refresh options manually
  const refresh = useCallback(() => {
    setOptions(null);
    setError(null);
  }, []);

  useEffect(() => {
    // Reset state when email changes or becomes invalid
    if (!enabled || !email || !isValidEmail(email)) {
      setOptions(null);
      setError(null);
      setLoading(false);
      return;
    }

    // Debounce: Wait for user to finish typing
    const timeoutId = setTimeout(async () => {
      setLoading(true);
      setError(null);

      try {
        console.log("🔄 Pre-loading challenge options for:", email);

        const response = await fetch(
          `${API_BASE_URL}/auth/passkey/register/start`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email }),
          },
        );

        if (!response.ok) {
          // Handle specific error cases
          if (response.status === 409) {
            setError(
              "An account with this email already exists. Please sign in instead.",
            );
          } else {
            let errorMessage = "Failed to prepare registration";
            try {
              const errorData = await response.json();
              errorMessage =
                errorData.detail?.message ||
                errorData.error?.message ||
                errorData.message ||
                errorMessage;
            } catch {
              errorMessage = `Server error (${response.status})`;
            }
            setError(errorMessage);
          }
          setOptions(null);
          return;
        }

        const data = await response.json();

        if (!data.challenge_id || !data.options) {
          throw new Error("Invalid response format from server");
        }

        setOptions({
          challenge_id: data.challenge_id,
          options: data.options,
          preloadedAt: Date.now(),
        });

        console.log("✅ Challenge options pre-loaded successfully");
      } catch (err: any) {
        console.error("❌ Failed to pre-load challenge:", err);
        setError(err.message || "Network error. Please check your connection.");
        setOptions(null);
      } finally {
        setLoading(false);
      }
    }, debounceMs);

    // Cleanup: Cancel pending requests when email changes
    return () => {
      clearTimeout(timeoutId);
    };
  }, [email, enabled, debounceMs]);

  // Auto-refresh expired challenges (15 minutes)
  useEffect(() => {
    if (!options) return;

    const CHALLENGE_LIFETIME_MS = 15 * 60 * 1000; // 15 minutes
    const age = Date.now() - options.preloadedAt;
    const timeUntilExpiry = CHALLENGE_LIFETIME_MS - age;

    if (timeUntilExpiry <= 0) {
      // Already expired
      console.warn("⚠️ Challenge expired, refreshing...");
      refresh();
      return;
    }

    // Set timer to refresh before expiration
    const refreshTimer = setTimeout(() => {
      console.log("🔄 Challenge expiring soon, refreshing...");
      refresh();
    }, timeUntilExpiry);

    return () => clearTimeout(refreshTimer);
  }, [options, refresh]);

  return {
    options,
    loading,
    error,
    refresh,
    clear,
  };
}
