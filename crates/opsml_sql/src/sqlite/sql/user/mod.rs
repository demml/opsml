use crate::sqlite::helper::SqliteQueryHelper;

use crate::error::SqlError;
use crate::schemas::schema::User;

use crate::traits::UserLogicTrait;
use async_trait::async_trait;
use sqlx::{Pool, Sqlite};

#[derive(Debug)]
pub struct UserLogicSqliteClient {
    pool: sqlx::Pool<Sqlite>,
}
impl UserLogicSqliteClient {
    pub fn new(pool: &Pool<Sqlite>) -> Self {
        Self { pool: pool.clone() }
    }

    fn pool(&self) -> &sqlx::Pool<Sqlite> {
        &self.pool
    }
}

#[async_trait]
impl UserLogicTrait for UserLogicSqliteClient {
    async fn insert_user(&self, user: &User) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_user_insert_query();

        let hashed_recovery_codes = serde_json::to_string(&user.hashed_recovery_codes)?;
        let group_permissions = serde_json::to_string(&user.group_permissions)?;
        let permissions = serde_json::to_string(&user.permissions)?;
        let favorite_spaces = serde_json::to_string(&user.favorite_spaces)?;

        sqlx::query(&query)
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
            Some(_) => SqliteQueryHelper::get_user_query_by_auth_type(),
            None => SqliteQueryHelper::get_user_query(),
        };

        let mut query_builder = sqlx::query_as(&query).bind(username);

        if let Some(auth_type) = auth_type {
            query_builder = query_builder.bind(auth_type);
        }

        let user: Option<User> = query_builder.fetch_optional(&self.pool).await?;

        Ok(user)
    }

    async fn get_users(&self) -> Result<Vec<User>, SqlError> {
        let query = SqliteQueryHelper::get_users_query();

        let users = sqlx::query_as::<_, User>(&query)
            .fetch_all(&self.pool)
            .await?;

        Ok(users)
    }

    async fn is_last_admin(&self, username: &str) -> Result<bool, SqlError> {
        // Count admins in the system
        let query = SqliteQueryHelper::get_last_admin_query();

        let admins: Vec<String> = sqlx::query_scalar(&query).fetch_all(&self.pool).await?;

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

        sqlx::query(&query)
            .bind(username)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn update_user(&self, user: &User) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_user_update_query();

        let hashed_recovery_codes = serde_json::to_string(&user.hashed_recovery_codes)?;
        let group_permissions = serde_json::to_string(&user.group_permissions)?;
        let permissions = serde_json::to_string(&user.permissions)?;
        let favorite_spaces = serde_json::to_string(&user.favorite_spaces)?;

        sqlx::query(&query)
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
            .bind(&user.authentication_type)
            .execute(&self.pool)
            .await?;

        Ok(())
    }
}
