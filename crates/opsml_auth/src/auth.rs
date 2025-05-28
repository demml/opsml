use crate::error::AuthError;
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use opsml_sql::schemas::schema::User;
use password_auth::verify_password;
use rand::{distr::Alphanumeric, Rng};
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
}
impl AuthManager {
    pub fn new(jwt_secret: &str, refresh_secret: &str, scouter_secret: &str) -> Self {
        Self {
            jwt_secret: jwt_secret.to_string(),
            refresh_secret: refresh_secret.to_string(),
            scouter_secret: scouter_secret.to_string(),
        }
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
            + 3600; // 1 hour expiration

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
        validation.insecure_disable_signature_validation();
        let token_data = decode::<Claims>(
            token,
            &DecodingKey::from_secret(self.jwt_secret.as_ref()),
            &validation,
        )?;

        Ok(token_data.claims)
    }

    pub fn validate_refresh_token(
        &self,
        token: &str,
    ) -> Result<Claims, jsonwebtoken::errors::Error> {
        let token_data = decode::<Claims>(
            token,
            &DecodingKey::from_secret(self.refresh_secret.as_ref()),
            &Validation::default(),
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
