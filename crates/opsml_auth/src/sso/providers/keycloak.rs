use crate::sso::error::SsoError;
use crate::sso::types::UserInfo;
use jsonwebtoken::DecodingKey;
use jsonwebtoken::{decode, Validation};
use reqwest::{Client, StatusCode};
use serde::Deserialize;
use tracing::{debug, error};

use crate::sso::providers::types::{
    get_env_var, IdTokenClaims, JwkResponse, OidcErrorResponse, TokenResponse,
};

#[derive(Clone)]
pub struct KeycloakSettings {
    pub client_id: String,
    pub client_secret: String,
    pub redirect_uri: String,
    pub decoding_key: DecodingKey,
    pub scope: String,
    pub token_url: String,
    pub authorization_url: String,
}

impl KeycloakSettings {
    pub async fn from_env(client: &Client) -> Result<Self, SsoError> {
        let client_id = get_env_var("KEYCLOAK_CLIENT_ID")?;
        let client_secret = get_env_var("KEYCLOAK_CLIENT_SECRET")?;
        let redirect_uri = get_env_var("KEYCLOAK_REDIRECT_URI")?;
        let auth_domain = get_env_var("KEYCLOAK_AUTH_DOMAIN")?;

        let auth_realm = get_env_var("KEYCLOAK_AUTH_REALM")?;

        let scope =
            std::env::var("KEYCLOAK_SCOPE").unwrap_or_else(|_| "openid profile email".to_string());

        let token_url = format!(
            "{}/realms/{}/protocol/openid-connect/token",
            auth_domain, auth_realm
        );

        let authorization_url = format!(
            "{}/realms/{}/protocol/openid-connect/auth",
            auth_domain, auth_realm
        );

        let certs_url = format!(
            "{}/realms/{}/protocol/openid-connect/certs",
            auth_domain, auth_realm
        );

        let response = client
            .get(&certs_url)
            .send()
            .await
            .map_err(SsoError::ReqwestError)?;

        let decoding_key = match response.status() {
            StatusCode::OK => {
                let jwk_response = response
                    .json::<JwkResponse>()
                    .await
                    .map_err(SsoError::ReqwestError)?;
                jwk_response.get_decoded_key()?
            }
            _ => {
                // get response body
                let body = response.text().await.map_err(SsoError::ReqwestError)?;
                error!("Failed to fetch public key from Keycloak at {}. Tokens will not be validated when decoding", certs_url);
                return Err(SsoError::FailedToFetchJwk(body));
            }
        };

        Ok(Self {
            client_id,
            client_secret,
            redirect_uri,
            decoding_key,
            scope,
            token_url,
            authorization_url,
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
        let settings = KeycloakSettings::from_env(&client).await?;

        Ok(Self { client, settings })
    }

    pub async fn make_token_request(
        &self,
        params: Vec<(&str, &str)>,
    ) -> Result<TokenResponse, SsoError> {
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
            // Get response body text first
            let body = response.text().await.map_err(SsoError::ReqwestError)?;

            // Try to parse error response for more detail
            if let Ok(error_response) = serde_json::from_str::<OidcErrorResponse>(&body) {
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

            // Fallback to generic error with the body we already have
            return Err(SsoError::FallbackError(body));
        }

        Ok(response.json::<TokenResponse>().await?)
    }

    pub async fn get_token_from_user_pass(
        &self,
        username: &str,
        password: &str,
    ) -> Result<TokenResponse, SsoError> {
        let params = self.settings.build_auth_params(username, password);

        debug!("Requesting token from Keycloak");
        self.make_token_request(params).await
    }

    pub async fn get_token_from_code(&self, code: &str) -> Result<TokenResponse, SsoError> {
        // Implement the token retrieval logic using the authorization code
        let params = self.settings.build_callback_auth_params(code);
        debug!("Requesting token from Keycloak with code");
        self.make_token_request(params).await
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
    fn decode_jwt_with_validation(&self, id_token: &str) -> Result<IdTokenClaims, SsoError> {
        let mut validation = Validation::new(jsonwebtoken::Algorithm::RS256);
        validation.validate_aud = false;

        let token_data =
            decode::<IdTokenClaims>(id_token, &self.settings.decoding_key, &validation).map_err(
                {
                    |e| {
                        error!("Failed to decode JWT token: {}", e);
                        SsoError::JwtDecodeError(e)
                    }
                },
            )?;

        Ok(token_data.claims)
    }

    pub async fn authenticate_resource_password(
        &self,
        username: &str,
        password: &str,
    ) -> Result<UserInfo, SsoError> {
        // Implement the authentication logic here
        debug!(
            "Requesting token from Keycloak at {}",
            self.settings.token_url
        );

        // Get access token from Keycloak
        let token_response = self.get_token_from_user_pass(username, password).await?;

        // Decode the token to get user info
        let claims = self.decode_jwt_with_validation(&token_response.id_token)?;

        Ok(UserInfo {
            username: claims.preferred_username,
            email: claims.email,
        })
    }

    pub async fn authenticate_auth_flow(&self, code: &str) -> Result<UserInfo, SsoError> {
        let token_response = self.get_token_from_code(code).await?;

        // Decode the code to get user info
        let claims = self.decode_jwt_with_validation(&token_response.id_token)?;

        Ok(UserInfo {
            username: claims.preferred_username,
            email: claims.email,
        })
    }

    pub fn authorization_url(&self, state: &str) -> String {
        format!(
            "{}?client_id={}&response_type=code&scope={}&redirect_uri={}&state={}",
            self.settings.authorization_url,
            self.settings.client_id,
            self.settings.scope,
            self.settings.redirect_uri,
            state
        )
    }
}
