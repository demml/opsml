use crate::core::cards::schema::{QueryPageResponse, RegistryStatsResponse};
use crate::core::cards::utils::{get_next_version, insert_card_into_db};
use crate::core::files::utils::create_artifact_key;
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{delete, get, post},
    Json, Router,
};
use opsml_sql::base::SqlClient;
use opsml_sql::schemas::*;
use opsml_types::{cards::*, contracts::*};
use semver::Version;
use sqlx::types::Json as SqlxJson;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::path::PathBuf;
use std::sync::Arc;
use tracing::{debug, error, instrument};

/// Route for checking if a card UID exists
pub async fn check_card_uid(
    State(state): State<Arc<AppState>>,
    Query(params): Query<UidRequest>,
) -> Result<Json<UidResponse>, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&params.registry_type);
    let exists = state
        .sql_client
        .check_uid_exists(&params.uid, &table)
        .await
        .map_err(|e| {
            error!("Failed to check if UID exists: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(UidResponse { exists }))
}

/// Get card respositories
pub async fn get_card_repositories(
    State(state): State<Arc<AppState>>,
    params: Query<RepositoryRequest>,
) -> Result<Json<RepositoryResponse>, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&params.registry_type);
    let repos = state
        .sql_client
        .get_unique_repository_names(&table)
        .await
        .map_err(|e| {
            error!("Failed to get unique repository names: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(RepositoryResponse {
        repositories: repos,
    }))
}

