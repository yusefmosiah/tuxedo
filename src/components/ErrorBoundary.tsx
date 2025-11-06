import React, { Component, ReactNode } from "react";
import { Text, Button } from "@stellar/design-system";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
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
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>⚠️</div>
            <Text
              as="h1"
              size="lg"
              weight="bold"
              style={{ marginBottom: "16px" }}
            >
              Something went wrong
            </Text>
            <Text
              as="p"
              size="sm"
              style={{
                color: "var(--color-text-secondary)",
                marginBottom: "24px",
              }}
            >
              {this.state.error?.message ||
                "An unexpected error occurred. Please try refreshing the page."}
            </Text>
            <Button
              variant="primary"
              size="md"
              onClick={() => window.location.reload()}
              isFullWidth
            >
              Refresh Page
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
