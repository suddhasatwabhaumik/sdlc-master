---
name: sdlc-master-orchestrator
description: >-
  Master "Skill of Skills" orchestrator for the entire Software Development Lifecycle (SDLC)
  using the Elephant-Goldfish Model (EGM). The persistent Main Thread acts as the Elephant
  (Design, Strategy, Contract Locking, Disjoint File-Slice Partitioning, and Triage), while
  all implementation, conciseness refactoring, multi-viewpoint auditing, Pass-2 falsification,
  remediation, E2E testing, and release-note generation execute in parallel waves of stateless,
  zero-context Goldfish sub-agents (max 3-4 concurrent agents per wave).
---

# SDLC Master Orchestrator ("Skill of Skills" — Elephant & Parallel Goldfish Engine)

This meta-skill orchestrates all specialized engineering skills across the workspace using the **Elephant-Goldfish Model (EGM)** combined with **Disjoint Parallel Sub-Agent Sharding**:
- **The Elephant (Persistent Main Thread)**: Holds system history, stakeholder intent, and architectural trade-offs. It **never writes production code in a bloated design conversation**. Instead, it resolves design choices with the human (`Author Decides Architecture`), locks shared interfaces (`ports.py`, `models.py`, schemas), partitions work into **mutually exclusive file slices ($S_1 \cap S_2 \cap \dots \cap S_K = \emptyset$)**, and triages audit findings (`PROPOSE FIX | CONTEST | ESCALATE | DECLINE`).
- **Parallel Goldfish Waves (Zero-Context Sub-Agents — Max 3–4 per Wave)**: Spawned via `invoke_subagent` with **zero conversation history**. Use `TypeName: "research"` for strictly read-only scouts/auditors and `TypeName: "self"`, `Workspace: "inherit"` for disjoint mutating workers. Goldfish implementers receive *only* their self-contained Slice Contract and `GoldfishContext` file paths; Goldfish auditors evaluate the resulting disk diff without confirmation bias.

---

## 1. Registered Skill Registry & Memory Model Routing Map

