---
name: python-design-patterns
description: >-
  Standard Operating Procedure (SOP) and architectural refactoring guide for applying Pythonic
  Adapter, Interfacing (typing.Protocol, abc.ABC), Structural, Creational, Behavioral, and
  Boundary-Hygiene software design patterns using the Elephant-Goldfish Model (EGM). The Elephant
  (Main Thread) selects boundaries, evaluates secondary operational trade-offs, and locks
  `domain/models.py` and `domain/ports.py` contracts, while parallel zero-context Goldfish
  sub-agents implement Concrete Adapters, In-Memory Adapters, and parametrized `pytest` contract
  test suites across disjoint file boundaries.
---

# Python Adapter, Interfacing & Software Design Patterns SOP (`python-design-patterns`)

This skill defines the production-grade methodology for refactoring and architecting Python codebases using idiomatic **Adapter**, **Interfacing (`Protocol` / `ABC`)**, **Facade**, **Strategy**, **Factory/Registry**, **Decorator/Proxy**, **Shared IR Pipeline**, and **Control-Plane/Data-Plane Bridge** patterns under the **Elephant-Goldfish Model (EGM)**:
- **The Elephant (Persistent Main Thread — Boundary Architect & Contract Locker)**: Audits coupling via parallel read-only scouts, evaluates pattern trade-offs (rejecting speculative Java-style over-engineering), and locks pure domain DTOs (`domain/models.py`) and narrow Port interfaces (`domain/ports.py`).
- **Parallel Goldfish Implementers (Zero-Context Sub-Agents)**: Read the canonical code blueprints in [`references/code_blueprints.md`](./references/code_blueprints.md) and implement Concrete Adapters, Deterministic `InMemory` Adapters, and Parametrized `pytest` Contract Suites **in parallel across mutually exclusive file boundaries ($S_1 \cap S_2 \cap S_3 = \emptyset$)**.

---

## 0. When to Read `references/code_blueprints.md`

All complete Before/After Python code blueprints are stored in **[`references/code_blueprints.md`](./references/code_blueprints.md)**. Goldfish implementers **MUST** read the relevant section before writing code:

| Section in `references/code_blueprints.md` | Pattern Blueprint | Target Files |
| :--- | :--- | :--- |
| **`## 4.1 The Adapter Pattern + Anti-Corruption Layer (Before vs. After)`** | Pure DTOs, `@runtime_checkable Protocol`, Concrete S3/Vendor Adapter (ACL), & `InMemory` Adapter | `domain/models.py`, `domain/ports.py`, `adapters/*.py` |
| **`## 4.2 Control-Plane Catalog vs. Data-Plane Compute Bridge (Preventing God Dataset Classes)`** | Separating MLOps `Catalog` facade from native `torch.utils.data.Dataset` / archive exports | `catalog.py`, `adapters/dataset_adapter.py` |
| **`## 4.3 Thread-Safe ContextVar Isolation & Compile-Time vs. Runtime Separation`** | `ContextVar(..., default=None)` trace scopes & compile-time vs. fail-fast runtime argument binding | `core/context.py`, `compiler/binding.py` |
| **`## 4.4 Bidirectional Boundary Hygiene: Generic Rule Predicates & Shared IR Enrichment`** | Domain-agnostic `MetricThresholdPredicate` & format-agnostic `.json`/`.yaml` IR enrichment | `domain/predicates.py`, `compiler/ir_passes.py` |
| **`## 4.5 Transparent Proxy, Type-Safe Registry, & Cached Telemetry Facade`** | `CachedMeterTracker` (`_gauges.setdefault`) & runtime W3C `trace_id` resolution | `telemetry/tracker.py` |
| **`## 4.6 Workspace-Anchored Module Resolution (Supporting PEP 420 Namespace Packages)`** | Canonical dotted module path loader (`spec_from_file_location` without `"dynamic_module"`) | `cli/loader.py` |
| **`## 4.7 Parametrized Contract Testing Pattern (pytest)`** | Identical behavioral `pytest` contract suite verifying LSP parity across `InMemory` and Concrete adapters | `tests/contract/test_*_contract.py` |

---

## 1. Core Architectural Principles

1. **Program to Interfaces with Zero Adapter Bypass (DIP, ISP & Strict LSP)**:
   - Core business and orchestration logic must **never** import or depend directly on concrete third-party vendor SDKs (`boto3`, `google.cloud`, `fiftyone`, `openai`, `psycopg2`, `httpx`), raw DB cursors, or external schemas.
   - Define small, role-specific interfaces (**Ports**) using `typing.Protocol` or `abc.ABC`.
   - **Never Bypass the Injected Port**: Once a class accepts `self._adapter`, every operation must route strictly through `self._adapter`. Never import the vendor library inside the host class, and **never** use `if hasattr(self._adapter, "method"):` to silently skip operations when an `InMemory` adapter is active.

