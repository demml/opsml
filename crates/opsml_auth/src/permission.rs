use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct UserPermissions {
    pub username: String,
    pub permissions: Vec<String>,
    pub group_permissions: Vec<String>,
}

impl UserPermissions {
    pub fn has_permission(&self, permission: &str) -> bool {
        self.permissions.contains(&permission.to_string())
            || self.group_permissions.contains(&"admin".to_string())
    }

    pub fn has_read_permission(&self, space_id: &str) -> bool {
        self.has_permission(&format!("read:{space_id}"))
            || self.permissions.contains(&"read:all".to_string())
    }

    pub fn has_write_permission(&self, space_id: &str) -> bool {
        self.has_permission(&format!("write:{space_id}"))
            || self.permissions.contains(&"write:all".to_string())
    }

    pub fn has_delete_permission(&self, space_id: &str) -> bool {
        self.has_permission(&format!("delete:{space_id}"))
            || self.permissions.contains(&"delete:all".to_string())
    }
}

impl UserPermissions {
    /// New users have read and write permissions
    pub fn new_with_default(username: String) -> Self {
        Self {
            username,
            permissions: vec!["read:all".to_string(), "write:all".to_string()],
            group_permissions: Vec::new(),
        }
    }
}
