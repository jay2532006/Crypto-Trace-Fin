"""
Move merged source files to docs/archive/raw_sources/
Ensures zero data loss while making root and docs/ clean and professional.
"""
import os
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_RAW = os.path.join(ROOT_DIR, "docs", "archive", "raw_sources")
os.makedirs(ARCHIVE_RAW, exist_ok=True)

root_files_to_archive = [
    "ADAPTATION_STRATEGY.md",
    "AUDIT.md",
    "CryptoTrace LEA — Live Data, Caching & Resilience Plan.md",
    "CRYPTOTRACE_LEA_IMPLEMENTATION_PLAN (1).md",
    "CRYPTOTRACE_LEA_PHASEWISE_IMPLEMENTATION_PLAN.md",
    "CRYPTOTRACE_LEA_PRD (1).md",
    "Frontend Requirements.md",
    "gap_analysis.md",
    "IMPLEMENTATION_CHECKLIST.md",
    "L1-Logs.md",
    "logic-core.md",
    "LOGIC_IMPLEMENTATION_PLAN (1).md",
    "LOGS.md",
    "MASTER_README.md",
    "PRODUCT_BRIEF.md",
    "SYSTEM_DATA_FLOW.md",
    "SYSTEM_SPECIFICATION.md",
    "TRACEX_SAHYOG_WIN_PLAN.md",
]

# Move LLM_CONTEXT.md directly to docs/archive/
llm_context_path = os.path.join(ROOT_DIR, "LLM_CONTEXT.md")
if os.path.exists(llm_context_path):
    dest = os.path.join(ROOT_DIR, "docs", "archive", "LLM_CONTEXT.md")
    shutil.move(llm_context_path, dest)
    print("Moved LLM_CONTEXT.md -> docs/archive/LLM_CONTEXT.md")

for fname in root_files_to_archive:
    src = os.path.join(ROOT_DIR, fname)
    if os.path.exists(src):
        dst = os.path.join(ARCHIVE_RAW, fname)
        shutil.move(src, dst)
        print(f"Moved {fname} -> docs/archive/raw_sources/{fname}")

# Move merged constituent docs from docs/ to docs/archive/raw_sources/
docs_files_to_archive = [
    "ARCHITECTURE.md",
    "BASELINE.md",
    "CHANGELOG.md",
    "LIMITATIONS.md",
    "REQUIREMENT_CONFLICTS.md",
    "VERIFICATION_REPORT.md",
]

for fname in docs_files_to_archive:
    src = os.path.join(ROOT_DIR, "docs", fname)
    if os.path.exists(src):
        dst = os.path.join(ARCHIVE_RAW, fname)
        shutil.move(src, dst)
        print(f"Moved docs/{fname} -> docs/archive/raw_sources/{fname}")

print("\nArchiving completed successfully!")
