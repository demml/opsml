use opsml_error::ApiError;
use opsml_semver::{VersionArgs, VersionValidator};
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_sql::schemas::*;
use opsml_storage::StorageClientEnum;
use opsml_types::cards::CardTable;
use opsml_types::{contracts::*, RegistryType};
use semver::Version;
use sqlx::types::chrono::NaiveDateTime;
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
) -> Result<(String, String, String, String, NaiveDateTime), ApiError> {
    // match on registry type
    let card = match card {
        Card::Data(client_card) => {
            let server_card = DataCardRecord::new(
                client_card.name,
                client_card.repository,
                version,
                client_card.tags,
                client_card.data_type,
                client_card.runcard_uid,
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
                client_card.tags,
                client_card.datacard_uid,
                client_card.data_type,
                client_card.model_type,
                client_card.runcard_uid,
                client_card.auditcard_uid,
                client_card.interface_type,
                client_card.task_type,
                client_card.username,
            );
            ServerCard::Model(server_card)
        }

        Card::Run(client_card) => {
            let server_card = RunCardRecord::new(
                client_card.name,
                client_card.repository,
                version,
                client_card.tags,
                client_card.datacard_uids,
                client_card.modelcard_uids,
                client_card.runcard_uids,
                client_card.username,
            );
            ServerCard::Run(server_card)
        }

        Card::Audit(client_card) => {
            let server_card = AuditCardRecord::new(
                client_card.name,
                client_card.repository,
                version,
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

    Ok((
        card.uid().to_string(),
        card.registry_type(),
        card.uri(),
        card.app_env(),
        card.created_at(),
    ))
}

#[instrument(skip_all)]
pub async fn cleanup_artifacts(
    storage_client: &Arc<StorageClientEnum>,
    sql_client: &Arc<SqlClientEnum>,
    uid: String,
    registry_type: RegistryType,
    table: &CardTable,
) -> Result<(), ApiError> {
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
        .map_err(|e| {
            error!("Failed to get artifact key: {}", e);
            ApiError::Error("Failed to get artifact key".to_string())
        })?;

    storage_client
        .rm(&key.storage_path(), true)
        .await
        .map_err(|e| {
            error!("Failed to remove artifact: {}", e);
            ApiError::Error("Failed to remove artifact".to_string())
        })?;

    sql_client
        .delete_artifact_key(&uid, &registry_type.to_string())
        .await
        .map_err(|e| {
            error!("Failed to delete artifact key: {}", e);
            ApiError::Error("Failed to delete artifact key".to_string())
        })?;

    Ok(())
}
