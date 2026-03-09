use crate::error::SqlError;
use crate::schemas::schema::Role;
use crate::traits::RoleLogicTrait;
use async_trait::async_trait;
use sqlx::{Pool, Postgres};

const INSERT_ROLE_SQL: &str = include_str!("insert_role.sql");
const GET_ROLE_SQL: &str = include_str!("get_role.sql");
const GET_ROLES_SQL: &str = include_str!("get_roles.sql");
const UPDATE_ROLE_SQL: &str = include_str!("update_role.sql");
const DELETE_ROLE_SQL: &str = include_str!("delete_role.sql");

#[derive(Debug, Clone)]
pub struct RoleLogicPostgresClient {
    pool: Pool<Postgres>,
}

impl RoleLogicPostgresClient {
    pub fn new(pool: &Pool<Postgres>) -> Self {
        Self { pool: pool.clone() }
    }
}

fn row_to_role(row: &sqlx::postgres::PgRow) -> Result<Role, sqlx::Error> {
    use sqlx::Row;
    let permissions: Vec<String> =
        serde_json::from_value(row.try_get("permissions")?).unwrap_or_default();
    Ok(Role {
        id: row.try_get("id")?,
        name: row.try_get("name")?,
        description: row.try_get("description")?,
        permissions,
        is_system: row.try_get("is_system")?,
        created_at: row.try_get("created_at")?,
        updated_at: row.try_get("updated_at")?,
    })
}

#[async_trait]
impl RoleLogicTrait for RoleLogicPostgresClient {
    async fn insert_role(&self, role: &Role) -> Result<(), SqlError> {
        let permissions = serde_json::to_value(&role.permissions)?;
        sqlx::query(INSERT_ROLE_SQL)
            .bind(&role.name)
            .bind(&role.description)
            .bind(&permissions)
            .bind(role.is_system)
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
        let placeholders: String = names
            .iter()
            .enumerate()
            .map(|(i, _)| format!("${}", i + 1))
            .collect::<Vec<_>>()
            .join(", ");
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
        let permissions = serde_json::to_value(&role.permissions)?;
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
            let perm_value: serde_json::Value = serde_json::from_str(permissions).unwrap();
            sqlx::query(
                "INSERT INTO opsml_role (name, description, permissions, is_system) VALUES ($1, $2, $3, TRUE) ON CONFLICT (name) DO NOTHING",
            )
            .bind(name)
            .bind(description)
            .bind(&perm_value)
            .execute(&self.pool)
            .await?;
        }
        Ok(())
    }
}
