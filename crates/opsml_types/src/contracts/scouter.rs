use scouter_client::ProfileRequest;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct UpdateProfileRequest {
    pub uid: String,
    pub profile_uri: String,
    pub request: ProfileRequest,
}

impl UpdateProfileRequest {
    pub fn get_metadata(&self) -> String {
        let metadata = serde_json::json!({
            "space": self.request.space,
            "drift_type": self.request.drift_type.to_string(),
        });
        serde_json::to_string(&metadata)
            .unwrap_or_else(|e| format!("Failed to serialize ProfileRequest: {e}"))
    }
}
