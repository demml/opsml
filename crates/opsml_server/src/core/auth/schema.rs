use serde::Serialize;

#[derive(Serialize)]
pub struct AuthError {
    pub error: String,
    pub message: String,
}
