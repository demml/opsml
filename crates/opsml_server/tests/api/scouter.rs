// test for scouter route integration
// mainly used to test internal opsml route logic while mocking scouter responses
use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use http_body_util::BodyExt;
use opsml_crypt::encrypt_file;
use opsml_types::contracts::{ArtifactKey, UpdateProfileRequest};
use opsml_types::SaveName;
use opsml_types::Suffix;
use rand::Rng;
use reqwest::header;
use scouter_client::{BinnedCustomMetrics, TimeInterval};
use scouter_client::{
    BinnedPsiFeatureMetrics, DriftRequest, DriftType, ProfileRequest, ProfileStatusRequest,
    SpcDriftFeatures, SpcDriftProfile,
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
async fn test_scouter_routes_insert_profile() {
    let helper = TestHelper::new().await;

    let request = ProfileRequest {
        repository: helper.repository.clone(),
        drift_type: DriftType::Psi,
        profile: "test_profile".to_string(),
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
    let mut helper = TestHelper::new().await;
    helper.create_modelcard().await;

    let mut profile = create_drift_profile(helper.key.clone());

    profile.config.name = "updated_name".to_string();

    // assert that the profile has been updated
    assert_eq!(profile.config.name, "updated_name");

    let serialized = profile.model_dump_json();
    let request = UpdateProfileRequest {
        uid: helper.key.uid.clone(),
        request: ProfileRequest {
            repository: helper.repository.clone(),
            drift_type: DriftType::Spc,
            profile: serialized,
        },
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
        repository: helper.repository.clone(),
        name: "updated_name".to_string(),
        version: profile.config.version.clone(),
        active: true,
        drift_type: Some(DriftType::Spc),
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
    let helper = TestHelper::new().await;

    let drift_request = DriftRequest {
        name: helper.name.clone(),
        repository: helper.repository.clone(),
        version: helper.version.clone(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        drift_type: DriftType::Spc,
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/drift/spc?{}", query_string))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_psi_drift_features() {
    let helper = TestHelper::new().await;

    let drift_request = DriftRequest {
        name: helper.name.clone(),
        repository: helper.repository.clone(),
        version: helper.version.clone(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        drift_type: DriftType::Psi,
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/drift/psi?{}", query_string))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_custom_drift_features() {
    let helper = TestHelper::new().await;

    let drift_request = DriftRequest {
        name: helper.name.clone(),
        repository: helper.repository.clone(),
        version: helper.version.clone(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        drift_type: DriftType::Psi,
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/drift/custom?{}", query_string))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}
