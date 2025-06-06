use axum::extract::connect_info::MockConnectInfo;
use axum::response::Response;
use axum::Router;
use axum::{
    body::Body,
    http::{header, Request, StatusCode},
};
use http_body_util::BodyExt;
use jsonwebtoken::encode;
use jsonwebtoken::EncodingKey;
use jsonwebtoken::Header;
use mockito;
use opsml_auth::sso::providers::keycloak::*;
use opsml_crypt::encrypt_file;
use opsml_semver::VersionType;
use opsml_server::create_app;
use opsml_settings::config::DatabaseSettings;
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_types::contracts::*;
use opsml_types::*;
use scouter_client::{BinnedCustomMetrics, BinnedPsiFeatureMetrics, SpcDriftFeatures};
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
        let binned_custom_metrics = BinnedCustomMetrics::default();
        let binned_custom_metrics_json = serde_json::to_string(&binned_custom_metrics).unwrap();
        server
            .mock("GET", "/scouter/drift/custom")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(binned_custom_metrics_json)
            .create_async()
            .await;

        Self {
            url: server.url(),
            server,
        }
    }
}

pub struct MockSsoServer {
    _server: mockito::ServerGuard,
    pub url: String,
    public_key_mock: mockito::Mock, // Store mock references
    token_mock: mockito::Mock,
}

impl MockSsoServer {
    fn public_key() -> String {
        r#"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAm2ATGZ7dHUqqRNP5JQ73
    2Vao7XNEU1XyldoD2P/2dk2pnDKVYkfN+KW5p8c0l9ITFRt77b99i9EGa0ybuV65
    wpMZKVahj8u0rLZEMWqBDQ/1E4ZeeVQSV0SlWzH5uTEkP5DgNB1ZnI31Wrro+X7m
    uhRzy45hqoE+43vnvhRM4Xwgo7Xgf7iwvmVv4iQVxZg5BnXVkeKP1Z4rlnAAa3EJ
    c9OkbW+LznNPyHVQxF9BlUg824Z0momQfLeNoZbuFU+wXIE5F1QMWpNesR/+iniO
    KTataEwMkwyB6YST3RCiXLij8XaqFMO/E8r1jBs4RzS1bk1KtRVjIKIoqjY8kwkQ
    0wIDAQAB"#
            .to_string()
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

        let expiration = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
            + 3600; // 1 hour

        let claims = KeycloakClaims {
            sub: String::new(),
            scope: String::new(),
            name: "guest".into(),
            preferred_username: "guest".into(),
            email: String::new(),
            exp: expiration as usize,
        };

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

    async fn new() -> Self {
        let mut server = mockito::Server::new_async().await;
        let url = server.url().to_string();

        let public_key_response = KeycloakPublicKeyResponse {
            realm: "opsml".to_string(),
            public_key: Self::public_key(),
        };

        let public_key_mock = server
            .mock("GET", "/realms/opsml")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(serde_json::to_string(&public_key_response).unwrap())
            .create();

        let token_mock = server
            .mock("POST", "/realms/opsml/protocol/openid-connect/token")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(Self::create_mock_token_response())
            .create();

        Self {
            _server: server,
            url,
            public_key_mock,
            token_mock,
        }
    }

    pub fn verify_public_key_called(&self) -> bool {
        self.public_key_mock.matched()
    }

    pub fn verify_token_called(&self) -> bool {
        self.token_mock.matched()
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
        let scouter_server = ScouterServer::new().await;

        // set OPSML_AUTH to true
        env::set_var("SCOUTER_SERVER_URI", scouter_server.url.clone());
        env::set_var("RUST_LOG", "debug");
        env::set_var("LOG_LEVEL", "debug");
        env::set_var("LOG_JSON", "false");
        env::set_var("OPSML_AUTH", "true");

        let mock_sso_server = if let Some(provider) = sso_provider {
            if provider == "keycloak" {
                let mock_sso_server = MockSsoServer::new().await;
                // set env vars
                std::env::set_var("SSO_PROVIDER", "keycloak");
                std::env::set_var("KEYCLOAK_CLIENT_ID", "opsml-client");
                std::env::set_var("KEYCLOAK_CLIENT_SECRET", "opsml-client-secret");
                std::env::set_var("KEYCLOAK_REDIRECT_URI", "http://localhost:8080/callback");
                std::env::set_var("KEYCLOAK_AUTH_URL", &mock_sso_server.url);
                std::env::set_var("KEYCLOAK_AUTH_REALM", "opsml");
                std::env::set_var("OPSML_USE_SSO", "true");

                Some(mock_sso_server)
            } else {
                None
            }
        } else {
            None
        };

        cleanup();

        // create the app
        let app = create_app().await.unwrap();

        let app = app.layer(MockConnectInfo(SocketAddr::from(([0, 0, 0, 0], 1337))));

        // populate db
        setup().await;

        // retrieve the token
        let token = TestHelper::login(&app).await;
        let name = "name".to_string();
        let space = "space".to_string();
        let version = "1.0.0".to_string();

        Self {
            app,
            token,
            name,
            space,
            version,
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

    pub fn verify_sso_called(&self) -> bool {
        if let Some(sso_server) = &self.sso_server {
            sso_server.verify_public_key_called() && sso_server.verify_token_called()
        } else {
            false
        }
    }
}
