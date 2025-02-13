use crate::base::SqlClient;

use crate::schemas::schema::ProjectCardRecord;
use crate::schemas::schema::{
    ArtifactKey, AuditCardRecord, CardResults, CardSummary, DataCardRecord, HardwareMetricsRecord,
    MetricRecord, ModelCardRecord, ParameterRecord, PipelineCardRecord, QueryStats, RunCardRecord,
    ServerCard, User, VersionResult,
};
use crate::sqlite::helper::SqliteQueryHelper;
use async_trait::async_trait;
use opsml_error::error::SqlError;
use opsml_semver::VersionValidator;
use opsml_settings::config::DatabaseSettings;
use opsml_types::{cards::CardTable, contracts::CardQueryArgs};
use semver::Version;
use sqlx::{
    sqlite::{SqlitePoolOptions, SqliteRow},
    types::chrono::NaiveDateTime,
    FromRow, Pool, Row, Sqlite,
};
use tracing::{debug, info, instrument};

impl FromRow<'_, SqliteRow> for User {
    fn from_row(row: &SqliteRow) -> Result<Self, sqlx::Error> {
        let id: Option<i32> = row.try_get("id")?;
        let created_at: Option<NaiveDateTime> = row.try_get("created_at")?;
        let active: bool = row.try_get("active")?;
        let username: String = row.try_get("username")?;
        let password_hash: String = row.try_get("password_hash")?;

        // Deserialize JSON strings into Vec<String>
        let permissions: String = row.try_get("permissions")?;
        let permissions: Vec<String> = serde_json::from_str(&permissions).unwrap_or_default();

        let group_permissions: String = row.try_get("group_permissions")?;
        let group_permissions: Vec<String> =
            serde_json::from_str(&group_permissions).unwrap_or_default();

        let refresh_token: Option<String> = row.try_get("refresh_token")?;

        Ok(User {
            id,
            created_at,
            active,
            username,
            password_hash,
            permissions,
            group_permissions,
            refresh_token,
        })
    }
}

#[derive(Debug, Clone)]
pub struct SqliteClient {
    pub pool: Pool<Sqlite>,
}

