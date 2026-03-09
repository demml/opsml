use crate::error::SqlError;
use crate::schemas::schema::Role;
use crate::traits::RoleLogicTrait;
use async_trait::async_trait;
use sqlx::{MySql, Pool};

const INSERT_ROLE_SQL: &str = include_str!("insert_role.sql");
const GET_ROLE_SQL: &str = include_str!("get_role.sql");
const GET_ROLES_SQL: &str = include_str!("get_roles.sql");
const UPDATE_ROLE_SQL: &str = include_str!("update_role.sql");
const DELETE_ROLE_SQL: &str = include_str!("delete_role.sql");

#[derive(Debug, Clone)]
pub struct RoleLogicMySqlClient {
    pool: Pool<MySql>,
}

impl RoleLogicMySqlClient {
    pub fn new(pool: &Pool<MySql>) -> Self {
        Self { pool: pool.clone() }
    }
}

fn row_to_role(row: &sqlx::mysql::MySqlRow) -> Result<Role, sqlx::Error> {
    use sqlx::Row;
    let permissions: Vec<String> =
        serde_json::from_value(row.try_get("permissions")?).unwrap_or_default();
    let is_system_int: i8 = row.try_get("is_system")?;
    Ok(Role {
        id: row.try_get("id")?,
        name: row.try_get("name")?,
        description: row.try_get("description")?,
        permissions,
        is_system: is_system_int != 0,
        created_at: row.try_get("created_at")?,
        updated_at: row.try_get("updated_at")?,
    })
}

#[async_trait]
impl RoleLogicTrait for RoleLogicMySqlClient {
    async fn insert_role(&self, role: &Role) -> Result<(), SqlError> {
        let permissions = serde_json::to_string(&role.permissions)?;
        sqlx::query(INSERT_ROLE_SQL)
            .bind(&role.name)
            .bind(&role.description)
            .bind(&permissions)
            .bind(role.is_system as i8)
            .execute(&self.pool)
            .await?;
        Ok(())
    }

    async fn get_role(&self, name: &str) -> Result<Option<Role>, SqlError> {
        let row = sqlx::query(GET_ROLE_SQL)
            .bind(name)
            .fetch_optional(&self.pool)
            .await?;

        match row {
            Some(r) => Ok(Some(row_to_role(&r).map_err(SqlError::SqlxError)?)),
            None => Ok(None),
        }
    }

    async fn get_roles(&self) -> Result<Vec<Role>, SqlError> {
        let rows = sqlx::query(GET_ROLES_SQL).fetch_all(&self.pool).await?;

        rows.iter()
            .map(|r| row_to_role(r).map_err(SqlError::SqlxError))
            .collect()
    }

    async fn get_roles_by_names(&self, names: &[String]) -> Result<Vec<Role>, SqlError> {
        if names.is_empty() {
            return Ok(vec![]);
        }
        let placeholders: String = names.iter().map(|_| "?").collect::<Vec<_>>().join(", ");
        let query_str = format!(
            "SELECT id, name, description, permissions, is_system, created_at, updated_at FROM opsml_role WHERE name IN ({placeholders})"
        );
        let mut query = sqlx::query(&query_str);
        for name in names {
            query = query.bind(name);
        }
        let rows = query.fetch_all(&self.pool).await?;
        rows.iter()
            .map(|r| row_to_role(r).map_err(SqlError::SqlxError))
            .collect()
    }

    async fn update_role(&self, role: &Role) -> Result<(), SqlError> {
        let permissions = serde_json::to_string(&role.permissions)?;
        sqlx::query(UPDATE_ROLE_SQL)
            .bind(&role.description)
            .bind(&permissions)
            .bind(&role.name)
            .execute(&self.pool)
            .await?;
        Ok(())
    }

    async fn delete_role(&self, name: &str) -> Result<(), SqlError> {
        sqlx::query(DELETE_ROLE_SQL)
            .bind(name)
            .execute(&self.pool)
            .await?;
        Ok(())
    }

    async fn seed_system_roles(&self) -> Result<(), SqlError> {
        let system_roles: &[(&str, &str, &str)] = &[
            (
                "admin",
                "Full platform access",
                r#"["read:all","write:all","delete:all"]"#,
            ),
            (
                "user",
                "Standard read/write access",
                r#"["read:all","write:all"]"#,
            ),
            ("viewer", "Read-only across all spaces", r#"["read:all"]"#),
            (
                "data_scientist",
                "Read/write; no delete or admin",
                r#"["read:all","write:all"]"#,
            ),
        ];
        for (name, description, permissions) in system_roles {
            sqlx::query(
                "INSERT IGNORE INTO opsml_role (name, description, permissions, is_system) VALUES (?, ?, ?, 1)",
            )
            .bind(name)
            .bind(description)
            .bind(permissions)
            .execute(&self.pool)
            .await?;
        }
        Ok(())
    }
}
