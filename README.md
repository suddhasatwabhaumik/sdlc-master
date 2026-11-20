# SDLC Master Orchestrator — Gemini Antigravity Plugin

[![Validate Antigravity Plugin](https://github.com/suddhasatwabhaumik/sdlc-master/actions/workflows/validate-plugin.yml/badge.svg)](https://github.com/suddhasatwabhaumik/sdlc-master/actions/workflows/validate-plugin.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

An open-source **"Skill of Skills"** plugin for **Gemini Antigravity** (Antigravity IDE, VSCode Extension, and Antigravity CLI) that orchestrates the entire Software Development Lifecycle (SDLC) for safe, structured, automated, error-free software engineering.

---

## Why This Plugin? (The Elephant-Goldfish Model)

Single-thread AI coding agents degrade over long conversations: they suffer from **confirmation bias** (rubber-stamping their own code), **context dilution** (missing deep security or concurrency bugs), and **speculative over-engineering**.

**SDLC Master Orchestrator** solves this with the **Elephant-Goldfish Model (EGM)** and **Disjoint Parallel Sub-Agent Sharding**:

- **The Elephant (Persistent Main Thread)**: Holds stakeholder goals, system invariants, and architectural trade-offs. It never writes multi-file production code inside a bloated design thread. Instead, it locks shared interfaces (`models.py`, `ports.py`, schemas), partitions work into mutually exclusive file slices ($S_1 \cap S_2 \cap \dots \cap S_K = \emptyset$), and triages audit findings (`PROPOSE FIX | CONTEST | ESCALATE | DECLINE`).
- **Parallel Goldfish Waves (Zero-Context Sub-Agents — Max 3–4 per Wave)**: Stateless sub-agents spawned with zero prior conversation history. Implementers receive only their self-contained Slice Contract and strict write allowlist; auditors review the resulting disk diff without confirmation bias, followed by a Pass-2 Falsifier that disproves false positives before anything reaches you.

### Core Safety & Quality Guardrails

- **Zero-Decision Rule**: Implementation workers halt (`BLOCKED_ON_SPEC_CONTRADICTION`) instead of guessing unstated architectural choices.
- **Strict File-Write Allowlists**: Parallel workers operate on disjoint file slices ($S_i \cap S_j = \emptyset$) and verify `git status` against the approved allowlist.
- **Contradiction Halt Rule**: If a request contradicts existing codebase invariants, the agent stops and asks before editing any files.
- **Untrusted PR Nonce Wrapping**: External PR diffs and comments are wrapped in random per-run nonces to mitigate prompt injection.
- **Never Push to `main` / `master`**: Commits and pushes target active feature branches only, with explicit user confirmation.
- **Progressive Disclosure**: Bundled strictly as Antigravity `skills/` (no always-on rules), consuming minimal context until activated.

---

## Bundled Skills (10)

| Skill | Role in the SDLC Pipeline |
| :--- | :--- |
| [`sdlc-master-orchestrator`](./skills/sdlc-master-orchestrator/SKILL.md) | Master router & 8-stage Elephant-Goldfish orchestrator (Modes A–F) |
| [`ai-assisted-software-engineering`](./skills/ai-assisted-software-engineering/SKILL.md) | Phases 1–3 (Planning, Requirements, ADRs, 4-Goldfish Design Shootdown), Phase 6 (CI/CD Readiness), & Phase 7 (3-Goldfish Incident RCA & Drift Audit) |
| [`coding`](./skills/coding/SKILL.md) | Contract locking, disjoint slice partitioning, parallel Goldfish implementation, & bounded 3-try test/lint verification |
| [`python-design-patterns`](./skills/python-design-patterns/SKILL.md) | Ports/Adapters (`typing.Protocol`, `abc.ABC`), Anti-Corruption Layers, `ContextVar` isolation, & parametrized `pytest` contract suites |
| [`python-readability`](./skills/python-readability/SKILL.md) | Python readability, code-density (*"optimize for readability, not conciseness"*), `pyproject.toml`/venv hygiene, hermetic tests, & §10 review guardrails |
| [`code-review`](./skills/code-review/SKILL.md) | Staged parallel Goldfish review: Wave 1 (Conciseness + Naive Paraphrase), Wave 2 (Arch/Config/Deps/Security), Wave 3 (Test Realism/Style/Domain), & Pass-2 Falsification |
| [`google-style-guide`](./skills/google-style-guide/SKILL.md) | Official Google Python Style Guide compliance, modern Python 3.10+ typing, & defensive prose calibration (`DROP \| CALIBRATE \| RELOCATE \| KEEP`), respecting repo linter config |
| [`pr-feature-branch-review`](./skills/pr-feature-branch-review/SKILL.md) | Safe branch sync, multi-viewpoint PR audit, 4-Goldfish parallel remediation (Prod, Unit Tests, Modular E2E Bash Suite, Docs), & GitHub PR reply generation |
| [`release-notes`](./skills/release-notes/SKILL.md) | 3-scout codebase-grounded release notes authoring under `<repo_root>/releases/vX.Y.Z_<slug>.md` |
| [`code-mentor`](./skills/code-mentor/SKILL.md) | Read-only Socratic architecture coach & pre-commit comprehension quiz ("Explain My Changes") |

---

## Installation

Choose the installation method that matches your workflow. Because **Antigravity CLI**, **Antigravity IDE**, and the **Antigravity VSCode Extension** all discover plugins from `~/.gemini/config/plugins/` (global) and `.agents/plugins/` (workspace), installing once works across all surfaces.

### Option 1: Antigravity CLI (Recommended — Works in IDE, VSCode Extension & CLI)

```bash
agy plugin install https://github.com/suddhasatwabhaumik/sdlc-master
```

Verify installation:

```bash
agy plugin list
```

### Option 2: Direct Global Clone (Antigravity IDE / VSCode Extension without CLI)

```bash
mkdir -p ~/.gemini/config/plugins
git clone https://github.com/suddhasatwabhaumik/sdlc-master.git \
  ~/.gemini/config/plugins/sdlc-master-orchestrator
```

Restart or open a new chat session in Antigravity IDE or VSCode to pick up the skills.

### Option 3: Team / Repository-Scoped Setup (`.agents/plugins.json`)

To share the plugin automatically with every engineer who clones your repository:

1. Vendor or add this repository as a submodule under `.agents/plugins/sdlc-master-orchestrator`:
   ```bash
   git submodule add https://github.com/suddhasatwabhaumik/sdlc-master.git \
     .agents/plugins/sdlc-master-orchestrator
   ```
2. Or place the plugin folder inside a directory (e.g., `tools/antigravity/plugins/sdlc-master-orchestrator/plugin.json`) and register the parent folder in `.agents/plugins.json` (Antigravity scans each entry one level deep):
   ```json
   {
     "entries": [
       { "path": "tools/antigravity/plugins" }
     ]
   }
   ```

### Option 4: Offline `.zip` Release Archive

Download `sdlc-master-orchestrator-v<VERSION>.zip` from tagged [GitHub Releases](https://github.com/suddhasatwabhaumik/sdlc-master/releases) (or build locally via `./scripts/package_plugin.sh`). Because `agy plugin install` requires an unpacked directory (not a `.zip` file), extract into a named directory first:

```bash
# Install via Antigravity CLI from an extracted directory
mkdir -p ./sdlc-master-orchestrator
unzip -q sdlc-master-orchestrator-v1.0.0.zip -d ./sdlc-master-orchestrator
agy plugin install ./sdlc-master-orchestrator
rm -rf ./sdlc-master-orchestrator
```

---

## Quickstart Prompts

Once installed, trigger any SDLC mode directly in Antigravity IDE, VSCode Extension chat, or `agy`:

- **Mode A — Greenfield Architecture & Implementation**:
  > *"Use `sdlc-master-orchestrator` to design and implement a rate-limited webhook ingestion service end-to-end."*
- **Mode B — Safe Feature Implementation / Bug Fix**:
  > *"Use `sdlc-master-orchestrator` to implement pagination on `/v1/orders` with disjoint parallel coding and full Goldfish review."*
- **Mode C — PR / Feature Branch Review & Remediation**:
  > *"Use `pr-feature-branch-review` to run a full Goldfish multi-viewpoint audit and remediate findings on my current feature branch."*
- **Mode D — Production Incident RCA**:
  > *"Use `sdlc-master-orchestrator` in Mode D to run a 3-Goldfish incident RCA on the timeout spike in `worker.py` and lock a failing reproduction test."*
- **Mode E — Spec-to-Code Drift Audit**:
  > *"Use `sdlc-master-orchestrator` in Mode E to compare `docs/designs/` against our live source code and generate a drift report."*
- **Mode F — Pre-Commit Comprehension Quiz ("Explain My Changes")**:
  > *"Use `code-mentor` in Mode 3 to quiz me on my uncommitted changes before I commit."*

---

## Optional Companion Plugins

- **Security Scanning**: In Stage 3 (Security & Trust Audit), `sdlc-master-orchestrator` automatically integrates with `Google.securecoder.securecoder` (`mandatory-secure-web-skills`, `run-security-scanner`, `scan_dependencies`) if installed in your environment. If not installed, it cleanly falls back to the built-in `code-review` Goldfish `2D` (`goldfish-2d-security-trust`) persona.

---

## Local Validation & Packaging

Contributors can validate the plugin manifest, relative links, size limits (`< 24,000` bytes per `SKILL.md`), and build a release `.zip`:

```bash
# 1. Run cross-platform Python integrity & sanitization checks
python3 scripts/validate_plugin.py

# 2. Run official Antigravity strict validation + build release zip
./scripts/package_plugin.sh
```

---

## License & Attribution

- Licensed under the [Apache License 2.0](./LICENSE).
- See [NOTICE](./NOTICE) for third-party attribution of the bundled Google Python Style Guide reference (`skills/google-style-guide/references/style_guide_full.md`).
