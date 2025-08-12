use crate::base::SqlClient;

use crate::error::SqlError;
use crate::postgres::helper::PostgresQueryHelper;
use crate::schemas::schema::{
    ArtifactSqlRecord, AuditCardRecord, CardResults, CardSummary, DataCardRecord,
    ExperimentCardRecord, HardwareMetricsRecord, MetricRecord, ModelCardRecord, ParameterRecord,
    PromptCardRecord, QueryStats, ServerCard, ServiceCardRecord, SqlSpaceRecord, User,
    VersionResult, VersionSummary,
};
use async_trait::async_trait;
use opsml_semver::VersionValidator;
use opsml_settings::config::DatabaseSettings;
use opsml_types::{
    cards::CardTable,
    contracts::{
        ArtifactKey, ArtifactQueryArgs, ArtifactRecord, AuditEvent, CardQueryArgs, SpaceNameEvent,
        SpaceRecord, SpaceStats,
    },
    RegistryType,
};
use semver::Version;
use sqlx::ConnectOptions;
use sqlx::{
    postgres::{PgConnectOptions, PgPoolOptions, PgRow, Postgres},
    FromRow, Pool, Row,
};
use tracing::debug;

impl FromRow<'_, PgRow> for User {
    fn from_row(row: &PgRow) -> Result<Self, sqlx::Error> {
        let id = row.try_get("id")?;
        let created_at = row.try_get("created_at")?;
        let updated_at = row.try_get("updated_at")?;
        let active = row.try_get("active")?;
        let username = row.try_get("username")?;
        let password_hash = row.try_get("password_hash")?;
        let email = row.try_get("email")?;
        let role = row.try_get("role")?;
        let refresh_token = row.try_get("refresh_token")?;
        let authentication_type: String = row.try_get("authentication_type")?;

        let group_permissions: Vec<String> =
            serde_json::from_value(row.try_get("group_permissions")?).unwrap_or_default();

        let permissions: Vec<String> =
            serde_json::from_value(row.try_get("permissions")?).unwrap_or_default();

        let hashed_recovery_codes: Vec<String> =
            serde_json::from_value(row.try_get("hashed_recovery_codes")?).unwrap_or_default();

        let favorite_spaces: Vec<String> =
            serde_json::from_value(row.try_get("favorite_spaces")?).unwrap_or_default();

        Ok(User {
            id,
            created_at,
            updated_at,
            active,
            username,
            password_hash,
            email,
            role,
            refresh_token,
            hashed_recovery_codes,
            permissions,
            group_permissions,
            favorite_spaces,
            authentication_type,
        })
    }
}

#[derive(Debug, Clone)]
pub struct PostgresClient {
    pub pool: Pool<Postgres>,
}

#[async_trait]
impl SqlClient for PostgresClient {
    async fn new(settings: &DatabaseSettings) -> Result<Self, SqlError> {
        let mut opts: PgConnectOptions = settings.connection_uri.parse()?;

        opts = opts.log_statements(tracing::log::LevelFilter::Off);

        let pool = PgPoolOptions::new()
            .max_connections(settings.max_connections)
            .connect_with(opts)
            .await
            .map_err(SqlError::ConnectionError)?;

        let client = Self { pool };

        // run migrations
        client.run_migrations().await?;

        Ok(client)
    }

    async fn run_migrations(&self) -> Result<(), SqlError> {
        debug!("Running migrations");
        sqlx::migrate!("src/postgres/migrations")
            .run(&self.pool)
            .await
            .map_err(SqlError::MigrationError)?;

        Ok(())
    }

    /// Check if uid exists in the database for a table
    ///
    /// # Arguments
    ///
    /// * `table` - The table to query
    /// * `uid` - The uid to check
    ///
    /// # Returns
    ///
    /// * `bool` - True if the uid exists, false otherwise
    async fn check_uid_exists(&self, uid: &str, table: &CardTable) -> Result<bool, SqlError> {
        let query = PostgresQueryHelper::get_uid_query(table);
        let exists: Option<String> = sqlx::query_scalar(&query)
            .bind(uid)
            .fetch_optional(&self.pool)
            .await?;

        Ok(exists.is_some())
    }

    /// Primary query for retrieving versions from the database. Mainly used to get most recent version when determining version increment
    ///
    /// # Arguments
    ///
    /// * `table` - The table to query
    /// * `name` - The name of the card
    /// * `space` - The space of the card
    /// * `version` - The version of the card
    ///
    /// # Returns
    ///
    /// * `Vec<String>` - A vector of strings representing the sorted (desc) versions of the card
    async fn get_versions(
        &self,
        table: &CardTable,
        space: &str,
        name: &str,
        version: Option<String>,
    ) -> Result<Vec<String>, SqlError> {
        // if version is None, get the latest version
        let query = PostgresQueryHelper::get_versions_query(table, version)?;

        let cards: Vec<VersionResult> = sqlx::query_as(&query)
            .bind(space)
            .bind(name)
            .fetch_all(&self.pool)
            .await?;

        let versions = cards
            .iter()
            .map(|c| c.to_version())
            .collect::<Result<Vec<Version>, SqlError>>()?;

        // sort semvers
        Ok(VersionValidator::sort_semver_versions(versions, true)?)
    }

