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
    contracts::{ArtifactKey, UpdateProfileRequest},
    RegistryType,
};
use rand::Rng;
use reqwest::header;
use scouter_client::{
    DriftRequest, DriftType, ProfileRequest, ProfileStatusRequest, SpcDriftProfile, TimeInterval,
    VersionRequest,
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
    let encryption_key = key.get_decrypt_key().unwrap();

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

#[tokio::test]
async fn test_scouter_routes_spc_drift_features() {
    let helper = TestHelper::new(None).await;

    let drift_request = DriftRequest {
        space: helper.space.clone(),
        uid: "mocked_uid".to_string(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/drift/spc?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_psi_drift_features() {
    let helper = TestHelper::new(None).await;

    let drift_request = DriftRequest {
        uid: "mocked_uid".to_string(),
        space: helper.space.clone(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/drift/psi?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_custom_drift_features() {
    let helper = TestHelper::new(None).await;

    let drift_request = DriftRequest {
        space: helper.space.clone(),
        uid: "mocked_uid".to_string(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/drift/custom?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}
