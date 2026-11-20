---
name: python-readability
description: >-
  Checks and enforces Python readability, style, testing, typing, code-density,
  and packaging standards across .py, test_*.py / *_test.py, and project
  configuration files. Use when authoring, refactoring, reviewing, or
  pre-checking Python code, unit tests, CLI binaries, or packaging config for
  readability compliance, graduating experimental code to production, or
  evaluating Python code size and density. Don't use for non-Python languages,
  large-scale automated cross-file renames, or general CI failures unrelated to
  Python.
metadata:
  icon: 🐍
---

# Python Readability Check

Self-contained specification and checklist for agents authoring, reviewing, or
pre-checking Python code, unit tests, CLI entry points, and project packaging
against the Google Python Style Guide and Python readability best practices.

**Core principle:** *"Optimize for readability, not conciseness."* Prefer clear,
explicit, unit-testable code over clever one-liners, while eliminating redundant
boilerplate.

## 1. Agent Check Workflow

When checking a file, diff, or pull request (PR):

1.  **Check Scope & Exemptions First**:
    -   Enforced by default across production Python source and test trees.
    -   Exempt paths: vendored/third-party directories (e.g., `vendor/`,
        `third_party/`) and explicitly excluded experimental or scratch
        subtrees.
    -   **Moves from exempt paths**: Files moved or copied out of
        `experimental/`, `prototypes/`, `scratch/`, or notebooks into
        production paths have not had readability review — inspect the
        **entire file** as new code.
    -   **Ineligible for formal readability review**: Throwaway prototypes and
        Jupyter/Colab notebooks (`.ipynb`).
    -   **PR / diff readiness**: Changes should be small and self-contained,
        with clear descriptions and passing CI/tests.
2.  **Inspect Project Packaging & Tooling Config**:
    -   Whenever reviewing a change touching `.py` files, inspect
        `pyproject.toml` (or `setup.cfg` / `requirements*.txt`) when present to
        verify declared dependencies, Python version constraints, and
        linter/type-checker settings (`ruff`, `mypy`, `pyright`, `pytest`).
    -   Respect explicit repository-level linter/formatter settings (such as line
        length `88`/`100` or established symbol imports in existing modules)
        where local consistency outweighs strict defaults.
3.  **Distinguish Severity & Cite Sources**:
    -   Classify findings as **`required`** (blocking style, correctness,
        missing tests/docstrings, packaging/import/reproducibility defects) or
        **`optional`** (idiomatic improvements, minor cleanups).
    -   Cite the relevant rule or style section (e.g., Google Python Style Guide
        §3.2) for each finding.
    -   Re-check any suggested code rewrite against every rule below before
        posting it.

## 2. Size, Granularity, and Code Density

| Granularity | Threshold / Rule | Guidance & Rationale |
| :--- | :--- | :--- |
| **Module / `.py` file** | No hard line limit; group by cohesion | Do not enforce one class per file (§3.16.2). Place related classes and functions together, but **separate library logic from CLI entry points**. |
| **Function length** | ~40 lines | Prefer small, focused functions (§3.18). Consider splitting above ~40 lines unless splitting harms structure. |
| **`main()` entry point** | < ~15 lines | Keep `main()` thin: parse/validate CLI arguments, initialize top-level deps, and delegate orchestration to testable functions. |
| **`try` block body** | Minimal lines | Wrap only the statements expected to raise (§2.4.4) so unexpected exceptions are not masked. |
| **Test method** | 1 behavior (~2–3 assertions max) | Each `test_*` function/method tests one thing. Use structured equality, `@pytest.mark.parametrize`, or `self.subTest()` instead of many assertions. |
| **Line length** | **80 characters max** (or project-configured limit) | Strict limit (§3.2), including docstrings (respect `pyproject.toml` if the repo configures 88/100). Exceptions: long imports, URLs/pathnames in comments, long whitespace-free string literals, `# pylint: disable=...` / `# noqa` / `# type: ignore`. |
| **PR / commit size** | Small & self-contained | Split unrelated logical changes into separate commits or PRs. |

### Where NOT to Over-Condense (Reject "Code Golf")

