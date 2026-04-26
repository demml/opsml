// test for scouter route integration
// mainly used to test internal opsml route logic while mocking scouter responses
use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use opsml_crypt::encrypt_file;
use opsml_types::SaveName;
use opsml_types::Suffix;
use opsml_types::{
    RegistryType,
    contracts::{ArtifactKey, UpdateProfileRequest},
};
use opsml_sql::schemas::User;
use rand::Rng;
use reqwest::header;
use scouter_client::{
    DriftProfile, DriftType, GetProfileRequest, ListProfilesRequest, ListedProfile,
    ProfileRequest, ProfileStatusRequest, SpcDriftProfile, VersionRequest,
};
use std::path::PathBuf;

fn create_drift_profile(key: ArtifactKey) -> SpcDriftProfile {
    let profile = SpcDriftProfile::default();
    let save_path = PathBuf::from(format!(
        "opsml_registries/opsml_model_registry/{}/{}/v{}/{}",
        "space",
        "name",
        "1.0.0",
        SaveName::Drift
    ));

    let random_hex: String = rand::rng()
        .sample_iter(&rand::distr::Alphanumeric)
        .take(3)
        .map(char::from)
        .collect();

    let filename = format!(
        "{}-{}-{}",
        DriftType::Spc,
        SaveName::DriftProfile,
        random_hex
    );

    let profile_save_path = save_path.join(filename).with_extension(Suffix::Json);
    let encryption_key = key.get_crypt_key().unwrap();

    profile
        .save_to_json(Some(profile_save_path.clone()))
        .unwrap();

    encrypt_file(&profile_save_path, &encryption_key).unwrap();

    profile
}

#[tokio::test]
async fn test_scouter_routes_healthcheck() {
    let helper = TestHelper::new(None).await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/healthcheck")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_insert_profile() {
    let helper = TestHelper::new(None).await;

    let request = ProfileRequest {
        space: helper.space.clone(),
        drift_type: DriftType::Psi,
        profile: "test_profile".to_string(),
        version_request: Some(VersionRequest::default()),
        active: true,
        deactivate_others: false,
    };

    let body = serde_json::to_string(&request).unwrap();

    let request = Request::builder()
        .uri("/opsml/api/scouter/profile")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;

    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_update_profile() {
    let mut helper = TestHelper::new(None).await;
    helper.create_modelcard().await;

    let mut profile = create_drift_profile(helper.key.clone());

    profile.config.name = "updated_name".to_string();

    // assert that the profile has been updated
    assert_eq!(profile.config.name, "updated_name");

    let serialized = profile.model_dump_json();
    let request = UpdateProfileRequest {
        uid: helper.key.uid.clone(),
        profile_uri: "mocked_uri".to_string(),
        request: ProfileRequest {
            space: helper.space.clone(),
            drift_type: DriftType::Spc,
            profile: serialized,
            version_request: Some(VersionRequest::default()),
            active: true,
            deactivate_others: false,
        },
        registry_type: RegistryType::Model,
    };

    let body = serde_json::to_string(&request).unwrap();
    let request = Request::builder()
        .uri("/opsml/api/scouter/profile")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // update status code
    let request = ProfileStatusRequest {
        space: helper.space.clone(),
        name: "updated_name".to_string(),
        version: profile.config.version.clone(),
        active: true,
        drift_type: Some(DriftType::Spc),
        deactivate_others: true,
    };

    let body = serde_json::to_string(&request).unwrap();
    let request = Request::builder()
        .uri("/opsml/api/scouter/profile/status")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

fn restricted_token(helper: &TestHelper) -> String {
    let user = User {
        username: "limited-user".to_string(),
        permissions: vec![],
        group_permissions: vec![],
        ..Default::default()
    };
    helper.app_state.auth_manager.generate_jwt(&user).unwrap()
}

#[tokio::test]
async fn test_scouter_routes_get_profile() {
    let mut helper = TestHelper::new(None).await;

    let profile = DriftProfile::Spc(SpcDriftProfile::default());
    let _mock = helper
        .server
        .server
        .mock("GET", "/scouter/profile")
        .match_query(mockito::Matcher::Any)
        .with_status(200)
        .with_body(serde_json::to_string(&profile).unwrap())
        .create_async()
        .await;

    let request = GetProfileRequest {
        name: "name".to_string(),
        space: helper.space.clone(),
        version: "1.0.0".to_string(),
        drift_type: DriftType::Spc,
    };
    let query_string = serde_qs::to_string(&request).unwrap();

    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/profile?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_list_profiles() {
    let mut helper = TestHelper::new(None).await;

    let response_payload = vec![ListedProfile {
        profile: DriftProfile::Spc(SpcDriftProfile::default()),
        active: true,
    }];

    let _mock = helper
        .server
        .server
        .mock("POST", "/scouter/profiles")
        .with_status(200)
        .with_body(serde_json::to_string(&response_payload).unwrap())
        .create_async()
        .await;

    let body = serde_json::to_string(&ListProfilesRequest {
        space: helper.space.clone(),
        name: "name".to_string(),
        version: "1.0.0".to_string(),
    })
    .unwrap();
    let request = Request::builder()
        .uri("/opsml/api/scouter/profiles")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_get_profile_requires_read_permission() {
    let helper = TestHelper::new(None).await;

    let token = restricted_token(&helper);
    let request_query = GetProfileRequest {
        name: "name".to_string(),
        space: helper.space.clone(),
        version: "1.0.0".to_string(),
        drift_type: DriftType::Spc,
    };
    let query_string = serde_qs::to_string(&request_query).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/profile?{query_string}"))
        .method("GET")
        .header(header::AUTHORIZATION, format!("Bearer {token}"))
        .header(header::USER_AGENT, "opsml-test")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_no_auth(request).await;
    assert_eq!(response.status(), StatusCode::FORBIDDEN);
}

#[tokio::test]
async fn test_scouter_routes_list_profiles_requires_read_permission() {
    let helper = TestHelper::new(None).await;

    let token = restricted_token(&helper);
    let body = serde_json::to_string(&ListProfilesRequest {
        space: "space".to_string(),
        name: "name".to_string(),
        version: "1.0.0".to_string(),
    })
    .unwrap();
    let request = Request::builder()
        .uri("/opsml/api/scouter/profiles")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .header(header::AUTHORIZATION, format!("Bearer {token}"))
        .header(header::USER_AGENT, "opsml-test")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_no_auth(request).await;
    assert_eq!(response.status(), StatusCode::FORBIDDEN);
}
