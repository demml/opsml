use crate::postgres::helper::PostgresQueryHelper;
use opsml_types::cards::CardTable;
use tracing::instrument;

use crate::error::SqlError;
use crate::schemas::schema::{
    AuditCardRecord, CardResults, CardSummary, DataCardRecord, ExperimentCardRecord,
    ModelCardRecord, PromptCardRecord, QueryStats, ServerCard, ServiceCardRecord, VersionResult,
    VersionSummary,
};

use crate::traits::CardLogicTrait;
use async_trait::async_trait;
use opsml_semver::VersionValidator;
use opsml_types::{
    contracts::{ArtifactKey, CardQueryArgs, ServiceQueryArgs},
    RegistryType,
};
use semver::Version;
use sqlx::{Pool, Postgres};
use tracing::debug;

#[derive(Debug, Clone)]
pub struct CardLogicPostgresClient {
    pool: sqlx::Pool<Postgres>,
}
impl CardLogicPostgresClient {
    pub fn new(pool: &Pool<Postgres>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl CardLogicTrait for CardLogicPostgresClient {
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
                    .bind(query_args.service_type.as_ref())
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
                        .bind(&record.service_type)
                        .bind(&record.metadata)
                        .bind(&record.deployment)
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
                        .bind(&record.service_type)
                        .bind(&record.metadata)
                        .bind(&record.deployment)
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
    #[instrument(skip_all)]
    async fn get_card_key_for_loading(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<ArtifactKey, SqlError> {
        let query = PostgresQueryHelper::get_load_card_query(table, query_args)?;
        debug!("Executing query: {}", query);

        let key: (String, String, String, Vec<u8>, String) = sqlx::query_as(&query)
            .bind(query_args.uid.as_ref())
            .bind(query_args.space.as_ref())
            .bind(query_args.name.as_ref())
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

    async fn get_recent_services(
        &self,
        query_args: &ServiceQueryArgs,
    ) -> Result<Vec<ServiceCardRecord>, SqlError> {
        let query = PostgresQueryHelper::get_recent_services_query(query_args);

        let records: Vec<ServiceCardRecord> = sqlx::query_as(&query)
            .bind(query_args.space.as_ref())
            .bind(query_args.name.as_ref())
            .bind(query_args.service_type.as_ref())
            .fetch_all(&self.pool)
            .await?;

        Ok(records)
    }
}