-   **Comprehensions & generators (§2.7.4, `required`)**: Allow **at most one
    `for` clause**. Multiple `for` clauses or complex filter chains are
    forbidden — use explicit nested `for` loops.
-   **Conditional expressions / ternaries (§2.11.4, `required`)**: Allowed only
    when each part (`true_expr`, `if cond`, `else false_expr`) fits on one line
    (`<= 3` lines total, never nested). Otherwise use `if`/`else`.
-   **Lambdas (§2.10.4)**: Simple single-line expressions only (avoid multi-line
    or > 60–80 char lambdas; use a `def` or `operator` module functions).
-   **One statement per line (§3.1, §3.13, §3.14, `required`)**: No semicolons
    (`;`), no comma-separated imports (`import os, sys`), and no parenthesized
    multi-line module imports. Single-line `if cond: action()` is allowed only
    with no `else` clause (never for `try`/`except`).
-   **Tuple unpacking over magic indexes**: Unpack sequences into named
    variables (`first_x, first_y = first_point` or `x, y, *_ = items`) instead
    of indexing `point[0]`, `point[1]` or slicing `items[:2]`.
-   **Descriptive names over abbreviations (§3.16.1)**: Never drop letters to
    shorten names (avoid `f_path`, `usr_ct`, `res`, `resp`, `val`, `obj`).
    Single-char names are disallowed except `i`, `j`, `k` (short loops), `e`
    (exceptions), `f` (file objects), `_T`/`_P` (unconstrained `TypeVar`/
    `ParamSpec`), or cited math formulas.
-   **No "power features" (§2.19)**: Avoid `getattr`, `hasattr`, `__dict__`
    reflection on known types, custom metaclasses, or import hacks. Use
    `isinstance` and explicit typed attributes.

### Where to Condense (Eliminate Boilerplate)

-   **Direct returns & yields**: Return or yield expressions directly instead of
    assigning a temporary variable on the preceding line.
-   **Implicit truthiness (§2.14.4)**: Use `if not users:` instead of
    `if len(users) == 0:` or `if users == []:`. Always use `is None` /
    `is not None` when testing specifically for `None`. *(Exception: if using
    Protobuf, never use truthiness on singular submessages — use
    `msg.HasField('sub_msg')`.)*
-   **Single-lookup dictionary access**: Replace
    `if key in d: v = d[key] else: v = default` with `d.get(key, default)`,
    `d.setdefault()`, `collections.defaultdict`, or `try`/`except KeyError`.
-   **Public attributes over trivial getters/setters (§2.13.4, §3.15)**: Expose
    public attributes directly (documented under `Attributes:`) rather than
    writing trivial `get_x()`/`set_x()` methods or pass-through `@property`
    wrappers. Use `@property` only for lightweight computed attributes without
    side effects.
-   **Omit redundant docstrings (§3.8.2.1, §3.8.3.1)**: Do not write docstrings
    on `test_*` functions/methods that repeat the name. Mark overridden methods
    with `@override` (`from typing import override`) and omit docstrings unless
    the contract or side effects change.

## 3. Packaging, Dependencies, & Reproducible Execution

-   **Declare direct dependencies (`required`)**: Every third-party module
    imported in production code must be declared as a direct dependency in
    `pyproject.toml` (or `requirements.txt` / `setup.cfg`). Do not rely on
    transitive dependencies.
-   **Separate dev/test dependencies (`required`)**: Keep test, lint, and
    type-check tools in `[dependency-groups]` / `[project.optional-dependencies]`
    (or `requirements-dev.txt`), not runtime dependencies.
-   **Static type checking & linting**: Configure `mypy` or `pyright` and
    `ruff` (or `flake8`/`pylint`) in `pyproject.toml`. Do not suppress type
    checks (`# type: ignore`) or lint rules (`# noqa`) without a specific error
    code and brief justification.
-   **Reproducible execution (`required`)**: Run scripts, linters, type-checkers,
    and tests inside the project's virtual environment (`uv run`, `poetry run`,
    `.venv/bin/python -m pytest`) rather than an unmanaged global Python.

## 4. Imports & Package Structure (§2.2, §3.13)

