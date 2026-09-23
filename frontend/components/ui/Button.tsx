import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost" | "outline" | "gold" | "success";
  size?: "sm" | "md" | "lg" | "icon";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", isLoading = false, children, disabled, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none rounded-md select-none";

    const variants = {
      primary:
        "bg-[#062B6F] text-white hover:bg-[#082B63] active:bg-[#041E4E] shadow-sm focus-visible:ring-[#1F66B8]",
      secondary:
        "bg-[#1F66B8] text-white hover:bg-[#1A5499] active:bg-[#14427A] shadow-sm focus-visible:ring-[#1F66B8]",
      success:
        "bg-emerald-600 text-white hover:bg-emerald-700 active:bg-emerald-800 shadow-sm focus-visible:ring-emerald-500",
      danger:
        "bg-red-600 text-white hover:bg-red-700 active:bg-red-800 shadow-sm focus-visible:ring-red-500",
      ghost:
        "text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 focus-visible:ring-slate-400",
      outline:
        "border border-slate-300 dark:border-slate-700 bg-transparent text-slate-800 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-900 focus-visible:ring-[#1F66B8]",
      gold:
        "bg-[#E5A33D] text-slate-900 font-semibold hover:bg-[#D4932D] shadow-sm focus-visible:ring-[#E5A33D]",
    };

    const sizes = {
      sm: "h-8 px-3 text-xs",
      md: "h-10 px-4 text-sm",
      lg: "h-11 px-6 text-base",
      icon: "h-9 w-9 p-0",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {isLoading && (
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v8H4z"
            ></path>
          </svg>
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
