use crate::base::SqlClient;
use crate::enums::client::SqlClientEnum;
use crate::error::SqlError;
use opsml_semver::{VersionArgs, VersionValidator};
use opsml_types::cards::CardTable;
use opsml_types::contracts::*;
use semver::Version;
use std::sync::Arc;
use tracing::{error, instrument};

#[instrument(skip_all)]
pub async fn get_next_version(
    sql_client: Arc<SqlClientEnum>,
    table: &CardTable,
    request: CardVersionRequest,
) -> Result<Version, SqlError> {
    let versions = sql_client
        .get_versions(
            table,
            &request.space,
            &request.name,
            request.version.clone(),
        )
        .await?;

    if versions.is_empty() {
        return match &request.version {
            Some(version_str) => VersionValidator::clean_version(version_str).map_err(|e| {
                error!("Invalid version format: {e}");
                e.into()
            }),
            None => Ok(Version::new(0, 1, 0)),
        };
    }

    // Get the latest version as base for bumping
    let base_version = versions.first().unwrap().to_string();

    let args = VersionArgs {
        version: base_version,
        version_type: request.version_type,
        pre: request.pre_tag,
        build: request.build_tag,
    };

    VersionValidator::bump_version(&args).map_err(|e| {
        error!("Failed to bump version: {e}");
        e.into()
    })
}
