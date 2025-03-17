// test for scouter route integration
// mainly used to test internal opsml route logic while mocking scouter responses
use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use opsml_crypt::encrypt_file;
use opsml_types::contracts::{ArtifactKey, UpdateProfileRequest};
use opsml_types::SaveName;
use opsml_types::Suffix;
use rand::Rng;
use scouter_client::{DriftType, ProfileRequest, SpcDriftProfile};
use std::path::PathBuf;

fn create_drift_profile(key: ArtifactKey) -> SpcDriftProfile {
    let profile = SpcDriftProfile::default();
    let save_path = PathBuf::from(format!(
        "opsml_registries/opsml_model_registry/{}/{}/v{}",
        "space", "name", "1.0.0"
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
}
