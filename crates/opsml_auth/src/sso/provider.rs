use crate::sso::error::SsoError;
use crate::sso::providers::default::DefaultProvider;
use crate::sso::providers::keycloak::KeycloakProvider;
use crate::sso::providers::okta::OktaProvider;
use crate::sso::providers::traits::SsoProviderExt;
use crate::sso::types::UserInfo;
use reqwest::Client;
use tracing::debug;

pub enum SsoProvider {
    Keycloak(KeycloakProvider),
    Okta(OktaProvider),
    Default(DefaultProvider),
}

impl SsoProvider {
    pub fn as_str(&self) -> &str {
        match self {
            SsoProvider::Keycloak(_) => "keycloak",
            SsoProvider::Okta(_) => "okta",
            SsoProvider::Default(_) => "default",
        }
    }

    pub async fn from_str(provider: &str) -> Result<Self, SsoError> {
        let client = Client::new();
        match provider.to_lowercase().as_str() {
            "keycloak" => Ok(SsoProvider::Keycloak(KeycloakProvider::new(client).await?)),
            "okta" => Ok(SsoProvider::Okta(OktaProvider::new(client).await?)),
            "default" => Ok(SsoProvider::Default(DefaultProvider::new(client).await?)),
            _ => Err(SsoError::InvalidProvider(provider.to_string())),
        }
    }

    pub async fn from_env() -> Result<Self, SsoError> {
        let client = Client::new();

        let provider_value = std::env::var("SSO_PROVIDER").map_err(|e| {
            tracing::debug!("SSO_PROVIDER env var error: {:?}", e);
            SsoError::EnvVarNotSet("SSO_PROVIDER".to_string())
        })?;

        debug!("SSO_PROVIDER value: {}", provider_value);

        match provider_value.to_lowercase().as_str() {
            "keycloak" => {
                debug!("Initializing Keycloak provider");
                Ok(SsoProvider::Keycloak(KeycloakProvider::new(client).await?))
            }
            "okta" => {
                debug!("Initializing Okta provider");
                Ok(SsoProvider::Okta(OktaProvider::new(client).await?))
            }
            "default" => {
                debug!("Initializing Default provider");
                Ok(SsoProvider::Default(DefaultProvider::new(client).await?))
            }
            _ => {
                debug!("Invalid SSO_PROVIDER value: {}", provider_value);
                Err(SsoError::SsoNotConfigured)
            }
        }
    }

    pub fn is_enabled() -> bool {
        std::env::var("SSO_ENABLED")
            .map(|val| val.to_lowercase() == "true")
            .unwrap_or(false)
    }

    pub async fn authenticate_resource_password(
        &self,
        username: &str,
        password: &str,
    ) -> Result<UserInfo, SsoError> {
        match self {
            SsoProvider::Keycloak(provider) => {
                provider
                    .authenticate_resource_password(username, password)
                    .await
            }
            SsoProvider::Okta(provider) => {
                provider
                    .authenticate_resource_password(username, password)
                    .await
            }
            SsoProvider::Default(provider) => {
                provider
                    .authenticate_resource_password(username, password)
                    .await
            }
        }
    }

    pub async fn authenticate_auth_flow(
        &self,
        code: &str,
        code_verifier: &str,
    ) -> Result<UserInfo, SsoError> {
        match self {
            SsoProvider::Keycloak(provider) => {
                provider.authenticate_auth_flow(code, code_verifier).await
            }
            SsoProvider::Okta(provider) => {
                provider.authenticate_auth_flow(code, code_verifier).await
            }
            SsoProvider::Default(provider) => {
                provider.authenticate_auth_flow(code, code_verifier).await
            }
        }
    }

