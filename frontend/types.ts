export type ExecutionMode = "FIXTURE_REPLAY" | "LIVE";
export type Chain = "ethereum" | "polygon" | "tron" | "bitcoin";
export type SourceType = "NCRP_INTAKE" | "SAHYOG" | "MANUAL";
export type LabelStatus = "VERIFIED" | "INFERRED" | "UNRESOLVED" | "LABELLED";
export type Coverage = "COMPLETE" | "PARTIAL";
export type EvidenceState = "DIRECT" | "HEURISTIC" | "BRIDGE_PROVEN" | "CORRELATION";
export type Role = "INVESTIGATOR" | "SUPERVISOR";

export interface ApiEnvelope<T> {
  success: boolean;
  execution_mode: ExecutionMode;
  demo_data: boolean;
  request_id: string;
  source: string;
  data: T;
  error?: { code: string; message: string; retryable: boolean };
}

export interface Case {
  case_id: string;
  complaint_id?: string;
  source: SourceType;
  source_badge: string;
  status: string;
  fraud_type: string;
  fraud_amount_inr: number;
  incident_datetime: string;
  state: string;
  primary_chain: Chain;
  reported_wallet: string;
  wallet_type: string;
  data_coverage: Coverage;
  created_at: string;
  last_updated_at: string;
}

export interface Wallet {
  id: string;
  address: string;
  chain: Chain;
  type: string;
  status: string;
  risk_tier: string;
  coverage: Coverage;
}

export interface Transaction {
  tx_hash: string;
  chain_id: Chain;
  block_height: number;
  timestamp: string;
  from_address: string;
  to_address: string;
  asset: string;
  event_type: "NATIVE" | "ERC20" | "TRC20" | "BRIDGE" | "INTERNAL";
  amount_native: string;
  value_inr: number;
  direction: "IN" | "OUT";
  finality: string;
  provider: string;
  hop: number;
  provenance_id: string;
}

export interface Asset {
  symbol: string;
  chain: Chain;
  decimals?: number;
}

export interface Transfer extends Transaction {
  transfer_index?: number;
}

export interface EntityLabel {
  label: string;
  status: LabelStatus;
  source: string;
  confidence: number;
}

export interface GraphNode {
  id: string;
  label: string;
  address: string;
  type: string;
  chain: Chain;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  tx_hash: string;
  value_inr: number;
  asset: string;
  hop: number;
  style: "SOLID" | "DASHED";
  evidence_type: EvidenceState;
  edge_label?: string;
}

export interface TraceResult {
  trace_id: string;
  root_wallet: string;
  node_count: number;
  edge_count: number;
  max_depth_reached: number;
  termination_reason: string;
  coverage: Coverage;
  limits: TraceLimits;
  paths: string[][];
}

export interface TraceLimits {
  max_hops: number;
  time_window_hours: number;
  minimum_value_inr: number;
  max_outflows: number;
  max_nodes: number;
  timeout_seconds: number;
}

export interface PatternFinding {
  finding_id: string;
  pattern_type: string;
  india_specific: boolean;
  confidence: string | number;
  confidence_band?: string;
  rule_version: string;
  evidence_references: string[];
  data_coverage: Coverage;
  uncertainty_note?: string;
  victim_wallet_count?: number;
  intermediate_wallet_addresses?: string[];
  aggregation_address?: string;
  time_window_hours?: number;
  total_value_aggregated_usd?: number;
  evidence_strength?: string;
}

export interface VASPCluster {
  candidate_id: string;
  name: string;
  address: string;
  chain: Chain;
  label_status: "VERIFIED" | "INFERRED" | "UNRESOLVED";
  label_source: string;
  confidence: number;
  confidence_band: string;
  hop_distance: number;
  evidence_references: string[];
  ownership_proof: false;
}

export interface AttributionAssessment {
  policy_version: string;
  candidate_id: string;
  base_weights: Record<string, number>;
  fired_modifiers: string[];
  final_weights: Record<string, number>;
  score: number;
  confidence_band: string;
  scoring_metadata: {
    steps: string[];
    path_contains_bridge: boolean;
  };
}

export interface CrossChainLink {
  link_id: string;
  from_chain: Chain;
  to_chain: Chain;
  from_address: string;
  to_address: string;
  relationship: "PROVEN_BRIDGE" | "HEURISTIC_CORRELATION";
  evidence_strength: "DIRECT" | "CORRELATION";
  timestamp_delta_minutes: number;
  value_correlation: number;
  uncertainty: boolean;
  evidence_references: string[];
}

export interface RiskAssessment {
  risk_tier: string;
  risk_score: number;
  rule_version: string;
  factors: Array<{ name: string; weight: number; evidence: string[] }>;
}

export interface RecoveryEstimate {
  eligible: boolean;
  label: "Heuristic Recovery Estimate";
  recovery_score: number;
  display_tier: string;
  action_window_hours: number;
  value_ratio: number;
  exchange_cooperation: number;
  time_urgency: number;
  path_clarity: number;
  top_candidate_confidence: number;
  disclaimer: string;
  cooperation_source: string;
  cooperation_last_reviewed: string;
}

export interface InvestigativeRecommendation {
  recommendation_id: string;
  priority: string;
  title: string;
  reason: string;
  evidence_references: string[];
  uncertainty: string;
}

export interface EvidenceItem {
  evidence_id: string;
  type: string;
  source: string;
  reference: string;
  payload_hash: string;
  immutable: boolean;
}

export interface EvidenceManifest {
  manifest_id: string;
  integrity_status: string;
  hash_algorithm: string;
  items: EvidenceItem[];
}

export interface CryptoAlert {
  alert_id: string;
  severity: string;
  type: string;
  title: string;
  case_id: string;
  wallet: string;
  created_at: string;
  status: string;
  evidence_references: string[];
}

export interface AuditEvent {
  audit_id: string;
  case_id: string;
  timestamp: string;
  actor_role: "INVESTIGATOR" | "SUPERVISOR" | "SYSTEM";
  action: string;
  target_id: string;
  integrity_hash: string;
}

export interface PreservationRequest {
  request_id: string;
  case_id: string;
  request_type: string;
  recipient: string;
  status: "DRAFT" | "PENDING_SUPERVISOR" | "APPROVED" | "REJECTED";
  purpose: string;
  evidence_manifest_id: string;
  drafted_by: string;
}

export interface SystemStatus {
  execution_mode: ExecutionMode;
  chains: Record<Chain, { status: string; last_block: number }>;
  pipeline: Record<string, string>;
}

export interface ReportView {
  case: Case;
  trace: TraceResult;
  typologies: PatternFinding[];
  vasps: VASPCluster[];
  attribution: AttributionAssessment;
  cross_chain: CrossChainLink[];
  risk: RiskAssessment;
  recovery: RecoveryEstimate;
  recommendations: InvestigativeRecommendation[];
  evidence: EvidenceManifest;
  audit: AuditEvent[];
}
