---
name: coding
description: >-
  Standard Operating Procedure (SOP) for day-to-day software engineering using the
  Elephant-Goldfish Model (EGM) and parallel sub-agent sharding. The Main Thread acts as the
  Elephant (Discovery, Anti-Bloat Scoping, Interface Locking, and Disjoint Slice Partitioning),
  while actual code implementation, black-box test authoring, and staged multi-viewpoint reviews
  execute in parallel waves of stateless, zero-context Goldfish sub-agents.
---

# Day-to-Day Coding & Parallel Goldfish Implementation SOP (`coding`)

This skill enforces a strict cognitive separation between **Strategic Design (The Elephant)** and **Zero-Context Implementation & Verification (Parallel Goldfish Sub-Agents)**:
- **The Elephant (Persistent Main Thread)**: Explores the repository, resolves ambiguities with the human engineer, locks shared interfaces (`ports.py`, `models.py`, function signatures), and partitions work into **Disjoint Implementation Slices ($S_1 \cap S_2 \cap \dots \cap S_K = \emptyset$)**.
- **Parallel Goldfish Implementers (Zero-Context Sub-Agents)**: Spawned via `invoke_subagent` with **zero prior conversation history**. Each Goldfish receives *only* its self-contained Slice Contract and explicit `GoldfishContext` file paths, writes code strictly within its assigned `Target Scope & File Boundary`, runs a bounded 3-try test/lint loop, and fails fast if the contract left any unstated design decision.

---

## 1. Core Engineering Principles

1. **Elephant Strategy vs. Parallel Goldfish Implementation**:
   - Never write multi-file production code inside a bloated conversational thread filled with earlier hypotheses.
   - **Contract-First Sharding**: Lock shared data models/signatures first, then spawn **2–4 parallel Goldfish Slice Workers** across mutually exclusive file allowlists ($S_i \cap S_j = \emptyset$) so implementation and contract-driven test authoring run concurrently without file-write collisions.
   - *(Micro-Patch Exception: Single-file edits `<= 15` lines with zero architectural choices and no prior design debate may be applied in a single fast pass).*

2. **The Zero-Decision Rule & Contradiction Auditing Halt**:
   - **Zero-Decision Rule**: The Elephant's Implementation Contract must leave **zero architectural or design choices** (schemas, API routes, dependencies, error policies) to the Goldfish implementer. If a Goldfish implementer encounters an unstated design choice or a mismatch with live disk code, it **MUST NOT guess**—it halts immediately and returns `BLOCKED_ON_SPEC_CONTRADICTION`.
   - **Contradiction Auditing Halt (Elephant)**: If the user's request contradicts earlier goals or codebase invariants, **do not call any file-editing tools in that turn**. Point out the contradiction in plain text with `[file:line]` citations and ask for resolution.
   - **Author Decides Architecture**: When a design question has $>1$ defensible answer, present up to 3 unranked options with their failure modes and ask the user to choose. Decide purely mechanical details (local variable names, formatting) autonomously.

3. **Surgical File-Boundary Allowlist & Scratchpad Isolation**:
   - **Strict Write Allowlist (`Target Scope & File Boundary`)**: Goldfish workers may only create, modify, or delete exact repository-relative paths listed in their assigned Slice Contract. Never reformat untouched files.
   - **Scratchpad Isolation**: Write temporary reproduction scripts or exploratory probes strictly to the conversation scratch directory (`<appDataDir>/brain/<id>/scratch/` or `mktemp -d`), never inside the source tree or fixed `/tmp/scratch.py`.

4. **Anti-Over-Engineering & Native Dependency First**:
   - Write the simplest idiomatic code solving the root problem. Reject speculative abstractions, premature interfaces, and deep wrapper layers.
   - Never write custom workaround code compensating for a missing dependency or reinventing `{{DOMAIN_STACK}}` / standard library primitives.