2. **Bidirectional Boundary Hygiene — Zero Downward Vendor Leakage & Zero Upward Consumer Leakage (ACL & OCP)**:
   - **Downward Anti-Corruption Layer (ACL)**: Adapters must never return raw vendor SDK objects, untyped `dict[str, Any]` payloads, or vendor exceptions across a Port boundary. Translate responses into immutable domain models (`@dataclass(frozen=True, slots=True)`) and chain exceptions (`raise DomainError(...) from exc`).
   - **Upward Domain Independence (SDKs & Shared Frameworks)**: Reusable platform SDKs, compilers, and evaluators must have **zero knowledge** of specific downstream consumer applications. Never hardcode consumer-specific parameter names, business metrics, table URIs, or fallback constants inside a core library; expose generic predicates (`MetricThresholdPredicate`) and dynamic signature inspection.

3. **Control-Plane vs. Data-Plane Separation & Ecosystem Protocol Reuse (ISP & Anti-Monolith)**:
   - **Do Not Reinvent Ecosystem Protocols**: Never build custom multi-tier SDK inheritance trees (`Dataset -> ImageDataset -> CustomDataset`) when standard ecosystem protocols (`torch.utils.data.Dataset`, `pandas.DataFrame`, `collections.abc.Iterable`, `io.BufferedIOBase`) already own the data-plane compute contract.
   - **Separate Catalog from Compute**: Keep control-plane concerns (ingestion, snapshot sync, metadata curation) in a focused `Catalog` class backed by a Port, and hand off to compute via explicit bridge methods (`.to_torch_dataset()`, `.to_dataframe()`, `.export_archive()`).
   - **PEP 562 Lazy Loading for Heavy Extras**: Isolate heavy optional dependencies (CUDA/GPU, vision frameworks, cloud SDKs) behind `pyproject.toml` extras and module-level `__getattr__` lazy imports.

4. **Producer-Consumer & Multi-Target Symmetry via Shared IR (LSP & SRP)**:
   - **Single Source of Truth for Emitter-Receiver Contracts**: Define shared CLI flags, env vars, `#sub_key` selectors, and `--xcom_out` contracts in one shared helper so compiler emission and runtime runner parsing never drift.
   - **Format-Agnostic In-Memory IR Passes**: Execute all enrichment, parameter binding, type synchronization, and telemetry injection passes on the **shared in-memory IR dict** before final serialization to `.json` or `.yaml`—never branch enrichment logic on file extensions.

5. **Strict Temporal & Concurrency Isolation (`ContextVar` Over Globals)**:
   - **Zero Mutable Module Globals**: Never store active tracing state, DAG builders, or task registries in mutable module-level globals (`_ACTIVE_CONTEXT = None`, `_REGISTERED_ITEMS = []`). Always use `contextvars.ContextVar("name", default=None)` and allocate fresh containers inside a `@contextmanager` entrypoint.
   - **Compile-Time Symbolic Tracing vs. Runtime Fail-Fast Execution**: Runtime execution must validate required arguments upfront and fail fast with `TypeError`/`ValueError`—**never** silently inject `"mock_<param>"` strings during real execution.
   - **Runtime Identity Precedence**: Derive execution/trace IDs lazily at runtime from orchestrator environment variables (`AIP_PIPELINE_RUN_ID`, `KFP_RUN_ID`, `WORKFLOW_ID`) before static compile-time defaults.

6. **Single-Provider Facade Consolidation & Instrument Caching (SRP)**:
   - Refactor duplicate observability/config modules into thin **Facades** delegating to a single canonical provider instance, and cache stateful OpenTelemetry instruments (`self._gauges.setdefault(name, meter.create_gauge(name))`).

7. **Canonical Module Identity & Customer-Ready Verification**:
   - Dynamic CLI loaders (`importlib.util.spec_from_file_location`) must resolve the canonical dotted module path relative to workspace root markers (`pyproject.toml`, `setup.py`, `.git`)—supporting PEP 420 namespace directories—rather than registering `"dynamic_module"`.
   - Every Port and Adapter must pass strict static type checking (`mypy` / `pyright`) and parametrized `pytest` contract suites across both `InMemory` and `Concrete` adapters.

---

## 2. Elephant & Parallel Goldfish Refactoring Lifecycle