| Skill Name | Memory Model | Role in Master Pipeline | Execution Mode |
| :--- | :--- | :--- | :--- |
| [`ai-assisted-software-engineering`](../ai-assisted-software-engineering/SKILL.md) | **Elephant** + **Parallel Goldfish Critics** | Phases 1–3 (Planning, Requirements, ADRs, 4-Goldfish Shootdown) & Phases 6–7 (CI/CD, 3-Goldfish Incident RCA) | Stage 0 (Main Thread + Wave 0) & Stage 6 (Goldfish 6C) |
| [`coding`](../coding/SKILL.md) | **Elephant** Partitioner $\rightarrow$ **Parallel Goldfish** Implementers | Phase 1–2 Contract & Slice Partitioning $\rightarrow$ Phase 3–5 Zero-Context Parallel Slice Implementation & 3-Try Test Loop | Stage 1 (Wave 1: 2–4 Parallel Goldfish Slice Workers) |
| [`python-design-patterns`](../python-design-patterns/SKILL.md) | **Elephant** Boundary Selector $\rightarrow$ **Parallel Goldfish** Builders | LLD Boundary Hygiene (Ports/Adapters, Catalog Bridge, Shared IR, `ContextVar`) guarded against over-engineering | Stage 0 Contract Design & Stage 2 Pre-Gate |
| [`code-review`](../code-review/SKILL.md) | **Parallel Goldfish** Auditors + **Pass-2 Falsifier** | Wave 1 (Paraphrase + Conciseness), Wave 2 (4 Core/Sec Goldfish), Wave 3 (3 Test/Style/Domain Goldfish), Pass-2 Disproof | Stages 2, 3, and 4 (Parallel Goldfish Waves) |
| [`google-style-guide`](../google-style-guide/SKILL.md) | **Parallel Goldfish** Style/Typing Shards | Google Python Style Guide compliance (types, docstrings, naming, imports, `DROP \| CALIBRATE \| RELOCATE \| KEEP` prose calibration, respecting repo config) | Stage 1 (Goldfish Implementers) & Stage 4 (Goldfish 4B) |
| [`python-readability`](../python-readability/SKILL.md) | **Elephant** Packaging/Scope Gate + **Parallel Goldfish** Readability Shards | Python readability, code-density (*"optimize for readability, not conciseness"*), `pyproject.toml`/venv reproducibility, hermetic tests, `required`/`optional` §-citations, & §10 Review Guardrails | Stages 0, 1, 2 (2A Guardrail), 4 (4A/4B/4D), & 5 |
| *(Optional companion plugin)* `mandatory-secure-web-skills` / `run-security-scanner` / `scan_dependencies` | **Goldfish** Security Auditor | Enhanced CWE & dependency scanning when installed (automatically falls back to `code-review` Goldfish `2D` otherwise) | Stage 3 (Goldfish 3D) |
| [`pr-feature-branch-review`](../pr-feature-branch-review/SKILL.md) | **Elephant** Triage $\rightarrow$ **Parallel Goldfish** Remediators | Safe branch sync, 4-Goldfish parallel remediation (Prod, Unit Tests, E2E Bash `tests/e2e_*`, Docs), GitHub PR response | Mode C Entry & Stage 5 Parallel Remediation Wave |
| [`release-notes`](../release-notes/SKILL.md) | **Parallel Goldfish** Scouts $\rightarrow$ **Goldfish** Compiler | Automated `<repo_root>/releases/vX.Y.Z_<slug>.md` authoring grounded in live code and test metrics | Stage 6 (Goldfish 6A) |
| [`code-mentor`](../code-mentor/SKILL.md) | **Elephant** Socratic Coach + **Parallel Goldfish** Scouts | Pre-design architecture stress-testing & Stage 7 pre-commit comprehension quiz ("Explain My Changes") | Mode F & Stage 7 Pre-Commit Gate |

---

## 2. Dynamic Entry Router (Determine Starting Stage)

Inspect the user's prompt and workspace state to enter the pipeline at the right stage:

1. **Mode A — Greenfield / Spec / Architecture Request**:
   - Run **Stage 0** (Elephant Spec + Wave 0 Parallel Goldfish Shootdown) $\rightarrow$ Pause for HITL approval $\rightarrow$ Proceed to **Stages 1–7**.
2. **Mode B — Feature Implementation / Bug Fix / Refactoring**:
   - Run **Stage 0** (Fast Contract & Disjoint Slice Partitioning) $\rightarrow$ Enter **Stage 1** (Wave 1 Parallel Goldfish Implementers) $\rightarrow$ Proceed through **Stages 2–7**. *(Micro-Patch Exception: Single-file edits `<= 15` lines with zero architectural choices may execute via a single fast Goldfish pass. Graduating Python code from `experimental/`, `prototypes/`, or `scratch/` into production paths triggers full-file [`python-readability`](../python-readability/SKILL.md) inspection).*
3. **Mode C — PR or Feature Branch Review & Remediation**:
   - Run [`pr-feature-branch-review`](../pr-feature-branch-review/SKILL.md) Phase 1 (Safe Branch Sync & Adaptive Depth Classification) $\rightarrow$ Proceed through **Stages 2–7**.
4. **Mode D — Production Incident / RCA**:
   - Run [`ai-assisted-software-engineering`](../ai-assisted-software-engineering/SKILL.md) Phase 7 (3 Parallel Goldfish RCA Scouts: Logs/Traces, Git Blame, Config Drift) $\rightarrow$ Lock failing reproduction test $\rightarrow$ Hand off to **Stages 1–7**.
5. **Mode E — Spec-to-Code Drift Audit**:
   - Spawn parallel read-only Goldfish Drift Auditors (`TypeName: "research"`) comparing `docs/designs/*.md` and `README.md` contracts against live source files to emit `{YYYY-MM-DD}_DRIFT_REPORT.md`.
