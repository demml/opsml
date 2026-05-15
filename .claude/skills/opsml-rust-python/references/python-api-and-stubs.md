# Python API And Stubs

The Python package is the user-facing SDK, but the Rust extension owns the core behavior. Python additions should be thin, typed, and tested through user workflows.

## Public API Wiring

For new Python-visible Rust API, check every layer:
1. Rust type/function exists in the owning crate.
2. PyO3 class/function is registered in the appropriate `py-opsml/src/*` module.
3. The module is attached from `py-opsml/src/lib.rs`.
4. Python package exports are updated under `py-opsml/python/opsml/`.
5. `__all__` is updated where the package uses it.
6. Stubs are regenerated or updated through the repo workflow.
7. Python tests cover the user-visible behavior.

Do not leave a type reachable only through `_opsml` unless that is already the local convention for the feature.

## Stub Workflow

Generated stubs live under:
- `py-opsml/python/opsml/_opsml.pyi`
- `py-opsml/python/opsml/stubs/`

Use the repo task:
- `mise run py:setup`

This task runs stub generation, syncs Python dependencies, and builds the Rust extension through maturin. Run it after Rust changes that affect Python-exposed classes, functions, signatures, docs, or enums.

## Python Package Style

Python code should:
- Keep durable business behavior in Rust.
- Use typed, ergonomic public APIs.
- Add docstrings to public functions/classes when intent, side effects, errors, or examples are not obvious.
- Avoid loose `Any` unless the Python boundary is truly dynamic.
- Follow existing import, export, and test conventions in `py-opsml/python/opsml/`.

When behavior is Python-only because it depends on a Python ecosystem object, keep the boundary explicit. Examples include Python model/data interfaces where user subclasses implement `save`, `load`, or prediction behavior.

## Python Tests

Python tests should model how a real user interacts with OpsML:
- Construct the Python-facing object.
- Register or load through `CardRegistry` when relevant.
- Assert stable behavior and error messages.
- Use fixtures such as `mock_db`, `pandas_data`, or `random_forest_classifier` where appropriate.

Do not test generated implementation details when a user workflow test would prove the contract better.

## Maturin And Versions

Do not rely on remembered PyO3 or maturin versions. Inspect:
- Root `Cargo.toml`.
- `py-opsml/Cargo.toml`.
- `py-opsml/pyproject.toml`.
- Lockfiles.
- `mise.toml`.

Version-specific PyO3 patterns should match the versions currently pinned by the repository.
