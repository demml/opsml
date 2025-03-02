use crate::schemas::schema::{
    CardResults, CardSummary, HardwareMetricsRecord, MetricRecord, ParameterRecord, QueryStats,
    ServerCard, User,
};
use async_trait::async_trait;
use opsml_error::error::SqlError;
use opsml_semver::VersionParser;
use opsml_settings::config::DatabaseSettings;
use opsml_types::{
    cards::CardTable,
    contracts::{ArtifactKey, CardQueryArgs},
};

pub fn add_version_bounds(builder: &mut String, version: &str) -> Result<(), SqlError> {
    let version_bounds = VersionParser::get_version_to_search(version)
        .map_err(|e| SqlError::VersionError(format!("{}", e)))?;

    // construct lower bound (already validated)
    builder.push_str(
        format!(
            " AND (major >= {} AND minor >= {} and patch >= {})",
            version_bounds.lower_bound.major,
            version_bounds.lower_bound.minor,
            version_bounds.lower_bound.patch
        )
        .as_str(),
    );

    if !version_bounds.no_upper_bound {
        // construct upper bound based on number of components
        if version_bounds.num_parts == 1 {
            builder
                .push_str(format!(" AND (major < {})", version_bounds.upper_bound.major).as_str());
        } else if version_bounds.num_parts == 2
            || version_bounds.num_parts == 3 && version_bounds.parser_type == VersionParser::Tilde
            || version_bounds.num_parts == 3 && version_bounds.parser_type == VersionParser::Caret
        {
            builder.push_str(
                format!(
                    " AND (major = {} AND minor < {})",
                    version_bounds.upper_bound.major, version_bounds.upper_bound.minor
                )
                .as_str(),
            );
        } else {
            builder.push_str(
                format!(
                    " AND (major = {} AND minor = {} AND patch < {})",
                    version_bounds.upper_bound.major,
                    version_bounds.upper_bound.minor,
                    version_bounds.upper_bound.patch
                )
                .as_str(),
            );
        }
    }
    Ok(())
}

#[async_trait]
pub trait SqlClient: Sized {
    async fn new(settings: &DatabaseSettings) -> Result<Self, SqlError>;
    async fn run_migrations(&self) -> Result<(), SqlError>;
    async fn get_versions(
        &self,
        table: &CardTable,
        name: &str,
        repository: &str,
        version: Option<String>,
    ) -> Result<Vec<String>, SqlError>;

    async fn query_cards(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<CardResults, SqlError>;

    async fn insert_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError>;
    async fn update_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError>;
    async fn get_unique_repository_names(&self, table: &CardTable)
        -> Result<Vec<String>, SqlError>;
    async fn query_stats(
        &self,
        table: &CardTable,
        search_term: Option<&str>,
    ) -> Result<QueryStats, SqlError>;

    async fn query_page(
        &self,
        sort_by: &str,
        page: i32,
        search_term: Option<&str>,
        repository: Option<&str>,
        table: &CardTable,
    ) -> Result<Vec<CardSummary>, SqlError>;

    async fn delete_card(&self, table: &CardTable, uid: &str) -> Result<(), SqlError>;

    /// Insert run metric
    ///
    /// # Arguments
    ///
    /// * `card` - The metric record
    ///
    /// # Returns
    ///
    async fn insert_experiment_metric(&self, record: &MetricRecord) -> Result<(), SqlError>;

    /// Insert run metrics
    async fn insert_experiment_metrics<'life1>(
        &self,
        record: &'life1 [MetricRecord],
    ) -> Result<(), SqlError>;

