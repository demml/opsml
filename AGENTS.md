# AGENTS.md

Guidance for AI agents (Claude Code, Codex, Gemini CLI, etc.) working with this repository.

## What OpsML Is

OpsML is an AI lifecycle platform. Its central abstraction is the **card** — a versioned, encrypted, registry-tracked record that wraps data, models, experiments, prompts, or services. Cards are created in Python, persisted to a Rust server, and visualized in a SvelteKit UI.

The codebase is a polyglot monorepo:
- **`crates/`** — 27 Rust crates forming the server, client, SQL, storage, auth, and card system
- **`py-opsml/`** — Python package (`opsml`) that wraps Rust via PyO3/maturin
- **`crates/opsml_server/opsml_ui/`** — SvelteKit frontend compiled and embedded in the server binary

## Common Commands

### Rust (root `Makefile`)
```bash
make format          # cargo fmt --all
make lints           # cargo clippy --workspace --all-targets -- -D warnings
make test.unit       # toml + cli + sql + storage + server + utils + version tests
make start.server    # build UI + Rust server → serves at http://localhost:3000
make stop.server     # kill port 3000
```

### Individual Rust crate tests
```bash
cargo test -p opsml-server test_opsml_server -- --nocapture --test-threads=1
cargo test -p opsml-sql test_sqlite -- --nocapture --test-threads=1
cargo test -p opsml-sql test_postgres_client -- --nocapture --test-threads=1
cargo test -p opsml-storage test_local_storage_server -- --nocapture --test-threads 1
cargo test -p opsml-toml -- --nocapture --test-threads=1
cargo test -p opsml-version -- --nocapture --test-threads=1
```

### SQL tests with Docker-backed databases
```bash
make build.postgres  # docker-compose up postgres
make build.mysql     # docker-compose up mysql
make test.sql        # sqlite + enum + postgres + mysql, in sequence
```

### Python (`py-opsml/` — run from that directory)
```bash
make setup.project           # build stubs + uv sync + maturin develop --features server
make format                  # isort + ruff + black
make lints                   # ruff + pylint + mypy
make lints.ci                # black --check + ruff + pylint + mypy (CI gate)
make test.unit               # pytest, excluding genai integration / tensorflow / service tests
make test.service            # pytest tests/service
make test.integration        # pytest tests/integration
make test.unit.tensorflow    # install TF deps + run TF-specific tests
```

After any Rust change that touches PyO3-exposed code, re-run `make setup.project` before running Python tests.

### Frontend (`crates/opsml_server/opsml_ui/`)
```bash
pnpm install
pnpm run dev    # hot-reload dev server on :3000 (requires backend on :8080)
pnpm build      # production build, outputs to site/
```
Via root Makefile: `make build.ui`, `make ui.dev`

### Development servers
```bash
make dev.both          # backend :8080 + frontend :3000 in parallel
make dev.backend       # backend only on :8080
make dev.frontend      # frontend only on :3000 (proxies API to :8080)

# With Scouter drift/monitoring integration (Scouter runs separately on :8000)
make dev.both.scouter  # backend :8090, frontend :3000
```

---

## Rust Backend Architecture

### Workspace layout (`crates/`)

All crates follow a single-responsibility pattern. Dependency versions are centralised in the root `Cargo.toml` `[workspace.dependencies]` table — never pin versions inside individual crates.

| Crate | Role |
|---|---|
| `opsml-server` | Axum HTTP server; owns `AppState`, router, and middleware composition |
| `opsml-client` | `reqwest`-based HTTP client used by Python bindings in server mode |
| `opsml-registry` | Python-facing `CardRegistry`; dispatches to local filesystem or server HTTP calls |
| `opsml-cards` | PyO3 card structs (`DataCard`, `ModelCard`, `PromptCard`) |
| `opsml-experiment` | `ExperimentCard` and all experiment tracking logic (metrics, parameters, artifacts) |
| `opsml-genai` | GenAI features: LLM prompt management, structured generation, provider integrations |
| `opsml-service` | `ServiceCard` and service deployment tracking |
| `opsml-sql` | Database abstraction: `SqlClientEnum` over SQLite / PostgreSQL / MySQL via `sqlx` |
| `opsml-storage` | Storage abstraction: `StorageClientEnum` over local / S3 / GCS / Azure |
| `opsml-auth` | JWT issuance and validation, SSO (Keycloak, Okta, generic OAuth2), `UserPermissions` |
| `opsml-types` | Shared request/response contract types, enums (`RegistryType`, `CardTable`), and feature-gated DB types |
| `opsml-crypt` | AES-GCM encrypt/decrypt of card artifact directories; key derivation via HKDF |
| `opsml-events` | 100-element audit event channel; `EventBus` + `AuditEventHandler` |
| `opsml-settings` | `OpsmlConfig` and `OpsmlStorageSettings` loaded from environment |
| `opsml-semver` | Semantic versioning with pre/build tag support |
| `opsml-interfaces` | Trait definitions for ML model and data interfaces |
| `opsml-toml` | TOML card configuration files |
| `opsml-cli` | CLI entry point |
| `opsml-app` | App bootstrap (`create_app`) used by both the server and tests |
| `opsml-mcp` | MCP server integration for tool-calling and agentic workflows |
| `opsml-colors` | Color utilities and theme constants shared across UI and server |
| `opsml-state` | Shared application state helpers and state machine primitives |
| `opsml-mocks` | Reusable mock infrastructure for testing (registries, storage, HTTP) |
| `opsml-utils` | Shared utility functions used across multiple crates |
| `opsml-version` | Version resolution and SemVer helpers |

