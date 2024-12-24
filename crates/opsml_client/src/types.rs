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
    AuthApiLogin,
    AuthApiRefresh,
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
    Presigned,
    StorageSettings,
}

impl Routes {
    pub fn as_str(&self) -> &str {
        match self {
            Routes::Files => "files",
            Routes::Multipart => "files/multipart",
            Routes::Presigned => "files/presigned",
            Routes::List => "files/list",
            Routes::ListInfo => "files/list/info",
            Routes::Healthcheck => "healthcheck",
            Routes::StorageSettings => "storage/settings",
            Routes::DeleteFiles => "files/delete",
            Routes::AuthApiLogin => "auth/api/login",
            Routes::AuthApiRefresh => "auth/api/refresh",
            Routes::Card => "card",
            Routes::CardCreate => "card/create",
            Routes::CardDelete => "card/delete",
            Routes::CardList => "card/list",
            Routes::CardVersion => "card/version",
            Routes::CardUpdate => "card/update",
        }
    }
}

#[derive(Serialize, Deserialize)]
pub struct JwtToken {
    pub token: String,
}
