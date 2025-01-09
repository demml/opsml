use crate::core::auth::schema::AuthError;
use crate::core::state::AppState;
use axum::http::{header, StatusCode};
use axum::response::IntoResponse;
use axum::{
    extract::{Request, State},
    middleware::Next,
    response::Json,
};
use axum_extra::extract::cookie::CookieJar;
use opsml_auth::permission::UserPermissions;
use serde::Serialize;
use std::sync::Arc;

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
    // if auth is disabled, just return
    if !state.config.auth_settings.enabled {
        req.extensions_mut().insert(UserPermissions {
            username: "".to_string(),
            permissions: vec![],
            group_permissions: vec![],
        });

        return Ok(next.run(req).await);
    }

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
