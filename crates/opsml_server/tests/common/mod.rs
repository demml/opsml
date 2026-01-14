use axum::extract::connect_info::MockConnectInfo;
use axum::response::Response;
use axum::Router;
use axum::{
    body::Body,
    http::{header, Request, StatusCode},
};
use base64::prelude::*;
use http_body_util::BodyExt;
use jsonwebtoken::encode;
use jsonwebtoken::EncodingKey;
use jsonwebtoken::Header;
use mockito;
use opsml_auth::sso::providers::types::IdTokenClaims;
use opsml_auth::sso::providers::types::*;
use opsml_crypt::encrypt_file;
use opsml_semver::VersionType;
use opsml_server::core::app::create_app;
use opsml_settings::config::DatabaseSettings;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_types::contracts::*;
use opsml_types::*;
use scouter_client::{
    BinnedMetrics, BinnedPsiFeatureMetrics, GenAIEvalRecordPaginationResponse,
    GenAIEvalTaskResponse, GenAIEvalTaskResult, GenAIEvalWorkflowPaginationResponse,
    SpcDriftFeatures,
};
use std::time::SystemTime;
use std::time::UNIX_EPOCH;
use std::{env, net::SocketAddr, vec};
use tower::ServiceExt;

fn cleanup() {
    // cleanup delete opsml.db and opsml_registries folder from the current directory
    let current_dir = std::env::current_dir().unwrap();
    let db_path = current_dir.join("opsml.db");
    let registry_path = current_dir.join("opsml_registries");

    if db_path.exists() {
        std::fs::remove_file(db_path).unwrap();
    }

    if registry_path.exists() {
        std::fs::remove_dir_all(registry_path).unwrap();
    }
}

fn get_connection_uri() -> String {
    let mut current_dir = env::current_dir().expect("Failed to get current directory");
    current_dir.push("opsml.db");

    format!(
        "sqlite://{}",
        current_dir
            .to_str()
            .expect("Failed to convert path to string")
    )
}

async fn setup() {
    let config = DatabaseSettings {
        connection_uri: get_connection_uri(),
        max_connections: 1,
        sql_type: SqlType::Sqlite,
    };

    let client = SqlClientEnum::new(&config).await.unwrap();

    // Run the SQL script to populate the database
    let script = std::fs::read_to_string("tests/fixtures/populate_db.sql").unwrap();

    client.query(&script).await;
}

pub struct ScouterServer {
    pub url: String,
    pub server: mockito::ServerGuard,
}

impl ScouterServer {
    fn create_genai_eval_task_response() -> String {
        let task = GenAIEvalTaskResult::default();
        let response = GenAIEvalTaskResponse { tasks: vec![task] };

        serde_json::to_string(&response).unwrap()
    }
    pub async fn new() -> Self {
        let mut server = mockito::Server::new_async().await;

        // scouter healthcheck
        server
            .mock("GET", "/scouter/healthcheck")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "Alive"}"#)
            .create_async()
            .await;

