use crate::core::cards::schema::DashboardStatsResponse;
use crate::core::cards::schema::FilterSummary;
use crate::core::cards::schema::PageInfo;
use crate::core::cards::schema::{
    CreateReadeMe, QueryPageResponse, ReadeMe, RegistryStatsResponse, VersionPageResponse,
};
use crate::core::cards::utils::{cleanup_artifacts, insert_card_into_db, run_skill_scan};
use crate::core::error::{OpsmlServerError, internal_server_error};
use crate::core::files::utils::{
    create_and_store_encrypted_file, create_artifact_key, download_artifact, get_artifact_key,
};
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::extract::OriginalUri;
use axum::{
    Extension, Json, Router,
    extract::{Query, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::{delete, get, post, put},
};
use opsml_auth::permission::UserPermissions;
use opsml_crypt::decrypt_directory;
use opsml_events::AuditContext;
use opsml_sql::enums::utils::get_next_version;
use opsml_sql::schemas::*;
use opsml_sql::traits::*;
use opsml_types::contracts::{CompareHashRequest, CompareHashResponse};
use opsml_types::{SaveName, Suffix};
use opsml_types::{cards::*, contracts::*};
use serde_qs;

use serde::de::DeserializeOwned;
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tempfile::tempdir;
use tracing::{debug, error, info, instrument, warn};

pub fn parse_qs_query<T: DeserializeOwned>(
    uri: &OriginalUri,
) -> Result<T, (StatusCode, Json<OpsmlServerError>)> {
    let query = uri.query().ok_or_else(|| {
        internal_server_error("No query string found", "No query string found", None)
    })?;

    serde_qs::from_str(query).map_err(|e| {
        error!("Failed to parse query string: {e}");
        internal_server_error(e, "Failed to parse query string", None)
    })
}

#[utoipa::path(
    get,
    path = "/opsml/api/card",
    params(
        ("uid" = String, Query, description = "Card UID to check"),
        ("registry_type" = String, Query, description = "Registry type"),
    ),
    responses(
        (status = 200, description = "UID existence check result", body = UidResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
            internal_server_error(e, "Failed to check if UID exists", None)
        })?;

    Ok(Json(UidResponse { exists }))
}

#[utoipa::path(
    get,
    path = "/opsml/api/card/spaces",
    params(
        ("registry_type" = String, Query, description = "Registry type"),
    ),
    responses(
        (status = 200, description = "List of unique space names", body = CardSpaceResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
            error!("Failed to get registry spaces: {e}");
            internal_server_error(e, "Failed to get registry spaces", None)
        })?;

    Ok(Json(CardSpaceResponse { spaces }))
}

#[utoipa::path(
    get,
    path = "/opsml/api/card/tags",
    params(
        ("registry_type" = String, Query, description = "Registry type"),
    ),
    responses(
        (status = 200, description = "List of unique tags", body = CardTagsResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
pub async fn get_registry_tags(
    State(state): State<Arc<AppState>>,
    Query(params): Query<RegistrySpaceRequest>,
) -> Result<Json<CardTagsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);

    let tags = state
        .sql_client
        .get_unique_tags(&table)
        .await
        .map_err(|e| {
            error!("Failed to get registry tags: {e}");
            internal_server_error(e, "Failed to get registry tags", None)
        })?;

    Ok(Json(CardTagsResponse { tags }))
}

#[utoipa::path(
    get,
    path = "/opsml/api/card/space/stats",
    responses(
        (status = 200, description = "Stats for all spaces", body = SpaceStatsResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
pub async fn get_all_space_stats(
    State(state): State<Arc<AppState>>,
) -> Result<Json<SpaceStatsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let stats = state.sql_client.get_all_space_stats().await.map_err(|e| {
        error!("Failed to get all space stats: {e}");
        internal_server_error(e, "Failed to get all space stats", None)
    })?;

    Ok(Json(SpaceStatsResponse { stats }))
}

#[utoipa::path(
    get,
    path = "/opsml/api/card/space",
    params(
        ("space" = String, Query, description = "Space name"),
        ("description" = Option<String>, Query, description = "Space description"),
    ),
    responses(
        (status = 200, description = "Space record", body = SpaceRecordResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
            Err(internal_server_error(e, "Failed to get space record", None))
        }
    }
}

