---
name: google-style-guide
description: "Enforces the official Google Python Style Guide when writing, refactoring, formatting, or reviewing Python (.py) code. Supports parallel zero-context Goldfish file-shard execution and defensive prose calibration (DROP | CALIBRATE | RELOCATE | KEEP). Use whenever generating new Python modules, editing existing Python files, adding type annotations or docstrings, or conducting Python code reviews."
disable-model-invocation: false
metadata:
  publisher: "engineering-standards"
  version: "1.2.0"
---

# Google Python Style Guide Enforcement Skill (`google-style-guide`)

You must adhere to the **Google Python Style Guide** whenever you write, modify, format, or review Python code, while respecting explicit repository configuration (`pyproject.toml`, `ruff.toml`, `.flake8`) and local codebase consistency (per Section 4 of the guide; see also [`python-readability`](../python-readability/SKILL.md) for density, packaging, and testing rules).

---

## 0. Elephant-Goldfish Execution & When to Read `references/style_guide_full.md`

### 0.1 Parallel Goldfish File-Shard Execution (For Multi-File Python Packages)
When enforcing Google Python Style Guide rules (type annotations, Google-style docstrings, import ordering, naming, and prose calibration) across multiple `.py` files:
1. **Elephant Partitioning (Main Thread)**: Lock any shared cross-module type aliases or public symbol renames first, then partition target `.py` files into **2–4 mutually exclusive file shards ($S_1 \cap S_2 \cap \dots \cap S_K = \emptyset$)**.
2. **Parallel Goldfish Style Workers (Zero-Context Sub-Agents)**: Spawn parallel Goldfish workers (`invoke_subagent`), each restricted to its assigned file shard $S_k$.
3. **Unified Verification Barrier**: Once all parallel shards complete, run the formatter and static checkers (`ruff check`, `pylint`, `mypy` / `pytype`) across the combined package.

### 0.2 When to Read `references/style_guide_full.md`
This `SKILL.md` provides the core rules required for everyday Python coding. The complete, verbatim Google Python Style Guide—including all `Pros`, `Cons`, `Decision` rationales, and canonical `Yes:` / `No:` code snippets—is stored in **[`references/style_guide_full.md`](./references/style_guide_full.md)**.

**You MUST read the relevant section of `references/style_guide_full.md` when:**
1. **Resolving Edge Cases:** You encounter an ambiguous formatting or language rule (e.g., complex multi-line type annotations, conditional imports, or mathematical notation exemptions).
2. **Conducting Code Reviews:** You need to cite the exact section number, decision rationale, or canonical `Yes:` / `No:` snippet to justify a review comment.
3. **Fixing Unfamiliar `pylint` / `pytype` Warnings:** A linter or type-checker warning triggers and you need the official Google suppression or refactoring pattern.

### Reference Lookup Index (`references/style_guide_full.md`)

Use search/grep on these exact headings or anchor IDs in `references/style_guide_full.md` instead of loading the entire file:

| Topic | Heading in `references/style_guide_full.md` | Anchor ID |
|---|---|---|
| Pylint & warning suppression | `### 2.1 Lint` | `#s2.1-lint` |
| Imports & packages | `### 2.2 Imports` / `### 2.3 Packages` | `#s2.2-imports` / `#s2.3-packages` |
| Exceptions & `assert` rules | `### 2.4 Exceptions` | `#s2.4-exceptions` |
| Mutable global state | `### 2.5 Mutable Global State` | `#s2.5-global-state` |
| Nested/inner functions & classes | `### 2.6 Nested/Local/Inner Classes and Functions` | `#s2.6-nested` |
| Comprehensions & generators | `### 2.7 Comprehensions & Generator Expressions` | `#s2.7-comprehensions` |
| Default iterators & operators | `### 2.8 Default Iterators and Operators` | `#s2.8-default-iterators-and-operators` |
| Generators & context cleanup | `### 2.9 Generators` | `#s2.9-generators` |
| Lambdas & conditional expressions | `### 2.10 Lambda Functions` / `### 2.11 Conditional Expressions` | `#s2.10-lambda-functions` |
| Default argument values | `### 2.12 Default Argument Values` | `#s2.12-default-argument-values` |
| Properties (`@property`) | `### 2.13 Properties` | `#s2.13-properties` |
| Implicit True/False evaluations | `### 2.14 True/False Evaluations` | `#s2.14-truefalse-evaluations` |
| Lexical scoping & decorators | `### 2.16 Lexical Scoping` / `### 2.17 Function and Method Decorators` | `#s2.17-function-and-method-decorators` |
| Threading & power features | `### 2.18 Threading` / `### 2.19 Power Features` | `#s2.19-power-features` |
| `__future__` & type checking | `### 2.20 Modern Python` / `### 2.21 Type Annotated Code` | `#s2.21-type-annotated-code` |
| Line length, parens & indentation | `### 3.2 Line length` / `### 3.3 Parentheses` / `### 3.4 Indentation` | `#s3.2-line-length` / `#s3.4-indentation` |
| Blank lines & whitespace | `### 3.5 Blank Lines` / `### 3.6 Whitespace` | `#s3.5-blank-lines` / `#s3.6-whitespace` |
| Docstrings (modules, functions, classes) | `### 3.8 Comments and Docstrings` | `#s3.8-comments-and-docstrings` |
| Strings, logging & error messages | `### 3.10 Strings` / `#### 3.10.1 Logging` / `#### 3.10.2 Error Messages` | `#s3.10-strings` / `#s3.10.1-logging` |
| Files, sockets & `TODO` comments | `### 3.11 Files, Sockets, and similar Stateful Resources` / `### 3.12 TODO Comments` | `#s3.11-files-sockets-closeables` |
| Import grouping & ordering | `### 3.13 Imports formatting` | `#s3.13-imports-formatting` |
| Getters/setters & naming rules | `### 3.15 Getters and Setters` / `### 3.16 Naming` | `#s3.16-naming` |
| `main()` & function length | `### 3.17 Main` / `### 3.18 Function length` | `#s3.17-main` |
| Type annotations (all rules) | `### 3.19 Type Annotations` | `#s3.19-type-annotations` |

---

## 1. Python Language Rules

### 1.1 Imports & Packages
* **Import modules, not symbols (unless repo convention overrides):** Default to `import x` or `from x import y` where `x` is the package prefix and `y` is a **module** name. Respect established repository conventions (e.g., `from dataclasses import dataclass`, `from pydantic import BaseModel`, `from fastapi import FastAPI`) when existing codebase modules or linter configs already import symbols directly.
* **Exemptions for static typing:** Always permitted to import symbols directly from `typing`, `collections.abc`, and `typing_extensions` (multiple symbols on one line are permitted, e.g., `from collections.abc import Mapping, Sequence`).
* **Full package paths only:** Always use absolute full package paths. Never use relative imports (e.g., `from . import foo`) even within the same package.
* **Aliasing (`as`):** Use `from x import y as z` only if duplicate module names are imported, `y` conflicts with a local/parameter name, `y` is inconveniently long, or `y` is too generic (`from storage.file_system import options as fs_options`). Use `import y as z` only for standard community abbreviations (e.g., `import numpy as np`).

### 1.2 Exceptions & Error Handling
* **Built-in exceptions:** Raise built-in exceptions when appropriate (e.g., `ValueError` for violated preconditions in arguments).
* **No `assert` for control flow:** Never use `assert` to validate preconditions or enforce critical application logic (`assert` is only for internal invariants or `pytest` tests).
* **Custom exceptions:** Inherit from an existing exception class, end names in `Error`, and avoid module stutter (`foo.FooError` is forbidden).
* **No bare `except:`:** Never use catch-all `except:` or catch `Exception`/`StandardError` unless re-raising or creating an outermost thread/process isolation point.
* **Minimal `try` blocks:** Keep `try` bodies as small as possible to avoid masking unexpected errors. Use `finally` for cleanup.