        // insert user mock
        server
            .mock("POST", "/scouter/user")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "created_user"}"#)
            .create_async()
            .await;

        // update user mock
        server
            .mock("PUT", "/scouter/user")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "updated_user"}"#)
            .create_async()
            .await;

        // delete user mock
        server
            .mock("DELETE", "/scouter/user")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "deleted_user"}"#)
            .create_async()
            .await;

        // insert profile mock
        server
            .mock("POST", "/scouter/profile")
            .match_header("content-type", mockito::Matcher::Any)
            .match_header("authorization", mockito::Matcher::Any)
            .match_body(mockito::Matcher::Any)
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "Profile created"}"#)
            .create_async()
            .await;

        server
            .mock("PUT", "/scouter/profile")
            .match_header("content-type", mockito::Matcher::Any)
            .match_header("authorization", mockito::Matcher::Any)
            .match_body(mockito::Matcher::Any)
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "Profile updated"}"#)
            .create_async()
            .await;

        server
            .mock("PUT", "/scouter/profile/status")
            .match_header("content-type", mockito::Matcher::Any)
            .match_header("authorization", mockito::Matcher::Any)
            .match_body(mockito::Matcher::Any)
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "Profile updated"}"#)
            .create_async()
            .await;

        // get spc drift features mock
        let spc_features = SpcDriftFeatures::default();
        let spc_features_json = serde_json::to_string(&spc_features).unwrap();
        server
            .mock("GET", "/scouter/drift/spc")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(spc_features_json)
            .create_async()
            .await;

        // get binned psi feature metrics mock
        let binned_psi_features = BinnedPsiFeatureMetrics::default();
        let binned_psi_features_json = serde_json::to_string(&binned_psi_features).unwrap();
        server
            .mock("GET", "/scouter/drift/psi")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(binned_psi_features_json)
            .create_async()
            .await;

        // get binned custom metrics mock
        let binned_metrics = BinnedMetrics::default();
        let binned_custom_metrics_json = serde_json::to_string(&binned_metrics).unwrap();
        server
            .mock("GET", "/scouter/drift/custom")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(binned_custom_metrics_json)
            .create_async()
            .await;

        let binned_metrics_json = serde_json::to_string(&binned_metrics).unwrap();
        server
            .mock("GET", "/scouter/drift/genai/task")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(binned_metrics_json)
            .create_async()
            .await;

        let binned_metrics_json = serde_json::to_string(&binned_metrics).unwrap();
        server
            .mock("GET", "/scouter/drift/genai/workflow")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(binned_metrics_json)
            .create_async()
            .await;

        let task_records = Self::create_genai_eval_task_response();
        server
            .mock("GET", "/scouter/genai/task")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(task_records)
            .create_async()
            .await;

        let workflow_page =
            serde_json::to_string(&GenAIEvalWorkflowPaginationResponse::default()).unwrap();
        server
            .mock("POST", "/scouter/genai/page/workflow")
            .match_header("content-type", mockito::Matcher::Any)
            .match_header("authorization", mockito::Matcher::Any)
            .match_body(mockito::Matcher::Any)
            .with_status(200)
            .with_body(workflow_page)
            .create_async()
            .await;

        let record_page =
            serde_json::to_string(&GenAIEvalRecordPaginationResponse::default()).unwrap();
        server
            .mock("POST", "/scouter/genai/page/record")
            .match_header("content-type", mockito::Matcher::Any)
            .match_header("authorization", mockito::Matcher::Any)
            .match_body(mockito::Matcher::Any)
            .with_status(200)
            .with_body(record_page)
            .create_async()
            .await;

        Self {
            url: server.url(),
            server,
        }
    }
}

pub struct SsoMocks {
    pub keycloak_certs_mock: mockito::Mock,
    pub okta_certs_mock: mockito::Mock,
    pub default_certs_mock: mockito::Mock,
    pub keycloak_token_mock: mockito::Mock,
    pub okta_token_mock: mockito::Mock,
    pub default_token_mock: mockito::Mock,
}

pub struct MockSsoServer {
    _server: mockito::ServerGuard,
    pub url: String,
    pub sso_mocks: SsoMocks,
}

impl MockSsoServer {
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
            preferred_username: Some("sso_guest".to_string()),
            exp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs()
                + 3600,
            ..Default::default()
        };

        let mut header = Header::new(jsonwebtoken::Algorithm::RS256);
        header.kid = Some("mock_key_id".to_string());

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

    async fn new() -> Self {
        let mut server = mockito::Server::new_async().await;
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
        let keycloak_certs_mock = server
            .mock("GET", "/realms/opsml/protocol/openid-connect/certs")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(body.clone())
            .create();

        // mock okta JWKS endpoint
        let okta_certs_mock = server
            .mock("GET", "/oauth2/v1/keys")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(body.clone())
            .create();

        // mock default jwks endpoint
        let default_certs_mock = server
            .mock("GET", "/oauth/keys")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(body.clone())
            .create();

        // mock keycloak token endpoint
        let keycloak_token_mock = server
            .mock("POST", "/realms/opsml/protocol/openid-connect/token")
            .match_header("Content-Type", "application/x-www-form-urlencoded")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(Self::create_mock_token_response())
            .create();

        // mock default token endpoint
        let default_token_mock = server
            .mock("POST", "/oauth/token")
            .match_header("Content-Type", "application/x-www-form-urlencoded")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(Self::create_mock_token_response())
            .create();

        // mock okta token endpoint
        let credentials = format!("{}:{}", "opsml-client", "client-secret");
        let encoded_credentials = BASE64_STANDARD.encode(credentials);
        let auth_header = format!("Basic {encoded_credentials}");

        let okta_token_mock = server
            .mock("POST", "/oauth2/v1/token")
            .match_header("Authorization", &*auth_header)
            // match the content type
            .match_header("Content-Type", "application/x-www-form-urlencoded")
            // match accept
            .match_header("Accept", "application/json")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(Self::create_mock_token_response())
            .create();

        Self {
            _server: server,
            url,
            sso_mocks: SsoMocks {
                keycloak_certs_mock,
                okta_certs_mock,
                default_certs_mock,
                keycloak_token_mock,
                okta_token_mock,
                default_token_mock,
            },
        }
    }

    pub fn verify_keycloak_certs_called(&self) -> bool {
        self.sso_mocks.keycloak_certs_mock.matched()
    }

    pub fn verify_keycloak_token_called(&self) -> bool {
        self.sso_mocks.keycloak_token_mock.matched()
    }

    pub fn verify_okta_certs_called(&self) -> bool {
        self.sso_mocks.okta_certs_mock.matched()
    }

    pub fn verify_okta_token_called(&self) -> bool {
        self.sso_mocks.okta_token_mock.matched()
    }

    pub fn verify_default_certs_called(&self) -> bool {
        self.sso_mocks.default_certs_mock.matched()
    }
    pub fn verify_default_token_called(&self) -> bool {
        self.sso_mocks.default_token_mock.matched()
    }
}