#[async_trait]
impl SqlClient for SqliteClient {
    async fn new(settings: &DatabaseSettings) -> Result<Self, SqlError> {
        debug!("settings: {:?}", settings);
        // if the connection uri is not in memory, create the file
        if !settings.connection_uri.contains(":memory:") {
            // strip "sqlite://" from the connection uri
            let uri = settings.connection_uri.replace("sqlite://", "");
            let path = std::path::Path::new(&uri);

            // check if the file exists
            if !path.exists() {
                debug!("SQLite file does not exist, creating file");
                // Ensure the parent directory exists
                if let Some(parent) = path.parent() {
                    if !parent.exists() {
                        std::fs::create_dir_all(parent)
                            .map_err(|e| {
                                SqlError::FileError(format!(
                                    "Failed to create SQLite file parents: {} with error: {}",
                                    &uri, e
                                ))
                            })
                            .unwrap();
                    }
                }

                // create the file
                std::fs::File::create(&uri)
                    .map_err(|e| {
                        SqlError::FileError(format!(
                            "Failed to create SQLite file: {} with error: {}",
                            &uri, e
                        ))
                    })
                    .unwrap();
            }
        }

        let pool = SqlitePoolOptions::new()
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
        sqlx::migrate!("src/sqlite/migrations")
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
        let query = SqliteQueryHelper::get_uid_query(table);
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
    #[instrument(skip_all)]
    async fn get_versions(
        &self,
        table: &CardTable,
        name: &str,
        repository: &str,
        version: Option<&str>,
    ) -> Result<Vec<String>, SqlError> {
        // if version is None, get the latest version
        let query = SqliteQueryHelper::get_versions_query(table, version)?;
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
        let query = SqliteQueryHelper::get_query_cards_query(table, query_args)?;

        match table {
            CardTable::Data => {
                let card: Vec<DataCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
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
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await
                    .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

                return Ok(CardResults::Model(card));
            }
            CardTable::Run => {
                let card: Vec<RunCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await
                    .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

                return Ok(CardResults::Run(card));
            }

            CardTable::Audit => {
                let card: Vec<AuditCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await
                    .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

                return Ok(CardResults::Audit(card));
            }
            CardTable::Pipeline => {
                let card: Vec<PipelineCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await
                    .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

                return Ok(CardResults::Pipeline(card));
            }
            CardTable::Project => {
                let card: Vec<ProjectCardRecord> = sqlx::query_as(&query)
                    .bind(query_args.uid.as_ref())
                    .bind(query_args.name.as_ref())
                    .bind(query_args.repository.as_ref())
                    .bind(query_args.max_date.as_ref())
                    .bind(query_args.limit.unwrap_or(50))
                    .fetch_all(&self.pool)
                    .await
                    .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

                return Ok(CardResults::Project(card));
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
                    let query = SqliteQueryHelper::get_datacard_insert_query();
                    sqlx::query(&query)
                        .bind(&data.uid)
                        .bind(&data.app_env)
                        .bind(&data.name)
                        .bind(&data.repository)
                        .bind(data.major)
                        .bind(data.minor)
                        .bind(data.patch)
                        .bind(&data.version)
                        .bind(&data.contact)
                        .bind(&data.data_type)
                        .bind(&data.interface_type)
                        .bind(&data.tags)
                        .bind(&data.runcard_uid)
                        .bind(&data.pipelinecard_uid)
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
                    let query = SqliteQueryHelper::get_modelcard_insert_query();
                    sqlx::query(&query)
                        .bind(&model.uid)
                        .bind(&model.app_env)
                        .bind(&model.name)
                        .bind(&model.repository)
                        .bind(model.major)
                        .bind(model.minor)
                        .bind(model.patch)
                        .bind(&model.version)
                        .bind(&model.contact)
                        .bind(&model.datacard_uid)
                        .bind(&model.data_type)
                        .bind(&model.model_type)
                        .bind(&model.interface_type)
                        .bind(&model.task_type)
                        .bind(&model.tags)
                        .bind(&model.runcard_uid)
                        .bind(&model.pipelinecard_uid)
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
            CardTable::Run => match card {
                ServerCard::Run(run) => {
                    let query = SqliteQueryHelper::get_runcard_insert_query();
                    sqlx::query(&query)
                        .bind(&run.uid)
                        .bind(&run.app_env)
                        .bind(&run.name)
                        .bind(&run.repository)
                        .bind(run.major)
                        .bind(run.minor)
                        .bind(run.patch)
                        .bind(&run.version)
                        .bind(&run.contact)
                        .bind(&run.project)
                        .bind(&run.tags)
                        .bind(&run.datacard_uids)
                        .bind(&run.modelcard_uids)
                        .bind(&run.pipelinecard_uid)
                        .bind(&run.artifact_uris)
                        .bind(&run.compute_environment)
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
                    let query = SqliteQueryHelper::get_auditcard_insert_query();
                    sqlx::query(&query)
                        .bind(&audit.uid)
                        .bind(&audit.app_env)
                        .bind(&audit.name)
                        .bind(&audit.repository)
                        .bind(audit.major)
                        .bind(audit.minor)
                        .bind(audit.patch)
                        .bind(&audit.version)
                        .bind(&audit.contact)
                        .bind(&audit.tags)
                        .bind(audit.approved)
                        .bind(&audit.datacard_uids)
                        .bind(&audit.modelcard_uids)
                        .bind(&audit.runcard_uids)
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
            CardTable::Pipeline => match card {
                ServerCard::Pipeline(pipeline) => {
                    let query = SqliteQueryHelper::get_pipelinecard_insert_query();
                    sqlx::query(&query)
                        .bind(&pipeline.uid)
                        .bind(&pipeline.app_env)
                        .bind(&pipeline.name)
                        .bind(&pipeline.repository)
                        .bind(pipeline.major)
                        .bind(pipeline.minor)
                        .bind(pipeline.patch)
                        .bind(&pipeline.version)
                        .bind(&pipeline.contact)
                        .bind(&pipeline.tags)
                        .bind(&pipeline.pipeline_code_uri)
                        .bind(&pipeline.datacard_uids)
                        .bind(&pipeline.modelcard_uids)
                        .bind(&pipeline.runcard_uids)
                        .bind(&pipeline.pre_tag)
                        .bind(&pipeline.build_tag)
                        .bind(&pipeline.username)
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
            CardTable::Project => match card {
                ServerCard::Project(project) => {
                    let query = SqliteQueryHelper::get_projectcard_insert_query();
                    sqlx::query(&query)
                        .bind(&project.uid)
                        .bind(&project.name)
                        .bind(&project.repository)
                        .bind(project.project_id)
                        .bind(project.major)
                        .bind(project.minor)
                        .bind(project.patch)
                        .bind(&project.version)
                        .bind(&project.pre_tag)
                        .bind(&project.build_tag)
                        .bind(&project.username)
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
                    let query = SqliteQueryHelper::get_datacard_update_query();
                    sqlx::query(&query)
                        .bind(&data.app_env)
                        .bind(&data.name)
                        .bind(&data.repository)
                        .bind(data.major)
                        .bind(data.minor)
                        .bind(data.patch)
                        .bind(&data.version)
                        .bind(&data.contact)
                        .bind(&data.data_type)
                        .bind(&data.interface_type)
                        .bind(&data.tags)
                        .bind(&data.runcard_uid)
                        .bind(&data.pipelinecard_uid)
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
                    let query = SqliteQueryHelper::get_modelcard_update_query();
                    sqlx::query(&query)
                        .bind(&model.app_env)
                        .bind(&model.name)
                        .bind(&model.repository)
                        .bind(model.major)
                        .bind(model.minor)
                        .bind(model.patch)
                        .bind(&model.version)
                        .bind(&model.contact)
                        .bind(&model.datacard_uid)
                        .bind(&model.data_type)
                        .bind(&model.model_type)
                        .bind(&model.interface_type)
                        .bind(&model.task_type)
                        .bind(&model.tags)
                        .bind(&model.runcard_uid)
                        .bind(&model.pipelinecard_uid)
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
            CardTable::Run => match card {
                ServerCard::Run(run) => {
                    let query = SqliteQueryHelper::get_runcard_update_query();
                    sqlx::query(&query)
                        .bind(&run.app_env)
                        .bind(&run.name)
                        .bind(&run.repository)
                        .bind(run.major)
                        .bind(run.minor)
                        .bind(run.patch)
                        .bind(&run.version)
                        .bind(&run.contact)
                        .bind(&run.project)
                        .bind(&run.tags)
                        .bind(&run.datacard_uids)
                        .bind(&run.modelcard_uids)
                        .bind(&run.pipelinecard_uid)
                        .bind(&run.artifact_uris)
                        .bind(&run.compute_environment)
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
                    let query = SqliteQueryHelper::get_auditcard_update_query();
                    sqlx::query(&query)
                        .bind(&audit.app_env)
                        .bind(&audit.name)
                        .bind(&audit.repository)
                        .bind(audit.major)
                        .bind(audit.minor)
                        .bind(audit.patch)
                        .bind(&audit.version)
                        .bind(&audit.contact)
                        .bind(&audit.tags)
                        .bind(audit.approved)
                        .bind(&audit.datacard_uids)
                        .bind(&audit.modelcard_uids)
                        .bind(&audit.runcard_uids)
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
            CardTable::Pipeline => match card {
                ServerCard::Pipeline(pipeline) => {
                    let query = SqliteQueryHelper::get_pipelinecard_update_query();
                    sqlx::query(&query)
                        .bind(&pipeline.app_env)
                        .bind(&pipeline.name)
                        .bind(&pipeline.repository)
                        .bind(pipeline.major)
                        .bind(pipeline.minor)
                        .bind(pipeline.patch)
                        .bind(&pipeline.version)
                        .bind(&pipeline.contact)
                        .bind(&pipeline.tags)
                        .bind(&pipeline.pipeline_code_uri)
                        .bind(&pipeline.datacard_uids)
                        .bind(&pipeline.modelcard_uids)
                        .bind(&pipeline.runcard_uids)
                        .bind(&pipeline.pre_tag)
                        .bind(&pipeline.build_tag)
                        .bind(&pipeline.username)
                        .bind(&pipeline.uid)
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

    /// Query stats for a table
    ///
    /// # Arguments
    ///
    /// * `table` - The table to query
    /// * `search_term` - The search term to query
    ///
    /// # Returns
    ///
    /// * `HashMap<String, i32>` - A hashmap of the stats
    ///
    async fn query_stats(
        &self,
        table: &CardTable,
        search_term: Option<&str>,
    ) -> Result<QueryStats, SqlError> {
        let query = SqliteQueryHelper::get_query_stats_query(table);

        // if search_term is not None, format with %search_term%, else None
        let stats: QueryStats = sqlx::query_as(&query)
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
        let query = SqliteQueryHelper::get_query_page_query(table, sort_by);

        let lower_bound = page * 30;
        let upper_bound = lower_bound + 30;

        let records: Vec<CardSummary> = sqlx::query_as(&query)
            .bind(repository)
            .bind(search_term)
            .bind(search_term.map(|term| format!("%{}%", term)))
            .bind(lower_bound)
            .bind(upper_bound)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(records)
    }

    async fn delete_card(&self, table: &CardTable, uid: &str) -> Result<(), SqlError> {
        let query = format!("DELETE FROM {} WHERE uid = ?1", table);
        sqlx::query(&query)
            .bind(uid)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_project_id(&self, project_name: &str, repository: &str) -> Result<i32, SqlError> {
        let query = SqliteQueryHelper::get_project_id_query();

        let project_id: i32 = sqlx::query_scalar(&query)
            .bind(project_name)
            .bind(repository)
            .fetch_one(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(project_id)
    }

    async fn insert_run_metric(&self, record: &MetricRecord) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_run_metric_insert_query();

        sqlx::query(&query)
            .bind(&record.run_uid)
            .bind(&record.name)
            .bind(record.value)
            .bind(record.step)
            .bind(record.timestamp)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn insert_run_metrics<'life1>(
        &self,
        records: &'life1 [MetricRecord],
    ) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_run_metrics_insert_query(records.len());

        let mut query_builder = sqlx::query(&query);

        for r in records {
            query_builder = query_builder
                .bind(&r.run_uid)
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

    async fn get_run_metric<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<MetricRecord>, SqlError> {
        let (query, bindings) = SqliteQueryHelper::get_run_metric_query(names);
        let mut query_builder = sqlx::query_as::<sqlx::Sqlite, MetricRecord>(&query).bind(uid);

        for binding in bindings {
            query_builder = query_builder.bind(binding);
        }

        let records: Vec<MetricRecord> = query_builder
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(records)
    }

    async fn get_run_metric_names(&self, uid: &str) -> Result<Vec<String>, SqlError> {
        let query = format!(
            "SELECT DISTINCT name FROM {} WHERE run_uid = ?1",
            CardTable::Metrics
        );

        let records: Vec<String> = sqlx::query_scalar(&query)
            .bind(uid)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(records)
    }

    async fn insert_hardware_metrics<'life1>(
        &self,
        record: &'life1 [HardwareMetricsRecord],
    ) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_hardware_metrics_insert_query(record.len());

        let mut query_builder = sqlx::query(&query);

        for r in record {
            query_builder = query_builder
                .bind(&r.run_uid)
                .bind(r.created_at)
                .bind(r.cpu_percent_utilization)
                .bind(&r.cpu_percent_per_core)
                .bind(r.compute_overall)
                .bind(r.compute_utilized)
                .bind(r.load_avg)
                .bind(r.sys_ram_total)
                .bind(r.sys_ram_used)
                .bind(r.sys_ram_available)
                .bind(r.sys_ram_percent_used)
                .bind(r.sys_swap_total)
                .bind(r.sys_swap_used)
                .bind(r.sys_swap_free)
                .bind(r.sys_swap_percent)
                .bind(r.bytes_recv)
                .bind(r.bytes_sent)
                .bind(r.gpu_percent_utilization)
                .bind(&r.gpu_percent_per_core);
        }

        query_builder
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_hardware_metric(&self, uid: &str) -> Result<Vec<HardwareMetricsRecord>, SqlError> {
        let query = SqliteQueryHelper::get_hardware_metric_query();

        let records: Vec<HardwareMetricsRecord> = sqlx::query_as(&query)
            .bind(uid)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(records)
    }

    async fn insert_run_parameters<'life1>(
        &self,
        records: &'life1 [ParameterRecord],
    ) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_run_parameters_insert_query(records.len());

        let mut query_builder = sqlx::query(&query);

        for record in records {
            query_builder = query_builder
                .bind(&record.run_uid)
                .bind(&record.name)
                .bind(&record.value);
        }

        query_builder
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_run_parameter<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<ParameterRecord>, SqlError> {
        let (query, bindings) = SqliteQueryHelper::get_run_parameter_query(names);
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
        let query = SqliteQueryHelper::get_user_insert_query();

        let group_permissions = serde_json::to_string(&user.group_permissions)
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        let permissions = serde_json::to_string(&user.permissions)
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        sqlx::query(&query)
            .bind(&user.username)
            .bind(&user.password_hash)
            .bind(&permissions)
            .bind(&group_permissions)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_user(&self, username: &str) -> Result<User, SqlError> {
        let query = SqliteQueryHelper::get_user_query();

        let user: User = sqlx::query_as(&query)
            .bind(username)
            .fetch_one(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(user)
    }
    async fn update_user(&self, user: &User) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_user_update_query();
        let group_permissions = serde_json::to_string(&user.group_permissions)
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        let permissions = serde_json::to_string(&user.permissions)
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

    async fn insert_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_artifact_key_insert_query();
        sqlx::query(&query)
            .bind(&key.uid)
            .bind(&key.card_type.to_string())
            .bind(key.encrypt_key.clone())
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }

    async fn get_artifact_key(&self, uid: &str, card_type: &str) -> Result<ArtifactKey, SqlError> {
        let query = SqliteQueryHelper::get_artifact_key_select_query();

        let key: ArtifactKey = sqlx::query_as(&query)
            .bind(uid)
            .bind(card_type)
            .fetch_one(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(key)
    }

    async fn update_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_artifact_key_update_query();
        sqlx::query(&query)
            .bind(key.encrypt_key.clone())
            .bind(&key.uid)
            .bind(&key.card_type.to_string())
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
        let query = SqliteQueryHelper::get_operation_insert_query();
        sqlx::query(&query)
            .bind(username)
            .bind(access_type)
            .bind(access_location)
            .execute(&self.pool)
            .await
            .map_err(|e| SqlError::QueryError(format!("{}", e)))?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {

    use super::*;

    use opsml_types::{cards::CardType, contracts::Operation, SqlType};
    use opsml_utils::utils::get_utc_datetime;
    use std::env;

    fn get_connection_uri() -> String {
        let mut current_dir = env::current_dir().expect("Failed to get current directory");
        current_dir.push("test.db");
        format!(
            "sqlite://{}",
            current_dir
                .to_str()
                .expect("Failed to convert path to string")
        )
    }

    pub fn cleanup() {
        // delete ./test.db if exists
        let mut current_dir = env::current_dir().expect("Failed to get current directory");
        current_dir.push("test.db");
        let _ = std::fs::remove_file(current_dir);
    }

    #[tokio::test]
    async fn test_sqlite() {
        let config = DatabaseSettings {
            connection_uri: "sqlite::memory:".to_string(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let _client = SqliteClient::new(&config).await;
    }

    // create test for non-memory sqlite

    #[tokio::test]
    async fn test_sqlite_versions() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

        // query all versions
        // get versions (should return 1)
        let versions = client
            .get_versions(&CardTable::Data, "Data1", "repo1", None)
            .await
            .unwrap();
        assert_eq!(versions.len(), 10);

        // check star pattern
        let versions = client
            .get_versions(&CardTable::Data, "Data1", "repo1", Some("*"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 10);

        let versions = client
            .get_versions(&CardTable::Data, "Data1", "repo1", Some("1.*"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 4);

        let versions = client
            .get_versions(&CardTable::Data, "Data1", "repo1", Some("1.1.*"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        // check tilde pattern
        let versions = client
            .get_versions(&CardTable::Data, "Data1", "repo1", Some("~1"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 4);

        // check tilde pattern
        let versions = client
            .get_versions(&CardTable::Data, "Data1", "repo1", Some("~1.1"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        // check tilde pattern
        let versions = client
            .get_versions(&CardTable::Data, "Data1", "repo1", Some("~1.1.1"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 1);

        let versions = client
            .get_versions(&CardTable::Data, "Data1", "repo1", Some("^2.0.0"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        let versions = client
            .get_versions(&CardTable::Data, "Data1", "repo1", Some("2.0.0"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 1);

        let versions = client
            .get_versions(&CardTable::Data, "Data1", "repo1", Some("2"))
            .await
            .unwrap();

        assert_eq!(versions.len(), 4);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_query_cards() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

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
            .query_cards(&CardTable::Run, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 2);

        // try tags
        let tags = ["key1".to_string()].iter().cloned().collect();
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

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_insert_cards() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();
        let data_card = DataCardRecord::default();
        let card = ServerCard::Data(data_card.clone());

        client.insert_card(&CardTable::Data, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(data_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // insert modelcard
        let model_card = ModelCardRecord::default();
        let card = ServerCard::Model(model_card.clone());

        client.insert_card(&CardTable::Model, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(model_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardTable::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // insert runcard
        let run_card = RunCardRecord::default();
        let card = ServerCard::Run(run_card.clone());

        client.insert_card(&CardTable::Run, &card).await.unwrap();

        // check if the card was inserted

        let card_args = CardQueryArgs {
            uid: Some(run_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardTable::Run, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // insert auditcard

        let audit_card = AuditCardRecord::default();
        let card = ServerCard::Audit(audit_card.clone());

        client.insert_card(&CardTable::Audit, &card).await.unwrap();

        // check if the card was inserted

        let card_args = CardQueryArgs {
            uid: Some(audit_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardTable::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // check pipeline card
        let pipeline_card = PipelineCardRecord::default();
        let card = ServerCard::Pipeline(pipeline_card.clone());

        client
            .insert_card(&CardTable::Pipeline, &card)
            .await
            .unwrap();

        // check if the card was inserted

        let card_args = CardQueryArgs {
            uid: Some(pipeline_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardTable::Pipeline, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_update_cards() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Test DataCardRecord
        let mut data_card = DataCardRecord::default();
        let card = ServerCard::Data(data_card.clone());

        client.insert_card(&CardTable::Data, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(data_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        data_card.name = "UpdatedDataName".to_string();
        let updated_card = ServerCard::Data(data_card.clone());

        client
            .update_card(&CardTable::Data, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Data(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedDataName");
        }

        // Test ModelCardRecord
        let mut model_card = ModelCardRecord::default();
        let card = ServerCard::Model(model_card.clone());

        client.insert_card(&CardTable::Model, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(model_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        model_card.name = "UpdatedModelName".to_string();
        let updated_card = ServerCard::Model(model_card.clone());

        client
            .update_card(&CardTable::Model, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardTable::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Model(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedModelName");
        }

        // Test RunCardRecord
        let mut run_card = RunCardRecord::default();
        let card = ServerCard::Run(run_card.clone());

        client.insert_card(&CardTable::Run, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(run_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Run, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        run_card.name = "UpdatedRunName".to_string();
        let updated_card = ServerCard::Run(run_card.clone());

        client
            .update_card(&CardTable::Run, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardTable::Run, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Run(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedRunName");
        }

        // Test AuditCardRecord
        let mut audit_card = AuditCardRecord::default();
        let card = ServerCard::Audit(audit_card.clone());

        client.insert_card(&CardTable::Audit, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(audit_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        audit_card.name = "UpdatedAuditName".to_string();
        let updated_card = ServerCard::Audit(audit_card.clone());

        client
            .update_card(&CardTable::Audit, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardTable::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Audit(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedAuditName");
        }

        // Test PipelineCardRecord
        let mut pipeline_card = PipelineCardRecord::default();
        let card = ServerCard::Pipeline(pipeline_card.clone());

        client
            .insert_card(&CardTable::Pipeline, &card)
            .await
            .unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(pipeline_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Pipeline, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        pipeline_card.name = "UpdatedPipelineName".to_string();
        let updated_card = ServerCard::Pipeline(pipeline_card.clone());

        client
            .update_card(&CardTable::Pipeline, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardTable::Pipeline, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Pipeline(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedPipelineName");
        }

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_unique_repos() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

        // get unique repository names
        let repos = client
            .get_unique_repository_names(&CardTable::Model)
            .await
            .unwrap();

        assert_eq!(repos.len(), 10);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_query_stats() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

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

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_query_page() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

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
            .query_page("name", 0, None, Some("repo3"), &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_delete_card() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

        // delete card

        let args = CardQueryArgs {
            uid: None,
            name: Some("Data1".to_string()),
            repository: Some("repo1".to_string()),
            ..Default::default()
        };

        let cards = client.query_cards(&CardTable::Data, &args).await.unwrap();

        let uid = match cards {
            CardResults::Data(cards) => cards[0].uid.clone(),
            _ => "".to_string(),
        };

        assert!(!uid.is_empty());

        // delete the card
        client.delete_card(&CardTable::Data, &uid).await.unwrap();

        // check if the card was deleted
        let args = CardQueryArgs {
            uid: Some(uid),
            ..Default::default()
        };

        let results = client.query_cards(&CardTable::Data, &args).await.unwrap();

        assert_eq!(results.len(), 0);
    }

    #[tokio::test]
    async fn test_sqlite_project_id() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

        // get project id

        let project_id = client.get_project_id("test", "repo").await.unwrap();
        assert_eq!(project_id, 1);

        // get next project id
        let project_id = client.get_project_id("test1", "repo").await.unwrap();

        assert_eq!(project_id, 2);

        let args = CardQueryArgs {
            uid: None,
            name: Some("test".to_string()),
            repository: Some("repo".to_string()),
            ..Default::default()
        };
        let cards = client
            .query_cards(&CardTable::Project, &args)
            .await
            .unwrap();

        assert_eq!(cards.len(), 1);
        cleanup();
    }

    // test run metric
    #[tokio::test]
    async fn test_sqlite_run_metric() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();

        sqlx::query(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let metric_names = vec!["metric1", "metric2", "metric3"];

        for name in metric_names {
            let metric = MetricRecord {
                run_uid: uid.clone(),
                name: name.to_string(),
                value: 1.0,
                ..Default::default()
            };

            client.insert_run_metric(&metric).await.unwrap();
        }

        let records = client.get_run_metric(&uid, &Vec::new()).await.unwrap();
        let names = client.get_run_metric_names(&uid).await.unwrap();

        assert_eq!(records.len(), 3);

        // assert names = "metric1"
        assert_eq!(names.len(), 3);

        // insert vec
        let records = vec![
            MetricRecord {
                run_uid: uid.clone(),
                name: "vec1".to_string(),
                value: 1.0,
                ..Default::default()
            },
            MetricRecord {
                run_uid: uid.clone(),
                name: "vec2".to_string(),
                value: 1.0,
                ..Default::default()
            },
        ];

        client.insert_run_metrics(&records).await.unwrap();

        let records = client.get_run_metric(&uid, &Vec::new()).await.unwrap();

        assert_eq!(records.len(), 5);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_hardware_metric() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();

        sqlx::query(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let mut metrics = vec![];

        // create a loop of 10
        for _ in 0..10 {
            let metric = HardwareMetricsRecord {
                run_uid: uid.clone(),
                created_at: get_utc_datetime(),
                ..Default::default()
            };
            metrics.push(metric.clone());
        }

        client.insert_hardware_metrics(&metrics).await.unwrap();
        let records = client.get_hardware_metric(&uid).await.unwrap();

        assert_eq!(records.len(), 10);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_parameter() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();

        sqlx::query(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let mut params = vec![];

        // create a loop of 10
        for i in 0..10 {
            let parameter = ParameterRecord {
                run_uid: uid.clone(),
                name: format!("param{}", i),
                ..Default::default()
            };

            params.push(parameter.clone());
        }

        client.insert_run_parameters(&params).await.unwrap();
        let records = client.get_run_parameter(&uid, &Vec::new()).await.unwrap();

        assert_eq!(records.len(), 10);

        let param_records = client
            .get_run_parameter(&uid, &["param1".to_string()])
            .await
            .unwrap();

        assert_eq!(param_records.len(), 1);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_user() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        let user = User::new("user".to_string(), "pass".to_string(), None, None);
        client.insert_user(&user).await.unwrap();

        let mut user = client.get_user("user").await.unwrap();
        assert_eq!(user.username, "user");

        // update user
        user.active = false;
        user.refresh_token = Some("token".to_string());

        client.update_user(&user).await.unwrap();
        let user = client.get_user("user").await.unwrap();
        assert!(!user.active);
        assert_eq!(user.refresh_token.unwrap(), "token");

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_artifact_keys() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        let encrypt_key: Vec<u8> = (0..32).collect();

        let key = ArtifactKey {
            uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
            card_type: CardType::Data.to_string(),
            encrypt_key: encrypt_key.clone(),
        };

        client.insert_artifact_key(&key).await.unwrap();

        let key = client
            .get_artifact_key(&key.uid, &key.card_type)
            .await
            .unwrap();

        assert_eq!(key.uid, "550e8400-e29b-41d4-a716-446655440000");

        // update key
        let encrypt_key: Vec<u8> = (32..64).collect();
        let key = ArtifactKey {
            uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
            card_type: CardType::Data.to_string(),
            encrypt_key: encrypt_key.clone(),
        };

        client.update_artifact_key(&key).await.unwrap();

        let key = client
            .get_artifact_key(&key.uid, &key.card_type)
            .await
            .unwrap();

        assert_eq!(key.encrypt_key, encrypt_key);
    }

    #[tokio::test]
    async fn test_sqlite_insert_operation() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

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
}
