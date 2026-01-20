use crate::sso::error::SsoError;

use jsonwebtoken::DecodingKey;

use crate::sso::providers::traits::SsoProviderExt;
use crate::sso::providers::types::{get_env_var, JwkResponse};
use base64::prelude::*;
use reqwest::{Client, StatusCode};

use tracing::{error, info};

#[derive(Clone)]
pub struct OktaSettings {
    pub client_id: String,
    pub client_secret: String,
    pub redirect_uri: String,
    pub jwk_response: JwkResponse,
    pub scope: String,
    pub token_url: String,
    pub authorization_url: String,
}

impl OktaSettings {
    pub async fn from_env(client: &Client) -> Result<Self, SsoError> {
        let client_id = get_env_var("OPSML_CLIENT_ID")?;
        let client_secret = get_env_var("OPSML_CLIENT_SECRET")?;
        let redirect_uri = get_env_var("OPSML_REDIRECT_URI")?;
        let okta_domain = get_env_var("OPSML_AUTH_DOMAIN")?;

        let scope = std::env::var("OPSML_AUTH_SCOPE")
            .unwrap_or_else(|_| "openid email profile".to_string());

        let authorization_server_id = std::env::var("OPSML_AUTHORIZATION_SERVER_ID").ok();

        let format_okta_url = |endpoint: &str| {
            if let Some(server_id) = &authorization_server_id {
                format!("{okta_domain}/oauth2/{server_id}/{endpoint}")
            } else {
                format!("{okta_domain}/oauth2/{endpoint}")
            }
        };

        let token_url = format_okta_url("v1/token");
        let certs_url = format_okta_url("v1/keys");
        let authorization_url = format_okta_url("v1/authorize");

        let response = client
            .get(&certs_url)
            .send()
            .await
            .map_err(SsoError::ReqwestError)?;

        let jwk_response = match response.status() {
            StatusCode::OK => response
                .json::<JwkResponse>()
                .await
                .map_err(SsoError::ReqwestError)?,
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
            token_url,
            jwk_response,
            scope,
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
            ("redirect_uri", &self.redirect_uri),
            ("code", code),
            ("scope", &self.scope),
            ("code_verifier", code_verifier),
        ]
    }
}

pub struct OktaProvider {
    pub client: Client,
    pub settings: OktaSettings,
}

impl OktaProvider {
    pub async fn new(client: Client) -> Result<Self, SsoError> {
        let settings = OktaSettings::from_env(&client).await?;

        info!("Okta SSO provider initialized");
        Ok(Self { client, settings })
    }
}

impl SsoProviderExt for OktaProvider {
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
        true // Okta requires basic auth for token requests
    }

    fn headers(&self) -> reqwest::header::HeaderMap {
        let mut headers = reqwest::header::HeaderMap::new();

        headers.insert(
            reqwest::header::AUTHORIZATION,
            format!(
                "Basic {}",
                BASE64_STANDARD.encode(format!("{}:{}", self.client_id(), self.client_secret()))
            )
            .parse()
            .unwrap(),
        );
        // application json
        headers.insert(reqwest::header::ACCEPT, "application/json".parse().unwrap());
        headers
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
