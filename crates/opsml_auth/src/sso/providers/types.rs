use crate::sso::error::SsoError;
use jsonwebtoken::{decode_header, DecodingKey};
use serde::{Deserialize, Serialize};
use tracing::{debug, error};

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

    pub fn signing_key_by_kid(&self, kid: &str) -> Option<&Jwk> {
        self.keys
            .iter()
            .find(|key| key.kid == kid && key.use_ == "sig")
    }

    /// Get the decoding key for a specific token by extracting the kid from its header
    pub fn get_decoded_key_for_token(&self, token: &str) -> Result<DecodingKey, SsoError> {
        // Decode the JWT header to get the kid
        let header = decode_header(token).map_err(SsoError::JwtDecodeError)?;

        debug!("Decoded JWT header: {:?}", header);

        let kid = header
            .kid
            .ok_or(SsoError::MissingSigningKey)
            .inspect_err(|_| {
                error!("No 'kid' found in token header");
            })?;

        let signing_key = self
            .signing_key_by_kid(&kid)
            .ok_or(SsoError::MissingSigningKey)
            .inspect_err(|_| {
                error!("No signing key found for kid: {}", kid);
            })?;

        DecodingKey::from_rsa_components(&signing_key.n, &signing_key.e)
            .map_err(SsoError::JwtDecodeError)
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