```
[Phase 1: Parallel Goldfish Coupling, Leakage & Symmetry Audit (3 Read-Only Scouts)]
      │  • Scout 1A: Downward vendor SDK imports, adapter bypasses & hasattr() silent skips
      │  • Scout 1B: Upward consumer-app domain leaks & producer/consumer IR format drift
      │  • Scout 1C: Mutable module globals, uncached OTel gauges & God Dataset classes
      ▼
[Phase 2 & 3: Elephant Pattern Selection & Domain Port Contract Lock (Main Thread)]
      │  • Evaluate pattern need against Secondary Operational Trade-offs (Anti-Bloat Gate)
      │  • Author & lock pure domain DTOs (`domain/models.py`) and narrow Ports (`domain/ports.py`)
      │  • Partition implementation into 3 disjoint Goldfish file slices (S1 ∩ S2 ∩ S3 = ∅)
      ▼
[Phase 4 & 5: Parallel Zero-Context Goldfish Implementation Wave (3 Concurrent Agents)]
      │  • Goldfish 4A (S1): Concrete Vendor Adapter (ACL) + DI/ContextVar/Facade wiring
      │  • Goldfish 4B (S2): Deterministic Zero-Dependency InMemory/Fake Adapter
      │  • Goldfish 4C (S3): Parametrized pytest LSP Contract Suite (`tests/contract/...`)
      ▼
[Phase 6: Synchronization Barrier, Static Typecheck & Contract Verification]
         • Run parametrized pytest contract suite across InMemory & Concrete adapters
         • Verify 0 mypy/pyright/ruff errors and 100% Pre-Delivery Checklist compliance
```

---

## 3. Pattern Selection Matrix & Secondary Operational Trade-offs (Elephant Gate)

### 3.1 Interfacing: `typing.Protocol` vs `abc.ABC` vs `Callable` vs Ecosystem Base

| Mechanism | Subtyping Model | Best Used When | Avoid When |
| :--- | :--- | :--- | :--- |
| **`typing.Protocol`** *(Recommended Default)* | **Structural** (Static Duck Typing) | Decoupling callers from implementations without forcing inheritance; adapting third-party/test classes; keeping dependencies zero-coupled. | Shared concrete base state or template methods are required across all implementations. |
| **`abc.ABC` + `@abstractmethod`** | **Nominal** (Explicit Inheritance) | Enforcing a **Template Method** pattern where base class provides shared lifecycle/validation logic and subclasses implement hooks (`_execute()`). | Implementations have no shared state or come from external packages you do not control. |
| **`collections.abc.Callable`** | **Functional** | The interface only has a single method (`execute`/`__call__`) and holds no lifecycle state (e.g., retry backoff, metric predicate, pure IR pass). | The component requires setup/teardown (`close()`) or multiple coordinated methods. |
| **Native Ecosystem ABC** (`torch.utils.data.Dataset`, `io.IOBase`) | **Ecosystem Standard** | Interfacing with data loaders, tensor pipelines, or standard library streams that check `isinstance()` or expect native dunder semantics. | Building an MLOps control-plane catalog (use a Catalog class with a `.to_<ecosystem>()` bridge method instead). |

### 3.2 Software Design Patterns Catalog & Secondary Trade-offs (TRIZ Discipline)

Every architectural pattern introduces operational trade-offs. The Elephant **must** verify that the code smell warrants the secondary trade-off before adding a pattern:

