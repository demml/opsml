// This is an evolving trait for cards.
use crate::error::CardError;
use chrono::{DateTime, Utc};
use opsml_types::{RegistryType, contracts::CardRecord};
use std::path::PathBuf;

pub trait OpsmlCard {
    /// Returns the card's alias
    fn get_registry_card(&self) -> Result<CardRecord, CardError>;

    fn get_version(&self) -> String;

    fn set_name(&mut self, name: String);

    fn set_space(&mut self, space: String);

    fn set_version(&mut self, version: String);

    fn set_uid(&mut self, uid: String);

    fn set_created_at(&mut self, created_at: DateTime<Utc>);

    fn set_app_env(&mut self, app_env: String);

    fn is_card(&self) -> bool;

    fn save(&self, path: PathBuf) -> Result<(), CardError>;

    fn registry_type(&self) -> &RegistryType;
}