### 1.3 State, Scope & Functions
* **No mutable global state:** Avoid mutable module-level variables or class attributes. If strictly required, prefix with `_`, provide access via public functions, and document why in a comment.
* **Module constants:** Allowed and encouraged (`CAPS_WITH_UNDER` for public, `_CAPS_WITH_UNDER` for internal).
* **No mutable default arguments:** Never use `[]`, `{}`, `time.time()`, or `flags.FLAGS` attributes as default parameter values. Use `None` (e.g., `b: Sequence[str] | None = None`) and initialize inside the function, or use an immutable tuple `()`.
* **Nested functions/classes:** Avoid nested functions or classes unless closing over a local variable other than `self` or `cls`. Do not nest functions just to hide them; use a module-level `_helper_func()` so it remains unit-testable.
* **Decorators:** Avoid `@staticmethod` (use a module-level function instead). Use `@classmethod` only for named constructors or class-specific global cache modification. Never rely on external resources (files, sockets, DBs) inside decorator evaluation time.
* **Lambda functions:** Allowed for single-line expressions (<60–80 chars). Prefer generator expressions over `map()`/`filter()` with `lambda`, and prefer `operator` module functions (e.g., `operator.mul`).
* **Power features:** Never use custom metaclasses, bytecode access, dynamic inheritance, import hacks, reflection hacks, or `__del__`. Standard library facilities (`abc.ABCMeta`, `dataclasses`, `enum`) are allowed.

### 1.4 Control Flow, Comprehensions & Iterators
* **Comprehensions & generators:** Allowed for simple cases only. **Never** use multiple `for` clauses or complex filter expressions inside a list/dict/set comprehension or generator expression—write an explicit loop instead.
* **Conditional expressions (Ternary):** Allowed only if each portion (`true-expr`, `if-expr`, `else-expr`) fits on its own single line.
* **Default iterators:** Use `for key in adict:` (never `adict.keys()`), `for line in afile:` (never `afile.readlines()`), and `in` / `not in`. Never mutate a container while iterating over it.
* **True/False evaluations:**
  * Use implicit false for sequences/collections (`if seq:`, `if not seq:` instead of `len(seq) == 0`).
  * Always check `None` explicitly with `if foo is None:` or `if foo is not None:`.
  * Never compare booleans with `== False`; use `if not x:`.
  * Compare integers explicitly against `0` (e.g., `if count == 0:`, `if i % 10 == 0:`).
  * For NumPy arrays, check `.size` (`if not arr.size:`).
* **Threading:** Do not assume built-in types are atomic. Use `queue.Queue` or `threading.Condition` over low-level locks.

### 1.5 Linting (`pylint`)
* Suppress inappropriate warnings with a line-level `# pylint: disable=<symbol-name>` comment (never use `disable-msg`) and include an explanation if the symbol isn't self-explanatory.
* Suppress unused argument warnings by deleting them at the start of the function with a comment: `del unused_arg1, unused_arg2  # Unused.` (do not prefix with `unused_` or assign to `_`).

---

## 2. Python Style & Formatting Rules

