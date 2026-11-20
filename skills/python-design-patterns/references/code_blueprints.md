# Python Design Patterns — Reference Code Blueprints

This reference contains the canonical Before/After implementation blueprints for [`python-design-patterns`](../SKILL.md). Goldfish implementation sub-agents must read the relevant section of this file whenever an Elephant Implementation Contract specifies one of these patterns.

---

## 4.1 The Adapter Pattern + Anti-Corruption Layer (Before vs. After)

### ❌ BEFORE: Tightly Coupled, Untestable, Leaky Vendor Code
```python
# ❌ BAD: Direct vendor SDK import, hardcoded client creation, raw dict return,
# and unmapped third-party exceptions leaking into core business logic.
import boto3


class InvoiceProcessor:
    def __init__(self, bucket_name: str) -> None:
        self.s3 = boto3.client("s3")
        self.bucket_name = bucket_name

    def archive_invoice(self, invoice_id: str, payload: bytes) -> dict:
        response = self.s3.put_object(
            Bucket=self.bucket_name,
            Key=f"invoices/{invoice_id}.pdf",
            Body=payload,
            ContentType="application/pdf",
        )
        return {"etag": response["ETag"], "status": response["ResponseMetadata"]["HTTPStatusCode"]}
```

### ✅ AFTER: Clean Port (`Protocol`), Domain DTOs, Concrete Adapter (ACL), & Fake Adapter

```python
# 1. domain/models.py — Pure Domain DTOs & Exceptions (Zero external dependencies)
from dataclasses import dataclass


class StorageError(Exception):
    """Base domain exception for all storage adapter failures."""


class ObjectNotFoundError(StorageError):
    """Raised when a requested artifact does not exist."""


@dataclass(frozen=True, slots=True)
class StoredArtifactResult:
    object_key: str
    checksum_etag: str
    size_bytes: int
```

```python
# 2. domain/ports.py — Narrow Interface Contract via typing.Protocol
from typing import Protocol, runtime_checkable
from .models import StoredArtifactResult


@runtime_checkable
class ArtifactStoragePort(Protocol):
    """Port defining the contract for storing and retrieving binary artifacts."""

    def put_artifact(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> StoredArtifactResult:
        """Persist binary artifact and return canonical domain metadata."""
        ...

    def get_artifact(self, key: str) -> bytes:
        """Retrieve raw artifact bytes by key or raise ObjectNotFoundError."""
        ...
```

```python
# 3. adapters/s3_storage_adapter.py — Concrete Object Adapter with Anti-Corruption Layer
from typing import Any
from domain.models import ObjectNotFoundError, StorageError, StoredArtifactResult


class S3ArtifactStorageAdapter:
    """Adapts an AWS boto3 S3 client to the domain ArtifactStoragePort."""

    def __init__(self, s3_client: Any, bucket_name: str) -> None:
        self._client = s3_client
        self._bucket = bucket_name

    def put_artifact(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> StoredArtifactResult:
        try:
            response = self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
            raw_etag = str(response.get("ETag", "")).strip('"')
            return StoredArtifactResult(
                object_key=key,
                checksum_etag=raw_etag,
                size_bytes=len(data),
            )
        except Exception as exc:
            raise StorageError(f"Failed to store artifact '{key}' in bucket '{self._bucket}'") from exc

    def get_artifact(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return bytes(response["Body"].read())
        except Exception as exc:
            error_code = getattr(exc, "response", {}).get("Error", {}).get("Code")
            if error_code in ("NoSuchKey", "404"):
                raise ObjectNotFoundError(f"Artifact '{key}' not found in '{self._bucket}'") from exc
            raise StorageError(f"Failed to fetch artifact '{key}' from '{self._bucket}'") from exc
```

