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
    AuthLogin,
    AuthRefresh,
    AuthValidate,
    AuthUiLogin,
    Card,
    CardCreate,
    CardDelete,
    CardList,
    CardVersion,
    CardUpdate,
    DeleteFiles,
    Files,
    Healthcheck,
    List,
    ListInfo,
    Multipart,
    CompleteMultipart,
    Presigned,
    StorageSettings,
    Encrypt,
    Decrypt,
    ExperimentMetrics,
    ExperimentMetricNames,
    ExperimentHardwareMetrics,
    ExperimentParameters,
}

impl Routes {
    pub fn as_str(&self) -> &str {
        match self {
            Routes::ArtifactKey => "files/key",
            Routes::Files => "files",
            Routes::Multipart => "files/multipart",
            Routes::CompleteMultipart => "files/multipart/complete",
            Routes::Presigned => "files/presigned",
            Routes::List => "files/list",
            Routes::ListInfo => "files/list/info",
            Routes::Encrypt => "files/encrypt",
            Routes::Decrypt => "files/decrypt",
            Routes::Healthcheck => "healthcheck",
            Routes::StorageSettings => "storage/settings",
            Routes::DeleteFiles => "files/delete",
            Routes::AuthLogin => "auth/login",
            Routes::AuthRefresh => "auth/refresh",
            Routes::AuthValidate => "auth/validate",
            Routes::AuthUiLogin => "auth/ui/login",
            Routes::Card => "card",
            Routes::CardCreate => "card/create",
            Routes::CardDelete => "card/delete",
            Routes::CardList => "card/list",
            Routes::CardVersion => "card/version",
            Routes::CardUpdate => "card/update",
            Routes::ExperimentMetrics => "experiment/metrics",
            Routes::ExperimentMetricNames => "experiment/metrics/names",
            Routes::ExperimentHardwareMetrics => "experiment/hardware/metrics",
            Routes::ExperimentParameters => "experiment/parameters",
        }
    }
}

#[derive(Serialize, Deserialize)]
pub struct JwtToken {
    pub token: String,
}
