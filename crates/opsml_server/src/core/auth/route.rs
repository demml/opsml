use crate::core::state::AppState;
use anyhow::{Context, Result};
/// Route for debugging information
use axum::extract::State;
use axum::{http::header, http::header::HeaderMap, http::StatusCode, routing::get, Json, Router};
use opsml_sql::base::SqlClient;
use opsml_types::JwtToken;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::error;

/// Route for the login endpoint when using the API
///
/// # Parameters
///
/// - `state` - The application state
/// - `headers` - The headers from the request
///
/// # Returns
///
/// Returns a `Result` containing either the JWT token or an error
pub async fn api_login_handler(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
) -> Result<Json<JwtToken>, (StatusCode, Json<serde_json::Value>)> {
    // get Username and Password from headers
    let username = headers
        .get("Username")
        .expect("Username not found in headers")
        .to_str()
        .expect("Failed to convert Username to string")
        .to_string();

    let password = headers
        .get("Password")
        .expect("Password not found in headers")
        .to_str()
        .expect("Failed to convert Password to string")
        .to_string();

    // get user from database
    let mut user = state.sql_client.get_user(&username).await.map_err(|e| {
        error!("Failed to get user from database: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({})),
        )
    })?;

    // check if password is correct
    state
        .auth_manager
        .validate_user(&user, &password)
        .map_err(|e| {
            error!("Failed to validate user: {}", e);
            (StatusCode::UNAUTHORIZED, Json(serde_json::json!({})))
        })?;

    // generate JWT token
    let jwt_token = state.auth_manager.generate_jwt(&user);
    let refresh_token = state.auth_manager.generate_refresh_token(&user);

    user.refresh_token = Some(refresh_token);

    // set refresh token in db
    state.sql_client.update_user(&user).await.map_err(|e| {
        error!("Failed to set refresh token in database: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({})),
        )
    })?;

    Ok(Json(JwtToken { token: jwt_token }))
}

/// Route for the refresh token endpoint when using the API
///
/// # Parameters
///
/// - `state` - The application state
/// - `headers` - The headers from the request
///
/// # Returns
///
/// Returns a `Result` containing either the JWT token or an error
pub async fn api_refresh_token_handler(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
) -> Result<Json<JwtToken>, (StatusCode, Json<serde_json::Value>)> {
    let bearer_token = headers
        .get(header::AUTHORIZATION)
        .and_then(|auth_header| auth_header.to_str().ok())
        .and_then(|auth_value| {
            auth_value
                .strip_prefix("Bearer ")
                .map(|token| token.to_owned())
        });

    if let Some(bearer_token) = bearer_token {
        // validate the refresh token
        let claims = state
            .auth_manager
            .decode_jwt_without_validation(&bearer_token)
            .map_err(|e| {
                error!("Failed to decode JWT token: {}", e);
                (StatusCode::UNAUTHORIZED, Json(serde_json::json!({})))
            })?;

        // get user from database
        let mut user = state.sql_client.get_user(&claims.sub).await.map_err(|e| {
            error!("Failed to get user from database: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

        // generate JWT token
        let jwt_token = state.auth_manager.generate_jwt(&user);

        // generate refresh token
        let refresh_token = state.auth_manager.generate_refresh_token(&user);

        user.refresh_token = Some(refresh_token);

        // set refresh token in db
        state.sql_client.update_user(&user).await.map_err(|e| {
            error!("Failed to set refresh token in database: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

        Ok(Json(JwtToken { token: jwt_token }))
    } else {
        Err((
            StatusCode::UNAUTHORIZED,
            Json(serde_json::json!({ "error": "No refresh token found" })),
        ))
    }
}

pub async fn get_auth_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{}/auth/api/login", prefix),
                get(api_login_handler),
            )
            .route(
                &format!("{}/auth/api/refresh", prefix),
                get(api_refresh_token_handler),
            )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create auth router");
            // panic
            Err(anyhow::anyhow!("Failed to create auth router"))
                .context("Panic occurred while creating the router")
        }
    }
}
