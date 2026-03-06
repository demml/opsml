pub struct DocEntry {
    pub id: &'static str,
    pub title: &'static str,
    pub category: &'static str,
    pub content: &'static str,
}

pub static DOCS: &[DocEntry] = &[
    // ---- Top-level docs ----
    DocEntry {
        id: "readme",
        title: "OpsML Overview",
        category: "readme",
        content: include_str!("../../../README.md"),
    },
    DocEntry {
        id: "index",
        title: "Documentation Index",
        category: "readme",
        content: include_str!("../../../py-opsml/docs/index.md"),
    },
    DocEntry {
        id: "installation",
        title: "Installation",
        category: "setup",
        content: include_str!("../../../py-opsml/docs/installation.md"),
    },
    DocEntry {
        id: "contributing",
        title: "Contributing",
        category: "readme",
        content: include_str!("../../../py-opsml/docs/contributing.md"),
    },
    DocEntry {
        id: "quality-control",
        title: "Quality Control",
        category: "readme",
        content: include_str!("../../../py-opsml/docs/quality_control.md"),
    },
    // ---- Cards ----
    DocEntry {
        id: "cards/overview",
        title: "Cards Overview",
        category: "cards",
        content: include_str!("../../../py-opsml/docs/docs/cards/overview.md"),
    },
    DocEntry {
        id: "cards/datacard",
        title: "DataCard",
        category: "cards",
        content: include_str!("../../../py-opsml/docs/docs/cards/datacard.md"),
    },
    DocEntry {
        id: "cards/modelcard",
        title: "ModelCard",
        category: "cards",
        content: include_str!("../../../py-opsml/docs/docs/cards/modelcard.md"),
    },
    DocEntry {
        id: "cards/experimentcard",
        title: "ExperimentCard",
        category: "cards",
        content: include_str!("../../../py-opsml/docs/docs/cards/experiment/experimentcard.md"),
    },
    DocEntry {
        id: "cards/experiment/usage",
        title: "ExperimentCard Usage",
        category: "cards",
        content: include_str!("../../../py-opsml/docs/docs/cards/experiment/usage.md"),
    },
    DocEntry {
        id: "cards/promptcard",
        title: "PromptCard",
        category: "cards",
        content: include_str!("../../../py-opsml/docs/docs/cards/promptcard.md"),
    },
    DocEntry {
        id: "cards/agentcard",
        title: "AgentCard",
        category: "cards",
        content: include_str!("../../../py-opsml/docs/docs/cards/agentcard.md"),
    },
    DocEntry {
        id: "cards/servicecard",
        title: "ServiceCard",
        category: "cards",
        content: include_str!("../../../py-opsml/docs/docs/cards/servicecard.md"),
    },
    DocEntry {
        id: "cards/versioning",
        title: "Card Versioning",
        category: "cards",
        content: include_str!("../../../py-opsml/docs/docs/cards/versioning.md"),
    },
    DocEntry {
        id: "cards/yaml",
        title: "YAML Definitions",
        category: "cards",
        content: include_str!("../../../py-opsml/docs/docs/cards/yaml-definitions.md"),
    },
    // ---- Setup ----
    DocEntry {
        id: "setup/overview",
        title: "Setup Overview",
        category: "setup",
        content: include_str!("../../../py-opsml/docs/docs/setup/overview.md"),
    },
    DocEntry {
        id: "setup/authentication",
        title: "Authentication",
        category: "setup",
        content: include_str!("../../../py-opsml/docs/docs/setup/authentication.md"),
    },
    // ---- CLI ----
    DocEntry {
        id: "cli/overview",
        title: "CLI Reference",
        category: "cli",
        content: include_str!("../../../py-opsml/docs/docs/cli/overview.md"),
    },
    // ---- API ----
    DocEntry {
        id: "api/stubs",
        title: "API Stubs",
        category: "api",
        content: include_str!("../../../py-opsml/docs/docs/api/stubs.md"),
    },
    // ---- Automation ----
    DocEntry {
        id: "automation/pyproject",
        title: "Pyproject Automation",
        category: "automation",
        content: include_str!("../../../py-opsml/docs/docs/automation/pyproject.md"),
    },
    // ---- Deployment ----
    DocEntry {
        id: "deployment/overview",
        title: "Deployment Overview",
        category: "deploy",
        content: include_str!("../../../py-opsml/docs/docs/deployment/overview.md"),
    },
    // ---- Monitoring ----
    DocEntry {
        id: "monitoring/overview",
        title: "Monitoring Overview",
        category: "monitor",
        content: include_str!("../../../py-opsml/docs/docs/monitoring/overview.md"),
    },
    // ---- Evaluation ----
    DocEntry {
        id: "evaluation/genai",
        title: "GenAI Evaluation",
        category: "evaluation",
        content: include_str!("../../../py-opsml/docs/docs/evaluation/genai.md"),
    },
    // ---- Benchmark ----
    DocEntry {
        id: "benchmark/overview",
        title: "Benchmark Overview",
        category: "benchmark",
        content: include_str!("../../../py-opsml/docs/docs/benchmark/overview.md"),
    },
    // ---- Specs ----
    DocEntry {
        id: "specs/readme",
        title: "Specs Overview",
        category: "specs",
        content: include_str!("../../../py-opsml/docs/docs/specs/Readme.md"),
    },
    DocEntry {
        id: "specs/ts-component-auditing",
        title: "Spec: Auditing Component",
        category: "specs",
        content: include_str!("../../../py-opsml/docs/docs/specs/ts-component-auditing.md"),
    },
    DocEntry {
        id: "specs/ts-component-cardservice",
        title: "Spec: Card Service Component",
        category: "specs",
        content: include_str!("../../../py-opsml/docs/docs/specs/ts-component-cardservice.md"),
    },
    DocEntry {
        id: "specs/ts-component-eventbus",
        title: "Spec: Event Bus Component",
        category: "specs",
        content: include_str!("../../../py-opsml/docs/docs/specs/ts-component-eventbus.md"),
    },
    DocEntry {
        id: "specs/ts-component-experiment",
        title: "Spec: Experiment Component",
        category: "specs",
        content: include_str!("../../../py-opsml/docs/docs/specs/ts-component-experiment.md"),
    },
    DocEntry {
        id: "specs/ts-evaluations",
        title: "Spec: Evaluations",
        category: "specs",
        content: include_str!("../../../py-opsml/docs/docs/specs/ts-evaluations.md"),
    },
    DocEntry {
        id: "specs/ts-feature-builds",
        title: "Spec: Feature Builds",
        category: "specs",
        content: include_str!("../../../py-opsml/docs/docs/specs/ts-feature-builds.md"),
    },
    DocEntry {
        id: "specs/ts-feature-registry-hardware-async",
        title: "Spec: Registry Hardware Async",
        category: "specs",
        content: include_str!("../../../py-opsml/docs/docs/specs/ts-feature-opsml-registry-hardware-async.md"),
    },
    // ---- Examples: getting started ----
    DocEntry {
        id: "example/getting-started",
        title: "Getting Started",
        category: "example",
        content: include_str!("../../../py-opsml/examples/getting_started.py"),
    },
    DocEntry {
        id: "example/overview-traditional",
        title: "Traditional ML Overview",
        category: "example",
        content: include_str!("../../../py-opsml/examples/docs/overview_traditional.py"),
    },
    DocEntry {
        id: "example/overview-genai",
        title: "GenAI Overview",
        category: "example",
        content: include_str!("../../../py-opsml/examples/docs/overview_genai.py"),
    },
    // ---- Examples: data ----
    DocEntry {
        id: "example/data/numpy",
        title: "Numpy Data Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/data/numpy_data.py"),
    },
    DocEntry {
        id: "example/data/pandas",
        title: "Pandas Data Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/data/pandas_data.py"),
    },
    DocEntry {
        id: "example/data/polars",
        title: "Polars Data Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/data/polars_data.py"),
    },
    DocEntry {
        id: "example/data/arrow",
        title: "Arrow Data Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/data/arrow_data.py"),
    },
    DocEntry {
        id: "example/data/custom",
        title: "Custom Data Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/data/custom_data.py"),
    },
    // ---- Examples: experiment ----
    DocEntry {
        id: "example/experiment/basic",
        title: "Basic Experiment",
        category: "example",
        content: include_str!("../../../py-opsml/examples/experiment/basic.py"),
    },
    DocEntry {
        id: "example/experiment/advanced",
        title: "Advanced Experiment",
        category: "example",
        content: include_str!("../../../py-opsml/examples/experiment/advanced.py"),
    },
    // ---- Examples: model ----
    DocEntry {
        id: "example/model/sklearn",
        title: "Sklearn Model Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/model/sklearn_model.py"),
    },
    DocEntry {
        id: "example/model/torch",
        title: "PyTorch Model Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/model/torch_model.py"),
    },
    DocEntry {
        id: "example/model/lightning",
        title: "Lightning Model Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/model/lightning_model.py"),
    },
    DocEntry {
        id: "example/model/xgboost",
        title: "XGBoost Model Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/model/xgb_booster.py"),
    },
    DocEntry {
        id: "example/model/lightgbm",
        title: "LightGBM Model Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/model/lightgbm_booster.py"),
    },
    DocEntry {
        id: "example/model/catboost",
        title: "CatBoost Model Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/model/catboost_model.py"),
    },
    DocEntry {
        id: "example/model/hf",
        title: "HuggingFace Model Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/model/hf_model.py"),
    },
    DocEntry {
        id: "example/model/onnx",
        title: "ONNX Model Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/model/onnx_model.py"),
    },
    DocEntry {
        id: "example/model/custom",
        title: "Custom Model Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/model/custom_model.py"),
    },
    // ---- Examples: genai ----
    DocEntry {
        id: "example/genai/openai-chat",
        title: "OpenAI Chat Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/genai/chat/openai_chat.py"),
    },
    DocEntry {
        id: "example/genai/pydantic-chat",
        title: "Pydantic AI Chat Example",
        category: "example",
        content: include_str!("../../../py-opsml/examples/genai/chat/pydantic_chat.py"),
    },
];