### 2.1 Layout, Line Length & Indentation
* **Line length:** Maximum **80 characters** unless the repository configures another limit in `pyproject.toml` / `ruff.toml` (e.g., `88` or `100`). Exceptions: long imports, URLs/pathnames in comments, whitespace-free long string constants, `# pylint: disable` comments, and docstring reference links.
* **No backslashes for line continuation:** Never use `\` for explicit line joining. Use implicit continuation inside `()`, `[]`, or `{}`. Wrap long literal strings in parentheses.
* **Indentation:** Always use **4 spaces** (never tabs, never 2-space hanging indents). Align wrapped elements vertically with the opening delimiter or use a 4-space hanging indent with nothing on the first line.
* **Trailing commas:** Recommended whenever the closing `]`, `)`, or `}` is on a separate line (and required for 1-element tuples `(foo,)`). Never place a trailing comma on the same line as the closing bracket.
* **Blank lines:**
  * **2 blank lines** between top-level definitions (functions or classes).
  * **1 blank line** between method definitions and between a `class` docstring and its first method.
  * **0 blank lines** immediately following a `def` line.
* **Semicolons & statements:** Never terminate lines with `;` or join statements with `;`. Put one statement per line (`if foo: bar(foo)` is allowed only if it fits on one line and has no `else`; never one-line `try`/`except`).
* **Parentheses:** Do not use extraneous parentheses in `if (x):`, `while (x):`, or `return (foo)`.

### 2.2 Whitespace
* No spaces inside `()`, `[]`, or `{}`: write `spam(ham[1], {'eggs': 2}, [])`.
* No space before `,`, `;`, `:`, or before `(`/`[` in calls or indexing.
* Surround binary operators (`=`, `==`, `<`, `>`, `!=`, `<=`, `>=`, `in`, `not in`, `is`, `is not`, `and`, `or`, `not`) with a single space.
* **Keyword & default `=` spacing:**
  * **No spaces** around `=` for keyword arguments or unannotated defaults: `def complex(real, imag=0.0): return Magic(r=real, i=imag)`.
  * **Single space** around `=` when a type annotation is present: `def complex(real, imag: float = 0.0):`.
* Never vertically align `=`, `:`, or `#` across consecutive lines.

### 2.3 Imports Ordering
Group imports at the top of the file (after module docstring, before globals) from most generic to least generic, separated by a blank line, sorted lexicographically (case-insensitive) by full package path within each block:
1. `from __future__ import ...`
2. Python standard library (`import os`, `import sys`, `from typing import ...`)
3. Third-party packages (`from absl import app`, `import numpy as np`)
4. Repository sub-packages (`from myproject.backend import huxley`)

### 2.4 Strings, Logging & Resources
* **String formatting:** Use f-strings, `%`, or `.format()`. Never concatenate strings with `+` for formatting (`x = a + b` is okay for a single join, never `first + ', ' + second`).
* **No string `+=` in loops:** Accumulate substrings in a `list` and call `''.join(items)` (or use `io.StringIO`) for $O(N)$ runtime.
* **Quotes:** Pick `'` or `"` consistently within a file; switch quotes only to avoid backslash-escaping inner quotes. Always use `"""` for docstrings and multi-line strings (use `textwrap.dedent()` or parenthesized adjacent strings to avoid unwanted leading spaces).
* **Logging:** Always pass a pattern string literal with `%`-placeholders as the first argument to logging calls (`logging.info('User %s status: %r', user, status)`). **Never pass an f-string to a logger.**
* **Error messages:** Match the exact failure condition (e.g., `if not 0 <= p <= 1:` to catch `NaN`) and keep interpolated variables clearly identifiable (`{p=}` or `%r`).
* **Stateful resources:** Always close files, sockets, and DB connections explicitly using `with open(...) as f:` or `contextlib.closing()`.
* **Shebang & Main:** Omit `#!` unless the file is executed directly (`#!/usr/bin/env python3`). Always wrap executable entry points in `def main():` guarded by `if __name__ == '__main__':` (or `app.run(main)` with `absl`).
* **Function length:** Prefer small, focused functions (~40 lines or fewer).
* **TODO comments:** Format strictly as `# TODO(bug_id_or_url): Actionable description.` Never use `# TODO(@username)`.

---

## 3. Comments, Docstrings & Defensive Prose Calibration

Always use triple double-quotes `"""`. Start with a one-line summary (<= 80 chars) ending with a period, followed by a blank line and the body aligned with the opening quotes.

* **Modules:** Include license boilerplate and a top-level docstring with summary, description, and optional `Typical usage example:` (omitted in `unittest` test modules unless explaining special test execution).
* **Functions & Methods:** Required for all public APIs, non-trivial size, or non-obvious logic. Use consistent descriptive (`"""Fetches rows."""`) or imperative (`"""Fetch rows."""`) phrasing per file.
  * `Args:` List each parameter followed by a colon and description (2- or 4-space hanging indent).
  * `Returns:` (or `Yields:` for generators) Describe return semantics. For tuples, describe as `A tuple (a, b), where...`.
  * `Raises:` Document interface-relevant exceptions (do not document `ValueError` from API precondition misuse).
  * **Overridden methods:** Decorate with `@override` (`from typing import override`); omit the docstring unless behavior refines the base contract.
* **Classes:** Describe what the instance represents (`"""The address of a cheese shop."""`, never `"""Class that describes..."""`). Document public non-property attributes under an `Attributes:` section.
* **Properties & Accessors:** Do not write trivial `@property` or `get_`/`set_` methods that merely wrap an attribute—make the attribute public. Use `@property` only for cheap derived values (docstring style: `"""The number of items."""`). Use `get_foo()`/`set_foo()` only when access is complex or expensive.
* **Inline comments:** Place at least 2 spaces after code (`# Comment`). Explain *why* the code does something tricky, never *what* standard Python syntax does.
* **Defensive Caveats & Claim Calibration (`DROP | CALIBRATE | RELOCATE | KEEP`):**
  * Strip AI-generated fluff, promotional adjectives (*"seamless"*, *"blazingly fast"*), and blanket CYA disclaimers from docstrings and comments:
    * **`DROP`**: Remove speculative caveats that do not inform any caller decision.
    * **`CALIBRATE`**: Narrow overstated capability claims in docstrings to match what the function and tests actually guarantee.
    * **`RELOCATE`**: Move operational warnings to the specific parameter in `Args:` or exception in `Raises:` where the caller acts on them.

---

## 4. Naming Conventions

| Entity Type | Public Convention | Internal / Protected Convention |
|---|---|---|
| Packages | `lower_with_under` | N/A |
| Modules / Files | `lower_with_under.py` (no `-` dashes) | `_lower_with_under.py` |
| Classes / Exceptions | `CapWords` (acronyms all-caps: `HTTPServerError`) | `_CapWords` |
| Functions & Methods | `lower_with_under()` | `_lower_with_under()` |
| Global / Class Constants | `CAPS_WITH_UNDER` | `_CAPS_WITH_UNDER` |
| Variables & Parameters | `lower_with_under` | `_lower_with_under` |
| Type Aliases | `CapWords: TypeAlias` | `_CapWords: TypeAlias` |
| Type Variables (`TypeVar`) | `DescriptiveCapWords` | `_T`, `_P` (only if unconstrained & internal) |

* **Avoid:** Single-character names (except short-scope loop counters `i, j, k, v`, `except ... as e`, `with ... as f`, unconstrained private `_T`, or cited paper math notation), double leading underscores `__private` (prefer single `_`), and variable names containing their type (`id_to_name_dict`).

---

## 5. Type Annotations

* **Scope:** Annotate all public APIs and complex/error-prone internal functions. Do not annotate `self`, `cls` (unless returning/accepting `typing.Self`), or `__init__ -> None`.
* **Line breaking in signatures:** If a signature wraps, place one parameter per line with a trailing comma after the last parameter, and place `) -> ReturnType:` on its own line aligned with `def`.
* **Nullable types (`NoneType`):** Always declare `None` explicitly using modern union syntax `X | None` (e.g., `a: str | None = None`). Never write implicit `a: str = None` or `Union[None, str]`.
* **Container types:** In function parameters, prefer abstract types from `collections.abc` (`Sequence`, `Mapping`, `Iterable`). For concrete types or return types, use built-in generics (`list[int]`, `dict[str, int]`, `tuple[int, ...]`) instead of `typing.List`, `typing.Dict`, or `typing.Tuple`.
* **Always parameterize generics:** Never use bare `Sequence` or `Mapping` (which default to `Any`); specify `Sequence[int]` or use a `TypeVar`.
* **String types:** Use `str` for text and `bytes` for binary data (or `AnyStr` when input/output match). Never use `typing.Text`.
* **Variable annotations:** Use `a: Foo = some_func()`, never legacy `# type: Foo` end-of-line comments.
* **Forward declarations & circular imports:** Use `from __future__ import annotations`. Avoid `if TYPE_CHECKING:` blocks or circular dependencies via refactoring; if unavoidable, alias the circular module to `Any`.

---

## 6. Verification & Self-Correction Workflow

Before completing any Python coding task:
1. **Check Local Consistency:** Inspect surrounding code in the file/module to respect local conventions where global rules allow flexibility.
2. **Consult `references/style_guide_full.md` if Uncertain:** Search [`references/style_guide_full.md`](./references/style_guide_full.md) using the Section Lookup Index in Section 0.
3. **Format Code:** Run the workspace auto-formatter (`pyink`, `ruff format`, or `black`) if available.
4. **Run Linter & Type Checker:** Execute `pylint` / `ruff check` and `mypy` / `pytype` on modified files and resolve all flagged violations before finishing your turn.
