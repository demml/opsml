use crate::sso::error::SsoError;
use crate::sso::providers::traits::SsoProviderExt;
use crate::sso::providers::types::{get_env_var, JwkResponse};
use jsonwebtoken::DecodingKey;
use reqwest::{Client, StatusCode};

use tracing::{error, info};

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
        let client_id = get_env_var("OPSML_CLIENT_ID")?;
        let client_secret = get_env_var("OPSML_CLIENT_SECRET")?;
        let redirect_uri = get_env_var("OPSML_REDIRECT_URI")?;
        let auth_domain = get_env_var("OPSML_AUTH_DOMAIN")?;

        let auth_realm = get_env_var("OPSML_AUTH_REALM")?;

        let scope = std::env::var("OPSML_AUTH_SCOPE")
            .unwrap_or_else(|_| "openid email profile".to_string());

        let token_url = format!("{auth_domain}/realms/{auth_realm}/protocol/openid-connect/token");

        let authorization_url =
            format!("{auth_domain}/realms/{auth_realm}/protocol/openid-connect/auth");

        let certs_url = format!("{auth_domain}/realms/{auth_realm}/protocol/openid-connect/certs");

        let response = client
            .get(&certs_url)
            .send()
            .await
            .map_err(SsoError::ReqwestError)?;

        let decoding_key = match response.status() {
            StatusCode::OK => {
                let jwk_response = response.json::<JwkResponse>().await.map_err(|e| {
                    error!(
                        "Failed to parse JWK response from Keycloak at {} error: {}",
                        certs_url, e
                    );
                    SsoError::ReqwestError(e)
                })?;
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
            ("scope", &self.scope),
        ]
    }

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

pub struct KeycloakProvider {
    pub client: Client,
    pub settings: KeycloakSettings,
}

impl KeycloakProvider {
    pub async fn new(client: Client) -> Result<Self, SsoError> {
        let settings = KeycloakSettings::from_env(&client).await?;

        info!("Keycloak SSO provider initialized");

        // scouter not integrated - exist early
        Ok(Self { client, settings })
    }
}

impl SsoProviderExt for KeycloakProvider {
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

    fn decoding_key(&self) -> &DecodingKey {
        &self.settings.decoding_key
    }
}
