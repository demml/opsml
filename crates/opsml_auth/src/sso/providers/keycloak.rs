use crate::sso::error::SsoError;
use crate::sso::types::UserInfo;
use jsonwebtoken::DecodingKey;
use jsonwebtoken::{decode, Validation};
use reqwest::{Client, StatusCode};
use serde::{Deserialize, Serialize};
use tracing::{debug, error};

#[derive(Debug, Serialize, Deserialize)]
pub struct KeycloakClaims {
    pub sub: String,
    pub scope: String,
    pub name: String,
    pub preferred_username: String,
    pub email: String,
    pub exp: usize, // Expiration time in seconds since epoch
}

#[derive(Debug, Deserialize)]
pub struct KeycloakErrorResponse {
    pub error: String,
    pub error_description: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct KeycloakPublicKeyResponse {
    pub realm: String,
    pub public_key: String,
}

impl KeycloakPublicKeyResponse {
    pub fn format_public_key(&self) -> String {
        // Format the public key as needed, e.g., removing newlines or spaces
        format!(
            "-----BEGIN PUBLIC KEY-----\n{}\n-----END PUBLIC KEY-----",
            self.public_key
        )
    }
}
#[derive(Debug, Clone, Default, Serialize)]
pub struct KeycloakSettings {
    pub client_id: String,
    pub client_secret: String,
    pub redirect_uri: String,
    pub auth_url: String,
    pub auth_realm: String,
    pub token_url: String,
    pub public_key: Option<String>,
    pub scope: String,
}

impl KeycloakSettings {
    pub fn from_env() -> Result<Self, SsoError> {
        let client_id =
            std::env::var("KEYCLOAK_CLIENT_ID").map_err(SsoError::KeycloakEnvVarError)?;

        let client_secret =
            std::env::var("KEYCLOAK_CLIENT_SECRET").map_err(SsoError::KeycloakEnvVarError)?;

        let redirect_uri =
            std::env::var("KEYCLOAK_REDIRECT_URI").map_err(SsoError::KeycloakEnvVarError)?;

        let auth_url = std::env::var("KEYCLOAK_AUTH_URL").map_err(SsoError::KeycloakEnvVarError)?;

        let auth_realm =
            std::env::var("KEYCLOAK_AUTH_REALM").map_err(SsoError::KeycloakEnvVarError)?;

        let scope =
            std::env::var("KEYCLOAK_SCOPE").unwrap_or_else(|_| "openid profile email".to_string());

        // if provide, the public key should have the format:
        // -----BEGIN PUBLIC KEY-----
        // <base64 encoded key>
        // ----END PUBLIC KEY-----
        let public_key = std::env::var("KEYCLOAK_PUBLIC_KEY")
            .ok()
            .map(|key| key.trim().to_string());

        let token_url = format!(
            "{}/realms/{}/protocol/openid-connect/token",
            auth_url, auth_realm
        );

        Ok(Self {
            client_id,
            client_secret,
            redirect_uri,
            auth_url,
            auth_realm,
            token_url,
            public_key,
            scope,
        })
    }

    pub fn build_auth_params<'a>(
        &'a self,
        username: &'a str,
        password: &'a str,
    ) -> Vec<(&'a str, &'a str)> {
        vec![
            ("grant_type", "password"),
            ("client_id", &self.client_id),
            ("client_secret", &self.client_secret),
            ("redirect_uri", &self.redirect_uri),
            ("username", username),
            ("password", password),
        ]
    }

    pub fn build_callback_auth_params<'a>(&'a self, code: &'a str) -> Vec<(&'a str, &'a str)> {
        vec![
            ("grant_type", "authorization_code"),
            ("client_id", &self.client_id),
            ("client_secret", &self.client_secret),
            ("redirect_uri", &self.redirect_uri),
            ("code", code),
        ]
    }
}

#[derive(Deserialize, Debug, Default)]
pub struct KeycloakTokenResponse {
    pub access_token: String,
    pub expires_in: u64,
    pub refresh_token: String,
    pub refresh_expires_in: u64,
    pub token_type: String,
    #[serde(rename = "not-before-policy")]
    pub not_before_policy: u64,
    pub session_state: String,
    pub scope: String,
}

#[derive(Deserialize, Debug, Default)]
pub struct KeycloakCodeResponse {
    pub access_token: String,
    pub expires_in: u64,
    pub refresh_token: String,
    pub refresh_expires_in: u64,
    pub token_type: String,
    pub id_token: String,
    #[serde(rename = "not-before-policy")]
    pub not_before_policy: u64,
    pub session_state: String,
    pub scope: String,
}

pub struct KeycloakProvider {
    pub client: Client,
    pub settings: KeycloakSettings,
}

impl KeycloakProvider {
    pub async fn new(client: Client) -> Result<Self, SsoError> {
        let mut settings = KeycloakSettings::from_env()?;

        // if settings.public_key is missing attempt to fetch it from the Keycloak server
        if settings.public_key.is_none() {
            // Fetch the public key from Keycloak
            let public_key_url = format!("{}/realms/{}", settings.auth_url, settings.auth_realm);
            let response = client.get(&public_key_url).send().await?;

            let public_key = if response.status().is_success() {
                let certs: KeycloakPublicKeyResponse =
                    response.json().await.map_err(SsoError::ReqwestError)?;
                Some(certs.format_public_key())
            } else {
                error!("Failed to fetch public key from Keycloak. Tokens will not be validated when decoding");
                None
            };
            settings.public_key = public_key;
        }

        Ok(Self { client, settings })
    }

