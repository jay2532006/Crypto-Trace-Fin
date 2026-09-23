"use client";

import * as React from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/query-client";
import { useAuthStore } from "@/stores/auth-store";

export function Providers({ children }: { children: React.ReactNode }) {
  const { initialize } = useAuthStore();

  React.useEffect(() => {
    initialize();
  }, [initialize]);

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
