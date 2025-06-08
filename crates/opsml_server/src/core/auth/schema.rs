use crate::core::user::schema::UserResponse;
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct AuthError {
    pub error: String,
    pub message: String,
}

#[derive(Serialize, Deserialize, Default)]
pub struct Authenticated {
    pub is_authenticated: bool,
    pub user_response: UserResponse,
}

#[derive(Serialize, Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

#[derive(Serialize, Deserialize)]
pub struct SsoAuthUrl {
    pub url: String,
    pub code_challenge: String,
    pub code_challenge_method: String,
    pub code_verifier: String,
    pub state: String,
}

#[derive(Serialize, Deserialize)]
pub struct SsoCallbackParams {
    pub code: String,
    pub code_verifier: String,
}

#[derive(Serialize, Deserialize, Default)]
pub struct LoginResponse {
    pub authenticated: bool,
    pub message: String,
    pub username: String,
    pub jwt_token: String,
    pub permissions: Vec<String>,
    pub group_permissions: Vec<String>,
}

#[derive(Serialize, Deserialize, Default)]
pub struct LogoutResponse {
    pub logged_out: bool,
}
