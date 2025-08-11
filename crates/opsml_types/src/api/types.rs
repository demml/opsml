use std::fmt::Display;

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone)]
pub enum RequestType {
    Get,
    Post,
    Put,
    Delete,
}

#[derive(Debug, Clone)]
pub enum Routes {
    ArtifactKey,
    ArtifactRecord,
    AuthLogin,
    AuthRefresh,
    AuthValidate,
    AuthUiLogin,

    Card,
    CardReadme,
    CardCreate,
    CardDelete,
    CardList,
    CardLoad,
    CardVersion,
    CardUpdate,

    CardMetadata,
    CardSpaces,
    CardRegistryStats,
    CardRegistryPage,
    CardRegistryVersionPage,

    DeleteFiles,
    Files,
    FileContent,
    FileDelete,
    Healthcheck,
    List,
    ListInfo,
    Multipart,
    CompleteMultipart,
    Presigned,
    StorageSettings,
    ExperimentMetrics,
    ExperimentGroupedMetrics,
    ExperimentMetricNames,
    ExperimentHardwareMetrics,
    ExperimentParameters,
    ScouterAuthLogin,

    ScouterDriftCustom,
    ScouterDriftPsi,
    ScouterDriftSpc,
    ScouterProfile,
    ScouterProfileStatus,
    ScouterUsers,
    ScouterProfileUi,
    ScouterHealthcheck,

    User,
}

impl Routes {
    pub fn as_str(&self) -> &str {
        match self {
            Routes::Files => "files",
            Routes::FileContent => "files/content",
            Routes::FileDelete => "files/delete",
            Routes::Multipart => "files/multipart",
            Routes::CompleteMultipart => "files/multipart/complete",
            Routes::Presigned => "files/presigned",
            Routes::List => "files/list",
            Routes::ListInfo => "files/list/info",
            Routes::ArtifactKey => "files/key",
            Routes::ArtifactRecord => "files/artifact",
            Routes::Healthcheck => "healthcheck",
            Routes::StorageSettings => "storage/settings",
            Routes::DeleteFiles => "files/delete",
            Routes::AuthLogin => "auth/login",
            Routes::AuthRefresh => "auth/refresh",
            Routes::AuthValidate => "auth/validate",
            Routes::AuthUiLogin => "auth/ui/login",
            Routes::Card => "card",
            Routes::CardReadme => "card/readme",
            Routes::CardSpaces => "card/spaces",
            Routes::CardMetadata => "card/metadata",
            Routes::CardRegistryStats => "card/registry/stats",
            Routes::CardRegistryPage => "card/registry/page",
            Routes::CardRegistryVersionPage => "card/registry/version/page",

            Routes::CardCreate => "card/create",
            Routes::CardDelete => "card/delete",
            Routes::CardList => "card/list",
            Routes::CardLoad => "card/load",
            Routes::CardVersion => "card/version",
            Routes::CardUpdate => "card/update",
            Routes::ExperimentMetrics => "experiment/metrics",
            Routes::ExperimentGroupedMetrics => "experiment/metrics/grouped",
            Routes::ExperimentMetricNames => "experiment/metrics/names",
            Routes::ExperimentHardwareMetrics => "experiment/hardware/metrics",
            Routes::ExperimentParameters => "experiment/parameters",

            // Scouter Auth Routes
            Routes::ScouterAuthLogin => "scouter/auth/login",

            // Scouter Drift Routes
            Routes::ScouterDriftCustom => "scouter/drift/custom",
            Routes::ScouterDriftPsi => "scouter/drift/psi",
            Routes::ScouterDriftSpc => "scouter/drift/spc",

            // Scouter Profile Routes
            Routes::ScouterProfile => "scouter/profile",
            Routes::ScouterProfileStatus => "scouter/profile/status",
            Routes::ScouterProfileUi => "scouter/profile/ui",

            // Scouter User Routes
            Routes::ScouterUsers => "scouter/user",

            // Scouter Healthcheck
            Routes::ScouterHealthcheck => "scouter/healthcheck",

            Routes::User => "user",
        }
    }
}

impl Display for Routes {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

#[derive(Serialize, Deserialize)]
pub struct JwtToken {
    pub token: String,
}

#[derive(Serialize, Deserialize)]
pub struct Alive {
    pub alive: bool,
}

impl Default for Alive {
    fn default() -> Self {
        Self { alive: true }
    }
}
