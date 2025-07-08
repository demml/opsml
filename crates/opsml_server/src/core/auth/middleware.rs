use crate::core::auth::middleware::header::HeaderValue;
use crate::core::auth::schema::AuthError;
use crate::core::state::AppState;
use crate::core::user::utils::get_user;
use axum::http::{header, StatusCode};
use axum::response::IntoResponse;
use axum::{
    extract::{Request, State},
    middleware::Next,
    response::Json,
};
use axum_extra::extract::cookie::CookieJar;
use opsml_auth::permission::UserPermissions;
use opsml_sql::base::SqlClient;
use serde::Serialize;
use std::sync::Arc;
use tracing::{error, info};

#[derive(Debug, Serialize)]
pub struct ErrorResponse {
    pub status: &'static str,
    pub message: String,
}

pub async fn auth_api_middleware(
    cookie_jar: CookieJar,
    State(state): State<Arc<AppState>>,
    mut req: Request,
    next: Next,
) -> Result<impl IntoResponse, (StatusCode, Json<AuthError>)> {
    // print route being accessed

    // get the access token from the cookie or the authorization header
    let access_token = cookie_jar
        .get("access_token")
        .map(|cookie| cookie.value().to_string())
        .or_else(|| {
            req.headers()
                .get(header::AUTHORIZATION)
                .and_then(|auth_header| auth_header.to_str().ok())
                .and_then(|auth_value| {
                    auth_value
                        .strip_prefix("Bearer ")
                        .map(|token| token.to_owned())
                })
        });

    let access_token = access_token.ok_or_else(|| {
        error!("Error accessing route: {}", req.uri());
        (
            StatusCode::UNAUTHORIZED,
            Json(AuthError {
                error: "Unauthorized".to_string(),
                message: "No access token provided".to_string(),
            }),
        )
    })?;

    // validate the access token (this will also check if the token is expired)
    let auth_middleware = match state.auth_manager.validate_jwt(&access_token) {
        Ok(claims) => {
            let permissions = claims.permissions.clone();
            let group_permissions = claims.group_permissions.clone();
            UserPermissions {
                username: claims.sub,
                permissions,
                group_permissions,
            }
        }
        Err(_) => {
            info!("Access token expired, attempting refresh");

            let expired_claims = state
                .auth_manager
                .decode_jwt_without_validation(&access_token)
                .map_err(|_| {
                    (
                        StatusCode::UNAUTHORIZED,
                        Json(AuthError {
                            error: "Unauthorized".to_string(),
                            message: "Invalid token format".to_string(),
                        }),
                    )
                })?;

            let mut user = get_user(&state.sql_client, &expired_claims.sub, None)
                .await
                .map_err(|_| {
                    (
                        StatusCode::UNAUTHORIZED,
                        Json(AuthError {
                            error: "Unauthorized".to_string(),
                            message: "User not found".to_string(),
                        }),
                    )
                })?;

            // Validate stored refresh token
            if let Some(stored_refresh) = user.refresh_token.as_ref() {
                if state.auth_manager.validate_jwt(stored_refresh).is_ok() {
                    // Generate new tokens
                    let new_access_token =
                        state.auth_manager.generate_jwt(&user).map_err(|_| {
                            (
                                StatusCode::INTERNAL_SERVER_ERROR,
                                Json(AuthError {
                                    error: "Server Error".to_string(),
                                    message: "Failed to generate access token".to_string(),
                                }),
                            )
                        })?;
                    let new_refresh_token = state
                        .auth_manager
                        .generate_refresh_token(&user)
                        .map_err(|_| {
                            (
                                StatusCode::INTERNAL_SERVER_ERROR,
                                Json(AuthError {
                                    error: "Server Error".to_string(),
                                    message: "Failed to generate refresh token".to_string(),
                                }),
                            )
                        })?;

                    // Update refresh token in database
                    user.refresh_token = Some(new_refresh_token.clone());

                    if (state.sql_client.update_user(&user).await).is_err() {
                        return Err((
                            StatusCode::INTERNAL_SERVER_ERROR,
                            Json(AuthError {
                                error: "Server Error".to_string(),
                                message: "Failed to update refresh token".to_string(),
                            }),
                        ));
                    }

                    let auth_middleware = UserPermissions {
                        username: user.username,
                        permissions: user.permissions,
                        group_permissions: user.group_permissions,
                    };
                    req.extensions_mut().insert(auth_middleware);

                    // Add new token to request headers for downstream handlers
                    req.headers_mut().insert(
                        header::AUTHORIZATION,
                        HeaderValue::from_str(&format!("Bearer {new_access_token}")).unwrap(),
                    );

                    // Run the request and modify the response
                    let response = next.run(req).await;
                    let mut response = response.into_response();

                    // Add new token to response headers
                    response.headers_mut().insert(
                        header::AUTHORIZATION,
                        HeaderValue::from_str(&format!("Bearer {new_access_token}")).unwrap(),
                    );

                    return Ok(response);
                }
            }

            return Err((
                StatusCode::UNAUTHORIZED,
                Json(AuthError {
                    error: "Unauthorized".to_string(),
                    message: "No refresh token found".to_string(),
                }),
            ));
        }
    };

    // add the auth middleware to the request extensions
    req.extensions_mut().insert(auth_middleware);

    Ok(next.run(req).await)
}
