use crate::core::auth::schema::{Authenticated, LoginRequest, LoginResponse};
use crate::core::state::AppState;
use crate::core::user::utils::get_user;
use anyhow::{Context, Result};
/// Route for debugging information
use axum::extract::State;
use axum::{
    http::header,
    http::header::HeaderMap,
    http::StatusCode,
    routing::{get, post},
    Json, Router,
};
use opsml_client::JwtToken;
use opsml_sql::base::SqlClient;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::{debug, error, instrument};

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
#[instrument(skip_all)]
pub async fn api_login_handler(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
) -> Result<Json<JwtToken>, (StatusCode, Json<serde_json::Value>)> {
    // get Username and Password from headers
    let username = headers
        .get("Username")
        .ok_or_else(|| {
            error!("Username not found in headers");
            (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({ "error": "Username not found in headers" })),
            )
        })?
        .to_str()
        .map_err(|_| {
            error!("Invalid UTF-8 in Username header");
            (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({ "error": "Invalid username format" })),
            )
        })?
        .to_string();

    let password = headers
        .get("Password")
        .ok_or_else(|| {
            error!("Password not found in headers");
            (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({ "error": "Password not found in headers" })),
            )
        })?
        .to_str()
        .map_err(|_| {
            error!("Invalid UTF-8 in Password header");
            (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({ "error": "Invalid password format" })),
            )
        })?
        .to_string();

    // get user from database
    let mut user = get_user(&state.sql_client, &username).await?;
    // check if password is correct
    state
        .auth_manager
        .validate_user(&user, &password)
        .map_err(|e| {
            error!("Failed to validate user: {}", e);
            (StatusCode::UNAUTHORIZED, Json(serde_json::json!({})))
        })?;

    // we may get multiple requests for the same user (setting up storage and registries), so we
    // need to check if current refresh and jwt tokens are valid and return them if they are

    // generate JWT token
    let jwt_token = state.auth_manager.generate_jwt(&user).map_err(|e| {
        error!("Failed to generate JWT token: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({})),
        )
    })?;

    // check if refresh token is already set.
    // if it is, check if its valid and return it
    // if it is not, generate a new one
    if let Some(refresh_token) = &user.refresh_token {
        if state
            .auth_manager
            .validate_refresh_token(refresh_token)
            .is_ok()
        {
            return Ok(Json(JwtToken { token: jwt_token }));
        }
    }

    let refresh_token = state
        .auth_manager
        .generate_refresh_token(&user)
        .map_err(|e| {
            error!("Failed to generate refresh token: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    user.refresh_token = Some(refresh_token);

    // set refresh token in db
    state.sql_client.update_user(&user).await.map_err(|e| {
        error!("Failed to set refresh token in database: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({})),
        )
    })?;

    // update scouter with new refresh token

    Ok(Json(JwtToken { token: jwt_token }))
}

/// Route for the login endpoint when using the API
///
/// # Parameters
///
/// - `state` - The application state
/// - `req` - The request body (username and password)
///
/// # Returns
///
/// Returns a `Result` containing either the JWT token or an error
async fn ui_login_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<LoginRequest>,
) -> Result<Json<LoginResponse>, (StatusCode, Json<serde_json::Value>)> {
    // get Username and Password from headers

    // get user from database
    let mut user = get_user(&state.sql_client, &req.username).await?;

    // check if password is correct
    state
        .auth_manager
        .validate_user(&user, &req.password)
        .map_err(|e| {
            error!("Failed to validate user: {}", e);
            (StatusCode::UNAUTHORIZED, Json(serde_json::json!({})))
        })?;

    // generate JWT token
    let jwt_token = state.auth_manager.generate_jwt(&user).map_err(|e| {
        error!("Failed to generate JWT token: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({})),
        )
    })?;
    let refresh_token = state
        .auth_manager
        .generate_refresh_token(&user)
        .map_err(|e| {
            error!("Failed to generate refresh token: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    user.refresh_token = Some(refresh_token);

    // set refresh token in db
    state.sql_client.update_user(&user).await.map_err(|e| {
        error!("Failed to set refresh token in database: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({})),
        )
    })?;

    Ok(Json(LoginResponse {
        username: user.username,
        jwt_token,
    }))
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
        let mut user = get_user(&state.sql_client, &claims.sub).await?;

        // generate JWT token
        let jwt_token = state.auth_manager.generate_jwt(&user).map_err(|e| {
            error!("Failed to generate JWT token: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

        // generate refresh token
        let refresh_token = state
            .auth_manager
            .generate_refresh_token(&user)
            .map_err(|e| {
                error!("Failed to generate refresh token: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({})),
                )
            })?;

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

async fn validate_jwt_token(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
) -> Result<Json<Authenticated>, (StatusCode, Json<serde_json::Value>)> {
    let bearer_token = headers
        .get(header::AUTHORIZATION)
        .and_then(|auth_header| auth_header.to_str().ok())
        .and_then(|auth_value| {
            auth_value
                .strip_prefix("Bearer ")
                .map(|token| token.to_owned())
        });

    if let Some(bearer_token) = bearer_token {
        debug!("Validating JWT token");
        match state.auth_manager.validate_jwt(&bearer_token) {
            Ok(_) => Ok(Json(Authenticated {
                is_authenticated: true,
            })),
            Err(e) => {
                error!("Failed to validate JWT token: {}", e);
                Err((
                    StatusCode::UNAUTHORIZED,
                    Json(serde_json::json!({ "error": "Invalid token" })),
                ))
            }
        }
    } else {
        debug!("No bearer token found");
        Err((
            StatusCode::UNAUTHORIZED,
            Json(serde_json::json!({ "error": "No bearer token found" })),
        ))
    }
}

pub async fn get_auth_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{}/auth/login", prefix), get(api_login_handler))
            .route(
                &format!("{}/auth/refresh", prefix),
                get(api_refresh_token_handler),
            )
            .route(
                &format!("{}/auth/validate", prefix),
                get(validate_jwt_token),
            )
            .route(&format!("{}/auth/ui/login", prefix), post(ui_login_handler))
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
