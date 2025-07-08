use crate::core::error::{internal_server_error, OpsmlServerError};
use crate::core::scouter;
use crate::core::state::AppState;
use crate::core::user::schema::{
    CreateUserRequest, CreateUserResponse, CreateUserUiResponse, RecoveryResetRequest,
    UpdateUserRequest, UserListResponse, UserResponse,
};
use crate::core::user::utils::get_user as get_user_from_db;
use anyhow::{Context, Result};
use axum::extract::Path;
use axum::{
    extract::State,
    http::StatusCode,
    routing::{delete, get, post, put},
    Extension, Json, Router,
};

use opsml_auth::permission::UserPermissions;
use opsml_auth::util::generate_recovery_codes_with_hashes;
use opsml_sql::base::SqlClient;
use opsml_sql::schemas::schema::User;
use opsml_types::RequestType;
use password_auth::generate_hash;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::{error, info, instrument};

use super::schema::ResetPasswordResponse;

/// Create a new user via SDK.
#[instrument(skip_all)]
async fn create_user(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(create_req): Json<CreateUserRequest>,
) -> Result<Json<CreateUserResponse>, (StatusCode, Json<OpsmlServerError>)> {
    // Check if requester has admin permissions

    // need to ensure that a create request that has admin perms can only be created by an admin
    if !perms.group_permissions.contains(&"admin".to_string())
        && create_req
            .group_permissions
            .as_ref()
            .is_some_and(|p| p.contains(&"admin".to_string()))
    {
        return OpsmlServerError::need_admin_permission().into_response(StatusCode::FORBIDDEN);
    }

    // Check if user already exists
    // This route is only use from creating non-sso users, so auth_type is None
    if let Ok(Some(_)) = state.sql_client.get_user(&create_req.username, None).await {
        return OpsmlServerError::user_already_exists().into_response(StatusCode::CONFLICT);
    }

    // Hash the password
    let password_hash = generate_hash(&create_req.password);

    // generate recovery codes
    let (recovery_codes, hashed_recovery_codes) = generate_recovery_codes_with_hashes(4);

    // Create the user
    let mut user = User::new(
        create_req.username,
        password_hash,
        create_req.email,
        hashed_recovery_codes,
        create_req.permissions,
        create_req.group_permissions,
        create_req.role,
        None,
        None,
    );

    // Set active status if provided
    if let Some(active) = create_req.active {
        user.active = active;
    }

    // Save to database
    if let Err(e) = state.sql_client.insert_user(&user).await {
        error!("Failed to create user: {e}");
        return Err(internal_server_error(e, "Failed to create user"));
    }

    info!("User {} created successfully", user.username);

    // pass to scouter if enabled
    if state.scouter_client.enabled {
        let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
            error!("Failed to exchange token for scouter: {e}");
            internal_server_error(e, "Failed to exchange token for scouter")
        })?;

        state
            .scouter_client
            .request(
                scouter::Routes::Users,
                RequestType::Post,
                Some(serde_json::json!(&user)),
                None,
                None,
                &exchange_token,
            )
            .await
            .map_err(|e| {
                error!("Failed to create user in scouter: {e}");
                internal_server_error(e, "Failed to create user in scouter")
            })?;
    }

    Ok(Json(CreateUserResponse::new(
        UserResponse::from(user),
        recovery_codes,
    )))
}

/// Create a new user via UI. This will always return a response so that
/// errors will be handled in the UI.
#[instrument(skip_all)]
async fn register_user_from_ui(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(create_req): Json<CreateUserRequest>,
) -> Result<Json<CreateUserUiResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let response = create_user(
        axum::extract::State(state),
        axum::extract::Extension(perms),
        axum::extract::Json(create_req),
    )
    .await;

    match response {
        Ok(res) => Ok(Json(CreateUserUiResponse {
            registered: true,
            response: Some(res.0),
            error: None,
        })),
        Err((_, err)) => {
            error!("Failed to create user: {:?}", err.0.error);
            Ok(Json(CreateUserUiResponse {
                registered: false,
                response: None,
                error: Some(err.0.error),
            }))
        }
    }
}

