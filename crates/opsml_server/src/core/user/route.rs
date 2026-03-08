use crate::core::error::{OpsmlServerError, internal_server_error};
use crate::core::scouter;
use crate::core::state::AppState;
use crate::core::user::schema::{
    AssignRolesRequest, CreateUserRequest, CreateUserResponse, EffectivePermissionsResponse,
    UpdateUserRequest, UserListResponse, UserResponse,
};
use crate::core::user::utils::get_user as get_user_from_db;
use anyhow::{Context, Result};
use axum::extract::Path;
use axum::{
    Extension, Json, Router,
    extract::State,
    http::StatusCode,
    routing::{delete, get, post, put},
};

use opsml_auth::permission::{UserPermissions, resolve_effective_permissions};
use opsml_auth::util::generate_recovery_codes_with_hashes;
use opsml_sql::schemas::schema::User;
use opsml_sql::traits::{RoleLogicTrait, UserLogicTrait};
use opsml_types::RequestType;
use password_auth::generate_hash;
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::{error, info, instrument};

/// Create a new user via SDK.
#[instrument(skip_all)]
pub async fn create_user(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(create_req): Json<CreateUserRequest>,
) -> Result<Json<CreateUserResponse>, (StatusCode, Json<OpsmlServerError>)> {
    // Check if requester has admin permissions

    // need to ensure that a create request that has admin perms can only be created by an admin
    if !perms.is_admin()
        && create_req
            .roles
            .as_ref()
            .is_some_and(|p| p.contains(&"admin".to_string()))
    {
        return OpsmlServerError::need_admin_permission().into_response(StatusCode::FORBIDDEN);
    }

    // Check if user already exists
    // This route is only used for creating non-sso users, so auth_type is None
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
        create_req.roles,
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
        return Err(internal_server_error(e, "Failed to create user", None));
    }

    info!("User {} created successfully", user.username);

    // pass to scouter if enabled — non-fatal: OpsML continues even if Scouter is unreachable
    if state.scouter_client.is_enabled() {
        match state.exchange_token_from_perms(&perms).await {
            Ok(exchange_token) => {
                if let Err(e) = state
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
                {
                    error!("Failed to sync new user to Scouter (non-fatal): {e}");
                }
            }
            Err(e) => {
                error!("Failed to get exchange token for Scouter sync (non-fatal): {e}");
            }
        }
    }

    Ok(Json(CreateUserResponse::new(
        UserResponse::from(user),
        recovery_codes,
    )))
}

/// Get a user by username
#[instrument(skip_all)]
async fn get_user(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(username): Path<String>,
) -> Result<Json<UserResponse>, (StatusCode, Json<OpsmlServerError>)> {
    // Check permissions - user can only get their own data or admin can get any user
    let is_admin = perms.is_admin();
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
    if !perms.is_admin() {
        return OpsmlServerError::need_admin_permission().into_response(StatusCode::FORBIDDEN);
    }

    // Get users from database
    let users = match state.sql_client.get_users().await {
        Ok(users) => users,
        Err(e) => {
            error!("Failed to list users: {e}");
            return Err(internal_server_error(e, "Failed to list users", None));
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
    let is_admin = perms.is_admin();
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

        if let Some(roles) = update_req.roles {
            let hash_set: std::collections::HashSet<_> = roles.into_iter().collect();
            user.roles = hash_set.into_iter().collect();
        }

        if let Some(active) = update_req.active {
            user.active = active;
        }
    }

    // Save updated user to database
    if let Err(e) = state.sql_client.update_user(&user).await {
        error!("Failed to update user: {e}");
        return Err(internal_server_error(e, "Failed to update user", None));
    }

    info!("User {} updated successfully", user.username);

    // pass to scouter if enabled — non-fatal: OpsML continues even if Scouter is unreachable
    if state.scouter_client.is_enabled() {
        match state.exchange_token_from_perms(&perms).await {
            Ok(exchange_token) => {
                if let Err(e) = state
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
                {
                    error!("Failed to sync updated user to Scouter (non-fatal): {e}");
                } else {
                    info!("User {} updated in scouter", user.username);
                }
            }
            Err(e) => {
                error!("Failed to get exchange token for Scouter sync (non-fatal): {e}");
            }
        }
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
    if !perms.is_admin() {
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
                None,
            ));
        }
    };

    if is_last_admin {
        return OpsmlServerError::cannot_delete_last_admin().into_response(StatusCode::FORBIDDEN);
    }

    // Delete in scouter first if enabled — non-fatal: proceed with OpsML delete even if Scouter is unreachable
    if state.scouter_client.is_enabled() {
        match state.exchange_token_from_perms(&perms).await {
            Ok(exchange_token) => {
                match state
                    .scouter_client
                    .delete_user(&username, &exchange_token)
                    .await
                {
                    Ok(_) => info!("User {} deleted in scouter", username),
                    Err(e) => error!("Failed to delete user in Scouter (non-fatal): {e}"),
                }
            }
            Err(e) => {
                error!("Failed to get exchange token for Scouter delete (non-fatal): {e}");
            }
        }
    }

    // Delete the user
    if let Err(e) = state.sql_client.delete_user(&username).await {
        error!("Failed to delete user: {e}");
        return Err(internal_server_error(e, "Failed to delete user", None));
    }

    info!("User {} deleted successfully", username);

    Ok(Json(serde_json::json!({"success": true})))
}

