use crate::core::cards::schema::{
    CreateReadeMe, QueryPageResponse, ReadeMe, RegistryStatsResponse, VersionPageResponse,
};
use crate::core::cards::utils::{cleanup_artifacts, get_next_version, insert_card_into_db};
use crate::core::error::{internal_server_error, OpsmlServerError};
use crate::core::files::utils::{
    create_and_store_encrypted_file, create_artifact_key, download_artifact, get_artifact_key,
};
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::{delete, get, post, put},
    Extension, Json, Router,
};
use opsml_auth::permission::UserPermissions;
use opsml_crypt::decrypt_directory;
use opsml_events::AuditContext;
use opsml_sql::base::SqlClient;
use opsml_sql::schemas::*;
use opsml_types::{cards::*, contracts::*};
use opsml_types::{SaveName, Suffix};

use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tempfile::tempdir;
use tracing::{debug, error, info, instrument};
/// Route for checking if a card UID exists
#[axum::debug_handler]
pub async fn check_card_uid(
    State(state): State<Arc<AppState>>,
    Query(params): Query<UidRequest>,
) -> Result<Json<UidResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);
    let exists = state
        .sql_client
        .check_uid_exists(&params.uid, &table)
        .await
        .map_err(|e| {
            error!("Failed to check if UID exists: {e}");
            internal_server_error(e, "Failed to check if UID exists")
        })?;

    Ok(Json(UidResponse { exists }))
}

/// Get card spaces
pub async fn get_registry_spaces(
    State(state): State<Arc<AppState>>,
    Query(params): Query<RegistrySpaceRequest>,
) -> Result<Json<CardSpaceResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);

    let spaces = state
        .sql_client
        .get_unique_space_names(&table)
        .await
        .map_err(|e| {
            error!("Failed to get unique space names: {e}");
            internal_server_error(e, "Failed to get unique space names")
        })?;

    Ok(Json(CardSpaceResponse { spaces }))
}

pub async fn get_all_space_stats(
    State(state): State<Arc<AppState>>,
) -> Result<Json<SpaceStatsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let stats = state.sql_client.get_all_space_stats().await.map_err(|e| {
        error!("Failed to get all space stats: {e}");
        internal_server_error(e, "Failed to get all space stats")
    })?;

    Ok(Json(SpaceStatsResponse { stats }))
}

pub async fn get_space_record(
    State(state): State<Arc<AppState>>,
    Query(params): Query<CrudSpaceRequest>,
) -> Result<Json<SpaceRecordResponse>, (StatusCode, Json<OpsmlServerError>)> {
    match state.sql_client.get_space_record(&params.space).await {
        Ok(Some(space)) => Ok(Json(SpaceRecordResponse {
            spaces: vec![space],
        })),
        Ok(None) => Ok(Json(SpaceRecordResponse { spaces: vec![] })),
        Err(e) => {
            error!("Failed to get space record: {e}");
            Err(internal_server_error(e, "Failed to get space record"))
        }
    }
}

#[instrument(skip_all)]
pub async fn create_space_record(
    State(state): State<Arc<AppState>>,
    Json(space_request): Json<CrudSpaceRequest>,
) -> Result<Json<CrudSpaceResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let record = SpaceRecord {
        space: space_request.space,
        description: space_request.description.unwrap_or_default(),
    };
    state
        .sql_client
        .insert_space_record(&record)
        .await
        .map_err(|e| {
            error!("Failed to create space record: {e}");
            internal_server_error(e, "Failed to create space record")
        })?;
    Ok(Json(CrudSpaceResponse { success: true }))
}

#[instrument(skip_all)]
pub async fn update_space_record(
    State(state): State<Arc<AppState>>,
    Json(space_request): Json<CrudSpaceRequest>,
) -> Result<Json<CrudSpaceResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let record = SpaceRecord {
        space: space_request.space,
        description: space_request.description.unwrap_or_default(),
    };
    state
        .sql_client
        .update_space_record(&record)
        .await
        .map_err(|e| {
            error!("Failed to update space record: {e}");
            internal_server_error(e, "Failed to update space record")
        })?;
    Ok(Json(CrudSpaceResponse { success: true }))
}

#[instrument(skip_all)]
pub async fn delete_space_record(
    State(state): State<Arc<AppState>>,
    Query(space_request): Query<CrudSpaceRequest>,
) -> Result<Json<CrudSpaceResponse>, (StatusCode, Json<OpsmlServerError>)> {
    state
        .sql_client
        .delete_space_record(&space_request.space)
        .await
        .map_err(|e| {
            error!("Failed to delete space record: {e}");
            internal_server_error(e, "Failed to delete space record")
        })?;
    Ok(Json(CrudSpaceResponse { success: true }))
}

