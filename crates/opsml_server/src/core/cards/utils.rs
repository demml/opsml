use crate::core::cards::schema::InsertCardResponse;
use crate::core::error::{OpsmlServerError, ServerError, internal_server_error};
use crate::core::state::AppState;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_sql::schemas::*;
use opsml_sql::traits::*;
use opsml_storage::StorageClientEnum;
use opsml_types::cards::CardTable;
use opsml_types::contracts::{SkillCardClientRecord, SkillScanResult};
use opsml_types::{RegistryType, contracts::*};
use semver::Version;
use std::sync::Arc;
use tracing::{error, instrument};
/// Insert a card into the database
///
/// # Arguments
/// * `sql_client` - The sql client
/// * `card` - The card to insert
/// * `version` - The version of the card
///
/// # Returns
///
/// The uid of the card
#[instrument(skip_all)]
pub async fn insert_card_into_db(
    sql_client: Arc<SqlClientEnum>,
    card: CardRecord,
    version: Version,
    table: &CardTable,
) -> Result<InsertCardResponse, ServerError> {
    // match on registry type
    let card = match card {
        CardRecord::Data(client_card) => {
            let server_card = DataCardRecord::new(
                client_card.name,
                client_card.space,
                version,
                client_card.tags,
                client_card.data_type,
                client_card.experimentcard_uid,
                client_card.auditcard_uid,
                client_card.interface_type,
                client_card.opsml_version,
                client_card.username,
            );
            ServerCard::Data(server_card)
        }
        CardRecord::Model(client_card) => {
            let server_card = ModelCardRecord::new(
                client_card.name,
                client_card.space,
                version,
                client_card.tags,
                client_card.datacard_uid,
                client_card.data_type,
                client_card.model_type,
                client_card.experimentcard_uid,
                client_card.auditcard_uid,
                client_card.interface_type,
                client_card.task_type,
                client_card.opsml_version,
                client_card.username,
            );
            ServerCard::Model(server_card)
        }

        CardRecord::Experiment(client_card) => {
            let server_card = ExperimentCardRecord::new(
                client_card.name,
                client_card.space,
                version,
                client_card.tags,
                client_card.datacard_uids,
                client_card.modelcard_uids,
                client_card.promptcard_uids,
                client_card.service_card_uids,
                client_card.experimentcard_uids,
                client_card.opsml_version,
                client_card.username,
                client_card.status,
            );
            ServerCard::Experiment(server_card)
        }

        CardRecord::Audit(client_card) => {
            let server_card = AuditCardRecord::new(
                client_card.name,
                client_card.space,
                version,
                client_card.tags,
                client_card.approved,
                client_card.datacard_uids,
                client_card.modelcard_uids,
                client_card.experimentcard_uids,
                client_card.opsml_version,
                client_card.username,
            );
            ServerCard::Audit(server_card)
        }
        CardRecord::Prompt(client_card) => {
            let server_card = PromptCardRecord::new(
                client_card.name,
                client_card.space,
                version,
                client_card.tags,
                client_card.experimentcard_uid,
                client_card.auditcard_uid,
                client_card.opsml_version,
                client_card.username,
                client_card.content_hash,
            );
            ServerCard::Prompt(server_card)
        }

        CardRecord::Service(client_card) => {
            let server_card = ServiceCardRecord::new(
                client_card.name,
                client_card.space,
                version,
                client_card.cards,
                client_card.opsml_version,
                client_card.service_type.to_string(),
                client_card.metadata,
                client_card.deployment,
                client_card.service_config,
                client_card.content_hash,
                client_card.username,
                client_card.tags,
            );
            ServerCard::Service(Box::new(server_card))
        }
        CardRecord::Skill(client_card) => {
            let server_card = SkillCardRecord::new(
                client_card.name,
                client_card.space,
                version,
                client_card.tags,
                client_card.compatible_tools,
                client_card.dependencies,
                client_card.description,
                client_card.license,
                client_card.opsml_version,
                client_card.username,
                client_card.content_hash,
                client_card.input_schema,
            );
            ServerCard::Skill(server_card)
        }
        CardRecord::SubAgent(client_card) => {
            let server_card = SubAgentCardRecord::new(
                client_card.name,
                client_card.space,
                version,
                client_card.tags,
                client_card.compatible_clis,
                client_card.description,
                client_card.opsml_version,
                client_card.username,
                client_card.content_hash,
            );
            ServerCard::SubAgent(server_card)
        }
        CardRecord::Tool(client_card) => {
            let server_card = ToolCardRecord::new(
                client_card.name,
                client_card.space,
                version,
                client_card.tags,
                client_card.tool_type,
                client_card.args_schema,
                client_card.description,
                client_card.opsml_version,
                client_card.username,
                client_card.content_hash,
            );
            ServerCard::Tool(server_card)
        }
    };
    sql_client.insert_card(table, &card).await?;

    Ok((
        card.uid().to_string(),
        card.space().to_string(),
        card.registry_type(),
        card.uri(),
        card.app_env(),
        card.created_at(),
    ))
}