    /// Query cards based on the query arguments
    ///
    /// # Arguments
    ///
    /// * `table` - The table to query
    /// * `query_args` - The query arguments
    ///
    /// # Returns
    ///
    /// * `CardResults` - The results of the query
    async fn query_cards(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<CardResults, SqlError> {
        let query = PostgresQueryHelper::get_query_cards_query(table, query_args)?;

        match table {
            CardTable::Data => {
                let card: Vec<DataCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.space.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await?;

                return Ok(CardResults::Data(card));
            }
            CardTable::Model => {
                let card: Vec<ModelCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.space.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await?;

                return Ok(CardResults::Model(card));
            }
            CardTable::Experiment => {
                let card: Vec<ExperimentCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.space.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await?;

                return Ok(CardResults::Experiment(card));
            }

            CardTable::Audit => {
                let card: Vec<AuditCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.space.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await?;

                return Ok(CardResults::Audit(card));
            }

            CardTable::Prompt => {
                let card: Vec<PromptCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.space.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await?;

                return Ok(CardResults::Prompt(card));
            }

            CardTable::Service => {
                let card: Vec<ServiceCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.space.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await?;

                return Ok(CardResults::Service(card));
            }
            _ => {
                return Err(SqlError::InvalidTableName);
            }
        }
    }
    async fn insert_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError> {
        match table {
            CardTable::Data => match card {
                ServerCard::Data(record) => {
                    let query = PostgresQueryHelper::get_datacard_insert_query();
                    sqlx::query(&query)
                        .bind(&record.uid)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.data_type)
                        .bind(&record.interface_type)
                        .bind(&record.tags)
                        .bind(&record.experimentcard_uid)
                        .bind(&record.auditcard_uid)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },
            CardTable::Model => match card {
                ServerCard::Model(record) => {
                    let query = PostgresQueryHelper::get_modelcard_insert_query();
                    sqlx::query(&query)
                        .bind(&record.uid)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.datacard_uid)
                        .bind(&record.data_type)
                        .bind(&record.model_type)
                        .bind(&record.interface_type)
                        .bind(&record.task_type)
                        .bind(&record.tags)
                        .bind(&record.experimentcard_uid)
                        .bind(&record.auditcard_uid)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },
            CardTable::Experiment => match card {
                ServerCard::Experiment(record) => {
                    let query = PostgresQueryHelper::get_experimentcard_insert_query();
                    sqlx::query(&query)
                        .bind(&record.uid)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.tags)
                        .bind(&record.datacard_uids)
                        .bind(&record.modelcard_uids)
                        .bind(&record.promptcard_uids)
                        .bind(&record.service_card_uids)
                        .bind(&record.experimentcard_uids)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },
            CardTable::Audit => match card {
                ServerCard::Audit(record) => {
                    let query = PostgresQueryHelper::get_auditcard_insert_query();
                    sqlx::query(&query)
                        .bind(&record.uid)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.tags)
                        .bind(record.approved)
                        .bind(&record.datacard_uids)
                        .bind(&record.modelcard_uids)
                        .bind(&record.experimentcard_uids)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }

                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            CardTable::Prompt => match card {
                ServerCard::Prompt(record) => {
                    let query = PostgresQueryHelper::get_promptcard_insert_query();
                    sqlx::query(&query)
                        .bind(&record.uid)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.tags)
                        .bind(&record.experimentcard_uid)
                        .bind(&record.auditcard_uid)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }

                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },
            CardTable::Service => match card {
                ServerCard::Service(record) => {
                    let query = PostgresQueryHelper::get_servicecard_insert_query();
                    sqlx::query(&query)
                        .bind(&record.uid)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.cards)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            _ => {
                return Err(SqlError::InvalidTableName);
            }
        }
    }

    async fn insert_artifact_record(&self, record: &ArtifactSqlRecord) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_artifact_record_insert_query();
        sqlx::query(&query)
            .bind(&record.uid)
            .bind(record.created_at)
            .bind(&record.app_env)
            .bind(&record.space)
            .bind(&record.name)
            .bind(record.major)
            .bind(record.minor)
            .bind(record.patch)
            .bind(&record.pre_tag)
            .bind(&record.build_tag)
            .bind(&record.version)
            .bind(&record.media_type)
            .execute(&self.pool)
            .await?;
        Ok(())
    }

    async fn query_artifacts(
        &self,
        query_args: &ArtifactQueryArgs,
    ) -> Result<Vec<ArtifactRecord>, SqlError> {
        let query = PostgresQueryHelper::get_query_artifacts_query(query_args)?;
        let rows: Vec<ArtifactSqlRecord> = sqlx::query_as(&query)
            .bind(query_args.uid.as_ref())
            .bind(query_args.artifact_type.as_ref().map(|a| a.to_string()))
            .bind(query_args.space.as_ref())
            .bind(query_args.name.as_ref())
            .bind(query_args.limit.unwrap_or(50))
            .fetch_all(&self.pool)
            .await?;

        Ok(rows
            .iter()
            .map(|r| r.to_artifact_record())
            .collect::<Vec<ArtifactRecord>>())
    }

