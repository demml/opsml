use crate::sqlite::helper::SqliteQueryHelper;

use crate::error::SqlError;
use crate::schemas::schema::User;

use crate::traits::UserLogicTrait;
use async_trait::async_trait;
use sqlx::{FromRow, Pool, Row, Sqlite, sqlite::SqliteRow};

impl FromRow<'_, SqliteRow> for User {
    fn from_row(row: &SqliteRow) -> Result<Self, sqlx::Error> {
        let id = row.try_get("id")?;
        let created_at = row.try_get("created_at")?;
        let updated_at = row.try_get("updated_at")?;
        let active = row.try_get("active")?;
        let username = row.try_get("username")?;
        let password_hash = row.try_get("password_hash")?;
        let email = row.try_get("email")?;
        let role = row.try_get("role")?;
        let refresh_token = row.try_get("refresh_token")?;
        let authentication_type: String = row.try_get("authentication_type")?;

        let roles: Vec<String> = serde_json::from_value(row.try_get("roles")?).unwrap_or_default();

        let permissions: Vec<String> =
            serde_json::from_value(row.try_get("permissions")?).unwrap_or_default();

        let hashed_recovery_codes: Vec<String> =
            serde_json::from_value(row.try_get("hashed_recovery_codes")?).unwrap_or_default();

        let favorite_spaces: Vec<String> =
            serde_json::from_value(row.try_get("favorite_spaces")?).unwrap_or_default();

        Ok(User {
            id,
            created_at,
            updated_at,
            active,
            username,
            password_hash,
            email,
            role,
            refresh_token,
            hashed_recovery_codes,
            permissions,
            roles,
            favorite_spaces,
            authentication_type,
        })
    }
}

#[derive(Debug, Clone)]
pub struct UserLogicSqliteClient {
    pool: sqlx::Pool<Sqlite>,
}
impl UserLogicSqliteClient {
    pub fn new(pool: &Pool<Sqlite>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl UserLogicTrait for UserLogicSqliteClient {
    async fn insert_user(&self, user: &User) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_user_insert_query();

        let hashed_recovery_codes = serde_json::to_string(&user.hashed_recovery_codes)?;
        let roles = serde_json::to_string(&user.roles)?;
        let permissions = serde_json::to_string(&user.permissions)?;
        let favorite_spaces = serde_json::to_string(&user.favorite_spaces)?;

        sqlx::query(query)
            .bind(&user.username)
            .bind(&user.password_hash)
            .bind(&hashed_recovery_codes)
            .bind(&permissions)
            .bind(&roles)
            .bind(&favorite_spaces)
            .bind(&user.role)
            .bind(user.active)
            .bind(&user.email)
            .bind(&user.authentication_type)
            .execute(&self.pool)
            .await?;

        Ok(())
    }
    async fn get_user(
        &self,
        username: &str,
        auth_type: Option<&str>,
    ) -> Result<Option<User>, SqlError> {
        let query = match auth_type {
            Some(_) => SqliteQueryHelper::get_user_query_by_auth_type(),
            None => SqliteQueryHelper::get_user_query(),
        };

        let mut query_builder = sqlx::query_as(query).bind(username);

        if let Some(auth_type) = auth_type {
            query_builder = query_builder.bind(auth_type);
        }

        let user: Option<User> = query_builder.fetch_optional(&self.pool).await?;

        Ok(user)
    }

    async fn get_users(&self) -> Result<Vec<User>, SqlError> {
        let query = SqliteQueryHelper::get_users_query();

        let users = sqlx::query_as::<_, User>(query)
            .fetch_all(&self.pool)
            .await?;

        Ok(users)
    }

    async fn is_last_admin(&self, username: &str) -> Result<bool, SqlError> {
        // Count admins in the system
        let query = SqliteQueryHelper::get_last_admin_query();

        let admins: Vec<String> = sqlx::query_scalar(query).fetch_all(&self.pool).await?;

        // If there are no other admins, this is the last one
        if admins.len() > 1 {
            return Ok(false);
        }

        // no admins found
        if admins.is_empty() {
            return Ok(false);
        }

        // check if the username is the last admin
        Ok(admins.len() == 1 && admins[0] == username)
    }

    async fn delete_user(&self, username: &str) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_user_delete_query();

        sqlx::query(query)
            .bind(username)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn update_user(&self, user: &User) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_user_update_query();

        let hashed_recovery_codes = serde_json::to_string(&user.hashed_recovery_codes)?;
        let roles = serde_json::to_string(&user.roles)?;
        let permissions = serde_json::to_string(&user.permissions)?;
        let favorite_spaces = serde_json::to_string(&user.favorite_spaces)?;

        sqlx::query(query)
            .bind(user.active)
            .bind(&user.password_hash)
            .bind(&hashed_recovery_codes)
            .bind(&permissions)
            .bind(&roles)
            .bind(&favorite_spaces)
            .bind(&user.refresh_token)
            .bind(&user.email)
            .bind(&user.authentication_type)
            .bind(&user.username)
            .bind(&user.authentication_type)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_users_paginated(
        &self,
        limit: i64,
        offset: i64,
        search: Option<&str>,
    ) -> Result<(Vec<User>, i64), SqlError> {
        let (users, total) = if let Some(search) = search {
            let pattern = format!("%{search}%");
            let users = sqlx::query_as::<_, User>(
                "SELECT id, created_at, active, username, password_hash, hashed_recovery_codes, permissions, roles, favorite_spaces, role, refresh_token, email, updated_at, authentication_type FROM opsml_user WHERE username LIKE ? OR email LIKE ? ORDER BY username LIMIT ? OFFSET ?",
            )
            .bind(&pattern)
            .bind(&pattern)
            .bind(limit)
            .bind(offset)
            .fetch_all(&self.pool)
            .await?;
            let total: i64 = sqlx::query_scalar(
                "SELECT COUNT(*) FROM opsml_user WHERE username LIKE ? OR email LIKE ?",
            )
            .bind(&pattern)
            .bind(&pattern)
            .fetch_one(&self.pool)
            .await?;
            (users, total)
        } else {
            let users = sqlx::query_as::<_, User>(
                "SELECT id, created_at, active, username, password_hash, hashed_recovery_codes, permissions, roles, favorite_spaces, role, refresh_token, email, updated_at, authentication_type FROM opsml_user ORDER BY username LIMIT ? OFFSET ?",
            )
            .bind(limit)
            .bind(offset)
            .fetch_all(&self.pool)
            .await?;
            let total: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM opsml_user")
                .fetch_one(&self.pool)
                .await?;
            (users, total)
        };
        Ok((users, total))
    }
}
