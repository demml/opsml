use crate::postgres::helper::PostgresQueryHelper;

use crate::error::SqlError;
use crate::schemas::schema::User;

use crate::traits::UserLogicTrait;
use async_trait::async_trait;
use sqlx::{FromRow, Pool, Postgres, Row, postgres::PgRow};

impl FromRow<'_, PgRow> for User {
    fn from_row(row: &PgRow) -> Result<Self, sqlx::Error> {
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

        let group_permissions: Vec<String> =
            serde_json::from_value(row.try_get("group_permissions")?).unwrap_or_default();

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
            group_permissions,
            favorite_spaces,
            authentication_type,
        })
    }
}
#[derive(Debug, Clone)]
pub struct UserLogicPostgresClient {
    pool: sqlx::Pool<Postgres>,
}
impl UserLogicPostgresClient {
    pub fn new(pool: &Pool<Postgres>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl UserLogicTrait for UserLogicPostgresClient {
    async fn insert_user(&self, user: &User) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_user_insert_query();

        let hashed_recovery_codes = serde_json::to_value(&user.hashed_recovery_codes)?;
        let group_permissions = serde_json::to_value(&user.group_permissions)?;
        let permissions = serde_json::to_value(&user.permissions)?;
        let favorite_spaces = serde_json::to_value(&user.favorite_spaces)?;

        sqlx::query(query)
            .bind(&user.username)
            .bind(&user.password_hash)
            .bind(&hashed_recovery_codes)
            .bind(&permissions)
            .bind(&group_permissions)
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
            Some(_) => PostgresQueryHelper::get_user_query_by_auth_type(),
            None => PostgresQueryHelper::get_user_query(),
        };

        let mut query_builder = sqlx::query_as(query).bind(username);

        if let Some(auth_type) = auth_type {
            query_builder = query_builder.bind(auth_type);
        }

        let user: Option<User> = query_builder.fetch_optional(&self.pool).await?;

        Ok(user)
    }

    async fn update_user(&self, user: &User) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_user_update_query();

        let hashed_recovery_codes = serde_json::to_value(&user.hashed_recovery_codes)?;
        let group_permissions = serde_json::to_value(&user.group_permissions)?;
        let permissions = serde_json::to_value(&user.permissions)?;
        let favorite_spaces = serde_json::to_value(&user.favorite_spaces)?;

        sqlx::query(query)
            .bind(user.active)
            .bind(&user.password_hash)
            .bind(&hashed_recovery_codes)
            .bind(&permissions)
            .bind(&group_permissions)
            .bind(&favorite_spaces)
            .bind(&user.refresh_token)
            .bind(&user.email)
            .bind(&user.authentication_type)
            .bind(&user.username)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_users(&self) -> Result<Vec<User>, SqlError> {
        let query = PostgresQueryHelper::get_users_query();

        let users = sqlx::query_as::<_, User>(query)
            .fetch_all(&self.pool)
            .await?;

        Ok(users)
    }

    async fn is_last_admin(&self, username: &str) -> Result<bool, SqlError> {
        // Count admins in the system
        let query = PostgresQueryHelper::get_last_admin_query();

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
        let query = PostgresQueryHelper::get_user_delete_query();

        sqlx::query(query)
            .bind(username)
            .execute(&self.pool)
            .await?;

        Ok(())
    }
}
