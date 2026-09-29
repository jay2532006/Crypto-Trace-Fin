// @ts-nocheck
import fixture from "../04_DEMO_FIXTURE.json";
import type {
  ApiEnvelope,
  AuditEvent,
  Case,
  CryptoAlert,
  CrossChainLink,
  EvidenceManifest,
  GraphEdge,
  GraphNode,
  InvestigativeRecommendation,
  PatternFinding,
  PreservationRequest,
  RecoveryEstimate,
  ReportView,
  RiskAssessment,
  SystemStatus,
  TraceLimits,
  TraceResult,
  Transaction,
  VASPCluster,
  Wallet,
  AttributionAssessment,
  Chain,
  SourceType
} from "../types";

const SOURCE = "CRYPTO_TRACE_DEMO_FIXTURE";
const delay = (ms = 220) => new Promise((resolve) => window.setTimeout(resolve, ms));
const requestId = () => `req-demo-${Math.random().toString(16).slice(2, 8)}`;

function envelope<T>(data: T): ApiEnvelope<T> {
  return {
    success: true,
    execution_mode: "FIXTURE_REPLAY",
    demo_data: true,
    request_id: requestId(),
    source: SOURCE,
    data
  };
}

let localCase: Case | null = null;
let supervisorRequest: PreservationRequest = fixture.supervisor_request as PreservationRequest;
let auditEvents: AuditEvent[] = [...(fixture.audit_events as AuditEvent[])];

const baseTransactions = fixture.transactions as Transaction[];
const syntheticTransactions = buildSyntheticTransactions(baseTransactions);
const allTransactions = [...baseTransactions, ...syntheticTransactions];
const syntheticAlerts = buildSyntheticAlerts();

function buildSyntheticTransactions(seedRows: Transaction[]) {
  const chains: Chain[] = ["ethereum", "polygon", "tron", "bitcoin"];
  const assets = ["ETH", "USDT", "USDC", "MATIC", "BTC", "TRX"];
  const providers: Record<Chain, string> = {
    ethereum: "ETH_RPC_PRIMARY",
    polygon: "POLYGON_RPC_PRIMARY",
    tron: "TRON_GRID",
    bitcoin: "MEMPOOL_SPACE"
  };
  const senders = ["0x7F31...A92C", "0xA431...B821", "0xAB31...72C9", "0xEE91...A812", "0x91AB...0C", "TQ...TRN1", "bc1q...7d9"];
  const receivers = ["0xB921...C441", "0xC211...D739", "0xF712...2A4", "0x48DC...C12", "TQm2...W9", "0x12AD...44C1", "bc1q...9fa"];
  const start = new Date("2026-09-16T17:45:00+05:30").getTime();

  return Array.from({ length: 54 }, (_, index): Transaction => {
    const chain = chains[index % chains.length];
    const asset = assets[index % assets.length];
    const hop = (index % 6) + 1;
    const direction = index % 5 === 0 ? "IN" : "OUT";
    const eventType = chain === "tron" ? "TRC20" : chain === "bitcoin" ? "NATIVE" : index % 7 === 0 ? "BRIDGE" : asset === "ETH" ? "NATIVE" : "ERC20";
    const timestamp = new Date(start + index * 4 * 60 * 1000).toISOString();
    const value = 4200 + ((index * 9300) % 128000);
    return {
      tx_hash: `DEMO-${chain.toUpperCase()}-${String(index + 1).padStart(3, "0")}-${seedRows[index % seedRows.length].tx_hash.slice(2, 8)}`,
      chain_id: chain,
      block_height: 23893000 + index * 17,
      timestamp,
      from_address: senders[index % senders.length],
      to_address: receivers[(index + 2) % receivers.length],
      asset,
      event_type: eventType,
      amount_native: (0.08 + (index % 11) * 0.173).toFixed(asset === "BTC" ? 6 : 3),
      value_inr: value,
      direction,
      finality: index % 9 === 0 ? "PENDING_FINALITY" : "CONFIRMED",
      provider: providers[chain],
      hop,
      provenance_id: `RAW-DEMO-${chain.toUpperCase()}-${String(index + 1).padStart(3, "0")}`
    };
  });
}

