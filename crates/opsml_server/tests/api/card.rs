use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{header, Request, StatusCode},
};
use http_body_util::BodyExt; // for `collect`
use opsml_semver::VersionType;
use opsml_types::contracts::*;
use opsml_types::*;

use opsml_crypt::encrypt_file;
use opsml_server::core::cards::schema::{
    CreateReadeMe, QueryPageResponse, ReadeMe, RegistryStatsResponse, VersionPageResponse,
};
use std::path::PathBuf;

// create json
fn create_card_metadata(key: ArtifactKey) {
    let json = r#"{"name":"name","repository":"space","version":"1.0.0","uid":"550e8400-e29b-41d4-a716-446655440000","app_env":"dev","created_at":"2021-08-01T00:00:00Z"}"#;
    let path = format!(
        "opsml_registries/opsml_model_registry/{}/{}/v{}",
        "space", "name", "1.0.0"
    );
    std::fs::create_dir_all(path.clone()).unwrap();
    let lpath = PathBuf::from(path).join("card.json");
    std::fs::write(&lpath, json).unwrap();

    let encryption_key = key.get_decrypt_key().unwrap();

    encrypt_file(&lpath, &encryption_key).unwrap();
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
        repository: None,
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
        repository: None,
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

    // test getting version page
    let args = VersionPageRequest {
        registry_type: RegistryType::Model,
        repository: Some("repo1".to_string()),
        name: Some("Model1".to_string()),
        page: None,
    };
    let query_string = serde_qs::to_string(&args).unwrap();

    let request = Request::builder()
        .uri(format!(
            "/opsml/api/card/registry/version/page?{}",
            query_string
        ))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let version_page_response: VersionPageResponse = serde_json::from_slice(&body).unwrap();

    assert_eq!(version_page_response.summaries.len(), 1);

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_card_list_cards() {
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
async fn test_opsml_server_card_datacard_crud() {
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
async fn test_opsml_server_card_modelcard_crud() {
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
        serde_json::from_slice(&response.into_body().collect().await.unwrap().to_bytes()).unwrap();

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
async fn test_opsml_server_card_experimentcard_crud() {
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
async fn test_opsml_server_card_auditcard_crud() {
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
async fn test_opsml_server_card_get_card() {
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
        card: Card::Model(ModelCardClientRecord {
            name: "name".to_string(),
            repository: "space".to_string(),
            version: "1.0.0".to_string(),
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

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
    //
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let create_response: CreateCardResponse = serde_json::from_slice(&body).unwrap();

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
        registry_type: RegistryType::Model,
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
async fn test_opsml_server_card_get_readme() {
    let mut helper = TestHelper::new().await;

    helper.create_modelcard().await;

    // Create and upload the readme
    let read_me = "This is a test README";
    let create_readme = CreateReadeMe {
        repository: "space".to_string(),
        name: "name".to_string(),
        registry_type: RegistryType::Model,
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
        registry_type: RegistryType::Model,
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
    assert!(card_readme.exists);
    assert_eq!(card_readme.readme, "This is a test README");

    //
}
