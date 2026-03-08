use opsml_sql::schemas::schema::{Role, User};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct UserPermissions {
    pub username: String,
    pub permissions: Vec<String>,
    pub roles: Vec<String>,
    pub effective_permissions: Vec<String>,
}

impl UserPermissions {
    pub fn is_admin(&self) -> bool {
        self.roles.contains(&"admin".to_string())
    }

    pub fn has_permission(&self, permission: &str) -> bool {
        self.is_admin() || self.effective_permissions.contains(&permission.to_string())
    }

    pub fn has_read_permission(&self, space_id: &str) -> bool {
        self.is_admin()
            || self.effective_permissions.contains(&"read:all".to_string())
            || self
                .effective_permissions
                .contains(&format!("read:{space_id}"))
    }

    pub fn has_write_permission(&self, space_id: &str) -> bool {
        self.is_admin()
            || self
                .effective_permissions
                .contains(&"write:all".to_string())
            || self
                .effective_permissions
                .contains(&format!("write:{space_id}"))
    }

    pub fn has_delete_permission(&self, space_id: &str) -> bool {
        self.is_admin()
            || self
                .effective_permissions
                .contains(&"delete:all".to_string())
            || self
                .effective_permissions
                .contains(&format!("delete:{space_id}"))
    }
}

impl UserPermissions {
    /// New users have read and write permissions
    pub fn new_with_default(username: String) -> Self {
        let permissions = vec!["read:all".to_string(), "write:all".to_string()];
        Self {
            username,
            effective_permissions: permissions.clone(),
            permissions,
            roles: Vec::new(),
        }
    }
}

/// Compute the effective permissions for a user by unioning their direct permissions
/// with all permissions from their assigned roles.
pub fn resolve_effective_permissions(user: &User, roles: &[Role]) -> Vec<String> {
    let mut seen = std::collections::BTreeSet::new();
    for p in &user.permissions {
        seen.insert(p.clone());
    }
    for role in roles {
        for p in &role.permissions {
            seen.insert(p.clone());
        }
    }
    seen.into_iter().collect()
}