    async fn update_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError> {
        match table {
            CardTable::Data => match card {
                ServerCard::Data(record) => {
                    let query = PostgresQueryHelper::get_datacard_update_query();
                    sqlx::query(&query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.data_type)
                        .bind(&record.interface_type)
                        .bind(&record.tags)
                        .bind(&record.experimentcard_uid)
                        .bind(&record.auditcard_uid)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(&record.uid)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },
            CardTable::Model => match card {
                ServerCard::Model(record) => {
                    let query = PostgresQueryHelper::get_modelcard_update_query();
                    sqlx::query(&query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.datacard_uid)
                        .bind(&record.data_type)
                        .bind(&record.model_type)
                        .bind(&record.interface_type)
                        .bind(&record.task_type)
                        .bind(&record.tags)
                        .bind(&record.experimentcard_uid)
                        .bind(&record.auditcard_uid)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(&record.uid)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },
            CardTable::Experiment => match card {
                ServerCard::Experiment(record) => {
                    let query = PostgresQueryHelper::get_experimentcard_update_query();
                    sqlx::query(&query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.tags)
                        .bind(&record.datacard_uids)
                        .bind(&record.modelcard_uids)
                        .bind(&record.promptcard_uids)
                        .bind(&record.service_card_uids)
                        .bind(&record.experimentcard_uids)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(&record.uid)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },
            CardTable::Audit => match card {
                ServerCard::Audit(record) => {
                    let query = PostgresQueryHelper::get_auditcard_update_query();
                    sqlx::query(&query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.tags)
                        .bind(record.approved)
                        .bind(&record.datacard_uids)
                        .bind(&record.modelcard_uids)
                        .bind(&record.experimentcard_uids)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(&record.uid)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            CardTable::Prompt => match card {
                ServerCard::Prompt(record) => {
                    let query = PostgresQueryHelper::get_promptcard_update_query();
                    sqlx::query(&query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.tags)
                        .bind(&record.experimentcard_uid)
                        .bind(&record.auditcard_uid)
                        .bind(&record.pre_tag)
                        .bind(&record.build_tag)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(&record.uid)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }

                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            CardTable::Service => match card {
                ServerCard::Service(record) => {
                    let query = PostgresQueryHelper::get_servicecard_update_query();
                    sqlx::query(&query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(record.major)
                        .bind(record.minor)
                        .bind(record.patch)
                        .bind(&record.version)
                        .bind(&record.cards)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(&record.uid)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            _ => {
                return Err(SqlError::InvalidTableName);
            }
        }
    }

    /// Get unique space names
    ///
    /// # Arguments
    ///
    /// * `table` - The table to query
    ///
    /// # Returns
    ///
    /// * `Vec<String>` - A vector of unique space names
    async fn get_unique_space_names(&self, table: &CardTable) -> Result<Vec<String>, SqlError> {
        let query = format!("SELECT DISTINCT space FROM {table}");
        let repos: Vec<String> = sqlx::query_scalar(&query).fetch_all(&self.pool).await?;

        Ok(repos)
    }

    async fn query_stats(
        &self,
        table: &CardTable,
        search_term: Option<&str>,
        space: Option<&str>,
    ) -> Result<QueryStats, SqlError> {
        let query = PostgresQueryHelper::get_query_stats_query(table);

        // if search_term is not None, format with %search_term%, else None
        let stats: QueryStats = sqlx::query_as(&query)
            .bind(search_term.map(|term| format!("%{term}%")))
            .bind(space)
            .fetch_one(&self.pool)
            .await?;

        Ok(stats)
    }

    /// Query a page of cards
    ///
    /// # Arguments
    ///
    /// * `sort_by` - The field to sort by
    /// * `page` - The page number
    /// * `search_term` - The search term to query
    /// * `space` - The space to query
    /// * `table` - The table to query
    ///
    /// # Returns
    ///
    /// * `Vec<CardSummary>` - A vector of card summaries
    async fn query_page(
        &self,
        sort_by: &str,
        page: i32,
        search_term: Option<&str>,
        space: Option<&str>,
        table: &CardTable,
    ) -> Result<Vec<CardSummary>, SqlError> {
        let query = PostgresQueryHelper::get_query_page_query(table, sort_by);

        let lower_bound = (page * 30) - 30;
        let upper_bound = page * 30;

        let records: Vec<CardSummary> = sqlx::query_as(&query)
            .bind(space)
            .bind(search_term)
            .bind(search_term.map(|term| format!("%{term}%")))
            .bind(lower_bound)
            .bind(upper_bound)
            .fetch_all(&self.pool)
            .await?;

        Ok(records)
    }

    async fn version_page(
        &self,
        page: i32,
        space: Option<&str>,
        name: Option<&str>,
        table: &CardTable,
    ) -> Result<Vec<VersionSummary>, SqlError> {
        let query = PostgresQueryHelper::get_version_page_query(table);

        let lower_bound = (page * 30) - 30;
        let upper_bound = page * 30;

        let records: Vec<VersionSummary> = sqlx::query_as(&query)
            .bind(space)
            .bind(name)
            .bind(lower_bound)
            .bind(upper_bound)
            .fetch_all(&self.pool)
            .await?;

        Ok(records)
    }

    async fn delete_card(
        &self,
        table: &CardTable,
        uid: &str,
    ) -> Result<(String, String), SqlError> {
        // First get the space
        let query = format!("DELETE FROM {table} WHERE uid = $1 RETURNING space, name");
        let (space, name): (String, String) = sqlx::query_as(&query)
            .bind(uid)
            .fetch_one(&self.pool)
            .await?;

        Ok((space, name))
    }

    async fn insert_experiment_metric(&self, record: &MetricRecord) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_experiment_metric_insert_query();
        sqlx::query(&query)
            .bind(&record.experiment_uid)
            .bind(&record.name)
            .bind(record.value)
            .bind(record.step)
            .bind(record.timestamp)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn insert_experiment_metrics<'life1>(
        &self,
        records: &'life1 [MetricRecord],
    ) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_experiment_metrics_insert_query(records.len());

        let mut query_builder = sqlx::query(&query);

        for r in records {
            query_builder = query_builder
                .bind(&r.experiment_uid)
                .bind(&r.name)
                .bind(r.value)
                .bind(r.step)
                .bind(r.timestamp);
        }

        query_builder.execute(&self.pool).await?;

        Ok(())
    }

    async fn get_experiment_metric<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<MetricRecord>, SqlError> {
        let (query, bindings) = PostgresQueryHelper::get_experiment_metric_query(names);
        let mut query_builder = sqlx::query_as::<sqlx::Postgres, MetricRecord>(&query).bind(uid);

        for binding in bindings {
            query_builder = query_builder.bind(binding);
        }

        let records: Vec<MetricRecord> = query_builder.fetch_all(&self.pool).await?;

        Ok(records)
    }

    async fn get_experiment_metric_names(&self, uid: &str) -> Result<Vec<String>, SqlError> {
        let query = format!(
            "SELECT DISTINCT name FROM {} WHERE experiment_uid = $1",
            CardTable::Metrics
        );

        let records: Vec<String> = sqlx::query_scalar(&query)
            .bind(uid)
            .fetch_all(&self.pool)
            .await?;

        Ok(records)
    }

    async fn insert_hardware_metrics(
        &self,
        record: &HardwareMetricsRecord,
    ) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_hardware_metrics_insert_query();

        sqlx::query(&query)
            .bind(&record.experiment_uid)
            .bind(record.created_at)
            .bind(record.cpu_percent_utilization)
            .bind(&record.cpu_percent_per_core)
            .bind(record.free_memory)
            .bind(record.total_memory)
            .bind(record.used_memory)
            .bind(record.available_memory)
            .bind(record.used_percent_memory)
            .bind(record.bytes_recv)
            .bind(record.bytes_sent)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_hardware_metric(&self, uid: &str) -> Result<Vec<HardwareMetricsRecord>, SqlError> {
        let query = PostgresQueryHelper::get_hardware_metric_query();

        let records: Vec<HardwareMetricsRecord> = sqlx::query_as(&query)
            .bind(uid)
            .fetch_all(&self.pool)
            .await?;

        Ok(records)
    }

    async fn insert_experiment_parameters<'life1>(
        &self,
        records: &'life1 [ParameterRecord],
    ) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_experiment_parameters_insert_query(records.len());

        let mut query_builder = sqlx::query(&query);

        for record in records {
            query_builder = query_builder
                .bind(&record.experiment_uid)
                .bind(&record.name)
                .bind(&record.value);
        }

        query_builder.execute(&self.pool).await?;

        Ok(())
    }

    async fn get_experiment_parameter<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<ParameterRecord>, SqlError> {
        let (query, bindings) = PostgresQueryHelper::get_experiment_parameter_query(names);
        let mut query_builder = sqlx::query_as::<_, ParameterRecord>(&query).bind(uid);

        for binding in bindings {
            query_builder = query_builder.bind(binding);
        }

        let records: Vec<ParameterRecord> = query_builder.fetch_all(&self.pool).await?;

        Ok(records)
    }

    async fn insert_user(&self, user: &User) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_user_insert_query();

        let hashed_recovery_codes = serde_json::to_value(&user.hashed_recovery_codes)?;
        let group_permissions = serde_json::to_value(&user.group_permissions)?;
        let permissions = serde_json::to_value(&user.permissions)?;
        let favorite_spaces = serde_json::to_value(&user.favorite_spaces)?;

        sqlx::query(&query)
            .bind(&user.username)
            .bind(&user.password_hash)
            .bind(&hashed_recovery_codes)
            .bind(&permissions)
            .bind(&group_permissions)
            .bind(&favorite_spaces)
            .bind(&user.role)
            .bind(user.active)
            .bind(&user.email)
            .bind(&user.authentication_type)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_user(
        &self,
        username: &str,
        auth_type: Option<&str>,
    ) -> Result<Option<User>, SqlError> {
        let query = match auth_type {
            Some(_) => PostgresQueryHelper::get_user_query_by_auth_type(),
            None => PostgresQueryHelper::get_user_query(),
        };

        let mut query_builder = sqlx::query_as(&query).bind(username);

        if let Some(auth_type) = auth_type {
            query_builder = query_builder.bind(auth_type);
        }

        let user: Option<User> = query_builder.fetch_optional(&self.pool).await?;

        Ok(user)
    }

    async fn update_user(&self, user: &User) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_user_update_query();

        let hashed_recovery_codes = serde_json::to_value(&user.hashed_recovery_codes)?;
        let group_permissions = serde_json::to_value(&user.group_permissions)?;
        let permissions = serde_json::to_value(&user.permissions)?;
        let favorite_spaces = serde_json::to_value(&user.favorite_spaces)?;

        sqlx::query(&query)
            .bind(user.active)
            .bind(&user.password_hash)
            .bind(&hashed_recovery_codes)
            .bind(&permissions)
            .bind(&group_permissions)
            .bind(&favorite_spaces)
            .bind(&user.refresh_token)
            .bind(&user.email)
            .bind(&user.authentication_type)
            .bind(&user.username)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_users(&self) -> Result<Vec<User>, SqlError> {
        let query = PostgresQueryHelper::get_users_query();

        let users = sqlx::query_as::<_, User>(&query)
            .fetch_all(&self.pool)
            .await?;

        Ok(users)
    }

    async fn is_last_admin(&self, username: &str) -> Result<bool, SqlError> {
        // Count admins in the system
        let query = PostgresQueryHelper::get_last_admin_query();

        let admins: Vec<String> = sqlx::query_scalar(&query).fetch_all(&self.pool).await?;

        // If there are no other admins, this is the last one
        if admins.len() > 1 {
            return Ok(false);
        }

        // no admins found
        if admins.is_empty() {
            return Ok(false);
        }

        // check if the username is the last admin
        Ok(admins.len() == 1 && admins[0] == username)
    }

    async fn delete_user(&self, username: &str) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_user_delete_query();

        sqlx::query(&query)
            .bind(username)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn insert_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_artifact_key_insert_query();

        sqlx::query(&query)
            .bind(&key.uid)
            .bind(&key.space)
            .bind(key.registry_type.to_string())
            .bind(key.encrypted_key.clone())
            .bind(&key.storage_key)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_artifact_key(
        &self,
        uid: &str,
        registry_type: &str,
    ) -> Result<ArtifactKey, SqlError> {
        let query = PostgresQueryHelper::get_artifact_key_select_query();

        let key: (String, String, String, Vec<u8>, String) = sqlx::query_as(&query)
            .bind(uid)
            .bind(registry_type)
            .fetch_one(&self.pool)
            .await?;

        Ok(ArtifactKey {
            uid: key.0,
            space: key.1,
            registry_type: RegistryType::from_string(&key.2)?,
            encrypted_key: key.3,
            storage_key: key.4,
        })
    }

    async fn get_artifact_key_from_path(
        &self,
        storage_path: &str,
        registry_type: &str,
    ) -> Result<Option<ArtifactKey>, SqlError> {
        let query = PostgresQueryHelper::get_artifact_key_from_storage_path_query();

        let key: Option<(String, String, String, Vec<u8>, String)> = sqlx::query_as(&query)
            .bind(storage_path)
            .bind(registry_type)
            .fetch_optional(&self.pool)
            .await?;

        return match key {
            Some(k) => Ok(Some(ArtifactKey {
                uid: k.0,
                space: k.1,
                registry_type: RegistryType::from_string(&k.2)?,
                encrypted_key: k.3,
                storage_key: k.4,
            })),
            None => Ok(None),
        };
    }

    async fn update_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_artifact_key_update_query();
        sqlx::query(&query)
            .bind(key.encrypted_key.clone())
            .bind(&key.uid)
            .bind(key.registry_type.to_string())
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn insert_audit_event(&self, event: AuditEvent) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_audit_event_insert_query();
        sqlx::query(&query)
            .bind(event.username)
            .bind(event.client_ip)
            .bind(event.user_agent)
            .bind(event.operation.to_string())
            .bind(event.resource_type.to_string())
            .bind(event.resource_id)
            .bind(event.access_location)
            .bind(event.status.to_string())
            .bind(event.error_message)
            .bind(event.metadata)
            .bind(event.registry_type.map(|r| r.to_string()))
            .bind(event.route)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_card_key_for_loading(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<ArtifactKey, SqlError> {
        let query = PostgresQueryHelper::get_load_card_query(table, query_args)?;

        let key: (String, String, String, Vec<u8>, String) = sqlx::query_as(&query)
            .bind(query_args.uid.as_ref())
            .bind(query_args.name.as_ref())
            .bind(query_args.space.as_ref())
            .bind(query_args.max_date.as_ref())
            .bind(query_args.limit.unwrap_or(1))
            .fetch_one(&self.pool)
            .await?;

        Ok(ArtifactKey {
            uid: key.0,
            space: key.1,
            registry_type: RegistryType::from_string(&key.2)?,
            encrypted_key: key.3,
            storage_key: key.4,
        })
    }

    async fn delete_artifact_key(&self, uid: &str, registry_type: &str) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_artifact_key_delete_query();
        sqlx::query(&query)
            .bind(uid)
            .bind(registry_type)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn insert_space_record(&self, space: &SpaceRecord) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_insert_space_record_query();
        sqlx::query(&query)
            .bind(&space.space)
            .bind(&space.description)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn insert_space_name_record(&self, event: &SpaceNameEvent) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_insert_space_name_record_query();
        sqlx::query(&query)
            .bind(&event.space)
            .bind(&event.name)
            .bind(event.registry_type.to_string())
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_all_space_stats(&self) -> Result<Vec<SpaceStats>, SqlError> {
        let query = PostgresQueryHelper::get_all_space_stats_query();
        let spaces: Vec<SqlSpaceRecord> = sqlx::query_as(&query).fetch_all(&self.pool).await?;

        Ok(spaces
            .into_iter()
            .map(|s| SpaceStats {
                space: s.0,
                model_count: s.1,
                data_count: s.2,
                prompt_count: s.3,
                experiment_count: s.4,
            })
            .collect())
    }

    async fn get_space_record(&self, space: &str) -> Result<Option<SpaceRecord>, SqlError> {
        let query = PostgresQueryHelper::get_space_record_query();
        let record: Option<(String, String)> = sqlx::query_as(&query)
            .bind(space)
            .fetch_optional(&self.pool)
            .await?;

        Ok(record.map(|r| SpaceRecord {
            space: r.0,
            description: r.1,
        }))
    }

    async fn update_space_record(&self, space: &SpaceRecord) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_update_space_record_query();
        sqlx::query(&query)
            .bind(&space.description)
            .bind(&space.space)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn delete_space_record(&self, space: &str) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_delete_space_record_query();
        sqlx::query(&query).bind(space).execute(&self.pool).await?;

        Ok(())
    }

    async fn delete_space_name_record(
        &self,
        space: &str,
        name: &str,
        registry_type: &RegistryType,
    ) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_delete_space_name_record_query();
        sqlx::query(&query)
            .bind(space)
            .bind(name)
            .bind(registry_type.to_string())
            .execute(&self.pool)
            .await?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {

    use crate::schemas::ServiceCardRecord;

    use super::*;
    use opsml_types::{contracts::ArtifactType, CommonKwargs, RegistryType, SqlType};
    use opsml_utils::utils::get_utc_datetime;
    use std::{env, vec};

    const SPACE: &str = "my_space";
    pub async fn cleanup(pool: &Pool<Postgres>) {
        sqlx::raw_sql(
            r#"
            DELETE 
            FROM opsml_data_registry;

            DELETE 
            FROM opsml_model_registry;

            DELETE
            FROM opsml_experiment_registry;

            DELETE
            FROM opsml_audit_registry;

            DELETE
            FROM opsml_experiment_metric;

            DELETE
            FROM opsml_experiment_hardware_metric;

            DELETE
            FROM opsml_experiment_parameter;

            DELETE
            FROM opsml_prompt_registry;

            DELETE
            FROM opsml_user;

            DELETE
            FROM opsml_artifact_key;

            DELETE
            FROM opsml_audit_event;

            DELETE
            FROM opsml_service_registry;

            DELETE
            FROM opsml_artifact_registry;

            DELETE
            FROM opsml_space;
            "#,
        )
        .fetch_all(pool)
        .await
        .unwrap();
    }

    async fn test_card_crud(
        client: &PostgresClient,
        table: &CardTable,
        updated_name: &str,
    ) -> Result<(), SqlError> {
        // Create initial card
        let card = match table {
            CardTable::Data => ServerCard::Data(DataCardRecord::default()),
            CardTable::Model => ServerCard::Model(ModelCardRecord::default()),
            CardTable::Experiment => ServerCard::Experiment(ExperimentCardRecord::default()),
            CardTable::Audit => ServerCard::Audit(AuditCardRecord::default()),
            CardTable::Prompt => ServerCard::Prompt(PromptCardRecord::default()),
            CardTable::Service => ServerCard::Service(ServiceCardRecord::default()),
            _ => panic!("Invalid card type"),
        };

        // Get UID for queries
        let uid = match &card {
            ServerCard::Data(c) => c.uid.clone(),
            ServerCard::Model(c) => c.uid.clone(),
            ServerCard::Experiment(c) => c.uid.clone(),
            ServerCard::Audit(c) => c.uid.clone(),
            ServerCard::Prompt(c) => c.uid.clone(),
            ServerCard::Service(c) => c.uid.clone(),
        };

        // Test Insert
        client.insert_card(table, &card).await?;

        // Verify Insert
        let card_args = CardQueryArgs {
            uid: Some(uid.clone()),
            ..Default::default()
        };
        let results = client.query_cards(table, &card_args).await?;
        assert_eq!(results.len(), 1);

        // Create updated card with new name
        let updated_card = match table {
            CardTable::Data => {
                let c = DataCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };
                ServerCard::Data(c)
            }
            CardTable::Model => {
                let c = ModelCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };

                ServerCard::Model(c)
            }
            CardTable::Experiment => {
                let c = ExperimentCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };
                ServerCard::Experiment(c)
            }
            CardTable::Audit => {
                let c = AuditCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };
                ServerCard::Audit(c)
            }
            CardTable::Prompt => {
                let c = PromptCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };
                ServerCard::Prompt(c)
            }
            CardTable::Service => {
                let c = ServiceCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };
                ServerCard::Service(c)
            }
            _ => panic!("Invalid card type"),
        };

        // Test Update
        client.update_card(table, &updated_card).await?;

        // Verify Update
        let updated_results = client.query_cards(table, &card_args).await?;
        assert_eq!(updated_results.len(), 1);

        // Verify updated name
        match updated_results {
            CardResults::Data(cards) => assert_eq!(cards[0].name, updated_name),
            CardResults::Model(cards) => assert_eq!(cards[0].name, updated_name),
            CardResults::Experiment(cards) => assert_eq!(cards[0].name, updated_name),
            CardResults::Audit(cards) => assert_eq!(cards[0].name, updated_name),
            CardResults::Prompt(cards) => assert_eq!(cards[0].name, updated_name),
            CardResults::Service(cards) => assert_eq!(cards[0].name, updated_name),
        }

        // delete card
        client.delete_card(table, &uid).await?;

        // Verify Delete
        let deleted_results = client.query_cards(table, &card_args).await?;
        assert_eq!(deleted_results.len(), 0);

        Ok(())
    }

