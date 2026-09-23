import * as React from "react";
import { UserRole } from "@/types/auth";
import { Shield, ShieldAlert, ShieldCheck } from "lucide-react";

interface UserRoleBadgeProps {
  role?: UserRole;
  showIcon?: boolean;
}

export function UserRoleBadge({ role = "INVESTIGATOR", showIcon = true }: UserRoleBadgeProps) {
  const config = {
    INVESTIGATOR: {
      label: "INVESTIGATOR",
      bg: "bg-blue-900/40 text-blue-300 border-blue-700/50",
      icon: <Shield className="h-3 w-3 text-blue-400" />,
    },
    SUPERVISOR: {
      label: "SUPERVISOR",
      bg: "bg-emerald-900/40 text-emerald-300 border-emerald-700/50",
      icon: <ShieldCheck className="h-3 w-3 text-emerald-400" />,
    },
    ADMINISTRATOR: {
      label: "ADMINISTRATOR",
      bg: "bg-amber-900/40 text-amber-300 border-amber-700/50",
      icon: <ShieldAlert className="h-3 w-3 text-amber-400" />,
    },
    INTEGRATION_SERVICE: {
      label: "SYSTEM SERVICE",
      bg: "bg-purple-900/40 text-purple-300 border-purple-700/50",
      icon: <Shield className="h-3 w-3 text-purple-400" />,
    },
  }[role] || {
    label: role,
    bg: "bg-slate-800 text-slate-300 border-slate-700",
    icon: <Shield className="h-3 w-3 text-slate-400" />,
  };

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide border ${config.bg}`}>
      {showIcon && config.icon}
      <span>{config.label}</span>
    </span>
  );
}