    pub fn authorization_url(
        &self,
        state: &str,
        code_challenge: &str,
        code_challenge_method: &str,
    ) -> String {
        match self {
            SsoProvider::Keycloak(provider) => {
                provider.get_authorization_url(state, code_challenge, code_challenge_method)
            }
            SsoProvider::Okta(provider) => {
                provider.get_authorization_url(state, code_challenge, code_challenge_method)
            }
            SsoProvider::Default(provider) => {
                provider.get_authorization_url(state, code_challenge, code_challenge_method)
            }
        }
    }
}
#[cfg(test)]
mod tests {
    use crate::sso::providers::types::{Algorithm, JwkResponse};
    use crate::sso::providers::types::{IdTokenClaims, Jwk};

    use super::*;
    use base64::prelude::*;
    use jsonwebtoken::encode;

    use jsonwebtoken::EncodingKey;
    use jsonwebtoken::Header;
    use mockito::{Server, ServerGuard};

    use std::time::SystemTime;
    use std::time::UNIX_EPOCH;

    fn create_mock_token_response() -> String {
        // this is a mock private key generated offline for testing purposes
        let mock_private_key = r#"-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDLZgJBLA7tvzJq
lfiBnlQyqv+VD9fN0bDIXWkX+KFutlMos2UZ3jZSLb68QD4Sw0Uuvs+Vpuxbo7ni
lddtALrwcJF9LvqFMj1JqtfOmcQouJbrURxBd6c0B5EVXq20o2udZ0FuWHmUDrZv
Cv0bTFE1LgaEisjX3qyZenhbgghbXidrNR3gAX7GdS4cy7IRMN7alZWGpXJYyyB/
6QdOzszhZ4H1eRNYdYYdgJTny8oBM3T//CwFiaR67lqs9tdj6xe5BfgoRa5kH9Wt
RA31+2fUI9f+FtLzYpx79OsbyYgJlzH9Kco6mPZvsRns3fb4M9+SHsUoFMQhvJx7
Lt2bDUkxAgMBAAECggEBAIJhf2x7a45nE1BTlhqwfVSFXJQWtcUPd3zYs/dTv1eS
tDfQ1yv/z15aSHuvypqIZZ6TXcmWWMhdaVifqJoM78gUwI44QQqEq9i/FNswohdg
TA3Hzo8AvkOR3iSOrlaustsRR1YOjNClpbgEmT6Yay3ltPPdauVFreosIV63Odgm
mtifvmQHO3Fs61o/jUG/yRY//CYibF+heMxvrSkSHkRa86A1ludFLqy0sY80j4wn
vggszRCxsAX14/LMBwcnIl0d0sf9ni6379fMn/W2qcBoRUSnUFFmxfAdnnZzdaVD
UyzXaYDWHP7IMzJxu8vywkYoQdhCxqzTtJrqL/e2oikCgYEAz+OwqDt0Eu60Rxn5
nxzjgm42/vhNWuXtlGaTS7i2+sM40cA3YMqk8LPP2Codf18D+3NEkzXbW3CoWZxr
pQyrOL2/BQ1SDyLsf9YZSFvMANjo/+hgPBoMksGtAyqubnCXFfcGjvVf7AgbSq/3
lD7bTNm1c+My/DrcBcedQnnJIi8CgYEA+nhBRoPLZfbg3Zt25t0p8Ff8PoAFLSqn
rPHt+F+VGdOiwC3KWZd0Yo4Gf+a0FpaWUxkvoxBniDXhkSE3a5pgrtOw1f2EJ0pU
CxiAdtT5ZwLriqCM8DpwpcJ/fXJFLt9tL4LJ3sDFRZs9tKciI80vGPLfOFSDy/mV
OWO8PrMyUp8CgYAcvTlayH1PcLhza9/aY0AAdAQeU20+N7MUZOnP+gUxvXNJa+07
8EfFDtaY55mUVipSxKiiQTvF9FkRqlInSw0QlwqlRCYn+YgAVDTCkA4vv8zWM+W5
6U/7qdKlMW1TzzTT0IaTlNBh7Oz48kKjt9zRTveKwcn2nJx2IBZZbkSj+QKBgFD7
7O8l0fAoANDmYW2H+PVzHWX/8qyF7C0pFC6IiScOnMLSi2ioZcMv9L4KFBRxoC1C
KXrp5O/PrB1GxiqOgdBFNhoanE4v5DiqNW82sWUzNoFeI/PQkXenCZ3AAsqDB0Sj
Xy4c2iwFY9AzcgBtaVsBvFb0TKD5E9y4eLc1LYI1AoGAbusWCkSQCOaN0c8KW81M
W6xV1rPJOHYtOedTWXf7N/5SMl+ioEqpo6eP5ZswOzqLqgCJ+Kpl5DmvA4Ht8qel
NTHa9XqoGvyPbaauojI0TIGa+mHYhY7hD2U/Z3xuegfDhm93CdgTwwWqJsezPXXV
GrrNOufvPsvmCRO9m4ESRrk=
-----END PRIVATE KEY-----"#;

        let claims = IdTokenClaims {
            preferred_username: Some("guest".to_string()),
            exp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs()
                + 3600,
            ..Default::default()
        };

        let header = Header::new(jsonwebtoken::Algorithm::RS256);

        let token = encode(
            &header,
            &claims,
            &EncodingKey::from_rsa_pem(mock_private_key.as_bytes()).unwrap(),
        )
        .unwrap();

        serde_json::json!({
            "access_token": "token",
            "expires_in": 3600,
            "refresh_token": "mock_refresh_token",
            "refresh_expires_in": 3600,
            "token_type": "Bearer",
            "not_before_policy": 0,
            "session_state": "mock_session_state",
            "scope": "openid profile email",
            "not-before-policy": 0,
            "id_token": token,
        })
        .to_string()
    }