function buildSyntheticAlerts(): CryptoAlert[] {
  const types = ["RAPID_HOP", "CROSS_CHAIN_EVENT", "VASP_PROXIMITY", "PARTIAL_COVERAGE", "HIGH_VALUE_OUTFLOW", "DEX_BOUNDARY"];
  const severities = ["HIGH", "MEDIUM", "LOW"];
  const wallets = ["0x7F31...A92C", "0xAB31...72C9", "0xEE91...A812", "0x91AB...0C", "TQm2...W9", "bc1q...7d9"];
  return Array.from({ length: 18 }, (_, index): CryptoAlert => ({
    alert_id: `ALERT-DEMO-${String(index + 1).padStart(3, "0")}`,
    severity: severities[index % severities.length],
    type: types[index % types.length],
    title: `${types[index % types.length].replaceAll("_", " ")} observed in fixture replay`,
    case_id: fixture.case.case_id,
    wallet: wallets[index % wallets.length],
    created_at: new Date(new Date("2026-09-16T18:00:00+05:30").getTime() + index * 6 * 60 * 1000).toISOString(),
    status: index % 4 === 0 ? "ACKNOWLEDGED" : "OPEN",
    evidence_references: index % 3 === 0 ? ["XCHAIN-001"] : [`DEMO-ETHEREUM-${String(index + 1).padStart(3, "0")}`]
  }));
}

export interface IntakeInput {
  source: SourceType;
  complaint_id?: string;
  fraud_type: string;
  fraud_amount_inr: number;
  incident_datetime: string;
  state: string;
  chain: Chain;
  wallet: string;
}