6. **Mode F — Socratic Mentorship / Pre-Commit Comprehension ("Explain My Changes")**:
   - Invoke [`code-mentor`](../code-mentor/SKILL.md) directly in Elephant Socratic Mode.

---

## 3. Master Execution Pipeline (Elephant Barriers & Parallel Goldfish Waves)

### Stage 0: Elephant Strategy, Parallel Shootdown & Disjoint Contract Locking
*Executed in the Main Thread (Elephant) with a 4-Goldfish Parallel Shootdown Wave.*

1. **Problem Framing & Contradiction Audit (Elephant)**:
   - Synthesize Goals, Non-Goals, FRs/NFRs (`Given/When/Then`), and candidate architecture ([`ai-assisted-software-engineering`](../ai-assisted-software-engineering/SKILL.md) Phases 1–3).
   - **Contradiction Halt Rule**: If the request contradicts existing system invariants, halt and ask the user in plain text without touching any files.
   - **Author Decides Architecture**: When $>1$ defensible design exists, present up to 3 unranked options with failure conditions for human selection.
2. **Wave 0: Parallel Goldfish Design Shootdown (4 Read-Only Goldfish — For Mode A or Complex Mode B)**:
   - Spawn **4 parallel zero-context Goldfish critics** (`TypeName: "research"`) to stress-test the proposed design:
     - **Goldfish 0A (Contrarian / YAGNI & Reuse)**: Searches repo for existing utilities solving the problem without new code.
     - **Goldfish 0B (Cost, Quota & Scale Economics)**: Audits QPS, memory, DB load, and token/API ceilings.
     - **Goldfish 0C (Security, Migration & Rollback Safety)**: Audits auth boundaries, schema compatibility, and rollback safety.
     - **Goldfish 0D (TRIZ Inventive Catalyst)**: Identifies false compromises and suggests software transforms with secondary trade-offs.
3. **Lock Shared Interfaces & Partition Disjoint Implementation Slices ($S_i \cap S_j = \emptyset$)**:
   - Write/lock shared interface contracts (`ports.py`, `models.py`, proto/OpenAPI schemas) first.
   - For Python repositories, inspect `pyproject.toml` (or `setup.cfg` / `requirements*.txt`) to lock Python version constraints, declared dependencies, linter/type-checker settings (`ruff`, `mypy`, `pyright`, `pytest`), and reproducible venv runners (`uv run`, `poetry run`, `.venv/bin/python`) in each slice's `VerificationCommand`, and flag any files graduated from `experimental/`/`prototypes/`/`scratch/` for full-file readability review ([`python-readability`](../python-readability/SKILL.md) §1, §3).
   - Partition the implementation into **$K$ Disjoint Goldfish Work Packets (`Slice 1..K`, max 3–4 concurrent per wave)** where every slice $k$ has a strictly mutually exclusive `Target Scope & File Boundary` allowlist $S_k$ ($S_i \cap S_j = \emptyset$ for $i \neq j$), explicit `GoldfishContext` reading paths, and exact `VerificationCommand`.

---

### Stage 1: Wave 1 — Parallel Zero-Context Goldfish Implementation Swarm
*Never implement multi-file features inside the Elephant's conversation context. Dispatch parallel Goldfish slice workers.*

Spawn **2–4 parallel Goldfish Implementer Sub-Agents** (`invoke_subagent`, `TypeName: "self"`, `Workspace: "inherit"`) following [`coding/SKILL.md` (Goldfish Worker Mode)](../coding/SKILL.md), passing **only** each worker's Slice Contract and `GoldfishContext`:

| Concurrent Goldfish Worker | Assigned Slice Boundary ($S_k$) | Exclusive Mandate |
| :--- | :--- | :--- |
| **Goldfish Implementer 1A** | $S_1$: Core Domain / Business Logic | Implement core logic and domain invariants strictly within $S_1$ (Python: [`python-readability`](../python-readability/SKILL.md) & [`google-style-guide`](../google-style-guide/SKILL.md) — `<= ~40`-line functions, `80`-char or repo-configured line limit, `collections.abc` & `X \| None` typing, immutable constants, no nested defs in `src`). |
| **Goldfish Implementer 1B** | $S_2$: Concrete & In-Memory Adapters | Implement infrastructure/SDK adapters and ACL error translation within $S_2$ (using [`python-design-patterns`](../python-design-patterns/SKILL.md) and [`python-readability`](../python-readability/SKILL.md) single-line module imports & `%s`/`%r` lazy logging). |
| **Goldfish Implementer 1C** | $S_3$: API Routes / CLI / Config Wiring | Implement entrypoints, DI wiring, and typed runtime env configuration within $S_3$ (Python CLI: separate library logic from thin `main() < ~15` lines with structured `argparse`/`click`/`typer` parsing). |
| **Goldfish Implementer 1D** | $S_4$: Unit, Negative & Contract Tests | Author black-box unit, adversarial (`401`/`403`/`422`/`429`/timeout), and contract tests within $S_4$ against the locked interface contract (Python: [`python-readability`](../python-readability/SKILL.md) §9 — 1 behavior/test, `@pytest.mark.parametrize`, `autospec=True`/`create_autospec`, `caplog`/`assertLogs`, `tmp_path`). Run static lint/type checks per slice; defer runtime `pytest` to the Synchronization Barrier below. |

**Stage 1 Synchronization & Integration Barrier (Elephant)**:
- If any Goldfish returns `BLOCKED_ON_SPEC_CONTRADICTION` (because the contract left an unstated design choice), the Elephant resolves the gap in the contract and re-runs that slice.
- Once all parallel Goldfish implementers return completion receipts, run a combined integration test and linter pass across $S_1 \cup \dots \cup S_K$.

---

### Stage 2: Wave 2 — Parallel Conciseness & Naive Comprehension Pre-Gate (2 Goldfish)

> **CRITICAL STOP RULE (Conciseness-First Pre-Gate Rule)**: Always complete Stage 2 *before* launching Stage 3 or Stage 4. Never run deep security, style, or architectural audits on un-simplified code.

Spawn **2 parallel Goldfish sub-agents** from [`code-review/references/goldfish_viewpoint_personas.md`](../code-review/references/goldfish_viewpoint_personas.md):
1. **Goldfish 2A (`goldfish-wave1-conciseness`)**: Strip verbose AI boilerplate, dead branches, and unnecessary wrappers across the diff; apply simplifications (`TypeName: "self"`, `Workspace: "inherit"`) and re-run fast tests. **Python Anti-Code-Golf Guardrail ([`python-readability`](../python-readability/SKILL.md) §2)**: *"Optimize for readability, not conciseness"* — eliminate boilerplate (direct returns, implicit truthiness, `d.get()`, `@override` without redundant docstrings, public attributes over trivial getters/setters) without introducing multi-`for` comprehensions, nested/multi-line ternaries, magic tuple indexing, or abbreviated names.
2. **Goldfish 2B (`goldfish-wave1-comprehension`, `TypeName: "research"`)**: Produce a **2–4 sentence Naive Behavioral Paraphrase** (*What this diff changes* and *What callers assume*). The Elephant compares this paraphrase against Stage 0 Goals; any mismatch is treated as a `[Blocker]`.

---

### Stage 3: Wave 3 — Core System, Config, Dependencies & Security Audit (4 Parallel Goldfish)

Spawn **4 parallel read-only Goldfish sub-agents** (`TypeName: "research"`) against the Stage 2 refactored diff (see [`code-review/references/goldfish_viewpoint_personas.md`](../code-review/references/goldfish_viewpoint_personas.md)):

