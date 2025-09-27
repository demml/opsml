use crate::error::SqlError;

use opsml_semver::VersionParser;
/// this file contains helper logic for generating sql queries across different databases
use opsml_types::{
    cards::CardTable,
    contracts::{ArtifactQueryArgs, CardQueryArgs, ServiceQueryArgs},
};

use opsml_utils::utils::is_valid_uuidv7;

// user
const INSERT_USER_SQL: &str = include_str!("sql/user/insert_user.sql");
const GET_USER_SQL: &str = include_str!("sql/user/get_user.sql");
const GET_USER_AUTH_TYPE_SQL: &str = include_str!("sql/user/get_user_auth_type.sql");
const GET_USERS_SQL: &str = include_str!("sql/user/get_users.sql");
const UPDATE_USER_SQL: &str = include_str!("sql/user/update_user.sql");
const DELETE_USER_SQL: &str = include_str!("sql/user/delete_user.sql");
const LAST_ADMIN_SQL: &str = include_str!("sql/user/last_admin.sql");

// space stats
const INSERT_SPACE_RECORD_SQL: &str = include_str!("sql/space/insert_space_record.sql");
const INSERT_SPACE_NAME_RECORD_SQL: &str = include_str!("sql/space/insert_space_name_record.sql");

const GET_ALL_SPACE_STATS_SQL: &str = include_str!("sql/space/get_all_space_stats.sql");
const GET_SPACE_RECORD_SQL: &str = include_str!("sql/space/get_space_record.sql");

const UPDATE_SPACE_RECORD_SQL: &str = include_str!("sql/space/update_space_record.sql");
const DELETE_SPACE_RECORD_SQL: &str = include_str!("sql/space/delete_space_record.sql");
const DELETE_SPACE_NAME_RECORD_SQL: &str = include_str!("sql/space/delete_space_name_record.sql");

// experiment
const GET_HARDWARE_METRIC_SQL: &str = include_str!("sql/experiment/get_hardware_metric.sql");
const INSERT_EXPERIMENT_METRIC_SQL: &str =
    include_str!("sql/experiment/insert_experiment_metric.sql");
const GET_EXPERIMENT_METRIC_SQL: &str = include_str!("sql/experiment/get_experiment_metric.sql");
const INSERT_HARDWARE_METRIC_SQL: &str = include_str!("sql/experiment/insert_hardware_metric.sql");

// cards
const INSERT_DATACARD_SQL: &str = include_str!("sql/card/insert_datacard.sql");
const INSERT_PROMPTCARD_SQL: &str = include_str!("sql/card/insert_promptcard.sql");
const INSERT_MODELCARD_SQL: &str = include_str!("sql/card/insert_modelcard.sql");
const INSERT_EXPERIMENTCARD_SQL: &str = include_str!("sql/card/insert_experimentcard.sql");
const INSERT_AUDITCARD_SQL: &str = include_str!("sql/card/insert_auditcard.sql");
const INSERT_SERVICECARD_SQL: &str = include_str!("sql/card/insert_servicecard.sql");
const INSERT_MCP_SERVICECARD_SQL: &str = include_str!("sql/card/insert_mcp_servicecard.sql");
const UPDATE_DATACARD_SQL: &str = include_str!("sql/card/update_datacard.sql");
const UPDATE_PROMPTCARD_SQL: &str = include_str!("sql/card/update_promptcard.sql");
const UPDATE_MODELCARD_SQL: &str = include_str!("sql/card/update_modelcard.sql");
const UPDATE_EXPERIMENTCARD_SQL: &str = include_str!("sql/card/update_experimentcard.sql");
const UPDATE_AUDITCARD_SQL: &str = include_str!("sql/card/update_auditcard.sql");
const UPDATE_SERVICECARD_SQL: &str = include_str!("sql/card/update_servicecard.sql");
const UPDATE_MCP_SERVICECARD_SQL: &str = include_str!("sql/card/update_mcp_servicecard.sql");

// artifact keys
const INSERT_ARTIFACT_KEY_SQL: &str = include_str!("sql/artifact/insert_artifact_key.sql");
const INSERT_ARTIFACT_RECORD_SQL: &str = include_str!("sql/artifact/insert_artifact_record.sql");
const GET_ARTIFACT_KEY_SQL: &str = include_str!("sql/artifact/get_artifact_key.sql");
const UPDATE_ARTIFACT_KEY_SQL: &str = include_str!("sql/artifact/update_artifact_key.sql");
const GET_ARTIFACT_KEY_FROM_STORAGE_PATH_SQL: &str =
    include_str!("sql/artifact/get_artifact_key_from_storage_path.sql");
