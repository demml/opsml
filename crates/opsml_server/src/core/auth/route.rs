use crate::core::auth::schema::{
    Authenticated, LoginRequest, LoginResponse, LogoutResponse, SsoCallbackParams,
};
use crate::core::auth::util::{authenticate_user_with_sso, authenticate_user_with_sso_callback};
use crate::core::error::{internal_server_error, OpsmlServerError};

use crate::core::state::AppState;
use crate::core::user::schema::UserResponse;
use crate::core::user::utils::get_user;
use anyhow::{Context, Result};
use axum::extract::Query;
/// Route for debugging information
use axum::extract::State;
use axum::{
    http::header,
    http::header::HeaderMap,
    http::StatusCode,
    routing::{get, post},
    Json, Router,
};
use opsml_crypt::{generate_code_challenge, generate_code_verifier};
use opsml_sql::traits::*;
use opsml_types::JwtToken;
use opsml_utils::create_uuid7;
use password_auth::verify_password;
use rand::Rng;

use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::{debug, error, info, instrument};

use crate::core::auth::schema::SsoAuthUrl;

fn parse_header(
    headers: &HeaderMap,
    key: &str,
) -> Result<String, (StatusCode, Json<OpsmlServerError>)> {
    headers
        .get(key)
        .and_then(|v| v.to_str().ok())
        .map(|s| s.to_string())
        .ok_or_else(|| {
            error!("{} not found in headers", key);
            (
                StatusCode::BAD_REQUEST,
                Json(OpsmlServerError::key_header_not_found(key.to_string())),
            )
        })
}

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
) -> Result<Json<JwtToken>, (StatusCode, Json<OpsmlServerError>)> {
    // get Username and Password from headers
    let username = parse_header(&headers, "Username")?;
    let password = parse_header(&headers, "Password")?;

    let use_sso = headers
        .get("Use-SSO")
        .is_some_and(|v| v.to_str().is_ok_and(|s| s.eq_ignore_ascii_case("true")));

    // Validation flow
    // If SSO is enabled, and the Use-SSO header is present, the username and password will be authenticated against the SSO provider.
    // If SSO is not enabled, we will get the user from the database.
    let mut user = if state.auth_manager.is_sso_enabled() && use_sso {
        let user = authenticate_user_with_sso(&state, &username, &password).await?;
        info!("User authenticated with SSO: {}", username);
        user
    } else {
        // if SSO is not enabled, we will get the user from the database
        match get_user(&state.sql_client, &username, Some("basic")).await {
            Ok(user) => {
                // check if password is correct
                state
                    .auth_manager
                    .validate_user(&user, &password)
                    .map_err(|_| {
                        (
                            StatusCode::BAD_REQUEST,
                            Json(OpsmlServerError::user_validation_error()),
                        )
                    })?;

                user
            }
            Err(_) => {
                // create dummy pass to verify (this is to avoid time-based attacks)
                // if a user does not exist, the time it takes to return an error will be shorter than the validation step
                // so we create a dummy validation step to increase the time it takes to return an error
                verify_password(
                    "dummy_password",
                    &state.auth_manager.dummy_user.password_hash,
                )
                .map_err(|_| {
                    error!("Invalid password for user: {}", username);
                    (
                        StatusCode::BAD_REQUEST,
                        Json(OpsmlServerError::user_validation_error()),
                    )
                })?;

                // add small amount of random jitter (between 0 and 100 milliseconds)
                // to avoid timing attacks
                let millis = rand::rng().random_range(0..30);
                tokio::time::sleep(std::time::Duration::from_millis(millis)).await;

                return OpsmlServerError::user_validation_error()
                    .into_response(StatusCode::BAD_REQUEST);
            }
        }
    };

    // generate JWT token
    let jwt_token = state.auth_manager.generate_jwt(&user).map_err(|e| {
        error!("Failed to generate JWT token: {e}");
        internal_server_error(e, "Failed to generate JWT token")
    })?;

    // check if refresh token is already set.
    // if it is, check if its valid and return it
    // if it is not, generate a new one
    if let Some(refresh_token) = &user.refresh_token {
        if state.auth_manager.validate_jwt(refresh_token).is_ok() {
            return Ok(Json(JwtToken { token: jwt_token }));
        }
    }

    let refresh_token = state
        .auth_manager
        .generate_refresh_token(&user)
        .map_err(|e| {
            error!("Failed to generate refresh token: {e}");
            internal_server_error(e, "Failed to generate refresh token")
        })?;

    user.refresh_token = Some(refresh_token);

    // set refresh token in db
    state.sql_client.update_user(&user).await.map_err(|e| {
        error!("Failed to set refresh token in database: {e}");
        internal_server_error(e, "Failed to set refresh token in database")
    })?;

    // update scouter with new refresh token
    info!("User connected: {}", user.username);
    Ok(Json(JwtToken { token: jwt_token }))
}

