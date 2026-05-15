# OpsML Rust/Python Architecture

OpsML is an AI lifecycle platform organized around cards: versioned, encrypted, registry-tracked records for data, models, experiments, prompts, services, agents, and skills. Python users create and operate cards, but the durable behavior belongs in Rust.

## Core Rule

Rust is the source of truth for:
- Card structure and validation.
- Registry behavior.
- Server contracts and route behavior.
- Storage, SQL, encryption, auth, events, and versioning.
- Serialization formats that persist or cross process boundaries.

Python should provide:
- Ergonomic constructors and usage patterns.
- Thin re-exports from `_opsml`.
- Small Python-only helpers where Python libraries are the natural boundary.
- User-journey tests for public Python behavior.

Do not implement durable business logic twice in Rust and Python. If Python and Rust disagree, the design is already drifting.

## Important Crates

- `opsml-cards`: PyO3 card structs and card-specific behavior.
- `opsml-registry`: Python-facing `CardRegistry`; dispatches to local or server-backed operations.
- `opsml-types`: shared contract types, enums, and request/response shapes.
- `opsml-server`: Axum routes, middleware, API handlers, server errors.
- `opsml-client`: Rust HTTP client used by Python bindings in server mode.
- `opsml-sql`: database abstraction over SQLite, PostgreSQL, and MySQL.
- `opsml-storage`: storage abstraction over local and cloud backends.
- `opsml-crypt`: artifact encryption.
- `opsml-experiment`, `opsml-genai`, `opsml-service`: domain-specific card logic.
- `py-opsml`: Python package and PyO3 extension wiring.

Read `AGENTS.md` for the full crate map before changing a cross-cutting path.

## Enum-Based Backends

OpsML favors enum dispatch for core backends:
- `StorageClientEnum` delegates `StorageClient` methods to local/S3/GCS/Azure variants.
- `SqlClientEnum` delegates SQL/card logic to SQLite/PostgreSQL/MySQL variants.

When adding a backend or domain variant, follow this pattern before reaching for `Box<dyn Trait>`.

## Contracts And Routes

Shared request/response types belong in `opsml-types/src/contracts/`.

Server routes live under `/opsml/api` and follow the existing handler shape:
- `State<Arc<AppState>>` for dependencies.
- `Extension<UserPermissions>` for protected routes, even read-only routes.
- `Query(...)` or `Json(...)` for inputs.
- `Result<Json<Response>, (StatusCode, Json<OpsmlServerError>)>` or an established local equivalent.

Use `parse_qs_query::<T>(&uri)` for query strings containing `Vec<T>`.

## Registry Modes

`CardRegistry` supports:
- Local mode: direct filesystem/SQLite-backed registry operations.
- Server mode: HTTP proxy through `opsml-client`.

New behavior should preserve both modes unless the feature is explicitly server-only. A change that only works through the Python package but not through Rust registry/server paths is usually in the wrong layer.

## Artifact Encryption

Card artifacts are encrypted before storage. Do not bypass:
- `create_artifact_key()`
- `create_and_store_encrypted_file()`
- `download_artifact()` plus decryption
- `ArtifactKey` as the database source of truth

Security-sensitive changes need targeted tests around key lookup, upload/download paths, and error behavior.
