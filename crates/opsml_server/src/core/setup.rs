use anyhow::{Context, Result as AnyhowResult};
use opsml_colors::Colorize;
use opsml_settings::config::OpsmlConfig;
use opsml_sql::enums::client::{get_sql_client, SqlClientEnum};
use opsml_storage::storage::enums::client::{get_storage_system, StorageClientEnum};
use rusty_logging::setup_logging;
use tracing::{debug, info};

pub async fn setup_components() -> AnyhowResult<(OpsmlConfig, StorageClientEnum, SqlClientEnum)> {
    // setup config
    let config = OpsmlConfig::default();

    // start logging
    let logging = setup_logging(&config.logging_config);

    if logging.is_err() {
        debug!("Failed to setup logging. {:?}", logging.err());
    }

    info!("Starting OpsML Server ....");

    // setup storage client
    let storage = get_storage_system(&config)
        .await
        .context(Colorize::purple("❌ Failed to setup storage client"))?;

    info!("✅ Storage client: {}", storage.name());

    // setup storage client
    let sql = get_sql_client(&config)
        .await
        .context(Colorize::purple("❌ Failed to setup sql client"))?;

    info!("✅ Sql client: {}", sql.name());

    Ok((config, storage, sql))
}