| Concurrent Agent | Goldfish Persona | Exact Audit Mandate |
| :--- | :--- | :--- |
| **Goldfish 3A** | `goldfish-2a-architecture-zoom-out-triz` | Detect architectural flaws, tight coupling, double concurrency lock acquisition, codebase wheel-reinvention, and TRIZ false compromises. |
| **Goldfish 3B** | `goldfish-2b-runtime-config` | Detect magic strings, hardcoded URLs, project IDs, ports, model names, or timeouts that must come from runtime environment config. |
| **Goldfish 3C** | `goldfish-2c-dependency-hygiene` | Detect code compensating for a missing dependency or reinventing `{{DOMAIN_STACK}}` primitives; verify dev packages aren't in runtime manifests. |
| **Goldfish 3D** | `goldfish-2d-security-trust` + Security Scanner | Audit cryptographic JWT/auth verification, zero `mock-token-*` backdoors, RBAC on admin routes, tenant isolation, and injection/CWE risks. |

*Wait for all 4 Goldfish in Wave 3 (retrying any timed-out agent once and tracking `completed | not run`) before launching Wave 4.*

---

### Stage 4: Wave 4 — Test Honesty, Style Guide & Domain Idioms + Pass-2 Falsification (4 Goldfish)

Spawn **3 parallel read-only Goldfish auditors** (`TypeName: "research"`) followed by the **Pass-2 Falsifier** (`TypeName: "research"`):

| Concurrent Agent | Goldfish Persona | Exact Audit Mandate |
| :--- | :--- | :--- |
| **Goldfish 4A** | `goldfish-3a-test-realism` | Detect test cases mocking out runtime scenarios (nulls, timeouts, 429s, network errors) not handled in production code, or E2E silent mock fallbacks; for Python tests, enforce [`python-readability`](../python-readability/SKILL.md) §9 (`autospec=True`/`create_autospec`, `caplog`/`assertLogs`, `tmp_path`, `@pytest.mark.parametrize`, 1 behavior per test). |
| **Goldfish 4B** | `goldfish-3b-standards-and-style` | Audit [`google-style-guide`](../google-style-guide/SKILL.md) & [`python-readability`](../python-readability/SKILL.md) rules (code density, `pyproject.toml` dependency hygiene, imports, `X \| None` & `collections.abc` typing, `<= 80`-char or repo-configured docstrings with `None` semantics, thin `main()`, lazy `%` logging, `required`/`optional` §-citations), OTel metric caching (when instrumented), and `DROP \| CALIBRATE \| RELOCATE \| KEEP` prose calibration. |
| **Goldfish 4C** | `goldfish-3c-domain-idioms` | Verify strict adherence to official `{{DOMAIN_STACK}}` conventions and lifecycle hooks. |
| **Goldfish 4D (Pass 2)** | `goldfish-synthesizer-and-disproof` | Actively **DISPROVE** candidate findings from Waves 3–4 against diff hunks, the Anti-Over-Engineering Ledger, and [`python-readability` §10 Review Guardrails](../python-readability/SKILL.md) (e.g., inline test/script regexes, `spec_set=True` with `autospec=True`, nested `for` loops, `typing.Final`, helper ordering), writing surviving findings (`required` vs `optional`) to `goldfish_review_report.md`. |

---

### Stage 5: Elephant Resolution Triage $\rightarrow$ Wave 5 Parallel Goldfish Remediation

1. **Elephant Resolution Triage (Main Thread)**:
   - Categorize every surviving finding in `goldfish_review_report.md` (and any human PR comments) into:
     - **`PROPOSE FIX`**: Valid defect; assign to a disjoint remediation slice.
     - **`CONTEST`**: Invalid critique; must cite checkable `[file:symbol]` evidence.
     - **`ESCALATE`**: Requires human decision; pause and ask the user if any `ESCALATE` item exists.
     - **`DECLINE`**: Non-blocking Nit.