### Enum-based polymorphism

OpsML does not use trait objects (`Box<dyn Trait>`) for its core backends. Instead, it uses enums with `impl Trait for Enum` delegation:

```rust
// Storage
pub enum StorageClientEnum { Google(..), AWS(..), Local(..), Azure(..) }

// Database
pub enum SqlClientEnum { Postgres(..), Sqlite(..), MySql(..) }
```

`impl StorageClient for StorageClientEnum` and `impl CardLogicTrait for SqlClientEnum` delegate each method to the inner variant. This avoids heap allocation and keeps dispatch at compile time. Follow this pattern when adding new backends.

### `AppState` — the dependency injection container

```rust
pub struct AppState {
    pub storage_client: Arc<StorageClientEnum>,
    pub sql_client: Arc<SqlClientEnum>,
    pub auth_manager: AuthManager,
    pub config: OpsmlConfig,
    pub storage_settings: OpsmlStorageSettings,
    pub scouter_client: ScouterApiClient,
    pub event_bus: EventBus,
}
```

`AppState` is wrapped in `Arc` and provided to every handler via Axum's `State` extractor. Never clone heavy resources — add new shared state here instead.

### Server startup sequence

```
main.rs
  → create_app()           (opsml-app)
    → setup_components()   → builds SqlClientEnum, StorageClientEnum, ScouterApiClient
    → AuthManager::new()   → reads JWT/refresh secrets
    → AppState::new()
    → initialize_default_user()   → creates admin + guest if missing
    → create_router(app_state)    (opsml-server)
  → TcpListener + axum::serve with graceful shutdown
  → start_metrics_server() → Prometheus on server_port + 1
```

### Router and middleware

All routes are prefixed `/opsml/api`. The router is composed from named sub-routers:

```
/opsml/api/auth/*       → get_auth_router()      (no auth required)
/opsml/api/healthcheck  → get_health_router()    (no auth required)
/opsml/api/ui/settings  → get_settings_router()  (no auth required)
/opsml/api/card/*       → get_card_router()      ─┐
/opsml/api/files/*      → get_file_router()       │  protected by
/opsml/api/experiment/* → get_experiment_router() │  auth_api_middleware
/opsml/api/user/*       → get_user_router()       │  + event_middleware
/opsml/api/scouter/*    → get_scouter_router()    │
/opsml/api/genai/*      → get_genai_router()     ─┘
```

Middleware execution order (outermost → innermost):
1. `track_metrics` — Prometheus counter/histogram
2. `CorsLayer` — allows `localhost:3000`, bearer + basic auth headers
3. `auth_api_middleware` — validates JWT, refreshes token if near expiry, populates `Extension<UserPermissions>`
4. `event_middleware` — reads `AuditContext` from response extensions after handler returns, publishes to `EventBus`

### Handler convention

Every route handler follows this signature:

```rust
#[instrument(skip_all)]
pub async fn handler_name(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,  // when auth needed
    Query(params): Query<RequestType>,             // for GET with simple query params
    Json(body): Json<RequestType>,                 // for POST/PUT bodies
) -> Result<Json<ResponseType>, (StatusCode, Json<OpsmlServerError>)>
```

Error handling uses two helpers — use them consistently:
- `internal_server_error(err, "Human message", None)` for 500s
- `OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN)` for 403s

