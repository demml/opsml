use crate::base::SqlClient;
use crate::mysql::helper::MySQLQueryHelper;
use crate::schemas::schema::{
    AuditCardRecord, CardSummary, DataCardRecord, ExperimentCardRecord, HardwareMetricsRecord,
    MetricRecord, ModelCardRecord, ParameterRecord, PromptCardRecord, QueryStats, ServerCard, User,
};
use crate::schemas::schema::{CardResults, VersionResult};
use async_trait::async_trait;
use opsml_error::error::SqlError;
use opsml_semver::VersionValidator;
use opsml_settings::config::DatabaseSettings;
use opsml_types::{
    cards::CardTable,
    contracts::{ArtifactKey, CardQueryArgs},
    RegistryType,
};
use semver::Version;
use sqlx::{
    mysql::{MySql, MySqlPoolOptions, MySqlRow},
    types::chrono::NaiveDateTime,
    FromRow, Pool, Row,
};

use tracing::info;

impl FromRow<'_, MySqlRow> for User {
    fn from_row(row: &MySqlRow) -> Result<Self, sqlx::Error> {
        let id: Option<i32> = row.try_get("id")?;
        let created_at: NaiveDateTime = row.try_get("created_at")?;
        let active: bool = row.try_get("active")?;
        let username: String = row.try_get("username")?;
        let password_hash: String = row.try_get("password_hash")?;

        // Deserialize JSON strings into Vec<String>
        let permissions: serde_json::Value = row.try_get("permissions")?;
        let permissions: Vec<String> = serde_json::from_value(permissions).unwrap_or_default();

        let group_permissions: serde_json::Value = row.try_get("group_permissions")?;
        let group_permissions: Vec<String> =
            serde_json::from_value(group_permissions).unwrap_or_default();
        let role = row.try_get("role")?;
        let refresh_token: Option<String> = row.try_get("refresh_token")?;

        Ok(User {
            id,
            created_at,
            active,
            username,
            password_hash,
            permissions,
            group_permissions,
            role,
            refresh_token,
        })
    }
}

#[derive(Debug, Clone)]
pub struct MySqlClient {
    pub pool: Pool<MySql>,
}

