use crate::core::state::AppState;
use crate::core::user::schema::{
    CreateUserRequest, UpdateUserRequest, UserListResponse, UserResponse,
};
use anyhow::{Context, Result};
use axum::extract::Path;
use axum::{
    extract::State,
    http::StatusCode,
    routing::{delete, get, post, put},
    Extension, Json, Router,
};
use opsml_auth::permission::UserPermissions;
use opsml_sql::base::SqlClient;
use opsml_sql::schemas::schema::User;
use password_auth::generate_hash;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::{error, info};

/// Create a new user via SDK
///
/// Requires admin permissions
async fn create_user(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(create_req): Json<CreateUserRequest>,
) -> Result<Json<UserResponse>, (StatusCode, Json<serde_json::Value>)> {
    // Check if requester has admin permissions
    if !perms.group_permissions.contains(&"admin".to_string()) {
        return Err((
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({"error": "Admin permissions required"})),
        ));
    }

    // Check if user already exists
    if let Ok(_) = state.sql_client.get_user(&create_req.username).await {
        return Err((
            StatusCode::CONFLICT,
            Json(serde_json::json!({"error": "User already exists"})),
        ));
    }

    // Hash the password
    let password_hash = generate_hash(&create_req.password);

    // Create the user
    let user = User::new(
        create_req.username,
        password_hash,
        create_req.permissions,
        create_req.group_permissions,
    );

    // Set active status if provided
    let mut user = user;
    if let Some(active) = create_req.active {
        user.active = active;
    }

    // Save to database
    if let Err(e) = state.sql_client.insert_user(&user).await {
        error!("Failed to create user: {}", e);
        return Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to create user"})),
        ));
    }

    info!("User {} created successfully", user.username);
    Ok(Json(UserResponse::from(user)))
}

/// Get a user by username
async fn get_user(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(username): Path<String>,
) -> Result<Json<UserResponse>, (StatusCode, Json<serde_json::Value>)> {
    // Check permissions - user can only get their own data or admin can get any user
    let is_admin = perms.group_permissions.contains(&"admin".to_string());
    let is_self = perms.username == username;

    if !is_admin && !is_self {
        return Err((
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({"error": "Permission denied"})),
        ));
    }

    // Get user from database
    let user = match state.sql_client.get_user(&username).await {
        Ok(user) => user,
        Err(e) => {
            error!("Failed to get user: {}", e);
            return Err((
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({"error": "User not found"})),
            ));
        }
    };

    Ok(Json(UserResponse::from(user)))
}

/// List all users
///
/// Requires admin permissions
async fn list_users(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
) -> Result<Json<UserListResponse>, (StatusCode, Json<serde_json::Value>)> {
    // Check if requester has admin permissions
    if !perms.group_permissions.contains(&"admin".to_string()) {
        return Err((
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({"error": "Admin permissions required"})),
        ));
    }

    // Get users from database
    let users = match state.sql_client.get_users().await {
        Ok(users) => users,
        Err(e) => {
            error!("Failed to list users: {}", e);
            return Err((
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "Failed to list users"})),
            ));
        }
    };

    let user_responses: Vec<UserResponse> = users.into_iter().map(UserResponse::from).collect();

    Ok(Json(UserListResponse {
        users: user_responses,
    }))
}

/// Update a user
async fn update_user(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(username): Path<String>,
    Json(update_req): Json<UpdateUserRequest>,
) -> Result<Json<UserResponse>, (StatusCode, Json<serde_json::Value>)> {
    // Check permissions - user can only update their own data or admin can update any user
    let is_admin = perms.group_permissions.contains(&"admin".to_string());
    let is_self = perms.username == username;

    if !is_admin && !is_self {
        return Err((
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({"error": "Permission denied"})),
        ));
    }

    // Get the current user state
    let mut user = match state.sql_client.get_user(&username).await {
        Ok(user) => user,
        Err(e) => {
            error!("Failed to get user for update: {}", e);
            return Err((
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({"error": "User not found"})),
            ));
        }
    };

    // Update fields based on request
    if let Some(password) = update_req.password {
        user.password_hash = generate_hash(&password);
    }

    // Only admins can change permissions
    if is_admin {
        if let Some(permissions) = update_req.permissions {
            user.permissions = permissions;
        }

        if let Some(group_permissions) = update_req.group_permissions {
            user.group_permissions = group_permissions;
        }

        if let Some(active) = update_req.active {
            user.active = active;
        }
    }

    // Save updated user to database
    if let Err(e) = state.sql_client.update_user(&user).await {
        error!("Failed to update user: {}", e);
        return Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to update user"})),
        ));
    }

    info!("User {} updated successfully", user.username);
    Ok(Json(UserResponse::from(user)))
}

/// Delete a user
///
/// Requires admin permissions
async fn delete_user(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(username): Path<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    // Check if requester has admin permissions
    if !perms.group_permissions.contains(&"admin".to_string()) {
        return Err((
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({"error": "Admin permissions required"})),
        ));
    }

    // Prevent deleting the last admin user
    let is_last_admin = match state.sql_client.is_last_admin(&username).await {
        Ok(is_last) => is_last,
        Err(e) => {
            error!("Failed to check if user is last admin: {}", e);
            return Err((
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "Failed to check admin status"})),
            ));
        }
    };

    if is_last_admin {
        return Err((
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({"error": "Cannot delete the last admin user"})),
        ));
    }

    // Delete the user
    if let Err(e) = state.sql_client.delete_user(&username).await {
        error!("Failed to delete user: {}", e);
        return Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to delete user"})),
        ));
    }

    info!("User {} deleted successfully", username);
    Ok(Json(serde_json::json!({"success": true})))
}

pub async fn get_user_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{}/users", prefix), post(create_user))
            .route(&format!("{}/users", prefix), get(list_users))
            .route(&format!("{}/users/:username", prefix), get(get_user))
            .route(&format!("{}/users/:username", prefix), put(update_user))
            .route(&format!("{}/users/:username", prefix), delete(delete_user))
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
