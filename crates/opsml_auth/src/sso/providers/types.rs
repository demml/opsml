use jsonwebtoken::DecodingKey;
use serde::{Deserialize, Serialize};

use crate::sso::error::SsoError;

pub enum Provider {
    Keycloak,
    Okta,
    Other,
}

#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub enum Algorithm {
    #[default]
    RS256,
    RS384,
    RS512,
    #[serde(rename = "RSA-OAEP")]
    RsaOaep,
    #[serde(other)]
    Unknown,
}
#[derive(Debug, Deserialize, Serialize, Clone, Default)]
pub struct JwkResponse {
    pub keys: Vec<Jwk>,
}

impl JwkResponse {
    /// Retrieve the signing key from the JWK response.
    /// OIDC standards use an RS256 algorithm for signing.
    pub fn signing_key(&self) -> Option<&Jwk> {
        self.keys
            .iter()
            .find(|key| key.alg == Algorithm::RS256 && key.use_ == "sig")
    }

    /// Get the public key in PEM format from the JWK response.
    /// This is needed to verify JWT signatures.
    pub fn get_decoded_key(&self) -> Result<DecodingKey, SsoError> {
        let signing_key = self.signing_key().ok_or(SsoError::MissingSigningKey)?;
        DecodingKey::from_rsa_components(&signing_key.n, &signing_key.e)
            .map_err(SsoError::JwtDecodeError)
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct Jwk {
    pub kty: String,
    pub alg: Algorithm,
    pub kid: String,
    #[serde(rename = "use")]
    pub use_: String,
    pub e: String,
    pub n: String,
}

#[derive(Debug, Deserialize)]
pub struct OidcErrorResponse {
    pub error: String,
    pub error_description: String,
}

pub fn get_env_var(name: &str) -> Result<String, SsoError> {
    std::env::var(name).map_err(|_| SsoError::EnvVarNotSet(name.to_string()))
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct TokenResponse {
    pub access_token: String,
    pub expires_in: u64,
    pub token_type: String,
    pub scope: String,
    pub id_token: String,
}

/// Only extract the fields we need to validate or create a user in opsml
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct IdTokenClaims {
    pub email: String,
    pub preferred_username: Option<String>,
    pub name: Option<String>,
    pub exp: u64,
    pub sub: String,
}
