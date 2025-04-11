use axum::response::Response;
use axum::Router;
use axum::{
    body::Body,
    http::{header, Request, StatusCode},
};
use http_body_util::BodyExt; // for `collect`
use mockito;
use opsml_crypt::encrypt_file;
use opsml_semver::VersionType;
use opsml_server::create_app;
use opsml_settings::config::DatabaseSettings;
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_types::contracts::*;
use opsml_types::*;
use scouter_client::{BinnedCustomMetrics, BinnedPsiFeatureMetrics, SpcDriftFeatures};

use axum::extract::connect_info::MockConnectInfo;
use std::{env, net::SocketAddr, vec};
use tower::ServiceExt; // for `call`, `oneshot`, and `ready`

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

pub struct TestHelper {
    app: Router,
    token: JwtToken,
    pub name: String,
    pub space: String,
    pub version: String,
    pub key: ArtifactKey,
    pub server: ScouterServer,
}

impl TestHelper {
    pub async fn new() -> Self {
        let scouter_server = ScouterServer::new().await;

        // set OPSML_AUTH to true
        env::set_var("SCOUTER_SERVER_URI", scouter_server.url.clone());
        env::set_var("RUST_LOG", "debug");
        env::set_var("LOG_LEVEL", "debug");
        env::set_var("LOG_JSON", "false");
        env::set_var("OPSML_AUTH", "true");

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
                registry_type: RegistryType::Data,
                encrypted_key: vec![],
                storage_key: "".to_string(),
            },
            server: scouter_server,
        }
    }

    pub async fn login(app: &Router) -> JwtToken {
        let response = app
            .clone()
            .oneshot(
                Request::builder()
                    .uri("/opsml/api/auth/login")
                    .header("Username", "admin")
                    .header("Password", "admin")
                    .body(Body::empty())
                    .unwrap(),
            )
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
            card: Card::Model(ModelCardClientRecord {
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
}
