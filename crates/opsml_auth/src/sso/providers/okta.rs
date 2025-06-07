use crate::sso::error::SsoError;

use jsonwebtoken::DecodingKey;

use crate::sso::providers::traits::SsoProvider;
use crate::sso::providers::types::{get_env_var, JwkResponse};

use reqwest::{Client, StatusCode};

use tracing::{debug, error};

#[derive(Clone)]
pub struct OktaSettings {
    pub client_id: String,
    pub client_secret: String,
    pub redirect_uri: String,
    pub decoding_key: DecodingKey,
    pub scope: String,
    pub token_url: String,
    pub authorization_url: String,
}

impl OktaSettings {
    pub async fn from_env(client: &Client) -> Result<Self, SsoError> {
        let client_id = get_env_var("OKTA_CLIENT_ID")?;
        let client_secret = get_env_var("OKTA_CLIENT_SECRET")?;
        let redirect_uri = get_env_var("OKTA_REDIRECT_URI")?;
        let okta_domain = get_env_var("OKTA_DOMAIN")?;

        let scope =
            std::env::var("OKTA_SCOPE").unwrap_or_else(|_| "openid profile email".to_string());

        let authorization_server_id = std::env::var("OKTA_AUTHORIZATION_SERVER_ID").ok();

        let format_okta_url = |endpoint: &str| {
            if let Some(server_id) = &authorization_server_id {
                format!("{}/oauth2/{}/{}", okta_domain, server_id, endpoint)
            } else {
                format!("{}/oauth2/{}", okta_domain, endpoint)
            }
        };

        let token_url = format_okta_url("v1/token");
        let certs_url = format_okta_url("v1/keys");
        let authorization_url = format_okta_url("v1/authorize");

        // Fetch public key from Okta
        debug!("Fetching public key from Okta at {}", certs_url);

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
            token_url,
            decoding_key,
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

    pub fn build_callback_auth_params<'a>(&'a self, code: &'a str) -> Vec<(&'a str, &'a str)> {
        vec![
            ("grant_type", "authorization_code"),
            ("redirect_uri", &self.redirect_uri),
            ("code", code),
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

        Ok(Self { client, settings })
    }
}

impl SsoProvider for OktaProvider {
    fn client(&self) -> &Client {
        &self.client
    }

    fn token_url(&self) -> &str {
        &self.settings.token_url
    }

    fn build_auth_params<'a>(
        &'a self,
        username: &'a str,
        password: &'a str,
    ) -> Vec<(&'a str, &'a str)> {
        self.settings.build_auth_params(username, password)
    }

    fn build_callback_auth_params<'a>(&'a self, code: &'a str) -> Vec<(&'a str, &'a str)> {
        self.settings.build_callback_auth_params(code)
    }

    fn decoding_key(&self) -> &DecodingKey {
        &self.settings.decoding_key
    }

    fn authorization_url(&self, state: &str) -> String {
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