/// query stats page
pub async fn get_registry_stats(
    State(state): State<Arc<AppState>>,
    Query(params): Query<RegistryStatsRequest>,
) -> Result<Json<RegistryStatsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);

    let stats = state
        .sql_client
        .query_stats(
            &table,
            params.search_term.as_deref(),
            params.space.as_deref(),
        )
        .await
        .map_err(|e| {
            error!("Failed to get unique space names: {e}");
            internal_server_error(e, "Failed to get unique space names")
        })?;

    Ok(Json(RegistryStatsResponse { stats }))
}

// query page
pub async fn get_page(
    State(state): State<Arc<AppState>>,
    Query(params): Query<QueryPageRequest>,
) -> Result<Json<QueryPageResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);
    let sort_by = params.sort_by.as_deref().unwrap_or("updated_at");
    let page = params.page.unwrap_or(1);
    let summaries = state
        .sql_client
        .query_page(
            sort_by,
            page,
            params.search_term.as_deref(),
            params.space.as_deref(),
            &table,
        )
        .await
        .map_err(|e| {
            error!("Failed to get unique space names: {e}");
            internal_server_error(e, "Failed to get unique space names")
        })?;
    Ok(Json(QueryPageResponse { summaries }))
}

pub async fn get_version_page(
    State(state): State<Arc<AppState>>,
    Query(params): Query<VersionPageRequest>,
) -> Result<Json<VersionPageResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);
    let page = params.page.unwrap_or(1);
    let summaries = state
        .sql_client
        .version_page(
            page,
            params.space.as_deref(),
            params.name.as_deref(),
            &table,
        )
        .await
        .map_err(|e| {
            error!("Failed to get unique space names: {e}");
            internal_server_error(e, "Failed to get unique space names")
        })?;

    Ok(Json(VersionPageResponse { summaries }))
}

pub async fn list_cards(
    State(state): State<Arc<AppState>>,
    Query(params): Query<CardQueryArgs>,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    debug!(
        "Listing cards for registry: {:?} with params: {:?}",
        &params.registry_type, &params
    );

    let table = CardTable::from_registry_type(&params.registry_type);

    let cards = state
        .sql_client
        .query_cards(&table, &params)
        .await
        .map_err(|e| {
            error!("Failed to get unique space names: {e}");
            internal_server_error(e, "Failed to get unique space names")
        })?;

    // convert to Cards struct
    let json_response = match cards {
        CardResults::Data(data) => Json(data.into_iter().map(convert_datacard).collect::<Vec<_>>()),
        CardResults::Model(data) => {
            Json(data.into_iter().map(convert_modelcard).collect::<Vec<_>>())
        }
        CardResults::Experiment(data) => Json(
            data.into_iter()
                .map(convert_experimentcard)
                .collect::<Vec<_>>(),
        ),
        CardResults::Audit(data) => {
            Json(data.into_iter().map(convert_auditcard).collect::<Vec<_>>())
        }
        CardResults::Prompt(data) => {
            Json(data.into_iter().map(convert_promptcard).collect::<Vec<_>>())
        }
        CardResults::Service(data) => Json(
            data.into_iter()
                .map(convert_servicecard)
                .collect::<Vec<_>>(),
        ),
    };

    // Create response and add audit context
    let mut response = json_response.into_response();

    let audit_context = AuditContext {
        resource_id: "list_cards".to_string(),
        resource_type: ResourceType::Database,
        metadata: params.get_metadata(),
        registry_type: Some(params.registry_type.clone()),
        operation: Operation::List,
        access_location: None,
    };

    response.extensions_mut().insert(audit_context);

    Ok(response)
}

#[instrument(skip_all)]
pub async fn create_card(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(card_request): Json<CreateCardRequest>,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&card_request.registry_type);

    if !perms.has_write_permission(card_request.card.space()) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    // (1) ------- Get the next version
    let version = get_next_version(
        state.sql_client.clone(),
        &table,
        card_request.version_request.clone(),
    )
    .await
    .map_err(|e| {
        error!("Failed to get next version: {e}");
        internal_server_error(e, "Failed to get next version")
    })?;

    info!(
        "Creating card: {}/{}/{} - registry: {:?}",
        &card_request.card.space(),
        &card_request.card.name(),
        &version,
        &card_request.registry_type
    );

    // (2) ------- Insert the card into the database
    let (uid, space, registry_type, card_uri, app_env, created_at) = insert_card_into_db(
        state.sql_client.clone(),
        card_request.card.clone(),
        version.clone(),
        &table,
    )
    .await
    .map_err(|e| {
        error!("Failed to insert card into db: {e}");
        internal_server_error(e, "Failed to insert card into db")
    })?;

    // (3) ------- Create the artifact key for card artifact encryption
    let key = create_artifact_key(
        &state.sql_client,
        &state.storage_settings.encryption_key,
        &uid,
        &space,
        &registry_type,
        &card_uri,
    )
    .await
    .map_err(|e| {
        error!("Failed to create artifact key: {e}");
        internal_server_error(e, "Failed to create artifact key")
    })?;

    debug!("Card created successfully");

    let mut response = Json(CreateCardResponse {
        registered: true,
        space: card_request.card.space().to_string(),
        name: card_request.card.name().to_string(),
        version: version.to_string(),
        app_env,
        created_at,
        key,
    })
    .into_response();

    // (4) ------- Create audit and space stats events
    let audit_context = AuditContext {
        resource_id: uid.clone(),
        resource_type: ResourceType::Database,
        metadata: card_request.get_metadata(),
        registry_type: Some(card_request.registry_type.clone()),
        operation: Operation::Create,
        access_location: None,
    };

    // (5) ------- Create space name registry event
    let space_name = SpaceNameEvent {
        space: card_request.card.space().to_string(),
        name: card_request.card.name().to_string(),
        registry_type: card_request.registry_type.clone(),
    };

    {
        let extensions = response.extensions_mut();
        extensions.insert(audit_context);
        extensions.insert(space_name);
    }

    Ok(response)
}

