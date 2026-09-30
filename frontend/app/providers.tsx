"use client";

import * as React from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { queryClient } from "@/lib/query-client";
import { useAuthStore } from "@/stores/auth-store";

export function Providers({ children }: { children: React.ReactNode }) {
  const { initialize } = useAuthStore();

  React.useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#0d1b2a",
            color: "#f8fafc",
            border: "1px solid #1e293b",
            fontSize: "13px",
            boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.5)",
          },
          success: {
            iconTheme: {
              primary: "#10b981",
              secondary: "#0d1b2a",
            },
          },
          error: {
            iconTheme: {
              primary: "#ef4444",
              secondary: "#0d1b2a",
            },
          },
        }}
      />
    </QueryClientProvider>
  );
}
