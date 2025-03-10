use chrono::NaiveDateTime;
use opsml_interfaces::{FeatureSchema, ModelInterfaceSaveMetadata, OnnxSchema};
use opsml_types::ModelInterfaceType;
use opsml_types::{DataType, ModelType, RegistryType, TaskType};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;

#[derive(Serialize, Deserialize)]
pub struct OnnxSession {
    pub schema: OnnxSchema,

    pub quantized: bool,
}

#[derive(Serialize, Deserialize)]
pub struct ModelInterfaceMetadata {
    pub task_type: TaskType,

    pub model_type: ModelType,

    pub data_type: DataType,

    pub onnx_session: Option<OnnxSession>,

    pub schema: FeatureSchema,

    pub save_metadata: ModelInterfaceSaveMetadata,

    pub extra_metadata: HashMap<String, String>,

    pub interface_type: ModelInterfaceType,

    pub model_specific_metadata: Value,
}

#[derive(Serialize, Deserialize)]
pub struct ModelCardMetadata {
    pub datacard_uid: Option<String>,

    pub experimentcard_uid: Option<String>,

    pub auditcard_uid: Option<String>,

    pub interface_metadata: ModelInterfaceMetadata,
}

#[derive(Serialize, Deserialize)]
pub struct ModelCard {
    pub repository: String,

    pub name: String,

    pub version: String,

    pub uid: String,

    pub tags: Vec<String>,

    pub metadata: ModelCardMetadata,

    pub registry_type: RegistryType,

    pub to_onnx: bool,

    pub app_env: String,

    pub created_at: NaiveDateTime,

    pub is_card: bool,
}
