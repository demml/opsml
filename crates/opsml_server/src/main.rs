use crate::core::router::create_router;
use crate::core::setup::setup_components;
use crate::core::state::AppState;
use anyhow::Ok;
use anyhow::Result;
use axum::Router;
use opsml_auth::auth::AuthManager;
use opsml_colors::Colorize;
use std::sync::Arc;
use tracing::{info, warn};

mod core;

async fn create_app() -> Result<Router> {
    // setup components (config, logging, storage client)
    let (config, storage_client, sql_client) = setup_components().await?;
    let auth_enabled = config.auth_settings.enabled;

    // Create shared state for the application (storage client, auth manager, config)
    let app_state = Arc::new(AppState {
        storage_client: Arc::new(storage_client),
        sql_client: Arc::new(sql_client),
        auth_manager: Arc::new(AuthManager::new(
            &config.auth_settings.jwt_secret,
            &config.auth_settings.refresh_secret,
        )),
        config: Arc::new(config),
    });

    info!("✅ Application state created");

    // create the router
    let app = create_router(app_state).await?;

    info!("✅ Router created");

    if auth_enabled {
        info!("✅ Auth enabled");
    } else {
        warn!("Auth disabled");
    }

    Ok(app)
}

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
    use crate::core::cards::schema::{QueryPageResponse, RegistryStatsResponse};
    use axum::response::Response;
    use axum::{
        body::Body,
        http::{header, Request, StatusCode},
    };
    use http_body_util::BodyExt; // for `collect`
    use opsml_client::*;
    use opsml_semver::VersionType;
    use opsml_settings::config::DatabaseSettings;
    use opsml_sql::base::SqlClient;
    use opsml_sql::enums::client::SqlClientEnum;
    use opsml_types::*;
    use opsml_types::{cards::*, contracts::*};

    use std::collections::HashMap;
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

    pub struct TestHelper {
        app: Router,
        token: JwtToken,
        write_dir: String,
    }

    impl TestHelper {
        pub async fn new() -> Self {
            // set OPSML_AUTH to true
            env::set_var("OPSML_AUTH", "true");

            cleanup();

            // create the app
            let app = create_app().await.unwrap();

            // populate db
            setup().await;

            // retrieve the token
            let token = TestHelper::login(&app).await;

            let write_dir = env::current_dir()
                .unwrap()
                .join("opsml_registries")
                .to_str()
                .unwrap()
                .to_string();

            Self {
                app,
                token,
                write_dir,
            }
        }

        pub async fn login(app: &Router) -> JwtToken {
            let response = app
                .clone()
                .oneshot(
                    Request::builder()
                        .uri("/opsml/auth/api/login")
                        .header("Username", "admin")
                        .header("Password", "test_password")
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

        pub async fn send_oneshot(&self, request: Request<Body>, use_auth: bool) -> Response<Body> {
            if use_auth {
                self.app
                    .clone()
                    .oneshot(self.with_auth_header(request))
                    .await
                    .unwrap()
            } else {
                self.app.clone().oneshot(request).await.unwrap()
            }
        }

        pub fn cleanup(&self) {
            cleanup();
        }
    }

    #[tokio::test]
    async fn test_opsml_server_login() {
        let helper = TestHelper::new().await;

        let request = Request::builder()
            .uri("/opsml/healthcheck")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        // add invalid token
        let request = Request::builder()
            .uri("/opsml/healthcheck")
            .header(header::AUTHORIZATION, format!("Bearer {}", "invalid_token"))
            .body(Body::empty())
            .unwrap();

        // false will use the invalid token
        let response = helper.send_oneshot(request, false).await;
        assert_eq!(response.status(), StatusCode::UNAUTHORIZED);

        // refresh token
        let request = Request::builder()
            .uri("/opsml/auth/api/refresh")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();

        let new_token: JwtToken = serde_json::from_slice(&body).unwrap();

        // check if the new token is different from the old token
        assert_ne!(helper.token.token, new_token.token);

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
            .uri(format!("/opsml/card?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
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
            .uri(format!("/opsml/card?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
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
            .uri(format!("/opsml/card/repositories?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
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
            .uri(format!("/opsml/card/registry/stats?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
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
            .uri(format!("/opsml/card/registry/stats?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
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
            .uri(format!("/opsml/card/registry/page?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
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
            .uri(format!("/opsml/card/registry/page?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let page_response: QueryPageResponse = serde_json::from_slice(&body).unwrap();

        assert_eq!(page_response.summaries.len(), 1);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_card_versions() {
        let helper = TestHelper::new().await;

        /////////////////////////// Card Versions/////////////////////
        let args = CardVersionRequest {
            registry_type: RegistryType::Data,
            name: "Data1".to_string(),
            repository: "repo1".to_string(),
            version: None,
            version_type: VersionType::Minor,
            pre_tag: None,
            build_tag: None,
        };

        let query_string = serde_qs::to_string(&args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/version?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let version_response: CardVersionResponse = serde_json::from_slice(&body).unwrap();

        assert_eq!(version_response.version, "3.1.0");

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_list_cards() {
        let helper = TestHelper::new().await;

        let args = ListCardRequest {
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
            .uri(format!("/opsml/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 10);

        let args = ListCardRequest {
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
            .uri(format!("/opsml/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 1);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_datacard_crud() {
        let helper = TestHelper::new().await;

        // DataCard
        let card_request = CreateCardRequest {
            card: Card::Data(DataCardClientRecord {
                name: "DataCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.0".to_string(),
                contact: "test".to_string(),
                ..DataCardClientRecord::default()
            }),
            registry_type: RegistryType::Data,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(create_response.registered);

        // get card by uid
        let list_cards = ListCardRequest {
            uid: Some(create_response.uid),
            registry_type: RegistryType::Data,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&list_cards).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
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
                contact: "test".to_string(),
                uid: card.uid.clone(),
                app_env: card.app_env,
                created_at: card.created_at,
                runcard_uid: card.runcard_uid,
                pipelinecard_uid: card.pipelinecard_uid,
                auditcard_uid: card.auditcard_uid,
                interface_type: card.interface_type,
                data_type: card.data_type,
                tags: card.tags,
                checksums: card.checksums,
            }),
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/update")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let update_response: UpdateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(update_response.updated);

        let delete_args = UidRequest {
            uid: card.uid.clone().unwrap(),
            registry_type: RegistryType::Data,
        };

        let query_string = serde_qs::to_string(&delete_args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/delete?{}", query_string))
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let delete_response: UidResponse = serde_json::from_slice(&body).unwrap();

        assert!(!delete_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_modelcard_crud() {
        let helper = TestHelper::new().await;

        // ModelCard
        let card_request = CreateCardRequest {
            card: Card::Model(ModelCardClientRecord {
                name: "ModelCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.0".to_string(),
                contact: "test".to_string(),
                ..ModelCardClientRecord::default()
            }),
            registry_type: RegistryType::Model,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(create_response.registered);

        // get card by uid
        let list_cards = ListCardRequest {
            uid: Some(create_response.uid),
            registry_type: RegistryType::Model,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&list_cards).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
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
                contact: "test".to_string(),
                uid: card.uid.clone(),
                app_env: card.app_env,
                created_at: card.created_at,
                runcard_uid: card.runcard_uid,
                pipelinecard_uid: card.pipelinecard_uid,
                auditcard_uid: card.auditcard_uid,
                interface_type: card.interface_type,
                datacard_uid: card.datacard_uid,
                sample_data_type: card.sample_data_type,
                model_type: card.model_type,
                task_type: card.task_type,
                tags: card.tags,
                checksums: card.checksums,
            }),
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/update")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let update_response: UpdateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(update_response.updated);

        let delete_args = UidRequest {
            uid: card.uid.clone().unwrap(),
            registry_type: RegistryType::Model,
        };

        let query_string = serde_qs::to_string(&delete_args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/delete?{}", query_string))
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let delete_response: UidResponse = serde_json::from_slice(&body).unwrap();

        assert!(!delete_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_runcard_crud() {
        let helper = TestHelper::new().await;

        // RunCard
        let card_request = CreateCardRequest {
            card: Card::Run(RunCardClientRecord {
                name: "RunCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.0".to_string(),
                contact: "test".to_string(),
                ..RunCardClientRecord::default()
            }),
            registry_type: RegistryType::Run,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(create_response.registered);

        // get card by uid
        let list_cards = ListCardRequest {
            uid: Some(create_response.uid),
            registry_type: RegistryType::Run,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&list_cards).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 1);

        // Update the card (get card from CardResults)
        let card = match card_results[0].clone() {
            Card::Run(card) => card,
            _ => panic!("Card not found"),
        };

        let card_request = UpdateCardRequest {
            registry_type: RegistryType::Run,
            card: Card::Run(RunCardClientRecord {
                name: "DataCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.1".to_string(),
                contact: "test".to_string(),
                uid: card.uid.clone(),
                app_env: card.app_env,
                created_at: Some(card.created_at.unwrap()),
                datacard_uids: card.datacard_uids,
                pipelinecard_uid: card.pipelinecard_uid,
                artifact_uris: card.artifact_uris,
                modelcard_uids: card.modelcard_uids,
                compute_environment: card.compute_environment,
                project: card.project,
                tags: card.tags,
                checksums: card.checksums,
            }),
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/update")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let update_response: UpdateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(update_response.updated);

        let delete_args = UidRequest {
            uid: card.uid.clone().unwrap(),
            registry_type: RegistryType::Run,
        };

        let query_string = serde_qs::to_string(&delete_args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/delete?{}", query_string))
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let delete_response: UidResponse = serde_json::from_slice(&body).unwrap();

        assert!(!delete_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_pipelinecard_crud() {
        let helper = TestHelper::new().await;

        // PipelineCard
        let card_request = CreateCardRequest {
            card: Card::Pipeline(PipelineCardClientRecord {
                name: "PipelineCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.0".to_string(),
                contact: "test".to_string(),
                ..PipelineCardClientRecord::default()
            }),
            registry_type: RegistryType::Pipeline,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(create_response.registered);

        // get card by uid
        let list_cards = ListCardRequest {
            uid: Some(create_response.uid),
            registry_type: RegistryType::Pipeline,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&list_cards).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 1);

        // Update the card (get card from CardResults)
        let card = match card_results[0].clone() {
            Card::Pipeline(card) => card,
            _ => panic!("Card not found"),
        };

        let card_request = UpdateCardRequest {
            registry_type: RegistryType::Pipeline,
            card: Card::Pipeline(PipelineCardClientRecord {
                name: "DataCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.1".to_string(),
                contact: "test".to_string(),
                uid: card.uid.clone(),
                app_env: card.app_env,
                created_at: card.created_at,
                datacard_uids: card.datacard_uids,
                modelcard_uids: card.modelcard_uids,
                runcard_uids: card.runcard_uids,
                tags: card.tags,
                pipeline_code_uri: card.pipeline_code_uri,
            }),
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/update")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let update_response: UpdateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(update_response.updated);

        let delete_args = UidRequest {
            uid: card.uid.clone().unwrap(),
            registry_type: RegistryType::Pipeline,
        };

        let query_string = serde_qs::to_string(&delete_args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/delete?{}", query_string))
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let delete_response: UidResponse = serde_json::from_slice(&body).unwrap();

        assert!(!delete_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_auditcard_crud() {
        let helper = TestHelper::new().await;

        // AuditCard
        let card_request = CreateCardRequest {
            card: Card::Audit(AuditCardClientRecord {
                name: "AuditCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.0".to_string(),
                contact: "test".to_string(),
                ..AuditCardClientRecord::default()
            }),
            registry_type: RegistryType::Audit,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(create_response.registered);

        // get card by uid
        let list_cards = ListCardRequest {
            uid: Some(create_response.uid),
            registry_type: RegistryType::Audit,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&list_cards).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
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
                contact: "test".to_string(),
                uid: card.uid.clone(),
                app_env: card.app_env,
                created_at: card.created_at,
                datacard_uids: card.datacard_uids,
                modelcard_uids: card.modelcard_uids,
                runcard_uids: card.runcard_uids,
                tags: card.tags,
                approved: card.approved,
            }),
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/update")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let update_response: UpdateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(update_response.updated);

        let delete_args = UidRequest {
            uid: card.uid.clone().unwrap(),
            registry_type: RegistryType::Audit,
        };

        let query_string = serde_qs::to_string(&delete_args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/delete?{}", query_string))
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let delete_response: UidResponse = serde_json::from_slice(&body).unwrap();

        assert!(!delete_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_projectcard_crud() {
        let helper = TestHelper::new().await;

        // ProjectCard
        let card_request = CreateCardRequest {
            card: Card::Project(ProjectCardClientRecord {
                name: "ProjectCard".to_string(),
                repository: "repo1".to_string(),
                version: "1.0.0".to_string(),
                project_id: 1,
                ..Default::default()
            }),
            registry_type: RegistryType::Project,
        };

        let body = serde_json::to_string(&card_request).unwrap();

        let request = Request::builder()
            .uri("/opsml/card/create")
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();
        assert!(create_response.registered);

        // get card by uid
        let list_cards = ListCardRequest {
            uid: Some(create_response.uid),
            registry_type: RegistryType::Project,
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&list_cards).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/list?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let card_results: Vec<Card> = serde_json::from_slice(&body).unwrap();

        assert_eq!(card_results.len(), 1);

        // Update the card (get card from CardResults)
        let card = match card_results[0].clone() {
            Card::Project(card) => card,
            _ => panic!("Card not found"),
        };

        let delete_args = UidRequest {
            uid: card.uid.clone().unwrap(),
            registry_type: RegistryType::Project,
        };

        let query_string = serde_qs::to_string(&delete_args).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/card/delete?{}", query_string))
            .method("DELETE")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let delete_response: UidResponse = serde_json::from_slice(&body).unwrap();

        assert!(!delete_response.exists);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_run_routes() {
        let helper = TestHelper::new().await;
        let run_uid = "550e8400-e29b-41d4-a716-446655440000".to_string();

        let request = MetricRequest {
            run_uid: run_uid.clone(),
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
            .uri("/opsml/run/metrics")
            .method("PUT")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let query_string = serde_qs::to_string(&GetMetricNamesRequest {
            run_uid: run_uid.clone(),
        })
        .unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/run/metrics/names?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let metric_names: Vec<String> = serde_json::from_slice(&body).unwrap();

        assert_eq!(metric_names.len(), 2);

        // get metric by run_uid
        let body = GetMetricRequest::new(run_uid.clone(), None);

        let request = Request::builder()
            .uri("/opsml/run/metrics") // should be post
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&body).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let metrics: Vec<Metric> = serde_json::from_slice(&body).unwrap();

        assert_eq!(metrics.len(), 2);

        // get metric by run_uid
        let body = GetMetricRequest::new(run_uid.clone(), Some(vec!["metric1".to_string()]));

        let request = Request::builder()
            .uri("/opsml/run/metrics") // should be post
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&body).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let metrics: Vec<Metric> = serde_json::from_slice(&body).unwrap();

        assert_eq!(metrics.len(), 1);

        // insert parameter

        let request = ParameterRequest {
            run_uid: run_uid.clone(),
            parameters: vec![
                Parameter {
                    name: "param1".to_string(),
                    value: "value1".to_string(),
                    ..Default::default()
                },
                Parameter {
                    name: "param2".to_string(),
                    value: "value2".to_string(),
                    ..Default::default()
                },
            ],
        };

        let body = serde_json::to_string(&request).unwrap();

        let request = Request::builder()
            .uri("/opsml/run/parameters")
            .method("PUT")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        // get parameters by run_uid
        let body = GetParameterRequest::new(run_uid.clone(), None);
        let request = Request::builder()
            .uri("/opsml/run/parameters") // should be post
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&body).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let parameters: Vec<Parameter> = serde_json::from_slice(&body).unwrap();
        assert_eq!(parameters.len(), 2);

        // get parameters by run_uid and parameter name
        let body = GetParameterRequest::new(run_uid.clone(), Some(vec!["param1".to_string()]));

        let request = Request::builder()
            .uri("/opsml/run/parameters") // should be post
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(serde_json::to_string(&body).unwrap()))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let parameters: Vec<Parameter> = serde_json::from_slice(&body).unwrap();
        assert_eq!(parameters.len(), 1);

        // insert hardware metrics

        let request = HardwareMetricRequest {
            run_uid: run_uid.clone(),
            metrics: vec![HardwareMetrics::default(), HardwareMetrics::default()],
        };

        let body = serde_json::to_string(&request).unwrap();

        let request = Request::builder()
            .uri("/opsml/run/hardware/metrics")
            .method("PUT")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(body))
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        // get hardware metrics by run_uid
        let body = GetHardwareMetricRequest {
            run_uid: run_uid.clone(),
        };

        let query_string = serde_qs::to_string(&body).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/run/hardware/metrics?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let metrics: Vec<HardwareMetrics> = serde_json::from_slice(&body).unwrap();

        assert_eq!(metrics.len(), 2);

        helper.cleanup();
    }

    #[tokio::test]
    async fn test_opsml_server_run_graphs() {
        let helper = TestHelper::new().await;

        let single_run_graph = RunGraph::new(
            "single".to_string(),
            GraphStyle::Line,
            "x".to_string(),
            "y".to_string(),
            vec![1.0, 2.0, 3.0],
            Some(vec![1.0, 2.0, 3.0]),
            None,
        )
        .unwrap();

        let mut y_grouped = HashMap::new();
        y_grouped.insert("y1".to_string(), vec![1.0, 2.0, 3.0]);
        y_grouped.insert("y2".to_string(), vec![1.0, 2.0, 3.0]);

        let multi_run_graph = RunGraph::new(
            "multi".to_string(),
            GraphStyle::Line,
            "x".to_string(),
            "y".to_string(),
            vec![1.0, 2.0, 3.0],
            None,
            Some(y_grouped),
        )
        .unwrap();

        let write_path = format!(
            "{}/opsml_run_registry/repo1/Run1/v0.0.0/graphs",
            helper.write_dir
        );

        // create pathBuf
        let path = PathBuf::from(write_path.clone());
        single_run_graph.save_to_json(Some(path.clone())).unwrap();
        multi_run_graph.save_to_json(Some(path.clone())).unwrap();

        let body = GetRunGraphsRequest {
            run_uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
        };

        let query_string = serde_qs::to_string(&body).unwrap();

        let request = Request::builder()
            .uri(format!("/opsml/run/graphs?{}", query_string))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request, true).await;

        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let graphs: Vec<RunGraph> = serde_json::from_slice(&body).unwrap();

        assert_eq!(graphs.len(), 2);

        helper.cleanup();
    }
}
