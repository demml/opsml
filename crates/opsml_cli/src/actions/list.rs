use crate::cli::arg::IntoQueryArgs;
use crate::cli::arg::ListCards;
use crate::error::CliError;
use opsml_colors::Colorize;
use opsml_registry::registries::card::OpsmlCardRegistry;
use opsml_types::RegistryType;
use opsml_types::contracts::CardList;

/// List cards from a registry and print them as a table
///
/// # Example
/// opsml-cli list-cards --registry data
///
/// # Arguments
/// * `args` - ListCards
///
/// # Returns
/// Result<(), CliError>
pub fn list_cards(args: &ListCards, registry_type: RegistryType) -> Result<(), CliError> {
    println!(
        "\nListing cards from {} registry",
        Colorize::green(&registry_type.to_string())
    );

    // convert to query args
    let query_args = args.into_query_args(registry_type)?;

    // get registry
    let registry = OpsmlCardRegistry::new(query_args.registry_type.clone())?;

    // list cards
    let cards = registry.list_cards(&query_args)?;

    // print cards
    CardList { cards }.as_table();

    Ok(())
}
