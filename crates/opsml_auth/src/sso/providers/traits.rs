use crate::sso::error::SsoError;
use crate::sso::providers::types::{IdTokenClaims, OidcErrorResponse, TokenResponse};
use crate::sso::types::UserInfo;
use async_trait::async_trait;
use jsonwebtoken::{decode, DecodingKey, Validation};
use reqwest::StatusCode;
use tracing::{debug, error};
#[async_trait]
pub trait SsoProvider {
    fn client(&self) -> &reqwest::Client;

    fn token_url(&self) -> &str;
    fn build_auth_params<'a>(
        &'a self,
        username: &'a str,
        password: &'a str,
    ) -> Vec<(&'a str, &'a str)>;
    fn build_callback_auth_params<'a>(&'a self, code: &'a str) -> Vec<(&'a str, &'a str)>;
    fn decoding_key(&self) -> &DecodingKey;

    async fn make_token_request(
        &self,
        params: Vec<(&str, &str)>,
    ) -> Result<TokenResponse, SsoError> {
        let response = self
            .client()
            .post(self.token_url())
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

    async fn get_token_from_user_pass(
        &self,
        username: &str,
        password: &str,
    ) -> Result<TokenResponse, SsoError> {
        let params = self.build_auth_params(username, password);

        debug!("Requesting token from Keycloak");
        self.make_token_request(params).await
    }

    async fn get_token_from_code(&self, code: &str) -> Result<TokenResponse, SsoError> {
        // Implement the token retrieval logic using the authorization code
        let params = self.build_callback_auth_params(code);
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

        let token_data = decode::<IdTokenClaims>(id_token, &self.decoding_key(), &validation)
            .map_err({
                |e| {
                    error!("Failed to decode JWT token: {}", e);
                    SsoError::JwtDecodeError(e)
                }
            })?;

        Ok(token_data.claims)
    }

    async fn authenticate_resource_password(
        &self,
        username: &str,
        password: &str,
    ) -> Result<UserInfo, SsoError> {
        // Implement the authentication logic here
        debug!("Requesting token from Okta for {}", username);

        // Get access token from Okta
        let token_response = self
            .get_token_from_user_pass(username, password)
            .await
            .map_err(|e| {
                error!("Failed to get token from Okta: {}", e);
                e
            })?;

        // Decode the token to get user info
        let claims = self.decode_jwt_with_validation(&token_response.id_token)?;

        Ok(UserInfo {
            username: claims.preferred_username,
            email: claims.email,
        })
    }

    async fn authenticate_auth_flow(&self, code: &str) -> Result<UserInfo, SsoError> {
        let token_response = self.get_token_from_code(code).await?;

        // Decode the code to get user info
        let claims = self.decode_jwt_with_validation(&token_response.id_token)?;

        Ok(UserInfo {
            username: claims.preferred_username,
            email: claims.email,
        })
    }

    fn authorization_url(&self, state: &str) -> String;
}
