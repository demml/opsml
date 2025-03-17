use opsml_colors::Colorize;
use tracing::info;
mod core;

use crate::core::app::create_app;

#[tokio::main]
async fn main() {
    let logo = r#"
     ____             __  _____       _____                          
    / __ \____  _____/  |/  / /      / ___/___  ______   _____  _____
   / / / / __ \/ ___/ /|_/ / /       \__ \/ _ \/ ___/ | / / _ \/ ___/
  / /_/ / /_/ (__  ) /  / / /___    ___/ /  __/ /   | |/ /  __/ /    
  \____/ .___/____/_/  /_/_____/   /____/\___/_/    |___/\___/_/     
      /_/                                                            
               
    "#;

    println!("{}", Colorize::green(logo));

    // build our application with routes
    let app = create_app().await.unwrap();

    // get OPSML_SERVER_PORT from env
    let port = std::env::var("OPSML_SERVER_PORT").unwrap_or_else(|_| "3000".to_string());
    let addr = format!("0.0.0.0:{}", port);

    // run it
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();

    info!("listening on {}", listener.local_addr().unwrap());

    println!("🚀 Server Running 🚀");
    axum::serve(listener, app).await.unwrap();
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::cards::schema::{
        CreateReadeMe, QueryPageResponse, ReadeMe, RegistryStatsResponse,
    };
    use crate::core::user::schema::{
        CreateUserRequest, UpdateUserRequest, UserListResponse, UserResponse,
    };
    use axum::response::Response;
    use axum::Router;
    use axum::{
        body::Body,
        http::{header, Request, StatusCode},
    };
    use http_body_util::BodyExt; // for `collect`
    use mockito;
    use opsml_client::*;
    use opsml_crypt::encrypt_file;
    use opsml_semver::VersionType;
    use opsml_settings::config::DatabaseSettings;
    use opsml_sql::base::SqlClient;
    use opsml_sql::enums::client::SqlClientEnum;
    use opsml_types::*;
    use opsml_types::{cards::*, contracts::*};
    use tokio::time::Duration;

    use std::path::PathBuf;
    use std::{env, vec};
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

    // create json
    fn create_card_metadata(key: ArtifactKey) {
        let json = r#"{"name":"name","repository":"space","version":"1.0.0","uid":"550e8400-e29b-41d4-a716-446655440000","app_env":"dev","created_at":"2021-08-01T00:00:00Z"}"#;
        let path = format!(
            "opsml_registries/opsml_data_registry/{}/{}/v{}",
            "space", "name", "1.0.0"
        );
        std::fs::create_dir_all(path.clone()).unwrap();
        let lpath = PathBuf::from(path).join("Card.json");
        std::fs::write(&lpath, json).unwrap();

        let encryption_key = key.get_decrypt_key().unwrap();

        encrypt_file(&lpath, &encryption_key).unwrap();
    }

    async fn setup() {
        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqlClientEnum::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_db.sql").unwrap();

        client.query(&script).await;
    }

    pub struct ScouterServer {
        pub server: mockito::ServerGuard,
    }

    impl ScouterServer {
        pub fn new() -> Self {
            let mut server = mockito::Server::new();

            server
                .mock("POST", "/scouter/profile")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(r#"{"status": "success", "message": "Profile created"}"#)
                .create();

            server
                .mock("PUT", "/scouter/profile")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(r#"{"status": "success", "message": "Profile updated"}"#)
                .create();

            Self { server }
        }
    }

    pub struct TestHelper {
        app: Router,
        token: JwtToken,
        pub name: String,
        pub repository: String,
        pub version: String,
        key: ArtifactKey,
    }

    impl TestHelper {
        pub async fn new() -> Self {
            let scouter_server = ScouterServer::new();

            // set OPSML_AUTH to true
            env::set_var("RUST_LOG", "debug");
            env::set_var("LOG_LEVEL", "debug");
            env::set_var("LOG_JSON", "false");
            env::set_var("OPSML_AUTH", "true");
            env::set_var("SCOUTER_SERVER_URI", scouter_server.server.url());

            cleanup();

            // create the app
            let app = create_app().await.unwrap();

            // populate db
            setup().await;

            // retrieve the token
            let token = TestHelper::login(&app).await;
            let name = "name".to_string();
            let repository = "space".to_string();
            let version = "1.0.0".to_string();

            Self {
                app,
                token,
                name,
                repository,
                version,
                key: ArtifactKey {
                    uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
                    registry_type: RegistryType::Data,
                    encrypted_key: vec![],
                    storage_key: "".to_string(),
                },
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
                "opsml_registries/opsml_data_registry/{}/{}/v{}",
                self.repository, self.name, self.version
            );

            let joined_path = current_dir.join(base_path.clone());
            // create the directory
            std::fs::create_dir_all(&joined_path).unwrap();

            let json = r#"{"name":"name","repository":"space","version":"1.0.0","uid":"550e8400-e29b-41d4-a716-446655440000","app_env":"dev","created_at":"2021-08-01T00:00:00Z"}"#;
            let path = &joined_path.join("file.json");
            std::fs::write(&path, json).unwrap();

            let png = &joined_path.join("file.png");
            std::fs::write(&png, "PNG").unwrap();

            let key_bytes = self.key.get_decrypt_key().unwrap();
            let _ = encrypt_file(&path, &key_bytes);
            let _ = encrypt_file(&png, &key_bytes);

            joined_path.to_str().unwrap().to_string()
        }

        pub async fn create_card(&mut self) {
            // 1. First create a card so we have something to get
            let card_version_request = CardVersionRequest {
                name: self.name.clone(),
                repository: self.repository.clone(),
                version: Some(self.version.clone()),
                version_type: VersionType::Minor,
                pre_tag: None,
                build_tag: None,
            };

            // Create a test card with some data
            let card_request = CreateCardRequest {
                card: Card::Data(DataCardClientRecord {
                    name: self.name.clone(),
                    repository: self.repository.clone(),
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

            // sleep for 1 sec
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    }

    #[tokio::test]
    async fn test_opsml_server_login() {
        let helper = TestHelper::new().await;

        let request = Request::builder()
            .uri("/opsml/api/healthcheck")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_card_uid() {
        let helper = TestHelper::new().await;

        /////////////////////// Test check uid ///////////////////////

        // Test if a card UID exists - should be false
        let params = UidRequest {
            uid: "test_uid".to_string(),
            registry_type: RegistryType::Data,
        };

        let query_string = serde_qs::to_string(&params).unwrap();

        // check if a card UID exists (get request with UidRequest params)
        let request = Request::builder()
            .uri(format!("/opsml/api/card?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let uid_response: UidResponse = serde_json::from_slice(&body).unwrap();

        // assert false
        assert!(!uid_response.exists);

        // Test if a card UID exists - should be True
        let params = UidRequest {
            uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
            registry_type: RegistryType::Data,
        };

        let query_string = serde_qs::to_string(&params).unwrap();

        // check if a card UID exists (get request with UidRequest params)
        let request = Request::builder()
            .uri(format!("/opsml/api/card?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let uid_response: UidResponse = serde_json::from_slice(&body).unwrap();

        // assert true
        assert!(uid_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_card_repositories() {
        let helper = TestHelper::new().await;

        /////////////////////// Test respositories ///////////////////////
        let params = RepositoryRequest {
            registry_type: RegistryType::Model,
        };

        let query_string = serde_qs::to_string(&params).unwrap();

        // check if a card UID exists (get request with UidRequest params)
        let request = Request::builder()
            .uri(format!("/opsml/api/card/repositories?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let repository_response: RepositoryResponse = serde_json::from_slice(&body).unwrap();

        // assert 10
        assert_eq!(repository_response.repositories.len(), 10);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_card_stats_and_query() {
        let helper = TestHelper::new().await;

        /////////////////////// Test registry stats ///////////////////////

        let params = RegistryStatsRequest {
            registry_type: RegistryType::Model,
            search_term: None,
        };

        let query_string = serde_qs::to_string(&params).unwrap();
        let request = Request::builder()
            .uri(format!("/opsml/api/card/registry/stats?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let stats_response: RegistryStatsResponse = serde_json::from_slice(&body).unwrap();
        assert_eq!(stats_response.stats.nbr_names, 10);

        let params = RegistryStatsRequest {
            registry_type: RegistryType::Model,
            search_term: Some("Model1".to_string()),
        };

        let query_string = serde_qs::to_string(&params).unwrap();
        let request = Request::builder()
            .uri(format!("/opsml/api/card/registry/stats?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let stats_response: RegistryStatsResponse = serde_json::from_slice(&body).unwrap();
        assert_eq!(stats_response.stats.nbr_names, 2);

        /////////////////////// Test query page ///////////////////////

        let args = QueryPageRequest {
            registry_type: RegistryType::Model,
            sort_by: None,
            repository: None,
            search_term: None,
            page: None,
        };

        let query_string = serde_qs::to_string(&args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/registry/page?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let page_response: QueryPageResponse = serde_json::from_slice(&body).unwrap();

        assert_eq!(page_response.summaries.len(), 10);

        let args = QueryPageRequest {
            registry_type: RegistryType::Model,
            sort_by: None,
            repository: None,
            search_term: Some("Model2".to_string()),
            page: None,
        };

        let query_string = serde_qs::to_string(&args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/registry/page?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let page_response: QueryPageResponse = serde_json::from_slice(&body).unwrap();

        assert_eq!(page_response.summaries.len(), 1);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_list_cards() {
        let helper = TestHelper::new().await;

        let args = CardQueryArgs {
            uid: None,
            name: None,
            repository: None,
            version: None,
            max_date: None,
            tags: None,
            limit: None,
            sort_by_timestamp: None,
            registry_type: RegistryType::Data,
        };

        let query_string = serde_qs::to_string(&args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 10);

        let args = CardQueryArgs {
            uid: None,
            name: None,
            repository: Some("repo1".to_string()),
            version: None,
            max_date: None,
            tags: None,
            limit: None,
            sort_by_timestamp: None,
            registry_type: RegistryType::Model,
        };

        let query_string = serde_qs::to_string(&args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 1);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_datacard_crud() {
        let helper = TestHelper::new().await;

        let card_version_request = CardVersionRequest {
            name: "DataCard".to_string(),
            repository: "repo1".to_string(),
            version: Some("1.0.0".to_string()),
            version_type: VersionType::Minor,
            pre_tag: None,
            build_tag: None,
        };

        // DataCard
        let card_request = CreateCardRequest {
            card: Card::Data(DataCardClientRecord {
                name: "DataCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.0".to_string(),
                ..DataCardClientRecord::default()
            }),
            registry_type: RegistryType::Data,
            version_request: card_version_request,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        // sleep for 1 sec
        tokio::time::sleep(Duration::from_millis(100)).await;

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(create_response.registered);

        // get card by uid
        let list_cards = CardQueryArgs {
            uid: Some(create_response.key.uid),
            registry_type: RegistryType::Data,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&list_cards).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 1);

        // Update the card (get card from CardResults)
        let card = match card_results[0].clone() {
            Card::Data(card) => card,
            _ => panic!("Card not found"),
        };

        let card_request = UpdateCardRequest {
            registry_type: RegistryType::Data,
            card: Card::Data(DataCardClientRecord {
                name: "DataCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.1".to_string(),
                uid: card.uid.clone(),
                app_env: card.app_env,
                created_at: card.created_at,
                experimentcard_uid: card.experimentcard_uid,
                auditcard_uid: card.auditcard_uid,
                interface_type: card.interface_type,
                data_type: card.data_type,
                tags: card.tags,
                username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            }),
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/card/update")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let update_response: UpdateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(update_response.updated);

        let delete_args = DeleteCardRequest {
            uid: card.uid.clone(),
            repository: card.repository.clone(),
            registry_type: RegistryType::Data,
        };

        let query_string = serde_qs::to_string(&delete_args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/delete?{}", query_string))
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let delete_response: UidResponse = serde_json::from_slice(&body).unwrap();

        assert!(!delete_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_modelcard_crud() {
        let helper = TestHelper::new().await;

        let card_version_request = CardVersionRequest {
            name: "ModelCard".to_string(),
            repository: "repo1".to_string(),
            version: Some("1.0.0".to_string()),
            version_type: VersionType::Minor,
            pre_tag: None,
            build_tag: None,
        };

        // ModelCard
        let card_request = CreateCardRequest {
            card: Card::Model(ModelCardClientRecord {
                name: "ModelCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.0".to_string(),
                ..ModelCardClientRecord::default()
            }),
            registry_type: RegistryType::Model,
            version_request: card_version_request,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(create_response.registered);

        // sleep for 1 second to allow the key to be stored
        tokio::time::sleep(Duration::from_millis(100)).await;

        let load_request = CardQueryArgs {
            uid: Some(create_response.key.uid.clone()),
            registry_type: RegistryType::Model,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&load_request).unwrap();

        // get key
        let request = Request::builder()
            .uri(format!("/opsml/api/card/load?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;

        assert_eq!(response.status(), StatusCode::OK);
        // get response body
        let key_from_server: ArtifactKey =
            serde_json::from_slice(&response.into_body().collect().await.unwrap().to_bytes())
                .unwrap();

        assert_eq!(
            create_response.key.encrypted_key,
            key_from_server.encrypted_key
        );

        // get card by uid
        let list_cards = CardQueryArgs {
            uid: Some(create_response.key.uid),
            registry_type: RegistryType::Model,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&list_cards).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 1);

        // Update the card (get card from CardResults)
        let card = match card_results[0].clone() {
            Card::Model(card) => card,
            _ => panic!("Card not found"),
        };

        let card_request = UpdateCardRequest {
            registry_type: RegistryType::Model,
            card: Card::Model(ModelCardClientRecord {
                name: "DataCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.1".to_string(),
                uid: card.uid.clone(),
                app_env: card.app_env,
                created_at: card.created_at,
                experimentcard_uid: card.experimentcard_uid,
                auditcard_uid: card.auditcard_uid,
                interface_type: card.interface_type,
                datacard_uid: card.datacard_uid,
                data_type: card.data_type,
                model_type: card.model_type,
                task_type: card.task_type,
                tags: card.tags,
                username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            }),
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/card/update")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let update_response: UpdateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(update_response.updated);

        let delete_args = DeleteCardRequest {
            uid: card.uid.clone(),
            repository: card.repository.clone(),
            registry_type: RegistryType::Model,
        };

        let query_string = serde_qs::to_string(&delete_args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/delete?{}", query_string))
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let delete_response: UidResponse = serde_json::from_slice(&body).unwrap();

        assert!(!delete_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_experimentcard_crud() {
        let helper = TestHelper::new().await;

        let card_version_request = CardVersionRequest {
            name: "experimentcard".to_string(),
            repository: "repo1".to_string(),
            version: Some("1.0.0".to_string()),
            version_type: VersionType::Minor,
            pre_tag: None,
            build_tag: None,
        };

        // experimentcard
        let card_request = CreateCardRequest {
            card: Card::Experiment(ExperimentCardClientRecord {
                name: "experimentcard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.0".to_string(),
                ..ExperimentCardClientRecord::default()
            }),
            registry_type: RegistryType::Experiment,
            version_request: card_version_request,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(create_response.registered);

        // get card by uid
        let list_cards = CardQueryArgs {
            name: Some(card_request.card.name().to_string()), // name of the card
            repository: Some(card_request.card.repository().to_string()),
            version: Some(card_request.card.version().to_string()),
            registry_type: RegistryType::Experiment,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&list_cards).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 1);

        // Update the card (get card from CardResults)
        let card = match card_results[0].clone() {
            Card::Experiment(card) => card,
            _ => panic!("Card not found"),
        };

        let card_request = UpdateCardRequest {
            registry_type: RegistryType::Experiment,
            card: Card::Experiment(ExperimentCardClientRecord {
                name: "DataCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.1".to_string(),
                uid: card.uid.clone(),
                app_env: card.app_env,
                created_at: card.created_at,
                datacard_uids: card.datacard_uids,
                promptcard_uids: card.promptcard_uids,
                experimentcard_uids: card.experimentcard_uids,
                modelcard_uids: card.modelcard_uids,
                tags: card.tags,
                username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            }),
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/card/update")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let update_response: UpdateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(update_response.updated);

        let delete_args = DeleteCardRequest {
            uid: card.uid.clone(),
            repository: card.repository.clone(),
            registry_type: RegistryType::Experiment,
        };

        let query_string = serde_qs::to_string(&delete_args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/delete?{}", query_string))
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let delete_response: UidResponse = serde_json::from_slice(&body).unwrap();

        assert!(!delete_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_auditcard_crud() {
        let helper = TestHelper::new().await;

        let card_version_request = CardVersionRequest {
            name: "AuditCard".to_string(),
            repository: "repo1".to_string(),
            version: Some("1.0.0".to_string()),
            version_type: VersionType::Minor,
            pre_tag: None,
            build_tag: None,
        };

        // AuditCard
        let card_request = CreateCardRequest {
            card: Card::Audit(AuditCardClientRecord {
                name: "AuditCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.0".to_string(),
                ..AuditCardClientRecord::default()
            }),
            registry_type: RegistryType::Audit,
            version_request: card_version_request,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        // sleep for 1 sec
        tokio::time::sleep(Duration::from_millis(100)).await;

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(create_response.registered);

        // get card by uid
        let list_cards = CardQueryArgs {
            uid: Some(create_response.key.uid),
            registry_type: RegistryType::Audit,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&list_cards).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 1);

        // Update the card (get card from CardResults)
        let card = match card_results[0].clone() {
            Card::Audit(card) => card,
            _ => panic!("Card not found"),
        };

        let card_request = UpdateCardRequest {
            registry_type: RegistryType::Audit,
            card: Card::Audit(AuditCardClientRecord {
                name: "DataCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.1".to_string(),
                uid: card.uid.clone(),
                app_env: card.app_env,
                created_at: card.created_at,
                datacard_uids: card.datacard_uids,
                modelcard_uids: card.modelcard_uids,
                experimentcard_uids: card.experimentcard_uids,
                tags: card.tags,
                approved: card.approved,
                username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            }),
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/card/update")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let update_response: UpdateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(update_response.updated);

        let delete_args = DeleteCardRequest {
            uid: card.uid.clone(),
            repository: card.repository.clone(),
            registry_type: RegistryType::Audit,
        };

        let query_string = serde_qs::to_string(&delete_args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/api/card/delete?{}", query_string))
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let delete_response: UidResponse = serde_json::from_slice(&body).unwrap();

        assert!(!delete_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_experiment_routes() {
        let helper = TestHelper::new().await;
        let experiment_uid = "550e8400-e29b-41d4-a716-446655440000".to_string();

        let request = MetricRequest {
            experiment_uid: experiment_uid.clone(),
            metrics: vec![
                Metric {
                    name: "metric1".to_string(),
                    value: 1.0,
                    ..Default::default()
                },
                Metric {
                    name: "metric2".to_string(),
                    value: 1.0,
                    ..Default::default()
                },
            ],
        };

        let body = serde_json::to_string(&request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/experiment/metrics")
            .method("PUT")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let query_string = serde_qs::to_string(&GetMetricNamesRequest {
            experiment_uid: experiment_uid.clone(),
        })
        .unwrap();

        let request = Request::builder()
            .uri(format!(
                "/opsml/api/experiment/metrics/names?{}",
                query_string
            ))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let metric_names: Vec<String> = serde_json::from_slice(&body).unwrap();

        assert_eq!(metric_names.len(), 2);

        // get metric by experiment_uid
        let body = GetMetricRequest::new(experiment_uid.clone(), None);

        let request = Request::builder()
            .uri("/opsml/api/experiment/metrics") // should be post
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&body).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let metrics: Vec<Metric> = serde_json::from_slice(&body).unwrap();

        assert_eq!(metrics.len(), 2);

        // get metric by experiment_uid
        let body = GetMetricRequest::new(experiment_uid.clone(), Some(vec!["metric1".to_string()]));

        let request = Request::builder()
            .uri("/opsml/api/experiment/metrics") // should be post
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&body).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let metrics: Vec<Metric> = serde_json::from_slice(&body).unwrap();

        assert_eq!(metrics.len(), 1);

        // insert parameter

        let request = ParameterRequest {
            experiment_uid: experiment_uid.clone(),
            parameters: vec![
                Parameter {
                    name: "param1".to_string(),
                    value: ParameterValue::Int(1),
                },
                Parameter {
                    name: "param2".to_string(),
                    value: ParameterValue::Int(1),
                },
            ],
        };

        let body = serde_json::to_string(&request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/experiment/parameters")
            .method("PUT")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        // get parameters by experiment_uid
        let body = GetParameterRequest::new(experiment_uid.clone(), None);
        let request = Request::builder()
            .uri("/opsml/api/experiment/parameters") // should be post
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&body).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let parameters: Vec<Parameter> = serde_json::from_slice(&body).unwrap();
        assert_eq!(parameters.len(), 2);

        // get parameters by experiment_uid and parameter name
        let body =
            GetParameterRequest::new(experiment_uid.clone(), Some(vec!["param1".to_string()]));

        let request = Request::builder()
            .uri("/opsml/api/experiment/parameters") // should be post
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&body).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let parameters: Vec<Parameter> = serde_json::from_slice(&body).unwrap();
        assert_eq!(parameters.len(), 1);

        // insert hardware metrics

        let request = HardwareMetricRequest {
            experiment_uid: experiment_uid.clone(),
            metrics: HardwareMetrics::default(),
        };

        let body = serde_json::to_string(&request).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/experiment/hardware/metrics")
            .method("PUT")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        // get hardware metrics by experiment_uid
        let body = GetHardwareMetricRequest {
            experiment_uid: experiment_uid.clone(),
        };

        let query_string = serde_qs::to_string(&body).unwrap();

        let request = Request::builder()
            .uri(format!(
                "/opsml/api/experiment/hardware/metrics?{}",
                query_string
            ))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let metrics: Vec<HardwareMetrics> = serde_json::from_slice(&body).unwrap();

        assert_eq!(metrics.len(), 1);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_user_crud() {
        let helper = TestHelper::new().await;

        // 1. Create a new user
        let create_req = CreateUserRequest {
            username: "test_user".to_string(),
            password: "test_password".to_string(),
            permissions: Some(vec!["read".to_string(), "write".to_string()]),
            group_permissions: Some(vec!["user".to_string()]),
            role: Some("user".to_string()),
            active: Some(true),
        };

        let body = serde_json::to_string(&create_req).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/users")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let user_response: UserResponse = serde_json::from_slice(&body).unwrap();
        assert_eq!(user_response.username, "test_user");
        assert_eq!(
            user_response.permissions,
            vec!["read".to_string(), "write".to_string()]
        );
        assert_eq!(user_response.group_permissions, vec!["user".to_string()]);
        assert!(user_response.active);

        // 2. Get the user
        let request = Request::builder()
            .uri("/opsml/api/users/test_user")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let user_response: UserResponse = serde_json::from_slice(&body).unwrap();
        assert_eq!(user_response.username, "test_user");

        // 3. Update the user
        let update_req = UpdateUserRequest {
            password: Some("new_password".to_string()),
            permissions: Some(vec![
                "read".to_string(),
                "write".to_string(),
                "execute".to_string(),
            ]),
            group_permissions: Some(vec!["user".to_string(), "developer".to_string()]),
            active: Some(true),
        };

        let body = serde_json::to_string(&update_req).unwrap();

        let request = Request::builder()
            .uri("/opsml/api/users/test_user")
            .method("PUT")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let user_response: UserResponse = serde_json::from_slice(&body).unwrap();
        assert_eq!(
            user_response.permissions,
            vec![
                "read".to_string(),
                "write".to_string(),
                "execute".to_string()
            ]
        );
        assert_eq!(
            user_response.group_permissions,
            vec!["user".to_string(), "developer".to_string()]
        );

        // 4. List all users
        let request = Request::builder()
            .uri("/opsml/api/users")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let list_response: UserListResponse = serde_json::from_slice(&body).unwrap();

        // Should have at least 2 users (admin and test_user)
        assert!(list_response.users.len() >= 2);

        // Find our test user in the list
        let test_user = list_response
            .users
            .iter()
            .find(|u| u.username == "test_user");
        assert!(test_user.is_some());

        // 5. Delete the user
        let request = Request::builder()
            .uri("/opsml/api/users/test_user")
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        // Verify the user is deleted by trying to get it
        let request = Request::builder()
            .uri("/opsml/api/users/test_user")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::NOT_FOUND);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_get_card() {
        let helper = TestHelper::new().await;

        // 1. First create a card so we have something to get
        let card_version_request = CardVersionRequest {
            name: "name".to_string(),
            repository: "space".to_string(),
            version: Some("1.0.0".to_string()),
            version_type: VersionType::Minor,
            pre_tag: None,
            build_tag: None,
        };

        // Create a test card with some data
        let card_request = CreateCardRequest {
            card: Card::Data(DataCardClientRecord {
                name: "name".to_string(),
                repository: "space".to_string(),
                version: "1.0.0".to_string(),
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

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);
        //
        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();

        // wait 1 sec
        tokio::time::sleep(Duration::from_millis(100)).await;

        create_card_metadata(create_response.key.clone());
        //
        //// 2. Now test getting the card
        let params = CardQueryArgs {
            uid: None,
            name: Some("name".to_string()),
            repository: Some("space".to_string()),
            version: Some(create_response.version),
            max_date: None,
            tags: None,
            limit: None,
            sort_by_timestamp: None,
            registry_type: RegistryType::Data,
        };
        //
        let query_string = serde_qs::to_string(&params).unwrap();
        //
        let request = Request::builder()
            .uri(format!("/opsml/api/card/metadata?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);
        //
        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_json: serde_json::Value = serde_json::from_slice(&body).unwrap();
        //
        //// Verify the response contains the expected data
        assert_eq!(card_json["name"], "name");
        assert_eq!(card_json["repository"], "space");
        assert_eq!(card_json["version"], "1.0.0");
        //
        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_get_readme() {
        let mut helper = TestHelper::new().await;

        helper.create_card().await;

        // Create and upload the readme
        let read_me = "This is a test README";
        let create_readme = CreateReadeMe {
            repository: "space".to_string(),
            name: "name".to_string(),
            registry_type: RegistryType::Data,
            readme: read_me.to_string(),
        };

        let request = Request::builder()
            .uri("/opsml/api/card/readme")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&create_readme).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        //// 2. Now test getting the card
        let params = CardQueryArgs {
            uid: None,
            name: Some(helper.name.clone()),
            repository: Some(helper.repository.clone()),
            version: Some(helper.version.clone()),
            max_date: None,
            tags: None,
            limit: None,
            sort_by_timestamp: None,
            registry_type: RegistryType::Data,
        };
        //
        let query_string = serde_qs::to_string(&params).unwrap();
        //
        let request = Request::builder()
            .uri(format!("/opsml/api/card/readme?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);
        //
        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_readme: ReadeMe = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_readme.readme, "This is a test README");

        //
    }

    #[tokio::test]
    async fn test_opsml_server_render_file() {
        let mut helper = TestHelper::new().await;

        helper.create_card().await;
        let path = helper.create_files();

        let list_query = ListFileQuery { path };

        let query_string = serde_qs::to_string(&list_query).unwrap();

        // check if a card UID exists (get request with UidRequest params)
        let request = Request::builder()
            .uri(format!("/opsml/api/files/tree?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        // get response text
        let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
        let file_tree: FileTreeResponse = serde_json::from_slice(&body_bytes).unwrap();

        assert!(file_tree.files.len() == 2);

        let file1req = RawFileRequest {
            path: file_tree.files[0].path.clone(),
            uid: helper.key.uid.clone(),
            registry_type: RegistryType::Data,
        };

        let request = Request::builder()
            .uri("/opsml/api/files/content")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&file1req).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
        let file1: RawFile = serde_json::from_slice(&body_bytes).unwrap();
        assert!(file1.mime_type == "application/json");

        let file2req = RawFileRequest {
            path: file_tree.files[1].path.clone(),
            uid: helper.key.uid.clone(),
            registry_type: RegistryType::Data,
        };

        let request = Request::builder()
            .uri("/opsml/api/files/content")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&file2req).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
        let file2: RawFile = serde_json::from_slice(&body_bytes).unwrap();
        assert!(file2.mime_type == "image/png");
    }
}