```python
# 4. adapters/memory_storage_adapter.py — Deterministic In-Memory Adapter for Testing & Local Dev
import hashlib
from domain.models import ObjectNotFoundError, StoredArtifactResult


class InMemoryArtifactStorageAdapter:
    """Zero-dependency in-memory adapter implementing ArtifactStoragePort."""

    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    def put_artifact(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> StoredArtifactResult:
        self._store[key] = data
        etag = hashlib.md5(data).hexdigest()  # noqa: S324
        return StoredArtifactResult(object_key=key, checksum_etag=etag, size_bytes=len(data))

    def get_artifact(self, key: str) -> bytes:
        if key not in self._store:
            raise ObjectNotFoundError(f"Artifact '{key}' not found in memory store")
        return self._store[key]
```

---

## 4.2 Control-Plane Catalog vs. Data-Plane Compute Bridge (Preventing God `Dataset` Classes)

Never conflate MLOps control-plane management (curation, remote sync, lineage) with data-plane sample iteration (`__getitem__`, `__len__`), and never bypass `self._adapter` with direct vendor calls or `hasattr()` checks:

```python
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Protocol


@dataclass(frozen=True, slots=True)
class SampleRecord:
    uri: str
    split: str = "train"
    annotations: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class DatasetAdapterPort(Protocol):
    """Vendor-neutral Port for dataset curation and native compute handoff."""

    def add_samples(self, samples: Sequence[SampleRecord]) -> int: ...
    def import_from_dir(self, dir_path: Path, split: str = "train") -> int: ...
    def to_torch_dataset(
        self,
        split: str | None = None,
        transforms: Callable[[Any], Any] | None = None,
    ) -> Any: ...
    def export_archive(
        self,
        export_dir: Path,
        fmt: Literal["yolov5", "coco"] = "yolov5",
        splits: Sequence[str] | None = None,
    ) -> Path: ...


class VisionDatasetCatalog:
    """Control-plane catalog facade delegating 100% of operations through DatasetAdapterPort."""

    def __init__(self, name: str, adapter: DatasetAdapterPort) -> None:
        self.name = name
        self._adapter = adapter

    def register_samples(
        self,
        raw_records: Sequence[dict[str, Any]],
        default_metadata: dict[str, Any] | None = None,
    ) -> int:
        base_meta = dict(default_metadata or {})
        samples = [
            SampleRecord(
                uri=str(r["uri"]),
                split=str(r.get("split", "train")),
                annotations=dict(r.get("annotations", {})),
                metadata={**base_meta, **dict(r.get("metadata", {}))},
            )
            for r in raw_records
        ]
        return self._adapter.add_samples(samples)

    def to_torch_dataset(
        self,
        split: str | None = None,
        transforms: Callable[[Any], Any] | None = None,
    ) -> Any:
        """Hand off to a genuine torch.utils.data.Dataset for DataLoader consumption."""
        return self._adapter.to_torch_dataset(split=split, transforms=transforms)

    def export_archive(
        self,
        export_dir: str | Path,
        fmt: Literal["yolov5", "coco"] = "yolov5",
        splits: Sequence[str] | None = None,
    ) -> Path:
        """Export directory structure required by external CLI trainers (e.g., YOLO, RF-DETR)."""
        return self._adapter.export_archive(Path(export_dir), fmt=fmt, splits=splits)
```

---

## 4.3 Thread-Safe `ContextVar` Isolation & Compile-Time vs. Runtime Separation

Never use mutable module-level globals (`_ACTIVE_DAG = None`, `_TASKS = []`) or inject `"mock_<param>"` strings when required arguments are missing at runtime:

```python
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
import inspect
from typing import Any, Callable


@dataclass
class TraceRecordingScope:
    """Isolated per-context state allocated freshly on each trace session."""

    tasks: list[str] = field(default_factory=list)
    symbolic_params: dict[str, str] = field(default_factory=dict)


# Always initialize ContextVar with default=None — never a mutable list/dict!
_ACTIVE_TRACE_SCOPE: ContextVar[TraceRecordingScope | None] = ContextVar(
    "_ACTIVE_TRACE_SCOPE", default=None
)


@contextmanager
def compiler_trace_context() -> Iterator[TraceRecordingScope]:
    """Thread-safe and async-safe context manager for symbolic compile-time tracing."""
    scope = TraceRecordingScope()
    token = _ACTIVE_TRACE_SCOPE.set(scope)
    try:
        yield scope
    finally:
        _ACTIVE_TRACE_SCOPE.reset(token)


def bind_pipeline_arguments(
    func: Callable[..., Any],
    provided_kwargs: dict[str, Any],
    *,
    allow_symbolic_placeholders: bool,
) -> dict[str, Any]:
    """Bind arguments strictly at runtime, or inject symbolic placeholders only during compile."""
    sig = inspect.signature(func)
    bound: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        if name in provided_kwargs:
            bound[name] = provided_kwargs[name]
        elif param.default is not inspect.Parameter.empty:
            bound[name] = param.default
        elif allow_symbolic_placeholders:
            bound[name] = f"{{{{$.inputs.parameters['{name}']}}}}"
        else:
            # Fail fast at runtime — NEVER inject "mock_<name>" into production/local execution!
            raise TypeError(f"Missing required pipeline parameter: '{name}'")
    return bound
```

---

## 4.4 Bidirectional Boundary Hygiene: Generic Rule Predicates & Shared IR Enrichment

Keep core evaluators and compilers 100% closed to downstream application domain leakage by using generic predicates and format-agnostic IR passes:

```python
from collections.abc import Mapping
from dataclasses import dataclass
import operator
from typing import Any, Literal

_OPS = {
    "le": operator.le,
    "lt": operator.lt,
    "ge": operator.ge,
    "gt": operator.gt,
    "eq": operator.eq,
}


@dataclass(frozen=True, slots=True)
class MetricThresholdPredicate:
    """Domain-agnostic stage-gate predicate so consuming apps inject their own metrics."""

    metric_name: str
    threshold: float
    comparison: Literal["le", "lt", "ge", "gt", "eq"] = "le"

    def evaluate(self, metrics: Mapping[str, float]) -> bool:
        if self.metric_name not in metrics:
            raise KeyError(f"Required gate metric '{self.metric_name}' missing from evaluation.")
        return bool(_OPS[self.comparison](metrics[self.metric_name], self.threshold))


def enrich_pipeline_ir_dict(
    ir_spec: dict[str, Any],
    declared_params: Mapping[str, tuple[str, Any]],
    task_param_bindings: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    """Mutate the in-memory IR dict for BOTH .json and .yaml targets with type synchronization."""
    root_params = ir_spec.setdefault("root", {}).setdefault("inputDefinitions", {}).setdefault("parameters", {})
    for param_name, (kfp_type, default_val) in declared_params.items():
        root_params[param_name] = {"parameterType": kfp_type, "defaultValue": default_val}

    tasks = ir_spec["root"].setdefault("dag", {}).setdefault("tasks", {})
    components = ir_spec.setdefault("components", {})

    for task_name, bindings in task_param_bindings.items():
        if task_name not in tasks:
            continue
        task_spec = tasks[task_name]
        comp_name = task_spec.get("componentRef", {}).get("name", "")
        task_inputs = task_spec.setdefault("inputs", {}).setdefault("parameters", {})

        for arg_name, root_param_name in bindings.items():
            task_inputs[arg_name] = {"componentInputParameter": root_param_name}
            if comp_name in components and root_param_name in root_params:
                comp_params = (
                    components[comp_name]
                    .setdefault("inputDefinitions", {})
                    .setdefault("parameters", {})
                )
                if arg_name in comp_params:
                    comp_params[arg_name]["parameterType"] = root_params[root_param_name]["parameterType"]

    return ir_spec
```

---

## 4.5 Transparent Proxy, Type-Safe Registry, & Cached Telemetry Facade

