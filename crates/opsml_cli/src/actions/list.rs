use crate::cli::arg::IntoQueryArgs;
use crate::cli::arg::ListCards;
use opsml_colors::Colorize;
use opsml_error::CliError;
use opsml_registry::base::OpsmlRegistry;
use opsml_types::contracts::CardList;

/// List cards from a registry and print them as a table
///
/// # Example
///
/// opsml-cli list-cards --registry data
///
/// # Arguments
///
/// * `args` - ListCards
///
/// # Returns
///
/// Result<(), CliError>å
pub fn list_cards(args: &ListCards) -> Result<(), CliError> {
    println!(
        "\nListing cards from {} registry",
        Colorize::green(&args.registry)
    );

    // convert to query args
    let query_args = args.into_query_args()?;

    // get registry
    let registry = OpsmlRegistry::new(query_args.registry_type.clone())?;

    // list cards
    let cards = registry.list_cards(query_args)?;

    // print cards
    CardList { cards }.as_table();

    Ok(())
}