Query strings that contain `Vec<String>` (e.g. tags) must use `serde_qs`, not standard Axum `Query`. Use `parse_qs_query::<T>(&uri)` for those routes.

Audit context is communicated to the middleware via response extensions — not function return values:

```rust
let mut response = Json(result).into_response();
response.extensions_mut().insert(AuditContext {
    resource_id: uid,
    operation: Operation::Create,
    ..
});
Ok(response)
```

### Adding a new route group

1. Create `crates/opsml_server/src/core/<domain>/` with `route.rs` (handlers), `schema.rs` (request/response types), and optionally `utils.rs`.
2. Implement `get_<domain>_router(prefix: &str) -> Result<Router<Arc<AppState>>>` in `route.rs`.
3. Register it in `crates/opsml_server/src/core/router.rs` — add to `merged_routes` if it needs auth, or merge directly if public.

### Artifact encryption

Every card artifact is individually encrypted before storage:

1. `create_artifact_key()` — generates salt, derives AES-GCM key via HKDF, stores `ArtifactKey` (uid → encrypted key) in the database.
2. `create_and_store_encrypted_file()` — encrypts file/directory, uploads to storage backend.
3. `download_artifact()` + `decrypt_directory()` — fetches from storage, decrypts with key from DB.

The `ArtifactKey` table is the source of truth for artifact encryption. Do not bypass it.

---

## PyO3 / Python Binding Architecture

### Module structure

The Rust extension `_opsml` is declared in `py-opsml/src/lib.rs`. Sub-modules register their PyO3 classes and functions:

```rust
#[pymodule]
fn _opsml(m: &Bound<'_, PyModule>) -> PyResult<()> {
    card::add_card_module(m)?;       // DataCard, ModelCard, ExperimentCard, ...
    data::add_data_module(m)?;       // PandasData, PolarsData, NumpyData, ...
    model::add_model_module(m)?;     // SklearnModel, XGBoostModel, TorchModel, ...
    experiment::add_experiment_module(m)?;
    genai::add_genai_module(m)?;
    service::add_service_module(m)?;
    types::add_types_module(m)?;
    // ...
}
```

The Python `opsml` package at `py-opsml/python/opsml/` re-exports everything from `_opsml` and adds pure-Python helpers.

### PyO3 patterns used in this codebase

**Card structs** use `#[pyclass]` with `#[pyo3(get, set)]` on public fields. Fields that hold Python objects (e.g. model interfaces) are `Py<PyAny>` — never clone them, always acquire the GIL first.

```rust
#[pyclass]
pub struct DataCard {
    #[pyo3(get, set)]
    pub space: String,
    #[pyo3(get, set)]
    pub interface: Option<Py<PyAny>>,  // Python DataInterface object
    artifact_key: Option<ArtifactKey>, // private — not exposed to Python
}
```

Constructor signatures use keyword-only arguments for optional fields:
```rust
#[pyo3(signature = (space, name, interface=None, **kwargs))]
pub fn new(space: String, name: String, interface: Option<Py<PyAny>>, kwargs: ...) -> PyResult<Self>
```

**Serialization boundary**: cards serialise to/from JSON at the Python↔Rust boundary. `Py<PyAny>` fields are not directly serialisable; they are replaced by interface metadata (type name, save paths) during serialization and reconstructed on deserialization.

**Python `ModelInterface` subclassing**: users subclass `ModelInterface` in Python and override `save()` / `load()`. The Rust side calls these via `pyo3::Python::with_gil`. Keep GIL acquisition scoped as tightly as possible.

**`#[pyclass]` fields inside `#[pyclass]` structs**: If a struct is `#[pyclass]` and one of its fields is itself a `#[pyclass]` type, do **not** apply `#[pyo3(get, set)]` to that field. PyO3's auto-generated accessors require a Python lifetime (`'py`) at the call site, which makes the field inaccessible in pure-Rust code (e.g. unit tests). Instead, implement getters and setters manually in `#[pymethods]` using `IntoPyObjectExt` / `extract`:

```rust
#[pymethods]
impl SkillCard {
    #[getter]
    pub fn skill<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, CardError> {
        Ok(self.skill.clone().into_bound_py_any(py)?)
    }

    #[setter]
    pub fn set_skill(&mut self, skill: &Bound<'_, PyAny>) -> Result<(), CardError> {
        self.skill = skill.extract::<AgentSkillStandard>()?;
        Ok(())
    }
}
```

See `crates/opsml_cards/src/skill/card.rs` (`skill` and `dependencies` fields) for the canonical example.

