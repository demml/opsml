use chrono::NaiveDateTime;
use opsml_interfaces::data::DataInterfaceMetadata;
use opsml_interfaces::types::FeatureSchema;
use opsml_types::RegistryType;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct DataCardMetadata {
    pub schema: FeatureSchema,

    pub experimentcard_uid: Option<String>,

    pub auditcard_uid: Option<String>,

    pub interface_metadata: DataInterfaceMetadata,
}

#[derive(Serialize, Deserialize)]
pub struct DataCard {
    pub repository: String,

    pub name: String,

    pub version: String,

    pub uid: String,

    pub tags: Vec<String>,

    pub metadata: DataCardMetadata,

    pub registry_type: RegistryType,

    pub app_env: String,
    pub created_at: NaiveDateTime,

    pub is_card: bool,
}