const DELETE_ARTIFACT_KEY_SQL: &str = include_str!("sql/artifact/delete_artifact_key.sql");

// evaluation
const INSERT_EVALUATION_RECORD_SQL: &str = include_str!("sql/evaluation/insert_evaluation.sql");
const GET_EVALUATION_RECORD_SQL: &str = include_str!("sql/evaluation/get_evaluation.sql");

// audit events
const INSERT_AUDIT_EVENT_SQL: &str = include_str!("sql/audit/insert_audit_event.sql");

pub fn add_version_bounds(builder: &mut String, version: &str) -> Result<(), SqlError> {
    let version_bounds = VersionParser::get_version_to_search(version)?;

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
pub struct PostgresQueryHelper;

impl PostgresQueryHelper {
    pub fn get_uid_query(table: &CardTable) -> String {
        format!("SELECT uid FROM {table} WHERE uid = $1")
    }

    pub fn get_user_insert_query() -> String {
        INSERT_USER_SQL.to_string()
    }

    pub fn get_user_query() -> String {
        GET_USER_SQL.to_string()
    }

    pub fn get_user_query_by_auth_type() -> String {
        GET_USER_AUTH_TYPE_SQL.to_string()
    }

    pub fn get_users_query() -> String {
        GET_USERS_SQL.to_string()
    }

    pub fn get_last_admin_query() -> String {
        LAST_ADMIN_SQL.to_string()
    }

    pub fn get_user_delete_query() -> String {
        DELETE_USER_SQL.to_string()
    }

    pub fn get_user_update_query() -> String {
        UPDATE_USER_SQL.to_string()
    }

    pub fn get_hardware_metric_query() -> String {
        GET_HARDWARE_METRIC_SQL.to_string()
    }
    pub fn get_experiment_metric_insert_query() -> String {
        INSERT_EXPERIMENT_METRIC_SQL.to_string()
    }
    pub fn get_artifact_record_insert_query() -> String {
        INSERT_ARTIFACT_RECORD_SQL.to_string()
    }

    pub fn get_experiment_metrics_insert_query(nbr_records: usize) -> String {
        let mut query = format!(
            "INSERT INTO {} (
                experiment_uid, 
                name, 
                value,
                step,
                timestamp,
                is_eval
            ) VALUES ",
            CardTable::Metrics
        );

        for i in 0..nbr_records {
            if i > 0 {
                query.push_str(", ");
            }
            query.push_str(&format!(
                "(${}, ${}, ${}, ${}, ${}, ${})",
                6 * i + 1,
                6 * i + 2,
                6 * i + 3,
                6 * i + 4,
                6 * i + 5,
                6 * i + 6
            ));
        }

        query
    }
    pub fn get_experiment_metric_query(
        names: &[String],
        is_eval: Option<bool>,
    ) -> (String, Vec<String>) {
        let mut query = GET_EXPERIMENT_METRIC_SQL.to_string();

        let mut bindings: Vec<String> = Vec::new();
        let mut param_index = 2; // Start from 2 because $1 is used for experiment_uid

        if !names.is_empty() {
            query.push_str(" AND (");
            for (idx, name) in names.iter().enumerate() {
                if idx > 0 {
                    query.push_str(" OR ");
                }
                query.push_str(&format!("name = ${param_index}"));
                bindings.push(name.to_string());
                param_index += 1;
            }
            query.push(')');
        }

        if let Some(is_eval) = is_eval {
            if is_eval {
                query.push_str(" AND is_eval = TRUE");
            } else {
                query.push_str(" AND is_eval = FALSE");
            }
        }

        (query, bindings)
    }

    pub fn get_query_page_query(table: &CardTable, sort_by: &str, tags: &Vec<String>) -> String {
        let mut binding_index = 4; // Start from 4 because $1, $2, $3 are used for space, name, search

        let tag_filter = if !tags.is_empty() {
            let condition = format!(" AND tags ?| ${binding_index}");
            binding_index += 1;
            condition
        } else {
            "".to_string()
        };

        let versions_cte = format!(
            "WITH versions AS (
                SELECT 
                    space, 
                    name, 
                    version, 
                    ROW_NUMBER() OVER (PARTITION BY space, name ORDER BY created_at DESC) AS row_num 
                FROM {table}
                WHERE ($1 IS NULL OR space = $1)
                AND ($2 IS NULL OR name LIKE $3 OR space LIKE $3)
                {tag_filter}
            )"
        );

        let stats_cte = format!(
            ", stats AS (
                SELECT 
                    space, 
                    name, 
                    COUNT(DISTINCT version) AS versions, 
                    MAX(created_at) AS updated_at, 
                    MIN(created_at) AS created_at 
                FROM {table}
                WHERE ($1 IS NULL OR space = $1)
                AND ($2 IS NULL OR name LIKE $3 OR space LIKE $3)
                {tag_filter}
                GROUP BY space, name
        )"
        );

        let filtered_versions_cte = ", filtered_versions AS (
             SELECT 
                    space, 
                    name, 
                    version, 
                    row_num
                FROM versions 
                WHERE row_num = 1
        )";

        let joined_cte = format!(
            ", joined AS (
                 SELECT 
                    stats.space, 
                    stats.name, 
                    filtered_versions.version, 
                    stats.versions, 
                    stats.updated_at, 
                    stats.created_at, 
                    ROW_NUMBER() OVER (ORDER BY stats.{sort_by}) AS row_num 
                FROM stats 
                JOIN filtered_versions 
                ON stats.space = filtered_versions.space 
                AND stats.name = filtered_versions.name
            )"
        );

        let combined_query = format!(
            "{versions_cte}{stats_cte}{filtered_versions_cte}{joined_cte}
            SELECT * FROM joined
            WHERE row_num > ${binding_index} AND row_num <= ${binding_index_plus_1}
            ORDER BY updated_at DESC",
            binding_index_plus_1 = binding_index + 1
        );

        combined_query
    }

    pub fn get_version_page_query(table: &CardTable) -> String {
        let versions_cte = format!(
            "WITH versions AS (
                SELECT 
                    space, 
                    name, 
                    version, 
                    created_at,
                    ROW_NUMBER() OVER (PARTITION BY space, name ORDER BY created_at DESC, major DESC, minor DESC, patch DESC) AS row_num
                FROM {table}
                WHERE space = $1
                AND name = $2
            )"
        );

        let query = format!(
            "{versions_cte}
            SELECT
            space,
            name,
            version,
            created_at,
            row_num
            FROM versions
            WHERE row_num > $3 AND row_num <= $4
            ORDER BY created_at DESC"
        );

        query
    }

    pub fn get_query_stats_query(table: &CardTable, tags: &Vec<String>) -> String {
        let mut base_query = format!(
            "SELECT
        COALESCE(CAST(COUNT(DISTINCT name) AS INTEGER), 0) AS nbr_names, 
        COALESCE(CAST(COUNT(major) AS INTEGER), 0) AS nbr_versions, 
        COALESCE(CAST(COUNT(DISTINCT space) AS INTEGER), 0) AS nbr_spaces 
        FROM {table}
        WHERE 1=1
        AND ($1 IS NULL OR name LIKE $1 OR space LIKE $1)
        AND ($2 IS NULL OR name = $2 OR space = $2)"
        );

        if !tags.is_empty() {
            base_query.push_str(" AND tags ?| $3");
        }

        base_query
    }
    pub fn get_versions_query(
        table: &CardTable,
        version: Option<String>,
    ) -> Result<String, SqlError> {
        let mut query = format!(
            "
            SELECT
             created_at,
             name, 
             space, 
             major, minor, 
             patch, 
             pre_tag, 
             build_tag, 
             uid
             FROM {table}
             WHERE 1=1
                AND space = $1
                AND name = $2
            "
        );

        if let Some(version) = version {
            add_version_bounds(&mut query, &version)?;
        }

        query.push_str(" ORDER BY created_at DESC LIMIT 20;");

        Ok(query)
    }

    pub fn get_query_cards_query(
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<String, SqlError> {
        let mut binding_index = 5; // Start from 6 because $1 to $5 are used for uid, space, name, max_date, version
        if query_args.uid.is_some() {
            is_valid_uuidv7(query_args.uid.as_ref().unwrap())?;
            return Ok(format!("SELECT * FROM {table} WHERE uid = $1 LIMIT 1"));
        }

        let mut query = format!(
            "
        SELECT * FROM {table}
        WHERE 1=1
        "
        );

        // Add conditions in order of index columns to maximize index usage
        if query_args.space.is_some() {
            query.push_str(" AND space = $2"); // space is first column in index
        }

        if query_args.name.is_some() {
            query.push_str(" AND name = $3"); // name is second column in index
        }

        // Date doesn't have an index but keep it in the original bind position
        if query_args.max_date.is_some() {
            query.push_str(" AND created_at <= TO_DATE($4, 'YYYY-MM-DD')");
        }

        // Add version bounds - will use the version part of the index
        if query_args.version.is_some() {
            add_version_bounds(&mut query, query_args.version.as_ref().unwrap())?;
        }

        // Tags query using jsonb operator
        if let Some(_expect) = &query_args.tags {
            query.push_str(&format!(" AND tags ?| ${binding_index}"));
            binding_index += 1;
        }

        // Add ordering
        if query_args.sort_by_timestamp.unwrap_or(false) {
            query.push_str(" ORDER BY created_at DESC");
        } else {
            query.push_str(" ORDER BY major DESC, minor DESC, patch DESC");
        }

        query.push_str(&format!(" LIMIT ${binding_index}"));

        Ok(query)
    }

    pub fn get_query_artifacts_query(query_args: &ArtifactQueryArgs) -> Result<String, SqlError> {
        let table = &CardTable::Artifact;
        if query_args.uid.is_some() {
            is_valid_uuidv7(query_args.uid.as_ref().unwrap())?;

            return Ok(format!("SELECT * FROM {table} WHERE uid = $1 LIMIT 1"));
        }

        let mut query = format!(
            "
        SELECT * FROM {table}
        WHERE 1=1
        "
        );

        if query_args.artifact_type.is_some() {
            query.push_str(" AND artifact_type = $2"); // artifact_type is first column in index
        }

        // Add conditions in order of index columns to maximize index usage
        if query_args.space.is_some() {
            query.push_str(" AND space = $3"); // space is first column in index
        }

        if query_args.name.is_some() {
            query.push_str(" AND name = $4"); // name is second column in index
        }

        // Add version bounds - will use the version part of the index
        if query_args.version.is_some() {
            add_version_bounds(&mut query, query_args.version.as_ref().unwrap())?;
        }

        // Add ordering
        if query_args.sort_by_timestamp.unwrap_or(false) {
            query.push_str(" ORDER BY created_at DESC");
        } else {
            query.push_str(" ORDER BY major DESC, minor DESC, patch DESC");
        }

        query.push_str(" LIMIT $5");

        Ok(query)
    }
    pub fn get_experiment_parameters_insert_query(nbr_records: usize) -> String {
        let mut query = format!(
            "INSERT INTO {} (
                experiment_uid, 
                name, 
                value
            ) VALUES ",
            CardTable::Parameters
        );

        for i in 0..nbr_records {
            if i > 0 {
                query.push_str(", ");
            }
            query.push_str(&format!("(${}, ${}, ${})", 3 * i + 1, 3 * i + 2, 3 * i + 3));
        }

        query
    }
    pub fn get_experiment_parameter_query(names: &[String]) -> (String, Vec<String>) {
        let mut query = format!(
            "SELECT *
            FROM {}
            WHERE experiment_uid = $1",
            CardTable::Parameters
        );

        let mut bindings: Vec<String> = Vec::new();
        let mut param_index = 2; // Start from 2 because $1 is used for experiment_uid

        if !names.is_empty() {
            query.push_str(" AND (");
            for (idx, name) in names.iter().enumerate() {
                if idx > 0 {
                    query.push_str(" OR ");
                }
                query.push_str(&format!("name = ${param_index}"));
                bindings.push(name.to_string());
                param_index += 1;
            }
            query.push(')');
        }

        (query, bindings)
    }
    pub fn get_hardware_metrics_insert_query() -> String {
        INSERT_HARDWARE_METRIC_SQL.to_string()
    }

    pub fn get_datacard_insert_query() -> String {
        INSERT_DATACARD_SQL.to_string()
    }

    pub fn get_promptcard_insert_query() -> String {
        INSERT_PROMPTCARD_SQL.to_string()
    }

    pub fn get_modelcard_insert_query() -> String {
        INSERT_MODELCARD_SQL.to_string()
    }

    pub fn get_experimentcard_insert_query() -> String {
        INSERT_EXPERIMENTCARD_SQL.to_string()
    }

    pub fn get_auditcard_insert_query() -> String {
        INSERT_AUDITCARD_SQL.to_string()
    }

    pub fn get_servicecard_insert_query(table: &CardTable) -> String {
        match table {
            CardTable::Service => INSERT_SERVICECARD_SQL.to_string(),
            CardTable::Mcp => INSERT_MCP_SERVICECARD_SQL.to_string(),
            _ => INSERT_SERVICECARD_SQL.to_string(),
        }
    }

    pub fn get_servicecard_update_query(table: &CardTable) -> String {
        match table {
            CardTable::Service => UPDATE_SERVICECARD_SQL.to_string(),
            CardTable::Mcp => UPDATE_MCP_SERVICECARD_SQL.to_string(),
            _ => UPDATE_SERVICECARD_SQL.to_string(),
        }
    }

    pub fn get_promptcard_update_query() -> String {
        UPDATE_PROMPTCARD_SQL.to_string()
    }

    pub fn get_datacard_update_query() -> String {
        UPDATE_DATACARD_SQL.to_string()
    }

    pub fn get_modelcard_update_query() -> String {
        UPDATE_MODELCARD_SQL.to_string()
    }

    pub fn get_experimentcard_update_query() -> String {
        UPDATE_EXPERIMENTCARD_SQL.to_string()
    }

    pub fn get_auditcard_update_query() -> String {
        UPDATE_AUDITCARD_SQL.to_string()
    }

    pub fn get_artifact_key_insert_query() -> String {
        INSERT_ARTIFACT_KEY_SQL.to_string()
    }

    pub fn get_artifact_key_select_query() -> String {
        GET_ARTIFACT_KEY_SQL.to_string()
    }

    pub fn get_artifact_key_update_query() -> String {
        UPDATE_ARTIFACT_KEY_SQL.to_string()
    }

    pub fn get_artifact_key_from_storage_path_query() -> String {
        GET_ARTIFACT_KEY_FROM_STORAGE_PATH_SQL.to_string()
    }

    pub fn get_audit_event_insert_query() -> String {
        INSERT_AUDIT_EVENT_SQL.to_string()
    }

    pub fn get_load_card_query(
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<String, SqlError> {
        // subquery 1 - query_cards_query

        let query_cards_query = PostgresQueryHelper::get_query_cards_query(table, query_args)?;

        let query = format!(
            "WITH query_cards AS (
                {}
            )
            SELECT a.uid, a.space, a.registry_type, a.encrypted_key, a.storage_key
            FROM {} as a
            INNER JOIN query_cards as b 
                ON a.uid = b.uid;",
            query_cards_query,
            CardTable::ArtifactKey
        );

        Ok(query)
    }

    pub fn get_artifact_key_delete_query() -> String {
        DELETE_ARTIFACT_KEY_SQL.to_string()
    }

    pub fn get_all_space_stats_query() -> String {
        GET_ALL_SPACE_STATS_SQL.to_string()
    }

    pub fn get_space_record_query() -> String {
        GET_SPACE_RECORD_SQL.to_string()
    }

    pub fn get_insert_space_name_record_query() -> String {
        INSERT_SPACE_NAME_RECORD_SQL.to_string()
    }

    pub fn get_insert_space_record_query() -> String {
        INSERT_SPACE_RECORD_SQL.to_string()
    }

    pub fn get_update_space_record_query() -> String {
        UPDATE_SPACE_RECORD_SQL.to_string()
    }

    pub fn get_delete_space_record_query() -> String {
        DELETE_SPACE_RECORD_SQL.to_string()
    }

    pub fn get_delete_space_name_record_query() -> String {
        DELETE_SPACE_NAME_RECORD_SQL.to_string()
    }

    pub fn get_evaluation_record_query() -> String {
        GET_EVALUATION_RECORD_SQL.to_string()
    }
    pub fn get_evaluation_record_insert_query() -> String {
        INSERT_EVALUATION_RECORD_SQL.to_string()
    }

    pub fn get_recent_services_query(query_args: &ServiceQueryArgs) -> String {
        let card_table = CardTable::from_service_type(&query_args.service_type);
        let mut where_clause = String::from(
            "
        WHERE 1=1
        AND ($1 IS NULL OR space = $1)
        AND ($2 IS NULL OR name = $2)
    ",
        );

        if let Some(tags) = &query_args.tags {
            for tag in tags {
                where_clause.push_str(
                format!(" AND EXISTS (SELECT 1 FROM jsonb_array_elements_text(tags) AS t WHERE t = '{tag}')").as_str(),
            );
            }
        }

        let query = format!(
            "
        SELECT *
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY space, name
                    ORDER BY created_at DESC
                ) AS rn
            FROM {card_table}
            {where_clause}
        )
        WHERE rn = 1;
        "
        );

        query
    }
}
