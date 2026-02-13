use crate::error::AuthError;
use crate::sso::SsoProvider;
use jsonwebtoken::{DecodingKey, EncodingKey, Header, Validation, decode, encode};
use opsml_sql::schemas::schema::User;
use password_auth::{generate_hash, verify_password};
use rand::{Rng, distr::Alphanumeric};
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,
    exp: usize,
    pub permissions: Vec<String>,
    pub group_permissions: Vec<String>,
    salt: String,
}

pub struct AuthManager {
    jwt_secret: String,
    refresh_secret: String,
    scouter_secret: String,
    pub sso_provider: Option<SsoProvider>,
    pub dummy_user: User,
}
impl AuthManager {
    /// Creates a new instance of `AuthManager` with the provided secrets and optional SSO provider.
    ///
    /// # Arguments
    /// * `jwt_secret`: The secret key used for signing JWT tokens.
    /// * `refresh_secret`: The secret key used for signing refresh tokens.
    /// * `scouter_secret`: The secret key used for Scouter integration.
    ///
    /// # Returns
    /// A `Result` containing the `AuthManager` instance or an `AuthError` if initialization fails.
    pub async fn new(
        jwt_secret: &str,
        refresh_secret: &str,
        scouter_secret: &str,
    ) -> Result<Self, AuthError> {
        let sso_provider = SsoProvider::from_env().await.ok();

        let dummy_user = User {
            username: "dummy_user".to_string(),
            password_hash: generate_hash("dummy_password"),
            ..Default::default()
        };

        Ok(Self {
            jwt_secret: jwt_secret.to_string(),
            refresh_secret: refresh_secret.to_string(),
            scouter_secret: scouter_secret.to_string(),
            sso_provider,
            dummy_user,
        })
    }

    fn generate_salt(&self) -> String {
        rand::rng()
            .sample_iter(&Alphanumeric)
            .take(16)
            .map(char::from)
            .collect()
    }

    pub fn generate_jwt(&self, user: &User) -> Result<String, AuthError> {
        let expiration = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
            + 3600; // 1 hour

        let claims = Claims {
            sub: user.username.clone(),
            exp: expiration as usize,
            permissions: user.permissions.clone(),
            group_permissions: user.group_permissions.clone(),
            salt: self.generate_salt(),
        };

        encode(
            &Header::default(),
            &claims,
            &EncodingKey::from_secret(self.jwt_secret.as_ref()),
        )
        .map_err(|_| AuthError::JWTError)
    }

    pub fn generate_refresh_token(&self, user: &User) -> Result<String, AuthError> {
        let expiration = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
            + 86400; // 24 hours expiration

        let claims = Claims {
            sub: user.username.clone(),
            exp: expiration as usize,
            permissions: user.permissions.clone(),
            group_permissions: user.group_permissions.clone(),
            salt: self.generate_salt(),
        };

        encode(
            &Header::default(),
            &claims,
            &EncodingKey::from_secret(self.refresh_secret.as_ref()),
        )
        .map_err(|_| AuthError::JWTError)
    }

    pub fn validate_jwt(&self, token: &str) -> Result<Claims, jsonwebtoken::errors::Error> {
        let token_data = decode::<Claims>(
            token,
            &DecodingKey::from_secret(self.jwt_secret.as_ref()),
            &Validation::default(),
        )?;
        Ok(token_data.claims)
    }

    pub fn decode_jwt_without_validation(
        &self,
        token: &str,
    ) -> Result<Claims, jsonwebtoken::errors::Error> {
        let mut validation = Validation::default();
        validation.validate_exp = false; // Disable expiration validation
        validation.validate_nbf = false; // Disable "not before" validation
        validation.required_spec_claims.clear();
        let token_data = decode::<Claims>(
            token,
            &DecodingKey::from_secret(self.jwt_secret.as_ref()),
            &validation,
        )?;

        Ok(token_data.claims)
    }

    pub fn validate_user(&self, user: &User, password: &str) -> Result<(), AuthError> {
        verify_password(password, &user.password_hash).map_err(|_| AuthError::InvalidPassword)
    }

    pub fn validate_recovery_code(
        &self,
        recovery_code: &str,
        server_hashed_recovery_code: &str,
    ) -> Result<(), AuthError> {
        verify_password(recovery_code, server_hashed_recovery_code)
            .map_err(|_| AuthError::InvalidRecoveryCode)
    }

    pub fn is_sso_enabled(&self) -> bool {
        self.sso_provider.is_some()
    }

    pub fn get_sso_provider(&self) -> Result<&SsoProvider, AuthError> {
        self.sso_provider
            .as_ref()
            .ok_or(AuthError::SsoProviderNotSet)
    }
}

impl AuthManager {
    pub async fn exchange_token_for_scouter(&self, user: &User) -> Result<String, AuthError> {
        // Generate a new token using Scouter's secret
        let scouter_token = self.generate_jwt_with_secret(user, &self.scouter_secret)?;

        Ok(scouter_token)
    }

    fn generate_jwt_with_secret(&self, user: &User, secret: &str) -> Result<String, AuthError> {
        let expiration = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
            + 3600;

        let claims = Claims {
            sub: user.username.clone(),
            exp: expiration as usize,
            permissions: user.permissions.clone(),
            group_permissions: user.group_permissions.clone(),
            salt: self.generate_salt(),
        };

        encode(
            &Header::default(),
            &claims,
            &EncodingKey::from_secret(secret.as_ref()),
        )
        .map_err(|_| AuthError::JWTError)
    }
}