    struct MockServer {
        _server: ServerGuard,
        url: String,
    }
    impl MockServer {
        async fn new() -> Self {
            let mut server = Server::new_async().await;
            let url = server.url().to_string();

            let jswk = Jwk {
                kty: "RSA".to_string(),
                alg: Algorithm ::RS256,
                kid: "mock_key_id".to_string(),
                use_: "sig".to_string(),
                e: "AQAB".to_string(), // public exponent
                n: "y2YCQSwO7b8yapX4gZ5UMqr_lQ_XzdGwyF1pF_ihbrZTKLNlGd42Ui2-vEA-EsNFLr7PlabsW6O54pXXbQC68HCRfS76hTI9SarXzpnEKLiW61EcQXenNAeRFV6ttKNrnWdBblh5lA62bwr9G0xRNS4GhIrI196smXp4W4IIW14nazUd4AF-xnUuHMuyETDe2pWVhqVyWMsgf-kHTs7M4WeB9XkTWHWGHYCU58vKATN0__wsBYmkeu5arPbXY-sXuQX4KEWuZB_VrUQN9ftn1CPX_hbS82Kce_TrG8mICZcx_SnKOpj2b7EZ7N32-DPfkh7FKBTEIbycey7dmw1JMQ".to_string(), // mock public key modulus
            };

            let cert_response = JwkResponse { keys: vec![jswk] };
            let body = serde_json::to_string(&cert_response).unwrap();

            // mock keycloak JWKS endpoint
            server
                .mock("GET", "/realms/opsml/protocol/openid-connect/certs")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(body.clone())
                .create();

            // mock okta JWKS endpoint
            server
                .mock("GET", "/oauth2/v1/keys")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(body.clone())
                .create();

            // mock default jwks endpoint
            server
                .mock("GET", "/oauth/keys")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(body.clone())
                .create();

            // mock keycloak token endpoint
            server
                .mock("POST", "/realms/opsml/protocol/openid-connect/token")
                .match_header("Content-Type", "application/x-www-form-urlencoded")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(create_mock_token_response())
                .create();

            server
                .mock("POST", "/oauth/token")
                .match_header("Content-Type", "application/x-www-form-urlencoded")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(create_mock_token_response())
                .create();

            // mock okta token endpoint
            let encoded_credentials = BASE64_STANDARD.encode("opsml-client:client-secret");
            let auth_header = format!("Basic {encoded_credentials}");

            server
                .mock("POST", "/oauth2/v1/token")
                .match_header("Authorization", &*auth_header)
                // match the content type
                .match_header("Content-Type", "application/x-www-form-urlencoded")
                // match accept
                .match_header("Accept", "application/json")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(create_mock_token_response())
                .create();

            MockServer {
                _server: server,
                url,
            }
        }
    }

