import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "institutional" | "success" | "warning" | "destructive" | "danger" | "outline" | "cyan" | "purple" | "navy";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border-slate-200 dark:border-slate-700",
    institutional: "bg-[#EAF3FC] text-[#062B6F] border-[#1F66B8]/30 font-semibold",
    navy: "bg-blue-950/60 text-blue-300 border-blue-800 font-medium",
    success: "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800",
    warning: "bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-800",
    destructive: "bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border-red-300 dark:border-red-800",
    danger: "bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border-red-300 dark:border-red-800",
    outline: "text-slate-800 dark:text-slate-200 border-slate-300 dark:border-slate-700",
    cyan: "bg-cyan-50 dark:bg-cyan-950/40 text-cyan-800 dark:text-cyan-300 border-cyan-300 dark:border-cyan-800 font-mono",
    purple: "bg-purple-50 dark:bg-purple-950/40 text-purple-800 dark:text-purple-300 border-purple-300 dark:border-purple-800",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors select-none",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}
