use opsml_sql::schemas::schema::User;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct CreateUserRequest {
    pub username: String,
    pub password: String,
    pub email: String,
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
    pub favorite_spaces: Option<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RecoveryResetRequest {
    pub username: String,
    pub recovery_code: String,
    pub new_password: String,
}

#[derive(Serialize, Deserialize)]
pub struct ResetPasswordResponse {
    pub message: String,
    pub remaining_recovery_codes: usize,
}

#[derive(Serialize, Deserialize, Default)]
pub struct UserResponse {
    pub username: String,
    pub email: String,
    pub active: bool,
    pub role: String,
    pub permissions: Vec<String>,
    pub group_permissions: Vec<String>,
    pub favorite_spaces: Vec<String>,
}

#[derive(Serialize, Deserialize, Default)]
pub struct CreateUserResponse {
    pub user: UserResponse,
    pub recovery_codes: Vec<String>,
    pub message: String,
}

impl CreateUserResponse {
    pub fn new(user: UserResponse, recovery_codes: Vec<String>) -> Self {
        Self {
            user,
            recovery_codes,
            message: "Save these recovery codes securely. They cannot be shown again!".to_string(),
        }
    }
}

#[derive(Serialize, Deserialize)]
pub struct CreateUserUiResponse {
    pub registered: bool,
    pub response: Option<CreateUserResponse>,
    pub error: Option<String>,
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
            email: user.email,
            role: user.role,
            favorite_spaces: user.favorite_spaces,
        }
    }
}
