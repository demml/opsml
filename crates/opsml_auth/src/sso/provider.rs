use crate::sso::error::SsoError;
use crate::sso::providers::keycloak::KeycloakProvider;
use crate::sso::providers::okta::OktaProvider;
use crate::sso::providers::traits::SsoProviderExt;
use crate::sso::types::UserInfo;
use reqwest::Client;

pub enum SsoProvider {
    Keycloak(KeycloakProvider),
    Okta(OktaProvider),
}

impl SsoProvider {
    pub fn as_str(&self) -> &str {
        match self {
            SsoProvider::Keycloak(_) => "keycloak",
            SsoProvider::Okta(_) => "okta",
        }
    }

    pub async fn from_str(provider: &str) -> Result<Self, SsoError> {
        let client = Client::new();
        match provider.to_lowercase().as_str() {
            "keycloak" => Ok(SsoProvider::Keycloak(KeycloakProvider::new(client).await?)),
            "okta" => Ok(SsoProvider::Okta(OktaProvider::new(client).await?)),
            _ => Err(SsoError::InvalidProvider(provider.to_string())),
        }
    }

    pub async fn from_env() -> Result<Self, SsoError> {
        let client = Client::new();
        match std::env::var("SSO_PROVIDER")
            .map_err(|_| SsoError::EnvVarNotSet("SSO_PROVIDER".to_string()))?
            .to_lowercase()
            .as_str()
        {
            "keycloak" => Ok(SsoProvider::Keycloak(KeycloakProvider::new(client).await?)),
            "okta" => Ok(SsoProvider::Okta(OktaProvider::new(client).await?)),
            _ => Err(SsoError::InvalidProvider(
                std::env::var("SSO_PROVIDER").unwrap_or_default(),
            )),
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
        }
    }

    pub async fn authenticate_auth_flow(&self, code: &str) -> Result<UserInfo, SsoError> {
        match self {
            SsoProvider::Keycloak(provider) => provider.authenticate_auth_flow(code).await,
            SsoProvider::Okta(provider) => provider.authenticate_auth_flow(code).await,
        }
    }

    pub fn authorization_url(&self, state: &str) -> String {
        match self {
            SsoProvider::Keycloak(provider) => provider.get_authorization_url(state),
            SsoProvider::Okta(provider) => provider.get_authorization_url(state),
        }
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    use jsonwebtoken::encode;
    use jsonwebtoken::EncodingKey;
    use jsonwebtoken::Header;
    use mockito::{Server, ServerGuard};

    use std::time::SystemTime;
    use std::time::UNIX_EPOCH;

    const PUBLIC_KEY: &str = r#"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAy2YCQSwO7b8yapX4gZ5U
    Mqr/lQ/XzdGwyF1pF/ihbrZTKLNlGd42Ui2+vEA+EsNFLr7PlabsW6O54pXXbQC6
    8HCRfS76hTI9SarXzpnEKLiW61EcQXenNAeRFV6ttKNrnWdBblh5lA62bwr9G0xR
    NS4GhIrI196smXp4W4IIW14nazUd4AF+xnUuHMuyETDe2pWVhqVyWMsgf+kHTs7M
    4WeB9XkTWHWGHYCU58vKATN0//wsBYmkeu5arPbXY+sXuQX4KEWuZB/VrUQN9ftn
    1CPX/hbS82Kce/TrG8mICZcx/SnKOpj2b7EZ7N32+DPfkh7FKBTEIbycey7dmw1J
    MQIDAQAB"#;

    impl Default for KeycloakClaims {
        fn default() -> Self {
            let expiration = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs()
                + 3600; // 1 hour

            Self {
                sub: String::new(),
                scope: String::new(),
                name: "guest".into(),
                preferred_username: "guest".into(),
                email: String::new(),
                exp: expiration as usize,
            }
        }
    }

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
-----END PRIVATE KEY-----

        "#;

        let claims = KeycloakClaims::default();
        let header = Header::new(jsonwebtoken::Algorithm::RS256);

        let token = encode(
            &header,
            &claims,
            &EncodingKey::from_rsa_pem(mock_private_key.as_bytes()).unwrap(),
        )
        .unwrap();

        serde_json::json!({
            "access_token": token,
            "expires_in": 3600,
            "refresh_token": "mock_refresh_token",
            "refresh_expires_in": 3600,
            "token_type": "Bearer",
            "not_before_policy": 0,
            "session_state": "mock_session_state",
            "scope": "openid profile email",
            "not-before-policy": 0,
            "id_token": "id_token"
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

            let public_key_response = KeycloakPublicKeyResponse {
                realm: "opsml".to_string(),
                // this is a mock public key
                public_key: PUBLIC_KEY.to_string(),
            };

            // mock public key endpoint
            server
                .mock("GET", "/realms/opsml")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(serde_json::to_string(&public_key_response).unwrap())
                .create();

            // mock token endpoint
            server
                .mock("POST", "/realms/opsml/protocol/openid-connect/token")
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
        std::env::set_var("SSO_PROVIDER", "keycloak");
        std::env::set_var("KEYCLOAK_CLIENT_ID", "opsml-client");
        std::env::set_var("KEYCLOAK_CLIENT_SECRET", "opsml-client-secret");
        std::env::set_var("KEYCLOAK_REDIRECT_URI", "http://localhost:8080/callback");
        std::env::set_var("KEYCLOAK_AUTH_URL", &mock_server.url);
        std::env::set_var("KEYCLOAK_AUTH_REALM", "opsml");

        // Initialize the SSO provider
        let sso_provider = SsoProvider::from_env().await.unwrap();

        // Test the public key endpoint
        let user_info = sso_provider
            .authenticate_resource_password("guest", "guest")
            .await
            .expect("Failed to authenticate with Keycloak");

        assert_eq!(user_info.username, "guest");

        let user_info = sso_provider
            .authenticate_auth_flow("mock_code")
            .await
            .expect("Failed to authenticate with Keycloak using callback code");

        assert_eq!(user_info.username, "guest");
    }

    #[tokio::test]
    async fn test_sso_provider_okta() {
        let mock_server = MockServer::new().await;

        // Set the SSO provider environment variable
        std::env::set_var("SSO_PROVIDER", "okta");
        std::env::set_var("OKTA_CLIENT_ID", "client");
        std::env::set_var("OKTA_CLIENT_SECRET", "secret");
        std::env::set_var("OKTA_REDIRECT_URI", "http://localhost:8080/callback");
        std::env::set_var("OKTA_DOMAIN", &mock_server.url);

        // Initialize the SSO provider
        let sso_provider = SsoProvider::from_env().await.unwrap();

        let user_info = sso_provider
            .authenticate_resource_password("guest", "guest")
            .await
            .expect("Failed to authenticate with Okta");
    }
}