    pub fn db_config() -> DatabaseSettings {
        DatabaseSettings {
            connection_uri: env::var("OPSML_TRACKING_URI").unwrap_or_else(|_| {
                "postgres://postgres:postgres@localhost:5432/postgres".to_string()
            }),
            max_connections: 1,
            sql_type: SqlType::Postgres,
        }
    }

    pub async fn db_client() -> PostgresClient {
        let config = db_config();
        let client = PostgresClient::new(&config).await.unwrap();

        cleanup(&client.pool).await;

        client
    }

    #[tokio::test]
    async fn test_postgres() {
        let _client = db_client().await;
        // Add assertions or further test logic here
    }

    #[tokio::test]
    async fn test_postgres_versions() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // query all versions
        // get versions (should return 1)
        let versions = client
            .get_versions(&CardTable::Data, "repo1", "Data1", None)
            .await
            .unwrap();
        assert_eq!(versions.len(), 10);

        // check star pattern
        let versions = client
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("*".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 10);

        let versions = client
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("1.*".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 4);

        let versions = client
            .get_versions(
                &CardTable::Data,
                "repo1",
                "Data1",
                Some("1.1.*".to_string()),
            )
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        // check tilde pattern
        let versions = client
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("~1".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 4);

        // check tilde pattern
        let versions = client
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("~1.1".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        // check tilde pattern
        let versions = client
            .get_versions(
                &CardTable::Data,
                "repo1",
                "Data1",
                Some("~1.1.1".to_string()),
            )
            .await
            .unwrap();
        assert_eq!(versions.len(), 1);

        let versions = client
            .get_versions(
                &CardTable::Data,
                "repo1",
                "Data1",
                Some("^2.0.0".to_string()),
            )
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);
    }

    #[tokio::test]
    async fn test_postgres_query_cards() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // check if uid exists
        let exists = client
            .check_uid_exists("fake", &CardTable::Data)
            .await
            .unwrap();

        assert!(!exists);

        // try name and space
        let card_args = CardQueryArgs {
            name: Some("Data1".to_string()),
            space: Some("repo1".to_string()),
            ..Default::default()
        };

        // query all versions
        // get versions (should return 1)
        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 10);

        // try name and space
        let card_args = CardQueryArgs {
            name: Some("Model1".to_string()),
            space: Some("repo1".to_string()),
            version: Some("~1.0.0".to_string()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // max_date
        let card_args = CardQueryArgs {
            max_date: Some("2023-11-28".to_string()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Experiment, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 2);

        // try tags
        let tags = ["key1".to_string()].to_vec();
        let card_args = CardQueryArgs {
            tags: Some(tags),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        let card_args = CardQueryArgs {
            sort_by_timestamp: Some(true),
            limit: Some(5),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 5);

        // test uid
        let card_args = CardQueryArgs {
            uid: Some("550e8400-e29b-41d4-a716-446655440000".to_string()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // check if uid exists
        let exists = client
            .check_uid_exists("550e8400-e29b-41d4-a716-446655440000", &CardTable::Data)
            .await
            .unwrap();

        assert!(exists);
    }

    #[tokio::test]
    async fn test_postgres_crud_cards() {
        let client = db_client().await;

        test_card_crud(&client, &CardTable::Data, "UpdatedDataName")
            .await
            .unwrap();
        test_card_crud(&client, &CardTable::Model, "UpdatedModelName")
            .await
            .unwrap();
        test_card_crud(&client, &CardTable::Experiment, "UpdatedRunName")
            .await
            .unwrap();
        test_card_crud(&client, &CardTable::Audit, "UpdatedAuditName")
            .await
            .unwrap();
        test_card_crud(&client, &CardTable::Prompt, "UpdatedPromptName")
            .await
            .unwrap();
        test_card_crud(&client, &CardTable::Service, "UpdatedDeckName")
            .await
            .unwrap();
    }

    #[tokio::test]
    async fn test_postgres_unique_repos() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // get unique space names
        let repos = client
            .get_unique_space_names(&CardTable::Model)
            .await
            .unwrap();

        assert_eq!(repos.len(), 9);
    }

    #[tokio::test]
    async fn test_postgres_query_stats() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // query stats
        let stats = client
            .query_stats(&CardTable::Model, None, None)
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 9);
        assert_eq!(stats.nbr_versions, 9);
        assert_eq!(stats.nbr_spaces, 9);

        // query stats with search term
        let stats = client
            .query_stats(&CardTable::Model, Some("Model1"), None)
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 2); // for Model1 and Model10

        let stats = client
            .query_stats(&CardTable::Model, Some("Model1"), Some("repo1"))
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 1); // for Model1

        // query page
        let results = client
            .query_page("name", 1, None, None, &CardTable::Data)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // query page
        let results = client
            .query_page("name", 1, None, None, &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 9);

        // query page
        let results = client
            .query_page("name", 1, None, Some("repo4"), &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);
    }

    #[tokio::test]
    async fn test_postgres_version_page() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // query page
        let results = client
            .version_page(1, Some("repo1"), Some("Model1"), &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);
    }

    #[tokio::test]
    async fn test_postgres_run_metrics() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let metric_names = vec!["metric1", "metric2", "metric3"];

        for name in metric_names {
            let metric = MetricRecord {
                experiment_uid: uid.clone(),
                name: name.to_string(),
                value: 1.0,
                ..Default::default()
            };

            client.insert_experiment_metric(&metric).await.unwrap();
        }

        let records = client
            .get_experiment_metric(&uid, &Vec::new())
            .await
            .unwrap();

        let names = client.get_experiment_metric_names(&uid).await.unwrap();

        assert_eq!(records.len(), 3);

        // assert names = "metric1"
        assert_eq!(names.len(), 3);

        // insert vec
        let records = vec![
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "vec1".to_string(),
                value: 1.0,
                ..Default::default()
            },
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "vec2".to_string(),
                value: 1.0,
                ..Default::default()
            },
        ];

        client.insert_experiment_metrics(&records).await.unwrap();

        let records = client
            .get_experiment_metric(&uid, &Vec::new())
            .await
            .unwrap();

        assert_eq!(records.len(), 5);
    }

    #[tokio::test]
    async fn test_postgres_hardware_metric() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();

        // create a loop of 10
        let metrics = HardwareMetricsRecord {
            experiment_uid: uid.clone(),
            created_at: get_utc_datetime(),
            ..Default::default()
        };

        client.insert_hardware_metrics(&metrics).await.unwrap();
        let records = client.get_hardware_metric(&uid).await.unwrap();

        assert_eq!(records.len(), 1);
    }

    #[tokio::test]
    async fn test_postgres_parameter() {
        let client = db_client().await;
        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let mut params = vec![];

        // create a loop of 10
        for i in 0..10 {
            let param = ParameterRecord {
                experiment_uid: uid.clone(),
                name: format!("param{i}"),
                ..Default::default()
            };

            params.push(param);
        }

        client.insert_experiment_parameters(&params).await.unwrap();
        let records = client
            .get_experiment_parameter(&uid, &Vec::new())
            .await
            .unwrap();

        assert_eq!(records.len(), 10);

        let param_records = client
            .get_experiment_parameter(&uid, &["param1".to_string()])
            .await
            .unwrap();

        assert_eq!(param_records.len(), 1);
    }

    #[tokio::test]
    async fn test_postgres_user() {
        let client = db_client().await;
        let recovery_codes = vec!["recovery_code_1".to_string(), "recovery_code_2".to_string()];

        let user = User::new(
            "user".to_string(),
            "pass".to_string(),
            "email".to_string(),
            recovery_codes,
            None,
            None,
            None,
            None,
            None,
        );

        let sso_user = User::new_from_sso("sso_user", "user@email.com");

        client.insert_user(&user).await.unwrap();
        client.insert_user(&sso_user).await.unwrap();

        // Read
        let mut user = client.get_user("user", None).await.unwrap().unwrap();

        assert_eq!(user.username, "user");
        assert_eq!(user.group_permissions, vec!["user"]);
        assert_eq!(user.email, "email");

        // update user
        user.active = false;
        user.refresh_token = Some("token".to_string());

        // Update
        client.update_user(&user).await.unwrap();
        let user = client.get_user("user", None).await.unwrap().unwrap();
        assert!(!user.active);
        assert_eq!(user.refresh_token.unwrap(), "token");

        // get users
        let users = client.get_users().await.unwrap();
        assert_eq!(users.len(), 2);

        let user = client
            .get_user("sso_user", Some("sso"))
            .await
            .unwrap()
            .unwrap();
        assert!(user.active);

        // delete
        client.delete_user("sso_user").await.unwrap();

        // get last admin
        let is_last_admin = client.is_last_admin("user").await.unwrap();
        assert!(!is_last_admin);

        // delete
        client.delete_user("user").await.unwrap();
    }

    #[tokio::test]
    async fn test_postgres_artifact_keys() {
        let client = db_client().await;

        let encrypted_key: Vec<u8> = (0..32).collect();

        let key = ArtifactKey {
            uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
            space: "repo1".to_string(),
            registry_type: RegistryType::Data,
            encrypted_key: encrypted_key.clone(),
            storage_key: "opsml_registry".to_string(),
        };

        client.insert_artifact_key(&key).await.unwrap();

        let key = client
            .get_artifact_key(&key.uid, &key.registry_type.to_string())
            .await
            .unwrap();

        assert_eq!(key.uid, "550e8400-e29b-41d4-a716-446655440000");

        // update key
        let encrypted_key: Vec<u8> = (32..64).collect();
        let key = ArtifactKey {
            uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
            space: "repo1".to_string(),
            registry_type: RegistryType::Data,
            encrypted_key: encrypted_key.clone(),
            storage_key: "opsml_registry".to_string(),
        };

        client.update_artifact_key(&key).await.unwrap();

        let key = client
            .get_artifact_key(&key.uid, &key.registry_type.to_string())
            .await
            .unwrap();

        assert_eq!(key.encrypted_key, encrypted_key);
    }

    #[tokio::test]
    async fn test_postgres_insert_operation() {
        let client = db_client().await;

        client
            .insert_audit_event(AuditEvent::default())
            .await
            .unwrap();

        // check if the operation was inserted
        let query = r#"SELECT username  FROM opsml_audit_event WHERE username = 'guest';"#;
        let result: String = sqlx::query_scalar(query)
            .fetch_one(&client.pool)
            .await
            .unwrap();

        assert_eq!(result, "guest");
    }

    #[tokio::test]
    async fn test_postgres_get_load_card_key() {
        let client = db_client().await;
        let data_card = DataCardRecord::default();
        let card = ServerCard::Data(data_card.clone());

        client.insert_card(&CardTable::Data, &card).await.unwrap();
        let encrypted_key: Vec<u8> = (0..32).collect();
        let key = ArtifactKey {
            uid: data_card.uid.clone(),
            space: "repo1".to_string(),
            registry_type: RegistryType::Data,
            encrypted_key: encrypted_key.clone(),
            storage_key: "opsml_registry".to_string(),
        };

        client.insert_artifact_key(&key).await.unwrap();

        let query_args = CardQueryArgs {
            uid: Some(data_card.uid.clone()),
            limit: Some(1),
            ..Default::default()
        };

        let key = client
            .get_card_key_for_loading(&CardTable::Data, &query_args)
            .await
            .unwrap();

        let _ = client
            .get_artifact_key_from_path(&key.storage_key, &RegistryType::Data.to_string())
            .await
            .unwrap()
            .unwrap();

        assert_eq!(key.uid, data_card.uid);
        assert_eq!(key.encrypted_key, encrypted_key);

        // delete
        client
            .delete_artifact_key(&data_card.uid, &RegistryType::Data.to_string())
            .await
            .unwrap();
    }

    #[tokio::test]
    async fn test_postgres_crud_space_record() {
        let client = db_client().await;

        // create a new space record
        let space_record = SpaceRecord {
            space: CommonKwargs::Undefined.to_string(),
            description: "Space description".to_string(),
        };

        client.insert_space_record(&space_record).await.unwrap();

        // insert datacard
        let data_card = DataCardRecord::default();
        let card = ServerCard::Data(data_card.clone());
        client.insert_card(&CardTable::Data, &card).await.unwrap();

        // insert modelcard
        let model_card = ModelCardRecord::default();
        let card = ServerCard::Model(model_card.clone());
        client.insert_card(&CardTable::Model, &card).await.unwrap();

        let space_event = SpaceNameEvent {
            space: data_card.space.clone(),
            name: data_card.name.clone(),
            registry_type: RegistryType::Data,
        };
        client.insert_space_name_record(&space_event).await.unwrap();

        let space_event = SpaceNameEvent {
            space: model_card.space.clone(),
            name: model_card.name.clone(),
            registry_type: RegistryType::Model,
        };

        client.insert_space_name_record(&space_event).await.unwrap();

        // get space stats
        let stats = client.get_all_space_stats().await.unwrap();
        assert_eq!(stats.len(), 1);

        // assert model_count
        assert_eq!(stats[0].data_count, 1);

        //create a new modelcard
        let model_card2 = ModelCardRecord {
            name: "Model2".to_string(),
            ..Default::default()
        };
        let card = ServerCard::Model(model_card2.clone());
        client.insert_card(&CardTable::Model, &card).await.unwrap();

        // update space stats again
        let space_event = SpaceNameEvent {
            space: model_card2.space.clone(),
            name: model_card2.name.clone(),
            registry_type: RegistryType::Model,
        };

        client.insert_space_name_record(&space_event).await.unwrap();
        // get space stats again

        let stats = client.get_all_space_stats().await.unwrap();
        assert_eq!(stats.len(), 1);

        // assert model_count
        assert_eq!(stats[0].model_count, 2);

        // update space record
        let updated_space_record = SpaceRecord {
            space: model_card2.space.clone(),
            description: "Updated Space description".to_string(),
        };
        client
            .update_space_record(&updated_space_record)
            .await
            .unwrap();

        // get space record
        let record = client
            .get_space_record(&model_card2.space)
            .await
            .unwrap()
            .unwrap();

        assert_eq!(record.description, "Updated Space description");

        // delete
        client
            .delete_space_record(&model_card2.space)
            .await
            .unwrap();

        // get space stats again
        let record = client.get_space_record(&model_card2.space).await.unwrap();
        assert_eq!(record, None);

        // delete space name record
        client
            .delete_space_name_record(&model_card2.space, &model_card2.name, &RegistryType::Model)
            .await
            .unwrap();
    }

    #[tokio::test]
    async fn test_postgres_log_artifact() {
        let client = db_client().await;
        let name = "my_file.json".to_string();

        // create a new artifact record
        let artifact_record1 = ArtifactSqlRecord::new(
            SPACE.to_string(),
            name.clone(),
            Version::new(0, 0, 0),
            "png".to_string(),
            ArtifactType::Figure.to_string(),
        );
        client
            .insert_artifact_record(&artifact_record1)
            .await
            .unwrap();

        let artifact_record2 = ArtifactSqlRecord::new(
            SPACE.to_string(),
            name.clone(),
            Version::new(0, 0, 0),
            "png".to_string(),
            ArtifactType::Figure.to_string(),
        );

        client
            .insert_artifact_record(&artifact_record2)
            .await
            .unwrap();

        // query artifacts
        let artifacts = client
            .query_artifacts(&ArtifactQueryArgs {
                space: Some(SPACE.to_string()),
                name: Some(name.clone()),
                ..Default::default()
            })
            .await
            .unwrap();
        assert_eq!(artifacts.len(), 2);
    }
}
