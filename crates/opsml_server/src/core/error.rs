use crate::core::audit::{spawn_audit_task, AuditArgs};
use axum::http::StatusCode;
use axum::Json;
use opsml_sql::enums::client::SqlClientEnum;
use serde_json::json;
use std::sync::Arc;

pub fn internal_server_error<E: std::fmt::Display>(
    error: E,
    message: &str,
) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({  "error": format!("{}: {}", message, error) })),
    )
}

pub fn internal_server_error_with_audit<E: std::fmt::Display>(
    error: E,
    message: &str,
    audit_args: AuditArgs,
    sql_client: Arc<SqlClientEnum>,
) -> (StatusCode, Json<serde_json::Value>) {
    spawn_audit_task(
        audit_args.with_error(format!("{}: {}", message, error)),
        sql_client,
    );

    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({  "error": format!("{}: {}", message, error) })),
    )
}