#[utoipa::path(
    post,
    path = "/opsml/api/card/space",
    request_body(content = CrudSpaceRequest, description = "Space creation request"),
    responses(
        (status = 200, description = "Space created", body = CrudSpaceResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
            internal_server_error(e, "Failed to create space record", None)
        })?;
    Ok(Json(CrudSpaceResponse { success: true }))
}

#[utoipa::path(
    put,
    path = "/opsml/api/card/space",
    request_body(content = CrudSpaceRequest, description = "Space update request"),
    responses(
        (status = 200, description = "Space updated", body = CrudSpaceResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
            internal_server_error(e, "Failed to update space record", None)
        })?;
    Ok(Json(CrudSpaceResponse { success: true }))
}

#[utoipa::path(
    delete,
    path = "/opsml/api/card/space",
    params(
        ("space" = String, Query, description = "Space name to delete"),
        ("description" = Option<String>, Query, description = "Space description"),
    ),
    responses(
        (status = 200, description = "Space deleted", body = CrudSpaceResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
            internal_server_error(e, "Failed to delete space record", None)
        })?;
    Ok(Json(CrudSpaceResponse { success: true }))
}

#[utoipa::path(
    post,
    path = "/opsml/api/card/registry/stats",
    request_body(content = RegistryStatsRequest, description = "Registry stats query"),
    responses(
        (status = 200, description = "Registry statistics", body = RegistryStatsResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
/// query stats page
pub async fn retrieve_registry_stats(
    State(state): State<Arc<AppState>>,
    Json(params): Json<RegistryStatsRequest>,
) -> Result<Json<RegistryStatsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);

    let stats = state
        .sql_client
        .query_stats(
            &table,
            params.search_term.as_deref(),
            &params.spaces,
            &params.tags,
        )
        .await
        .map_err(|e| {
            error!("Failed to get registry stats: {e}");
            internal_server_error(e, "Failed to get registry stats", None)
        })?;

    Ok(Json(RegistryStatsResponse { stats }))
}

