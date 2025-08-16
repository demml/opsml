use crate::cli::arg::DownloadCard;
use crate::cli::arg::IntoQueryArgs;
use crate::error::CliError;
use opsml_registry::download::{download_card_from_registry, download_service_from_registry};
use opsml_types::RegistryType;

/// Download all artifacts of a card
///
/// # Arguments
/// * `args` - DownloadCard
/// * `registry_type` - RegistryType
///
/// # Returns
/// None
///
/// # Errors
/// CliError
pub fn download_card(args: &DownloadCard, registry_type: RegistryType) -> Result<(), CliError> {
    // convert to query args
    let query_args = args.into_query_args(registry_type)?;

    // get registry
    download_card_from_registry(&query_args, args.write_path())?;

    Ok(())
}

/// Helper function to download a service when called from the cli
/// # Arguments
/// * `args` - DownloadCard
/// # Returns
/// None
///
/// # Errors
/// CliError
pub fn download_service(args: &DownloadCard) -> Result<(), CliError> {
    // convert to query args
    let query_args = args.into_query_args(RegistryType::Service)?;

    download_service_from_registry(&query_args, args.write_path())?;

    Ok(())
}
