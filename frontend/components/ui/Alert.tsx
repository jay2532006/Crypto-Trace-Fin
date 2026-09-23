import * as React from "react";
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";
import { cn } from "@/lib/utils";

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "info" | "warning" | "danger" | "success";
  title?: string;
}

export function Alert({ className, variant = "info", title, children, ...props }: AlertProps) {
  const icons = {
    info: <Info className="h-4 w-4 text-[#1F66B8] mt-0.5 flex-shrink-0" />,
    warning: <AlertTriangle className="h-4 w-4 text-[#E5A33D] mt-0.5 flex-shrink-0" />,
    danger: <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />,
    success: <CheckCircle2 className="h-4 w-4 text-[#198754] mt-0.5 flex-shrink-0" />,
  };

  const variants = {
    info: "bg-[#EAF3FC] border-[#1F66B8]/30 text-[#062B6F]",
    warning: "bg-amber-50 dark:bg-amber-950/30 border-amber-300 dark:border-amber-800 text-amber-900 dark:text-amber-200",
    danger: "bg-red-50 dark:bg-red-950/30 border-red-300 dark:border-red-800 text-red-900 dark:text-red-200",
    success: "bg-emerald-50 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200",
  };

  return (
    <div
      role="alert"
      className={cn("relative w-full rounded-lg border p-4 text-xs flex gap-3", variants[variant], className)}
      {...props}
    >
      {icons[variant]}
      <div className="space-y-1">
        {title && <h5 className="font-bold tracking-tight">{title}</h5>}
        <div className="leading-relaxed opacity-95">{children}</div>
      </div>
    </div>
  );
}
