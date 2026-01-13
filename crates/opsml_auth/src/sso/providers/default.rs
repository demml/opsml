use crate::sso::error::SsoError;
use crate::sso::providers::traits::SsoProviderExt;
use crate::sso::providers::types::{get_env_var, JwkResponse};
use jsonwebtoken::DecodingKey;
use reqwest::{Client, StatusCode};

use tracing::{error, info};

#[derive(Clone)]
pub struct DefaultSsoSettings {
    pub client_id: String,
    pub client_secret: String,
    pub redirect_uri: String,
    pub jwk_response: JwkResponse,
    pub scope: String,
    pub token_url: String,
    pub authorization_url: String,
}

impl DefaultSsoSettings {
    pub async fn from_env(client: &Client) -> Result<Self, SsoError> {
        let client_id = get_env_var("OPSML_CLIENT_ID")?;
        let client_secret = get_env_var("OPSML_CLIENT_SECRET")?;
        let redirect_uri = get_env_var("OPSML_REDIRECT_URI")?;
        let auth_domain = get_env_var("OPSML_AUTH_DOMAIN")?;

        let token_endpoint = get_env_var("OPSML_TOKEN_ENDPOINT")?;
        let certs_endpoint = get_env_var("OPSML_CERT_ENDPOINT")?;
        let authorization_endpoint = get_env_var("OPSML_AUTHORIZATION_ENDPOINT")?;

        let scope = std::env::var("OPSML_AUTH_SCOPE")
            .unwrap_or_else(|_| "openid email profile".to_string());

        let token_url = format!("{auth_domain}/{token_endpoint}");
        let authorization_url = format!("{auth_domain}/{authorization_endpoint}");
        let certs_url = format!("{auth_domain}/{certs_endpoint}");

        let response = client
            .get(&certs_url)
            .send()
            .await
            .map_err(SsoError::ReqwestError)?;

        let jwk_response = match response.status() {
            StatusCode::OK => {
                response.json::<JwkResponse>().await.map_err(|e| {
                    error!("Failed to parse JWK response from Keycloak at {certs_url} error: {e}");
                    SsoError::ReqwestError(e)
                })?
            }
            _ => {
                // get response body
                let body = response.text().await.map_err(SsoError::ReqwestError)?;
                error!("Failed to fetch public key from Keycloak at {certs_url}. Tokens will not be validated when decoding");
                return Err(SsoError::FailedToFetchJwk(body));
            }
        };

        Ok(Self {
            client_id,
            client_secret,
            redirect_uri,
            jwk_response,
            scope,
            token_url,
            authorization_url,
        })
    }

    /// params for resource owner password credentials grant
    /// # Arguments
    /// * `username` - the username of the user
    /// * `password` - the password of the user
    /// # Returns
    /// a vector of tuples containing the parameters for the request
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
            ("scope", &self.scope),
        ]
    }

    /// params for authorization code grant
    /// # Arguments
    /// * `code` - the authorization code received from the authorization server
    /// * `code_verifier` - the code verifier used in the PKCE flow
    /// # Returns
    /// a vector of tuples containing the parameters for the request
    pub fn build_callback_auth_params<'a>(
        &'a self,
        code: &'a str,
        code_verifier: &'a str,
    ) -> Vec<(&'a str, &'a str)> {
        vec![
            ("grant_type", "authorization_code"),
            ("client_id", &self.client_id),
            ("client_secret", &self.client_secret),
            ("redirect_uri", &self.redirect_uri),
            ("code", code),
            ("code_verifier", code_verifier),
            ("scope", &self.scope),
        ]
    }
}

pub struct DefaultProvider {
    pub client: Client,
    pub settings: DefaultSsoSettings,
}

impl DefaultProvider {
    pub async fn new(client: Client) -> Result<Self, SsoError> {
        let settings = DefaultSsoSettings::from_env(&client).await?;

        info!("Default SSO provider initialized");

        // scouter not integrated - exist early
        Ok(Self { client, settings })
    }
}

impl SsoProviderExt for DefaultProvider {
    fn client(&self) -> &Client {
        &self.client
    }

    fn token_url(&self) -> &str {
        &self.settings.token_url
    }

    fn authorization_url(&self) -> &str {
        &self.settings.authorization_url
    }
    fn client_id(&self) -> &str {
        &self.settings.client_id
    }
    fn redirect_uri(&self) -> &str {
        &self.settings.redirect_uri
    }
    fn scope(&self) -> &str {
        &self.settings.scope
    }
    fn client_secret(&self) -> &str {
        &self.settings.client_secret
    }

    fn require_basic_auth(&self) -> bool {
        false
    }

    fn headers(&self) -> reqwest::header::HeaderMap {
        reqwest::header::HeaderMap::new()
    }

    fn build_auth_params<'a>(
        &'a self,
        username: &'a str,
        password: &'a str,
    ) -> Vec<(&'a str, &'a str)> {
        self.settings.build_auth_params(username, password)
    }

    fn build_callback_auth_params<'a>(
        &'a self,
        code: &'a str,
        code_verifier: &'a str,
    ) -> Vec<(&'a str, &'a str)> {
        self.settings
            .build_callback_auth_params(code, code_verifier)
    }

    fn get_decoding_key_for_token(&self, token: &str) -> Result<DecodingKey, SsoError> {
        self.settings.jwk_response.get_decoded_key_for_token(token)
    }
}
