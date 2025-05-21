use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct AuthError {
    pub error: String,
    pub message: String,
}

#[derive(Serialize)]
pub struct Authenticated {
    pub is_authenticated: bool,
}

#[derive(Serialize, Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

#[derive(Serialize, Default)]
pub struct LoginResponse {
    pub authenticated: bool,
    pub message: String,
    pub username: String,
    pub jwt_token: String,
    pub permissions: Vec<String>,
    pub group_permissions: Vec<String>,
}