**GIL / linker errors in Rust tests**: If `cargo test` fails with errors about Python linking, GIL acquisition, or missing `libpython`, a Python lifetime has leaked into pure-Rust code. Common causes:
- A `#[pyclass]` field has `#[pyo3(get, set)]` applied — remove it and implement manual accessors (see above).
- An error type stores `PyErr` directly as an enum variant via `#[from] PyErr` or `#[error(transparent)] Python(#[from] PyErr)`. **This is wrong.** `PyErr` carries a Python lifetime; storing it in an enum makes the entire error type unusable in pure-Rust tests. Instead, implement the conversions manually: `From<PyErr> for MyError` converts to a `String`-backed variant, and `From<MyError> for PyErr` is the boundary conversion. This rule applies transitively — all errors wrapped via `#[from]` must also follow it. See `crates/opsml_cards/src/skill/error.rs` for the canonical example.

### Two registry modes

`CardRegistry` operates in one of two modes, selected automatically from `OpsmlConfig`:
- **Local** — reads/writes directly to `opsml_registries/` on disk via the storage crate.
- **Server** — proxies all operations through `opsml-client` HTTP calls to the running server.

Python tests use the `mock_db` fixture (`opsml.mock.RegistryTestHelper`) which spins up an in-process local registry backed by SQLite — no server required.

---

## Server API Design Conventions

- All endpoints are JSON in / JSON out. No XML, no form encoding (except SSO token exchange).
- Route paths use snake_case nouns: `/card/create`, `/card/list`, `/experiment/metric`.
- `GET` — query params only. Use `serde_qs` when params include `Vec<T>` (e.g. `tags[]=a&tags[]=b`).
- `POST` — JSON body for creation/mutation. `PUT` for updates. `DELETE` with query params for deletion.
- Pagination uses a cursor pattern: `QueryPageRequest` → `QueryPageResponse { items, has_next, next_cursor, has_previous, previous_cursor, page_info }`.
- Permissions are checked at the handler level, not in middleware: `perms.has_write_permission(&space)` before any mutation.
- **Every handler must accept `Extension(perms): Extension<UserPermissions>`**, even read-only or aggregate routes that don't currently enforce space-level checks. This ensures full RBAC can be layered on without touching handler signatures later. Routes that don't yet enforce permissions should name the parameter `_perms` to suppress the unused warning, but must not omit the extension entirely.
- New contract types belong in `opsml-types/src/contracts/`. Keep request and response types co-located.

---

## UI Architecture (SvelteKit)

### Stack
- **Svelte 5** with runes exclusively (`$state`, `$derived`, `$props`, `$effect`). No Svelte 3/4 patterns (`$:`, `writable()`, `on:click=`).
- **SvelteKit** for SSR routing and server-side data loading.
- **Tailwind CSS v4** + **opsml-theme.css** for styling. All colors come from the theme — never use arbitrary hex values.
- **Skeleton Labs** (`@skeletonlabs/skeleton-svelte`) for component primitives.

### Authentication flow

Authentication state lives entirely in httpOnly cookies. `hooks.server.ts` intercepts every request:
- Public routes (login, register, healthcheck) bypass auth.
- All other routes call `validateTokenOrRedirect()` — redirects to `/opsml/user/login` if invalid.
- `handleFetch` automatically attaches the JWT cookie as an `Authorization: Bearer` header on every outgoing server-side `fetch`.
- If the backend responds with a new `Authorization` header (token refresh), the cookie is silently updated.

### Server-side API client

`src/lib/server/api/opsmlClient.ts` wraps `fetch` with `/opsml/api/` base URL construction. Always use this client from `+page.server.ts` load functions and form actions — do not call the API directly from client-side components.

### Design system

The UI follows a Neo-Brutalist aesthetic. Key rules (see `.github/instructions/UI.instructions.md` for the full spec):
- Hard-offset box shadows (`shadow`, `shadow-small`, `shadow-primary`) — no `backdrop-blur`, no soft shadows.
- Borders are always `border-black` or `border-primary-800` — no `border-gray-*`.
- `rounded-base` (0.375rem) maximum border radius — no `rounded-xl`.
- `bg-surface-50` for page/card backgrounds; opsml-theme palette for all accent colors.
- Transitions are `duration-100`/`duration-200` with `ease-out` — no slow or elastic animations.
- Data-dense areas (tables, trace waterfalls) use restrained styling. Full brutalism is for hero sections and empty states only.

### Route structure

