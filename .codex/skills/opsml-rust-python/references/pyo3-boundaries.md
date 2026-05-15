# PyO3 Boundary Rules

PyO3 code is a boundary layer. Keep Python lifetimes, `PyErr`, and object extraction at the edge so Rust core code remains testable with normal Rust tests.

## Boundary Types

Use these types only when the code is actually crossing into Python:
- `Python<'py>`
- `Bound<'py, PyAny>`
- `Py<PyAny>`
- `PyErr`
- `#[pyclass]`, `#[pymethods]`, `#[pyfunction]`

Pure Rust functions should generally accept and return Rust types, not Python-bound objects.

## Constructors

For Python constructors, keep extraction and conversion near `#[new]`, then call a Rust-native constructor such as `new_rs`, `from_config`, or a domain-specific builder.

Preferred shape:

```rust
#[cfg(feature = "python")]
#[pymethods]
impl SkillCard {
    #[new]
    pub fn new(skill: &Bound<'_, PyAny>, space: Option<&str>) -> Result<Self, SkillError> {
        let skill = skill.extract::<AgentSkillStandard>()?;
        Self::new_rs(skill, space, None, None, None, None, None, None)
    }
}
```

Keep the Rust-native constructor usable without Python.

## Nested `#[pyclass]` Fields

If a `#[pyclass]` struct has a field whose type is itself a `#[pyclass]`, do not put `#[pyo3(get, set)]` on that field. PyO3-generated accessors can leak Python lifetimes into pure Rust call sites and tests.

Use the canonical pattern in `crates/opsml_cards/src/skill/card.rs`:
- `skill` field getter at `SkillCard::skill`.
- `set_skill` setter using `extract`.
- `dependencies` getter using `IntoPyObjectExt`.
- `set_dependencies` setter using `extract::<Vec<SkillDependency>>()`.

Preferred shape:

```rust
#[getter]
pub fn skill<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, SkillError> {
    Ok(self.skill.clone().into_bound_py_any(py)?)
}

#[setter]
pub fn set_skill(&mut self, skill: &Bound<'_, PyAny>) -> Result<(), SkillError> {
    self.skill = skill.extract::<AgentSkillStandard>()?;
    Ok(())
}
```

## Python Objects In Cards

Some cards hold Python-owned objects, such as model or data interfaces. Keep GIL acquisition scoped tightly:
- Acquire the GIL only where calling Python methods or extracting Python objects.
- Convert Python-side data into Rust metadata before serialization.
- Do not attempt to serialize `Py<PyAny>` directly.
- Reconstruct Python-facing objects only at load/deserialization boundaries where the Python API needs them.

## Feature Gates

Respect existing `python` and `server` feature gates. If a Rust unit test fails with Python linking or libpython errors, inspect for leaked PyO3 types in core code or transitive error chains.

Common causes:
- `PyErr` stored in a reusable error enum.
- `#[pyo3(get, set)]` on nested `#[pyclass]` fields.
- Python-only imports not guarded with `#[cfg(feature = "python")]`.

## Module Registration

New Python-visible Rust functions/classes must be wired through `py-opsml/src/lib.rs` and the appropriate submodule registration function, such as:
- `card::add_card_module(m)?`
- `data::add_data_module(m)?`
- `model::add_model_module(m)?`
- `experiment::add_experiment_module(m)?`
- `agent::add_agent_module(m)?`
- `service::add_service_module(m)?`
- `types::add_types_module(m)?`

Do not stop after adding `#[pyclass]`; registration, Python exports, stubs, and tests are part of the public API surface.
