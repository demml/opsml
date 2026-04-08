use crate::mysql::helper::MySqlQueryHelper;
use opsml_types::cards::CardTable;
use opsml_types::contracts::CardArgs;

use crate::error::SqlError;
use crate::schemas::schema::{
    AuditCardRecord, CardResults, CardSummary, DataCardRecord, ExperimentCardRecord,
    ModelCardRecord, PromptCardRecord, QueryStats, ServerCard, ServiceCardRecord, SkillCardRecord,
    SubAgentCardRecord, ToolCardRecord, VersionResult, VersionSummary,
};
use crate::traits::{CardLogicTrait, SkillLogicTrait, SubAgentLogicTrait, ToolLogicTrait};
use async_trait::async_trait;
use opsml_semver::VersionValidator;
use opsml_types::contracts::skill::MarketplaceStats;
use opsml_types::{
    RegistryType,
    contracts::{ArtifactKey, CardQueryArgs, DashboardStats, ServiceQueryArgs, VersionCursor},
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

    /// Helper for comparing content hash for cards. Mainly used for cli work to determine if card has changed before
    /// registering a new version or not.
    /// # Arguments
    /// * `table` - The table to query
    /// * `content_hash` - The content hash to compare
    /// # Returns
    /// * `bool` - True if the content hash matches an existing card, false otherwise
    async fn compare_hash(
        &self,
        table: &CardTable,
        content_hash: &[u8],
        space: Option<&str>,
        name: Option<&str>,
    ) -> Result<Option<CardArgs>, SqlError> {
        let mut query = format!(
            "SELECT space, name, version, uid, app_env, created_at FROM {} WHERE content_hash = ?",
            table
        );

        if space.is_some() {
            query.push_str(" AND space = ?");
        }
        if name.is_some() {
            query.push_str(" AND name = ?");
        }
        query.push_str(" ORDER BY created_at DESC LIMIT 1");

        let mut q = sqlx::query_as(&query).bind(content_hash);
        if let Some(s) = space {
            q = q.bind(s);
        }
        if let Some(n) = name {
            q = q.bind(n);
        }

        let exists: Option<CardArgs> = q.fetch_optional(&self.pool).await?;

        Ok(exists)
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
            CardTable::Service | CardTable::Mcp | CardTable::Agent => {
                let cards =
                    query_cards_generic::<ServiceCardRecord>(&self.pool, &query, query_args, 1000)
                        .await?;
                Ok(CardResults::Service(cards))
            }
            CardTable::Skill => {
                let cards =
                    query_cards_generic::<SkillCardRecord>(&self.pool, &query, query_args, 50)
                        .await?;
                Ok(CardResults::Skill(cards))
            }
            CardTable::SubAgent => {
                let cards =
                    query_cards_generic::<SubAgentCardRecord>(&self.pool, &query, query_args, 50)
                        .await?;
                Ok(CardResults::SubAgent(cards))
            }
            CardTable::Tool => {
                let cards =
                    query_cards_generic::<ToolCardRecord>(&self.pool, &query, query_args, 50)
                        .await?;
                Ok(CardResults::Tool(cards))
            }
            _ => Err(SqlError::InvalidTableName),
        }
    }

    async fn insert_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError> {
        match table {
            CardTable::Data => match card {
                ServerCard::Data(record) => {
                    let query = MySqlQueryHelper::get_datacard_insert_query();
                    sqlx::query(query)
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
                    sqlx::query(query)
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
                    sqlx::query(query)
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
                        .bind(&record.status)
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
                    sqlx::query(query)
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
                    sqlx::query(query)
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
                        .bind(&record.content_hash)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }

                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            CardTable::Service | CardTable::Mcp | CardTable::Agent => match card {
                ServerCard::Service(record) => {
                    let query = MySqlQueryHelper::get_servicecard_insert_query(table);
                    sqlx::query(query)
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
                        .bind(&record.content_hash)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            CardTable::Skill => match card {
                ServerCard::Skill(record) => {
                    let query = MySqlQueryHelper::get_skillcard_insert_query();
                    sqlx::query(query)
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
                        .bind(&record.tags)
                        .bind(&record.compatible_tools)
                        .bind(&record.dependencies)
                        .bind(&record.description)
                        .bind(&record.license)
                        .bind(&record.content_hash)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(&record.input_schema)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            CardTable::SubAgent => match card {
                ServerCard::SubAgent(record) => {
                    let query = MySqlQueryHelper::get_subagent_card_insert_query();
                    sqlx::query(query)
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
                        .bind(&record.tags)
                        .bind(&record.compatible_clis)
                        .bind(&record.description)
                        .bind(&record.content_hash)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(record.download_count)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            CardTable::Tool => match card {
                ServerCard::Tool(record) => {
                    let query = MySqlQueryHelper::get_tool_card_insert_query();
                    sqlx::query(query)
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
                        .bind(&record.tags)
                        .bind(&record.tool_type)
                        .bind(&record.args_schema)
                        .bind(&record.description)
                        .bind(&record.content_hash)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(record.download_count)
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
                    sqlx::query(query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(&record.data_type)
                        .bind(&record.interface_type)
                        .bind(&record.tags)
                        .bind(&record.experimentcard_uid)
                        .bind(&record.auditcard_uid)
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
                    sqlx::query(query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(&record.datacard_uid)
                        .bind(&record.data_type)
                        .bind(&record.model_type)
                        .bind(&record.interface_type)
                        .bind(&record.task_type)
                        .bind(&record.tags)
                        .bind(&record.experimentcard_uid)
                        .bind(&record.auditcard_uid)
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
                    sqlx::query(query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(&record.tags)
                        .bind(&record.datacard_uids)
                        .bind(&record.modelcard_uids)
                        .bind(&record.promptcard_uids)
                        .bind(&record.service_card_uids)
                        .bind(&record.experimentcard_uids)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(&record.status)
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
                    sqlx::query(query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(&record.tags)
                        .bind(record.approved)
                        .bind(&record.datacard_uids)
                        .bind(&record.modelcard_uids)
                        .bind(&record.experimentcard_uids)
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
                    sqlx::query(query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(&record.tags)
                        .bind(&record.experimentcard_uid)
                        .bind(&record.auditcard_uid)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(&record.content_hash)
                        .bind(&record.uid)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }

                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            CardTable::Service | CardTable::Mcp | CardTable::Agent => match card {
                ServerCard::Service(record) => {
                    let query = MySqlQueryHelper::get_servicecard_update_query(table);
                    sqlx::query(query)
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
                        .bind(&record.content_hash)
                        .bind(&record.uid)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            CardTable::Skill => match card {
                ServerCard::Skill(record) => {
                    let query = MySqlQueryHelper::get_skillcard_update_query();
                    sqlx::query(query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(&record.tags)
                        .bind(&record.compatible_tools)
                        .bind(&record.dependencies)
                        .bind(&record.description)
                        .bind(&record.license)
                        .bind(&record.content_hash)
                        .bind(&record.username)
                        .bind(&record.opsml_version)
                        .bind(&record.input_schema)
                        .bind(&record.uid)
                        .execute(&self.pool)
                        .await?;
                    Ok(())
                }
                _ => {
                    return Err(SqlError::InvalidCardType);
                }
            },

            CardTable::SubAgent => match card {
                ServerCard::SubAgent(record) => {
                    let query = MySqlQueryHelper::get_subagent_card_update_query();
                    sqlx::query(query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(&record.tags)
                        .bind(&record.compatible_clis)
                        .bind(&record.description)
                        .bind(&record.content_hash)
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

            CardTable::Tool => match card {
                ServerCard::Tool(record) => {
                    let query = MySqlQueryHelper::get_tool_card_update_query();
                    sqlx::query(query)
                        .bind(&record.app_env)
                        .bind(&record.name)
                        .bind(&record.space)
                        .bind(&record.tags)
                        .bind(&record.tool_type)
                        .bind(&record.args_schema)
                        .bind(&record.description)
                        .bind(&record.content_hash)
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

    async fn query_dashboard_stats(&self) -> Result<DashboardStats, SqlError> {
        let query = MySqlQueryHelper::get_dashboard_stats_query();
        let stats: DashboardStats = sqlx::query_as(query).fetch_one(&self.pool).await?;
        Ok(stats)
    }

    /// Query a page of cards with cursor-based pagination
    ///
    /// # Arguments
    ///
    /// * `sort_by` - The field to sort by
    /// * `limit` - Number of items per page (will fetch limit + 1 for has_next detection)
    /// * `offset` - Starting position in result set
    /// * `search_term` - Optional search term (from cursor)
    /// * `spaces` - Space filters (from cursor)
    /// * `tags` - Tag filters (from cursor)
    /// * `table` - The table to query
    ///
    /// # Returns
    ///
    /// * `Vec<CardSummary>` - A vector of card summaries (may contain limit + 1 items)
    async fn query_page(
        &self,
        sort_by: &str,
        limit: i32,
        offset: i32,
        search_term: Option<&str>,
        spaces: &[String],
        tags: &[String],
        table: &CardTable,
    ) -> Result<Vec<CardSummary>, SqlError> {
        let query = MySqlQueryHelper::get_query_page_query(table, sort_by, spaces, tags);

        // Build query with proper parameter binding
        // MySQL uses positional parameters (?)
        let mut query_builder = sqlx::query_as::<_, CardSummary>(&query)
            .bind(search_term) // First ? for NULL check
            .bind(search_term.map(|term| format!("%{term}%"))) // Second ? for name LIKE
            .bind(search_term.map(|term| format!("%{term}%"))); // Third ? for space LIKE

        // Bind space filters
        for space in spaces {
            query_builder = query_builder.bind(space);
        }

        // Bind tag filters (JSON format for MySQL)
        for tag in tags {
            query_builder = query_builder.bind(format!("\"{}\"", tag));
        }

        // Bind pagination parameters (limit + 1, then offset)
        query_builder = query_builder.bind(limit + 1).bind(offset);

        let records = query_builder.fetch_all(&self.pool).await?;
        Ok(records)
    }

    async fn version_page(
        &self,
        cursor: &VersionCursor,
        table: &CardTable,
    ) -> Result<Vec<VersionSummary>, SqlError> {
        let query = MySqlQueryHelper::get_version_page_query(table);

        // Fetch limit + 1 to determine if there's a next page
        let records: Vec<VersionSummary> = sqlx::query_as(&query)
            .bind(&cursor.space)
            .bind(&cursor.name)
            .bind(cursor.offset)
            .bind(cursor.offset + cursor.limit + 1)
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

#[async_trait]
impl SkillLogicTrait for CardLogicMySqlClient {
    async fn get_skill_card_by_name(
        &self,
        space: &str,
        name: &str,
    ) -> Result<SkillCardRecord, SqlError> {
        let record =
            sqlx::query_as::<_, SkillCardRecord>(MySqlQueryHelper::get_skill_card_by_name_query())
                .bind(space)
                .bind(name)
                .fetch_optional(&self.pool)
                .await?
                .ok_or_else(|| SqlError::MissingField(format!("{}/{}", space, name)))?;
        Ok(record)
    }

    async fn get_skill_card_by_version(
        &self,
        space: &str,
        name: &str,
        version: &str,
    ) -> Result<SkillCardRecord, SqlError> {
        let record = sqlx::query_as::<_, SkillCardRecord>(
            MySqlQueryHelper::get_skill_card_by_version_query(),
        )
        .bind(space)
        .bind(name)
        .bind(version)
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| SqlError::MissingField(format!("{}/{}/{}", space, name, version)))?;
        Ok(record)
    }

    async fn increment_skill_download_count(&self, uid: &str) -> Result<(), SqlError> {
        let result = sqlx::query(MySqlQueryHelper::get_increment_skill_download_count_query())
            .bind(uid)
            .execute(&self.pool)
            .await?;
        if result.rows_affected() == 0 {
            return Err(SqlError::MissingField(format!(
                "skill uid not found: {uid}"
            )));
        }
        Ok(())
    }

    async fn list_skill_cards_by_space(
        &self,
        space: &str,
    ) -> Result<Vec<SkillCardRecord>, SqlError> {
        let records = sqlx::query_as::<_, SkillCardRecord>(
            MySqlQueryHelper::get_list_skill_cards_by_space_query(),
        )
        .bind(space)
        .fetch_all(&self.pool)
        .await?;
        Ok(records)
    }

    async fn get_featured_skills(&self, limit: i64) -> Result<Vec<SkillCardRecord>, SqlError> {
        let records =
            sqlx::query_as::<_, SkillCardRecord>(MySqlQueryHelper::get_featured_skills_query())
                .bind(limit)
                .fetch_all(&self.pool)
                .await?;
        Ok(records)
    }

    async fn get_all_skill_tags(&self) -> Result<Vec<String>, SqlError> {
        let tags: Vec<String> = sqlx::query_scalar(MySqlQueryHelper::get_all_skill_tags_query())
            .fetch_all(&self.pool)
            .await?;
        Ok(tags)
    }

    async fn get_marketplace_stats(&self) -> Result<MarketplaceStats, SqlError> {
        let row: (i64, i64, i64) = sqlx::query_as(MySqlQueryHelper::get_marketplace_stats_query())
            .fetch_one(&self.pool)
            .await?;

        Ok(MarketplaceStats {
            total_skills: row.0,
            total_spaces: row.1,
            total_downloads: row.2,
        })
    }
}

#[async_trait]
impl SubAgentLogicTrait for CardLogicMySqlClient {
    async fn get_subagent_card_by_name(
        &self,
        space: &str,
        name: &str,
    ) -> Result<SubAgentCardRecord, SqlError> {
        let record = sqlx::query_as::<_, SubAgentCardRecord>(
            MySqlQueryHelper::get_subagent_card_by_name_query(),
        )
        .bind(space)
        .bind(name)
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| SqlError::MissingField(format!("{}/{}", space, name)))?;
        Ok(record)
    }

    async fn get_subagent_card_by_version(
        &self,
        space: &str,
        name: &str,
        version: &str,
    ) -> Result<SubAgentCardRecord, SqlError> {
        let record = sqlx::query_as::<_, SubAgentCardRecord>(
            MySqlQueryHelper::get_subagent_card_by_version_query(),
        )
        .bind(space)
        .bind(name)
        .bind(version)
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| SqlError::MissingField(format!("{}/{}/{}", space, name, version)))?;
        Ok(record)
    }

    async fn increment_subagent_download_count(&self, uid: &str) -> Result<(), SqlError> {
        let result = sqlx::query(MySqlQueryHelper::get_increment_subagent_download_count_query())
            .bind(uid)
            .execute(&self.pool)
            .await?;
        if result.rows_affected() == 0 {
            return Err(SqlError::MissingField(format!(
                "subagent uid not found: {uid}"
            )));
        }
        Ok(())
    }

    async fn list_subagent_cards_by_space(
        &self,
        space: &str,
    ) -> Result<Vec<SubAgentCardRecord>, SqlError> {
        let records = sqlx::query_as::<_, SubAgentCardRecord>(
            MySqlQueryHelper::get_list_subagent_cards_by_space_query(),
        )
        .bind(space)
        .fetch_all(&self.pool)
        .await?;
        Ok(records)
    }

    async fn get_featured_subagents(
        &self,
        space: &str,
        limit: i64,
    ) -> Result<Vec<SubAgentCardRecord>, SqlError> {
        let records = sqlx::query_as::<_, SubAgentCardRecord>(
            MySqlQueryHelper::get_featured_subagents_query(),
        )
        .bind(space)
        .bind(limit)
        .fetch_all(&self.pool)
        .await?;
        Ok(records)
    }

    async fn get_all_subagent_tags(&self, space: &str) -> Result<Vec<String>, SqlError> {
        let tags: Vec<String> = sqlx::query_scalar(MySqlQueryHelper::get_all_subagent_tags_query())
            .bind(space)
            .fetch_all(&self.pool)
            .await?;
        Ok(tags)
    }

    async fn get_subagent_marketplace_stats(
        &self,
        space: &str,
    ) -> Result<MarketplaceStats, SqlError> {
        let row: (i64, i64, i64) =
            sqlx::query_as(MySqlQueryHelper::get_subagent_marketplace_stats_query())
                .bind(space)
                .fetch_one(&self.pool)
                .await?;

        Ok(MarketplaceStats {
            total_skills: row.0,
            total_spaces: row.1,
            total_downloads: row.2,
        })
    }
}

#[async_trait]
impl ToolLogicTrait for CardLogicMySqlClient {
    async fn get_tool_card_by_name(
        &self,
        space: &str,
        name: &str,
    ) -> Result<ToolCardRecord, SqlError> {
        let record =
            sqlx::query_as::<_, ToolCardRecord>(MySqlQueryHelper::get_tool_card_by_name_query())
                .bind(space)
                .bind(name)
                .fetch_optional(&self.pool)
                .await?
                .ok_or_else(|| SqlError::MissingField(format!("{}/{}", space, name)))?;
        Ok(record)
    }

    async fn get_tool_card_by_version(
        &self,
        space: &str,
        name: &str,
        version: &str,
    ) -> Result<ToolCardRecord, SqlError> {
        let record =
            sqlx::query_as::<_, ToolCardRecord>(MySqlQueryHelper::get_tool_card_by_version_query())
                .bind(space)
                .bind(name)
                .bind(version)
                .fetch_optional(&self.pool)
                .await?
                .ok_or_else(|| SqlError::MissingField(format!("{}/{}/{}", space, name, version)))?;
        Ok(record)
    }

    async fn increment_tool_download_count(&self, uid: &str) -> Result<(), SqlError> {
        let result = sqlx::query(MySqlQueryHelper::get_increment_tool_download_count_query())
            .bind(uid)
            .execute(&self.pool)
            .await?;
        if result.rows_affected() == 0 {
            return Err(SqlError::MissingField(format!("tool uid not found: {uid}")));
        }
        Ok(())
    }

    async fn list_tool_cards_by_space(
        &self,
        space: &str,
        tool_type: Option<&str>,
    ) -> Result<Vec<ToolCardRecord>, SqlError> {
        let records = sqlx::query_as::<_, ToolCardRecord>(
            MySqlQueryHelper::get_list_tool_cards_by_space_query(),
        )
        .bind(space)
        .bind(tool_type)
        .bind(tool_type)
        .fetch_all(&self.pool)
        .await?;
        Ok(records)
    }

    async fn get_featured_tools(
        &self,
        space: &str,
        limit: i64,
    ) -> Result<Vec<ToolCardRecord>, SqlError> {
        let records =
            sqlx::query_as::<_, ToolCardRecord>(MySqlQueryHelper::get_featured_tools_query())
                .bind(space)
                .bind(limit)
                .fetch_all(&self.pool)
                .await?;
        Ok(records)
    }

    async fn get_all_tool_tags(&self, space: &str) -> Result<Vec<String>, SqlError> {
        let tags: Vec<String> = sqlx::query_scalar(MySqlQueryHelper::get_all_tool_tags_query())
            .bind(space)
            .fetch_all(&self.pool)
            .await?;
        Ok(tags)
    }

    async fn get_tool_marketplace_stats(&self, space: &str) -> Result<MarketplaceStats, SqlError> {
        let row: (i64, i64, i64) =
            sqlx::query_as(MySqlQueryHelper::get_tool_marketplace_stats_query())
                .bind(space)
                .fetch_one(&self.pool)
                .await?;

        Ok(MarketplaceStats {
            total_skills: row.0,
            total_spaces: row.1,
            total_downloads: row.2,
        })
    }
}
