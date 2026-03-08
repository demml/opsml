use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateRoleRequest {
    pub name: String,
    pub description: Option<String>,
    pub permissions: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UpdateRoleRequest {
    pub description: Option<String>,
    pub permissions: Option<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RoleResponse {
    pub name: String,
    pub description: String,
    pub permissions: Vec<String>,
    pub is_system: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RoleListResponse {
    pub roles: Vec<RoleResponse>,
}