/// Run the skill-scan agent gate. Returns Ok(()) if scan is disabled, body is missing,
/// or the skill is classified Clean. Returns a 422 error response if a Violation is detected.
#[instrument(skip_all)]
pub async fn run_skill_scan(
    state: &Arc<AppState>,
    skill_record: &SkillCardClientRecord,
) -> Result<(), (axum::http::StatusCode, axum::Json<OpsmlServerError>)> {
    if !state.config.agent_settings.skill_scan_enabled {
        return Ok(());
    }

    let Some(body) = &skill_record.body else {
        return Err((
            axum::http::StatusCode::UNPROCESSABLE_ENTITY,
            axum::Json(OpsmlServerError {
                error: "Skill scan is enabled but no body was provided — registration rejected"
                    .to_string(),
            }),
        ));
    };

    let invoke_result = state
        .agent_store
        .invoke("skill-scan", body)
        .await
        .map_err(|e| {
            error!("Skill scan invocation failed: {e}");
            internal_server_error(e, "Skill scan failed", None)
        })?;

    let Some(result_value) = invoke_result.result else {
        return Err((
            axum::http::StatusCode::UNPROCESSABLE_ENTITY,
            axum::Json(OpsmlServerError {
                error: "Skill scan returned no result — registration rejected".to_string(),
            }),
        ));
    };

    let scan = SkillScanResult::from_response_value(result_value).map_err(|e| {
        error!("Failed to parse skill scan result: {e}");
        internal_server_error(e, "Failed to parse scan result", None)
    })?;

    if !scan.passed() {
        return Err((
            axum::http::StatusCode::UNPROCESSABLE_ENTITY,
            axum::Json(OpsmlServerError {
                error: format!(
                    "Skill scan violation: {} — {:?}",
                    scan.reason, scan.findings
                ),
            }),
        ));
    }

    Ok(())
}

#[instrument(skip_all)]
pub async fn cleanup_artifacts(
    storage_client: &Arc<StorageClientEnum>,
    sql_client: &Arc<SqlClientEnum>,
    uid: String,
    registry_type: RegistryType,
    table: &CardTable,
) -> Result<(), ServerError> {
    // get artifact key
    let key = sql_client
        .get_card_key_for_loading(
            table,
            &CardQueryArgs {
                uid: Some(uid.clone()),
                registry_type: registry_type.clone(),
                ..Default::default()
            },
        )
        .await
        .inspect_err(|e| {
            error!("Failed to get artifact key: {e}");
        })?;

    storage_client
        .rm(&key.storage_path(), true)
        .await
        .inspect_err(|e| {
            error!("Failed to remove artifact: {e}");
        })?;

    sql_client
        .delete_artifact_key(&uid, &registry_type.to_string())
        .await
        .inspect_err(|e| {
            error!("Failed to delete artifact key: {e}");
        })?;

    Ok(())
}
