# Rust Core Practices

OpsML's Python API is only as good as the Rust core underneath it. Design Rust code first as a clean, testable library; then expose the right boundary to Python.

## API Shape

Prefer APIs that make invalid states difficult to represent:
- Use domain types instead of raw strings or loose maps for durable concepts.
- Use enums for closed sets of states, backends, card kinds, operations, and variants.
- Use structs with named fields for meaningful records.
- Use traits for behavior shared across real implementations, not for one call site.
- Keep public functions explicit about inputs, outputs, and error behavior.

Do not shape core Rust APIs around what is easiest to extract from `PyAny`. Convert Python inputs at the boundary, then call Rust-native functions.

## Zero-Cost Abstractions

Prefer abstractions that compile down to direct code:
- Generic functions with trait bounds when the caller can be monomorphized.
- Enum dispatch for known backend variants, matching existing `StorageClientEnum` and `SqlClientEnum` patterns.
- Iterators instead of building intermediate vectors.
- Borrowed data such as `&str`, `&Path`, and `&[T]` when ownership is not needed.
- `Cow<'_, str>` only when both borrowed and owned paths are real and the complexity pays for itself.

Use `Box<dyn Trait>` only when runtime extensibility is required and the allocation/dynamic dispatch is an intentional tradeoff.

## Ownership And Cloning

Treat `.clone()` as a question, not a reflex:
- Prefer borrowing when the callee does not need ownership.
- Prefer moving values when the current scope no longer needs them.
- Use `Arc<T>` for real shared ownership across tasks, state, or handlers.
- Avoid `Arc<Mutex<T>>` as a default; first ask whether ownership, message passing, a narrower lock, or immutable state is enough.
- Do not derive `Clone` speculatively. Derive it only when concrete call sites need it.

Common acceptable clones:
- Small identifiers or config values at API boundaries where ownership is clearer than lifetimes.
- `Arc::clone` for shared application state.
- Data copied into an owned response type.

Common suspicious clones:
- Large vectors, maps, schemas, payloads, or serialized values in loops.
- Cloning to work around a borrow caused by overly broad scopes.
- Cloning Python objects or PyO3 wrappers without a clear GIL/boundary reason.

## Allocation And Strings

Avoid accidental allocation in hot or repeated paths:
- Use `String::with_capacity` when building a known-size string.
- Use `Vec::with_capacity` when the item count is known or cheaply estimated.
- Use `write!` into an existing `String` instead of repeated `format!` in loops.
- Avoid serializing/deserializing just to move data between Rust layers.
- Keep JSON conversion at API, storage, or Python boundaries unless the core domain truly stores JSON.

Do not micro-optimize code that is not on a meaningful path. Prefer clear algorithms first, then optimize measured bottlenecks.

## Traits

Use traits when they express a stable capability:
- Storage behavior.
- SQL/card persistence behavior.
- Card lifecycle behavior.
- Interface behavior with multiple implementations.

Keep traits small enough to implement correctly. Avoid kitchen-sink traits that force unrelated implementations to carry meaningless methods.

Prefer associated types or generics when they simplify call sites. Avoid clever trait machinery when an enum, function, or concrete type would be easier to read and test.

## Async And Shared State

Use async for I/O boundaries: HTTP, database, storage, network calls, and server handlers. Keep pure computation synchronous unless the caller requires async.

For shared server state:
- Put heavy shared dependencies in `AppState`.
- Wrap shared backend clients in `Arc` as established by the repo.
- Avoid cloning heavy clients or rebuilding pools per request.
- Keep locks out of request hot paths where possible.

Use timeouts, cancellation-aware APIs, and bounded concurrency for external calls when the surrounding code already supports those patterns.

## Error Design

Rust errors should be precise and useful before they become Python exceptions:
- Use `thiserror` enums for domain errors.
- Include the failing operation and field/resource where possible.
- Preserve source errors with `#[from]` only when the wrapped error is safe for Rust-only code.
- Avoid `anyhow` in library surfaces unless the crate already uses it for an internal boundary.

For errors crossing Python, follow `references/errors.md`.

## Testing Rust Core

New core logic should have Rust tests that do not require Python unless the behavior is inherently Python-facing.

Good Rust tests:
- Exercise domain behavior through public or crate-visible APIs.
- Cover success, edge cases, and stable failures.
- Use local fixtures and mocks instead of external services.
- Keep SQLite/server tests isolated with `--test-threads=1` where the repo requires it.

If a test requires Python for non-Python behavior, inspect the design for leaked PyO3 types or a misplaced boundary.