5. **100% Honest Verification (Test Realism Over Mock Theatre)**:
   - Every change must pass automated unit/integration tests, linters, and static type-checkers (`0 errors`).
   - **Mock Realism Rule**: Never pass a test by mocking out a runtime state (nulls, timeouts, `429`s, `5xx`s, malformed payloads) that production code fails to handle.

6. **Security & Runtime Configuration Hygiene**:
   - Zero hardcoded secrets, credentials, `mock-token-*` backdoors, magic strings, URLs, project IDs, ports, or timeouts in business logic—inject all runtime parameters via typed environment configuration.

---

## 2. End-to-End Elephant & Parallel Goldfish Coding Lifecycle

```
[Phase 1: Parallel Goldfish Discovery Scouts (Read-Only)]
       │  • Inspect manifests, lockfiles, and {{DOMAIN_STACK}}
       │  • (Multi-module repos) Spawn 2-3 parallel Goldfish Scouts:
       │    (1A: Toolchain/Manifests, 1B: Existing Reuse Search, 1C: Caller Blast Radius)
       ▼
[Phase 2: Elephant Scoping, Interface Lock & Disjoint Slice Partitioning]
       │  • Resolve trade-offs with user (Author Decides Architecture)
       │  • Lock shared interface/DTO files (models.py, ports.py, schemas) first
       │  • Partition into 2-4 Disjoint Goldfish Slices (S1 ∩ S2 ∩ ... ∩ SK = ∅)
       ▼
[Phase 3: Parallel Zero-Context Goldfish Implementation Wave (Max 3-4 Agents)]
       │  • Spawn parallel Goldfish Slice Workers (zero chat history):
       │    - Goldfish A: Core / Domain Slice (S1)
       │    - Goldfish B: Adapters / Infra / Wiring Slice (S2)
       │    - Goldfish C: Black-Box Unit, Negative & Contract Tests Slice (S3)
       │  • Enforce Zero-Decision Rule (halt on BLOCKED_ON_SPEC_CONTRADICTION)
       ▼
[Phase 4 & 5: Per-Slice & Integration Test Barrier + Bounded 3-Try Auto-Fix Loop]
       │  • Run detected test runner, linter, and typechecker across combined slices
       │  • Bounded 3-iteration debug loop with Churn Detection (fix prod code, never weaken tests)
       ▼
[Phase 6: Parallel Goldfish Self-Review Gate (Delegate to `code-review`)]
       │  • Wave 1 (2 Goldfish): Conciseness Refactor + Naive Behavioral Paraphrase
       │  • Waves 2 & 3 (4 + 3 Goldfish) + Pass-2 Falsifier (for Focused/Full changes)
       │  • Elephant Triage (PROPOSE FIX | CONTEST | ESCALATE | DECLINE)
       ▼
[Phase 7 & 8: File-Boundary Audit, Git Hygiene & Delivery Summary]
          • Verify git status matches Target Scope & File Boundary allowlist
          • Atomic Conventional Commit & summary with clickable file:// links
```

---

## 3. Detailed Phase Protocols

### Phase 1: Discovery, Domain & Dependency Audit (Elephant + Parallel Scouts)

1. **Detect Ecosystem Toolchain & `{{DOMAIN_STACK}}`**:

| Ecosystem | Toolchain Detection | Test Command | Lint / Typecheck Command |
| :--- | :--- | :--- | :--- |
| **Python (`uv`)** | `uv.lock` | `uv run pytest` | `uv run ruff check .` & `uv run mypy .` |
| **Python (`poetry`)** | `poetry.lock` | `poetry run pytest` | `poetry run flake8` & `poetry run mypy` |
| **Python (Pip/Std)** | `pyproject.toml`, `requirements.txt` | `pytest` | `ruff check .` / `pylint` & `mypy` / `pytype` |
| **Node / TS (`pnpm`)** | `pnpm-lock.yaml` | `pnpm test` | `pnpm run lint` & `pnpm run typecheck` |
| **Node / TS (`npm`)** | `package-lock.json` | `npm test` | `npm run lint` & `npm run build` |
| **Go** | `go.mod` | `go test ./...` | `golangci-lint run` |
| **Rust** | `Cargo.toml` | `cargo test` | `cargo clippy` & `cargo check` |
| **Java / Kotlin** | `pom.xml` or `build.gradle` | `mvn test` or `./gradlew test` | `mvn verify` or `./gradlew check` |

