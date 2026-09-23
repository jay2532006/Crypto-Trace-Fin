import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { ShieldAlert, ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-slate-50 dark:bg-[#070F1E]">
      <div className="max-w-md w-full bg-white dark:bg-[#0D1B2A] border border-slate-200 dark:border-slate-800 rounded-xl p-8 shadow-xl text-center space-y-4">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-600">
          <ShieldAlert className="h-8 w-8 text-[#E5A33D]" />
        </div>
        <h2 className="text-xl font-bold font-display text-[#062B6F] dark:text-white">
          404 — Forensic Dossier Not Found
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          The requested case, resource, or investigation endpoint does not exist or has been archived.
        </p>
        <div className="pt-2">
          <Link href="/dashboard">
            <Button variant="primary" size="sm" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              <span>Return to Case Overview</span>
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
