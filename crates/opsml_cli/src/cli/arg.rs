use clap::Args;
use opsml_error::CliError;
use opsml_types::{contracts::CardQueryArgs, RegistryType};
use opsml_utils::clean_string;

pub trait IntoQueryArgs {
    fn into_query_args(&self) -> Result<CardQueryArgs, CliError>;
}

#[derive(Args)]
pub struct ListCards {
    /// Name of the registry (data, model, experiment, prompt etc)
    #[arg(long = "registry")]
    pub registry: String,

    /// repository name
    #[arg(long = "repository")]
    pub repository: Option<String>,

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
    fn into_query_args(&self) -> Result<CardQueryArgs, CliError> {
        let name = self
            .name
            .clone()
            .map(|name| clean_string(&name))
            .transpose()?;

        let repository = self
            .repository
            .clone()
            .map(|repository| clean_string(&repository))
            .transpose()?;

        let registry_type = RegistryType::from_string(&self.registry).unwrap();

        Ok(CardQueryArgs {
            registry_type,
            repository,
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

#[derive(Args)]
pub struct DownloadCard {
    /// Name of the registry (data, model, experiment, prompt etc)
    #[arg(long = "registry")]
    pub registry: String,

    /// Card repository
    #[arg(long = "repository")]
    pub repository: Option<String>,

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

impl IntoQueryArgs for DownloadCard {
    fn into_query_args(&self) -> Result<CardQueryArgs, CliError> {
        let name = self
            .name
            .clone()
            .map(|name| clean_string(&name))
            .transpose()?;

        let repository = self
            .repository
            .clone()
            .map(|repository| clean_string(&repository))
            .transpose()?;

        let registry_type = RegistryType::from_string(&self.registry).unwrap();

        Ok(CardQueryArgs {
            uid: self.uid.clone(),
            name,
            repository,
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