2. **Parallel Read-Only Goldfish Discovery Wave (When Exploring Multi-Module Codebases)**:
   Spawn **2–3 parallel read-only Goldfish Explorer Scouts** (`invoke_subagent` with `TypeName: "research"`) to gather facts without polluting the Elephant's context:
   - **Scout 1A (Reuse & Native Capability Scout)**: Searches the repo and installed packages for existing helpers, clients, or `{{DOMAIN_STACK}}` primitives that can be reused.
   - **Scout 1B (Blast-Radius & Caller Contract Scout)**: Maps all upstream callers, downstream consumers, and invariants of the target modules.
   - **Scout 1C (Test & Config Fixture Scout)**: Identifies existing test fixtures, cryptographic auth helpers, and config schemas.

---

### Phase 2: Elephant Contract Locking & Disjoint Slice Partitioning

Before spawning any mutating Goldfish implementers, the Elephant compiles the **Goldfish Implementation Contract**:

1. **Lock Shared Seams First**:
   - If multiple slices depend on shared types, DTOs, or `Protocol`/`ABC` ports (e.g., `domain/models.py`, `domain/ports.py`), write or update those shared contract files first so every parallel Goldfish worker reads an identical, immutable contract from disk.
2. **Partition into Disjoint Parallel Slices ($S_1 \cap S_2 \cap \dots \cap S_K = \emptyset$)**:
   - Partition the remaining work into **2–4 parallel slices** with **zero overlapping write paths**:
     - **Pattern A (Single-Module Parallel TDD Split)**:
       - *Slice 1 (Production Goldfish)*: Exclusive write access to `src/<module>.py`.
       - *Slice 2 (Black-Box Test Goldfish)*: Exclusive write access to `tests/test_<module>.py`. Writes unit, edge-case, and adversarial tests strictly against the locked function signatures/contracts in parallel with Slice 1—preventing tests from being biased by implementation bugs!
     - **Pattern B (Multi-Layer Architectural Split)**:
       - *Slice 1*: Core domain/service logic (`src/domain/...`).
       - *Slice 2*: Concrete & InMemory adapters (`src/adapters/...`).
       - *Slice 3*: API routes / CLI / config wiring (`src/api/...`).
       - *Slice 4*: Unit & parametrized contract tests (`tests/...`).
3. **Goldfish Slice Contract Schema (Pass Verbatim to Each Worker)**:
   ```markdown
   ## Goldfish Slice Contract: [Slice ID & Name]
   - **Role**: Zero-Context Goldfish Implementer (No shared chat history).
   - **Domain Stack**: `{{DOMAIN_STACK}}`
   - **GoldfishContext (Read-Only Baseline Files)**: `[exact repo-relative paths to read first]`
   - **Target Scope & File Boundary (STRICT WRITE ALLOWLIST — S_k)**:
     - `path/to/target_file.ext` (`Create` | `Modify` | `Delete`)
   - **Exact Behavioral & Interface Specification**:
     - [Exact signatures, data transformations, runtime config keys, and error handling for nulls/timeouts/4xx/5xx]
   - **Slice Verification Command**: `[static syntax/lint/typecheck command when running concurrently with sibling slices (e.g., ruff check / mypy / py_compile); defer combined runtime pytest to the Synchronization Barrier]`
   ```

---

### Phase 3: Parallel Zero-Context Goldfish Implementation Wave

Spawn the **2–4 Goldfish Slice Sub-Agents in parallel** (`invoke_subagent`, `TypeName: "self"`, `Workspace: "inherit"`). Each Goldfish worker must execute these rules:

