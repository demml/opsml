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
use opsml_types::contracts::DeploymentConfig;
use std::path::PathBuf;

// create json
fn create_card_metadata(key: ArtifactKey) {
    let json = r#"{"name":"name","space":"space","version":"1.0.0","uid":"550e8400-e29b-41d4-a716-446655440000","app_env":"dev","created_at":"2021-08-01T00:00:00Z"}"#;
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
    let helper = TestHelper::new(None).await;

    /////////////////////// Test check uid ///////////////////////

    // Test if a card UID exists - should be false
    let params = UidRequest {
        uid: "test_uid".to_string(),
        registry_type: RegistryType::Data,
    };

    let query_string = serde_qs::to_string(&params).unwrap();

    // check if a card UID exists (get request with UidRequest params)
    let request = Request::builder()
        .uri(format!("/opsml/api/card?{query_string}"))
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
        .uri(format!("/opsml/api/card?{query_string}"))
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
async fn test_opsml_server_card_spaces() {
    let helper = TestHelper::new(None).await;

    /////////////////////// Test respositories ///////////////////////
    let params = RegistrySpaceRequest {
        registry_type: RegistryType::Model,
    };

    let query_string = serde_qs::to_string(&params).unwrap();

    // check if a card UID exists (get request with UidRequest params)
    let request = Request::builder()
        .uri(format!("/opsml/api/card/spaces?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let space_response: CardSpaceResponse = serde_json::from_slice(&body).unwrap();

    // assert 10
    assert_eq!(space_response.spaces.len(), 10);

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_card_stats_and_query() {
    let helper = TestHelper::new(None).await;

    /////////////////////// Test registry stats ///////////////////////

    let params = RegistryStatsRequest {
        registry_type: RegistryType::Model,
        search_term: None,
        space: None,
    };

    let query_string = serde_qs::to_string(&params).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/card/registry/stats?{query_string}"))
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
        space: None,
    };

    let query_string = serde_qs::to_string(&params).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/card/registry/stats?{query_string}"))
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
        space: None,
        search_term: None,
        page: None,
    };

    let query_string = serde_qs::to_string(&args).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/registry/page?{query_string}"))
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
        space: None,
        search_term: Some("Model2".to_string()),
        page: None,
    };

    let query_string = serde_qs::to_string(&args).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/registry/page?{query_string}"))
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
        space: Some("repo1".to_string()),
        name: Some("Model1".to_string()),
        page: None,
    };
    let query_string = serde_qs::to_string(&args).unwrap();

    let request = Request::builder()
        .uri(format!(
            "/opsml/api/card/registry/version/page?{query_string}",
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
    let helper = TestHelper::new(None).await;

    let args = CardQueryArgs {
        uid: None,
        name: None,
        space: None,
        version: None,
        max_date: None,
        tags: None,
        limit: None,
        sort_by_timestamp: None,
        service_type: None,
        registry_type: RegistryType::Data,
    };

    let query_string = serde_qs::to_string(&args).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/list?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let card_results: Vec<CardRecord> = serde_json::from_slice(&body).unwrap();

    assert_eq!(card_results.len(), 10);

    let args = CardQueryArgs {
        uid: None,
        name: None,
        space: Some("repo1".to_string()),
        version: None,
        max_date: None,
        tags: None,
        limit: None,
        sort_by_timestamp: None,
        service_type: None,
        registry_type: RegistryType::Model,
    };

    let query_string = serde_qs::to_string(&args).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/list?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let card_results: Vec<CardRecord> = serde_json::from_slice(&body).unwrap();

    assert_eq!(card_results.len(), 1);

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_card_datacard_crud() {
    let helper = TestHelper::new(None).await;

    let card_version_request = CardVersionRequest {
        name: "DataCard".to_string(),
        space: "repo1".to_string(),
        version: Some("1.0.0".to_string()),
        version_type: VersionType::Minor,
        pre_tag: None,
        build_tag: None,
    };

    // DataCard
    let card_request = CreateCardRequest {
        card: CardRecord::Data(DataCardClientRecord {
            name: "DataCard".to_string(),
            space: "repo1".to_string(),
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
        .uri(format!("/opsml/api/card/list?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let card_results: Vec<CardRecord> = serde_json::from_slice(&body).unwrap();

    assert_eq!(card_results.len(), 1);

    // Update the card (get card from CardResults)
    let card = match card_results[0].clone() {
        CardRecord::Data(card) => card,
        _ => panic!("Card not found"),
    };

    let card_request = UpdateCardRequest {
        registry_type: RegistryType::Data,
        card: CardRecord::Data(DataCardClientRecord {
            name: "DataCard".to_string(),
            space: "repo1".to_string(),
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
            opsml_version: card.opsml_version,
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
        space: card.space.clone(),
        registry_type: RegistryType::Data,
    };

    let query_string = serde_qs::to_string(&delete_args).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/delete?{query_string}"))
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
    let helper = TestHelper::new(None).await;

    let card_version_request = CardVersionRequest {
        name: "ModelCard".to_string(),
        space: "repo1".to_string(),
        version: Some("1.0.0".to_string()),
        version_type: VersionType::Minor,
        pre_tag: None,
        build_tag: None,
    };

    // ModelCard
    let card_request = CreateCardRequest {
        card: CardRecord::Model(ModelCardClientRecord {
            name: "ModelCard".to_string(),
            space: "repo1".to_string(),
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
        .uri(format!("/opsml/api/card/load?{query_string}"))
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
        .uri(format!("/opsml/api/card/list?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let card_results: Vec<CardRecord> = serde_json::from_slice(&body).unwrap();

    assert_eq!(card_results.len(), 1);

    // Update the card (get card from CardResults)
    let card = match card_results[0].clone() {
        CardRecord::Model(card) => card,
        _ => panic!("Card not found"),
    };

    let card_request = UpdateCardRequest {
        registry_type: RegistryType::Model,
        card: CardRecord::Model(ModelCardClientRecord {
            name: "DataCard".to_string(),
            space: "repo1".to_string(),
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
            opsml_version: card.opsml_version,
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
        space: card.space.clone(),
        registry_type: RegistryType::Model,
    };

    let query_string = serde_qs::to_string(&delete_args).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/delete?{query_string}"))
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
    let helper = TestHelper::new(None).await;

    let card_version_request = CardVersionRequest {
        name: "experimentcard".to_string(),
        space: "repo1".to_string(),
        version: Some("1.0.0".to_string()),
        version_type: VersionType::Minor,
        pre_tag: None,
        build_tag: None,
    };

    // experimentcard
    let card_request = CreateCardRequest {
        card: CardRecord::Experiment(ExperimentCardClientRecord {
            name: "experimentcard".to_string(),
            space: "repo1".to_string(),
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
        space: Some(card_request.card.space().to_string()),
        version: Some(card_request.card.version().to_string()),
        registry_type: RegistryType::Experiment,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&list_cards).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/list?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let card_results: Vec<CardRecord> = serde_json::from_slice(&body).unwrap();

    assert_eq!(card_results.len(), 1);

    // Update the card (get card from CardResults)
    let card = match card_results[0].clone() {
        CardRecord::Experiment(card) => card,
        _ => panic!("Card not found"),
    };

    let card_request = UpdateCardRequest {
        registry_type: RegistryType::Experiment,
        card: CardRecord::Experiment(ExperimentCardClientRecord {
            name: "DataCard".to_string(),
            space: "repo1".to_string(),
            version: "1.0.1".to_string(),
            uid: card.uid.clone(),
            app_env: card.app_env,
            created_at: card.created_at,
            datacard_uids: card.datacard_uids,
            modelcard_uids: card.modelcard_uids,
            promptcard_uids: card.promptcard_uids,
            service_card_uids: card.service_card_uids,
            experimentcard_uids: card.experimentcard_uids,
            tags: card.tags,
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            opsml_version: card.opsml_version,
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
        space: card.space.clone(),
        registry_type: RegistryType::Experiment,
    };

    let query_string = serde_qs::to_string(&delete_args).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/delete?{query_string}"))
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
    let helper = TestHelper::new(None).await;

    let card_version_request = CardVersionRequest {
        name: "AuditCard".to_string(),
        space: "repo1".to_string(),
        version: Some("1.0.0".to_string()),
        version_type: VersionType::Minor,
        pre_tag: None,
        build_tag: None,
    };

    // AuditCard
    let card_request = CreateCardRequest {
        card: CardRecord::Audit(AuditCardClientRecord {
            name: "AuditCard".to_string(),
            space: "repo1".to_string(),
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
        .uri(format!("/opsml/api/card/list?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;

    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let card_results: Vec<CardRecord> = serde_json::from_slice(&body).unwrap();

    assert_eq!(card_results.len(), 1);

    // Update the card (get card from CardResults)
    let card = match card_results[0].clone() {
        CardRecord::Audit(card) => card,
        _ => panic!("Card not found"),
    };

    let card_request = UpdateCardRequest {
        registry_type: RegistryType::Audit,
        card: CardRecord::Audit(AuditCardClientRecord {
            name: "DataCard".to_string(),
            space: "repo1".to_string(),
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
            opsml_version: card.opsml_version,
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
        space: card.space.clone(),
        registry_type: RegistryType::Audit,
    };

    let query_string = serde_qs::to_string(&delete_args).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/delete?{query_string}"))
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
async fn test_opsml_server_card_service_card_crud() {
    let helper = TestHelper::new(None).await;

    let card_version_request = CardVersionRequest {
        name: "service".to_string(),
        space: "repo1".to_string(),
        version: Some("1.0.0".to_string()),
        version_type: VersionType::Minor,
        pre_tag: None,
        build_tag: None,
    };

    // ServiceCard
    let card_request = CreateCardRequest {
        card: CardRecord::Service(ServiceCardClientRecord {
            name: "service".to_string(),
            space: "repo1".to_string(),
            version: "1.0.0".to_string(),
            ..ServiceCardClientRecord::default()
        }),
        registry_type: RegistryType::Service,
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
        registry_type: RegistryType::Service,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&list_cards).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/list?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let card_results: Vec<CardRecord> = serde_json::from_slice(&body).unwrap();

    assert_eq!(card_results.len(), 1);

    let card = match card_results[0].clone() {
        CardRecord::Service(card) => card,
        _ => panic!("Card not found"),
    };

    let card_request = UpdateCardRequest {
        registry_type: RegistryType::Service,
        card: CardRecord::Service(ServiceCardClientRecord {
            name: "service".to_string(),
            space: "repo1".to_string(),
            version: "1.0.1".to_string(),
            uid: card.uid.clone(),
            app_env: card.app_env,
            created_at: card.created_at,
            cards: card.cards,
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            service_type: card.service_type,
            metadata: card.metadata,
            deployment: card.deployment,
            service_config: card.service_config,
            opsml_version: card.opsml_version,
            tags: card.tags,
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
        space: card.space.clone(),
        registry_type: RegistryType::Service,
    };

    let query_string = serde_qs::to_string(&delete_args).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/delete?{query_string}"))
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
async fn test_opsml_server_card_service_card_mcps() {
    let helper = TestHelper::new(None).await;

    let card_version_request = CardVersionRequest {
        name: "service".to_string(),
        space: "repo1".to_string(),
        version: Some("1.0.0".to_string()),
        version_type: VersionType::Minor,
        pre_tag: None,
        build_tag: None,
    };

    let deploy = DeploymentConfig {
        environment: "dev".to_string(),
        provider: None,
        location: None,
        endpoints: vec!["http://localhost:8080".to_string()],
        resources: None,
        links: None,
    };

    // ServiceCard
    let card_request = CreateCardRequest {
        card: CardRecord::Service(ServiceCardClientRecord {
            name: "service".to_string(),
            space: "repo1".to_string(),
            version: "1.0.0".to_string(),
            service_type: ServiceType::Mcp.to_string(),
            service_config: ServiceConfig {
                mcp: Some(McpConfig {
                    capabilities: vec![McpCapability::Resources, McpCapability::Tools],
                    transport: McpTransport::Http,
                }),
                ..Default::default()
            },
            deployment: Some(vec![deploy]),
            ..ServiceCardClientRecord::default()
        }),
        registry_type: RegistryType::Service,
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

    // list mcp services
    let list_mcps = ServiceQueryArgs {
        service_type: Some(ServiceType::Mcp.to_string()),
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&list_mcps).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/genai/mcp/servers?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let mcp_results: McpServers = serde_json::from_slice(&body).unwrap();

    assert_eq!(mcp_results.servers.len(), 1);

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_card_promptcard_crud() {
    let helper = TestHelper::new(None).await;

    let card_version_request = CardVersionRequest {
        name: "prompt".to_string(),
        space: "repo1".to_string(),
        version: Some("1.0.0".to_string()),
        version_type: VersionType::Minor,
        pre_tag: None,
        build_tag: None,
    };

    // ServiceCard
    let card_request = CreateCardRequest {
        card: CardRecord::Prompt(PromptCardClientRecord {
            name: "prompt".to_string(),
            space: "repo1".to_string(),
            version: "1.0.0".to_string(),
            ..PromptCardClientRecord::default()
        }),
        registry_type: RegistryType::Prompt,
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
        registry_type: RegistryType::Prompt,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&list_cards).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/list?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let card_results: Vec<CardRecord> = serde_json::from_slice(&body).unwrap();

    assert_eq!(card_results.len(), 1);

    let card = match card_results[0].clone() {
        CardRecord::Prompt(card) => card,
        _ => panic!("Card not found"),
    };

    let card_request = UpdateCardRequest {
        registry_type: RegistryType::Prompt,
        card: CardRecord::Prompt(PromptCardClientRecord {
            name: "prompt".to_string(),
            space: "repo1".to_string(),
            version: "1.0.1".to_string(),
            uid: card.uid.clone(),
            app_env: card.app_env,
            tags: card.tags,
            experimentcard_uid: card.experimentcard_uid,
            auditcard_uid: card.auditcard_uid,
            created_at: card.created_at,
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            opsml_version: card.opsml_version,
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
        space: card.space.clone(),
        registry_type: RegistryType::Prompt,
    };

    let query_string = serde_qs::to_string(&delete_args).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/card/delete?{query_string}"))
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
    let helper = TestHelper::new(None).await;

    // 1. First create a card so we have something to get
    let card_version_request = CardVersionRequest {
        name: "name".to_string(),
        space: "space".to_string(),
        version: Some("1.0.0".to_string()),
        version_type: VersionType::Minor,
        pre_tag: None,
        build_tag: None,
    };

    // Create a test card with some data
    let card_request = CreateCardRequest {
        card: CardRecord::Model(ModelCardClientRecord {
            name: "name".to_string(),
            space: "space".to_string(),
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
        space: Some("space".to_string()),
        version: Some(create_response.version),
        max_date: None,
        tags: None,
        limit: None,
        sort_by_timestamp: None,
        service_type: None,
        registry_type: RegistryType::Model,
    };
    //
    let query_string = serde_qs::to_string(&params).unwrap();
    //
    let request = Request::builder()
        .uri(format!("/opsml/api/card/metadata?{query_string}"))
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
    assert_eq!(card_json["space"], "space");
    assert_eq!(card_json["version"], "1.0.0");
    //
    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_card_get_readme() {
    let mut helper = TestHelper::new(None).await;

    helper.create_modelcard().await;

    // Create and upload the readme
    let read_me = "This is a test README";
    let create_readme = CreateReadeMe {
        space: "space".to_string(),
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
        space: Some(helper.space.clone()),
        version: Some(helper.version.clone()),
        max_date: None,
        tags: None,
        limit: None,
        sort_by_timestamp: None,
        service_type: None,
        registry_type: RegistryType::Model,
    };
    //
    let query_string = serde_qs::to_string(&params).unwrap();
    //
    let request = Request::builder()
        .uri(format!("/opsml/api/card/readme?{query_string}"))
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

#[tokio::test]
async fn test_opsml_server_space_crud() {
    let helper = TestHelper::new(None).await;

    // 1. Create
    let request = CrudSpaceRequest {
        space: "space".to_string(),
        description: Some("This is a test space".to_string()),
    };

    let request = Request::builder()
        .uri("/opsml/api/card/space")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&request).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    //
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let space_crud: CrudSpaceResponse = serde_json::from_slice(&body).unwrap();

    assert!(space_crud.success);

    // 2. Read
    let params = CrudSpaceRequest {
        space: "space".to_string(),
        description: None, // We don't need a description for this request
    };

    let query_string = serde_qs::to_string(&params).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/card/space?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let space_record: SpaceRecordResponse = serde_json::from_slice(&body).unwrap();

    assert_eq!(space_record.spaces.len(), 1);
    assert_eq!(space_record.spaces[0].space, "space");
    assert_eq!(
        space_record.spaces[0].description,
        "This is a test space".to_string()
    );

    // 3. Update
    let update_request = CrudSpaceRequest {
        space: "space".to_string(),
        description: Some("Updated description".to_string()),
    };

    let request = Request::builder()
        .uri("/opsml/api/card/space")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&update_request).unwrap()))
        .unwrap();
    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let update_response: CrudSpaceResponse = serde_json::from_slice(&body).unwrap();
    assert!(update_response.success);

    // Verify the update
    let request = Request::builder()
        .uri(format!("/opsml/api/card/space?space={}", "space"))
        .method("GET")
        .body(Body::empty())
        .unwrap();
    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let space_record: SpaceRecordResponse = serde_json::from_slice(&body).unwrap();
    assert_eq!(space_record.spaces.len(), 1);
    assert_eq!(space_record.spaces[0].space, "space");
    assert_eq!(
        space_record.spaces[0].description,
        "Updated description".to_string()
    );

    // 4. Delete
    let delete_request = CrudSpaceRequest {
        space: "space".to_string(),
        description: None, // No description needed for deletion
    };

    let query_string = serde_qs::to_string(&delete_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/card/space?{query_string}"))
        .method("DELETE")
        .body(Body::empty())
        .unwrap();
    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let delete_response: CrudSpaceResponse = serde_json::from_slice(&body).unwrap();
    assert!(delete_response.success);
    // Verify deletion
    let request = Request::builder()
        .uri(format!("/opsml/api/card/space?space={}", "space"))
        .method("GET")
        .body(Body::empty())
        .unwrap();
    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let space_record: SpaceRecordResponse = serde_json::from_slice(&body).unwrap();
    assert!(space_record.spaces.is_empty(), "Space should be deleted");
}

#[tokio::test]
async fn test_opsml_server_space_stats() {
    let mut helper = TestHelper::new(None).await;

    helper.create_modelcard().await;

    // wait 200 ms
    tokio::time::sleep(tokio::time::Duration::from_millis(200)).await;

    let request = Request::builder()
        .uri("/opsml/api/card/space/stats")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    //
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let space_stats: SpaceStatsResponse = serde_json::from_slice(&body).unwrap();

    assert_eq!(space_stats.stats[0].space, "space");
    assert_eq!(space_stats.stats[0].model_count, 1);
    assert_eq!(space_stats.stats[0].data_count, 0);

    // create datacard

    helper.create_datacard().await;

    // wait 200 ms
    tokio::time::sleep(tokio::time::Duration::from_millis(200)).await;

    let request = Request::builder()
        .uri("/opsml/api/card/space/stats")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let space_stats: SpaceStatsResponse = serde_json::from_slice(&body).unwrap();

    assert_eq!(space_stats.stats[0].space, "space");
    assert_eq!(space_stats.stats[0].model_count, 1);
    assert_eq!(space_stats.stats[0].data_count, 1);

    // delete the datacard
    let delete_args = DeleteCardRequest {
        uid: helper.key.uid.clone(),
        space: helper.space.clone(),
        registry_type: RegistryType::Data,
    };
    let query_string = serde_qs::to_string(&delete_args).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/card/delete?{query_string}"))
        .method("DELETE")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // wait 200 ms
    tokio::time::sleep(tokio::time::Duration::from_millis(200)).await;

    let request = Request::builder()
        .uri("/opsml/api/card/space/stats")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let space_stats: SpaceStatsResponse = serde_json::from_slice(&body).unwrap();

    assert_eq!(space_stats.stats[0].space, "space");
    assert_eq!(space_stats.stats[0].model_count, 1);
    assert_eq!(space_stats.stats[0].data_count, 0);
    assert_eq!(space_stats.stats[0].prompt_count, 0);
    assert_eq!(space_stats.stats[0].experiment_count, 0);
}