1.  **Absolute imports (`required`)**: Prefer absolute imports from the package
    root (e.g., `from my_pkg.subpkg import my_mod`). Avoid `import *`,
    `sys.path` hacks, and deep relative imports (`from ... import ...`).
2.  **Import modules, not symbols (unless repo convention overrides)**:
    -   Default to `from pkg.subpkg import module` then `module.Symbol` (or
        `import pkg.subpkg.module`).
    -   **Exemptions**: Symbols from `typing` and `collections.abc` are imported
        directly and may share one line (§3.19.12; long import lines are exempt
        from the 80-char limit). Respect established repository conventions (e.g.,
        `dataclasses`, `pydantic`, `fastapi`) when the existing codebase or
        `pyproject.toml` already imports classes/functions directly.
3.  **Single-line module imports only (§3.13, `required`)**: Put each imported
    module on its own dedicated line — never comma-separate modules or wrap them
    in parentheses (`from pkg import (mod_a, mod_b)` is bad).
4.  **Third-party imports**: Import by top-level package name (`import numpy`).
5.  **Package `__init__.py` hygiene**: Keep `__init__.py` empty or minimal
    (only explicit public API re-exports with `__all__` at the top-level
    package boundary if intended). Never put heavy runtime logic or side effects
    in `__init__.py`.
6.  **Import order** (one blank line between groups):
    `__future__` -> stdlib -> third-party -> first-party absolute imports.
7.  **No circular imports**: If `a` imports `b`, `b` must not import `a`.

## 5. Type Annotations, Constants, & Data Structures (§3.19)

-   **Public APIs (`required`)**: Annotate all parameters and return types on
    public functions, methods, and nontrivial private helpers. Do not annotate
    `self`, `cls`, or `__init__` return type. Spaces around `=` only when a
    type annotation is present (`def f(a: int = 0)` vs `def f(a=0)`).
-   **Abstract collection types (§3.19.12)**: Use `collections.abc`
    (`Sequence`, `Mapping`, `Set`, `Collection`, `Iterable`, `Callable`,
    `Generator[T, None, None]`) for **both parameters and return types**, unless
    callers specifically require mutation (`MutableSequence` / `list` / `dict`).
    Never import `typing.List`, `typing.Dict`, `typing.Tuple`, `typing.Set`,
    `typing.Type`, or `typing.AbstractSet`.
-   **Modern unions**: Use `X | None` and `A | B` rather than `Optional[X]` or
    `Union[A, B]` (use `from __future__ import annotations` if supporting
    Python < 3.10).
-   **Immutable constants (`required`, §2.5.4)**: Module/class
    `CAPS_WITH_UNDER` / `_CAPS_WITH_UNDER` constants must use immutable types
    (`tuple`, `frozenset`, `types.MappingProxyType`) instead of `list`, `set`,
    or `dict`. Replace magic literals with named constants. Do not add
    `typing.Final` unless the project explicitly requires it.
-   **Structured data over `dict[str, Any]` (`optional`)**: Avoid gratuitous
    `Any` (`dict[str, Any]`, `list[Any]`, `-> Any`) when a schema is fixed —
    use `@dataclasses.dataclass(frozen=True)`, `TypedDict`, or `NamedTuple`
    (or a descriptive `Json` alias for free-form JSON).

## 6. Documentation & Docstrings (§3.8)

