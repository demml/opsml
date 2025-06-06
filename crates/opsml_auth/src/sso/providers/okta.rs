use crate::sso::error::SsoError;
use crate::sso::types::UserInfo;
use jsonwebtoken::DecodingKey;

use jsonwebtoken::{decode, Validation};
use reqwest::{Client, StatusCode};
use serde::{Deserialize, Serialize};
use tracing::{debug, error};

#[derive(Debug, Serialize, Deserialize)]
pub struct OktaTokenClaims {
    pub ver: u8,
    pub jti: String,
    pub iss: String,
    pub aud: String,
    pub sub: String,
    pub iat: usize,
    pub exp: usize,
    pub cid: String,
    pub uid: String,
    pub scp: Vec<String>,
    pub auth_time: usize,
}

#[derive(Debug, Deserialize)]
pub struct OktaErrorResponse {
    pub error: String,
    pub error_description: String,
}

#[derive(Debug, Deserialize, Serialize, Clone, Default)]
pub struct OktaOktaJwkResponse {
    pub keys: Vec<OktaJwk>,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct OktaJwk {
    pub kty: String,
    pub alg: String,
    pub kid: String,
    #[serde(rename = "use")]
    pub use_: String,
    pub e: String,
    pub n: String,
}

impl OktaOktaJwkResponse {
    /// Currently only support jwk format
    pub fn decode_jwk(&self) -> Result<DecodingKey, SsoError> {
        // get first key
        let key = self.keys.get(0).ok_or(SsoError::MissingPublicKey)?;
        Ok(DecodingKey::from_rsa_components(&key.n, &key.e).map_err(SsoError::JwtDecodeError)?)
    }
}

#[derive(Debug, Clone, Default, Serialize)]
pub struct OktaSettings {
    pub client_id: String,
    pub client_secret: String,
    pub redirect_uri: String,
    pub okta_domain: String,
    pub authorization_server_id: Option<String>,
    pub token_url: String,
    pub authorization_url: String,
    pub public_key: OktaOktaJwkResponse,
    pub scope: String,
}

impl OktaSettings {
    pub async fn from_env(client: &Client) -> Result<Self, SsoError> {
        fn get_env_var(name: &str) -> Result<String, SsoError> {
            std::env::var(name).map_err(SsoError::OktaEnvVarError)
        }

        let client_id = get_env_var("OKTA_CLIENT_ID")?;
        let client_secret = get_env_var("OKTA_CLIENT_SECRET")?;
        let redirect_uri = get_env_var("OKTA_REDIRECT_URI")?;
        let okta_domain = get_env_var("OKTA_DOMAIN")?;
        let okta_scope =
            std::env::var("OKTA_SCOPE").unwrap_or_else(|_| "openid profile email".to_string());
        let authorization_server_id = std::env::var("OKTA_AUTHORIZATION_SERVER_ID").ok();

        let format_okta_url = |endpoint: &str| {
            if let Some(server_id) = &authorization_server_id {
                format!("https://{}/oauth2/{}/{}", okta_domain, server_id, endpoint)
            } else {
                format!("https://{}/oauth2/{}", okta_domain, endpoint)
            }
        };

        let token_url = format_okta_url("v1/token");
        let public_key_url = format_okta_url("v1/keys");
        let authorization_url = format_okta_url("v1/authorize");

        // Fetch public key from Okta
        debug!("Fetching public key from Okta at {}", public_key_url);
        let response = client.get(&public_key_url).send().await?;

        let public_key = if response.status().is_success() {
            response
                .json::<OktaOktaJwkResponse>()
                .await
                .map_err(SsoError::ReqwestError)?
        } else {
            error!(
                "Failed to fetch public key from Okta. Status: {}",
                response.status()
            );
            return Err(SsoError::MissingPublicKey);
        };

        Ok(Self {
            client_id,
            client_secret,
            redirect_uri,
            okta_domain,
            token_url,
            public_key: public_key,
            scope: okta_scope,
            authorization_server_id,
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

#[derive(Deserialize, Debug, Default)]
pub struct OktaTokenResponse {
    pub token_type: String,
    pub expires_in: u64,
    pub access_token: String,
    pub scope: String,
    pub id_token: String,
    pub refresh_token: Option<String>,
}

pub struct OktaProvider {
    pub client: Client,
    pub settings: OktaSettings,
    pub decoding_key: DecodingKey,
}

impl OktaProvider {
    pub async fn new(client: Client) -> Result<Self, SsoError> {
        let settings = OktaSettings::from_env(&client).await?;

        let decoding_key = settings.public_key.decode_jwk()?;

        Ok(Self {
            client,
            settings,
            decoding_key,
        })
    }

    /// Method use for retrieving an access token from Okta using username and password.
    pub async fn get_token_from_user_pass(
        &self,
        username: &str,
        password: &str,
    ) -> Result<OktaTokenResponse, SsoError> {
        // Implement the token retrieval logic here
        let params = self.settings.build_auth_params(username, password);

        let response = self
            .client
            .post(&self.settings.token_url)
            .basic_auth(&self.settings.client_id, Some(&self.settings.client_secret))
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
            if let Ok(error_response) = response.json::<OktaErrorResponse>().await {
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

        Ok(response.json::<OktaTokenResponse>().await?)
    }

    pub async fn get_token_from_code(&self, code: &str) -> Result<OktaTokenResponse, SsoError> {
        // Implement the token retrieval logic using the authorization code
        let params = self.settings.build_callback_auth_params(code);

        let response = self
            .client
            .post(&self.settings.token_url)
            .basic_auth(&self.settings.client_id, Some(&self.settings.client_secret))
            .form(&params)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .send()
            .await
            .map_err(|e| {
                error!("Failed to send request to Okta: {}", e);
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
            if let Ok(error_response) = response.json::<OktaErrorResponse>().await {
                return Err(SsoError::AuthenticationFailed(
                    error_response.error_description,
                ));
            }

            // Fallback to generic error
            return Err(SsoError::FallbackError(status.to_string()));
        }

        let token = response
            .json::<OktaTokenResponse>()
            .await
            .map_err(SsoError::ReqwestError)?;

        Ok(token)
    }

    /// Decode a JWT token with validation against the Okta public key.
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
        public_key: &DecodingKey,
    ) -> Result<OktaTokenClaims, SsoError> {
        let mut validation = Validation::new(jsonwebtoken::Algorithm::RS256);
        validation.validate_aud = false;

        let token_data = decode::<OktaTokenClaims>(token, public_key, &validation).map_err({
            |e| {
                error!("Failed to decode JWT token: {}", e);
                SsoError::JwtDecodeError(e)
            }
        })?;

        Ok(token_data.claims)
    }

    pub async fn authenticate_resource_password(
        &self,
        username: &str,
        password: &str,
    ) -> Result<UserInfo, SsoError> {
        // Implement the authentication logic here
        debug!("Requesting token from Okta at {}", self.settings.token_url);

        // Get access token from Okta
        let token_response = self.get_token_from_user_pass(username, password).await?;

        // Decode the token to get user info
        let claims =
            self.decode_jwt_with_validation(&token_response.access_token, &self.decoding_key)?;

        Ok(UserInfo {
            username: claims.sub.clone(),
            email: claims.sub,
        })
    }

    pub async fn authenticate_auth_flow(&self, code: &str) -> Result<UserInfo, SsoError> {
        let token_response = self.get_token_from_code(code).await?;

        // Decode the code to get user info
        let claims =
            self.decode_jwt_with_validation(&token_response.access_token, &self.decoding_key)?;

        Ok(UserInfo {
            username: claims.sub.clone(),
            email: claims.sub,
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