#[utoipa::path(
    get,
    path = "/opsml/api/card/dashboard/stats",
    responses(
        (status = 200, description = "Dashboard statistics", body = DashboardStatsResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
/// Get dashboard stats for the homepage
pub async fn retrieve_dashboard_stats(
    State(state): State<Arc<AppState>>,
) -> Result<Json<DashboardStatsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let stats = state
        .sql_client
        .query_dashboard_stats()
        .await
        .map_err(|e| {
            error!("Failed to get dashboard stats: {e}");
            internal_server_error(e, "Failed to get dashboard stats", None)
        })?;

    Ok(Json(DashboardStatsResponse { stats }))
}

#[utoipa::path(
    post,
    path = "/opsml/api/card/registry/page",
    request_body(content = QueryPageRequest, description = "Paginated card query"),
    responses(
        (status = 200, description = "Paginated card results", body = QueryPageResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
// query page
pub async fn retrieve_page(
    State(state): State<Arc<AppState>>,
    Json(params): Json<QueryPageRequest>,
) -> Result<Json<QueryPageResponse>, (StatusCode, Json<OpsmlServerError>)> {
    const DEFAULT_LIMIT: i32 = 30;
    const DEFAULT_SORT_BY: &str = "updated_at";

    let table = CardTable::from_registry_type(&params.registry_type);
    let cursor = params.get_cursor(DEFAULT_LIMIT, DEFAULT_SORT_BY);

    debug!(
        "Querying page: offset={}, limit={}, sort_by={}, filters={{search: {:?}, spaces: {:?}, tags: {:?}}}",
        cursor.offset, cursor.limit, cursor.sort_by, cursor.search_term, cursor.spaces, cursor.tags
    );

    let mut summaries = state
        .sql_client
        .query_page(
            &cursor.sort_by,
            cursor.limit,
            cursor.offset,
            cursor.search_term.as_deref(),
            &cursor.spaces,
            &cursor.tags,
            &table,
        )
        .await
        .map_err(|e| {
            error!("Failed to query page: {e}");
            internal_server_error(e, "Failed to query page", None)
        })?;

    let has_next = summaries.len() > cursor.limit as usize;
    if has_next {
        summaries.pop();
    }

    let has_previous = !cursor.is_first_page();

    let next_cursor = if has_next { Some(cursor.next()) } else { None };

    let previous_cursor = if has_previous {
        Some(cursor.previous())
    } else {
        None
    };

    debug!(
        "Next cursor: {:?}, Previous cursor: {:?}",
        next_cursor, previous_cursor
    );

    let page_info = PageInfo {
        page_size: summaries.len(),
        offset: cursor.offset,
        filters: FilterSummary {
            search_term: cursor.search_term.clone(),
            spaces: cursor.spaces.clone(),
            tags: cursor.tags.clone(),
            sort_by: cursor.sort_by.clone(),
        },
    };

    Ok(Json(QueryPageResponse {
        items: summaries,
        has_next,
        next_cursor,
        has_previous,
        previous_cursor,
        page_info,
    }))
}

#[utoipa::path(
    post,
    path = "/opsml/api/card/registry/version/page",
    request_body(content = VersionPageRequest, description = "Paginated version query"),
    responses(
        (status = 200, description = "Paginated version results", body = VersionPageResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
pub async fn query_version_page(
    State(state): State<Arc<AppState>>,
    Json(params): Json<VersionPageRequest>,
) -> Result<Json<VersionPageResponse>, (StatusCode, Json<OpsmlServerError>)> {
    const DEFAULT_LIMIT: i32 = 30;

    let table = CardTable::from_registry_type(&params.registry_type);
    let cursor = params.get_cursor(DEFAULT_LIMIT);

    debug!(
        "Querying version page: space={}, name={}, offset={}, limit={}",
        cursor.space, cursor.name, cursor.offset, cursor.limit
    );

    let mut items = state
        .sql_client
        .version_page(&cursor, &table)
        .await
        .map_err(|e| {
            error!("Failed to get version page: {e}");
            internal_server_error(e, "Failed to get version page", None)
        })?;

    let has_next = items.len() > cursor.limit as usize;
    if has_next {
        items.pop();
    }

    let has_previous = !cursor.is_first_page();

    let next_cursor = if has_next { Some(cursor.next()) } else { None };

    let previous_cursor = if has_previous {
        Some(cursor.previous())
    } else {
        None
    };

    debug!(
        "Next cursor: {:?}, Previous cursor: {:?}",
        next_cursor, previous_cursor
    );

    Ok(Json(VersionPageResponse {
        items,
        has_next,
        next_cursor,
        has_previous,
        previous_cursor,
    }))
}

#[utoipa::path(
    get,
    path = "/opsml/api/card/list",
    params(
        ("space" = Option<String>, Query, description = "Filter by space"),
        ("name" = Option<String>, Query, description = "Filter by name"),
        ("version" = Option<String>, Query, description = "Filter by version"),
        ("uid" = Option<String>, Query, description = "Filter by UID"),
        ("tags[]" = Option<Vec<String>>, Query, description = "Filter by tags (repeatable)"),
        ("registry_type" = String, Query, description = "Registry type"),
        ("limit" = Option<i64>, Query, description = "Max results"),
        ("sort_by" = Option<String>, Query, description = "Sort field"),
        ("max_date" = Option<String>, Query, description = "Max date filter"),
    ),
    responses(
        (status = 200, description = "List of cards", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
pub async fn list_cards(
    State(state): State<Arc<AppState>>,
    // CardQueryArgs contains Vec<String> for tags, which serde_qs can parse correctly
    uri: OriginalUri,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    let params: CardQueryArgs = parse_qs_query(&uri)?;

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
            error!("Failed to list cards: {e}");
            internal_server_error(e, "Failed to list cards", None)
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
        CardResults::Skill(data) => {
            Json(data.into_iter().map(convert_skillcard).collect::<Vec<_>>())
        }
        CardResults::SubAgent(data) => Json(
            data.into_iter()
                .map(convert_subagent_card)
                .collect::<Vec<_>>(),
        ),
        CardResults::Tool(data) => {
            Json(data.into_iter().map(convert_tool_card).collect::<Vec<_>>())
        }
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

#[utoipa::path(
    post,
    path = "/opsml/api/card/create",
    request_body(content = inline(serde_json::Value), description = "Card creation request"),
    responses(
        (status = 200, description = "Card created", body = CreateCardResponse),
        (status = 403, description = "Forbidden", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
#[instrument(skip_all)]
pub async fn create_card(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(mut card_request): Json<CreateCardRequest>,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&card_request.registry_type);

    // Override username with the server-verified JWT identity to prevent client-side spoofing.
    if let CardRecord::SubAgent(ref mut r) = card_request.card {
        r.username = perms.username.clone();
    }
    if let CardRecord::Tool(ref mut r) = card_request.card {
        r.username = perms.username.clone();
    }

    if !perms.has_write_permission(card_request.card.space()) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    // Size validation for ToolCard blobs
    const MAX_SCHEMA_BYTES: usize = 64 * 1024;
    if let CardRecord::Tool(ref r) = card_request.card
        && let Some(schema) = &r.args_schema
        && serde_json::to_vec(schema).map(|v| v.len()).unwrap_or(0) > MAX_SCHEMA_BYTES
    {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(OpsmlServerError::new(
                "args_schema exceeds maximum size of 64KB".to_string(),
            )),
        ));
    }

    // Run skill scan gate for SkillCards
    if let CardRecord::Skill(ref skill_record) = card_request.card {
        run_skill_scan(&state, skill_record).await?;
    }

    // Content hash dedup for SkillCards
    if let CardRecord::Skill(ref skill_record) = card_request.card
        && let Some(existing) = state
            .sql_client
            .compare_hash(
                &table,
                &skill_record.content_hash,
                Some(&skill_record.space),
                Some(&skill_record.name),
            )
            .await
            .map_err(|e| internal_server_error(e, "Content hash check failed", None))?
    {
        let key = state
            .sql_client
            .get_artifact_key(&existing.uid, &card_request.registry_type.to_string())
            .await
            .map_err(|e| internal_server_error(e, "Failed to get artifact key", None))?;

        info!(
            "Skill content unchanged, returning existing {}/{}/{}",
            &existing.space, &existing.name, &existing.version
        );

        let mut response = Json(CreateCardResponse {
            registered: true,
            deduplicated: true,
            space: existing.space.clone(),
            name: existing.name.clone(),
            version: existing.version.clone(),
            app_env: existing.app_env,
            created_at: existing.created_at,
            key,
        })
        .into_response();

        let audit_context = AuditContext {
            resource_id: existing.uid,
            resource_type: ResourceType::Database,
            metadata: card_request.get_metadata(),
            registry_type: Some(card_request.registry_type.clone()),
            operation: Operation::Read,
            access_location: None,
        };
        let space_name = SpaceNameEvent {
            space: existing.space,
            name: existing.name,
            registry_type: card_request.registry_type.clone(),
        };
        {
            let extensions = response.extensions_mut();
            extensions.insert(audit_context);
            extensions.insert(space_name);
        }

        return Ok(response);
    }

    // Resolve version and insert (with retry on unique violation for skills)
    let is_skill = matches!(card_request.card, CardRecord::Skill(_));
    let max_retries: u32 = if is_skill { 3 } else { 1 };
    let mut attempt = 0u32;

    let (version, (uid, space, registry_type, card_uri, app_env, created_at)) = loop {
        let version = get_next_version(
            state.sql_client.clone(),
            &table,
            card_request.version_request.clone(),
        )
        .await
        .map_err(|e| {
            error!("Failed to get next version: {e}");
            internal_server_error(e, "Failed to get next version", None)
        })?;

        info!(
            "Creating card: {}/{}/{} - registry: {:?} (attempt {})",
            &card_request.card.space(),
            &card_request.card.name(),
            &version,
            &card_request.registry_type,
            attempt + 1
        );

        match insert_card_into_db(
            state.sql_client.clone(),
            card_request.card.clone(),
            version.clone(),
            &table,
        )
        .await
        {
            Ok(result) => break (version, result),
            Err(e) if e.is_unique_violation() && attempt + 1 < max_retries => {
                attempt += 1;
                warn!(
                    "Version collision for {}/{}, retrying (attempt {}/{})",
                    &card_request.card.space(),
                    &card_request.card.name(),
                    attempt + 1,
                    max_retries
                );

                // For SkillCards: the collision may be a concurrent push of the same content.
                // Re-check the content hash — if a matching row now exists, return it as a
                // dedup hit rather than bumping the version and inserting a duplicate.
                if let CardRecord::Skill(ref skill_record) = card_request.card
                    && let Some(existing) = state
                        .sql_client
                        .compare_hash(
                            &table,
                            &skill_record.content_hash,
                            Some(&skill_record.space),
                            Some(&skill_record.name),
                        )
                        .await
                        .map_err(|e| {
                            internal_server_error(e, "Content hash re-check failed", None)
                        })?
                {
                    // The concurrent inserter may not have called create_artifact_key yet.
                    // Retry the key lookup in a tight inner loop before giving up — a `continue`
                    // here would re-enter `get_next_version` and produce a NEW version for the
                    // same content hash, defeating dedup entirely.
                    let mut key_opt = None;
                    for _ in 0..3u8 {
                        tokio::time::sleep(tokio::time::Duration::from_millis(50)).await;
                        match state
                            .sql_client
                            .get_artifact_key(
                                &existing.uid,
                                &card_request.registry_type.to_string(),
                            )
                            .await
                        {
                            Ok(k) => {
                                key_opt = Some(k);
                                break;
                            }
                            Err(e) if e.is_row_not_found() => continue,
                            Err(e) => {
                                return Err(internal_server_error(
                                    e,
                                    "Failed to get artifact key",
                                    None,
                                ));
                            }
                        }
                    }
                    let key = match key_opt {
                        Some(k) => k,
                        None => {
                            return Err(internal_server_error(
                                "artifact key not available after 3 retries",
                                "Concurrent skill push did not complete; please retry",
                                Some(StatusCode::SERVICE_UNAVAILABLE),
                            ));
                        }
                    };

                    let mut response = Json(CreateCardResponse {
                        registered: true,
                        deduplicated: true,
                        space: existing.space.clone(),
                        name: existing.name.clone(),
                        version: existing.version.clone(),
                        app_env: existing.app_env,
                        created_at: existing.created_at,
                        key,
                    })
                    .into_response();

                    let audit_context = AuditContext {
                        resource_id: existing.uid,
                        resource_type: ResourceType::Database,
                        metadata: card_request.get_metadata(),
                        registry_type: Some(card_request.registry_type.clone()),
                        operation: Operation::Read,
                        access_location: None,
                    };
                    let space_name = SpaceNameEvent {
                        space: existing.space,
                        name: existing.name,
                        registry_type: card_request.registry_type.clone(),
                    };
                    {
                        let extensions = response.extensions_mut();
                        extensions.insert(audit_context);
                        extensions.insert(space_name);
                    }

                    return Ok(response);
                }

                continue;
            }
            Err(e) => {
                error!("Failed to insert card into db: {e}");
                return Err(internal_server_error(
                    e,
                    "Failed to insert card into db",
                    None,
                ));
            }
        }
    };

    // Create the artifact key for card artifact encryption
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
        internal_server_error(e, "Failed to create artifact key", None)
    })?;

    debug!("Card created successfully");

    let mut response = Json(CreateCardResponse {
        registered: true,
        deduplicated: false,
        space: card_request.card.space().to_string(),
        name: card_request.card.name().to_string(),
        version: version.to_string(),
        app_env,
        created_at,
        key,
    })
    .into_response();

    // Create audit and space stats events
    let audit_context = AuditContext {
        resource_id: uid.clone(),
        resource_type: ResourceType::Database,
        metadata: card_request.get_metadata(),
        registry_type: Some(card_request.registry_type.clone()),
        operation: Operation::Create,
        access_location: None,
    };

    // Create space name registry event
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

#[utoipa::path(
    post,
    path = "/opsml/api/card/update",
    request_body(content = inline(serde_json::Value), description = "Card update request"),
    responses(
        (status = 200, description = "Card updated", body = UpdateCardResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
        internal_server_error(e, "Failed to convert card", None)
    })?;

    state
        .sql_client
        .update_card(&table, &card)
        .await
        .map_err(|e| {
            error!("Failed to update card: {e}");
            internal_server_error(e, "Failed to update card", None)
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

#[utoipa::path(
    delete,
    path = "/opsml/api/card/delete",
    params(
        ("uid" = String, Query, description = "Card UID to delete"),
        ("space" = String, Query, description = "Card space"),
        ("registry_type" = String, Query, description = "Registry type"),
    ),
    responses(
        (status = 200, description = "Card deleted", body = UidResponse),
        (status = 403, description = "Forbidden", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
        internal_server_error(e, "Failed to cleanup artifacts", None)
    })?;

    // delete card
    let (space, name) = state
        .sql_client
        .delete_card(&table, &params.uid)
        .await
        .map_err(|e| {
            error!("Failed to delete card: {e}");
            internal_server_error(e, "Failed to delete card", None)
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
            error!("Failed to delete cards: {e}");
            internal_server_error(e, "Failed to delete cards", None)
        })?;

    // If no cards remain in the space, delete the space name record
    if cards.is_empty() {
        state
            .sql_client
            .delete_space_name_record(&space, &name, &params.registry_type)
            .await
            .map_err(|e| {
                error!("Failed to delete space name record: {e}");
                internal_server_error(e, "Failed to delete space name record", None)
            })?;
    }

    Ok(response)
}

#[utoipa::path(
    get,
    path = "/opsml/api/card/load",
    params(
        ("space" = Option<String>, Query, description = "Filter by space"),
        ("name" = Option<String>, Query, description = "Filter by name"),
        ("version" = Option<String>, Query, description = "Filter by version"),
        ("uid" = Option<String>, Query, description = "Filter by UID"),
        ("tags[]" = Option<Vec<String>>, Query, description = "Filter by tags (repeatable)"),
        ("registry_type" = String, Query, description = "Registry type"),
    ),
    responses(
        (status = 200, description = "Artifact key for card loading", body = ArtifactKey),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
#[instrument(skip_all)]
pub async fn load_card(
    State(state): State<Arc<AppState>>,
    uri: OriginalUri,
) -> Result<Json<ArtifactKey>, (StatusCode, Json<OpsmlServerError>)> {
    let params: CardQueryArgs = parse_qs_query(&uri)?;

    let table = CardTable::from_registry_type(&params.registry_type);

    debug!(
        "Loading card with params: space={:?}, name={:?}, version={:?}, uid={:?}, registry_type={:?}, table={:?}",
        params.space, params.name, params.version, params.uid, params.registry_type, table
    );

    let key = state
        .sql_client
        .get_card_key_for_loading(&table, &params)
        .await
        .map_err(|e| {
            error!("Failed to get card key for loading: {e}");
            internal_server_error(e, "Failed to get card key for loading", None)
        })?;

    Ok(Json(key))
}

#[utoipa::path(
    get,
    path = "/opsml/api/card/metadata",
    params(
        ("space" = Option<String>, Query, description = "Filter by space"),
        ("name" = Option<String>, Query, description = "Filter by name"),
        ("version" = Option<String>, Query, description = "Filter by version"),
        ("uid" = Option<String>, Query, description = "Filter by UID"),
        ("tags[]" = Option<Vec<String>>, Query, description = "Filter by tags (repeatable)"),
        ("registry_type" = String, Query, description = "Registry type"),
    ),
    responses(
        (status = 200, description = "Card metadata as JSON", body = inline(serde_json::Value)),
        (status = 403, description = "Forbidden", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
            internal_server_error(e, "Failed to get card key for loading", None)
        })?;

    if !perms.has_read_permission(&key.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    // create temp dir
    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {e}");
        internal_server_error(e, "Failed to create temp dir", None)
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
            internal_server_error(e, "Failed to get card", None)
        })?;

    let decryption_key = key.get_crypt_key().map_err(|e| {
        error!("Failed to get decryption key: {e}");
        internal_server_error(e, "Failed to get decryption key", None)
    })?;

    decrypt_directory(tmp_path, &decryption_key).map_err(|e| {
        error!("Failed to decrypt directory: {e}");
        internal_server_error(e, "Failed to decrypt directory", None)
    })?;

    let card = std::fs::read_to_string(lpath).map_err(|e| {
        error!("Failed to read card from file: {e}");
        internal_server_error(e, "Failed to read card from file", None)
    })?;

    let card = serde_json::from_str(&card).map_err(|e| {
        error!("Failed to parse card: {e}");
        internal_server_error(e, "Failed to parse card", None)
    })?;

    Ok(Json(card))
}

#[utoipa::path(
    get,
    path = "/opsml/api/card/readme",
    params(
        ("space" = Option<String>, Query, description = "Card space"),
        ("name" = Option<String>, Query, description = "Card name"),
        ("version" = Option<String>, Query, description = "Card version"),
        ("uid" = Option<String>, Query, description = "Card UID"),
        ("registry_type" = String, Query, description = "Registry type"),
    ),
    responses(
        (status = 200, description = "Card readme content", body = ReadeMe),
        (status = 403, description = "Forbidden", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
        internal_server_error(e, "Failed to create temp dir", None)
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

#[utoipa::path(
    post,
    path = "/opsml/api/card/readme",
    request_body(content = CreateReadeMe, description = "Readme creation request"),
    responses(
        (status = 200, description = "Readme uploaded", body = UploadResponse),
        (status = 403, description = "Forbidden", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
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
        internal_server_error(e, "Failed to get artifact key", None)
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

#[utoipa::path(
    post,
    path = "/opsml/api/card/compare_hash",
    request_body(content = CompareHashRequest, description = "Content hash comparison request"),
    responses(
        (status = 200, description = "Hash comparison result", body = CompareHashResponse),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "cards"
)]
#[instrument(skip_all)]
pub async fn compare_content_hash(
    State(state): State<Arc<AppState>>,
    Extension(_perms): Extension<UserPermissions>,
    Json(params): Json<CompareHashRequest>,
) -> Result<Json<CompareHashResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let table = CardTable::from_registry_type(&params.registry_type);

    let card = state
        .sql_client
        .compare_hash(
            &table,
            &params.content_hash,
            params.space.as_deref(),
            params.name.as_deref(),
        )
        .await
        .map_err(|e| {
            error!("Failed to compare content hash: {e}");
            internal_server_error(e, "Failed to compare content hash", None)
        })?;

    Ok(Json(CompareHashResponse { card }))
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
            .route(&format!("{prefix}/card/tags"), get(get_registry_tags))
            .route(
                &format!("{prefix}/card/registry/stats"),
                post(retrieve_registry_stats),
            )
            .route(
                &format!("{prefix}/card/dashboard/stats"),
                get(retrieve_dashboard_stats),
            )
            .route(&format!("{prefix}/card/registry/page"), post(retrieve_page))
            .route(
                &format!("{prefix}/card/registry/version/page"),
                post(query_version_page),
            )
            .route(&format!("{prefix}/card/list"), get(list_cards))
            .route(&format!("{prefix}/card/create"), post(create_card))
            .route(&format!("{prefix}/card/load"), get(load_card))
            .route(&format!("{prefix}/card/update"), post(update_card))
            .route(&format!("{prefix}/card/delete"), delete(delete_card))
            .route(
                &format!("{prefix}/card/compare_hash"),
                post(compare_content_hash),
            )
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
