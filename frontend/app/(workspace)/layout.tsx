"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { TopBar } from "@/components/navigation/TopBar";
import { Sidebar } from "@/components/navigation/Sidebar";
import { DebugPanel } from "@/components/debug/DebugPanel";
import { useAuthStore } from "@/stores/auth-store";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { session, isLoading } = useAuthStore();

  React.useEffect(() => {
    if (!isLoading && !session) {
      router.replace("/login");
    }
  }, [session, isLoading, router]);

  if (isLoading || !session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#070F1E] text-slate-300">
        <div className="flex items-center gap-3 font-sans text-sm">
          <svg className="animate-spin h-5 w-5 text-[#E5A33D]" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <span>Authenticating Officer Credentials...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 dark:bg-[#070F1E]">
      <TopBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-7xl space-y-6">{children}</div>
        </main>
      </div>
      <DebugPanel />
    </div>
  );
}
