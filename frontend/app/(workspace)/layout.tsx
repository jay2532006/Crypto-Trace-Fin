// @ts-nocheck
"use client";
import * as React from "react";
import { useRouter, usePathname } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { DrawerPanel } from "@/components/layout/DrawerPanel";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [mobileNavOpen, setMobileNavOpen] = React.useState(false);
  const [drawer, setDrawer] = React.useState<any>(null);
  
  let currentRoute = "overview";
  if (pathname.includes("/cases")) currentRoute = "cases";
  else if (pathname.includes("/alerts")) currentRoute = "alerts";
  else if (pathname.includes("/investigations")) currentRoute = "investigations";
  else if (pathname.includes("/transactions")) currentRoute = "transactions";
  else if (pathname.includes("/wallets")) currentRoute = "wallets";
  else if (pathname.includes("/typologies")) currentRoute = "typologies";
  else if (pathname.includes("/vasp")) currentRoute = "vasp";
  else if (pathname.includes("/evidence")) currentRoute = "evidence";
  else if (pathname.includes("/reports")) currentRoute = "reports";
  else if (pathname.includes("/supervisor")) currentRoute = "supervisor";
  else if (pathname.includes("/system-status")) currentRoute = "system-status";
  else if (pathname.includes("/cross-chain")) currentRoute = "cross-chain";

  const handleNavigate = (route: string) => {
    if (route === "overview") router.push("/dashboard");
    else router.push(`/${route}`);
  };

  return (
    <div className="kestrel-app">
      <Sidebar
        currentRoute={currentRoute}
        onNavigate={handleNavigate}
        openAlertsCount={18}
        mobileOpen={mobileNavOpen}
        onClose={() => setMobileNavOpen(false)}
        onQuickAction={() => {}}
      />
      <main className="kestrel-main">
        <Topbar
          activeCase={null}
          role="INVESTIGATOR"
          onRoleToggle={() => {}}
          uiMode="kestrel"
          onToggleUiMode={() => {}}
          searchQuery=""
          onSearchChange={() => {}}
          onRefresh={() => {}}
          onOpenAlerts={() => {}}
          onOpenNavigation={() => setMobileNavOpen(true)}
        />
        <div className="kestrel-content">{children}</div>
      </main>
      <DrawerPanel drawer={drawer} onClose={() => setDrawer(null)} openTransaction={() => {}} />
    </div>
  );
}
