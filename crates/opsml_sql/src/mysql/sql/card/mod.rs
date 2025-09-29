use crate::mysql::helper::MySqlQueryHelper;
use opsml_types::cards::CardTable;

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
use sqlx::{MySql, Pool};
use std::collections::HashSet;

/// Generic function to query cards from the database
async fn query_cards_generic<T>(
    pool: &sqlx::Pool<MySql>,
    query: &str,
    query_args: &CardQueryArgs,
    default_limit: i32,
) -> Result<Vec<T>, SqlError>
where
    T: for<'r> sqlx::FromRow<'r, sqlx::mysql::MySqlRow> + Send + Unpin,
{
    let mut query_builder = sqlx::query_as::<_, T>(query)
        .bind(query_args.uid.as_ref())
        .bind(query_args.uid.as_ref())
        .bind(query_args.space.as_ref())
        .bind(query_args.space.as_ref())
        .bind(query_args.name.as_ref())
        .bind(query_args.name.as_ref())
        .bind(query_args.max_date.as_ref())
        .bind(query_args.max_date.as_ref());

    if let Some(tags) = &query_args.tags {
        for tag in tags {
            query_builder = query_builder.bind(format!("\"{}\"", tag));
        }
    }
    query_builder = query_builder.bind(query_args.limit.unwrap_or(default_limit));
    let records = query_builder.fetch_all(pool).await?;
    Ok(records)
}

