---
name: release-notes
description: >-
  Standard Operating Procedure (SOP) for drafting comprehensive, production-grade release notes
  markdown files under `<repo_root>/releases/` using the Elephant-Goldfish Model (EGM). The
  Elephant locks the version/slug scope, spawns 3 parallel read-only Goldfish extraction scouts
  (Git Diff Scout, Source Symbol/Config Scout, and Test/E2E Metrics Scout), and compiles a
  100% codebase-grounded release note with zero unverified claims.
---

# Release Notes Authoring SOP (`release-notes`)

This skill defines the enterprise-grade methodology for authoring developer-ready release notes markdown files under `<repo_root>/releases/` using the **Elephant-Goldfish Model (EGM)**:
- **The Elephant (Main Thread)**: Identifies the SemVer release target (`v<MAJOR>.<MINOR>.<PATCH>`) and feature slug, dispatches 3 parallel read-only Goldfish scouts to extract ground-truth facts from disk, and verifies the final artifact.
- **Parallel Goldfish Extraction Scouts (3 Read-Only Sub-Agents)**: Inspect git history, source modules, and test harnesses with **zero conversational bias** so release notes never contain hallucinated CLI flags, fabricated test counts, or uncalibrated claims.

---

## 1. Core Operating Principles

1. **Target Directory & Standardized Filename Enforcement**:
   - Every release note markdown document MUST be written to `<repo_root>/releases/v<MAJOR>.<MINOR>.<PATCH>_<descriptive_feature_slug>.md` (e.g., `releases/v1.1.0_dynamic_environment_resolution.md`).
   - If `<repo_root>/releases/` does not exist, create it first. Never write release notes to the repo root or arbitrary subdirectories.

2. **Goldfish Codebase Grounding & Prose Calibration (`DROP | CALIBRATE | RELOCATE | KEEP`)**:
   - Release notes are technical runbooks and architectural manifests—never marketing blurbs.
   - Every function signature, configuration key, environment variable, CLI flag, and test command must be verified against live repository files (`[file:symbol]`).
   - Apply EGM prose calibration: strip promotional adjectives (*"seamless"*, *"revolutionary"*), **CALIBRATE** every capability claim to match actual test evidence, and **NEVER** fabricate test pass counts.

3. **Zero Tolerance for Exposed Secrets or Hardcoded Proprietary IDs**:
   - Ensure release notes contain zero live tokens, internal passwords, or proprietary customer identifiers. Use generic placeholders (`projects/{project_id}/secrets/...`, `europe-west4`, `example-cloud-project`).

4. **Visual Architecture & ASCII Diagrams**:
   - Include clear ASCII/Unicode diagrams (boxes, precedence tables, execution flows) illustrating evaluation chains, data pipelines, or E2E verification harnesses.

---

## 2. Target File Structure & The 6-Section Standard

Every release note must adhere to the standardized 6-section structure (see [`resources/release_note_template.md`](./resources/release_note_template.md)):

```text
<repo_root>/releases/v<VERSION>_<feature_slug>.md
├── Header: Title with Version & Target Module / Subsystem
├── Section 1: Overview (Context, Problem Statement, Before vs After, Impact)
├── Section 2: Architecture / Technical Design / Precedence Hierarchy (with ASCII Diagram)
├── Section 3: How to Use in Your Workflow (Verified Code Examples & Subsystem Routing)
├── Section 4: How to Run Unit & Integration Tests (Exact pytest/test commands & coverage)
├── Section 5: End-to-End Testing with the Automated Test Harness (ASCII Flow & Scenarios)
└── Section 6: Verification Status & Compliance Guardrails (Pass rates & standards compliance)
```

---

## 3. Detailed Section Requirements

### Header Block
```markdown
# Release Notes: <Feature / System Name> (`v<MAJOR>.<MINOR>.<PATCH>`)

## Module: `<target.module.or.subsystem>`
<!-- or ## Component: `<component_name>` / ## Service: `<service_name>` -->

---
```

### Section 1: Overview
- **Problem Statement**: What concrete friction, limitation, manual configuration, or vulnerability existed prior to this release?
- **Core Solution**: What does this module/feature do, and how does it solve the issue?
- **Impact on Downstream Subsystems**: How do other services, connectors, or pipelines benefit?

