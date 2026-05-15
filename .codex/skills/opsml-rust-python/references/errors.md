# Errors Across Rust And Python

OpsML errors should be clear enough for humans and structured enough for agents. They should name what failed, where possible include the affected field/resource, and preserve enough context to fix the issue without parsing vague prose.

## No Stored `PyErr`

Do not store `PyErr` inside reusable Rust error enums. `PyErr` can pull Python runtime/lifetime concerns into pure Rust code and cause C linker or GIL-related failures in Rust tests.

Use the canonical pattern in `crates/opsml_cards/src/skill/error.rs`:
- Rust error variants store Rust-owned data such as `String`.
- `From<PyErr> for SkillError` converts to a string-backed variant.
- `From<SkillError> for PyErr` exists only behind the Python feature and maps to a Python exception at the boundary.

Preferred shape:

```rust
#[derive(thiserror::Error, Debug)]
pub enum DomainError {
    #[error("{0}")]
    Error(String),

    #[error(transparent)]
    Io(#[from] std::io::Error),
}

#[cfg(feature = "python")]
impl From<PyErr> for DomainError {
    fn from(err: PyErr) -> Self {
        DomainError::Error(err.to_string())
    }
}

#[cfg(feature = "python")]
impl From<DomainError> for PyErr {
    fn from(err: DomainError) -> PyErr {
        pyo3::exceptions::PyRuntimeError::new_err(err.to_string())
    }
}
```

Avoid this in core errors:

```rust
#[error(transparent)]
Python(#[from] PyErr)
```

Only use direct Python error storage in code that is permanently Python-only and cannot be reached by Rust tests or Rust core logic. That should be rare in OpsML.

## Transitive Error Chains

The rule applies transitively. If `CardError` wraps `ModelInterfaceError`, and `ModelInterfaceError` stores `PyErr`, then `CardError` is contaminated too.

When adding `#[from]` variants, inspect wrapped errors for PyO3 types. Prefer converting upstream errors to string-backed variants at the boundary.

## Server Error Envelope

Server handlers should use the existing `OpsmlServerError` helpers and structured fields where available. For new agent-facing or validation work, prefer stable data:
- `code`
- `field`
- `suggested_action` or hint
- `doc_url`
- `retry`

Prefer one stable error shape across HTTP, PyO3, CLI, lint output, validation, and eval. A Python caller, CLI user, UI route, and coding agent should be able to recognize the same failure without parsing unrelated prose.

## Human And Agent Debuggability

Error messages should:
- Name the operation that failed.
- Include the resource identifier when safe, such as card UID, space/name/version, file path, or field.
- Avoid generic messages like "invalid input" when the failing field is known.
- Avoid logging secrets, tokens, encryption keys, or provider credentials.
- Keep wording concise and stable enough for tests and agents.

## Mapping To Python Exceptions

Choose Python exception types deliberately:
- Invalid user input: `PyValueError`.
- Missing key or field: `PyKeyError` or `PyValueError`, depending on existing local style.
- Filesystem/IO: `PyOSError`.
- Runtime integration failure: `PyRuntimeError`.

Follow nearby mappings in the same crate before introducing a new exception style.