/// update card
#[instrument(skip_all)]
pub async fn update_card(
    State(state): State<Arc<AppState>>,
    Json(card_request): Json<UpdateCardRequest>,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    info!(
        "Updating card: {}/{}/{} - registry: {:?}",
        &card_request.card.space(),
        &card_request.card.name(),
        &card_request.card.version(),
        &card_request.registry_type
    );
    let table = CardTable::from_registry_type(&card_request.registry_type);

    let card = ServerCard::from_card(card_request.clone().card).map_err(|e| {
        error!("Failed to convert card: {e}");
        internal_server_error(e, "Failed to convert card")
    })?;

    state
        .sql_client
        .update_card(&table, &card)
        .await
        .map_err(|e| {
            error!("Failed to update card: {e}");
            internal_server_error(e, "Failed to update card")
        })?;

    debug!("Card updated successfully");
    let mut response = Json(UpdateCardResponse { updated: true }).into_response();

    let audit_context = AuditContext {
        resource_id: card.uid().to_string(),
        resource_type: ResourceType::Database,
        metadata: card_request.get_metadata(),
        registry_type: Some(card_request.registry_type.clone()),
        operation: Operation::Update,
        access_location: None,
    };

    response.extensions_mut().insert(audit_context);

    Ok(response)
}

#[instrument(skip_all)]
pub async fn delete_card(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DeleteCardRequest>,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    info!("Deleting card: {}", &params.uid);

    if !perms.has_delete_permission(&params.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
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
        error!("Failed to cleanup artifacts: {e}");
        internal_server_error(e, "Failed to cleanup artifacts")
    })?;

    // delete card
    let (space, name) = state
        .sql_client
        .delete_card(&table, &params.uid)
        .await
        .map_err(|e| {
            error!("Failed to delete card: {e}");
            internal_server_error(e, "Failed to delete card")
        })?;

    let mut response = Json(UidResponse { exists: false }).into_response();

    let audit_context = AuditContext {
        resource_id: params.uid.clone(),
        resource_type: ResourceType::Database,
        metadata: params.get_metadata(),
        registry_type: Some(params.registry_type.clone()),
        operation: Operation::Delete,
        access_location: None,
    };

    response.extensions_mut().insert(audit_context);

    // Get count of remaining cards in the space
    let query_params = CardQueryArgs {
        space: Some(space.clone()),
        name: Some(name.clone()),
        registry_type: params.registry_type.clone(),
        ..Default::default()
    };

    let cards = state
        .sql_client
        .query_cards(&table, &query_params)
        .await
        .map_err(|e| {
            error!("Failed to get unique space names: {e}");
            internal_server_error(e, "Failed to get unique space names")
        })?;

    // If no cards remain in the space, delete the space name record
    if cards.is_empty() {
        state
            .sql_client
            .delete_space_name_record(&space, &name, &params.registry_type)
            .await
            .map_err(|e| {
                error!("Failed to delete space name record: {e}");
                internal_server_error(e, "Failed to delete space name record")
            })?;
    }

    Ok(response)
}

#[instrument(skip_all)]
pub async fn load_card(
    State(state): State<Arc<AppState>>,
    Query(params): Query<CardQueryArgs>,
) -> Result<Json<ArtifactKey>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);
    let key = state
        .sql_client
        .get_card_key_for_loading(&table, &params)
        .await
        .map_err(|e| {
            error!("Failed to get card key for loading: {e}");
            internal_server_error(e, "Failed to get card key for loading")
        })?;

    Ok(Json(key))
}

