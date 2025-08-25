use std::path::PathBuf;

use crate::error::CliError;
use clap::Args;
use opsml_types::{contracts::CardQueryArgs, RegistryType};
use opsml_utils::clean_string;
use pyo3::{pyclass, pymethods};
use scouter_client::DriftType;

#[allow(clippy::wrong_self_convention)]
pub trait IntoQueryArgs {
    fn into_query_args(&self, registry_type: RegistryType) -> Result<CardQueryArgs, CliError>;
}

#[derive(Args)]
pub struct ListCards {
    /// space name
    #[arg(long = "space")]
    pub space: Option<String>,

    /// Name given to a card
    #[arg(long = "name")]
    pub name: Option<String>,

    /// Card version
    #[arg(long = "version")]
    pub version: Option<String>,

    /// Card uid
    #[arg(long = "uid")]
    pub uid: Option<String>,

    /// Card limit
    #[arg(long = "limit")]
    pub limit: Option<i32>,

    /// Tag name
    #[arg(long = "tags", use_value_delimiter = true, value_delimiter = ',')]
    pub tags: Option<Vec<String>>,

    /// max date
    #[arg(long = "max_date")]
    pub max_date: Option<String>,

    /// ignore release candidate
    #[arg(long = "sort_by_timestamp", default_value = "true")]
    pub sort_by_timestamp: bool,
}

impl IntoQueryArgs for ListCards {
    fn into_query_args(&self, registry_type: RegistryType) -> Result<CardQueryArgs, CliError> {
        let name = self
            .name
            .clone()
            .map(|name| clean_string(&name))
            .transpose()?;

        let space = self
            .space
            .clone()
            .map(|space| clean_string(&space))
            .transpose()?;

        Ok(CardQueryArgs {
            registry_type,
            space,
            name,
            version: self.version.clone(),
            uid: self.uid.clone(),
            limit: self.limit,
            tags: self.tags.clone(),
            max_date: self.max_date.clone(),
            sort_by_timestamp: Some(self.sort_by_timestamp),
        })
    }
}

#[derive(Args, Clone)]
#[pyclass]
pub struct DownloadCard {
    /// Card space
    #[arg(long = "space")]
    pub space: Option<String>,

    /// Name given to card
    #[arg(long = "name")]
    pub name: Option<String>,

    /// Card version
    #[arg(long = "version")]
    pub version: Option<String>,

    /// Card uid
    #[arg(long = "uid")]
    pub uid: Option<String>,

    /// Write directory
    #[arg(long = "write-dir", default_value = "artifacts")]
    pub write_dir: String,
}

#[pymethods]
impl DownloadCard {
    /// Create a new DownloadCard
    #[new]
    #[pyo3(signature = (space=None, name=None, version=None, uid=None, write_dir=None))]
    pub fn new(
        space: Option<String>,
        name: Option<String>,
        version: Option<String>,
        uid: Option<String>,
        write_dir: Option<String>,
    ) -> Self {
        let write_dir = write_dir.unwrap_or_else(|| "artifacts".into());
        Self {
            space,
            name,
            version,
            uid,
            write_dir,
        }
    }
}

impl DownloadCard {
    pub fn write_path(&self) -> PathBuf {
        PathBuf::from(&self.write_dir)
    }

    pub fn service_path(&self) -> PathBuf {
        PathBuf::from(&self.write_dir)
    }
}

impl IntoQueryArgs for DownloadCard {
    fn into_query_args(&self, registry_type: RegistryType) -> Result<CardQueryArgs, CliError> {
        let name = self
            .name
            .clone()
            .map(|name| clean_string(&name))
            .transpose()?;

        let space = self
            .space
            .clone()
            .map(|space| clean_string(&space))
            .transpose()?;

        Ok(CardQueryArgs {
            uid: self.uid.clone(),
            name,
            space,
            version: self.version.clone(),
            registry_type,
            ..Default::default()
        })
    }
}

#[derive(Args)]
pub struct LaunchServer {
    /// Default port to use with the opsml server
    #[arg(long = "port", default_value = "8888")]
    pub port: i32,
}

#[derive(Args)]
pub struct KeyArgs {
    /// Password to use for the key
    #[arg(long = "key")]
    pub password: String,

    /// Number of rounds to use for the key
    #[arg(long = "rounds", default_value = "100000")]
    pub rounds: u32,
}

#[derive(Args, Clone)]
#[pyclass]
pub struct ScouterArgs {
    /// Space name
    #[arg(long = "space")]
    pub space: String,

    /// Name
    #[arg(long = "name")]
    pub name: String,

    /// Version
    #[arg(long = "version")]
    pub version: String,

    /// Drift type
    #[arg(long = "drift-type")]
    pub drift_type: DriftType,

    /// Status
    #[arg(long = "active")]
    pub active: bool,

    #[arg(long = "deactivate-others", default_value = "false")]
    pub deactivate_others: bool,
}

#[pymethods]
impl ScouterArgs {
    /// Convert the ScouterArgs to a CardQueryArgs
    #[new]
    pub fn new(
        space: String,
        name: String,
        version: String,
        drift_type: DriftType,
        active: bool,
        deactivate_others: bool,
    ) -> Self {
        Self {
            space,
            name,
            version,
            drift_type,
            active,
            deactivate_others,
        }
    }
}

#[derive(Args, Clone)]
pub struct UiArgs {
    /// Version
    #[arg(long = "version")]
    pub version: Option<String>,
}