2. **Wave 5: Parallel Disjoint Goldfish Remediation Swarm (Up to 3 Concurrent Mutators)**:
   - Partition approved `PROPOSE FIX` items into non-overlapping file sets ($R_A \cap R_B \cap R_C = \emptyset$) and spawn parallel Goldfish workers (`TypeName: "self"`, `Workspace: "inherit"`):
     - **Goldfish Remediator 5A**: Applies production code, security, config, and style fixes ($R_A$).
     - **Goldfish Remediator 5B**: Upgrades unit/integration tests and adversarial cases ($R_B$).
     - **Goldfish Remediator 5C**: Builds/updates the modular E2E bash harness under `tests/e2e_<feature>/` ($R_C$, per [`pr-feature-branch-review/references/e2e_harness_guide.md`](../pr-feature-branch-review/references/e2e_harness_guide.md)).
3. **100% Honest Verification & Post-Fix Intermediate Zoom-Out (EGM Stage 8)**:
   - Run the full unit/integration test suite, linters, type-checkers, and E2E runner inside the project's reproducible environment (`uv run`, `poetry run`, `.venv/bin/python`; for Python: `ruff check .`, `ruff format --check .`, `mypy .` / `pyright`, `pytest` per [`python-readability`](../python-readability/SKILL.md) §3, §11) until **100% green (`0 errors`)** (capped at 3 fix iterations; halt on churn).
   - Run a fast **Intermediate Zoom-Out check** to ensure Stage 5 fixes did not introduce defensive bloat or violate `python-readability` rules.

---

### Stage 6: Wave 6 — Parallel Goldfish Delivery Artifacts & Drift Verification (3 Parallel Goldfish)

Once source code and tests are 100% locked and green, spawn **3 parallel Goldfish workers** on non-overlapping delivery paths:

| Concurrent Agent | Skill Invoked | Deliverable Output |
| :--- | :--- | :--- |
| **Goldfish 6A** | [`release-notes`](../release-notes/SKILL.md) | Inspect `git diff <default-branch>...HEAD` and generate `<repo_root>/releases/v<VERSION>_<slug>.md` grounded in real symbols and test counts. |
| **Goldfish 6B** | [`pr-feature-branch-review`](../pr-feature-branch-review/SKILL.md) (Phase 7 + Drift Check) | Update `docs/<feature>_guide.md` and `README.md`, purge dead config fields, and verify 0 Spec-to-Code drift against Stage 0 contracts. |
| **Goldfish 6C** | [`ai-assisted-software-engineering`](../ai-assisted-software-engineering/SKILL.md) (Phase 6) | Perform CI/CD pipeline & production readiness audit (cached dependencies, runtime config portability, rollback safety; OTel probes & `/healthz`/`/readyz` for deployed services/APIs). |

---

### Stage 7: Elephant Boundary Audit, Socratic Comprehension Gate & Master Handoff

1. **File-Boundary & Working Tree Verification**:
   - Run `git status` and `git diff --stat` to verify that every modified file belongs to the approved Stage 0/Stage 5 `Target Scope & File Boundary` allowlists and zero scratch files leaked into the repo.
2. **Pre-Commit Author Comprehension Gate (Optional / When Requested)**:
   - Invoke [`code-mentor` (Mode 3: "Explain My Changes")](../code-mentor/SKILL.md) in the Elephant thread to quiz the human engineer on the Goldfish-implemented changes before committing.
3. **Atomic Commit & Safe Branch Push (With User Confirmation)**:
   - Commit using Conventional Commits (`feat:`, `fix:`, `refactor:`). Push to the active feature branch (`origin feat/<branch>`—**NEVER push to `main` or `master`**) when requested by the user.
4. **Master Output Report**:
   - **Elephant & Goldfish Wave Scorecard**: Summary of parallel implementation slices, Wave 2–4 audit findings, `PROPOSE FIX | CONTEST | ESCALATE` resolutions, and test/E2E pass counts.
   - **Clickable `file://` Links & Verification Commands**: Links to all modified files, release notes, and exact terminal verification commands.
