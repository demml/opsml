use crate::core::agentic::agent_route::{get_agent_job, invoke_agent};
use crate::core::agentic::schema::{ArtifactMeta, MapResponse};
use crate::core::error::{OpsmlServerError, internal_server_error};
use crate::core::state::AppState;
use anyhow::Result;
use axum::{
    Extension, Json, Router,
    body::Body,
    extract::{Path, State},
    http::{StatusCode, header},
    response::Response,
    routing::{get, post},
};
use opsml_auth::permission::UserPermissions;
use opsml_cards::SubAgentCard;
use opsml_crypt::decrypt_directory;
use opsml_events::AuditContext;
use opsml_sql::traits::{ArtifactLogicTrait, SkillLogicTrait, SubAgentLogicTrait};
use opsml_types::{
    RegistryType, SaveName, Suffix,
    contracts::{Operation, ResourceType, skill::MarketplaceStats},
};
use std::sync::Arc;
use tempfile::tempdir;
use tracing::{error, instrument, warn};

fn bytes_to_hex(bytes: &[u8]) -> String {
    use std::fmt::Write as _;
    let mut s = String::with_capacity(bytes.len() * 2);
    for b in bytes {
        write!(s, "{b:02x}").expect("write to String is infallible");
    }
    s
}

/// Serve the latest version of a skill as markdown.
#[instrument(skip_all)]
pub async fn get_skill_latest(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path((space, name)): Path<(String, String)>,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_read_permission(&space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let record = state
        .sql_client
        .get_skill_card_by_name(&space, &name)
        .await
        .map_err(|e| {
            error!("Failed to get skill card {space}/{name}: {e}");
            internal_server_error(e, "Skill not found", None)
        })?;

    let markdown = load_skill_markdown(&state, &record.uid).await?;

    if let Err(e) = state
        .sql_client
        .increment_skill_download_count(&record.uid)
        .await
    {
        warn!("Failed to increment download count for {}: {e}", record.uid);
    }

    let mut response = Response::builder()
        .status(StatusCode::OK)
        .header(header::CONTENT_TYPE, "text/markdown; charset=utf-8")
        .header("X-Content-Type-Options", "nosniff")
        .body(Body::from(markdown))
        .map_err(|e| internal_server_error(e, "Failed to build response", None))?;

    response.extensions_mut().insert(AuditContext {
        resource_id: record.uid,
        resource_type: ResourceType::Card,
        metadata: format!("space={space} name={name}"),
        operation: Operation::Read,
        registry_type: Some(RegistryType::Skill),
        access_location: None,
    });

    Ok(response)
}

/// Serve a pinned version of a skill as markdown.
#[instrument(skip_all)]
pub async fn get_skill_pinned(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path((space, name, version)): Path<(String, String, String)>,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_read_permission(&space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let record = state
        .sql_client
        .get_skill_card_by_version(&space, &name, &version)
        .await
        .map_err(|e| {
            error!("Failed to get skill card {space}/{name}/{version}: {e}");
            internal_server_error(e, "Skill not found", None)
        })?;

    let markdown = load_skill_markdown(&state, &record.uid).await?;

    if let Err(e) = state
        .sql_client
        .increment_skill_download_count(&record.uid)
        .await
    {
        warn!("Failed to increment download count for {}: {e}", record.uid);
    }

    let mut response = Response::builder()
        .status(StatusCode::OK)
        .header(header::CONTENT_TYPE, "text/markdown; charset=utf-8")
        .header("X-Content-Type-Options", "nosniff")
        .body(Body::from(markdown))
        .map_err(|e| internal_server_error(e, "Failed to build response", None))?;

    response.extensions_mut().insert(AuditContext {
        resource_id: record.uid,
        resource_type: ResourceType::Card,
        metadata: format!("space={space} name={name} version={version}"),
        operation: Operation::Read,
        registry_type: Some(RegistryType::Skill),
        access_location: None,
    });

    Ok(response)
}

/// List all skills in a space with metadata.
#[instrument(skip_all)]
pub async fn get_skill_map(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(space): Path<String>,
) -> Result<Json<MapResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_read_permission(&space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let records = state
        .sql_client
        .list_skill_cards_by_space(&space)
        .await
        .map_err(|e| {
            error!("Failed to list skills for space {space}: {e}");
            internal_server_error(e, "Failed to list skills", None)
        })?;

    let skills = records
        .into_iter()
        .map(|r| ArtifactMeta {
            name: r.name,
            latest_version: r.version,
            description: r.description,
            etag: bytes_to_hex(&r.content_hash),
            compatible_tools: r.compatible_tools.0,
            download_count: r.download_count,
        })
        .collect();

    let subagent_records = state
        .sql_client
        .list_subagent_cards_by_space(&space)
        .await
        .map_err(|e| {
            error!("Failed to list subagents for space {space}: {e}");
            internal_server_error(e, "Failed to list subagents", None)
        })?;

    let subagents = subagent_records
        .into_iter()
        .map(|r| ArtifactMeta {
            name: r.name,
            latest_version: r.version,
            description: r.description,
            etag: r
                .content_hash
                .as_deref()
                .map(bytes_to_hex)
                .unwrap_or_default(),
            compatible_tools: r.compatible_clis.0,
            download_count: r.download_count,
        })
        .collect();

    Ok(Json(MapResponse {
        space,
        skills,
        subagents,
        tools: vec![],
        agents: vec![],
    }))
}

/// Return top N skills by download count.
#[instrument(skip_all)]
pub async fn get_featured_skills(
    State(state): State<Arc<AppState>>,
    Extension(_perms): Extension<UserPermissions>,
) -> Result<Json<Vec<ArtifactMeta>>, (StatusCode, Json<OpsmlServerError>)> {
    let records = state.sql_client.get_featured_skills(6).await.map_err(|e| {
        error!("Failed to get featured skills: {e}");
        internal_server_error(e, "Failed to get featured skills", None)
    })?;

    let skills = records
        .into_iter()
        .map(|r| ArtifactMeta {
            name: r.name,
            latest_version: r.version,
            description: r.description,
            etag: bytes_to_hex(&r.content_hash),
            compatible_tools: r.compatible_tools.0,
            download_count: r.download_count,
        })
        .collect();

    Ok(Json(skills))
}

/// Return all distinct tags across all skills.
#[instrument(skip_all)]
pub async fn get_all_tags(
    State(state): State<Arc<AppState>>,
    Extension(_perms): Extension<UserPermissions>,
) -> Result<Json<Vec<String>>, (StatusCode, Json<OpsmlServerError>)> {
    let tags = state.sql_client.get_all_skill_tags().await.map_err(|e| {
        error!("Failed to get skill tags: {e}");
        internal_server_error(e, "Failed to get skill tags", None)
    })?;

    Ok(Json(tags))
}

/// Return aggregate marketplace stats.
#[instrument(skip_all)]
pub async fn get_marketplace_stats(
    State(state): State<Arc<AppState>>,
    Extension(_perms): Extension<UserPermissions>,
) -> Result<Json<MarketplaceStats>, (StatusCode, Json<OpsmlServerError>)> {
    let stats = state
        .sql_client
        .get_marketplace_stats()
        .await
        .map_err(|e| {
            error!("Failed to get marketplace stats: {e}");
            internal_server_error(e, "Failed to get marketplace stats", None)
        })?;

    Ok(Json(stats))
}

/// Download, decrypt, and convert a skill card artifact to markdown.
async fn load_skill_markdown(
    state: &Arc<AppState>,
    uid: &str,
) -> Result<String, (StatusCode, Json<OpsmlServerError>)> {
    let registry_type = RegistryType::Skill.to_string();

    let key = state
        .sql_client
        .get_artifact_key(uid, &registry_type)
        .await
        .map_err(|e| {
            error!("Failed to get artifact key for {uid}: {e}");
            internal_server_error(e, "Failed to get artifact key", None)
        })?;

    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {e}");
        internal_server_error(e, "Failed to create temp dir", None)
    })?;

    let tmp_path = tmp_dir.path();
    let lpath = tmp_path.join(SaveName::Card).with_extension(Suffix::Json);
    let rpath = key
        .storage_path()
        .join(SaveName::Card)
        .with_extension(Suffix::Json);

    state
        .storage_client
        .get(&lpath, &rpath, false)
        .await
        .map_err(|e| {
            error!("Failed to download skill artifact for {uid}: {e}");
            internal_server_error(e, "Failed to download skill artifact", None)
        })?;

    let decryption_key = key.get_crypt_key().map_err(|e| {
        error!("Failed to get decryption key for {uid}: {e}");
        internal_server_error(e, "Failed to get decryption key", None)
    })?;

    decrypt_directory(tmp_path, &decryption_key).map_err(|e| {
        error!("Failed to decrypt skill artifact for {uid}: {e}");
        internal_server_error(e, "Failed to decrypt skill artifact", None)
    })?;

    let json_str = std::fs::read_to_string(&lpath).map_err(|e| {
        error!("Failed to read skill artifact for {uid}: {e}");
        internal_server_error(e, "Failed to read skill artifact", None)
    })?;

    let card_value: serde_json::Value = serde_json::from_str(&json_str).map_err(|e| {
        error!("Failed to parse skill card JSON for {uid}: {e}");
        internal_server_error(e, "Failed to parse skill card", None)
    })?;

    let skill: opsml_types::contracts::agent::AgentSkillStandard =
        serde_json::from_value(card_value["skill"].clone()).map_err(|e| {
            error!("Failed to parse AgentSkillStandard for {uid}: {e}");
            internal_server_error(e, "Failed to parse skill", None)
        })?;

    skill.to_markdown().map_err(|e| {
        error!("Failed to convert skill to markdown for {uid}: {e}");
        internal_server_error(e, "Failed to render skill markdown", None)
    })
}

