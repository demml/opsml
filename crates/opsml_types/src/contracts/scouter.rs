use scouter_client::ProfileRequest;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct UpdateProfileRequest {
    pub uid: String,
    pub request: ProfileRequest,
}