### Section 2: Architecture & Technical Design (with ASCII/Unicode Diagrams)
- **Visual Representation**: Provide an ASCII/Unicode box diagram showing the evaluation chain, state machine, or pipeline architecture:
  ```text
  ┌────────────────────────────────────────────────────────────────────────┐
  │                        Evaluation Precedence                           │
  ├─────────┬──────────────────────────────────┬───────────────────────────┤
  │ Tier 1  │ In-Code Overrides                │ set_override_env(), ...   │
  ├─────────┼──────────────────────────────────┼───────────────────────────┤
  │ Tier 2  │ Project YAML Configuration       │ mlops_config.yaml, ...    │
  └─────────┴──────────────────────────────────┴───────────────────────────┘
  ```
- **Tier / Component Breakdown**: Numbered breakdown of every tier, component, fallback mechanism, timeout, and environment variable evaluated.
- **Fail-Safe & Edge Case Handling**: Detail how network timeouts, offline workstations, or invalid configs are handled.

### Section 3: How to Use in Your Workflow
- Provide practical, copy-pasteable code snippets verified against actual module imports:
  - **A. Basic Usage / Quickstart**: Importing, initializing, and basic invocation.
  - **B. Downstream Routing / Subsystem Integration**: How other components react to the feature.
  - **C. Configuration & Environment Parity**: How local sandbox, CI/CD, and cloud production environments are configured.
  - **D. Interoperability with Application Engines**: How consumer repos or services consume this module.

### Section 4: How to Run Unit & Integration Tests
- Exact terminal commands to execute the test suite:
  ```bash
  # 1. Run targeted unit test suite
  pytest tests/test_<feature>.py -v

  # 2. Run with coverage report
  pytest tests/test_<feature>.py --cov=<module_path> --cov-report=term-missing

  # 3. Run full repository regression suite
  pytest tests/
  ```
- Document exact verified test counts and coverage thresholds.

### Section 5: End-to-End Testing with the Automated Test Harness
- Provide the exact shell script or runner command (`./tests/e2e_<feature>/run_all_<feature>_tests.sh [PROJECT_ID_OR_ARGS]`) and an ASCII diagram of the test harness stages, breaking down each scenario and standalone script execution.

### Section 6: Verification Status & Compliance Guardrails
- **Generic Standards**: Confirm zero hardcoded client projects, credentials, or proprietary URLs exist in the library.
- **Pass Rate Summary**: Explicit quantitative metrics grounded in actual test execution (e.g., `100% (23/23 unit tests, 79/79 full repo tests, 4/4 E2E scenarios)`).

---

## 4. End-to-End Elephant & Parallel Goldfish Execution Protocol

```
[Step 1 & 2: Version & Scope Lock (Elephant Main Thread)]
       │  • Inspect git log, git diff main...HEAD, and pyproject.toml / package.json / VERSION
       │  • Lock target path: <repo_root>/releases/v<VERSION>_<feature_slug>.md
       ▼
[Step 3: Parallel Zero-Context Goldfish Extraction Wave (3 Read-Only Scouts)]
       │  • Goldfish Scout 3A (Git & Scope Scout): Map all modified files, commits, and breaking changes
       │  • Goldfish Scout 3B (Source & Config Contract Scout): Extract exact signatures, env vars,
       │    precedence tiers, error types, and CLI flags with [file:symbol] citations
       │  • Goldfish Scout 3C (Test & E2E Metrics Scout): Inspect unit tests & E2E shell scripts,
       │    run/verify exact test counts, and extract scenario matrices
       ▼
[Step 4 & 5: Goldfish Release Notes Compilation]
       │  • Populate all 6 standard sections from the verified Scout payloads
       │  • Construct ASCII architecture & E2E harness diagrams matching real code boundaries
       ▼
[Step 6: Quality, Secret & Drift Audit (Elephant Final Gate)]
          • Verify zero hardcoded secrets, zero hallucinated symbols, & valid GFM tables/code fences
          • Confirm file exists under <repo_root>/releases/ and report clickable file:// link
```

---

## 5. Quick Reference & Templates

- **Reference Implementation**: See [`v1.1.0_dynamic_environment_resolution.md`](./examples/v1.1.0_dynamic_environment_resolution.md) for the canonical gold standard.
- **Ready-to-Use Template**: See [`release_note_template.md`](./resources/release_note_template.md).