#[async_trait]
impl SqlClient for MySqlClient {
    async fn new(settings: &DatabaseSettings) -> Result<Self, SqlError> {
        let pool = MySqlPoolOptions::new()
            .max_connections(settings.max_connections)
            .connect(&settings.connection_uri)
            .await
            .map_err(|e| SqlError::ConnectionError(format!("{}", e)))?;

        let client = Self { pool };

        // run migrations
        client.run_migrations().await?;

        Ok(client)
    }
    async fn run_migrations(&self) -> Result<(), SqlError> {
        info!("Running migrations");
        sqlx::migrate!("src/mysql/migrations")
            .run(&self.pool)
            .await
            .map_err(|e| SqlError::MigrationError(format!("{}", e)))?;

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
        let query = MySQLQueryHelper::get_uid_query(table);
        let exists: Option<String> = sqlx::query_scalar(&query)
            .bind(uid)
            .fetch_optional(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(exists.is_some())
    }

    /// Primary query for retrieving versions from the database. Mainly used to get most recent version when determining version increment
    ///
    /// # Arguments
    ///
    /// * `table` - The table to query
    /// * `name` - The name of the card
    /// * `repository` - The repository of the card
    /// * `version` - The version of the card
    ///
    /// # Returns
    ///
    /// * `Vec<String>` - A vector of strings representing the sorted (desc) versions of the card
    async fn get_versions(
        &self,
        table: &CardTable,
        repository: &str,
        name: &str,
        version: Option<String>,
    ) -> Result<Vec<String>, SqlError> {
        let query = MySQLQueryHelper::get_versions_query(table, version)?;
        let cards: Vec<VersionResult> = sqlx::query_as(&query)
            .bind(name)
            .bind(repository)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        let versions = cards
            .iter()
            .map(|c| {
                c.to_version()
                    .map_err(|e| SqlError::VersionError(format!("{}", e)))
            })
            .collect::<Result<Vec<Version>, SqlError>>()?;

        // sort semvers
        VersionValidator::sort_semver_versions(versions, true)
            .map_err(|e| SqlError::VersionError(format!("{}", e)))
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
        let query = MySQLQueryHelper::get_query_cards_query(table, query_args)?;

        match table {
            CardTable::Data => {
                let card: Vec<DataCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await
                    .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

                return Ok(CardResults::Data(card));
            }
            CardTable::Model => {
                let card: Vec<ModelCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await
                    .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

                return Ok(CardResults::Model(card));
            }
            CardTable::Experiment => {
                let card: Vec<ExperimentCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await
                    .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

                return Ok(CardResults::Experiment(card));
            }

            CardTable::Audit => {
                let card: Vec<AuditCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await
                    .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

                return Ok(CardResults::Audit(card));
            }

            CardTable::Prompt => {
                let card: Vec<PromptCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await
                    .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

                return Ok(CardResults::Prompt(card));
            }

            _ => {
                return Err(SqlError::QueryError(
                    "Invalid table name for query".to_string(),
                ));
            }
        }
    }

    async fn insert_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError> {
        match table {
            CardTable::Data => match card {
                ServerCard::Data(data) => {
                    let query = MySQLQueryHelper::get_datacard_insert_query();
                    sqlx::query(&query)
                        .bind(&data.uid)
                        .bind(&data.app_env)
                        .bind(&data.name)
                        .bind(&data.repository)
                        .bind(data.major)
                        .bind(data.minor)
                        .bind(data.patch)
                        .bind(&data.version)
                        .bind(&data.data_type)
                        .bind(&data.interface_type)
                        .bind(&data.tags)
                        .bind(&data.experimentcard_uid)
                        .bind(&data.auditcard_uid)
                        .bind(&data.pre_tag)
                        .bind(&data.build_tag)
                        .bind(&data.username)
                        .execute(&self.pool)
                        .await
                        .map_err(|e| SqlError::QueryError(format!("{}", e)))?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::QueryError(
                        "Invalid card type for insert".to_string(),
                    ));
                }
            },
            CardTable::Model => match card {
                ServerCard::Model(model) => {
                    let query = MySQLQueryHelper::get_modelcard_insert_query();
                    sqlx::query(&query)
                        .bind(&model.uid)
                        .bind(&model.app_env)
                        .bind(&model.name)
                        .bind(&model.repository)
                        .bind(model.major)
                        .bind(model.minor)
                        .bind(model.patch)
                        .bind(&model.version)
                        .bind(&model.datacard_uid)
                        .bind(model.data_type.to_string())
                        .bind(model.model_type.to_string())
                        .bind(&model.interface_type)
                        .bind(&model.task_type)
                        .bind(&model.tags)
                        .bind(&model.experimentcard_uid)
                        .bind(&model.auditcard_uid)
                        .bind(&model.pre_tag)
                        .bind(&model.build_tag)
                        .bind(&model.username)
                        .execute(&self.pool)
                        .await
                        .map_err(|e| SqlError::QueryError(format!("{}", e)))?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::QueryError(
                        "Invalid card type for insert".to_string(),
                    ));
                }
            },
            CardTable::Experiment => match card {
                ServerCard::Experiment(run) => {
                    let query = MySQLQueryHelper::get_experimentcard_insert_query();
                    sqlx::query(&query)
                        .bind(&run.uid)
                        .bind(&run.app_env)
                        .bind(&run.name)
                        .bind(&run.repository)
                        .bind(run.major)
                        .bind(run.minor)
                        .bind(run.patch)
                        .bind(&run.version)
                        .bind(&run.tags)
                        .bind(&run.datacard_uids)
                        .bind(&run.modelcard_uids)
                        .bind(&run.promptcard_uids)
                        .bind(&run.experimentcard_uids)
                        .bind(&run.pre_tag)
                        .bind(&run.build_tag)
                        .bind(&run.username)
                        .execute(&self.pool)
                        .await
                        .map_err(|e| SqlError::QueryError(format!("{}", e)))?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::QueryError(
                        "Invalid card type for insert".to_string(),
                    ));
                }
            },
            CardTable::Audit => match card {
                ServerCard::Audit(audit) => {
                    let query = MySQLQueryHelper::get_auditcard_insert_query();
                    sqlx::query(&query)
                        .bind(&audit.uid)
                        .bind(&audit.app_env)
                        .bind(&audit.name)
                        .bind(&audit.repository)
                        .bind(audit.major)
                        .bind(audit.minor)
                        .bind(audit.patch)
                        .bind(&audit.version)
                        .bind(&audit.tags)
                        .bind(audit.approved)
                        .bind(&audit.datacard_uids)
                        .bind(&audit.modelcard_uids)
                        .bind(&audit.experimentcard_uids)
                        .bind(&audit.pre_tag)
                        .bind(&audit.build_tag)
                        .bind(&audit.username)
                        .execute(&self.pool)
                        .await
                        .map_err(|e| SqlError::QueryError(format!("{}", e)))?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::QueryError(
                        "Invalid card type for insert".to_string(),
                    ));
                }
            },

            CardTable::Prompt => match card {
                ServerCard::Prompt(card) => {
                    let query = MySQLQueryHelper::get_promptcard_insert_query();
                    sqlx::query(&query)
                        .bind(&card.uid)
                        .bind(&card.app_env)
                        .bind(&card.name)
                        .bind(&card.repository)
                        .bind(card.major)
                        .bind(card.minor)
                        .bind(card.patch)
                        .bind(&card.version)
                        .bind(&card.prompt_type)
                        .bind(&card.tags)
                        .bind(&card.experimentcard_uid)
                        .bind(&card.auditcard_uid)
                        .bind(&card.pre_tag)
                        .bind(&card.build_tag)
                        .bind(&card.username)
                        .execute(&self.pool)
                        .await
                        .map_err(|e| SqlError::QueryError(format!("{}", e)))?;
                    Ok(())
                }

                _ => {
                    return Err(SqlError::QueryError(
                        "Invalid card type for insert".to_string(),
                    ));
                }
            },

            _ => {
                return Err(SqlError::QueryError(
                    "Invalid table name for insert".to_string(),
                ));
            }
        }
    }

    async fn update_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError> {
        match table {
            CardTable::Data => match card {
                ServerCard::Data(data) => {
                    let query = MySQLQueryHelper::get_datacard_update_query();

                    sqlx::query(&query)
                        .bind(&data.app_env)
                        .bind(&data.name)
                        .bind(&data.repository)
                        .bind(data.major)
                        .bind(data.minor)
                        .bind(data.patch)
                        .bind(&data.version)
                        .bind(data.data_type.to_string())
                        .bind(&data.interface_type)
                        .bind(&data.tags)
                        .bind(&data.experimentcard_uid)
                        .bind(&data.auditcard_uid)
                        .bind(&data.pre_tag)
                        .bind(&data.build_tag)
                        .bind(&data.username)
                        .bind(&data.uid)
                        .execute(&self.pool)
                        .await
                        .map_err(|e| SqlError::QueryError(format!("{}", e)))?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::QueryError(
                        "Invalid card type for insert".to_string(),
                    ));
                }
            },
            CardTable::Model => match card {
                ServerCard::Model(model) => {
                    let query = MySQLQueryHelper::get_modelcard_update_query();
                    sqlx::query(&query)
                        .bind(&model.app_env)
                        .bind(&model.name)
                        .bind(&model.repository)
                        .bind(model.major)
                        .bind(model.minor)
                        .bind(model.patch)
                        .bind(&model.version)
                        .bind(&model.datacard_uid)
                        .bind(&model.data_type)
                        .bind(&model.model_type)
                        .bind(&model.interface_type)
                        .bind(&model.task_type)
                        .bind(&model.tags)
                        .bind(&model.experimentcard_uid)
                        .bind(&model.auditcard_uid)
                        .bind(&model.pre_tag)
                        .bind(&model.build_tag)
                        .bind(&model.username)
                        .bind(&model.uid)
                        .execute(&self.pool)
                        .await
                        .map_err(|e| SqlError::QueryError(format!("{}", e)))?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::QueryError(
                        "Invalid card type for insert".to_string(),
                    ));
                }
            },
            CardTable::Experiment => match card {
                ServerCard::Experiment(run) => {
                    let query = MySQLQueryHelper::get_experimentcard_update_query();
                    sqlx::query(&query)
                        .bind(&run.app_env)
                        .bind(&run.name)
                        .bind(&run.repository)
                        .bind(run.major)
                        .bind(run.minor)
                        .bind(run.patch)
                        .bind(&run.version)
                        .bind(&run.tags)
                        .bind(&run.datacard_uids)
                        .bind(&run.modelcard_uids)
                        .bind(&run.promptcard_uids)
                        .bind(&run.experimentcard_uids)
                        .bind(&run.pre_tag)
                        .bind(&run.build_tag)
                        .bind(&run.username)
                        .bind(&run.uid)
                        .execute(&self.pool)
                        .await
                        .map_err(|e| SqlError::QueryError(format!("{}", e)))?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::QueryError(
                        "Invalid card type for insert".to_string(),
                    ));
                }
            },
            CardTable::Audit => match card {
                ServerCard::Audit(audit) => {
                    let query = MySQLQueryHelper::get_auditcard_update_query();
                    sqlx::query(&query)
                        .bind(&audit.app_env)
                        .bind(&audit.name)
                        .bind(&audit.repository)
                        .bind(audit.major)
                        .bind(audit.minor)
                        .bind(audit.patch)
                        .bind(&audit.version)
                        .bind(&audit.tags)
                        .bind(audit.approved)
                        .bind(&audit.datacard_uids)
                        .bind(&audit.modelcard_uids)
                        .bind(&audit.experimentcard_uids)
                        .bind(&audit.pre_tag)
                        .bind(&audit.build_tag)
                        .bind(&audit.username)
                        .bind(&audit.uid)
                        .execute(&self.pool)
                        .await
                        .map_err(|e| SqlError::QueryError(format!("{}", e)))?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::QueryError(
                        "Invalid card type for insert".to_string(),
                    ));
                }
            },

            CardTable::Prompt => match card {
                ServerCard::Prompt(card) => {
                    let query = MySQLQueryHelper::get_promptcard_update_query();
                    sqlx::query(&query)
                        .bind(&card.app_env)
                        .bind(&card.name)
                        .bind(&card.repository)
                        .bind(card.major)
                        .bind(card.minor)
                        .bind(card.patch)
                        .bind(&card.version)
                        .bind(&card.prompt_type)
                        .bind(&card.tags)
                        .bind(&card.experimentcard_uid)
                        .bind(&card.auditcard_uid)
                        .bind(&card.pre_tag)
                        .bind(&card.build_tag)
                        .bind(&card.username)
                        .bind(&card.uid)
                        .execute(&self.pool)
                        .await
                        .map_err(|e| SqlError::QueryError(format!("{}", e)))?;
                    Ok(())
                }

                _ => {
                    return Err(SqlError::QueryError(
                        "Invalid card type for insert".to_string(),
                    ));
                }
            },

            _ => {
                return Err(SqlError::QueryError(
                    "Invalid table name for insert".to_string(),
                ));
            }
        }
    }

    /// Get unique repository names
    ///
    /// # Arguments
    ///
    /// * `table` - The table to query
    ///
    /// # Returns
    ///
    /// * `Vec<String>` - A vector of unique repository names
    async fn get_unique_repository_names(
        &self,
        table: &CardTable,
    ) -> Result<Vec<String>, SqlError> {
        let query = format!("SELECT DISTINCT repository FROM {}", table);
        let repos: Vec<String> = sqlx::query_scalar(&query)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(repos)
    }

    async fn query_stats(
        &self,
        table: &CardTable,
        search_term: Option<&str>,
    ) -> Result<QueryStats, SqlError> {
        let query = MySQLQueryHelper::get_query_stats_query(table);

        let stats = sqlx::query_as(&query)
            .bind(search_term)
            .bind(search_term.map(|term| format!("%{}%", term)))
            .bind(search_term.map(|term| format!("%{}%", term)))
            .fetch_one(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(stats)
    }

    /// Query a page of cards
    ///
    /// # Arguments
    ///
    /// * `sort_by` - The field to sort by
    /// * `page` - The page number
    /// * `search_term` - The search term to query
    /// * `repository` - The repository to query
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
        repository: Option<&str>,
        table: &CardTable,
    ) -> Result<Vec<CardSummary>, SqlError> {
        let query = MySQLQueryHelper::get_query_page_query(table, sort_by);

        let lower_bound = page * 30;
        let upper_bound = lower_bound + 30;

        let records: Vec<CardSummary> = sqlx::query_as(&query)
            .bind(repository) // 1st ? in versions_cte
            .bind(repository) // 2nd ? in versions_cte
            .bind(search_term) // 3rd ? in versions_cte
            .bind(search_term.map(|term| format!("%{}%", term))) // 4th ? in versions_cte
            .bind(search_term.map(|term| format!("%{}%", term))) // 5th ? in versions_cte
            .bind(repository) // 1st ? in stats_cte
            .bind(repository) // 2nd ? in stats_cte
            .bind(search_term) // 3rd ? in stats_cte
            .bind(search_term.map(|term| format!("%{}%", term))) // 4th ? in stats_cte
            .bind(search_term.map(|term| format!("%{}%", term))) // 5th ? in stats_cte
            .bind(lower_bound) // 1st ? in final SELECT
            .bind(upper_bound)
            .fetch_all(&self.pool)
            .await
            .unwrap();

        Ok(records)
    }

    async fn delete_card(&self, table: &CardTable, uid: &str) -> Result<(), SqlError> {
        let query = format!("DELETE FROM {} WHERE uid = ?", table);

        sqlx::query(&query)
            .bind(uid)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn insert_experiment_metric(&self, record: &MetricRecord) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_experiment_metric_insert_query();

        sqlx::query(&query)
            .bind(&record.experiment_uid)
            .bind(&record.name)
            .bind(record.value)
            .bind(record.step)
            .bind(record.timestamp)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn insert_experiment_metrics<'life1>(
        &self,
        records: &'life1 [MetricRecord],
    ) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_experiment_metrics_insert_query(records.len());

        let mut query_builder = sqlx::query(&query);

        for r in records {
            query_builder = query_builder
                .bind(&r.experiment_uid)
                .bind(&r.name)
                .bind(r.value)
                .bind(r.step)
                .bind(r.timestamp);
        }

        query_builder
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_experiment_metric<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<MetricRecord>, SqlError> {
        let (query, bindings) = MySQLQueryHelper::get_experiment_metric_query(names);

        let mut query_builder = sqlx::query_as::<_, MetricRecord>(&query).bind(uid);

        for binding in bindings {
            query_builder = query_builder.bind(binding);
        }

        let records: Vec<MetricRecord> = query_builder
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(records)
    }

    async fn get_experiment_metric_names(&self, uid: &str) -> Result<Vec<String>, SqlError> {
        let query = format!(
            "SELECT DISTINCT name FROM {} WHERE experiment_uid = ?",
            CardTable::Metrics
        );

        let records: Vec<String> = sqlx::query_scalar(&query)
            .bind(uid)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(records)
    }
    async fn insert_hardware_metrics(
        &self,
        record: &HardwareMetricsRecord,
    ) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_hardware_metrics_insert_query();
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
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_hardware_metric(&self, uid: &str) -> Result<Vec<HardwareMetricsRecord>, SqlError> {
        let query = format!(
            "SELECT * FROM {} WHERE experiment_uid = ?",
            CardTable::HardwareMetrics
        );

        let records: Vec<HardwareMetricsRecord> = sqlx::query_as(&query)
            .bind(uid)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(records)
    }

    async fn insert_experiment_parameters<'life1>(
        &self,
        records: &'life1 [ParameterRecord],
    ) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_experiment_parameters_insert_query(records.len());

        let mut query_builder = sqlx::query(&query);

        for record in records {
            query_builder = query_builder
                .bind(&record.experiment_uid)
                .bind(&record.name)
                .bind(&record.value);
        }

        query_builder
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_experiment_parameter<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<ParameterRecord>, SqlError> {
        let (query, bindings) = MySQLQueryHelper::get_experiment_parameter_query(names);
        let mut query_builder = sqlx::query_as::<_, ParameterRecord>(&query).bind(uid);

        for binding in bindings {
            query_builder = query_builder.bind(binding);
        }

        let records: Vec<ParameterRecord> = query_builder
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(records)
    }

    async fn insert_user(&self, user: &User) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_user_insert_query();

        let group_permissions = serde_json::to_value(&user.group_permissions)
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        let permissions = serde_json::to_value(&user.permissions)
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        sqlx::query(&query)
            .bind(&user.username)
            .bind(&user.password_hash)
            .bind(&permissions)
            .bind(&group_permissions)
            .bind(&user.role)
            .bind(user.active)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_user(&self, username: &str) -> Result<Option<User>, SqlError> {
        let query = MySQLQueryHelper::get_user_query();

        let user: Option<User> = sqlx::query_as(&query)
            .bind(username)
            .fetch_optional(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(user)
    }

    async fn update_user(&self, user: &User) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_user_update_query();

        let group_permissions = serde_json::to_value(&user.group_permissions)
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        let permissions = serde_json::to_value(&user.permissions)
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        sqlx::query(&query)
            .bind(user.active)
            .bind(&user.password_hash)
            .bind(&permissions)
            .bind(&group_permissions)
            .bind(&user.refresh_token)
            .bind(&user.username)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_users(&self) -> Result<Vec<User>, SqlError> {
        let query = MySQLQueryHelper::get_users_query();

        let users = sqlx::query_as::<_, User>(&query)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(users)
    }

    async fn is_last_admin(&self, username: &str) -> Result<bool, SqlError> {
        // Count admins in the system
        let query = MySQLQueryHelper::get_last_admin_query();

        let admins: Vec<String> = sqlx::query_scalar(&query)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        // If there are no other admins, this is the last one
        if admins.len() > 1 {
            return Ok(false);
        }

        // no admins found
        if admins.len() == 0 {
            return Ok(false);
        }

        // check if the username is the last admin
        Ok(admins.len() == 1 && admins[0] == username)
    }

    async fn delete_user(&self, username: &str) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_user_delete_query();

        sqlx::query(&query)
            .bind(username)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn insert_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_artifact_key_insert_query();
        sqlx::query(&query)
            .bind(&key.uid)
            .bind(key.registry_type.to_string())
            .bind(key.encrypted_key.clone())
            .bind(&key.storage_key)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_artifact_key(
        &self,
        uid: &str,
        registry_type: &str,
    ) -> Result<ArtifactKey, SqlError> {
        let query = MySQLQueryHelper::get_artifact_key_select_query();

        let key: (String, String, Vec<u8>, String) = sqlx::query_as(&query)
            .bind(uid)
            .bind(registry_type)
            .fetch_one(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(ArtifactKey {
            uid: key.0,
            registry_type: RegistryType::from_string(&key.1)?,
            encrypted_key: key.2,
            storage_key: key.3,
        })
    }

    async fn get_artifact_key_from_path(
        &self,
        storage_path: &str,
        registry_type: &str,
    ) -> Result<Option<ArtifactKey>, SqlError> {
        let query = MySQLQueryHelper::get_artifact_key_from_storage_path_query();

        let key: Option<(String, String, Vec<u8>, String)> = sqlx::query_as(&query)
            .bind(storage_path)
            .bind(registry_type)
            .fetch_optional(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        return match key {
            Some(k) => Ok(Some(ArtifactKey {
                uid: k.0,
                registry_type: RegistryType::from_string(&k.1)?,
                encrypted_key: k.2,
                storage_key: k.3,
            })),
            None => Ok(None),
        };
    }

    async fn update_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_artifact_key_update_query();
        sqlx::query(&query)
            .bind(key.encrypted_key.clone())
            .bind(&key.uid)
            .bind(key.registry_type.to_string())
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn insert_operation(
        &self,
        username: &str,
        access_type: &str,
        access_location: &str,
    ) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_operation_insert_query();
        sqlx::query(&query)
            .bind(username)
            .bind(access_type)
            .bind(access_location)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_card_key_for_loading(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<ArtifactKey, SqlError> {
        let query = MySQLQueryHelper::get_load_card_query(table, query_args)?;

        let key: (String, String, Vec<u8>, String) = sqlx::query_as(&query)
            .bind(query_args.uid.as_ref())
            .bind(query_args.uid.as_ref())
            .bind(query_args.name.as_ref())
            .bind(query_args.name.as_ref())
            .bind(query_args.repository.as_ref())
            .bind(query_args.repository.as_ref())
            .bind(query_args.max_date.as_ref())
            .bind(query_args.max_date.as_ref())
            .bind(query_args.limit.unwrap_or(1))
            .fetch_one(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(ArtifactKey {
            uid: key.0,
            registry_type: RegistryType::from_string(&key.1)?,
            encrypted_key: key.2,
            storage_key: key.3,
        })
    }

    async fn delete_artifact_key(&self, uid: &str, registry_type: &str) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_artifact_key_delete_query();
        sqlx::query(&query)
            .bind(uid)
            .bind(registry_type)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {

    use super::*;
    use opsml_types::{contracts::Operation, RegistryType, SqlType};
    use opsml_utils::utils::get_utc_datetime;
    use std::env;

    pub async fn cleanup(pool: &Pool<MySql>) {
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
            FROM opsml_prompt_registry;

            DELETE
            FROM opsml_experiment_metrics;

            DELETE
            FROM opsml_experiment_hardware_metrics;

            DELETE
            FROM opsml_experiment_parameters;

            DELETE
            FROM opsml_users;

            DELETE
            FROM opsml_artifact_key;

            DELETE
            FROM opsml_operations;
            "#,
        )
        .fetch_all(pool)
        .await
        .unwrap();
    }

    async fn test_card_crud(
        client: &MySqlClient,
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
            _ => panic!("Invalid card type"),
        };

        // Get UID for queries
        let uid = match &card {
            ServerCard::Data(c) => c.uid.clone(),
            ServerCard::Model(c) => c.uid.clone(),
            ServerCard::Experiment(c) => c.uid.clone(),
            ServerCard::Audit(c) => c.uid.clone(),
            ServerCard::Prompt(c) => c.uid.clone(),
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
            connection_uri: env::var("OPSML_TRACKING_URI")
                .unwrap_or_else(|_| "mysql://admin:admin@localhost:3306/mysql".to_string()),
            max_connections: 1,
            sql_type: SqlType::MySql,
        }
    }

    pub async fn db_client() -> MySqlClient {
        let config = db_config();
        let client = MySqlClient::new(&config).await.unwrap();

        cleanup(&client.pool).await;

        client
    }

    #[tokio::test]
    async fn test_mysql() {
        let _client = db_client().await;
    }

    #[tokio::test]
    async fn test_mysql_versions() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_mysql_test.sql").unwrap();
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
    async fn test_mysql_query_cards() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_mysql_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // check if uid exists
        let exists = client
            .check_uid_exists("fake", &CardTable::Data)
            .await
            .unwrap();

        assert!(!exists);

        // try name and repository
        let card_args = CardQueryArgs {
            name: Some("Data1".to_string()),
            repository: Some("repo1".to_string()),
            ..Default::default()
        };

        // query all versions
        // get versions (should return 1)
        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 10);

        // try name and repository
        let card_args = CardQueryArgs {
            name: Some("Model1".to_string()),
            repository: Some("repo1".to_string()),
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
    async fn test_mysql_crud_cards() {
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
    }

    #[tokio::test]
    async fn test_mysql_unique_repos() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_mysql_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // get unique repository names
        let repos = client
            .get_unique_repository_names(&CardTable::Model)
            .await
            .unwrap();

        assert_eq!(repos.len(), 10);
    }

    #[tokio::test]
    async fn test_mysql_query_stats() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_mysql_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // query stats
        let stats = client.query_stats(&CardTable::Model, None).await.unwrap();

        assert_eq!(stats.nbr_names, 10);
        assert_eq!(stats.nbr_versions, 10);
        assert_eq!(stats.nbr_repositories, 10);

        // query stats with search term
        let stats = client
            .query_stats(&CardTable::Model, Some("Model1"))
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 2); // for Model1 and Model10
    }

    #[tokio::test]
    async fn test_mysql_query_page() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_mysql_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // query page
        let results = client
            .query_page("name", 0, None, None, &CardTable::Data)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // query page
        let results = client
            .query_page("name", 0, None, None, &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 10);

        // query page
        let results = client
            .query_page("name", 0, None, Some("repo4"), &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);
    }

    #[tokio::test]
    async fn test_mysql_run_metrics() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_mysql_test.sql").unwrap();
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
    async fn test_mysql_hardware_metric() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_mysql_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();

        // create a loop of 10

        let metric = HardwareMetricsRecord {
            experiment_uid: uid.clone(),
            created_at: get_utc_datetime(),
            ..Default::default()
        };

        client.insert_hardware_metrics(&metric).await.unwrap();
        let records = client.get_hardware_metric(&uid).await.unwrap();

        assert_eq!(records.len(), 1);
    }

    #[tokio::test]
    async fn test_mysql_parameter() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_mysql_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let mut params = vec![];

        // create a loop of 10
        for i in 0..10 {
            let param = ParameterRecord {
                experiment_uid: uid.clone(),
                name: format!("param{}", i),
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

        let records = client
            .get_experiment_parameter(&uid, &["param1".to_string()])
            .await
            .unwrap();

        assert_eq!(records.len(), 1);
    }

    #[tokio::test]
    async fn test_mysql_user() {
        let client = db_client().await;

        let user = User::new("user".to_string(), "pass".to_string(), None, None, None);
        client.insert_user(&user).await.unwrap();

        let mut user = client.get_user("user").await.unwrap().unwrap();
        assert_eq!(user.username, "user");

        // update user
        user.active = false;
        user.refresh_token = Some("token".to_string());

        client.update_user(&user).await.unwrap();
        let user = client.get_user("user").await.unwrap().unwrap();
        assert!(!user.active);
        assert_eq!(user.refresh_token.unwrap(), "token");

        // get users
        let users = client.get_users().await.unwrap();
        assert_eq!(users.len(), 1);

        // get last admin
        let is_last_admin = client.is_last_admin("user").await.unwrap();
        assert!(is_last_admin);

        // delete
        client.delete_user("user").await.unwrap();
    }

    #[tokio::test]
    async fn test_mysql_artifact_keys() {
        let client = db_client().await;

        let encrypted_key: Vec<u8> = (0..32).collect();

        let key = ArtifactKey {
            uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
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
    async fn test_mysql_insert_operation() {
        let client = db_client().await;

        client
            .insert_operation("guest", &Operation::Read.to_string(), "model/registry")
            .await
            .unwrap();

        // check if the operation was inserted
        let query = r#"SELECT username  FROM opsml_operations WHERE username = 'guest';"#;
        let result: String = sqlx::query_scalar(query)
            .fetch_one(&client.pool)
            .await
            .unwrap();

        assert_eq!(result, "guest");
    }

    #[tokio::test]
    async fn test_mysql_get_load_card_key() {
        let client = db_client().await;
        let data_card = DataCardRecord::default();
        let card = ServerCard::Data(data_card.clone());

        client.insert_card(&CardTable::Data, &card).await.unwrap();
        let encrypted_key: Vec<u8> = (0..32).collect();
        let key = ArtifactKey {
            uid: data_card.uid.clone(),
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
}