#[instrument(skip_all)]
pub async fn ui_logout_handler(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
) -> Result<Json<LogoutResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let bearer_token = headers
        .get(header::AUTHORIZATION)
        .and_then(|auth_header| auth_header.to_str().ok())
        .and_then(|auth_value| {
            auth_value
                .strip_prefix("Bearer ")
                .map(|token| token.to_owned())
        });

    // validate token and then remove refresh token from user
    if let Some(bearer_token) = bearer_token {
        let claims = state
            .auth_manager
            .validate_jwt(&bearer_token)
            .map_err(|e| {
                (
                    StatusCode::UNAUTHORIZED,
                    Json(OpsmlServerError::jwt_decode_error(e)),
                )
            })?;
        info!("Logging out user: {}", claims.sub);
        // get user from database
        let mut user = match get_user(&state.sql_client, &claims.sub, None).await {
            Ok(user) => user,
            Err(_) => {
                return OpsmlServerError::user_validation_error()
                    .into_response(StatusCode::BAD_REQUEST);
            }
        };

        // invalidate the refresh token
        user.refresh_token = None;

        // update user in database
        state.sql_client.update_user(&user).await.map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(OpsmlServerError::refresh_token_error(e)),
            )
        })?;

        info!("User logged out: {}", user.username);
        return Ok(Json(LogoutResponse { logged_out: true }));
    }

    Err((
        StatusCode::UNAUTHORIZED,
        Json(OpsmlServerError::missing_token()),
    ))
}

/// Route for the login endpoint when using the UI and non-sso
///
/// # Parameters
///
/// - `state` - The application state
/// - `req` - The request body (username and password)
///
/// # Returns
///
/// Returns a `Result` containing either the JWT token or an error
#[instrument(skip_all)]
async fn ui_login_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<LoginRequest>,
) -> Result<Json<LoginResponse>, (StatusCode, Json<OpsmlServerError>)> {
    // get Username and Password from headers

    // get user from database
    let mut user = match get_user(&state.sql_client, &req.username, Some("basic")).await {
        Ok(user) => user,
        Err(_) => {
            error!("User not found {:?}", req.username);
            return Ok(Json(LoginResponse {
                authenticated: false,
                message: "User not found".to_string(),
                ..Default::default()
            }));
        }
    };

    // check if password is correct
    match state.auth_manager.validate_user(&user, &req.password) {
        Ok(_) => {}
        Err(_) => {
            error!("Invalid password for user {:?}", req.username);
            return Ok(Json(LoginResponse {
                authenticated: false,
                message: "Invalid password".to_string(),
                ..Default::default()
            }));
        }
    }

    // generate JWT token
    let jwt_token = state.auth_manager.generate_jwt(&user).map_err(|e| {
        error!("Failed to generate JWT token: {e}");
        internal_server_error(e, "Failed to generate JWT token")
    })?;

    let refresh_token = state
        .auth_manager
        .generate_refresh_token(&user)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(OpsmlServerError::refresh_token_error(e)),
            )
        })?;

    user.refresh_token = Some(refresh_token);

    // set refresh token in db
    state.sql_client.update_user(&user).await.map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(OpsmlServerError::refresh_token_error(e)),
        )
    })?;

    info!("User logged in: {}", user.username);
    Ok(Json(LoginResponse {
        authenticated: true,
        message: "User authenticated".to_string(),
        username: user.username,
        jwt_token,
        group_permissions: user.group_permissions,
        permissions: user.permissions,
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
#[instrument(skip_all)]
pub async fn api_refresh_token_handler(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
) -> Result<Json<JwtToken>, (StatusCode, Json<OpsmlServerError>)> {
    let bearer_token = headers
        .get(header::AUTHORIZATION)
        .and_then(|auth_header| auth_header.to_str().ok())
        .and_then(|auth_value| {
            auth_value
                .strip_prefix("Bearer ")
                .map(|token| token.to_owned())
        });

    if let Some(bearer_token) = bearer_token {
        // validate the bearer token
        let claims = state
            .auth_manager
            .decode_jwt_without_validation(&bearer_token)
            .map_err(|e| {
                (
                    StatusCode::UNAUTHORIZED,
                    Json(OpsmlServerError::jwt_decode_error(e)),
                )
            })?;

        // get user from database
        let mut user = match get_user(&state.sql_client, &claims.sub, None).await {
            Ok(user) => user,
            Err(_) => {
                return OpsmlServerError::user_validation_error()
                    .into_response(StatusCode::BAD_REQUEST);
            }
        };

        // validate refresh token (if this fails, we return an error)
        // We are ensuring that the refresh token is still valid before generating a new one.
        state
            .auth_manager
            .validate_jwt(user.refresh_token.as_deref().unwrap_or(""))
            .map_err(|_| {
                (
                    StatusCode::UNAUTHORIZED,
                    Json(OpsmlServerError::refresh_token_error(
                        "Invalid refresh token",
                    )),
                )
            })?;

        // generate new JWT token
        let jwt_token = state.auth_manager.generate_jwt(&user).map_err(|_| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(OpsmlServerError::failed_token_generation()),
            )
        })?;

        // generate new refresh token
        info!("Generating new refresh token for user: {}", user.username);
        let refresh_token = state
            .auth_manager
            .generate_refresh_token(&user)
            .map_err(|e| {
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(OpsmlServerError::refresh_token_error(e)),
                )
            })?;

        user.refresh_token = Some(refresh_token);

        // set refresh token in db
        state.sql_client.update_user(&user).await.map_err(|e| {
            error!("Failed to set refresh token in database: {e}");
            internal_server_error(e, "Failed to set refresh token in database")
        })?;

        Ok(Json(JwtToken { token: jwt_token }))
    } else {
        OpsmlServerError::refresh_token_not_found().into_response(StatusCode::BAD_REQUEST)
    }
}

