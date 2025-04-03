use crate::core::audit::{spawn_audit_task, AuditArgs};
use crate::core::cards::schema::{
    CreateReadeMe, QueryPageResponse, ReadeMe, RegistryStatsResponse, VersionPageResponse,
};
use crate::core::cards::utils::{cleanup_artifacts, get_next_version, insert_card_into_db};
use crate::core::error::internal_server_error_with_audit;
use crate::core::files::utils::{
    create_and_store_encrypted_file, create_artifact_key, download_artifact, get_artifact_key,
};
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{ConnectInfo, Query, State},
    http::{HeaderMap, StatusCode},
    response::IntoResponse,
    routing::{delete, get, post},
    Extension, Json, Router,
};
use axum_extra::TypedHeader;
use headers::UserAgent;
use opsml_auth::permission::UserPermissions;
use opsml_client::Routes;
use opsml_crypt::decrypt_directory;
use opsml_sql::base::SqlClient;
use opsml_sql::schemas::*;
use opsml_types::{cards::*, contracts::*};
use opsml_types::{CommonKwargs, SaveName, Suffix};
use semver::Version;
use serde_json::json;
use sqlx::types::Json as SqlxJson;
use std::net::SocketAddr;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tempfile::tempdir;
use tracing::{debug, error, instrument};
/// Route for checking if a card UID exists
pub async fn check_card_uid(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(params): Query<UidRequest>,
) -> Result<Json<UidResponse>, (StatusCode, Json<serde_json::Value>)> {
    let audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::Check,
        ResourceType::Database,
        params.uid.clone(),
        serde_json::to_string(&params).unwrap_or_default(),
        params.registry_type.clone(),
        Routes::Card,
    );

    let table = CardTable::from_registry_type(&params.registry_type);
    let exists = state
        .sql_client
        .check_uid_exists(&params.uid, &table)
        .await
        .map_err(|e| {
            error!("Failed to check if UID exists: {}", e);
            internal_server_error_with_audit(
                e,
                "Failed to check if UID exists",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    Ok(Json(UidResponse { exists }))
}

/// Get card repositories
pub async fn get_card_repositories(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(params): Query<RepositoryRequest>,
) -> Result<Json<RepositoryResponse>, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&params.registry_type);

    let audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::List,
        ResourceType::Database,
        Routes::CardRepositories.to_string(),
        serde_json::to_string(&params).unwrap_or_default(),
        params.registry_type.clone(),
        Routes::CardRepositories,
    );

    let repos = state
        .sql_client
        .get_unique_repository_names(&table)
        .await
        .map_err(|e| {
            error!("Failed to get unique repository names: {}", e);
            internal_server_error_with_audit(
                e,
                "Failed to get unique repository names",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    Ok(Json(RepositoryResponse {
        repositories: repos,
    }))
}

/// query stats page
pub async fn get_registry_stats(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(params): Query<RegistryStatsRequest>,
) -> Result<Json<RegistryStatsResponse>, (StatusCode, Json<serde_json::Value>)> {
    let audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::List,
        ResourceType::Database,
        Routes::CardRegistryStats.to_string(),
        serde_json::to_string(&params).unwrap_or_default(),
        params.registry_type.clone(),
        Routes::CardRegistryStats,
    );

    let table = CardTable::from_registry_type(&params.registry_type);

    let stats = state
        .sql_client
        .query_stats(
            &table,
            params.search_term.as_deref(),
            params.repository.as_deref(),
        )
        .await
        .map_err(|e| {
            error!("Failed to get unique repository names: {}", e);
            internal_server_error_with_audit(
                e,
                "Failed to get unique repository names",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    Ok(Json(RegistryStatsResponse { stats }))
}

// query page
pub async fn get_page(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(params): Query<QueryPageRequest>,
) -> Result<Json<QueryPageResponse>, (StatusCode, Json<serde_json::Value>)> {
    let audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::List,
        ResourceType::Database,
        Routes::CardRegistryPage.to_string(),
        serde_json::to_string(&params).unwrap_or_default(),
        params.registry_type.clone(),
        Routes::CardRegistryPage,
    );

    let table = CardTable::from_registry_type(&params.registry_type);
    let sort_by = params.sort_by.as_deref().unwrap_or("updated_at");
    let page = params.page.unwrap_or(1);
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
            internal_server_error_with_audit(
                e,
                "Failed to get unique repository names",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    Ok(Json(QueryPageResponse { summaries }))
}

pub async fn get_version_page(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(params): Query<VersionPageRequest>,
) -> Result<Json<VersionPageResponse>, (StatusCode, Json<serde_json::Value>)> {
    let audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::List,
        ResourceType::Database,
        Routes::CardRegistryVersionPage.to_string(),
        serde_json::to_string(&params).unwrap_or_default(),
        params.registry_type.clone(),
        Routes::CardRegistryVersionPage,
    );

    let table = CardTable::from_registry_type(&params.registry_type);
    let page = params.page.unwrap_or(1);
    let summaries = state
        .sql_client
        .version_page(
            page,
            params.repository.as_deref(),
            params.name.as_deref(),
            &table,
        )
        .await
        .map_err(|e| {
            error!("Failed to get unique repository names: {}", e);
            internal_server_error_with_audit(
                e,
                "Failed to get unique repository names",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    Ok(Json(VersionPageResponse { summaries }))
}

pub async fn list_cards(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(params): Query<CardQueryArgs>,
) -> Result<Json<Vec<Card>>, (StatusCode, Json<serde_json::Value>)> {
    debug!(
        "Listing cards for registry: {:?} with params: {:?}",
        &params.registry_type, &params
    );

    let table = CardTable::from_registry_type(&params.registry_type);

    // get uid if present, else use CommonKwargs::Undefined
    let uid = params
        .uid
        .as_ref()
        .unwrap_or(&Routes::CardList.to_string())
        .to_string();

    let audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::List,
        ResourceType::Database,
        uid,
        serde_json::to_string(&params).unwrap_or_default(),
        params.registry_type.clone(),
        Routes::CardList,
    );

    let cards = state
        .sql_client
        .query_cards(&table, &params)
        .await
        .map_err(|e| {
            error!("Failed to get unique repository names: {}", e);
            internal_server_error_with_audit(
                e,
                "Failed to get unique repository names",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    spawn_audit_task(audit_args, state.sql_client.clone());
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

        CardResults::Experiment(data) => {
            let cards = data.into_iter().map(convert_experimentcard).collect();
            Ok(Json(cards))
        }

        CardResults::Audit(data) => {
            let cards = data.into_iter().map(convert_auditcard).collect();
            Ok(Json(cards))
        }

        CardResults::Prompt(data) => {
            let cards = data.into_iter().map(convert_promptcard).collect();
            Ok(Json(cards))
        }
    }
}

#[instrument(skip_all)]
pub async fn create_card(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Json(card_request): Json<CreateCardRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    let table = CardTable::from_registry_type(&card_request.registry_type);

    let mut audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::Create,
        ResourceType::Database,
        format!(
            "{}/{}/{}",
            card_request.card.repository(),
            card_request.card.name(),
            card_request.card.version()
        ),
        serde_json::to_string(&card_request).unwrap_or_default(),
        card_request.registry_type.clone(),
        Routes::CardCreate,
    );
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
        internal_server_error_with_audit(
            e,
            "Failed to get next version",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;
    // (2) ------- Insert the card into the database
    let (uid, registry_type, card_uri, app_env, created_at) = insert_card_into_db(
        state.sql_client.clone(),
        card_request.card.clone(),
        version.clone(),
        &table,
    )
    .await
    .map_err(|e| {
        error!("Failed to insert card into db: {}", e);
        internal_server_error_with_audit(
            e,
            "Failed to insert card into db",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;

    // update audit args now that we have the uid
    audit_args.resource_id = uid.to_string();

    // (3) ------- Create the artifact key for card artifact encryption
    let key = create_artifact_key(
        &state.sql_client,
        &state.storage_settings.encryption_key,
        &uid,
        &registry_type,
        &card_uri,
    )
    .await
    .map_err(|e| {
        error!("Failed to create artifact key: {}", e);
        internal_server_error_with_audit(
            e,
            "Failed to create artifact key",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;

    debug!("Card created successfully");
    spawn_audit_task(audit_args, state.sql_client.clone());
    Ok(Json(CreateCardResponse {
        registered: true,
        repository: card_request.card.repository().to_string(),
        name: card_request.card.name().to_string(),
        version: version.to_string(),
        app_env,
        created_at,
        key,
    }))
}

/// update card
#[instrument(skip_all)]
pub async fn update_card(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Json(card_request): Json<UpdateCardRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    debug!(
        "Updating card: {}/{}/{} - registry: {:?}",
        &card_request.card.repository(),
        &card_request.card.name(),
        &card_request.card.version(),
        &card_request.registry_type
    );
    let table = CardTable::from_registry_type(&card_request.registry_type);

    let audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::Create,
        ResourceType::Database,
        card_request.card.uid().to_string(),
        serde_json::to_string(&card_request).unwrap_or_default(),
        card_request.registry_type.clone(),
        Routes::CardUpdate,
    );

    // Note: We can use unwrap() here because a card being updated has already been created and thus has defaults.
    // match on registry type (all fields should be supplied)
    let card = match card_request.card {
        Card::Data(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                internal_server_error_with_audit(
                    e,
                    "Failed to parse version",
                    audit_args.clone(),
                    state.sql_client.clone(),
                )
            })?;

            let server_card = DataCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                app_env: client_card.app_env,
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                tags: SqlxJson(client_card.tags),
                data_type: client_card.data_type,
                experimentcard_uid: client_card.experimentcard_uid,
                auditcard_uid: client_card.auditcard_uid,
                interface_type: client_card.interface_type,
                username: client_card.username,
            };
            ServerCard::Data(server_card)
        }

        Card::Model(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                internal_server_error_with_audit(
                    e,
                    "Failed to parse version",
                    audit_args.clone(),
                    state.sql_client.clone(),
                )
            })?;

            let server_card = ModelCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                app_env: client_card.app_env,
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                tags: SqlxJson(client_card.tags),
                datacard_uid: client_card.datacard_uid,
                data_type: client_card.data_type,
                model_type: client_card.model_type,
                experimentcard_uid: client_card.experimentcard_uid,
                auditcard_uid: client_card.auditcard_uid,
                interface_type: client_card.interface_type,
                task_type: client_card.task_type,
                username: client_card.username,
            };
            ServerCard::Model(server_card)
        }

        Card::Experiment(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                internal_server_error_with_audit(
                    e,
                    "Failed to parse version",
                    audit_args.clone(),
                    state.sql_client.clone(),
                )
            })?;

            let server_card = ExperimentCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                app_env: client_card.app_env,
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                tags: SqlxJson(client_card.tags),
                datacard_uids: SqlxJson(client_card.datacard_uids),
                modelcard_uids: SqlxJson(client_card.modelcard_uids),
                promptcard_uids: SqlxJson(client_card.promptcard_uids),
                experimentcard_uids: SqlxJson(client_card.experimentcard_uids),
                username: client_card.username,
            };
            ServerCard::Experiment(server_card)
        }

        Card::Audit(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                internal_server_error_with_audit(
                    e,
                    "Failed to parse version",
                    audit_args.clone(),
                    state.sql_client.clone(),
                )
            })?;

            let server_card = AuditCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                app_env: client_card.app_env,
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                tags: SqlxJson(client_card.tags),
                approved: client_card.approved,
                datacard_uids: SqlxJson(client_card.datacard_uids),
                modelcard_uids: SqlxJson(client_card.modelcard_uids),
                experimentcard_uids: SqlxJson(client_card.experimentcard_uids),
                username: client_card.username,
            };
            ServerCard::Audit(server_card)
        }

        Card::Prompt(client_card) => {
            let version = Version::parse(&client_card.version).map_err(|e| {
                error!("Failed to parse version: {}", e);
                internal_server_error_with_audit(
                    e,
                    "Failed to parse version",
                    audit_args.clone(),
                    state.sql_client.clone(),
                )
            })?;

            let server_card = PromptCardRecord {
                uid: client_card.uid,
                created_at: client_card.created_at,
                app_env: client_card.app_env,
                name: client_card.name,
                repository: client_card.repository,
                major: version.major as i32,
                minor: version.minor as i32,
                patch: version.patch as i32,
                pre_tag: Some(version.pre.to_string()),
                build_tag: Some(version.build.to_string()),
                version: client_card.version,
                tags: SqlxJson(client_card.tags),
                experimentcard_uid: client_card.experimentcard_uid,
                auditcard_uid: client_card.auditcard_uid,
                username: client_card.username,
            };
            ServerCard::Prompt(server_card)
        }
    };

    state
        .sql_client
        .update_card(&table, &card)
        .await
        .map_err(|e| {
            error!("Failed to update card: {}", e);
            internal_server_error_with_audit(
                e,
                "Failed to update card",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    debug!("Card updated successfully");
    spawn_audit_task(audit_args, state.sql_client.clone());
    Ok(Json(UpdateCardResponse { updated: true }))
}

#[instrument(skip_all)]
pub async fn delete_card(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(params): Query<DeleteCardRequest>,
) -> Result<Json<UidResponse>, (StatusCode, Json<serde_json::Value>)> {
    debug!("Deleting card: {}", &params.uid);

    let audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::Delete,
        ResourceType::File,
        params.uid.clone(),
        serde_json::to_string(&params).unwrap_or_default(),
        params.registry_type.clone(),
        Routes::CardDelete,
    );

    if !perms.has_delete_permission(&params.repository) {
        error!("Permission denied");
        spawn_audit_task(
            audit_args.clone().with_error("Permission denied"),
            state.sql_client.clone(),
        );
        return Err((
            StatusCode::FORBIDDEN,
            Json(json!({ "error": "Permission denied" })),
        ));
    }

    let table = CardTable::from_registry_type(&params.registry_type);

    // delete the artifact key and the artifact itself
    cleanup_artifacts(
        &state.storage_client,
        &state.sql_client,
        params.uid.clone(),
        params.registry_type.clone(),
        &table,
    )
    .await
    .map_err(|e| {
        error!("Failed to cleanup artifacts: {}", e);
        internal_server_error_with_audit(
            e,
            "Failed to cleanup artifacts",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;

    // delete card
    state
        .sql_client
        .delete_card(&table, &params.uid)
        .await
        .map_err(|e| {
            error!("Failed to delete card: {}", e);
            internal_server_error_with_audit(
                e,
                "Failed to delete card",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    // need to delete the artifact key and the artifact itself

    spawn_audit_task(audit_args, state.sql_client.clone());
    Ok(Json(UidResponse { exists: false }))
}

#[instrument(skip_all)]
pub async fn load_card(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(params): Query<CardQueryArgs>,
) -> Result<Json<ArtifactKey>, (StatusCode, Json<serde_json::Value>)> {
    // get uid if exists
    let mut audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::Load,
        ResourceType::Database,
        CommonKwargs::Undefined.to_string(),
        serde_json::to_string(&params).unwrap_or_default(),
        params.registry_type.clone(),
        Routes::CardLoad,
    );

    let table = CardTable::from_registry_type(&params.registry_type);
    let key = state
        .sql_client
        .get_card_key_for_loading(&table, &params)
        .await
        .map_err(|e| {
            error!("Failed to get card key for loading: {}", e);
            internal_server_error_with_audit(
                e,
                "Failed to get card key for loading",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    // update audit args now that we have the uid
    audit_args.resource_id = key.uid.clone();
    spawn_audit_task(audit_args, state.sql_client.clone());
    Ok(Json(key))
}

#[instrument(skip_all)]
pub async fn get_card(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(params): Query<CardQueryArgs>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let mut audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::Load,
        ResourceType::Card,
        Routes::CardMetadata.to_string(),
        serde_json::to_string(&params).unwrap_or_default(),
        params.registry_type.clone(),
        Routes::CardMetadata,
    );

    if !perms.has_read_permission() {
        error!("Permission denied");
        spawn_audit_task(
            audit_args.clone().with_error("Permission denied"),
            state.sql_client.clone(),
        );
        return Err((
            StatusCode::FORBIDDEN,
            Json(json!({ "error": "Permission denied" })),
        ));
    }

    let table = CardTable::from_registry_type(&params.registry_type);

    let key = state
        .sql_client
        .get_card_key_for_loading(&table, &params)
        .await
        .map_err(|e| {
            error!("Failed to get card key for loading: {}", e);
            internal_server_error_with_audit(
                e,
                "Failed to get card key for loading",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    // get uid
    audit_args.resource_id = key.uid.clone();

    // create temp dir
    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {}", e);
        internal_server_error_with_audit(
            e,
            "Failed to create temp dir",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;

    let tmp_path = tmp_dir.path();
    let lpath = tmp_dir
        .path()
        .join(SaveName::Card)
        .with_extension(Suffix::Json);
    let rpath = key
        .storage_path()
        .join(SaveName::Card)
        .with_extension(Suffix::Json);

    state
        .storage_client
        .get(&lpath, &rpath, false)
        .await
        .map_err(|e| {
            error!("Failed to get card: {}", e);
            internal_server_error_with_audit(
                e,
                "Failed to get card",
                audit_args.clone(),
                state.sql_client.clone(),
            )
        })?;

    let decryption_key = key.get_decrypt_key().map_err(|e| {
        error!("Failed to get decryption key: {}", e);
        internal_server_error_with_audit(
            e,
            "Failed to get decryption key",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;

    decrypt_directory(tmp_path, &decryption_key).map_err(|e| {
        error!("Failed to decrypt directory: {}", e);
        internal_server_error_with_audit(
            e,
            "Failed to decrypt directory",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;

    let card = std::fs::read_to_string(lpath).map_err(|e| {
        error!("Failed to read card from file: {}", e);
        internal_server_error_with_audit(
            e,
            "Failed to read card from file",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;

    let card = serde_json::from_str(&card).map_err(|e| {
        error!("Failed to parse card: {}", e);
        internal_server_error_with_audit(
            e,
            "Failed to parse card",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;

    Ok(Json(card))
}

#[instrument(skip_all)]
pub async fn get_readme(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(params): Query<CardQueryArgs>,
) -> Result<Json<ReadeMe>, (StatusCode, Json<serde_json::Value>)> {
    let audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::Load,
        ResourceType::File,
        Routes::CardReadme.to_string(),
        serde_json::to_string(&params).unwrap_or_default(),
        params.registry_type.clone(),
        Routes::CardReadme,
    );

    if !perms.has_read_permission() {
        error!("Permission denied");
        spawn_audit_task(
            audit_args.clone().with_error("Permission denied"),
            state.sql_client.clone(),
        );
        return Err((
            StatusCode::FORBIDDEN,
            Json(json!({ "error": "Permission denied" })),
        ));
    }

    let table = CardTable::from_registry_type(&params.registry_type);

    // name and repository are required
    if params.name.is_none() || params.repository.is_none() {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({ "error": "Name and repository are required" })),
        ));
    }

    let name = params.name.as_ref().unwrap();
    let repository = params.repository.as_ref().unwrap();

    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {}", e);
        internal_server_error_with_audit(
            e,
            "Failed to create temp dir",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;

    let lpath = tmp_dir
        .path()
        .join(SaveName::ReadMe)
        .with_extension(Suffix::Md);

    let rpath = format!(
        "{}/{}/{}/{}.{}",
        table,
        repository,
        name,
        SaveName::ReadMe,
        Suffix::Md
    );

    match download_artifact(
        state.storage_client.clone(),
        state.sql_client.clone(),
        &lpath,
        &rpath,
        &params.registry_type.to_string(),
        None,
    )
    .await
    {
        Ok(_) => {
            let content = std::fs::read_to_string(&lpath).unwrap_or_default();
            spawn_audit_task(audit_args, state.sql_client.clone());
            Ok(Json(ReadeMe {
                readme: content,
                exists: true,
            }))
        }
        Err(e) => {
            error!("Failed to download artifact: {}", e);
            spawn_audit_task(audit_args, state.sql_client.clone());
            Ok(Json(ReadeMe {
                readme: "".to_string(),
                exists: false,
            }))
        }
    }
}

#[instrument(skip_all)]
pub async fn create_readme(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Json(req): Json<CreateReadeMe>,
) -> Result<Json<UploadResponse>, (StatusCode, Json<serde_json::Value>)> {
    let audit_args = AuditArgs::new(
        addr,
        agent,
        headers,
        Operation::Create,
        ResourceType::File,
        Routes::CardReadme.to_string(),
        serde_json::to_string(&req).unwrap_or_default(),
        req.registry_type.clone(),
        Routes::CardReadme,
    );

    if !perms.has_write_permission(&req.repository) {
        spawn_audit_task(
            audit_args.clone().with_error("Permission denied"),
            state.sql_client.clone(),
        );
        return Err((
            StatusCode::FORBIDDEN,
            Json(json!({ "error": "Permission denied" })),
        ));
    }

    let table = CardTable::from_registry_type(&req.registry_type);

    let readme_path = format!(
        "{}/{}/{}/{}.{}",
        table,
        &req.repository,
        &req.name,
        SaveName::ReadMe,
        Suffix::Md
    );

    // check if artifact key exists before creating a new key
    let key = get_artifact_key(
        &state.sql_client,
        &state.storage_settings.encryption_key,
        &req.registry_type.to_string(),
        &readme_path,
    )
    .await
    .map_err(|e| {
        error!("Failed to get artifact key: {}", e);
        internal_server_error_with_audit(
            e,
            "Failed to get artifact key",
            audit_args.clone(),
            state.sql_client.clone(),
        )
    })?;

    let lpath = format!("{}.{}", SaveName::ReadMe, Suffix::Md);
    let result = create_and_store_encrypted_file(
        state.storage_client.clone(),
        &req.readme,
        &lpath,
        &readme_path,
        key,
    )
    .await;

    spawn_audit_task(audit_args, state.sql_client.clone());
    match result {
        Ok(uploaded) => Ok(Json(uploaded)),
        Err(e) => Ok(Json(UploadResponse {
            uploaded: false,
            message: format!("Failed to upload readme: {}", e),
        })),
    }
}

pub async fn get_card_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{}/card", prefix), get(check_card_uid))
            .route(&format!("{}/card/metadata", prefix), get(get_card))
            .route(&format!("{}/card/readme", prefix), get(get_readme))
            .route(&format!("{}/card/readme", prefix), post(create_readme))
            .route(
                &format!("{}/card/repositories", prefix),
                get(get_card_repositories),
            )
            .route(
                &format!("{}/card/registry/stats", prefix),
                get(get_registry_stats),
            )
            .route(&format!("{}/card/registry/page", prefix), get(get_page))
            .route(
                &format!("{}/card/registry/version/page", prefix),
                get(get_version_page),
            )
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
