use clap::Args;

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

#[derive(Args)]
pub struct DownloadArtifacts {
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

#[derive(Args)]
pub struct LaunchServer {
    /// Default port to use with the opsml server
    #[arg(long = "port", default_value = "8888")]
    pub port: i32,
}
