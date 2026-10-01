# CryptoTrace LEA — Limitations & Boundary Conditions

## 1. Probabilistic vs Cryptographic Boundaries
- **Attribution vs Ownership**: CryptoTrace LEA identifies candidate Virtual Asset Service Providers (VASPs) through transaction clustering, deposit sweep patterns, and proximity heuristics. **Attribution does not constitute legal proof of beneficial ownership**; ownership can only be established through lawful KYC disclosure obtained via Section 91 BNSS 2023 directives served to the VASP nodal officer.
- **Unhosted Mule Wallets**: While the `MULE_NETWORK` rule identifies single-in/single-out rapid forwarding rings characteristic of organized mule syndicates, **confidence is strictly capped at MEDIUM**. Intermediate wallets are unhosted (self-custodial), and their controllers cannot be conclusively identified without off-chain banking or telecommunication evidence.

---

## 2. Privacy Mixers & Anonymity Enhancers
- **Mixer Boundary Heuristic**: Transits through Tornado Cash, Wasabi, or other coinjoin/mixer pools break deterministic transaction continuity. CryptoTrace LEA flags potential exits using temporal windows ($+14,400\text{s}$) and pool payout ratios ($0.90 - 0.995$), but labels these edges strictly as:
  $$\text{Possible Exit — Heuristic Only (Confidence: 0.25 / LEAD)}$$
- The system **never** claims confirmed attribution across a privacy pool.

---

## 3. Cross-Chain Bridges
- **Proven vs Heuristic Correlation**: Only cross-chain bridge events containing cryptographic validator attestations, mint/burn proofs, or verified contract event logs are classified as `PROVEN`.
- Time/value correlation across different blockchains without cryptographic proof is explicitly tagged as `HEURISTIC_CORRELATION` and carries mandatory uncertainty disclaimers.

---

## 4. Heuristic Recovery Estimate & PRD FR-016 Boundary Gating
- The recovery score (0-100) is an **operational prioritization metric** for law enforcement dispatch. It does **not** represent a statistical probability of fund return, nor does it guarantee asset seizure. Actual recovery depends entirely on judicial orders issued under Section 106 BNSS 2023 or Section 5 PMLA 2002.
- **Mandatory Boundary Gating (PRD FR-016)**:
  - **Zero-Hop Rejection**: Trace depth == 0 $\implies$ `ESTIMATE_NOT_APPLICABLE` (untracked funds cannot be prioritized).
  - **Attribution Gating**: Attribution == `LEAD` or `NONE` $\implies$ `ESTIMATE_NOT_APPLICABLE` (cannot calculate freeze probability without an identifiable custodial counterparty).
  - **Low-Value Threshold**: Defrauded amount $< \$120$ $\implies$ `LOW_VALUE_UNECONOMIC` (below actionable statutory recovery threshold).

---

## 5. Algorithmic Reproducibility & Baseline Invariants
- **Deterministic Branching**: In evaluation mode, DEMO cases follow realistic branching paths (`MIXER_HALT` for Tornado Cash pools and `SANCTION_HALT` for Lazarus OFAC addresses) rather than homogeneous paths.
- **Snapshot Integrity**: 10 immutable baseline snapshots in `backend/tests/fixtures/baselines/` enforce that all 9 canonical output keys remain byte-for-byte reproducible across releases.
- **Test Gate**: Verified via 129/129 passing pytest tests with 0 regressions.

