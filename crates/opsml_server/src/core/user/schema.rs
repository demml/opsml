use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{Path, Query, State},
    http::{HeaderMap, StatusCode},
    response::Json,
    routing::{delete, get, post, put},
    Router,
};
use opsml_auth::permission::UserPermissions;
use opsml_error::error::AuthError;
use opsml_sql::base::SqlClient;
use opsml_sql::schemas::schema::User;
use password_auth::generate_hash;
use serde::{Deserialize, Serialize};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::{error, info};

#[derive(Deserialize)]
pub struct CreateUserRequest {
    pub username: String,
    pub password: String,
    pub permissions: Option<Vec<String>>,
    pub group_permissions: Option<Vec<String>>,
    pub active: Option<bool>,
}

#[derive(Deserialize)]
pub struct UpdateUserRequest {
    pub username: String,
    pub password: Option<String>,
    pub permissions: Option<Vec<String>>,
    pub group_permissions: Option<Vec<String>>,
    pub active: Option<bool>,
}

#[derive(Serialize)]
pub struct UserResponse {
    pub username: String,
    pub active: bool,
    pub permissions: Vec<String>,
    pub group_permissions: Vec<String>,
}

#[derive(Serialize)]
pub struct UserListResponse {
    pub users: Vec<UserResponse>,
}

// Convert User to UserResponse (strips sensitive data)
impl From<User> for UserResponse {
    fn from(user: User) -> Self {
        UserResponse {
            username: user.username,
            active: user.active,
            permissions: user.permissions,
            group_permissions: user.group_permissions,
        }
    }
}
