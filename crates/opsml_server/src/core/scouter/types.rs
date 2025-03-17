use scouter_client::ProfileRequest;
use serde::Deserialize;

#[derive(Deserialize, Debug, Clone)]
pub struct UpdateProfileRequest {
    pub uid: String,
    pub repository: String,
    pub request: ProfileRequest,
}
