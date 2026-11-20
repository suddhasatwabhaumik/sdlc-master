---
name: ai-assisted-software-engineering
description: >-
  End-to-end SDLC Architecture, Governance, and Operations SOP covering Phase 1 (Planning &
  Roadmapping), Phase 2 (Requirements Engineering), Phase 3 (System Architecture, ADRs,
  4-Goldfish Parallel Design Shootdowns, & Zero-Decision Implementation Contracts), Phase 6
  (CI/CD & Production Readiness), and Phase 7 (Parallel Goldfish Incident Triage, RCA &
  Spec-to-Code Drift Auditing).
---

# AI-Assisted Software Engineering (Elephant Spec & Goldfish Governance SOP)

This skill defines the governance and execution framework for the **upstream (Planning, Requirements, Architecture, & Spec Verification)** and **downstream (CI/CD Deployment, Incident RCA, & Drift Auditing)** phases of the Software Development Lifecycle using the **Elephant-Goldfish Model (EGM)**:
- **The Elephant (Persistent Main Thread — Architect & Spec Compiler)**: Synthesizes stakeholder goals, resolves architectural trade-offs with the human engineer (`Author Decides Architecture`), reconciles predecessor context for contradictions, and authors checked-in design documents (`docs/designs/<feature>.md`) with a strict **Zero-Decision Goldfish Implementation Contract** (`Target Scope & File Boundary` allowlists $S_1 \cap \dots \cap S_K = \emptyset$).
- **Parallel Goldfish Waves (Zero-Context Sub-Agents)**: Stress-test candidate designs in parallel during Phases 1–3 (**4-Goldfish Shootdown Swarm**), execute disjoint implementation slices in Phases 4–5 (via [`coding`](../coding/SKILL.md) and [`pr-feature-branch-review`](../pr-feature-branch-review/SKILL.md)), triangulate production incidents in Phase 7 (**3-Goldfish RCA Swarm**), and audit Spec-to-Code drift.

---

## 1. Core Governance Principles

1. **Deterministic Proof Over Statistical Plausibility ("Never Trust Plausible Output")**:
   - Ground every design and operational decision in actual repository manifests, installed package versions, upstream/downstream API contracts, and verifiable telemetry.
2. **Elephant Context vs. Zero-Context Goldfish Verification**:
   - Never allow the same conversational thread to brainstorm, draft a spec, and self-approve it without spawning isolated **Goldfish Critic Sub-Agents** (with zero prior conversation history) to expose unstated assumptions, YAGNI bloat, and false compromises.
3. **Artifact-First UX & Semantic Boundary Split**:
   - Never dump multi-page specifications directly into the chat stream. Write design documents to `docs/designs/<feature>.md` (or an artifact file) divided by an explicit semantic boundary header (`## Detailed Implementation Plan`) separating high-level architecture (`FeatureRange`) from the zero-decision file-change plan (`DetailedRange`).
4. **The Zero-Decision Rule & Disjoint Slice Partitioning ($S_i \cap S_j = \emptyset$)**:
   - Phase 3 specifications must leave **zero architectural or design choices** to Phase 4–5 Goldfish implementers, and must partition implementation tasks into mutually exclusive file write boundaries so parallel Goldfish implementers can execute simultaneously without collisions.
5. **Human-in-the-Loop (HITL) Curation (`Author Decides Architecture`)**:
   - When an architectural decision has $>1$ defensible answer, present 2–3 unranked options with their mechanism, trade-offs, and failure conditions for human selection.

---

## 2. End-to-End AI-Augmented SDLC & Parallel Goldfish Routing

