# Plan

The following are a non-exhaustive lists of current items on the roadmap split by effort estimation. Feel free to make a PR and contribute!

---
## `Low/Medium effort`

- [ ] Add CatBoost compatibility to modelcards/onnx conversion [link](https://catboost.ai/en/docs/concepts/apply-onnx-ml)
- [ ] Add S3 storage integration
- [ ] Add AWS DB integration
- [ ] Add bigquery db integration
- [ ] SqlAlchemy V2.0 upgrade

---
## `Large effort`

- [ ] Drift detection (data, models, etc.)
    - No set plan, but ideally Opsml should provide minimal tooling
- [ ] Auditability reports (**in progress**)
    - [ ] Initial template/generating docs (pdf, google sheets?)
    - [ ] Python implementation
    - [ ] New webserver

---
## `Version 2.0 - The future is Rust`
- [ ] Re-write core `Opsml` logic in Rust
    - Allows for faster execution reduced python dependencies
    - Rust card system
- [ ] Dataframe profiling in Rust
- [ ] Data-centric AI tooling in Rust
- [ ] `Opsml` CLI in Rust
- [ ] `Opsml` Api via Rust?