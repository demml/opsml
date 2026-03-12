## Pull Request

### Short Summary

Renames `GenAIEval*` scouter types to generic `Eval*` equivalents across Rust, Python bindings, TypeScript, and Svelte components. Also refactors the `install_service` CLI action into two distinct functions — `install_service_from_spec` (spec-first, used by `AppState`) and `install_service` (lock-first with spec fallback, used by the CLI).

### Context

**Scouter naming convention alignment** — Scouter upstream renamed its GenAI evaluation types to drop the `GenAI` prefix (e.g. `GenAIEvalRecord` → `EvalRecord`, `GenAIEvalResults` → `EvalResults`, `GenAIEvalDataset` → `EvalDataset`). This PR propagates those renames end-to-end: the Rust server route types, Python PyO3 bindings, Python stubs/type hints, TypeScript interfaces, and Svelte UI components all switch to the new names. The server-side `GenAIEvalRecordPaginationRequest/Response` contract types are similarly updated to `EvalRecordPaginationRequest/Response`.

**CLI `install_service` refactor** — The original `install_service` function tried to read an `opsml.lock` file and fell back to creating one from `opsmlspec.yaml` if the lock file was missing. `AppState::from_spec` needs a spec-first install path that *never* checks for a pre-existing lock file. This is now split into:

**Before:**
```rust
// One function handles both paths; lock-file fallback embedded inside
pub fn install_service(path: PathBuf, write_path: Option<PathBuf>) -> Result<(), CliError> {
    let lockfile = match LockFile::read(&path) {
        Ok(lf) => lf,
        Err(_) => { lock_service(spec_path)?; LockFile::read(&path)? }
    };
    // download artifacts ...
}
```

**After:**
```rust
// Shared helpers
fn create_lock_from_spec(path: &Path) -> Result<LockFile, CliError> { ... }
fn download_service_artifacts(lockfile: LockFile, write_path: Option<PathBuf>) -> Result<(), CliError> { ... }

// Spec-first (used by AppState::from_spec — skips lock check)
pub fn install_service_from_spec(path: PathBuf, write_path: Option<PathBuf>) -> Result<(), CliError> { ... }

// Lock-first with spec fallback (Python-exposed CLI command — unchanged behavior)
#[pyfunction]
pub fn install_service(path: PathBuf, write_path: Option<PathBuf>) -> Result<(), CliError> { ... }
```

A new `CliError::SpecNotFound(PathBuf)` variant provides a clear error when the spec file is missing.

**MCP server formatting** — Minor Rust formatting fixes in `opsml_mcp/src/handler.rs` and `main.rs` (no logic change).

| File | Change |
|---|---|
| `crates/opsml_cli/src/actions/lock.rs` | Splits `install_service` into spec-first and lock-first variants; extracts shared helpers |
| `crates/opsml_cli/src/error.rs` | Adds `CliError::SpecNotFound` variant |
| `crates/opsml_app/src/app.rs` | Calls `install_service_from_spec` instead of `install_service` |
| `crates/opsml_server/src/core/scouter/genai/route.rs` | Updates request/response types to `EvalRecordPaginationRequest/Response` |
| `crates/opsml_server/tests/api/scouter/genai.rs` | Updates test assertions to use renamed types |
| `py-opsml/src/scouter/evaluate.rs` | Updates PyO3 bindings to `Eval*` types |
| `py-opsml/python/opsml/scouter/{__init__,drift,evaluate,queue}/__init__.py` | Re-exports `Eval*` names |
| `py-opsml/python/opsml/stubs/scouter/scouter.pyi` | Updates all type stubs to `Eval*` |
| `py-opsml/python/opsml/_opsml.pyi` | Updates top-level stub exports |
| `crates/opsml_server/opsml_ui/src/lib/components/scouter/genai/record/` | Renames `GenAIEvalRecord*.svelte` → `EvalRecord*.svelte`; updates prop types |
| `crates/opsml_server/opsml_ui/src/lib/components/scouter/genai/task.ts` | Renames `GenAIEvalTaskResult` → `EvalTaskResult` |
| `crates/opsml_server/opsml_ui/src/lib/components/scouter/genai/types.ts` | Renames pagination response type |
| `crates/opsml_mcp/src/handler.rs`, `main.rs` | Formatting only |
| `py-opsml/examples/genai/agent/recipe_generator/` | Updates example agent to use `EvalRecord`, adds new prompt YAMLs and callback module |

### Is this a Breaking Change?

Yes. `GenAIEvalRecord`, `GenAIEvalResults`, `GenAIEvalDataset`, `GenAIEvalSet`, `GenAIEvalTaskResult`, and `GenAIEvalResultSet` are removed from the `opsml.scouter` public Python API and replaced by `EvalRecord`, `EvalResults`, `EvalDataset`, `EvalSet`, `EvalTaskResult`, and `EvalResultSet`. Any existing code importing the old `GenAIEval*` names must update to the new names.