```python
import hashlib
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class CachedMeterTracker:
    """Caches OpenTelemetry gauge instruments instead of recreating them on every log_metric call."""

    def __init__(self, meter: Any) -> None:
        self._meter = meter
        self._gauges: dict[str, Any] = {}

    def log_metric(self, key: str, value: float, attributes: dict[str, str] | None = None) -> None:
        gauge = self._gauges.setdefault(key, self._meter.create_gauge(key))
        gauge.set(value, attributes=attributes or {})


def resolve_runtime_trace_id(
    env: dict[str, str] | None = None,
    run_id_keys: tuple[str, ...] = ("AIP_PIPELINE_RUN_ID", "KFP_RUN_ID", "WORKFLOW_ID", "MLOPS_RUN_ID"),
) -> str | None:
    """Derive a deterministic 32-hex-char W3C trace_id from runtime run IDs before static env vars."""
    environ = env if env is not None else os.environ
    for key in run_id_keys:
        raw_val = environ.get(key, "").strip()
        if raw_val and not (raw_val.startswith("{{") and raw_val.endswith("}}")):
            return hashlib.sha256(raw_val.encode("utf-8")).hexdigest()[:32]
    return None
```

---

## 4.6 Workspace-Anchored Module Resolution (Supporting PEP 420 Namespace Packages)

```python
import importlib.util
import os
from pathlib import Path
import sys
from types import ModuleType

_WORKSPACE_MARKERS = ("pyproject.toml", "mlops_config.yaml", "setup.py", ".git")


def load_module_with_canonical_path(file_path: str | Path) -> tuple[ModuleType, str]:
    """Import a Python file under its canonical workspace dotted path (PEP 420 compatible)."""
    abs_file = Path(file_path).resolve()
    search_dir = abs_file.parent
    workspace_root: Path | None = None

    for candidate in (search_dir, *search_dir.parents):
        if any((candidate / marker).exists() for marker in _WORKSPACE_MARKERS):
            workspace_root = candidate
            break

    if workspace_root is None:
        cwd = Path(os.getcwd()).resolve()
        workspace_root = cwd if abs_file.is_relative_to(cwd) else abs_file.parent

    rel_parts = abs_file.relative_to(workspace_root).with_suffix("").parts
    module_name = ".".join(rel_parts)

    root_str = str(workspace_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    spec = importlib.util.spec_from_file_location(module_name, str(abs_file))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module specification from '{abs_file}'")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module, module_name
```

---

## 4.7 Parametrized Contract Testing Pattern (`pytest`)

Every Port (`Protocol` or `ABC`) and multi-target Compiler must have a **Contract Test Suite** running identical behavioral assertions across all implementations to guarantee Liskov Substitution Principle (LSP) compliance:

```python
import pytest
from adapters.memory_storage_adapter import InMemoryArtifactStorageAdapter
from domain.models import ObjectNotFoundError
from domain.ports import ArtifactStoragePort


@pytest.fixture(params=["memory"])
def storage_adapter(request: pytest.FixtureRequest) -> ArtifactStoragePort:
    if request.param == "memory":
        return InMemoryArtifactStorageAdapter()
    raise ValueError(f"Unknown adapter fixture: {request.param}")


def test_storage_port_roundtrip_contract(storage_adapter: ArtifactStoragePort) -> None:
    payload = b"customer-invoice-content"
    result = storage_adapter.put_artifact("invoices/001.pdf", payload, content_type="application/pdf")

    assert result.object_key == "invoices/001.pdf"
    assert result.size_bytes == len(payload)
    assert result.checksum_etag != ""
    assert storage_adapter.get_artifact("invoices/001.pdf") == payload


def test_storage_port_missing_key_raises_domain_error(storage_adapter: ArtifactStoragePort) -> None:
    with pytest.raises(ObjectNotFoundError):
        storage_adapter.get_artifact("non-existent/key.pdf")
```
