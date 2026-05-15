# Testing And Workflow Commands

Use `mise` as the default command surface. The tasks encode environment variables, working directories, feature flags, and server setup.

## Default Commands

Rust:
- Format: `mise run format`
- Lint: `mise run lints`
- Full Rust aggregate when justified: `mise run test:unit`
- Targeted crate tests: `cargo test -p <crate> <test_or_module> -- --nocapture --test-threads=1`

Python:
- Build stubs and extension: `mise run py:setup`
- Format: `mise run py:format`
- Lint/type checks: `mise run py:lints`
- CI lint gate: `mise run py:lints-ci`
- Unit tests: `mise run py:test:unit`
- Service tests: `mise run py:test:service`
- Integration tests: `mise run py:test:integration`

Frontend work belongs to `opsml-ui`, not this skill.

## Command Selection

Use targeted tests first:
- Changed a single Rust crate: run that crate's focused tests.
- Changed SQL behavior: use the relevant `test:sql-*` task.
- Changed server handlers: use targeted `opsml-server` tests with `--test-threads=1`.
- Changed PyO3-exposed API: run `mise run py:setup`, then targeted Python tests or `mise run py:test:unit`.
- Changed Python-only public API: run targeted pytest, then `mise run py:lints` if practical.

Broaden to aggregate tasks when the change crosses boundaries or before final handoff on high-risk work.

## Server Test Caution

Do not run all `opsml_server` tests casually. The repo guidance warns that broad failures can leave stale state. Prefer isolated tests and cleanup. Use `TestHelper::new(None)` patterns and `helper.cleanup()` where applicable.

Canonical Rust server tests:
- Use `TestHelper::new(None)`.
- Send requests through `helper.send_oneshot(request)` so auth headers are added.
- Use `retry_flaky_test!` for transient SQLite contention.
- Run with `--test-threads=1`.
- Mock Scouter and SSO; do not require live external services.

## PyO3 Change Checklist

After changing a Python-exposed Rust type:
1. Confirm Rust core behavior is tested without Python where possible.
2. Confirm PyO3 registration is complete.
3. Run `mise run py:setup`.
4. Confirm imports work from `opsml`, not only from `_opsml`.
5. Add or update Python tests for the user workflow.
6. Run targeted Python tests or `mise run py:test:unit`.

## Test Philosophy

Tests should prove user journeys and stable contracts:
- Card creation, serialization, registration, retrieval, and loading.
- Local and server-backed registry behavior where both apply.
- Structured error behavior for invalid inputs.
- Python-visible behavior from the public `opsml` package.

Avoid tests that mirror private implementation details. Add regression tests when fixing a bug.
