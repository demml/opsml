use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct CardsRequest {
    pub space: Option<String>,
}
