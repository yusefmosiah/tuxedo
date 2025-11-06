import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import "@stellar/design-system/build/styles.min.css";
import { AgentProvider } from "./providers/AgentProvider.tsx";
import { NotificationProvider } from "./providers/NotificationProvider.tsx";
import { AuthProvider } from "./contexts/AuthContext_passkey.tsx";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
    },
  },
});

createRoot(document.getElementById("root") as HTMLElement).render(
  <StrictMode>
    <NotificationProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider>
            <AgentProvider>
              <App />
            </AgentProvider>
          </AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </NotificationProvider>
  </StrictMode>,
);
