# Plan

The following are a no-exhaustive lists of current items on the roadmap split by effort estimation. Feel free to make a PR and contribute!

---
## `Low/Medium effort`

- [ ] Add CatBoost compatibility to modelcards/onnx conversion [link](https://catboost.ai/en/docs/concepts/apply-onnx-ml)
- [ ] Expand out CLI
    - [ ] Compare metrics and generate plots
- [ ] Pipelines Integration (already in progress)
    - [ ] Flush out `PipelineCards`
    - [ ] Add KubeFlow integration
    - [ ] Add Vertex integration
        - [ ] Different levels of abstraction
            - [ ] Pure kubeflow/vertex
            - [ ] Decorator based
            - [ ] Config based
    - [ ] Airflow
- [ ] Add S3 storage integration
- [ ] Add AWS DB integration
- [ ] Add bigquery db integration
- [ ] SqlAlchemy V2.0 upgrade
- [ ] Pydantic V2.0 upgrade (when available)

---
## `Large effort`

- [ ] Drift detection (data, models, etc.)
    - No set plan, but ideally Opsml should provide minimal tooling
- [ ] Auditability reports
    - [ ] Initial template/generating docs (pdf, google sheets?)
    - [ ] Python implementation
    - [ ] Cli implementation
- [ ] Auto ML-api
    - Already have working draft in previous releases
    - [ ] Dynamic API generation from Onnx model
    - [ ] Allow for DS/eng to write custom funcs/tasks that can be used when making predictions (pre/post-processing, background tasks for recording preds, etc.)
