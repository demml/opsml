use opsml_error::ApiError;
use opsml_semver::{VersionArgs, VersionValidator};
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_sql::schemas::*;
use opsml_types::{cards::*, contracts::*};
use semver::Version;
use std::sync::Arc;
use tracing::{error, instrument};

#[instrument(skip_all)]
pub async fn get_next_version(
    sql_client: Arc<SqlClientEnum>,
    table: &CardTable,
    request: CardVersionRequest,
) -> Result<Version, ApiError> {
    let versions = sql_client
        .get_versions(table, &request.repository, &request.name, request.version)
        .await
        .map_err(|e| {
            error!("Failed to get versions: {}", e);
            ApiError::Error("Failed to get versions".to_string())
        })?;

    let version = versions.first().ok_or_else(|| {
        error!("Failed to get first version");
        ApiError::Error("Failed to get first version".to_string())
    })?;

    let args = VersionArgs {
        version: version.to_string(),
        version_type: request.version_type.clone(),
        pre: request.pre_tag,
        build: request.build_tag,
    };

    VersionValidator::bump_version(&args).map_err(|e| {
        error!("Failed to bump version: {}", e);
        ApiError::Error("Failed to bump version".to_string())
    })
}

/// Insert a card into the database
///
/// # Arguments
///
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
    card: Card,
    version: Version,
    table: &CardTable,
) -> Result<(String, String, String), ApiError> {
    // match on registry type
    let card = match card {
        Card::Data(client_card) => {
            let server_card = DataCardRecord::new(
                client_card.name,
                client_card.repository,
                version,
                client_card.contact,
                client_card.tags,
                client_card.data_type,
                client_card.runcard_uid,
                client_card.pipelinecard_uid,
                client_card.auditcard_uid,
                client_card.interface_type,
                client_card.username,
            );
            ServerCard::Data(server_card)
        }
        Card::Model(client_card) => {
            let server_card = ModelCardRecord::new(
                client_card.name,
                client_card.repository,
                version,
                client_card.contact,
                client_card.tags,
                client_card.datacard_uid,
                client_card.data_type,
                client_card.model_type,
                client_card.runcard_uid,
                client_card.pipelinecard_uid,
                client_card.auditcard_uid,
                client_card.interface_type,
                client_card.task_type,
                client_card.username,
            );
            ServerCard::Model(server_card)
        }

        Card::Project(client_card) => {
            let server_card = ProjectCardRecord::new(
                client_card.name,
                client_card.repository,
                version,
                client_card.project_id,
                client_card.username,
            );
            ServerCard::Project(server_card)
        }

        Card::Run(client_card) => {
            let server_card = RunCardRecord::new(
                client_card.name,
                client_card.repository,
                version,
                client_card.contact,
                client_card.tags,
                client_card.datacard_uids,
                client_card.modelcard_uids,
                client_card.pipelinecard_uid,
                client_card.project,
                client_card.artifact_uris,
                client_card.compute_environment,
                client_card.username,
            );
            ServerCard::Run(server_card)
        }

        Card::Pipeline(client_card) => {
            let server_card = PipelineCardRecord::new(
                client_card.name,
                client_card.repository,
                version,
                client_card.contact,
                client_card.tags,
                client_card.pipeline_code_uri,
                client_card.datacard_uids,
                client_card.modelcard_uids,
                client_card.runcard_uids,
                client_card.username,
            );
            ServerCard::Pipeline(server_card)
        }

        Card::Audit(client_card) => {
            let server_card = AuditCardRecord::new(
                client_card.name,
                client_card.repository,
                version,
                client_card.contact,
                client_card.tags,
                client_card.approved,
                client_card.datacard_uids,
                client_card.modelcard_uids,
                client_card.runcard_uids,
                client_card.username,
            );
            ServerCard::Audit(server_card)
        }
    };
    sql_client.insert_card(table, &card).await.map_err(|e| {
        error!("Failed to insert card: {}", e);
        ApiError::Error("Failed to insert card".to_string())
    })?;

    Ok((card.uid().to_string(), card.registry_type(), card.uri()))
}
