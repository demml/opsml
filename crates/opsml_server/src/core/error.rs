use axum::http::StatusCode;
use axum::Json;
use serde_json::json;

pub fn internal_server_error<E: std::fmt::Display>(
    error: E,
) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": error.to_string() })),
    )
}