```
src/routes/opsml/
├── home/          # dashboard
├── user/          # login, register, profile, reset
├── cards/         # card listing and detail pages (data, model, experiment, prompt, service)
└── traces/        # Scouter trace waterfall and span detail
```

Each route directory has `+page.svelte` (component), `+page.server.ts` (load + actions), and optionally `+layout.svelte`.

---

## Testing

### Rust server tests (`crates/opsml_server/tests/`)

The canonical Rust integration test pattern:

```rust
#[tokio::test]
async fn test_something() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;  // spins up full app + SQLite + mock Scouter

        let request = Request::builder()
            .uri("/opsml/api/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&payload).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request).await;  // adds auth header automatically
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let result: CreateCardResponse = serde_json::from_slice(&body).unwrap();

        helper.cleanup();  // removes opsml.db and opsml_registries/
    });
}
```

Key test infrastructure:
- `TestHelper::new(None)` — creates the full app via `create_app()`, seeds SQLite from `tests/fixtures/populate_db.sql`, logs in as `admin`, holds the JWT.
- `helper.send_oneshot(request)` — sends request with auth header automatically added.
- `ScouterServer::new()` — `mockito` HTTP mock pre-configured with all Scouter endpoints.
- `MockSsoServer::new()` — `mockito` SSO server with JWKS + token endpoints for Keycloak, Okta, and generic OAuth2.
- `retry_flaky_test!` — retries the body on transient failures (SQLite write contention).
- Always run crate tests with `--test-threads=1` to avoid SQLite contention.

External Scouter calls are always mocked — never require a live Scouter instance in Rust tests.

### Python tests (`py-opsml/tests/`)

```python
# Unit tests use the mock_db fixture for local registry (no server needed)
def test_datacard_creation(mock_db, pandas_data):
    card = DataCard(space="test", name="iris", interface=pandas_data)
    registry = CardRegistry(registry_type="data")
    registry.register_card(card)
    assert card.version is not None

# Service tests require a running server (make start.server.background first)
# Run with: make test.service
```

Fixtures in `tests/conftest.py`:
- `mock_db` — `RegistryTestHelper().setup()` / `.cleanup()` wrapping a local SQLite registry.
- `pandas_data`, `example_dataframe`, `random_forest_classifier` — standard ML test data.
- `chat_prompt` — a `Prompt` instance for GenAI tests.

Test markers: `@pytest.mark.tensorflow` gates TF-specific tests; `make test.unit` excludes them by default.

---

## Feature Flags

`opsml-types` and `opsml-storage` use a `server` feature flag to gate cloud SDK dependencies (`aws-sdk-s3`, `azure_storage`, `gcloud-storage`). The flag is enabled when building the server binary. Python bindings are built with `--features server` via maturin. Unit tests that don't need cloud storage run without it.

---

## Important Design Considerations

OpsML aims to implement a thin Python wrapper around a Rust core. This means:
- The Rust code should be the source of truth for all business logic, data structures, and error handling. Python should not have divergent logic.
- PyO3 bindings should be as thin as possible and only use Python types and runtime when absolutely necessary (e.g. for model interfaces). Avoid complex logic in the PyO3 layer. This allows us to test core logic in Rust unit tests without needing the Python layer.
- Follow idiomatic patterns in both languages, but prioritize Rust conventions for core logic.

### Performance

OpsML is optimized for minimal allocation and maximum throughput. Treat clone as a code smell in hot paths:
- **Avoid `.clone()` unless the borrow checker requires it.** Prefer references, `Arc`, and ownership transfer.
- Do not add `#[derive(Clone)]` speculatively. Only derive it when a concrete callsite needs it — if code compiles without `Clone`, it is not needed.
- Pre-allocate buffers with known capacity (`String::with_capacity`, `Vec::with_capacity`) instead of repeated `push`/`format!` into uninitialized containers.
- Prefer `write!` into a pre-allocated `String` over `format!` in loops.
- Prefer `fetch_one` over `fetch_optional + ok_or_else` for DB lookups that must return a row — fewer allocations, and `sqlx::Error::RowNotFound` propagates naturally.

## Tool Versions

| Tool | Version / notes |
|---|---|
| Rust | Edition 2024, workspace resolver `"2"` |
| Python | 3.10 >= ; `uv` for environment and dependency management |
| Node / Frontend | pnpm (not npm or yarn) |
| PyO3 | 0.27.x with `abi3-py310` |
| Build bridge | maturin |
| DB in tests | SQLite (local/CI); Postgres + MySQL via docker-compose |
