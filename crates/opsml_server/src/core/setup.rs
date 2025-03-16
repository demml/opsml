use crate::core::scouter::client::{build_scouter_http_client, ScouterApiClient};
use anyhow::{Context, Result as AnyhowResult};
use opsml_client::RequestType;
use opsml_client::Routes;
use opsml_colors::Colorize;
use opsml_settings::config::{OpsmlConfig, ScouterSettings};
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::{get_sql_client, SqlClientEnum};
use opsml_sql::schemas::User;
use opsml_storage::storage::enums::client::{get_storage_system, StorageClientEnum};
use rusty_logging::setup_logging;
use tracing::{debug, info};

/// Initialize a default admin user if no users exist in the database
pub async fn initialize_default_user(
    sql_client: &SqlClientEnum,
    scouter_client: &mut ScouterApiClient,
) -> AnyhowResult<()> {
    // Check if any users exist
    let users = sql_client
        .get_users()
        .await
        .context(Colorize::purple("❌ Failed to check existing users"))?;

    // If users already exist, don't create a default user
    if !users.is_empty() {
        return Ok(());
    }

    // Create default admin user
    info!("Creating default admin user...");
    let default_username = std::env::var("OPSML_DEFAULT_USERNAME").unwrap_or("admin".to_string());
    let default_password = std::env::var("OPSML_DEFAULT_PASSWORD").unwrap_or("admin".to_string());
    let password_hash = password_auth::generate_hash(&default_password);

    // Create admin user with admin permissions
    let admin_user = User::new(
        default_username.clone(),
        password_hash,
        Some(vec!["read".to_string(), "write".to_string()]), // permissions
        Some(vec!["admin".to_string()]),                     // group_permissions
        Some("admin".to_string()),                           // role
    );

    // Insert the user
    sql_client
        .insert_user(&admin_user)
        .await
        .context(Colorize::purple("❌ Failed to create default admin user"))?;

    // create guest user
    let guest_user = User::new(
        "guest".to_string(),
        password_auth::generate_hash("guest"),
        Some(vec!["read".to_string(), "write:all".to_string()]),
        Some(vec!["user".to_string()]),
        Some("guest".to_string()),
    );

    // Insert the user
    sql_client
        .insert_user(&guest_user)
        .await
        .context(Colorize::purple("❌ Failed to create default guest user"))?;

    info!("✅ Created default admin and guest user (change password on first login)",);

    if scouter_client.enabled {
        // send admin user to scouter
        scouter_client
            .create_initial_user(&admin_user)
            .await
            .context(Colorize::purple(
                "❌ Failed to create default admin in scouter",
            ))?;

        // send guest user to scouter
        scouter_client
            .create_initial_user(&guest_user)
            .await
            .context(Colorize::purple(
                "❌ Failed to create default guest in scouter",
            ))?;

        info!(
            "✅ Created default admin and guest user in Scouter (change password on first login)",
        );
    }

    // if scouter_client is enabled, pass the default user and admin to scouter

    Ok(())
}

pub async fn setup_components() -> AnyhowResult<(
    OpsmlConfig,
    StorageClientEnum,
    SqlClientEnum,
    ScouterApiClient,
)> {
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
    let sql = get_sql_client(&config.database_settings)
        .await
        .context(Colorize::purple("❌ Failed to setup sql client"))?;

    info!("✅ Sql client: {}", sql.name());

    let scouter = setup_scouter_components(&config.scouter_settings)
        .await
        .context(Colorize::purple("❌ Failed to setup scouter client"))?;

    if !scouter.base_path.is_empty() {
        info!("✅ Scouter client: {}", scouter.base_path);
    }

    Ok((config, storage, sql, scouter))
}

pub async fn setup_scouter_components(
    settings: &ScouterSettings,
) -> AnyhowResult<ScouterApiClient> {
    // setup config
    let client = build_scouter_http_client(settings)
        .await
        .context(Colorize::purple("❌ Failed to setup scouter client"))?;

    Ok(client)
}