```
┌────────────────────────────────────────────────────────────────────────────┐
│ 1 & 2. PLANNING & REQUIREMENTS (Elephant Main Thread)                      │
│    • Extract Goals, Non-Goals, KPIs/SLOs, FRs/NFRs (Given/When/Then)       │
│    • Contradiction & Missing-Dependency Audit against repo manifests       │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     ▼  [HITL Gate: Scope & Requirements Sign-Off]
┌────────────────────────────────────────────────────────────────────────────┐
│ 3A. CANDIDATE ARCHITECTURE & PARALLEL GOLDFISH SHOOTDOWN (4 Goldfish)      │
│    • Goldfish 0A: Contrarian / YAGNI & Codebase Reuse Search               │
│    • Goldfish 0B: Cost, Quota, Latency & Token Economics                   │
│    • Goldfish 0C: Security, Tenant Trust & Migration/Rollback Safety       │
│    • Goldfish 0D: TRIZ Inventive Catalyst (False-Compromise Resolution)    │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ 3B. SPEC FINALIZATION & DISJOINT SLICE CONTRACT (`docs/designs/<feat>.md`) │
│    • Predecessor Contradiction Reconciliation (Brief vs. Draft)            │
│    • Lock shared interfaces (`ports.py`/schemas) & Disjoint Slices (S1..SK)│
└────────────────────────────────────┬───────────────────────────────────────┘
                                     ▼  [HITL Gate: Architecture & Contract Approval]
┌────────────────────────────────────────────────────────────────────────────┐
│ 4 & 5. PARALLEL GOLDFISH IMPLEMENTATION & AUDIT (`coding` + `code-review`) │
│    • Wave 1: 2-4 Parallel Goldfish Slice Implementers (S1 ∩ S2 = ∅)        │
│    • Waves 2-4: Parallel Goldfish Viewpoint Audit + Pass-2 Falsification   │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ 6. DEPLOYMENT READINESS (Goldfish Readiness Auditor)                       │
│    • CI/CD caching, zero hardcoded env vars, OTel probes & rollback gates  │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     ▼  [HITL Gate: Release Approval]
┌────────────────────────────────────────────────────────────────────────────┐
│ 7. MAINTENANCE: PARALLEL INCIDENT RCA & SPEC-TO-CODE DRIFT (3 Goldfish)    │
│    • RCA Scouts: (7A: Logs/Traces, 7B: Git Blame/Diff, 7C: Config Drift)   │
│    • Periodic Drift Report comparing `docs/designs/*.md` vs. live code     │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. SDLC Phase Playbooks

### Phase 1: Planning (Ideation, Scoping & Roadmapping — Elephant)

| Step | Action | Output Section in Spec Artifact |
| :--- | :--- | :--- |
| **1. Context Synthesis** | Ingest stakeholder notes, RFCs, or briefs; extract explicit **Goals**, **Non-Goals (Out of Scope)**, **Success KPIs/SLOs**, and **Open Questions**. | `## Overview`, `## Goals`, `## Non-Goals` |
| **2. Work Breakdown** | Decompose into Milestones (MVP $\rightarrow$ v1.0 $\rightarrow$ Hardening) and atomic work slices with a critical-path Dependency DAG. | `## Phasing & Milestones` |
| **3. Risk Register** | Identify technical, security, and dependency risks with Probability, Impact, and Concrete Mitigation. | `## Risks & Mitigations` |

---

### Phase 2: Analysis (Requirements Engineering & Feasibility QA — Elephant)

1. **Deterministic Requirements & Critical User Journeys (CUJs)**:
   - Express functional and non-functional requirements (latency, throughput, auth/RBAC, tenant isolation) in testable **Given / When / Then** CUJ format—explicitly including negative/error states (nulls, timeouts, `429`s, `401`/`403`) so downstream tests never mock them away.
2. **Contradiction & Native Dependency Audit**:
   - Check repository manifests (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`) to verify whether required capabilities are already supported by `{{DOMAIN_STACK}}`.
   - If a new requirement contradicts an earlier goal or system invariant, halt immediately and ask the user in plain text before editing any files.

---

### Phase 3: Design (Parallel Goldfish Shootdown, ADRs & Zero-Decision Contracts)

1. **Anti-Bloat Architectural Decision Records (ADRs) & Mandatory Alternatives**:
   - Present 2–3 viable options (always including the simplest idiomatic design leveraging existing `{{DOMAIN_STACK}}` primitives). Document rejected options under `## Alternatives Considered` with concrete technical reasons (`Rejected by author: [rationale]`).
2. **Parallel 4-Goldfish Design Shootdown Wave**:
   - Spawn **4 parallel zero-context Goldfish sub-agents** (`invoke_subagent` with `TypeName: "research"`, strictly read-only) to stress-test the draft architecture:
     - **Goldfish 0A (Skeptical Architect / YAGNI)**: Searches the codebase for existing utilities to prevent reinvention and flags premature abstractions.
     - **Goldfish 0B (Scale & Quota Critic)**: Audits peak QPS, storage footprint, DB query amplification, and LLM/API token budgets.
     - **Goldfish 0C (Security, Migration & Rollback Critic)**: Audits cryptographic auth, tenant boundaries, backward schema compatibility, and mid-migration rollback safety.
     - **Goldfish 0D (TRIZ Inventive Catalyst)**: Challenges unexamined technical contradictions and proposes concrete software transforms (declaring secondary operational trade-offs).
3. **Visual Modeling & Predecessor Contradiction Reconciliation**:
   - Include Mermaid (`flowchart`, `sequenceDiagram`, `erDiagram`) or ASCII diagrams.
   - Re-read Phase 1–2 requirements and verify the Phase 3 draft introduces zero silent contradictions.
4. **Compile the `## Detailed Implementation Plan` (Zero-Decision Goldfish Contract)**:
   - Define the semantic split boundary at `## Detailed Implementation Plan` containing:
     - **Shared Interface Contracts**: Exact `models.py`, `ports.py`, OpenAPI/Protobuf schemas, and runtime environment variables.
     - **Disjoint Parallel Slice Map ($S_1 \cap S_2 \cap \dots \cap S_K = \emptyset$)**: Partition target files (`Create | Modify | Delete`) into 2–4 non-overlapping slices with exact function signatures and test cases so Phase 4–5 Goldfish implementers make **zero** design guesses.

---

### Phases 4 & 5: Parallel Goldfish Coding, Testing & Review (Delegation Protocol)

Delegate implementation and PR verification to specialized skills:
- **Feature Implementation & Parallel Slice Coding**: Invoke [`coding`](../coding/SKILL.md) (spawning 2–4 parallel Goldfish Slice Implementers across $S_1 \dots S_K$).
- **Code & PR Verification**: Invoke [`code-review`](../code-review/SKILL.md) and [`pr-feature-branch-review`](../pr-feature-branch-review/SKILL.md) (running Wave 1 Paraphrase + Conciseness $\rightarrow$ Waves 2–3 Viewpoint Audit $\rightarrow$ Pass-2 Falsification $\rightarrow$ Parallel 4-Goldfish Remediation).

---

### Phase 6: Deployment (CI/CD Automation & Production Readiness Audit)

| Readiness Pillar | Mandatory Pre-Flight Verification |
| :--- | :--- |
| **Pipeline Determinism** | Linting, static type-checking, dependency scans, and unit/E2E suites run with cached dependencies and zero flaky poll loops. |
| **Runtime Config Portability** | Zero hardcoded URLs, project IDs, or magic strings—all environment-specific values injected via documented config/secret stores. |
| **Observability & Probes** | Structured logging (with trace/correlation IDs), plus cached OpenTelemetry metrics and `/healthz` + `/readyz` endpoints for deployed services/APIs. |
| **Safe Rollout & Rollback** | Backward-compatible DB/schema migrations, feature flags, and verified one-command rollback procedures. |

---

### Phase 7: Maintenance (Parallel Incident RCA & Spec-to-Code Drift Auditing)

1. **Parallel 3-Goldfish Incident Triage & Root Cause Analysis (RCA)**:
   - When investigating a production incident or regression, spawn **3 parallel read-only Goldfish Investigators** (`invoke_subagent` with `TypeName: "research"`):
     - **Goldfish 7A (Telemetry & Stack-Trace Scout)**: Correlates error logs, stack traces, and metric spikes.
     - **Goldfish 7B (Git Blame & Diff Scout)**: Inspects recent commits/PR diffs touching the failing call path.
     - **Goldfish 7C (Config, Manifest & Mock-Gap Scout)**: Checks for runtime env drift, dependency mismatches, or unit tests that mocked away the failing runtime state.
   - Synthesize into a structured RCA (`Timeline -> Root Cause -> Contributing Test/Mock Gap -> Remediation Slice Contract`), write a **failing reproduction test first** (without mocking away the broken state), and patch via [`coding`](../coding/SKILL.md).

2. **Periodic Spec-to-Code Drift Audit (`egm-drift-report` Pattern)**:
   - When asked to check documentation/spec health across `docs/designs/` or package `README.md` files, spawn parallel read-only Goldfish Drift Auditors to compare each document against live source files:
     - Flag **Missing Features**, **Incomplete Models/DTOs**, **Hardcoded Logic Shortcuts**, **Architectural Divergence**, and **Hallucinated/Renamed Symbols**.
     - Write ONLY verified discrepancies to `{YYYY-MM-DD}_DRIFT_REPORT.md` for human triage.

---

## 4. 8-Point Curator Audit Rubric & HITL Deliverable Format

Before signing off on any SDLC phase deliverable, verify all 8 curator dimensions:
1. **Conciseness vs. Bloat** (Wave 1 pre-gate applied; zero speculative Factory/Strategy bloat)
2. **Zero Hallucinations** (All symbols/flags verified against lockfiles and static type-checkers)
3. **Architecture & TRIZ Balance** (Single-point concurrency locks, clean Ports, secondary trade-offs declared)
4. **Runtime Env Hygiene** (Zero magic strings, hardcoded URLs, or project IDs)
5. **Native Dependency Alignment** (Zero hand-rolled compensation for `{{DOMAIN_STACK}}` primitives; clean runtime vs. dev manifests)
6. **Test Mock Realism** (Production code handles every mocked failure mode; zero silent E2E mock fallbacks)
7. **Security & Trust Boundaries** (Cryptographic auth, zero `mock-token-*` backdoors, strict RBAC & tenant isolation)
8. **Artifact-First Ergonomics** (Specs/reports written to files with clickable `file://` links, exact verification commands, and explicit HITL decision gates)
