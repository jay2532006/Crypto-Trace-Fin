"""
CryptoTrace LEA - Documentation Consolidation Script
Merges all redundant and scattered markdown files into structured,
high-value master documents with ZERO loss of content.
"""
import os
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_file(rel_path):
    path = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(rel_path, content):
    path = os.path.join(ROOT_DIR, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {rel_path} ({len(content)} bytes, {len(content.splitlines())} lines)")

# ==============================================================================
# Cluster 1: docs/PRODUCT_SPECIFICATION.md
# ==============================================================================
def build_product_specification():
    sources = [
        ("PRODUCT_BRIEF.md", "Executive Product Brief & Capability Overview"),
        ("CRYPTOTRACE_LEA_PRD (1).md", "Product Requirements Document (PRD: FR-001 - FR-016)"),
        ("Frontend Requirements.md", "Frontend UI/UX Specification & Screen Catalog"),
        ("docs/LIMITATIONS.md", "System Limitations, Uncertainty & Boundary Conditions"),
    ]
    
    header = """# CryptoTrace LEA — Unified Product & Functional Specification
**Smart India Hackathon SIH 26183 | Ministry of Home Affairs (MHA) / I4C CIS Division**  
**Version:** 2.1.0-SIH26183  
**Status:** 100% IMPLEMENTED & VERIFIED (129/129 Tests Passing, 10 Immutable Golden Baselines)  

---

## Master Document Navigation
This master document consolidates all product requirements, functional definitions, user experience requirements, and statutory boundary conditions into a single authoritative reference with zero content loss.

- [Part 1: Executive Product Brief & Capability Overview](#part-1-executive-product-brief--capability-overview) (Source: `PRODUCT_BRIEF.md`)
- [Part 2: Product Requirements Document (PRD: FR-001 - FR-016)](#part-2-product-requirements-document-prd-fr-001---fr-016) (Source: `CRYPTOTRACE_LEA_PRD (1).md`)
- [Part 3: Frontend UI/UX Specification & Screen Catalog](#part-3-frontend-uiux-specification--screen-catalog) (Source: `Frontend Requirements.md`)
- [Part 4: System Limitations, Uncertainty & Boundary Conditions](#part-4-system-limitations-uncertainty--boundary-conditions) (Source: `docs/LIMITATIONS.md`)

---
"""
    body = []
    for idx, (rel_path, title) in enumerate(sources, 1):
        content = read_file(rel_path)
        section = f"""
# Part {idx}: {title}
> **Original Source Document:** `{rel_path}`  
> **Lines Preserved:** {len(content.splitlines())}  

---

{content}

---
"""
        body.append(section)
    
    write_file("docs/PRODUCT_SPECIFICATION.md", header + "\n".join(body))

# ==============================================================================
# Cluster 2: docs/ARCHITECTURE_AND_CORE_LOGIC.md
# ==============================================================================
def build_architecture_and_core_logic():
    sources = [
        ("docs/ARCHITECTURE.md", "System Architecture & Evidence-First Philosophy"),
        ("SYSTEM_DATA_FLOW.md", "End-to-End System & Live Data Flow"),
        ("logic-core.md", "12 Core Forensic Algorithms Exhaustive Code Specification"),
        ("SYSTEM_SPECIFICATION.md", "Exhaustive Codebase Extraction & Technical Specification"),
    ]
    
    header = """# CryptoTrace LEA — Architecture, Data Flow & Core Forensic Logic
**Smart India Hackathon SIH 26183 | Technical Architecture & Algorithmic Blueprint**  
**Version:** 2.1.0-SIH26183  
**Status:** 100% IMPLEMENTED & VERIFIED (129/129 Tests Passing, 10 Immutable Golden Baselines)  

---

## Master Document Navigation
This master document consolidates the complete system architecture, data flow lifecycles, and code-level breakdowns of all 12 core forensic algorithms into a single authoritative technical reference with zero content loss.

- [Part 1: System Architecture & Evidence-First Philosophy](#part-1-system-architecture--evidence-first-philosophy) (Source: `docs/ARCHITECTURE.md`)
- [Part 2: End-to-End System & Live Data Flow](#part-2-end-to-end-system--live-data-flow) (Source: `SYSTEM_DATA_FLOW.md`)
- [Part 3: 12 Core Forensic Algorithms Exhaustive Code Specification](#part-3-12-core-forensic-algorithms-exhaustive-code-specification) (Source: `logic-core.md`)
- [Part 4: Exhaustive Codebase Extraction & Technical Specification](#part-4-exhaustive-codebase-extraction--technical-specification) (Source: `SYSTEM_SPECIFICATION.md`)

---
"""
    body = []
    for idx, (rel_path, title) in enumerate(sources, 1):
        content = read_file(rel_path)
        section = f"""
# Part {idx}: {title}
> **Original Source Document:** `{rel_path}`  
> **Lines Preserved:** {len(content.splitlines())}  

---

{content}

---
"""
        body.append(section)
    
    write_file("docs/ARCHITECTURE_AND_CORE_LOGIC.md", header + "\n".join(body))

# ==============================================================================
# Cluster 3: docs/MASTER_IMPLEMENTATION_PLAN.md
# ==============================================================================
def build_master_implementation_plan():
    sources = [
        ("LOGIC_IMPLEMENTATION_PLAN (1).md", "Definitive Logic Implementation Plan (Phases 0–5 + Post-Audit Complete)"),
        ("CRYPTOTRACE_LEA_IMPLEMENTATION_PLAN (1).md", "Master Phased Implementation Plan & Governance Rules"),
        ("CRYPTOTRACE_LEA_PHASEWISE_IMPLEMENTATION_PLAN.md", "Phasewise Implementation & Adaptation Plan"),
        ("IMPLEMENTATION_CHECKLIST.md", "Task-Level Implementation Checklist"),
        ("TRACEX_SAHYOG_WIN_PLAN.md", "Win Plan & Defect Closure Roadmap"),
        ("ADAPTATION_STRATEGY.md", "TraceX to CryptoTrace LEA Architectural Adaptation Strategy"),
        ("CryptoTrace LEA — Live Data, Caching & Resilience Plan.md", "Live Data, Caching & System Resilience Plan"),
    ]
    
    header = """# CryptoTrace LEA — Master Phased Implementation Plan & Roadmaps
**Smart India Hackathon SIH 26183 | Complete Engineering & Adaptation Roadmap**  
**Version:** 2.1.0-SIH26183  
**Status:** 100% COMPLETED & VERIFIED (All 35 Logic Tasks Done · 129/129 Tests Green)  

---

## Master Document Navigation
This master document consolidates all historical, architectural, and definitive implementation plans into a single comprehensive repository reference with zero content loss.

- [Part 1: Definitive Logic Implementation Plan (Phases 0–5 + Post-Audit Complete)](#part-1-definitive-logic-implementation-plan-phases-05--post-audit-complete) (Source: `LOGIC_IMPLEMENTATION_PLAN (1).md`)
- [Part 2: Master Phased Implementation Plan & Governance Rules](#part-2-master-phased-implementation-plan--governance-rules) (Source: `CRYPTOTRACE_LEA_IMPLEMENTATION_PLAN (1).md`)
- [Part 3: Phasewise Implementation & Adaptation Plan](#part-3-phasewise-implementation--adaptation-plan) (Source: `CRYPTOTRACE_LEA_PHASEWISE_IMPLEMENTATION_PLAN.md`)
- [Part 4: Task-Level Implementation Checklist](#part-4-task-level-implementation-checklist) (Source: `IMPLEMENTATION_CHECKLIST.md`)
- [Part 5: Win Plan & Defect Closure Roadmap](#part-5-win-plan--defect-closure-roadmap) (Source: `TRACEX_SAHYOG_WIN_PLAN.md`)
- [Part 6: TraceX to CryptoTrace LEA Architectural Adaptation Strategy](#part-6-tracex-to-cryptotrace-lea-architectural-adaptation-strategy) (Source: `ADAPTATION_STRATEGY.md`)
- [Part 7: Live Data, Caching & System Resilience Plan](#part-7-live-data-caching--system-resilience-plan) (Source: `CryptoTrace LEA — Live Data, Caching & Resilience Plan.md`)

---
"""
    body = []
    for idx, (rel_path, title) in enumerate(sources, 1):
        content = read_file(rel_path)
        section = f"""
# Part {idx}: {title}
> **Original Source Document:** `{rel_path}`  
> **Lines Preserved:** {len(content.splitlines())}  

---

{content}

---
"""
        body.append(section)
    
    write_file("docs/MASTER_IMPLEMENTATION_PLAN.md", header + "\n".join(body))

# ==============================================================================
# Cluster 4: docs/AUDIT_AND_GAP_ANALYSIS.md
# ==============================================================================
def build_audit_and_gap_analysis():
    sources = [
        ("AUDIT.md", "Complete System Audit & Post-Audit Implementation Verification"),
        ("gap_analysis.md", "Exhaustive 30-Finding Gap Analysis & Resolution Map"),
        ("docs/REQUIREMENT_CONFLICTS.md", "Requirement Discrepancy & Conflict Register"),
    ]
    
    header = """# CryptoTrace LEA — System Audit, Gap Analysis & Resolution Register
**Smart India Hackathon SIH 26183 | Complete Forensic & Codebase Audit Ledger**  
**Version:** 2.1.0-SIH26183  
**Status:** 100% RESOLVED & VERIFIED (30/30 Gaps Closed · 129/129 Tests Passing)  

---

## Master Document Navigation
This master document consolidates all historical audits, identified architectural/logical gaps, requirement discrepancies, and verified resolution proofs with zero content loss.

- [Part 1: Complete System Audit & Post-Audit Implementation Verification](#part-1-complete-system-audit--post-audit-implementation-verification) (Source: `AUDIT.md`)
- [Part 2: Exhaustive 30-Finding Gap Analysis & Resolution Map](#part-2-exhaustive-30-finding-gap-analysis--resolution-map) (Source: `gap_analysis.md`)
- [Part 3: Requirement Discrepancy & Conflict Register](#part-3-requirement-discrepancy--conflict-register) (Source: `docs/REQUIREMENT_CONFLICTS.md`)

---
"""
    body = []
    for idx, (rel_path, title) in enumerate(sources, 1):
        content = read_file(rel_path)
        section = f"""
# Part {idx}: {title}
> **Original Source Document:** `{rel_path}`  
> **Lines Preserved:** {len(content.splitlines())}  

---

{content}

---
"""
        body.append(section)
    
    write_file("docs/AUDIT_AND_GAP_ANALYSIS.md", header + "\n".join(body))

# ==============================================================================
# Cluster 5: docs/VERIFICATION_AND_EXECUTION_LOGS.md
# ==============================================================================
def build_verification_and_execution_logs():
    sources = [
        ("L1-Logs.md", "Master Phase 0–5 Implementation & Verification Log"),
        ("docs/VERIFICATION_REPORT.md", "System Verification Report & Test Telemetry (129/129 Green)"),
        ("docs/BASELINE.md", "Technical Baseline Comparison & 10 Immutable Golden Snapshots"),
        ("LOGS.md", "Historical Change Log & Code Mutation Ledger"),
        ("docs/CHANGELOG.md", "Formal Project Changelog (v2.0 & v2.1.0-SIH26183)"),
    ]
    
    header = """# CryptoTrace LEA — Verification Telemetry, Baselines & Execution Logs
**Smart India Hackathon SIH 26183 | Complete Verification & Evidence Dossier**  
**Version:** 2.1.0-SIH26183  
**Status:** 129/129 Pytest Tests Passing (100% Green, 0 Regressions) | 10 Immutable Golden Baselines  

---

## Master Document Navigation
This master document consolidates all implementation logs, verification reports, test telemetry, immutable baseline snapshots, and release changelogs with zero content loss.

- [Part 1: Master Phase 0–5 Implementation & Verification Log](#part-1-master-phase-05-implementation--verification-log) (Source: `L1-Logs.md`)
- [Part 2: System Verification Report & Test Telemetry (129/129 Green)](#part-2-system-verification-report--test-telemetry-129129-green) (Source: `docs/VERIFICATION_REPORT.md`)
- [Part 3: Technical Baseline Comparison & 10 Immutable Golden Snapshots](#part-3-technical-baseline-comparison--10-immutable-golden-snapshots) (Source: `docs/BASELINE.md`)
- [Part 4: Historical Change Log & Code Mutation Ledger](#part-4-historical-change-log--code-mutation-ledger) (Source: `LOGS.md`)
- [Part 5: Formal Project Changelog (v2.0 & v2.1.0-SIH26183)](#part-5-formal-project-changelog-v20--v210-sih26183) (Source: `docs/CHANGELOG.md`)

---
"""
    body = []
    for idx, (rel_path, title) in enumerate(sources, 1):
        content = read_file(rel_path)
        section = f"""
# Part {idx}: {title}
> **Original Source Document:** `{rel_path}`  
> **Lines Preserved:** {len(content.splitlines())}  

---

{content}

---
"""
        body.append(section)
    
    write_file("docs/VERIFICATION_AND_EXECUTION_LOGS.md", header + "\n".join(body))

# ==============================================================================
# Update Root README.md from MASTER_README.md
# ==============================================================================
def build_root_readme():
    content = read_file("MASTER_README.md")
    
    # Prepend a clean Documentation Directory index
    doc_index = """## 📚 Master Documentation Directory

All system documentation has been organized into comprehensive, unified master documents under the `docs/` directory with zero loss of technical content:

| Master Document | Purpose & Content | Source Documents Preserved |
| :--- | :--- | :--- |
| [`docs/PRODUCT_SPECIFICATION.md`](file:///d:/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/docs/PRODUCT_SPECIFICATION.md) | **Product Requirements & UI/UX** | PRD (FR-001–FR-016), Product Brief, 18 Frontend Screens, UI Tokens, and Operational Boundaries |
| [`docs/ARCHITECTURE_AND_CORE_LOGIC.md`](file:///d:/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/docs/ARCHITECTURE_AND_CORE_LOGIC.md) | **Architecture & 12 Core Algorithms** | System Architecture, Data Flow Lifecycle, Code-level breakdown of all 12 algorithms, Database schemas |
| [`docs/MASTER_IMPLEMENTATION_PLAN.md`](file:///d:/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/docs/MASTER_IMPLEMENTATION_PLAN.md) | **Implementation Roadmap & Checklists** | Phased Execution (Phases 0–5 + Post-Audit Complete, 35/35 tasks), Win Plan, Adaptation Strategy, Resilience |
| [`docs/AUDIT_AND_GAP_ANALYSIS.md`](file:///d:/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/docs/AUDIT_AND_GAP_ANALYSIS.md) | **System Audit & Gap Closures** | Complete Pre/Post Audit, 30 Gap Analysis Findings & Resolutions, Governing Conflict Register |
| [`docs/VERIFICATION_AND_EXECUTION_LOGS.md`](file:///d:/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/docs/VERIFICATION_AND_EXECUTION_LOGS.md) | **Telemetry, Baselines & Execution Logs** | 129/129 Test Telemetry, 10 Golden Baselines, Phase 0–5 Execution Logs, Mutation Ledgers, Changelog |
| [`docs/DEMO_SCRIPT.md`](file:///d:/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/docs/DEMO_SCRIPT.md) | **Evaluation Walkthrough** | 15-Step Live Evaluation Script & 10 Dedicated Demonstration Benchmark Scenarios |
| [`docs/SECURITY.md`](file:///d:/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/docs/SECURITY.md) | **Security & Governance** | Canonical 4-Role RBAC Matrix, Disabled Legacy Endpoints, BIP-39 Credential Quarantine |
| [`SETUP_GUIDE.md`](file:///d:/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/SETUP_GUIDE.md) | **Quick Start Guide** | Environment variables, backend/frontend setup, preset accounts, and test execution |

---
"""
    # Insert doc_index right after section 1 of MASTER_README
    parts = content.split("## 2. Completed 8-Phase Win Plan Implementation")
    new_readme = parts[0] + doc_index + "\n## 2. Completed 8-Phase Win Plan Implementation" + parts[1]
    write_file("README.md", new_readme)

if __name__ == "__main__":
    print("Beginning documentation consolidation...")
    build_product_specification()
    build_architecture_and_core_logic()
    build_master_implementation_plan()
    build_audit_and_gap_analysis()
    build_verification_and_execution_logs()
    build_root_readme()
    print("Consolidation files successfully created!")
