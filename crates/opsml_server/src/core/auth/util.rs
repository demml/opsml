use crate::core::error::{internal_server_error, OpsmlServerError};
use crate::core::scouter::Routes as ScouterRoutes;
use crate::core::state::AppState;
use anyhow::Result;
/// Route for debugging information
use axum::{http::StatusCode, Json};
use opsml_auth::sso::types::UserInfo;
use opsml_sql::schemas::User;
use opsml_sql::traits::*;
use opsml_types::RequestType;
use std::sync::Arc;
use tracing::{error, info};

/// helper function for authenticating a user with sso
/// # Arguments
/// * `state` - The application state containing the auth manager
/// * `username` - The username of the user to authenticate
/// * `password` - The password of the user to authenticate
/// # Returns
/// * `Result<User, (StatusCode, Json<OpsmlServerError>)>` - The authenticated user or an error
async fn authenticate_user_with_sso_provider(
    state: &Arc<AppState>,
    username: &str,
    password: &str,
) -> Result<UserInfo, (StatusCode, Json<OpsmlServerError>)> {
    // get provider
    let provider = state.auth_manager.get_sso_provider().map_err(|e| {
        error!("SSO provider not set: {e}");
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(OpsmlServerError::sso_provider_not_set()),
        )
    })?;

    // authenticate with SSO provider
    let user = provider
        .authenticate_resource_password(username, password)
        .await
        .map_err(|e| {
            error!("Failed to authenticate with SSO provider: {e}");
            (
                StatusCode::UNAUTHORIZED,
                Json(OpsmlServerError::user_validation_error()),
            )
        })?;

    Ok(user)
}

async fn authenticate_user_with_sso_provider_callback(
    state: &Arc<AppState>,
    code: &str,
    code_verifier: &str,
) -> Result<UserInfo, (StatusCode, Json<OpsmlServerError>)> {
    // get provider
    let provider = state.auth_manager.get_sso_provider().map_err(|e| {
        error!("SSO provider not set: {e}");
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(OpsmlServerError::sso_provider_not_set()),
        )
    })?;

    // authenticate with SSO provider
    let user = provider
        .authenticate_auth_flow(code, code_verifier)
        .await
        .map_err(|e| {
            error!("Failed to authenticate with SSO provider: {e}");
            (
                StatusCode::UNAUTHORIZED,
                Json(OpsmlServerError::user_validation_error()),
            )
        })?;

    Ok(user)
}

async fn create_user(
    state: &Arc<AppState>,
    user: &UserInfo,
) -> Result<User, (StatusCode, Json<OpsmlServerError>)> {
    // create user for opsml
    let new_user = User::new_from_sso(&user.username, &user.email);

    // Save to database
    if let Err(e) = state.sql_client.insert_user(&new_user).await {
        error!("Failed to create user: {e}");
        return Err(internal_server_error(e, "Failed to create user"));
    }

    info!("User {} created successfully", user.username);

    // pass to scouter if enabled
    if state.scouter_client.enabled {
        let exchange_token = state
            .auth_manager
            .exchange_token_for_scouter(&new_user)
            .await
            .map_err(|e| {
                error!("Failed to exchange token from permissions: {e}");
                internal_server_error(e, "Failed to exchange token from permissions")
            })?;

        state
            .scouter_client
            .request(
                ScouterRoutes::Users,
                RequestType::Post,
                Some(serde_json::json!(&new_user)),
                None,
                None,
                &exchange_token,
            )
            .await
            .map_err(|e| {
                error!("Failed to create user in scouter: {e}");
                internal_server_error(e, "Failed to create user in scouter")
            })?;
    }
    info!("User {} created in scouter", user.username);
    // return the user
    Ok(new_user)
}

/// Validates a user with OpsML when logging in with SSO.
/// If the user does not exist in the database, it will be created.
/// # Arguments
/// * `state` - The application state
/// * `user` - The user information
/// # Returns
/// * `Result<User, (StatusCode, Json<OpsmlServerError>)>` - The user if it exists or was created, or an error
async fn validate_user_with_opsml(
    state: &Arc<AppState>,
    user: &UserInfo,
) -> Result<User, (StatusCode, Json<OpsmlServerError>)> {
    // get user from database
    // check if user exists in db
    match state
        .sql_client
        .get_user(&user.username, Some("sso"))
        .await
        .map_err(|e| {
            error!("Failed to get user from database: {e}");
            internal_server_error(e, "Failed to get user from database")
        })? {
        Some(opsml_user) => {
            // user exists, return it
            info!("User {} found in database", user.username);
            Ok(opsml_user)
        }
        None => {
            // user does not exist, create it
            info!(
                "User {} not found in database, creating new user",
                user.username
            );
            create_user(state, user).await
        }
    }
}

pub async fn authenticate_user_with_sso(
    state: &Arc<AppState>,
    username: &str,
    password: &str,
) -> Result<User, (StatusCode, Json<OpsmlServerError>)> {
    // authenticate user with sso provider
    let user_info = authenticate_user_with_sso_provider(state, username, password).await?;

    // validate user with opsml
    let user = validate_user_with_opsml(state, &user_info).await?;

    Ok(user)
}

pub async fn authenticate_user_with_sso_callback(
    state: &Arc<AppState>,
    code: &str,
    code_verifier: &str,
) -> Result<User, (StatusCode, Json<OpsmlServerError>)> {
    // authenticate user with sso provider callback code
    let user_info =
        authenticate_user_with_sso_provider_callback(state, code, code_verifier).await?;

    // validate user with opsml
    let user = validate_user_with_opsml(state, &user_info).await?;

    Ok(user)
}
