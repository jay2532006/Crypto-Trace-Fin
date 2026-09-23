"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";

export default function RootPage() {
  const router = useRouter();
  const { session, isLoading } = useAuthStore();

  React.useEffect(() => {
    if (!isLoading) {
      if (session) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }
    }
  }, [session, isLoading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#070F1E] text-slate-300">
      <div className="flex items-center gap-3 font-sans text-sm">
        <svg className="animate-spin h-5 w-5 text-[#E5A33D]" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        <span>Loading CryptoTrace LEA Workspace...</span>
      </div>
    </div>
  );
}
