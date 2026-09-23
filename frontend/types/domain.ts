export type BlockchainNetwork = "ETH" | "BTC" | "TRON" | "POLYGON" | "SOL";

export type ConfidenceLevel = "HIGH" | "MEDIUM" | "LOW" | "LEAD";
export type LabelType = "VERIFIED" | "INFERRED" | "UNRESOLVED";
export type LinkType = "PROVEN" | "HEURISTIC_CORRELATION";
export type NoticeStatus = "DRAFT" | "PENDING_APPROVAL" | "APPROVED" | "REJECTED";

export interface CaseRecord {
  case_id: string;
  source: string;
  chain: string;
  wallet: string;
  reported_amount?: number | null;
  complaint_text?: string | null;
  complainant_name?: string | null;
  fir_number?: string | null;
  created_by: string;
  assigned_to?: string | null;
  status: "OPEN" | "CLOSED" | "ARCHIVED" | "UNDER_INVESTIGATION";
  created_date: string;
  demo_data?: boolean;
  source_origin?: string;
}

export interface HopNode {
  hop_number: number;
  from_address?: string;
  to_address?: string;
  address?: string;
  amount: number;
  asset?: string;
  timestamp_epoch?: number;
  tx_hash?: string;
  label?: string;
  vasp?: string;
  is_mixer?: boolean;
}

export interface PatternFinding {
  finding_id?: string;
  case_id?: string;
  rule?: string;
  typology_name: string;
  confidence: ConfidenceLevel;
  india_specific?: boolean;
  evidence?: string;
  evidence_json?: Record<string, any>;
  uncertainty_note?: string;
  uncertainty_notes?: string;
}

export interface ScoringStep {
  step_name: string;
  input_value: any;
  weight: number;
  contribution: number;
  reasoning: string;
}

export interface AttributionScore {
  vasp_name: string;
  vasp_id: string;
  score: number;
  policy_version: string;
  label_type: LabelType;
  confidence_band: ConfidenceLevel;
  nodal_officer_email: string;
  fiu_status: string;
  scoring_steps: ScoringStep[];
}

export interface RecoveryAssessment {
  case_id: string;
  recovery_score: number;
  action_window_hours: number;
  display_tier: "eligible" | "moderate" | "ineligible" | string;
  calculation_basis: string;
  disclaimer: string;
  components?: {
    value_ratio?: number;
    exchange_cooperation?: number;
    time_urgency?: number;
    path_clarity?: number;
  };
}

export interface TraceResult {
  address: string;
  chain: string;
  case_id?: string;
  hops: HopNode[];
  nodes?: any[];
  edges?: any[];
  typologies?: string[];
  pattern_findings?: PatternFinding[];
  attribution?: AttributionScore;
  recovery?: RecoveryAssessment;
  recovery_estimate?: RecoveryAssessment;
  nearest_vasp?: string;
  risk_score?: number;
  risk_category?: string;
  risk?: {
    composite_risk_score?: number;
    risk_level?: string;
    risk_factors?: string[];
  };
  confidence_score?: number;
  data_completeness_pct?: number;
  mode?: string;
  execution_mode?: string;
  timestamp?: string;
  execution_time_ms?: number;
  termination_reason?: string;
}

export interface PreservationNoticeDraft {
  draft_id: string;
  case_id: string;
  recipient_vasp: string;
  recipient_email: string;
  legal_authority: string;
  demanded_items: string;
  transaction_references: string[];
  draft_text: string;
  status: NoticeStatus;
  created_by: string;
  created_timestamp: string;
  supervisor_id?: string | null;
  supervisor_notes?: string | null;
  reviewed_timestamp?: string | null;
  evidence_manifest_hash?: string;
}

export interface AuditEventRecord {
  id?: number;
  event_id: string;
  timestamp: string;
  user_id: string;
  action: string;
  resource_id: string;
  resource_type: string;
  result: string;
  details?: Record<string, any>;
  details_json?: string;
  previous_event_hash: string;
  event_hash: string;
}

export interface ProviderStatusItem {
  id: string;
  name: string;
  chain: string;
  type: string;
  endpoint: string;
  operational: boolean;
  status: "ONLINE" | "DEGRADED" | "OFFLINE";
  latency_ms: number;
  error?: string | null;
  last_checked: string;
  circuit_breaker_active?: boolean;
}

export interface GraphNode {
  id: string;
  label?: string;
  address: string;
  type: 'SUSPECT' | 'VASP' | 'MIXER' | 'MULE' | 'INTERMEDIARY' | string;
  balance?: number;
  risk_score?: number;
  vasp_name?: string;
  depth?: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  amount: number;
  token?: string;
  tx_hash?: string;
  is_mixer_boundary?: boolean;
  edge_type?: string;
}
