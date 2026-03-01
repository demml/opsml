# Pre-PR Test Suite

Run the full OpsML test suite (Rust + Python) before submitting a PR. Capture and report all errors clearly at each step. Stop a workflow only if a step produces errors that would block the next step from running correctly.

## Rust Workflow

Work from the repo root (`/Users/stevenforrester/Documents/GitHub/opsml`).

### Step 1 — Format
```
make format
```
Report any formatting changes applied.

### Step 2 — Lints
```
make lints
```
If clippy errors are found:
- Show the full error output
- Fix each lint error in the relevant source file(s)
- Re-run `make lints` to confirm all errors are resolved before proceeding

### Step 3 — Unit Tests
```
make test.unit
```
Capture full test output. If any tests fail:
- Identify the failing test(s) and the error message
- Investigate the root cause in the source
- Fix the issue and re-run `make test.unit` to confirm

---

## Python Workflow

Change directory to `py-opsml/` for all Python steps.

### Step 4 — Setup (rebuild stubs + wheel)
```
cd py-opsml && make setup.project
```
This must complete successfully before running Python tests. If it fails, diagnose and fix before proceeding.

### Step 5 — Format
```
make format
```
Report any formatting changes applied.

### Step 6 — Lints
```
make lints
```
If lint errors are found:
- Show the full error output
- Fix each issue
- Re-run `make lints` to confirm clean

### Step 7 — Unit Tests
```
make test.unit
```
Capture full test output. If any tests fail:
- Identify the failing test(s) and the error message
- Investigate the root cause
- Fix the issue and re-run `make test.unit` to confirm

---

## Final Report

After all steps complete, output a summary table:

| Step | Status | Notes |
|------|--------|-------|
| Rust: format | ✓ / ✗ | |
| Rust: lints | ✓ / ✗ | |
| Rust: test.unit | ✓ / ✗ | |
| Python: setup.project | ✓ / ✗ | |
| Python: format | ✓ / ✗ | |
| Python: lints | ✓ / ✗ | |
| Python: test.unit | ✓ / ✗ | |

If everything passes: confirm the branch is ready to submit as a PR.
If anything failed and could not be fixed: list the outstanding issues with file paths and error messages so the user can address them manually.
