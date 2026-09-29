// @ts-nocheck
"use client";
import * as React from "react";
import { EvidenceView } from "@/views/EvidenceView";

export default function Page() {
  const mockCase = { 
    case_id: "CASE-001", 
    status: "Active",
    source_badge: "NCRP",
    complaint_id: "CMP-9921",
    fraud_type: "PIG_BUTCHERING",
    primary_chain: "eth",
    state: "Maharashtra",
    fraud_amount_inr: 720500,
    reported_wallet: "0x71c8fb9284285741829e05e55099e0344d9f1091"
  };
  return <EvidenceView activeCase={mockCase} onNavigate={() => {}} openTransaction={async () => {}} setDrawer={() => {}} />
}
