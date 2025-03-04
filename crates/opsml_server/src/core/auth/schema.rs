use serde::Serialize;

#[derive(Serialize)]
pub struct AuthError {
    pub error: String,
    pub message: String,
}

#[derive(Serialize)]
pub struct Authenticated {
    pub is_authenticated: bool,
}

#[derive(Serialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

#[derive(Serialize)]
pub struct LoginResponse {
    pub username: String,
    pub jwt_token: String,
}
