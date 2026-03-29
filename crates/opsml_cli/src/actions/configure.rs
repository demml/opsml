use crate::cli::arg::ConfigureArgs;
use crate::error::CliError;

pub fn configure_cli(_args: &ConfigureArgs) -> Result<(), CliError> {
    Err(CliError::Error(
        "configure not yet implemented — coming in next commit".into(),
    ))
}