-   **80-char line limit (`required`)**: Every docstring line, including the
    first summary line (ending in `.`, `?`, or `!`), must be `<= 80` chars (or
    the repo's configured limit).
-   **Module docstrings (`required`)**: Required at the top of every non-test
    module describing contents and usage (`test_*.py` / `*_test.py` exempt).
-   **Callable docstrings (`required`)**: Required for every public callable
    (**including `__init__`**, typically `"""Initializes the instance."""`) and
    nontrivial private functions. Do not repeat parameter types in `Args:`/`Returns:`
    when already in the signature.
-   **Sections**: Use `Args:`, `Returns:` (omit if always `None` or fully
    described by a `"Returns ..."` summary), `Yields:` (for generators;
    `@contextlib.contextmanager` uses `Returns:`), and `Raises:`.
-   **Document `None` (`required`)**: Whenever an arg or return type is
    `X | None`, explicitly state what passing `None` means or under what
    condition `None` is returned.
-   **Classes & dataclasses**: Describe what instances represent (not `"A class
    that..."`), and document public attributes/fields in an `Attributes:`
    section (`optional`) or prefix internal attributes with `_`.
-   **Exceptions & properties (`optional`)**: Exception docstrings describe the
    error state (`"""No more cheese is available."""`, not `"Raised when..."`).
    `@property` docstrings use noun-phrase style (`"""The user profile path."""`,
    not `"Returns..."`).

## 7. Exceptions, Control Flow, Regexes, & Idioms

-   **Naming (§3.16)**: `lower_with_under` for modules/functions/variables
    (`_internal`), `CapWords` for classes/exceptions, `CAPS_WITH_UNDER` for
    constants. Use single `_foo` (not dunder `__foo`) for private members, and
    do not encode container types in names (`user_ids`, not `user_id_list`).
-   **Exceptions (§2.4)**:
    -   Catch specific exceptions; never use bare `except:` or swallow broad
        `Exception` with `pass` (log or re-raise unless an expected narrow
        exception is explicitly justified in a comment).
    -   Preserve tracebacks with `raise NewError('...') from err`.
    -   Do not catch solely to log and re-raise (`optional`).
    -   Prefer EAFP (`try`/`except`) over LBYL (`os.access()` before `open()`).
    -   Prefer built-in exceptions (`ValueError` for invalid args); never use
        `assert` for argument validation or application logic (`optional`).
-   **Mutable default arguments (§2.12, `required`)**: Never use `[]`, `{}`, or
    `set()` as default parameter values; use `None` sentinel. Avoid
    time-dependent defaults (`time.time()`).
-   **Class & module layout**: Place `__init__` / factory `@classmethod`s at the
    top of classes (never put `_helper` methods above `__init__`). Module order:
    docstring -> `__future__` -> dunders -> imports -> constants -> classes &
    functions -> `main()` -> `if __name__ == '__main__': main()`.
-   **Nested definitions (§2.6, `required` in `src`)**: Avoid nested functions
    or classes inside production functions/methods unless closing over a local
    variable other than `self`/`cls`. Hoist to module-level `_helper` or a
    private `_method` so they are unit-testable.
-   **`@staticmethod` (§2.17)**: Discouraged — prefer module-level functions or
    `@classmethod`.
-   **Regexes**: Hoist static regexes to module-level constants
    (`_PATTERN = re.compile(r'...')`) in reusable library code or loops; keep
    one-off regexes inline in tests and one-shot scripts.
-   **Multiline string literals (§3.10, `required`)**: Never leave non-docstring
    multiline string continuation lines flush-left; indent them or use
    `textwrap.dedent("""\ ...""")`.
-   **Strings, loops, resources, & gotchas**:
    -   Format strings with f-strings, `%`, or `.format()` (never `+` loops or
        redundant `str()` inside `{...}`).
    -   Use `enumerate()`, `dict.items()`, `zip(..., strict=True)`; never
        `range(len(...))`; never reassign a loop invariant inside a loop.
    -   Consider `match`/`case` or enum dispatch over 3+ `if`/`elif` string
        checks (`optional`).
    -   Use `with` for files/resources (`contextlib.closing()` if no `__enter__`),
        `tempfile.TemporaryDirectory()` over hardcoded `/tmp` or bare `mkdtemp()`.
    -   Use `timedelta.total_seconds()` (not `.seconds`), avoid `pickle` on
        untrusted data, never `subprocess(..., shell=True)`, and wrap
        `@contextlib.contextmanager` teardown in `try`/`finally` when required.
-   **Diff hygiene (`required`)**: Delete any unused imports, variables,
    module-level classes, type aliases, constants, functions, or fields added in
    the diff.

## 8. CLI Entry Points, Arguments, & Logging

-   **Structured CLI parsing (`required`, §2.10, §3.18)**: Use `argparse`,
    `click`, or `typer` (or `absl.flags` if already used in the repo) instead of
    raw `sys.argv` indexing.
-   **Thin `main()` & decoupled logic**: Keep `main()` under ~15 lines. Parse
    and validate CLI arguments in `main()` (never at import time) and pass plain
    parameters into testable library functions.
-   **Logging (§3.10.1, `required`)**:
    -   Use `logging` rather than `print()` for library and service diagnostics.
    -   **Never use f-strings in `logging.*` calls** — always use `%s`/`%r` lazy
        formatting.
    -   Do not pass the exception instance to `logging.exception('Failed: %s', e)`
        (traceback is appended automatically; pass context args instead).
    -   Raise an exception instead of calling `sys.exit()` or `logging.critical()`
        inside library code.

## 9. Unit Testing (`test_*.py` / `*_test.py`)

-   **Same-PR test requirement (`required`)**: Every new or modified public
    function, method, or non-trivial branch needs unit tests in the same
    commit/PR. Test private `_helpers` transitively through the public API.
-   **Framework (`required`)**: Use `pytest` (preferred) or `unittest.TestCase`
    consistent with the repository's test suite.
-   **Parameterization**: Use `@pytest.mark.parametrize` (or `self.subTest()` /
    `@parameterized.named_parameters`) over copy-pasted `test_*` methods, `for`
    loops inside tests, or `_assert_case` wrappers. Do not merge success and
    error cases with an `expect_error` boolean flag.
-   **Fakes & strict mocks (`required`)**:
    -   Prefer real objects and lightweight in-memory fakes first.
    -   Always use `unittest.mock.patch.object(module, 'Symbol', autospec=True)`
        or `unittest.mock.create_autospec(module.Class, instance=True)` (or
        `pytest`'s `monkeypatch`) — **never** bare `MagicMock()`, `Mock()`, or
        unguarded string-path `patch('...')`.
    -   Prefer `with mock.patch.object(...)` or `pytest` fixtures /
        `self.enter_context(...)` over `mock.patch.stopall`.
-   **Hermeticity & assertions (`required`)**:
    -   **Logging**: Never mock `logging` — use `caplog` in `pytest` or
        `with self.assertLogs(level='...') as log_ctx:` in `unittest`.
    -   **Files & assets**: Use `tmp_path` (`pytest`) or
        `tempfile.TemporaryDirectory()`, never hardcoded `/tmp/...` or
        `mock_open`. Load checked-in test fixtures via `importlib.resources` or
        `pathlib.Path(__file__).parent / 'testdata'`.
    -   **Specific assertions**: Use clear, specific assertions
        (`assert not items`, `assert x is None`, `pytest.raises(..., match=...)`,
        or `assertIsNone`/`assertCountEqual`/`assertIn`/`assertRaisesRegex` in
        `unittest`) rather than `assert len(x) > 0` or bare `pytest.raises(Exception)`.

## 10. When NOT to Comment (Review Guardrails)

Stay silent in these verified safe contexts:

-   **Inline regexes in tests or one-shot CLI scripts**: Do not request
    module-level `re.compile` constants there.
-   **`spec_set=True` when `autospec=True` is set**: `autospec=True` (or
    `mock.create_autospec`) is sufficient; `spec_set=True` breaks classes that
    set attributes in `__init__`.
-   **Nested `for` loops**: Never suggest replacing nested `for` loops with a
    multi-`for` comprehension.
-   **Valid packaging or isolated snippets**: Never flag untouched packaging
    files, passive test fixtures, or missing packaging config when reviewing an
    isolated snippet outside a full repo.
-   **`typing.Final` on `CAPS_WITH_UNDER` constants**: Do not ask for `Final`
    annotations unless the repository enforces them.
-   **Consistent helper ordering**: Do not nitpick whether `_helper` functions
    appear before callers, after callers, or at the bottom when consistent
    (do flag helpers above `__init__` or script code outside `main()`).
-   **Non-lint cleanups on clear tests**: Minor stylistic preferences on already
    clear tests must be `optional`.

## 11. Local Verification Commands

Run these from the repository root before committing or opening a PR (adapting
to the project's configured runner such as `uv run` or `poetry run`):

-   **Format & lint**: `ruff check .` and `ruff format --check .` (or
    `flake8` / `pylint` / `black --check`)
-   **Type-check**: `mypy .` or `pyright`
-   **Test**: `pytest` (or `python -m unittest discover`)
