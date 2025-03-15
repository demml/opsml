use opsml_sql::schemas::schema::User;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct CreateUserRequest {
    pub username: String,
    pub password: String,
    pub permissions: Option<Vec<String>>,
    pub group_permissions: Option<Vec<String>>,
    pub role: Option<String>,
    pub active: Option<bool>,
}

#[derive(Serialize, Deserialize)]
pub struct UpdateUserRequest {
    pub password: Option<String>,
    pub permissions: Option<Vec<String>>,
    pub group_permissions: Option<Vec<String>>,
    pub active: Option<bool>,
}

#[derive(Serialize, Deserialize)]
pub struct UserResponse {
    pub username: String,
    pub active: bool,
    pub permissions: Vec<String>,
    pub group_permissions: Vec<String>,
}

#[derive(Serialize, Deserialize)]
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