/// Get a user by username
#[instrument(skip_all)]
async fn get_user(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(username): Path<String>,
) -> Result<Json<UserResponse>, (StatusCode, Json<OpsmlServerError>)> {
    // Check permissions - user can only get their own data or admin can get any user
    let is_admin = perms.group_permissions.contains(&"admin".to_string());
    let is_self = perms.username == username;

    if !is_admin && !is_self {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    // Get user from database
    let user = match get_user_from_db(&state.sql_client, &username, None).await {
        Ok(user) => user,
        Err(e) => return Err(e),
    };

    info!("User {} retrieved successfully", user.username);

    Ok(Json(UserResponse::from(user)))
}

/// List all users
///
/// Requires admin permissions
#[instrument(skip_all)]
async fn list_users(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
) -> Result<Json<UserListResponse>, (StatusCode, Json<OpsmlServerError>)> {
    // Check if requester has admin permissions
    if !perms.group_permissions.contains(&"admin".to_string()) {
        return OpsmlServerError::need_admin_permission().into_response(StatusCode::FORBIDDEN);
    }

    // Get users from database
    let users = match state.sql_client.get_users().await {
        Ok(users) => users,
        Err(e) => {
            error!("Failed to list users: {e}");
            return Err(internal_server_error(e, "Failed to list users"));
        }
    };

    let user_responses: Vec<UserResponse> = users.into_iter().map(UserResponse::from).collect();

    Ok(Json(UserListResponse {
        users: user_responses,
    }))
}

/// Update a user
#[instrument(skip_all)]
async fn update_user(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(username): Path<String>,
    Json(update_req): Json<UpdateUserRequest>,
) -> Result<Json<UserResponse>, (StatusCode, Json<OpsmlServerError>)> {
    // Check permissions - user can only update their own data or admin can update any user
    let is_admin = perms.group_permissions.contains(&"admin".to_string());
    let is_self = perms.username == username;

    if !is_admin && !is_self {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    // Get the current user state
    let mut user = get_user_from_db(&state.sql_client, &username, None).await?;

    // Update fields based on request
    if let Some(password) = update_req.password {
        user.password_hash = generate_hash(&password);
    }

    if let Some(favorite_spaces) = update_req.favorite_spaces {
        // make  request favorite into unique list
        let hash_set: std::collections::HashSet<_> = favorite_spaces.into_iter().collect();
        user.favorite_spaces = hash_set.into_iter().collect();
    }

    // Only admins can change permissions
    if is_admin {
        if let Some(permissions) = update_req.permissions {
            let hash_set: std::collections::HashSet<_> = permissions.into_iter().collect();
            user.permissions = hash_set.into_iter().collect();
        }

        if let Some(group_permissions) = update_req.group_permissions {
            let hash_set: std::collections::HashSet<_> = group_permissions.into_iter().collect();
            user.group_permissions = hash_set.into_iter().collect();
        }

        if let Some(active) = update_req.active {
            user.active = active;
        }
    }

    // Save updated user to database
    if let Err(e) = state.sql_client.update_user(&user).await {
        error!("Failed to update user: {e}");
        return Err(internal_server_error(e, "Failed to update user"));
    }

    info!("User {} updated successfully", user.username);

    // pass to scouter if enabled
    if state.scouter_client.enabled {
        let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
            error!("Failed to exchange token for scouter: {e}");
            internal_server_error(e, "Failed to exchange token for scouter")
        })?;
        state
            .scouter_client
            .request(
                scouter::Routes::Users,
                RequestType::Put,
                Some(serde_json::json!(&user)),
                None,
                None,
                &exchange_token,
            )
            .await
            .map_err(|e| {
                error!("Failed to create user in scouter: {e}");
                internal_server_error(e, "Failed to create user in scouter")
            })?;
        info!("User {} updated in scouter", user.username);
    }

    Ok(Json(UserResponse::from(user)))
}

