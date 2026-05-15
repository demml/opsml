---
name: opsml-rust-python
description: Repo-local OpsML skill for Rust core, Python bindings, PyO3, maturin, card/registry/server/client logic, Python API exports, generated stubs, and cross-language tests. Use when working in OpsML crates, `py-opsml`, PyO3-exposed types, Rust errors that cross Python, card or registry behavior, server/client contracts, or Python-visible SDK behavior. Do not use for Svelte UI work; use `opsml-ui` instead.
---

# OpsML Rust/Python

Use this skill as the source of truth for OpsML work where Rust core logic is exposed to Python through PyO3. OpsML is not a generic Rust/Python package: cards are the central abstraction, Rust owns the business logic, and Python is a thin ergonomic API over the Rust core.

Start by locating the layer you are changing:
- Rust core design, traits, ownership, performance, cloning, async, or crate-local API shape: read `references/rust-core.md`.
- Rust card, registry, storage, SQL, server, auth, events, or shared contracts: read `references/architecture.md`.
- PyO3 classes, `#[pymethods]`, GIL usage, nested `#[pyclass]` fields, or Python lifetimes: read `references/pyo3-boundaries.md`.
- Error types, `PyErr`, server envelopes, CLI errors, or Python exceptions: read `references/errors.md`.
- Python exports, `__all__`, generated stubs, maturin setup, or Python-visible SDK behavior: read `references/python-api-and-stubs.md`.
- Tests, linting, formatting, or command selection: read `references/testing-workflows.md`.
- Agent-readable APIs, structured errors, validation, lint sensors, or harness work: read `references/agent-harness.md`.

Follow these repo-specific rules:
- Keep core behavior in Rust. Python should expose a typed, ergonomic API and small helpers, not duplicate card, registry, storage, or validation logic.
- Design Rust APIs around domain-owned data, precise traits, and explicit ownership before thinking about the Python binding.
- Keep Python lifetimes out of Rust-only code. Introduce `Python<'py>`, `Bound<'py, PyAny>`, `Py<PyAny>`, and `PyErr` only where code crosses the Python boundary.
- Do not store `PyErr` in reusable Rust error enums. Convert Python errors into string-backed Rust variants, then convert Rust errors back into Python exceptions at the PyO3 boundary.
- For `#[pyclass]` fields whose type is also `#[pyclass]`, do not use `#[pyo3(get, set)]`. Implement manual `#[getter]` and `#[setter]` methods with `IntoPyObjectExt` and `extract`.
- Prefer zero-cost Rust abstractions: enums with delegated trait impls, static dispatch, concrete types, precise errors, iterators, references, ownership transfer, and `Arc` only where shared state is real.
- Treat speculative `Clone`, broad abstractions, unnecessary allocation, and Python-driven core design as design smells. Add them only for concrete call sites.
- Make new Rust core logic testable without Python whenever possible. Add Python tests for Python-visible workflows.
- Write errors and API contracts so humans and coding agents can debug them: stable names, clear fields, concise messages, and actionable hints.
- Use repository workflow tooling from `mise.toml`. Do not invent ad hoc commands when a `mise run ...` task exists.
- Inspect current dependency versions in `Cargo.toml`, `py-opsml/pyproject.toml`, and lockfiles before relying on version-specific behavior.

When making Rust/PyO3 changes, inspect in this order:
1. The Rust crate that owns the domain behavior.
2. Shared types in `opsml-types/src/contracts/` if the behavior crosses server/client/Python boundaries.
3. PyO3 module registration under `py-opsml/src/`.
4. Python package re-exports under `py-opsml/python/opsml/`.
5. Generated stubs under `py-opsml/python/opsml/_opsml.pyi` and `py-opsml/python/opsml/stubs/`.
6. Rust and Python tests that model the user journey.

Use these verification commands when relevant:
- Rust formatting: `mise run format`
- Rust linting: `mise run lints`
- Targeted Rust tests: `cargo test -p <crate> <test_name> -- --nocapture --test-threads=1`
- Full Rust aggregate when justified: `mise run test:unit`
- Rebuild Python bindings after PyO3-exposed Rust changes: `mise run py:setup`
- Python linting: `mise run py:lints`
- Python unit tests: `mise run py:test:unit`

Prefer narrow, local edits that match existing OpsML patterns. Broaden the architecture only when the current domain boundary is truly wrong for the user workflow.
