use crate::core::error::{OpsmlServerError, internal_server_error};
use crate::core::role::schema::{
    CreateRoleRequest, RoleListResponse, RoleResponse, UpdateRoleRequest,
};
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::extract::Path;
use axum::{
    Extension, Json, Router,
    extract::State,
    http::StatusCode,
    routing::{delete, get, post, put},
};
use opsml_auth::permission::UserPermissions;
use opsml_sql::schemas::schema::Role;
use opsml_sql::traits::RoleLogicTrait;
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::{error, info, instrument};

#[instrument(skip_all)]
async fn list_roles(
    State(state): State<Arc<AppState>>,
    Extension(_perms): Extension<UserPermissions>,
) -> Result<Json<RoleListResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let roles = state.sql_client.get_roles().await.map_err(|e| {
        error!("Failed to list roles: {e}");
        internal_server_error(e, "Failed to list roles", None)
    })?;

    let role_responses: Vec<RoleResponse> = roles
        .into_iter()
        .map(|r| RoleResponse {
            name: r.name,
            description: r.description,
            permissions: r.permissions,
            is_system: r.is_system,
        })
        .collect();

    Ok(Json(RoleListResponse {
        roles: role_responses,
    }))
}

#[instrument(skip_all)]
async fn get_role(
    State(state): State<Arc<AppState>>,
    Extension(_perms): Extension<UserPermissions>,
    Path(name): Path<String>,
) -> Result<Json<RoleResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let role = state.sql_client.get_role(&name).await.map_err(|e| {
        error!("Failed to get role: {e}");
        internal_server_error(e, "Failed to get role", None)
    })?;

    match role {
        Some(r) => Ok(Json(RoleResponse {
            name: r.name,
            description: r.description,
            permissions: r.permissions,
            is_system: r.is_system,
        })),
        None => Err((
            StatusCode::NOT_FOUND,
            Json(OpsmlServerError::new(format!("Role '{name}' not found"))),
        )),
    }
}

#[instrument(skip_all)]
async fn create_role(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<CreateRoleRequest>,
) -> Result<Json<RoleResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.is_admin() {
        return OpsmlServerError::need_admin_permission().into_response(StatusCode::FORBIDDEN);
    }

    let role = Role {
        id: None,
        name: req.name,
        description: req.description.unwrap_or_default(),
        permissions: req.permissions,
        is_system: false,
        created_at: chrono::Utc::now(),
        updated_at: chrono::Utc::now(),
    };

    state.sql_client.insert_role(&role).await.map_err(|e| {
        error!("Failed to create role: {e}");
        internal_server_error(e, "Failed to create role", None)
    })?;

    info!("Role {} created successfully", role.name);

    Ok(Json(RoleResponse {
        name: role.name,
        description: role.description,
        permissions: role.permissions,
        is_system: role.is_system,
    }))
}

#[instrument(skip_all)]
async fn update_role(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(name): Path<String>,
    Json(req): Json<UpdateRoleRequest>,
) -> Result<Json<RoleResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.is_admin() {
        return OpsmlServerError::need_admin_permission().into_response(StatusCode::FORBIDDEN);
    }

    let mut role = state
        .sql_client
        .get_role(&name)
        .await
        .map_err(|e| internal_server_error(e, "Failed to get role", None))?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(OpsmlServerError::new(format!("Role '{name}' not found"))),
            )
        })?;

    if role.is_system {
        return Err((
            StatusCode::FORBIDDEN,
            Json(OpsmlServerError::new(
                "Cannot modify system role".to_string(),
            )),
        ));
    }

    if let Some(desc) = req.description {
        role.description = desc;
    }
    if let Some(role_perms) = req.permissions {
        role.permissions = role_perms;
    }

    state.sql_client.update_role(&role).await.map_err(|e| {
        error!("Failed to update role: {e}");
        internal_server_error(e, "Failed to update role", None)
    })?;

    info!("Role {} updated successfully", role.name);

    Ok(Json(RoleResponse {
        name: role.name,
        description: role.description,
        permissions: role.permissions,
        is_system: role.is_system,
    }))
}

#[instrument(skip_all)]
async fn delete_role(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(name): Path<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.is_admin() {
        return OpsmlServerError::need_admin_permission().into_response(StatusCode::FORBIDDEN);
    }

    let role = state
        .sql_client
        .get_role(&name)
        .await
        .map_err(|e| internal_server_error(e, "Failed to get role", None))?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(OpsmlServerError::new(format!("Role '{name}' not found"))),
            )
        })?;

    if role.is_system {
        return Err((
            StatusCode::FORBIDDEN,
            Json(OpsmlServerError::new(
                "Cannot delete system role".to_string(),
            )),
        ));
    }

    state.sql_client.delete_role(&name).await.map_err(|e| {
        error!("Failed to delete role: {e}");
        internal_server_error(e, "Failed to delete role", None)
    })?;

    info!("Role {} deleted successfully", name);

    Ok(Json(serde_json::json!({"success": true})))
}

pub async fn get_role_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{prefix}/role"), get(list_roles))
            .route(&format!("{prefix}/role"), post(create_role))
            .route(&format!("{prefix}/role/{{name}}"), get(get_role))
            .route(&format!("{prefix}/role/{{name}}"), put(update_role))
            .route(&format!("{prefix}/role/{{name}}"), delete(delete_role))
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create role router");
            Err(anyhow::anyhow!("Failed to create role router"))
                .context("Panic occurred while creating the router")
        }
    }
}