#[instrument(skip_all)]
pub async fn get_card(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<CardQueryArgs>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);

    let key = state
        .sql_client
        .get_card_key_for_loading(&table, &params)
        .await
        .map_err(|e| {
            error!("Failed to get card key for loading: {e}");
            internal_server_error(e, "Failed to get card key for loading")
        })?;

    if !perms.has_read_permission(&key.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    // create temp dir
    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {e}");
        internal_server_error(e, "Failed to create temp dir")
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
            error!("Failed to get card: {e}");
            internal_server_error(e, "Failed to get card")
        })?;

    let decryption_key = key.get_decrypt_key().map_err(|e| {
        error!("Failed to get decryption key: {e}");
        internal_server_error(e, "Failed to get decryption key")
    })?;

    decrypt_directory(tmp_path, &decryption_key).map_err(|e| {
        error!("Failed to decrypt directory: {e}");
        internal_server_error(e, "Failed to decrypt directory")
    })?;

    let card = std::fs::read_to_string(lpath).map_err(|e| {
        error!("Failed to read card from file: {e}");
        internal_server_error(e, "Failed to read card from file")
    })?;

    let card = serde_json::from_str(&card).map_err(|e| {
        error!("Failed to parse card: {e}");
        internal_server_error(e, "Failed to parse card")
    })?;

    Ok(Json(card))
}

#[instrument(skip_all)]
pub async fn get_readme(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<CardQueryArgs>,
) -> Result<Json<ReadeMe>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);

    // name and space are required
    if params.name.is_none() || params.space.is_none() {
        return OpsmlServerError::missing_space_and_name().into_response(StatusCode::BAD_REQUEST);
    }

    let name = params.name.as_ref().unwrap();
    let space = params.space.as_ref().unwrap();

    if !perms.has_read_permission(space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {e}");
        internal_server_error(e, "Failed to create temp dir")
    })?;

    let lpath = tmp_dir
        .path()
        .join(SaveName::ReadMe)
        .with_extension(Suffix::Md);

    let rpath = format!(
        "{}/{}/{}/{}.{}",
        table,
        space,
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
            Ok(Json(ReadeMe {
                readme: content,
                exists: true,
            }))
        }
        Err(_) => Ok(Json(ReadeMe {
            readme: "".to_string(),
            exists: false,
        })),
    }
}

#[instrument(skip_all)]
pub async fn create_readme(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<CreateReadeMe>,
) -> Result<Json<UploadResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_write_permission(&req.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let table = CardTable::from_registry_type(&req.registry_type);

    let readme_path = format!(
        "{}/{}/{}/{}.{}",
        table,
        &req.space,
        &req.name,
        SaveName::ReadMe,
        Suffix::Md
    );

    // check if artifact key exists before creating a new key
    let key = get_artifact_key(
        &state.sql_client,
        &state.storage_settings.encryption_key,
        &req.registry_type.to_string(),
        &req.space,
        &readme_path,
    )
    .await
    .map_err(|e| {
        error!("Failed to get artifact key: {e}");
        internal_server_error(e, "Failed to get artifact key")
    })?;

    let lpath = format!("{}.{}", SaveName::ReadMe, Suffix::Md);
    let result = create_and_store_encrypted_file(
        state.storage_client.clone(),
        &req.readme,
        &lpath,
        &readme_path,
        &key,
    )
    .await;

    match result {
        Ok(uploaded) => Ok(Json(uploaded)),
        Err(e) => Ok(Json(UploadResponse {
            uploaded: false,
            message: format!("Failed to upload readme: {e}"),
        })),
    }
}

pub async fn get_card_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{prefix}/card/space/stats"),
                get(get_all_space_stats),
            )
            .route(&format!("{prefix}/card/space"), get(get_space_record))
            .route(&format!("{prefix}/card/space"), post(create_space_record))
            .route(&format!("{prefix}/card/space"), put(update_space_record))
            .route(&format!("{prefix}/card/space"), delete(delete_space_record))
            // placing spaces here for now as there's not enough routes to justify a separate router
            .route(&format!("{prefix}/card"), get(check_card_uid))
            .route(&format!("{prefix}/card/metadata"), get(get_card))
            .route(&format!("{prefix}/card/readme"), get(get_readme))
            .route(&format!("{prefix}/card/readme"), post(create_readme))
            .route(&format!("{prefix}/card/spaces"), get(get_registry_spaces))
            .route(
                &format!("{prefix}/card/registry/stats"),
                get(get_registry_stats),
            )
            .route(&format!("{prefix}/card/registry/page"), get(get_page))
            .route(
                &format!("{prefix}/card/registry/version/page"),
                get(get_version_page),
            )
            .route(&format!("{prefix}/card/list"), get(list_cards))
            .route(&format!("{prefix}/card/create"), post(create_card))
            .route(&format!("{prefix}/card/load"), get(load_card))
            .route(&format!("{prefix}/card/update"), post(update_card))
            .route(&format!("{prefix}/card/delete"), delete(delete_card))
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
