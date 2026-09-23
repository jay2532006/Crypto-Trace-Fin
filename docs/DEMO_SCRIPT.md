# CryptoTrace LEA — SIH 26183 Live Demonstration Script

## 1. Overview & Demonstration Objectives

This script guides the presenter through the 15-step live demonstration sequence for **CryptoTrace LEA (Smart India Hackathon SIH 26183)**. 

The demonstration highlights that CryptoTrace LEA is **evidence-first, explainable, and legally defensible**, rejecting fabricated metrics and unverified data claims.

---

## 2. Opening: The Three Core Innovations (2 Minutes)

Before opening the investigative case, present the three core algorithmic contributions in the system:

1. **`MULE_NETWORK` Typology Rule**:
   - Algorithmic criteria: $\ge 3$ intermediate wallets, sub-60 minute velocity, $\pm 15\%$ gas/fee tolerance.
   - **Legal Defensibility**: Strictly caps confidence at `MEDIUM` and attaches an explicit uncertainty disclosure: *"Automated typology heuristic. Intermediate addresses may represent non-custodial aggregators or automated payment processors. Field corroboration required."*

2. **`AdaptiveVASPScorer`**:
   - 6-step context-weighted scoring mechanism (`policy_v1_india_kyc`).
   - Distinguishes `VERIFIED` (on-chain operational proof) from `INFERRED` (heuristic pattern).
   - Clamps individual evidence contributions to $[0.01, 0.80]$ with normalization to $1.0$.

3. **`Heuristic Recovery Estimate`**:
   - Governed by strict PRD FR-016 boundary rules:
     - Zero-hop trace $\implies$ Invalid (untracked).
     - Attribution candidate is `LEAD` or `NONE` $\implies$ Invalid (no VASP counterparty identified).
     - Sub-$120 amount $\implies$ Invalid (uneconomic to freeze).
   - Generates an actionable 72-hour window countdown linked to VASP compliance SLA.

---

## 3. The 15-Step Investigative Case Walkthrough (8 Minutes)

### Step 1: Authorized Intake
- **Action**: Navigate to Case Intake or use NCRP / Case API (`POST /api/v1/cases`).
- **Narration**: *"Every investigation begins with an authorized case intake. Incoming data is tagged with complainant details, FIR/NCRP reference numbers, and actor credentials. Private keys or seed phrases in intake narratives are automatically detected and rejected for compliance."*

### Step 2: Source & Chain Provenance
- **Action**: Inspect Case Metadata card.
- **Narration**: *"The system records immutable provenance: chain network (EVM, Bitcoin, Tron), ingestion timestamp, and upstream intake source (`NCRP_PORTAL` or `MANUAL_INTAKE`)."*

### Step 3: Current Indexed Blockchain Activity
- **Action**: Show live ingestion status and indexed block height.
- **Narration**: *"CryptoTrace LEA operates over continuously indexed transactions. Ingestion uses an 8-stage pipeline with reorg rollback protection and raw payload hashing."*

### Step 4: Bounded Trace Over Actual Transactions
- **Action**: Trigger bounded trace (`POST /api/v1/trace`) on target wallet with max hops = 4.
- **Narration**: *"The trace engine traverses transactions deterministically up to depth limits. It avoids unbounded graph explosion and records transfer hashes for every edge."*

### Step 5: Identification of Suspicious Intermediaries
- **Action**: Inspect graph path and hop timeline.
- **Narration**: *"The system highlights rapid hops occurring within minutes of each other, calculating transfer velocity and retention time across hops."*

### Step 6: Typology Evidence Tied to Transaction Hashes
- **Action**: Open the `Mule Network` alert banner in `dashboard.html`.
- **Narration**: *"Notice the `sih-mule-banner`. The alert links directly to transaction hashes `0x...` on-chain. Below the finding is our mandatory uncertainty note, ensuring officers understand the evidentiary boundaries before filing charges."*

### Step 7: VASP Candidate & 6-Step Scoring Trace
- **Action**: Expand `sih-adaptive-card` on the dashboard.
- **Narration**: *"Here is our `AdaptiveVASPScorer`. Rather than an opaque black box, it presents an interactive 6-step breakdown: Hot Wallet Match, Deposit Pattern, Sweeper Cluster, Volume Consistency, Indian KYC Entity Status, and Timing Alignment. Each step shows its raw evidence and normalized weight."*

### Step 8: Proven vs Heuristic Cross-Chain Status
- **Action**: Inspect cross-chain hop link.
- **Narration**: *"If a bridge event is detected on-chain, it is flagged as `PROVEN`. If funds merely moved around the same time across chains, it is explicitly classified as `HEURISTIC_CORRELATION`. We never claim proof without bridge contract logs."*

### Step 9: Separate Risk and Attribution
- **Action**: Point out Risk Score vs VASP Attribution Confidence.
- **Narration**: *"Risk score measures illicit pattern severity; attribution confidence measures entity certainty. A high-risk wallet may have low attribution confidence. CryptoTrace LEA keeps these metrics strictly decoupled."*

### Step 10: Recovery Estimate & Boundary Conditions
- **Action**: Inspect `sih-recovery-card`.
- **Narration**: *"Our recovery estimator checks PRD FR-016 boundary conditions: trace depth $\ge 1$, valid VASP candidate (`WazirX` / `CoinDCX`), and threshold $> \$120$. Only when all criteria are satisfied does the probability gauge render, alongside an active 72-hour countdown window."*

### Step 11: Evidence-Linked Recommendation
- **Action**: View automated investigative next-step recommendation.
- **Narration**: *"The system recommends issuing an immediate Section 91 CrPC Preservation Notice to the identified Indian exchange, citing specific transaction hashes."*

### Step 12: Evidence Manifest & Raw Payload Hash Verification
- **Action**: Open Evidence Manifest and click **Verify Hash Integrity**.
- **Narration**: *"Every raw JSON payload from the blockchain provider is stored deterministically with sorted keys. Its SHA-256 hash forms a Section 65B-admissible evidence manifest."*

### Step 13: Preservation Request Draft (Section 91 Notice)
- **Action**: Click **Draft Section 91 Notice** in the Supervisor Deck.
- **Narration**: *"An official notice is generated in state `DRAFT`, complete with suspect wallet, transaction IDs, frozen target amount, and legal citations."*

### Step 14: Supervisor Approval State Transition
- **Action**: Log in as Supervisor and click **Approve Notice**.
- **Narration**: *"Investigators cannot issue binding notices unilaterally. The notice transitions from `DRAFT` $\to$ `PENDING_APPROVAL` $\to$ `APPROVED`. Every transition is signed and appended to the cryptographic audit chain."*

### Step 15: Cryptographic Audit Verification & Limitation Disclosure
- **Action**: Click **Verify Audit Chain** to view the block-linked chain verification modal.
- **Narration**: *"We verify the entire audit log cryptographically from the genesis root. We conclude by disclosing operational limitations: unindexed blocks, private key privacy, and off-chain P2P cash settlements that require ground policing."*

---

## 4. Summary & Judge Takeaways

1. **Live-Data Only**: No simulated responses claimed as operational.
2. **Explainable AI/Heuristics**: Every score discloses its mathematical calculation and evidence hashes.
3. **Court-Admissible**: Tamper-evident audit chain, Section 65B manifest, and multi-tier approval workflow.