fn set_common_env_vars(scouter_url: &str) {
    unsafe {
        env::set_var("SCOUTER_SERVER_URI", scouter_url);
        env::set_var("RUST_LOG", "debug");
        env::set_var("LOG_LEVEL", "debug");
        env::set_var("LOG_JSON", "false");
        env::set_var("OPSML_AUTH", "true");
    }
}

/// Set up the SSO provider and return the mock server
async fn setup_sso_provider(provider: &str) -> Option<MockSsoServer> {
    // Create initial mock server and set common SSO variables
    let mock_sso_server = MockSsoServer::new().await;

    unsafe {
        std::env::set_var("OPSML_CLIENT_ID", "opsml-client");
        std::env::set_var("OPSML_CLIENT_SECRET", "client-secret");
        std::env::set_var("OPSML_REDIRECT_URI", "http://localhost:8080/callback");
        std::env::set_var("OPSML_AUTH_DOMAIN", &mock_sso_server.url);
        std::env::set_var("OPSML_USE_SSO", "true");

        // default env vars for sso (these are only use for DefaultSsoSettings)
        std::env::set_var("OPSML_TOKEN_ENDPOINT", "oauth/token");
        std::env::set_var("OPSML_CERT_ENDPOINT", "oauth/keys");
        std::env::set_var("OPSML_AUTHORIZATION_ENDPOINT", "oauth/authorize");
    }

    println!("Setting up SSO provider: {provider}");

    match provider {
        "keycloak" => {
            unsafe {
                std::env::set_var("SSO_PROVIDER", "keycloak");
                std::env::set_var("OPSML_AUTH_REALM", "opsml");
            }
            Some(mock_sso_server)
        }
        "okta" => {
            unsafe {
                std::env::set_var("SSO_PROVIDER", "okta");
            }
            Some(mock_sso_server)
        }
        _ => {
            unsafe {
                std::env::set_var("SSO_PROVIDER", "default");
            }
            Some(mock_sso_server)
        }
    }
}

pub struct TestHelper {
    app: Router,
    token: JwtToken,
    pub name: String,
    pub space: String,
    pub version: String,
    pub key: ArtifactKey,
    pub server: ScouterServer,
    pub sso_server: Option<MockSsoServer>,
}

impl TestHelper {
    pub async fn new(sso_provider: Option<String>) -> Self {
        // Set up the mock Scouter server
        let scouter_server = ScouterServer::new().await;

        // Set common environment variables
        set_common_env_vars(&scouter_server.url);

        // Set up SSO if a provider was specified
        let mock_sso_server = match sso_provider {
            Some(provider) => setup_sso_provider(&provider).await,
            None => None,
        };

        // Clean up any existing data
        cleanup();

        // Create and configure the application
        let app = create_app().await.unwrap();
        let app = app.layer(MockConnectInfo(SocketAddr::from(([0, 0, 0, 0], 1337))));

        // Set up the database
        setup().await;

        // Retrieve the authentication token
        let token = TestHelper::login(&app).await;

        // Create a new test helper
        Self {
            app,
            token,
            name: "name".to_string(),
            space: "space".to_string(),
            version: "1.0.0".to_string(),
            key: ArtifactKey {
                uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
                space: "space".to_string(),
                registry_type: RegistryType::Data,
                encrypted_key: vec![],
                storage_key: "".to_string(),
            },
            server: scouter_server,
            sso_server: mock_sso_server,
        }
    }