/// Serve the latest version of a subagent as markdown.
#[instrument(skip_all)]
pub async fn get_subagent_latest(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path((space, name)): Path<(String, String)>,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_read_permission(&space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let record = state
        .sql_client
        .get_subagent_card_by_name(&space, &name)
        .await
        .map_err(|e| {
            error!("Failed to get subagent card {space}/{name}: {e}");
            internal_server_error(e, "SubAgent not found", None)
        })?;

    let markdown = load_subagent_markdown(&state, &record.uid).await?;

    if let Err(e) = state
        .sql_client
        .increment_subagent_download_count(&record.uid)
        .await
    {
        warn!("Failed to increment download count for {}: {e}", record.uid);
    }

    let mut response = Response::builder()
        .status(StatusCode::OK)
        .header(header::CONTENT_TYPE, "text/markdown; charset=utf-8")
        .header("X-Content-Type-Options", "nosniff")
        .body(Body::from(markdown))
        .map_err(|e| internal_server_error(e, "Failed to build response", None))?;

    response.extensions_mut().insert(AuditContext {
        resource_id: record.uid,
        resource_type: ResourceType::Card,
        metadata: format!("space={space} name={name}"),
        operation: Operation::Read,
        registry_type: Some(RegistryType::SubAgent),
        access_location: None,
    });

    Ok(response)
}

/// Serve a pinned version of a subagent as markdown.
#[instrument(skip_all)]
pub async fn get_subagent_pinned(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path((space, name, version)): Path<(String, String, String)>,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_read_permission(&space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let record = state
        .sql_client
        .get_subagent_card_by_version(&space, &name, &version)
        .await
        .map_err(|e| {
            error!("Failed to get subagent card {space}/{name}/{version}: {e}");
            internal_server_error(e, "SubAgent not found", None)
        })?;

    let markdown = load_subagent_markdown(&state, &record.uid).await?;

    if let Err(e) = state
        .sql_client
        .increment_subagent_download_count(&record.uid)
        .await
    {
        warn!("Failed to increment download count for {}: {e}", record.uid);
    }

    let mut response = Response::builder()
        .status(StatusCode::OK)
        .header(header::CONTENT_TYPE, "text/markdown; charset=utf-8")
        .header("X-Content-Type-Options", "nosniff")
        .body(Body::from(markdown))
        .map_err(|e| internal_server_error(e, "Failed to build response", None))?;

    response.extensions_mut().insert(AuditContext {
        resource_id: record.uid,
        resource_type: ResourceType::Card,
        metadata: format!("space={space} name={name} version={version}"),
        operation: Operation::Read,
        registry_type: Some(RegistryType::SubAgent),
        access_location: None,
    });

    Ok(response)
}

async fn load_subagent_markdown(
    state: &Arc<AppState>,
    uid: &str,
) -> Result<String, (StatusCode, Json<OpsmlServerError>)> {
    let registry_type = RegistryType::SubAgent.to_string();

    let key = state
        .sql_client
        .get_artifact_key(uid, &registry_type)
        .await
        .map_err(|e| {
            error!("Failed to get artifact key for {uid}: {e}");
            internal_server_error(e, "Failed to get artifact key", None)
        })?;

    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {e}");
        internal_server_error(e, "Failed to create temp dir", None)
    })?;

    let tmp_path = tmp_dir.path();
    let lpath = tmp_path.join(SaveName::Card).with_extension(Suffix::Json);
    let rpath = key
        .storage_path()
        .join(SaveName::Card)
        .with_extension(Suffix::Json);

    state
        .storage_client
        .get(&lpath, &rpath, false)
        .await
        .map_err(|e| {
            error!("Failed to download subagent artifact for {uid}: {e}");
            internal_server_error(e, "Failed to download subagent artifact", None)
        })?;

    let decryption_key = key.get_crypt_key().map_err(|e| {
        error!("Failed to get decryption key for {uid}: {e}");
        internal_server_error(e, "Failed to get decryption key", None)
    })?;

    decrypt_directory(tmp_path, &decryption_key).map_err(|e| {
        error!("Failed to decrypt subagent artifact for {uid}: {e}");
        internal_server_error(e, "Failed to decrypt subagent artifact", None)
    })?;

    let json_str = std::fs::read_to_string(&lpath).map_err(|e| {
        error!("Failed to read subagent artifact for {uid}: {e}");
        internal_server_error(e, "Failed to read subagent artifact", None)
    })?;

    let card = SubAgentCard::model_validate_json(json_str).map_err(|e| {
        error!("Failed to parse SubAgentCard for {uid}: {e}");
        internal_server_error(e, "Failed to parse subagent card", None)
    })?;

    card.to_markdown().map_err(|e| {
        error!("Failed to render subagent markdown for {uid}: {e}");
        internal_server_error(e, "Failed to render subagent markdown", None)
    })
}

