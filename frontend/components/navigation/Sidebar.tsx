"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderLock,
  GitFork,
  Network,
  Building2,
  Scale,
  FileText,
  Binary,
  History,
  Activity,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Case Management", href: "/cases", icon: FolderLock },
  { label: "Investigation Workspace", href: "/investigations", icon: GitFork },
  { label: "Typology Findings", href: "/typologies", icon: Network },
  { label: "VASP Attribution", href: "/attribution", icon: Building2 },
  { label: "Recovery Estimation", href: "/recovery", icon: Scale },
  { label: "Legal Notices (Sec 91)", href: "/legal-notices", icon: FileText },
  { label: "Evidence Manifest", href: "/evidence", icon: Binary },
  { label: "Audit Ledger", href: "/audit", icon: History },
  { label: "Provider Status", href: "/provider-status", icon: Activity },
  { label: "System Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = React.useState(false);

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-[#070F1E] transition-all duration-300 z-20 shadow-sm",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-6 flex h-6 w-6 items-center justify-center rounded-full border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-500 hover:text-slate-800 dark:hover:text-white shadow-sm transition-colors z-30"
        title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? <ChevronRight className="h-3.5 w-3.5" /> : <ChevronLeft className="h-3.5 w-3.5" />}
      </button>

      {/* Nav Link List */}
      <nav className="flex-1 space-y-1 p-3 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs font-medium transition-all group select-none",
                isActive
                  ? "bg-[#062B6F] text-white font-semibold shadow-sm"
                  : "text-slate-700 dark:text-slate-300 hover:bg-[#EAF3FC] hover:text-[#062B6F] dark:hover:bg-slate-800/80 dark:hover:text-white"
              )}
              title={collapsed ? item.label : undefined}
            >
              <Icon
                className={cn(
                  "h-4 w-4 flex-shrink-0 transition-colors",
                  isActive ? "text-[#E5A33D]" : "text-slate-400 group-hover:text-[#1F66B8]"
                )}
              />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer Branding Info */}
      {!collapsed && (
        <div className="border-t border-slate-200 dark:border-slate-800/80 p-4 text-[10px] text-slate-400 space-y-1">
          <p className="font-semibold text-slate-600 dark:text-slate-300">CryptoTrace LEA v2.0</p>
          <p>MHA / I4C Authorized Evaluation Build</p>
        </div>
      )}
    </aside>
  );
}