    pub async fn login(app: &Router) -> JwtToken {
        let mut builder = Request::builder()
            .uri("/opsml/api/auth/login")
            .header("Username", "admin")
            .header("Password", "admin");

        // if sso provider is set, add Use-SSO header
        let use_sso = env::var("OPSML_USE_SSO").unwrap_or_else(|_| "false".to_string());
        if use_sso == "true" {
            builder = builder.header("Use-SSO", "true");
        }

        let response = app
            .clone()
            .oneshot(builder.body(Body::empty()).unwrap())
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let token: JwtToken = serde_json::from_slice(&body).unwrap();

        token
    }

    pub fn with_auth_header(&self, mut request: Request<Body>) -> Request<Body> {
        request.headers_mut().insert(
            header::AUTHORIZATION,
            format!("Bearer {}", self.token.token).parse().unwrap(),
        );
        request
            .headers_mut()
            .insert(header::USER_AGENT, "opsml-test".parse().unwrap());

        request
    }

    pub async fn send_oneshot(&self, request: Request<Body>) -> Response<Body> {
        self.app
            .clone()
            .oneshot(self.with_auth_header(request))
            .await
            .unwrap()
    }

    pub fn cleanup(&self) {
        cleanup();
    }

    pub fn create_files(&self) -> String {
        // get current directory
        let current_dir = std::env::current_dir().unwrap();

        let base_path = format!(
            "opsml_registries/opsml_model_registry/{}/{}/v{}",
            self.space, self.name, self.version
        );

        let joined_path = current_dir.join(base_path.clone());
        // create the directory
        std::fs::create_dir_all(&joined_path).unwrap();

        let json = r#"{"name":"name","space":"space","version":"1.0.0","uid":"550e8400-e29b-41d4-a716-446655440000","app_env":"dev","created_at":"2021-08-01T00:00:00Z"}"#;
        let path = &joined_path.join("file.json");
        std::fs::write(path, json).unwrap();

        let png = &joined_path.join("file.png");
        std::fs::write(png, "PNG").unwrap();

        let key_bytes = self.key.get_decrypt_key().unwrap();
        let _ = encrypt_file(path, &key_bytes);
        let _ = encrypt_file(png, &key_bytes);

        joined_path.to_str().unwrap().to_string()
    }

    pub async fn create_modelcard(&mut self) {
        // 1. First create a card so we have something to get
        let card_version_request = CardVersionRequest {
            name: self.name.clone(),
            space: self.space.clone(),
            version: Some(self.version.clone()),
            version_type: VersionType::Minor,
            pre_tag: None,
            build_tag: None,
        };

        // Create a test card with some data
        let card_request = CreateCardRequest {
            card: CardRecord::Model(ModelCardClientRecord {
                name: self.name.clone(),
                space: self.space.clone(),
                version: self.version.clone(),
                tags: vec!["test".to_string()],
                ..ModelCardClientRecord::default()
            }),
            registry_type: RegistryType::Model,
            version_request: card_version_request,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        // Create the card first
        let request = Request::builder()
            .uri("/opsml/api/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = self.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);
        //
        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        self.key = create_response.key.clone();
    }

    pub async fn create_datacard(&mut self) {
        // 1. First create a card so we have something to get
        let card_version_request = CardVersionRequest {
            name: self.name.clone(),
            space: self.space.clone(),
            version: Some(self.version.clone()),
            version_type: VersionType::Minor,
            pre_tag: None,
            build_tag: None,
        };

        // Create a test card with some data
        let card_request = CreateCardRequest {
            card: CardRecord::Data(DataCardClientRecord {
                name: self.name.clone(),
                space: self.space.clone(),
                version: self.version.clone(),
                tags: vec!["test".to_string()],
                ..DataCardClientRecord::default()
            }),
            registry_type: RegistryType::Data,
            version_request: card_version_request,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        // Create the card first
        let request = Request::builder()
            .uri("/opsml/api/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = self.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);
        //
        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        self.key = create_response.key.clone();
    }

    pub fn verify_keycloak_sso_called(&self) -> bool {
        if let Some(sso_server) = &self.sso_server {
            sso_server.verify_keycloak_certs_called() && sso_server.verify_keycloak_token_called()
        } else {
            false
        }
    }

    pub fn verify_okta_sso_called(&self) -> bool {
        if let Some(sso_server) = &self.sso_server {
            sso_server.verify_okta_certs_called() && sso_server.verify_okta_token_called()
        } else {
            false
        }
    }

    pub fn verify_default_sso_called(&self) -> bool {
        if let Some(sso_server) = &self.sso_server {
            sso_server.verify_default_certs_called() && sso_server.verify_default_token_called()
        } else {
            false
        }
    }
}