#[derive(Debug, Clone)]
pub struct CardLogicMySqlClient {
    pool: sqlx::Pool<MySql>,
}
impl CardLogicMySqlClient {
    pub fn new(pool: &Pool<MySql>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl CardLogicTrait for CardLogicMySqlClient {
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
        let query = MySqlQueryHelper::get_uid_query(table);
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
        let query = MySqlQueryHelper::get_versions_query(table, version)?;
        let cards: Vec<VersionResult> = sqlx::query_as(&query)
            .bind(name)
            .bind(space)
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
        let query = MySqlQueryHelper::get_query_cards_query(table, query_args)?;

        match table {
            CardTable::Data => {
                let cards =
                    query_cards_generic::<DataCardRecord>(&self.pool, &query, query_args, 50)
                        .await?;
                Ok(CardResults::Data(cards))
            }
            CardTable::Model => {
                let cards =
                    query_cards_generic::<ModelCardRecord>(&self.pool, &query, query_args, 50)
                        .await?;
                Ok(CardResults::Model(cards))
            }
            CardTable::Experiment => {
                let cards =
                    query_cards_generic::<ExperimentCardRecord>(&self.pool, &query, query_args, 50)
                        .await?;
                Ok(CardResults::Experiment(cards))
            }
            CardTable::Audit => {
                let cards =
                    query_cards_generic::<AuditCardRecord>(&self.pool, &query, query_args, 50)
                        .await?;
                Ok(CardResults::Audit(cards))
            }
            CardTable::Prompt => {
                let cards =
                    query_cards_generic::<PromptCardRecord>(&self.pool, &query, query_args, 50)
                        .await?;
                Ok(CardResults::Prompt(cards))
            }
            CardTable::Service | CardTable::Mcp => {
                let cards =
                    query_cards_generic::<ServiceCardRecord>(&self.pool, &query, query_args, 1000)
                        .await?;
                Ok(CardResults::Service(cards))
            }
            _ => Err(SqlError::InvalidTableName),
        }
    }

    async fn insert_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError> {
        match table {
            CardTable::Data => match card {
                ServerCard::Data(record) => {
                    let query = MySqlQueryHelper::get_datacard_insert_query();
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
                    let query = MySqlQueryHelper::get_modelcard_insert_query();
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
                    let query = MySqlQueryHelper::get_experimentcard_insert_query();
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
                    let query = MySqlQueryHelper::get_auditcard_insert_query();
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
                    let query = MySqlQueryHelper::get_promptcard_insert_query();
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

            CardTable::Service | CardTable::Mcp => match card {
                ServerCard::Service(record) => {
                    let query = MySqlQueryHelper::get_servicecard_insert_query(table);
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
                        .bind(&record.service_config)
                        .bind(&record.tags)
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
                    let query = MySqlQueryHelper::get_datacard_update_query();
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
                    let query = MySqlQueryHelper::get_modelcard_update_query();
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
                    let query = MySqlQueryHelper::get_experimentcard_update_query();
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
                    let query = MySqlQueryHelper::get_auditcard_update_query();
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
                    let query = MySqlQueryHelper::get_promptcard_update_query();
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

            CardTable::Service | CardTable::Mcp => match card {
                ServerCard::Service(record) => {
                    let query = MySqlQueryHelper::get_servicecard_update_query(table);
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
                        .bind(&record.service_config)
                        .bind(&record.tags)
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

    async fn get_unique_tags(&self, table: &CardTable) -> Result<Vec<String>, SqlError> {
        let query = format!(
            r#"
            SELECT DISTINCT jt.tag AS tag
            FROM {table}
            JOIN JSON_TABLE(
                {table}.tags,
                '$[*]' COLUMNS(tag VARCHAR(255) PATH '$')
            ) AS jt
            WHERE {table}.tags IS NOT NULL
            "#
        );
        let rows: Vec<(String,)> = sqlx::query_as(&query).fetch_all(&self.pool).await?;

        let unique_tags: HashSet<String> = rows.into_iter().map(|(tag,)| tag).collect();
        Ok(unique_tags.into_iter().collect())
    }

    async fn query_stats(
        &self,
        table: &CardTable,
        search_term: Option<&str>,
        spaces: &[String],
        tags: &[String],
    ) -> Result<QueryStats, SqlError> {
        let query = MySqlQueryHelper::get_query_stats_query(table, spaces, tags);

        let mut stats_query = sqlx::query_as(&query)
            .bind(search_term)
            .bind(search_term.map(|term| format!("%{term}%")))
            .bind(search_term.map(|term| format!("%{term}%")));

        for space in spaces {
            stats_query = stats_query.bind(space);
        }

        for tag in tags {
            stats_query = stats_query.bind(format!("\"{}\"", tag));
        }

        let stats = stats_query.fetch_one(&self.pool).await?;
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
        spaces: &[String],
        tags: &[String],
        table: &CardTable,
    ) -> Result<Vec<CardSummary>, SqlError> {
        let query = MySqlQueryHelper::get_query_page_query(table, sort_by, spaces, tags);

        let lower_bound = (page * 30) - 30;
        let upper_bound = page * 30;

        // start query for first cte
        let mut records = sqlx::query_as(&query)
            .bind(search_term) // 3rd ? in versions_cte
            .bind(search_term.map(|term| format!("%{term}%"))) // 4th ? in versions_cte
            .bind(search_term.map(|term| format!("%{term}%"))); // 5th ? in versions_cte

        for space in spaces {
            records = records.bind(space);
        }

        // bind tags for first cte
        for tag in tags {
            records = records.bind(format!("\"{}\"", tag));
        }

        // 2nd cte
        records = records
            .bind(search_term) // 3rd ? in stats_cte
            .bind(search_term.map(|term| format!("%{term}%"))) // 4th ? in stats_cte
            .bind(search_term.map(|term| format!("%{term}%"))); // 5th ? in stats_cte

        for space in spaces {
            records = records.bind(space);
        }

        // bind tags for 2nd cte
        for tag in tags {
            records = records.bind(format!("\"{}\"", tag));
        }

        // final select
        let records: Vec<CardSummary> = records
            .bind(lower_bound) // 1st ? in final SELECT
            .bind(upper_bound)
            .fetch_all(&self.pool)
            .await
            .unwrap();

        Ok(records)
    }

    async fn version_page(
        &self,
        page: i32,
        space: Option<&str>,
        name: Option<&str>,
        table: &CardTable,
    ) -> Result<Vec<VersionSummary>, SqlError> {
        let query = MySqlQueryHelper::get_version_page_query(table);

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
        let select_query = format!("SELECT space, name FROM {table} WHERE uid = ?");
        let (space, name): (String, String) = sqlx::query_as(&select_query)
            .bind(uid)
            .fetch_one(&self.pool)
            .await?;

        // Then delete the record
        let delete_query = format!("DELETE FROM {table} WHERE uid = ?");
        sqlx::query(&delete_query)
            .bind(uid)
            .execute(&self.pool)
            .await?;

        Ok((space, name))
    }

    async fn get_card_key_for_loading(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<ArtifactKey, SqlError> {
        let query = MySqlQueryHelper::get_load_card_query(table, query_args)?;

        let key: (String, String, String, Vec<u8>, String) = sqlx::query_as(&query)
            .bind(query_args.uid.as_ref())
            .bind(query_args.uid.as_ref())
            .bind(query_args.space.as_ref())
            .bind(query_args.space.as_ref())
            .bind(query_args.name.as_ref())
            .bind(query_args.name.as_ref())
            .bind(query_args.max_date.as_ref())
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
        let query = MySqlQueryHelper::get_recent_services_query(query_args);

        let records: Vec<ServiceCardRecord> = sqlx::query_as(&query)
            .bind(query_args.space.as_ref())
            .bind(query_args.space.as_ref())
            .bind(query_args.name.as_ref())
            .bind(query_args.name.as_ref())
            .fetch_all(&self.pool)
            .await?;

        Ok(records)
    }
}
