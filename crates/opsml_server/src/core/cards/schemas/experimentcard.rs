use chrono::NaiveDateTime;
use opsml_cards::UidMetadata;
use opsml_types::cards::ComputeEnvironment;
use opsml_types::RegistryType;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct ExperimentCard {
    pub repository: String,

    pub name: String,

    pub version: String,

    pub uid: String,

    pub tags: Vec<String>,

    pub uids: UidMetadata,

    pub compute_environment: ComputeEnvironment,

    pub registry_type: RegistryType,

    pub app_env: String,

    pub created_at: NaiveDateTime,

    pub subexperiment: bool,

    pub is_card: bool,
}