/// Assign roles to a user (replaces group_permissions)
#[instrument(skip_all)]
async fn assign_roles(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(username): Path<String>,
    Json(req): Json<AssignRolesRequest>,
) -> Result<Json<UserResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.is_admin() {
        return OpsmlServerError::need_admin_permission().into_response(StatusCode::FORBIDDEN);
    }

    let mut user = get_user_from_db(&state.sql_client, &username, None).await?;
    user.roles = req.roles;

    if let Err(e) = state.sql_client.update_user(&user).await {
        error!("Failed to assign roles to user: {e}");
        return Err(internal_server_error(e, "Failed to assign roles", None));
    }

    info!("Roles assigned to user {} successfully", user.username);
    Ok(Json(UserResponse::from(user)))
}

/// Remove a single role from a user
#[instrument(skip_all)]
async fn remove_role(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path((username, role)): Path<(String, String)>,
) -> Result<Json<UserResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.is_admin() {
        return OpsmlServerError::need_admin_permission().into_response(StatusCode::FORBIDDEN);
    }

    let mut user = get_user_from_db(&state.sql_client, &username, None).await?;
    user.roles.retain(|r| r != &role);

    if let Err(e) = state.sql_client.update_user(&user).await {
        error!("Failed to remove role from user: {e}");
        return Err(internal_server_error(e, "Failed to remove role", None));
    }

    info!(
        "Role {} removed from user {} successfully",
        role, user.username
    );
    Ok(Json(UserResponse::from(user)))
}

/// Get effective permissions for a user
#[instrument(skip_all)]
async fn get_effective_permissions(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(username): Path<String>,
) -> Result<Json<EffectivePermissionsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let is_admin = perms.is_admin();
    let is_self = perms.username == username;

    if !is_admin && !is_self {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let user = get_user_from_db(&state.sql_client, &username, None).await?;
    let role_records = state
        .sql_client
        .get_roles_by_names(&user.roles)
        .await
        .map_err(|e| internal_server_error(e, "Failed to get roles", None))?;
    let effective = resolve_effective_permissions(&user, &role_records);

    Ok(Json(EffectivePermissionsResponse {
        username: user.username,
        roles: user.roles,
        direct_permissions: user.permissions,
        effective_permissions: effective,
    }))
}

pub async fn get_user_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{prefix}/user"), post(create_user))
            .route(&format!("{prefix}/user"), get(list_users))
            .route(&format!("{prefix}/user/{{username}}"), get(get_user))
            .route(&format!("{prefix}/user/{{username}}"), put(update_user))
            .route(&format!("{prefix}/user/{{username}}"), delete(delete_user))
            .route(
                &format!("{prefix}/user/{{username}}/roles"),
                put(assign_roles),
            )
            .route(
                &format!("{prefix}/user/{{username}}/roles/{{role}}"),
                delete(remove_role),
            )
            .route(
                &format!("{prefix}/user/{{username}}/permissions"),
                get(get_effective_permissions),
            )
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