| Pattern Name | Code Smell Detected in Source | Refactoring Target (`references/code_blueprints.md`) | Secondary Operational Trade-off (When NOT to Use) |
| :--- | :--- | :--- | :--- |
| **Object Adapter (ACL)** | Business logic calls external SDKs directly, or host class bypasses `self._adapter` via direct vendor imports / `hasattr()` checks. | Move vendor calls behind a `Protocol` Port implemented with 100% parity by `ConcreteAdapter` and `InMemoryAdapter` (`§4.1`). | Adds DTO mapping and dual-adapter maintenance; do not wrap stable Python stdlib primitives (`pathlib`, `json`). |
| **Control-Plane Catalog + Compute Bridge** | A 500+ line `Dataset` or `Table` class mixes metadata sync, cloud I/O, and broken `__getitem__`/`__len__` dunders. | Scope class to a `Catalog` facade backed by `AdapterPort`, exposing `.to_torch_dataset()` / `.export_archive()` bridges (`§4.2`). | Requires explicit handoff step between curation and training; unnecessary for pure in-memory array transforms. |
| **Single-Provider Facade** | Multiple modules instantiate separate `TracerProvider`, `Config`, or `Client` singletons, causing split brain. | Turn secondary modules into thin Facades delegating to the canonical provider; cache metric gauges (`§4.5`). | Indirection hop in legacy callers; remove deprecated facade aliases once downstream migrations finish. |
| **Decorator / Proxy** | Retry loops, logging, instrument caching, or auth checks are copy-pasted inside every business or adapter method. | Create a wrapper class implementing the same `Protocol` that delegates to an inner `Protocol` instance (`§4.5`). | Deeper call stack during debugging; keep decorator chains shallow (<= 2 layers). |
| **Bridge** | Cartesian product of classes (`JsonGcsExporter`, `ParquetGcsExporter`, `JsonS3Exporter`, `ParquetS3Exporter`). | Split into two orthogonal `Protocol` hierarchies: `FormatterPort` and `StorageTransportPort` composed via DI. | Two constructor dependencies instead of one; overkill when only 1 format and 1 transport exist. |
| **Factory / Plugin Registry** | Sprawling `if provider == "gcp": ... elif provider == "aws": ...` blocks scattered across multiple files. | Centralize instantiation in a type-safe Registry/Factory mapping config keys/enums to Adapter constructors. | Indirection when jumping to concrete implementation in IDEs; do not use for a single concrete implementation. |
| **Generic Specification / Predicate** | Core SDK or evaluator hardcodes consumer-specific domain thresholds (`max_forecast_rmse`, `custom_threshold_1`). | Replace hardcoded domain fields with generic `MetricThresholdPredicate(name, threshold, op)` (`§4.4`). | Requires caller configuration at composition root. |
| **Shared IR Pipeline** | `.json` and `.yaml` compilers diverge in feature support, or compiler CLI flags drift from runtime runner parser flags. | Run pure `dict -> dict` enrichment passes on the shared in-memory IR before format serialization (`§4.4`). | Requires strict schema discipline on the in-memory IR dictionary. |
| **Context-Scoped State (`ContextVar`)** | Module-level globals (`_ACTIVE_DAG = None`, `_TASKS = []`) corrupt state under multi-threading or async execution. | Encapsulate ambient state in `ContextVar(..., default=None)` managed via a `@contextmanager` (`§4.3`). | Implicit context propagation across thread pools requires `contextvars.copy_context().run(...)`. |

---

## 4. Pre-Delivery Customer Readiness Checklist

Before completing any refactoring task or handing code off to the customer, verify every item:

1. **Bidirectional Boundary Hygiene (DIP, OCP & ACL)**:
   - [ ] Are all third-party vendor imports confined strictly to `adapters/` or `infrastructure/` modules (with lazy PEP 562 imports for heavy optional extras)?
   - [ ] Is the core library/SDK 100% free of hardcoded parameter names, table URIs, metric names, or fallback constants belonging to a specific downstream consumer application?
   - [ ] Are all vendor exceptions caught at the adapter boundary and re-raised as domain exceptions using `raise DomainError(...) from exc`?
2. **Strict Interface Segregation & Adapter Parity (ISP & LSP)**:
   - [ ] Are `Protocol` / `ABC` interfaces narrow and role-specific, delegating compute iteration to native ecosystem protocols (`torch.utils.data.Dataset`, `DataFrame`) instead of custom monoliths?
   - [ ] Does the host class route 100% of operations through `self._adapter` with **zero** direct vendor library calls and **zero** `if hasattr(self._adapter, ...):` silent no-op fallbacks?
3. **Producer-Consumer & Multi-Target Symmetry (If Authoring Multi-Target Compilers / IR Exporters)**:
   - [ ] Do all compilers/exporters mutate a shared in-memory IR dictionary (synchronizing component and root parameter types) before serializing to `.json` or `.yaml`?
   - [ ] Does every compiler emit the exact CLI arguments, sub-key selectors, output flags, and shared mounts expected by the runtime runner?
4. **Concurrency, Temporal Isolation & Telemetry Hygiene**:
   - [ ] Are all module-level mutable trace/context globals replaced with `contextvars.ContextVar(..., default=None)` that allocate fresh containers per scope?
   - [ ] Does runtime execution fail fast with `TypeError` on missing required parameters (zero `"mock_<param>"` injection) and invoke argument type validation?
   - [ ] Are overlapping observability/config modules unified via a thin Facade over a single provider, with cached metric instruments (`self._gauges.setdefault(...)`) and runtime-derived trace IDs?
5. **Static Type Checking, Canonical Imports & Contract Tests**:
   - [ ] Do CLI file loaders resolve canonical dotted module paths from workspace root markers (supporting PEP 420 namespaces) instead of `"dynamic_module"`?
   - [ ] Does `mypy` / `pyright` pass with **0 errors**, and do parametrized `pytest` contract suites pass with **0 failures** (without `autouse=True` global mocks hiding broken integrations)?