pub async fn get_agentic_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let router = Router::new()
        .route(
            &format!("{prefix}/v1/agent/{{id}}/invoke"),
            post(invoke_agent),
        )
        .route(
            &format!("{prefix}/v1/agent/{{id}}/jobs/{{job_id}}"),
            get(get_agent_job),
        )
        .route(
            &format!("{prefix}/v1/skill/{{space}}/{{name}}"),
            get(get_skill_latest),
        )
        .route(
            &format!("{prefix}/v1/skill/{{space}}/{{name}}/{{version}}"),
            get(get_skill_pinned),
        )
        .route(&format!("{prefix}/v1/map/{{space}}"), get(get_skill_map))
        .route(
            &format!("{prefix}/v1/subagent/{{space}}/{{name}}"),
            get(get_subagent_latest),
        )
        .route(
            &format!("{prefix}/v1/subagent/{{space}}/{{name}}/{{version}}"),
            get(get_subagent_pinned),
        )
        .route(
            &format!("{prefix}/v1/marketplace/featured"),
            get(get_featured_skills),
        )
        .route(&format!("{prefix}/v1/marketplace/tags"), get(get_all_tags))
        .route(
            &format!("{prefix}/v1/marketplace/stats"),
            get(get_marketplace_stats),
        );

    Ok(router)
}