#[instrument(skip_all)]
async fn validate_jwt_token(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
) -> Result<Json<Authenticated>, (StatusCode, Json<OpsmlServerError>)> {
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
            Ok(claims) => {
                let user = match get_user(&state.sql_client, &claims.sub, None).await {
                    Ok(user) => user,
                    Err(_) => {
                        return OpsmlServerError::user_validation_error()
                            .into_response(StatusCode::BAD_REQUEST);
                    }
                };
                Ok(Json(Authenticated {
                    is_authenticated: true,
                    user_response: UserResponse {
                        username: user.username,
                        permissions: user.permissions,
                        group_permissions: user.group_permissions,
                        active: user.active,
                        email: user.email,
                        role: user.role,
                        favorite_spaces: user.favorite_spaces,
                    },
                }))
            }
            Err(_) => OpsmlServerError::invalid_token().into_response(StatusCode::UNAUTHORIZED),
        }
    } else {
        info!("No bearer token found");
        Ok(Json(Authenticated {
            is_authenticated: false,
            ..Default::default()
        }))
    }
}

#[instrument(skip_all)]
async fn get_sso_authorization_url(
    State(state): State<Arc<AppState>>,
) -> Result<Json<SsoAuthUrl>, (StatusCode, Json<OpsmlServerError>)> {
    if !state.auth_manager.is_sso_enabled() {
        return Err((
            StatusCode::NOT_IMPLEMENTED,
            Json(OpsmlServerError::sso_not_enabled()),
        ));
    }

    let provider = state.auth_manager.get_sso_provider().map_err(|e| {
        error!("SSO provider not set: {e}");
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(OpsmlServerError::sso_provider_not_set()),
        )
    })?;

    let state = create_uuid7();
    let code_verifier = generate_code_verifier();
    let code_challenge = generate_code_challenge(&code_verifier);
    let code_challenge_method = "S256".to_string();
    let url = provider.authorization_url(&state, &code_challenge, &code_challenge_method);

    Ok(Json(SsoAuthUrl {
        url,
        code_challenge,
        code_challenge_method,
        code_verifier,
        state,
    }))
}

#[instrument(skip_all)]
async fn exchange_callback_token(
    State(state): State<Arc<AppState>>,
    Query(params): Query<SsoCallbackParams>,
) -> Result<Json<LoginResponse>, (StatusCode, Json<OpsmlServerError>)> {
    info!("Exchanging SSO callback token");
    let code = params.code;
    let code_verifier = params.code_verifier;

    let mut user = authenticate_user_with_sso_callback(&state, &code, &code_verifier).await?;

    // generate JWT token
    let jwt_token = state.auth_manager.generate_jwt(&user).map_err(|e| {
        error!("Failed to generate JWT token: {e}");
        internal_server_error(e, "Failed to generate JWT token")
    })?;

    let refresh_token = state
        .auth_manager
        .generate_refresh_token(&user)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(OpsmlServerError::refresh_token_error(e)),
            )
        })?;

    user.refresh_token = Some(refresh_token);

    // set refresh token in db
    state.sql_client.update_user(&user).await.map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(OpsmlServerError::refresh_token_error(e)),
        )
    })?;

    info!("User logged in with sso: {}", user.username);

    Ok(Json(LoginResponse {
        authenticated: true,
        message: "User authenticated".to_string(),
        username: user.username,
        jwt_token,
        group_permissions: user.group_permissions,
        permissions: user.permissions,
    }))
}

pub async fn get_auth_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{prefix}/auth/login"), get(api_login_handler))
            .route(
                &format!("{prefix}/auth/refresh"),
                get(api_refresh_token_handler),
            )
            .route(&format!("{prefix}/auth/validate"), get(validate_jwt_token))
            .route(&format!("{prefix}/auth/ui/login"), post(ui_login_handler))
            .route(&format!("{prefix}/auth/ui/logout"), get(ui_logout_handler))
            .route(
                &format!("{prefix}/auth/sso/authorization"),
                get(get_sso_authorization_url),
            )
            .route(
                &format!("{prefix}/auth/sso/callback"),
                get(exchange_callback_token),
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