    /// insert run parameter
    ///
    /// # Arguments
    ///
    /// * `card` - The parameter record
    ///
    /// # Returns
    ///
    async fn insert_experiment_parameters<'life1>(
        &self,
        records: &'life1 [ParameterRecord],
    ) -> Result<(), SqlError>;

    /// Get run metric
    ///
    /// # Arguments
    ///
    /// * `uid` - The unique identifier of the card
    /// * `names` - The names of the metrics
    ///
    /// # Returns
    ///
    /// * `Vec<MetricRecord>` - The metrics
    ///
    async fn get_experiment_metric<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<MetricRecord>, SqlError>;

    /// Get run metric names
    ///
    /// # Arguments
    ///
    /// * `uid` - The unique identifier of the card
    ///
    /// # Returns
    ///
    /// * `Vec<String>` - The names of the metrics
    ///
    async fn get_experiment_metric_names(&self, uid: &str) -> Result<Vec<String>, SqlError>;

    /// Get run parameter
    ///
    /// # Arguments
    ///
    /// * `uid` - The unique identifier of the card
    /// * `names` - The names of the parameters
    ///
    /// # Returns
    ///
    /// * `Vec<ParameterRecord>` - The parameters
    async fn get_experiment_parameter<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<ParameterRecord>, SqlError>;

    /// Insert hardware metrics
    ///
    /// # Arguments
    ///
    /// * `metric_record` - The hardware metrics
    ///
    async fn insert_hardware_metrics(
        &self,
        records: &HardwareMetricsRecord,
    ) -> Result<(), SqlError>;

    /// Get hardware metrics
    ///
    /// # Arguments
    ///
    /// * `uid` - The unique identifier of the card
    ///
    /// # Returns
    ///
    /// * `HardwareMetricsRecord` - The hardware metrics
    async fn get_hardware_metric(&self, uid: &str) -> Result<Vec<HardwareMetricsRecord>, SqlError>;

    /// Insert user
    ///
    /// # Arguments
    ///
    /// * `user` - The user
    ///
    async fn insert_user(&self, user: &User) -> Result<(), SqlError>;

    /// Get user
    ///
    /// # Arguments
    ///
    /// * `username` - The username
    ///
    /// # Returns
    ///
    /// * `User` - The user
    async fn get_user(&self, username: &str) -> Result<User, SqlError>;

    /// update user
    ///
    /// # Arguments
    ///
    /// * `user` - The user
    ///
    /// # Returns
    ///
    /// * `Result<(), SqlError>` - The result of the operation
    async fn update_user(&self, user: &User) -> Result<(), SqlError>;

    /// Check if uid exists
    ///
    /// # Arguments
    ///
    /// * `uid` - The unique identifier of the card
    /// * `table` - The table to search
    ///
    /// # Returns
    ///
    /// * `bool` - True if the uid exists
    async fn check_uid_exists(&self, uid: &str, table: &CardTable) -> Result<bool, SqlError>;

    /// Insert artifact key
    ///
    /// # Arguments
    ///
    /// * `key` - The artifact key
    ///
    /// # Returns
    async fn insert_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError>;

    /// Get artifact key
    ///
    /// # Arguments
    ///
    /// * `uid` - The unique identifier of the card
    ///
    /// # Returns
    ///
    /// * `ArtifactKey` - The artifact key
    async fn get_artifact_key(
        &self,
        uid: &str,
        registry_type: &str,
    ) -> Result<ArtifactKey, SqlError>;

    /// Update artifact key
    ///
    /// # Arguments
    ///
    /// * `key` - The artifact key
    ///
    ///
    /// # Returns
    ///
    /// * `Result<(), SqlError>` - The result of the operation
    async fn update_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError>;

    /// Insert operation
    ///  Records a given file operation
    ///
    /// # Arguments
    ///
    /// * `username` - The username
    /// * `access_type` - The type of access
    /// * `access_location` - The location of the access
    ///
    /// # Returns
    ///
    /// * `Result<(), SqlError>` - The result of the operation
    async fn insert_operation(
        &self,
        username: &str,
        access_type: &str,
        access_location: &str,
    ) -> Result<(), SqlError>;

    /// Queries the a card registry for a card version and returns
    /// the artifact keys for loading the card on the client side
    ///
    /// # Arguments
    ///
    /// * `table` - The card table
    /// * `query_args` - The query arguments
    ///
    /// # Returns
    ///
    /// * `ArtifactKey` - The artifact key
    async fn get_card_key_for_loading(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<ArtifactKey, SqlError>;

    /// Delete artifact key
    ///
    /// # Arguments
    ///
    /// * `uid` - The unique identifier of the card
    /// * `registry_type` - The card type
    ///
    /// # Returns
    ///
    /// * `Result<(), SqlError>` - The result of the operation
    async fn delete_artifact_key(&self, uid: &str, registry_type: &str) -> Result<(), SqlError>;

    // Add to the SqlClient trait:

    /// Get all users
    ///
    /// # Returns
    ///
    /// * `Vec<User>` - The list of users
    async fn get_users(&self) -> Result<Vec<User>, SqlError>;

    /// Delete a user
    ///
    /// # Arguments
    ///
    /// * `username` - The username of the user to delete
    ///
    /// # Returns
    ///
    /// * `Result<(), SqlError>` - The result of the operation
    async fn delete_user(&self, username: &str) -> Result<(), SqlError>;

    /// Check if a user is the last admin
    ///
    /// # Arguments
    ///
    /// * `username` - The username to check
    ///
    /// # Returns
    ///
    /// * `Result<bool, SqlError>` - True if the user is the last admin
    async fn is_last_admin(&self) -> Result<bool, SqlError>;
}