1. **Zero-Decision Verification First**:
   - Read *only* the Slice Contract and `GoldfishContext` files.
   - If the contract requires making an undocumented architectural decision, or if a `GoldfishContext` file contradicts the contract, **do not guess or invent workarounds**. Stop immediately without modifying files and return:
     `STATUS: BLOCKED_ON_SPEC_CONTRADICTION — [file:line and exact contradiction]`.
2. **Strict Write-Boundary Enforcement**:
   - Modify **only** files listed in `Target Scope & File Boundary` ($S_k$). Creating or editing any file outside $S_k$ is a hard violation.
3. **Clean Code & Style Compliance**:
   - Keep functions cohesive (~40 lines or fewer), use flat control flow, enforce strict typing (follow [`python-readability`](../python-readability/SKILL.md) & [`google-style-guide`](../google-style-guide/SKILL.md) for Python while respecting repo `pyproject.toml`/`ruff` settings), and extract all constants/URLs/timeouts to runtime config.
   - Never swallow exceptions (`except Exception: pass`); chain domain exceptions (`raise DomainError(...) from exc`).

---

### Phases 4 & 5: Synchronization Barrier & Bounded 3-Try Honest Test Loop

1. **Slice Synchronization Barrier**:
   - Wait for all parallel Goldfish Slice Workers (`1..K`) to return their completion receipts.
2. **Execute Combined Toolchain Verification**:
   - Run the full unit/integration test suite, linter, and static type-checker across all modified slices (`S_1 \cup \dots \cup S_K`).
3. **Bounded 3-Iteration Auto-Fix Loop & Churn Guard**:
   - If any test, lint, or typecheck fails:
     - Trace the exact root cause in production code (or fix a test syntax bug without weakening assertions).
     - **Mock Realism Audit**: Verify that every mocked response or error in `tests/` corresponds to a state explicitly handled in production code.
     - **Hard Cap (Max 3 Iterations) & Churn Detection**: Allow at most **3 fix attempts**. If fixing Failure A causes Failure B to oscillate (Churn), or if failures persist after 3 attempts, halt immediately and report the root cause to the Elephant for architectural resolution.

---

### Phase 6: Parallel Goldfish Self-Review Gate (Delegate to `code-review`)

Before committing, invoke [`code-review`](../code-review/SKILL.md) (using the canonical personas in [`code-review/references/goldfish_viewpoint_personas.md`](../code-review/references/goldfish_viewpoint_personas.md)) according to the diff's **Adaptive Review Depth**:
1. **Wave 1 (2 Parallel Goldfish — Mandatory for All Changes)**:
   - `Goldfish 1A`: Conciseness & Readability Refactoring Specialist.
   - `Goldfish 1B`: Naive Behavioral Paraphraser (verifies the diff matches the Elephant's intent).
2. **Waves 2 & 3 + Pass-2 Falsifier (For `Focused` and `Full` Changes)**:
   - Run Wave 2 (4 Goldfish: Architecture/TRIZ, Runtime Config, Dependencies, Security) and Wave 3 (3 Goldfish: Test Realism, Standards/Style, `{{DOMAIN_STACK}}`), followed by Pass-2 Falsification.
3. **Elephant Resolution**:
   - Triage surviving findings (`PROPOSE FIX | CONTEST | ESCALATE | DECLINE`), apply approved fixes via a Goldfish worker, and re-verify tests (`100% green`).

---

### Phases 7 & 8: File-Boundary Audit, Git Hygiene & Delivery Summary

1. **Verify Write Allowlist Against `git status`**:
   ```bash
   git status --porcelain
   git diff --stat
   ```
   Confirm that 100% of modified/untracked files belong to the approved `Target Scope & File Boundary` ($S_1 \cup \dots \cup S_K$) and zero debug prints or scratch files remain.
2. **Atomic Commit & Safe Branch Policy**:
   - Commit with Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`).
   - **Never push directly to `main` or `master`**; push to feature branches only when requested.
3. **Structured Delivery Summary**:
   - Report the Elephant Contract & Slice Partitioning, Goldfish worker statuses, clickable `file://` links to all modified files, and exact verification commands executed.
