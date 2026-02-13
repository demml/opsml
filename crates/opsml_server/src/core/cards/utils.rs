use crate::core::cards::schema::InsertCardResponse;
use crate::core::error::ServerError;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_sql::schemas::*;
use opsml_sql::traits::*;
use opsml_storage::StorageClientEnum;
use opsml_types::cards::CardTable;
use opsml_types::{contracts::*, RegistryType};
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
                client_card.promptcard_uids,
                client_card.username,
                client_card.tags,
            );
            ServerCard::Service(server_card)
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
