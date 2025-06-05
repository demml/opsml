use crate::sso::error::SsoError;
use crate::sso::providers::keycloak::KeycloakProvider;
use crate::sso::types::UserInfo;
use reqwest::Client;

pub enum SsoProvider {
    Keycloak(KeycloakProvider),
}

impl SsoProvider {
    pub fn as_str(&self) -> &str {
        match self {
            SsoProvider::Keycloak(_) => "keycloak",
        }
    }

    pub async fn from_env() -> Result<Self, SsoError> {
        let client = Client::new();
        match std::env::var("SSO_PROVIDER")
            .map_err(|_| SsoError::EnvVarNotSet)?
            .to_lowercase()
            .as_str()
        {
            "keycloak" => Ok(SsoProvider::Keycloak(KeycloakProvider::new(client).await?)),
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

    pub async fn authenticate(&self, username: &str, password: &str) -> Result<UserInfo, SsoError> {
        match self {
            SsoProvider::Keycloak(provider) => provider.authenticate(username, password).await,
        }
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    use crate::sso::providers::keycloak::*;
    use jsonwebtoken::encode;
    use jsonwebtoken::EncodingKey;
    use jsonwebtoken::Header;
    use mockito::{Server, ServerGuard};
    use std::time::SystemTime;
    use std::time::UNIX_EPOCH;

    const PUBLIC_KEY: &str = r#"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAm2ATGZ7dHUqqRNP5JQ73
    2Vao7XNEU1XyldoD2P/2dk2pnDKVYkfN+KW5p8c0l9ITFRt77b99i9EGa0ybuV65
    wpMZKVahj8u0rLZEMWqBDQ/1E4ZeeVQSV0SlWzH5uTEkP5DgNB1ZnI31Wrro+X7m
    uhRzy45hqoE+43vnvhRM4Xwgo7Xgf7iwvmVv4iQVxZg5BnXVkeKP1Z4rlnAAa3EJ
    c9OkbW+LznNPyHVQxF9BlUg824Z0momQfLeNoZbuFU+wXIE5F1QMWpNesR/+iniO
    KTataEwMkwyB6YST3RCiXLij8XaqFMO/E8r1jBs4RzS1bk1KtRVjIKIoqjY8kwkQ
    0wIDAQAB"#;

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
        let mock_private_key = r#"-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAm2ATGZ7dHUqqRNP5JQ732Vao7XNEU1XyldoD2P/2dk2pnDKV
YkfN+KW5p8c0l9ITFRt77b99i9EGa0ybuV65wpMZKVahj8u0rLZEMWqBDQ/1E4Ze
eVQSV0SlWzH5uTEkP5DgNB1ZnI31Wrro+X7muhRzy45hqoE+43vnvhRM4Xwgo7Xg
f7iwvmVv4iQVxZg5BnXVkeKP1Z4rlnAAa3EJc9OkbW+LznNPyHVQxF9BlUg824Z0
momQfLeNoZbuFU+wXIE5F1QMWpNesR/+iniOKTataEwMkwyB6YST3RCiXLij8Xaq
FMO/E8r1jBs4RzS1bk1KtRVjIKIoqjY8kwkQ0wIDAQABAoIBACYzY97LuU+HWP+d
IkdjO7q63MOssGLQ4djIBmQm4oDJrWbS5PmJ7/EvRcsjZiHhq4FoBXs5tnNWy/47
kpnr2T4mjmwkeYpyKhTAp1mC9wGwJ7BKPBYWfn/oR8N5MQ3AMEpUo1sM0Eh2epl5
FOiqs62Sc7nbYtXZ+w1RHHQWZ6SUTtRlLIT2FsunVUEPhuajOfOdNKqIWD9cNplh
YmW2tF1VRSChjytDhV3/eS3mFurhRJqNyVHhS7TvmnUapAUp39pUubHAJQ5YqDBX
ZvUQcvMyH/blAs13zhJIoKac346RXBqcLqERg0GSYYvnfLGqRPiUm8sJOKEwRPUO
AVLuj6kCgYEA1xchIhsEuUSgGMP707ZKGpQ91Ko/VCD3yrjROu18ryhdjOytd8hN
OC0d/aLFOHW6ZykApcavpzOKkNrhiGi2OmvjCRm0jgI0QQXAqAmgVGcNQ/j2H0Hj
K+Sw5JIHcNIkCNl5GysSpNRDxAJ+xfBvGynozoZv4/s4qsAl7ebs2j8CgYEAuO1i
oo5JniB2qlkCVaGEu1c0/wzUrfWfqJLiYKaP5JjvnDcbd1NWLK6BG1fi0g6A5Pfm
ArDK/8uP2dPk1g07DiA1ZCSM+LB1QUYkU232pogrjd2ElBFUnyYh6tIjKth2ueJ9
4VGgozs6cA0tacn1foN5Rrm2S52Ss9UTlw7e3G0CgYEAx62gQ9JDY19zJSqkWZos
V1pxwEFAw3BLufYzv3oDu3REzPRX4hCgp1szMWjvoIeiwexNvpiiLx3pMKsSnxle
uwO3ZJZpiUBAlHCrtxQgtNpqdUTl8ISxSeln0vpCUBm1/EUwaellyIGKW6hZWpbn
/pa8myYxL7vkkpgJXj94eO8CgYA4rVjLpXxeoGh+MSWMBSLfIA04FkCgyGUUj2Ae
ay4yy8S0Rhd+7OW+cAVV0gvMgXFzu56dOH4fA86k3lKGYCu3WpvCg4lJNxvY05yS
jWNJCvb+VeQqVV1wIYnHpHvux8Url4UpJ5FqNd7lNMS0ZZd+HOFwkb6TUkoCH84P
QBmByQKBgB7G8k+LbWMU34foEWwefTI8nuFYdiuSNakFhHcJ9T+zFlpVS7bMQMfK
TcuAZ2BC53r9hNlfkGh+F5si2XB5AYJhai2tTdYtWjdJhAgLzeorZTa685Ny6Vmp
R3rJENWcXj473lMzYW0/DBDd0OrfFPd8s7ef6umP5Jj7jS4RuXZn
-----END RSA PRIVATE KEY-----
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
            "scope": "openid profile email"
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
            .authenticate("guest", "guest")
            .await
            .expect("Failed to authenticate with Keycloak");

        assert_eq!(user_info.username, "guest");
    }
}