    pub async fn get_token(
        &self,
        username: &str,
        password: &str,
    ) -> Result<KeycloakTokenResponse, SsoError> {
        // Implement the token retrieval logic here
        let params = self.settings.build_auth_params(username, password);

        let response = self
            .client
            .post(&self.settings.token_url)
            .form(&params)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .send()
            .await?;

        // check for 401
        if response.status() == StatusCode::UNAUTHORIZED {
            return Err(SsoError::Unauthorized);
        }

        // handle other errors
        if !response.status().is_success() {
            let status = response.status();
            // Try to parse error response for more detail
            if let Ok(error_response) = response.json::<KeycloakErrorResponse>().await {
                if error_response.error == "invalid_grant"
                    && error_response
                        .error_description
                        .contains("Account is not fully set up")
                {
                    return Err(SsoError::AccountNotConfigured(
                        "User account requires additional setup in Keycloak".to_string(),
                    ));
                }
                return Err(SsoError::AuthenticationFailed(
                    error_response.error_description,
                ));
            }

            // Fallback to generic error
            return Err(SsoError::FallbackError(status.to_string()));
        }

        Ok(response.json::<KeycloakTokenResponse>().await?)
    }

    pub async fn get_token_from_code(&self, code: &str) -> Result<KeycloakCodeResponse, SsoError> {
        // Implement the token retrieval logic using the authorization code
        let params = self.settings.build_callback_auth_params(code);

        let response = self
            .client
            .post(&self.settings.token_url)
            .form(&params)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .send()
            .await
            .map_err(|e| {
                error!("Failed to send request to Keycloak: {}", e);
                SsoError::ReqwestError(e)
            })?;

        // check for 401
        if response.status() == StatusCode::UNAUTHORIZED {
            return Err(SsoError::Unauthorized);
        }

        // handle other errors
        if !response.status().is_success() {
            let status = response.status();
            // Try to parse error response for more detail
            if let Ok(error_response) = response.json::<KeycloakErrorResponse>().await {
                return Err(SsoError::AuthenticationFailed(
                    error_response.error_description,
                ));
            }

            // Fallback to generic error
            return Err(SsoError::FallbackError(status.to_string()));
        }

        let token = response
            .json::<KeycloakCodeResponse>()
            .await
            .map_err(SsoError::ReqwestError)?;

        Ok(token)
    }

    /// Decode a JWT token with validation against the Keycloak public key.
    /// If the public key is not available, it will fall back to decoding without validation.
    ///
    /// # Arguments
    /// * `token` - The JWT token to decode.
    /// * `public_key` - The public key to validate the token against.
    ///
    /// # Returns
    /// * `Result<Claims, SsoError>` - The decoded claims if successful, or an error if validation fails.
    fn decode_jwt_with_validation(
        &self,
        token: &str,
        public_key: &str,
    ) -> Result<KeycloakClaims, SsoError> {
        let mut validation = Validation::new(jsonwebtoken::Algorithm::RS256);
        validation.validate_aud = false;

        let token_data = decode::<KeycloakClaims>(
            token,
            &DecodingKey::from_rsa_pem(public_key.as_bytes())?,
            &validation,
        )
        .map_err({
            |e| {
                error!("Failed to decode JWT token: {}", e);
                SsoError::JwtDecodeError(e)
            }
        })?;

        Ok(token_data.claims)
    }

    pub async fn authenticate(&self, username: &str, password: &str) -> Result<UserInfo, SsoError> {
        // Implement the authentication logic here
        debug!(
            "Requesting token from Keycloak at {}",
            self.settings.token_url
        );

        // Get access token from Keycloak
        let token_response = self.get_token(username, password).await?;

        // Decode the token to get user info
        let claims = if let Some(public_key) = &self.settings.public_key {
            self.decode_jwt_with_validation(&token_response.access_token, public_key)?
        } else {
            // If public key is not available, decode without validation
            return Err(SsoError::MissingPublicKey);
        };

        Ok(UserInfo {
            username: claims.preferred_username,
            email: claims.email,
        })
    }

    pub async fn authenticate_callback_code(&self, code: &str) -> Result<UserInfo, SsoError> {
        let token_response = self.get_token_from_code(code).await?;

        // Decode the code to get user info
        let claims = if let Some(public_key) = &self.settings.public_key {
            self.decode_jwt_with_validation(&token_response.access_token, public_key)?
        } else {
            return Err(SsoError::MissingPublicKey);
        };

        Ok(UserInfo {
            username: claims.preferred_username,
            email: claims.email,
        })
    }

    pub fn authorization_url(&self, state: &str) -> String {
        format!(
            "{}/realms/{}/protocol/openid-connect/auth?client_id={}&response_type=code&scope={}&redirect_uri={}&state={}",
            self.settings.auth_url,
            self.settings.auth_realm,
            self.settings.client_id,
            self.settings.scope,
            self.settings.redirect_uri,
            state
        )
    }
}
