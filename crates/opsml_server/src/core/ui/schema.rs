use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct CardsRequest {
    pub respository: Option<String>,
}
