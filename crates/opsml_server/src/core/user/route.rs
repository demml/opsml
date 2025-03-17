use crate::core::scouter;
use crate::core::state::AppState;
use crate::core::user::schema::{
    CreateUserRequest, UpdateUserRequest, UserListResponse, UserResponse,
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
use opsml_client::RequestType;
use opsml_error::error::ApiError;
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_sql::schemas::schema::User;
use password_auth::generate_hash;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::{error, info};

async fn query_user(sql_client: &SqlClientEnum, username: &str) -> Result<User, ApiError> {
    // Get user from database
    let user = match sql_client.get_user(username).await {
        Ok(Some(user)) => user,
        Ok(None) => {
            return Err(ApiError::Error("User not found".to_string()));
        }
        Err(e) => {
            error!("Failed to get user: {}", e);
            return Err(ApiError::Error("Failed to get user".to_string()));
        }
    };

    Ok(user)
}

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
    if let Ok(Some(_)) = state.sql_client.get_user(&create_req.username).await {
        return Err((
            StatusCode::CONFLICT,
            Json(serde_json::json!({"error": "User already exists"})),
        ));
    }

    // Hash the password
    let password_hash = generate_hash(&create_req.password);

    // Create the user
    let mut user = User::new(
        create_req.username,
        password_hash,
        create_req.permissions,
        create_req.group_permissions,
        create_req.role,
    );

    // Set active status if provided
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

    // pass to scouter if enabled
    if state.scouter_client.enabled {
        let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
            error!("Failed to exchange token for scouter: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "Failed to exchange token for scouter"})),
            )
        })?;

        state
            .scouter_client
            .request(
                scouter::Routes::Users,
                RequestType::Post,
                Some(serde_json::json!(&user)),
                None,
                None,
                exchange_token,
            )
            .await
            .map_err(|e| {
                error!("Failed to create user in scouter: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({"error": "Failed to create user in scouter"})),
                )
            })?;
    }
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
    let user = query_user(&state.sql_client, &username)
        .await
        .map_err(|e| {
            error!("Failed to get user: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "Failed to get user"})),
            )
        })?;

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
    let mut user = get_user_from_db(&state, &username).await?;

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

    // pass to scouter if enabled
    if state.scouter_client.enabled {
        let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
            error!("Failed to exchange token for scouter: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "Failed to exchange token for scouter"})),
            )
        })?;
        state
            .scouter_client
            .request(
                scouter::Routes::Users,
                RequestType::Put,
                Some(serde_json::json!(&user)),
                None,
                None,
                exchange_token,
            )
            .await
            .map_err(|e| {
                error!("Failed to create user in scouter: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({"error": "Failed to create user in scouter"})),
                )
            })?;
    }

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

    // pass to scouter if enabled
    if state.scouter_client.enabled {
        let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
            error!("Failed to exchange token for scouter: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "Failed to exchange token for scouter"})),
            )
        })?;

        state
            .scouter_client
            .delete_user(&username, exchange_token)
            .await
            .map_err(|e| {
                error!("Failed to delete user in scouter: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({"error": "Failed to delete user in scouter"})),
                )
            })?;
    }

    Ok(Json(serde_json::json!({"success": true})))
}

pub async fn get_user_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{}/users", prefix), post(create_user))
            .route(&format!("{}/users", prefix), get(list_users))
            .route(&format!("{}/users/{{username}}", prefix), get(get_user))
            .route(&format!("{}/users/{{username}}", prefix), put(update_user))
            .route(
                &format!("{}/users/{{username}}", prefix),
                delete(delete_user),
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