    #[tokio::test]
    async fn test_sso_provider_keycloak() {
        let mock_server = MockServer::new().await;

        // Set the SSO provider environment variable
        unsafe {
            std::env::set_var("SSO_PROVIDER", "keycloak");
            std::env::set_var("OPSML_CLIENT_ID", "opsml-client");
            std::env::set_var("OPSML_CLIENT_SECRET", "client-secret");
            std::env::set_var("OPSML_REDIRECT_URI", "http://localhost:8080/callback");
            std::env::set_var("OPSML_AUTH_DOMAIN", &mock_server.url);
            std::env::set_var("OPSML_AUTH_REALM", "opsml");
        }

        // Initialize the SSO provider
        let sso_provider = SsoProvider::from_env().await.unwrap();

        // Test the public key endpoint
        let user_info = sso_provider
            .authenticate_resource_password("guest", "guest")
            .await
            .expect("Failed to authenticate with Keycloak");

        assert_eq!(user_info.username, "guest");

        let user_info = sso_provider
            .authenticate_auth_flow("mock_code", "mock_code_verifier")
            .await
            .expect("Failed to authenticate with Keycloak using callback code");

        assert_eq!(user_info.username, "guest");
    }

    #[tokio::test]
    async fn test_sso_provider_okta() {
        let mock_server = MockServer::new().await;

        // Set the SSO provider environment variable
        unsafe {
            std::env::set_var("SSO_PROVIDER", "okta");
            std::env::set_var("OPSML_CLIENT_ID", "opsml-client");
            std::env::set_var("OPSML_CLIENT_SECRET", "client-secret");
            std::env::set_var("OPSML_REDIRECT_URI", "https://localhost:8080/callback");
            std::env::set_var("OPSML_AUTH_DOMAIN", &mock_server.url);
        }

        // Initialize the SSO provider
        let sso_provider = SsoProvider::from_env().await.unwrap();

        let user_info = sso_provider
            .authenticate_resource_password("guest", "guest")
            .await
            .expect("Failed to authenticate with Okta");

        assert_eq!(user_info.username, "guest");

        let user_info = sso_provider
            .authenticate_auth_flow("mock_code", "mock_code_verifier")
            .await
            .expect("Failed to authenticate with Keycloak using callback code");

        assert_eq!(user_info.username, "guest");
    }

    #[tokio::test]
    async fn test_sso_provider_default() {
        let mock_server = MockServer::new().await;

        // Set the SSO provider environment variable
        unsafe {
            std::env::set_var("SSO_PROVIDER", "default");
            std::env::set_var("OPSML_CLIENT_ID", "opsml-client");
            std::env::set_var("OPSML_CLIENT_SECRET", "client-secret");
            std::env::set_var("OPSML_REDIRECT_URI", "https://localhost:8080/callback");
            std::env::set_var("OPSML_AUTH_DOMAIN", &mock_server.url);

            std::env::set_var("OPSML_TOKEN_ENDPOINT", "oauth/token");
            std::env::set_var("OPSML_CERT_ENDPOINT", "oauth/keys");
            std::env::set_var("OPSML_AUTHORIZATION_ENDPOINT", "oauth/authorize");
        }

        // Initialize the SSO provider
        let sso_provider = SsoProvider::from_env().await.unwrap();

        // Test the public key endpoint
        let user_info = sso_provider
            .authenticate_resource_password("guest", "guest")
            .await
            .expect("Failed to authenticate with default");

        assert_eq!(user_info.username, "guest");

        let user_info = sso_provider
            .authenticate_auth_flow("mock_code", "mock_code_verifier")
            .await
            .expect("Failed to authenticate with default using callback code");

        assert_eq!(user_info.username, "guest");
    }
}