/// Delete a user
///
/// Requires admin permissions
#[instrument(skip_all)]
async fn delete_user(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,

    Path(username): Path<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<OpsmlServerError>)> {
    // Check if requester has admin permissions
    if !perms.group_permissions.contains(&"admin".to_string()) {
        return OpsmlServerError::need_admin_permission().into_response(StatusCode::FORBIDDEN);
    }

    // Prevent deleting the last admin user
    let is_last_admin = match state.sql_client.is_last_admin(&username).await {
        Ok(is_last) => is_last,
        Err(e) => {
            error!("Failed to check if user is last admin: {e}");
            return Err(internal_server_error(
                e,
                "Failed to check if user is last admin",
            ));
        }
    };

    if is_last_admin {
        return OpsmlServerError::cannot_delete_last_admin().into_response(StatusCode::FORBIDDEN);
    }

    // Delete in scouter first
    // (if we delete in opsml before scouter, we won't be able to get user and token)
    if state.scouter_client.enabled {
        let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
            error!("Failed to exchange token for scouter: {e}");
            internal_server_error(e, "Failed to exchange token for scouter")
        })?;

        state
            .scouter_client
            .delete_user(&username, &exchange_token)
            .await
            .map_err(|e| {
                error!("Failed to delete user in scouter: {e}");
                internal_server_error(e, "Failed to delete user in scouter")
            })?;

        info!("User {} deleted in scouter", username);
    }

    // Delete the user
    if let Err(e) = state.sql_client.delete_user(&username).await {
        error!("Failed to delete user: {e}");
        return Err(internal_server_error(e, "Failed to delete user"));
    }

    info!("User {} deleted successfully", username);

    Ok(Json(serde_json::json!({"success": true})))
}

#[instrument(skip_all)]
async fn reset_password_with_recovery(
    State(state): State<Arc<AppState>>,
    Json(req): Json<RecoveryResetRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<OpsmlServerError>)> {
    // Get user and their recovery codes
    let mut user = get_user_from_db(&state.sql_client, &req.username, Some("basic")).await?;

    // Find and verify the recovery code
    let code_index = match user.hashed_recovery_codes.iter().position(|stored_hash| {
        password_auth::verify_password(&req.recovery_code, stored_hash)
            .map(|_| true)
            .unwrap_or(false)
    }) {
        Some(index) => index,
        None => {
            return Err((
                StatusCode::UNAUTHORIZED,
                Json(OpsmlServerError::invalid_recovery_code()),
            ))
        }
    };
    // Update password
    user.password_hash = generate_hash(&req.new_password);

    // Remove used recovery code
    user.hashed_recovery_codes.remove(code_index);

    // Save changes
    if let Err(e) = state.sql_client.update_user(&user).await {
        return Err(internal_server_error(e, "Failed to update password"));
    }

    Ok(Json(serde_json::json!(ResetPasswordResponse {
        message: "Password updated successfully".to_string(),
        remaining_recovery_codes: user.hashed_recovery_codes.len(),
    })))
}

pub async fn get_user_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{prefix}/user"), post(create_user))
            .route(
                &format!("{prefix}/user/register"),
                post(register_user_from_ui),
            )
            .route(&format!("{prefix}/user"), get(list_users))
            .route(
                &format!("{prefix}/user/reset-password/recovery"),
                post(reset_password_with_recovery),
            )
            .route(&format!("{prefix}/user/{{username}}"), get(get_user))
            .route(&format!("{prefix}/user/{{username}}"), put(update_user))
            .route(&format!("{prefix}/user/{{username}}"), delete(delete_user))
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create user router");
            Err(anyhow::anyhow!("Failed to create user router"))
                .context("Panic occurred while creating the router")
        }
    }
}
