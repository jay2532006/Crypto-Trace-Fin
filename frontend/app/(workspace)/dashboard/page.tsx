// @ts-nocheck
"use client";
import * as React from "react";
import { useRouter } from "next/navigation";
import { OverviewView } from "@/views/OverviewView";
import { mockApi } from "@/services/mockApi";
import type { Case } from "@/types";

const FALLBACK_CASE: Case = {
  case_id: "CR-2026-DEMO-001",
  source: "NCRP_INTAKE",
  source_badge: "NCRP",
  complaint_id: "NCRP-2026-184721",
  fraud_type: "PIG_BUTCHERING",
  primary_chain: "ethereum",
  state: "Maharashtra",
  fraud_amount_inr: 720500,
  incident_datetime: "2026-09-16T14:32:00+05:30",
  status: "ACTIVE",
  reported_wallet: "0x71c8fb9284285741829e05e55099e0344d9f1091",
};

export default function DashboardPage() {
  const router = useRouter();
  const [activeCase, setActiveCase] = React.useState<Case>(FALLBACK_CASE);

  React.useEffect(() => {
    let active = true;
    mockApi.getCases()
      .then((res) => {
        if (active && res.data && res.data.length > 0) {
          setActiveCase(res.data[0]);
        }
      })
      .catch(() => {/* keep fallback */});
    return () => { active = false; };
  }, []);

  const handleNavigate = (route: string) => {
    if (route === "overview") router.push("/dashboard");
    else router.push(`/${route}`);
  };

  const handleOpenTransaction = async (txHash: string) => {
    router.push(`/investigations?tx=${encodeURIComponent(txHash)}`);
  };

  return (
    <OverviewView
      activeCase={activeCase}
      onNavigate={handleNavigate}
      openTransaction={handleOpenTransaction}
      uiMode="kestrel"
    />
  );
}