export const mockApi = {
  async getCases() {
    await delay();
    return envelope<Case[]>([localCase ?? (fixture.case as Case)]);
  },

  async getCase(caseId?: string) {
    await delay();
    const demoCase = localCase ?? (fixture.case as Case);
    if (caseId && caseId !== demoCase.case_id) return envelope(demoCase);
    return envelope<Case>(demoCase);
  },

  async createCase(input: IntakeInput) {
    await delay(420);
    if (!input.wallet || input.wallet.length < 8 || input.fraud_amount_inr <= 0) {
      return {
        success: false,
        execution_mode: "FIXTURE_REPLAY" as const,
        demo_data: true,
        request_id: requestId(),
        source: SOURCE,
        data: null,
        error: {
          code: "VALIDATION_FAILED",
          message: "Wallet and positive reported amount are required for demo intake.",
          retryable: false
        }
      };
    }
    localCase = {
      ...(fixture.case as Case),
      source: input.source,
      source_badge: input.source === "NCRP_INTAKE" ? "NCRP" : input.source === "SAHYOG" ? "SAHYOG" : "MANUAL",
      complaint_id: input.complaint_id || (input.source === "MANUAL" ? "MANUAL-DEMO-001" : fixture.case.complaint_id),
      fraud_type: input.fraud_type,
      fraud_amount_inr: Number(input.fraud_amount_inr),
      incident_datetime: input.incident_datetime,
      state: input.state,
      primary_chain: input.chain,
      reported_wallet: input.wallet,
      status: "TRACE_QUEUED"
    };
    auditEvents = [
      {
        audit_id: `AUD-UI-${auditEvents.length + 1}`,
        case_id: localCase.case_id,
        timestamp: new Date().toISOString(),
        actor_role: "INVESTIGATOR",
        action: "CASE_CREATED_FROM_DEMO_INTAKE",
        target_id: localCase.case_id,
        integrity_hash: "fixture-ui...case"
      },
      ...auditEvents
    ];
    return envelope({
      case_id: localCase.case_id,
      complaint_id: localCase.complaint_id,
      source: localCase.source,
      status: localCase.status,
      confirmation: "Case created and wallet queued for investigation."
    });
  },

  async getWallet(address?: string) {
    await delay();
    const wallet = (fixture.wallets as Wallet[]).find((item) => item.address === address || item.address.includes(address ?? "")) ?? fixture.wallets[0];
    return envelope<Wallet>(wallet as Wallet);
  },

  async getTransactions(filters?: { chain?: Chain | "all"; query?: string; limit?: number }) {
    await delay(260);
    let rows = [...allTransactions].sort((a, b) => Date.parse(b.timestamp) - Date.parse(a.timestamp));
    if (filters?.chain && filters.chain !== "all") rows = rows.filter((row) => row.chain_id === filters.chain);
    if (filters?.query) {
      const q = filters.query.toLowerCase();
      rows = rows.filter((row) => JSON.stringify(row).toLowerCase().includes(q));
    }
    return envelope<Transaction[]>(rows.slice(0, filters?.limit ?? rows.length));
  },

  async getTransaction(txHash: string) {
    await delay();
    const tx = allTransactions.find((item) => item.tx_hash === txHash || item.tx_hash.includes(txHash.replace("...", ""))) ?? allTransactions[0];
    return envelope<Transaction>(tx as Transaction);
  },

  async runTrace(limits: TraceLimits) {
    await delay(700);
    auditEvents = [
      {
        audit_id: `AUD-UI-${auditEvents.length + 1}`,
        case_id: fixture.case.case_id,
        timestamp: new Date().toISOString(),
        actor_role: "INVESTIGATOR",
        action: "TRACE_EXECUTED_WITH_LIMITS",
        target_id: fixture.trace.trace_id,
        integrity_hash: "fixture-ui...trace"
      },
      ...auditEvents
    ];
    return envelope<TraceResult>({ ...(fixture.trace as TraceResult), limits });
  },

  async getTrace() {
    await delay();
    return envelope<TraceResult>(fixture.trace as TraceResult);
  },

  async getGraph() {
    await delay();
    return envelope<{ nodes: GraphNode[]; edges: GraphEdge[] }>(fixture.graph as { nodes: GraphNode[]; edges: GraphEdge[] });
  },

  async getTypologies() {
    await delay();
    return envelope<PatternFinding[]>(fixture.typologies as PatternFinding[]);
  },

  async getVaspCandidates() {
    await delay();
    return envelope<VASPCluster[]>(fixture.vasp_candidates as VASPCluster[]);
  },

  async getAttribution() {
    await delay();
    return envelope<AttributionAssessment>(fixture.attribution as AttributionAssessment);
  },

  async getCrossChain() {
    await delay();
    return envelope<CrossChainLink[]>(fixture.cross_chain as CrossChainLink[]);
  },

  async getRisk() {
    await delay();
    return envelope<RiskAssessment>(fixture.risk as RiskAssessment);
  },

  async getRecovery() {
    await delay();
    return envelope<RecoveryEstimate>(fixture.recovery as RecoveryEstimate);
  },

  async getAlerts() {
    await delay();
    return envelope<CryptoAlert[]>([...(fixture.alerts as CryptoAlert[]), ...syntheticAlerts]);
  },

  async getRecommendations() {
    await delay();
    return envelope<InvestigativeRecommendation[]>(fixture.recommendations as InvestigativeRecommendation[]);
  },

  async getEvidence() {
    await delay();
    return envelope<EvidenceManifest>(fixture.evidence as EvidenceManifest);
  },

  async getReport() {
    await delay();
    return envelope<ReportView>({
      case: localCase ?? (fixture.case as Case),
      trace: fixture.trace as TraceResult,
      typologies: fixture.typologies as PatternFinding[],
      vasps: fixture.vasp_candidates as VASPCluster[],
      attribution: fixture.attribution as AttributionAssessment,
      cross_chain: fixture.cross_chain as CrossChainLink[],
      risk: fixture.risk as RiskAssessment,
      recovery: fixture.recovery as RecoveryEstimate,
      recommendations: fixture.recommendations as InvestigativeRecommendation[],
      evidence: fixture.evidence as EvidenceManifest,
      audit: auditEvents
    });
  },

  async getAudit() {
    await delay();
    return envelope<AuditEvent[]>(auditEvents);
  },

  async getSystemStatus() {
    await delay();
    return envelope<SystemStatus>(fixture.system_status as SystemStatus);
  },

  async getSupervisorRequests() {
    await delay();
    return envelope<PreservationRequest[]>([supervisorRequest]);
  },

  async createPreservationRequest() {
    await delay(300);
    supervisorRequest = { ...supervisorRequest, status: "PENDING_SUPERVISOR" };
    auditEvents = [
      {
        audit_id: `AUD-UI-${auditEvents.length + 1}`,
        case_id: supervisorRequest.case_id,
        timestamp: new Date().toISOString(),
        actor_role: "INVESTIGATOR",
        action: "PRESERVATION_REQUEST_DRAFTED",
        target_id: supervisorRequest.request_id,
        integrity_hash: "fixture-ui...request"
      },
      ...auditEvents
    ];
    return envelope(supervisorRequest);
  },

  async approvePreservationRequest(decision: "APPROVED" | "REJECTED", reviewer: string) {
    await delay(360);
    supervisorRequest = { ...supervisorRequest, status: decision };
    auditEvents = [
      {
        audit_id: `AUD-UI-${auditEvents.length + 1}`,
        case_id: supervisorRequest.case_id,
        timestamp: new Date().toISOString(),
        actor_role: "SUPERVISOR",
        action: decision === "APPROVED" ? "PRESERVATION_REQUEST_APPROVED" : "PRESERVATION_REQUEST_REJECTED",
        target_id: supervisorRequest.request_id,
        integrity_hash: `fixture-ui...${reviewer.toLowerCase().replace(/\s+/g, "-")}`
      },
      ...auditEvents
    ];
    return envelope(supervisorRequest);
  }
};