/// query stats page
pub async fn get_registry_stats(
    State(state): State<Arc<AppState>>,
    Query(params): Query<RegistryStatsRequest>,
) -> Result<Json<RegistryStatsResponse>, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&params.registry_type);
    let stats = state
        .sql_client
        .query_stats(&table, params.search_term.as_deref())
        .await
        .map_err(|e| {
            error!("Failed to get unique repository names: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(RegistryStatsResponse { stats }))
}

// query page
pub async fn get_page(
    State(state): State<Arc<AppState>>,
    Query(params): Query<QueryPageRequest>,
) -> Result<Json<QueryPageResponse>, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&params.registry_type);
    let sort_by = params.sort_by.as_deref().unwrap_or("updated_at");
    let page = params.page.unwrap_or(0);
    let summaries = state
        .sql_client
        .query_page(
            sort_by,
            page,
            params.search_term.as_deref(),
            params.repository.as_deref(),
            &table,
        )
        .await
        .map_err(|e| {
            error!("Failed to get unique repository names: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(QueryPageResponse { summaries }))
}

pub async fn list_cards(
    State(state): State<Arc<AppState>>,
    Query(params): Query<CardQueryArgs>,
) -> Result<Json<Vec<Card>>, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&params.registry_type);

    let cards = state
        .sql_client
        .query_cards(&table, &params)
        .await
        .map_err(|e| {
            error!("Failed to get unique repository names: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    // convert to Cards struct
    match cards {
        CardResults::Data(data) => {
            let cards = data.into_iter().map(convert_datacard).collect();
            Ok(Json(cards))
        }
        CardResults::Model(data) => {
            let cards = data.into_iter().map(convert_modelcard).collect();
            Ok(Json(cards))
        }
        CardResults::Project(data) => {
            let cards = data.into_iter().map(convert_projectcard).collect();
            Ok(Json(cards))
        }
        CardResults::Run(data) => {
            let cards = data.into_iter().map(convert_runcard).collect();
            Ok(Json(cards))
        }
        CardResults::Pipeline(data) => {
            let cards = data.into_iter().map(convert_pipelinecard).collect();
            Ok(Json(cards))
        }
        CardResults::Audit(data) => {
            let cards = data.into_iter().map(convert_auditcard).collect();
            Ok(Json(cards))
        }
    }
}

#[instrument(skip_all)]
pub async fn create_card(
    State(state): State<Arc<AppState>>,
    Json(card_request): Json<CreateCardRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&card_request.registry_type);

    debug!(
        "Creating card: {}/{}/{} - registry: {:?}",
        &card_request.card.repository(),
        &card_request.card.name(),
        &card_request.card.version(),
        &card_request.registry_type
    );

    // (1) ------- Get the next version
    let version = get_next_version(
        state.sql_client.clone(),
        &table,
        card_request.version_request,
    )
    .await
    .map_err(|e| {
        error!("Failed to get next version: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({})),
        )
    })?;

    // (2) ------- Insert the card into the database
    let (uid, card_type, card_uri) = insert_card_into_db(
        state.sql_client.clone(),
        card_request.card.clone(),
        version.clone(),
        &table,
    )
    .await
    .map_err(|e| {
        error!("Failed to insert card into db: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({})),
        )
    })?;

    // (3) ------- Create the artifact key for card artifact encryption
    let key = create_artifact_key(
        state.sql_client.clone(),
        state.storage_settings.encryption_key.clone(),
        &uid,
        &card_type,
        &card_uri,
    )
    .await
    .map_err(|e| {
        error!("Failed to create artifact key: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({})),
        )
    })?;

    debug!("Card created successfully");
    Ok(Json(CreateCardResponse {
        registered: true,
        repository: card_request.card.repository().to_string(),
        name: card_request.card.name().to_string(),
        version: version.to_string(),
        key,
    }))
}

/// update card
#[instrument(skip_all)]
pub async fn update_card(
    State(state): State<Arc<AppState>>,
    Json(card_request): Json<UpdateCardRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&card_request.registry_type);

    // Note: We can use unwrap() here because a card being updated has already been created and thus has defaults.
    // match on registry type (all fields should be supplied)
    let card = match card_request.card {
        Card::Data(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({})),
                )
            })?;

            let server_card = DataCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                app_env: client_card.app_env.unwrap(),
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                contact: client_card.contact,
                tags: SqlxJson(client_card.tags),
                data_type: client_card.data_type,
                runcard_uid: client_card.runcard_uid.unwrap(),
                pipelinecard_uid: client_card.pipelinecard_uid.unwrap(),
                auditcard_uid: client_card.auditcard_uid.unwrap(),
                interface_type: client_card.interface_type,
                username: client_card.username,
            };
            ServerCard::Data(server_card)
        }

        Card::Model(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({})),
                )
            })?;

            let server_card = ModelCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                app_env: client_card.app_env.unwrap(),
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                contact: client_card.contact,
                tags: SqlxJson(client_card.tags),
                datacard_uid: client_card.datacard_uid.unwrap(),
                data_type: client_card.data_type,
                model_type: client_card.model_type,
                runcard_uid: client_card.runcard_uid.unwrap(),
                pipelinecard_uid: client_card.pipelinecard_uid.unwrap(),
                auditcard_uid: client_card.auditcard_uid.unwrap(),
                interface_type: client_card.interface_type,
                task_type: client_card.task_type,
                username: client_card.username,
            };
            ServerCard::Model(server_card)
        }

        Card::Project(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({})),
                )
            })?;

            let server_card = ProjectCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                project_id: client_card.project_id,
                username: client_card.username,
            };
            ServerCard::Project(server_card)
        }

        Card::Run(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({})),
                )
            })?;

            let server_card = RunCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                app_env: client_card.app_env.unwrap(),
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                contact: client_card.contact,
                tags: SqlxJson(client_card.tags),
                datacard_uids: SqlxJson(client_card.datacard_uids.unwrap()),
                modelcard_uids: SqlxJson(client_card.modelcard_uids.unwrap()),
                pipelinecard_uid: client_card.pipelinecard_uid.unwrap(),
                project: client_card.project,
                artifact_uris: SqlxJson(client_card.artifact_uris.unwrap()),
                compute_environment: SqlxJson(client_card.compute_environment.unwrap()),
                username: client_card.username,
            };
            ServerCard::Run(server_card)
        }

        Card::Pipeline(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({})),
                )
            })?;

            let server_card = PipelineCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                app_env: client_card.app_env.unwrap(),
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                contact: client_card.contact,
                tags: SqlxJson(client_card.tags),
                pipeline_code_uri: client_card.pipeline_code_uri,
                datacard_uids: SqlxJson(client_card.datacard_uids.unwrap()),
                modelcard_uids: SqlxJson(client_card.modelcard_uids.unwrap()),
                runcard_uids: SqlxJson(client_card.runcard_uids.unwrap()),
                username: client_card.username,
            };
            ServerCard::Pipeline(server_card)
        }

        Card::Audit(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({})),
                )
            })?;

            let server_card = AuditCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                app_env: client_card.app_env.unwrap(),
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                contact: client_card.contact,
                tags: SqlxJson(client_card.tags),
                approved: client_card.approved,
                datacard_uids: SqlxJson(client_card.datacard_uids.unwrap()),
                modelcard_uids: SqlxJson(client_card.modelcard_uids.unwrap()),
                runcard_uids: SqlxJson(client_card.runcard_uids.unwrap()),
                username: client_card.username,
            };
            ServerCard::Audit(server_card)
        }
    };

    state
        .sql_client
        .update_card(&table, &card)
        .await
        .map_err(|e| {
            error!("Failed to update card: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(UpdateCardResponse { updated: true }))
}

#[instrument(skip_all)]
pub async fn delete_card(
    State(state): State<Arc<AppState>>,
    Query(params): Query<UidRequest>,
) -> Result<Json<UidResponse>, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&params.registry_type);
    state
        .sql_client
        .delete_card(&table, &params.uid)
        .await
        .map_err(|e| {
            error!("Failed to delete card: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(UidResponse { exists: false }))
}

#[instrument(skip_all)]
pub async fn load_card(
    State(state): State<Arc<AppState>>,
    Query(params): Query<CardQueryArgs>,
) -> Result<Json<opsml_sql::schemas::ArtifactKey>, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&params.registry_type);
    let key = state
        .sql_client
        .get_card_key_for_loading(&table, &params)
        .await
        .map_err(|e| {
            error!("Failed to get card key for loading: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(key))
}

pub async fn get_card_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{}/card", prefix), get(check_card_uid))
            .route(
                &format!("{}/card/repositories", prefix),
                get(get_card_repositories),
            )
            .route(
                &format!("{}/card/registry/stats", prefix),
                get(get_registry_stats),
            )
            .route(&format!("{}/card/registry/page", prefix), get(get_page))
            .route(&format!("{}/card/list", prefix), get(list_cards))
            .route(&format!("{}/card/create", prefix), post(create_card))
            .route(&format!("{}/card/load", prefix), get(load_card))
            .route(&format!("{}/card/update", prefix), post(update_card))
            .route(&format!("{}/card/delete", prefix), delete(delete_card))
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create card router");
            // panic
            Err(anyhow::anyhow!("Failed to create card router"))
                .context("Panic occurred while creating the router")
        }
    }
}
