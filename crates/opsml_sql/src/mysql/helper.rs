use crate::base::add_version_bounds;

use crate::error::SqlError;
use opsml_types::{cards::CardTable, contracts::CardQueryArgs};
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
const UPDATE_DATACARD_SQL: &str = include_str!("sql/card/update_datacard.sql");
const UPDATE_PROMPTCARD_SQL: &str = include_str!("sql/card/update_promptcard.sql");
const UPDATE_MODELCARD_SQL: &str = include_str!("sql/card/update_modelcard.sql");
const UPDATE_EXPERIMENTCARD_SQL: &str = include_str!("sql/card/update_experimentcard.sql");
const UPDATE_AUDITCARD_SQL: &str = include_str!("sql/card/update_auditcard.sql");
const UPDATE_SERVICECARD_SQL: &str = include_str!("sql/card/update_servicecard.sql");

// artifact keys
const INSERT_ARTIFACT_KEY_SQL: &str = include_str!("sql/artifact/insert_artifact_key.sql");
const GET_ARTIFACT_KEY_SQL: &str = include_str!("sql/artifact/get_artifact_key.sql");
const UPDATE_ARTIFACT_KEY_SQL: &str = include_str!("sql/artifact/update_artifact_key.sql");
const GET_ARTIFACT_KEY_FROM_STORAGE_PATH_SQL: &str =
    include_str!("sql/artifact/get_artifact_key_from_storage_path.sql");
const DELETE_ARTIFACT_KEY_SQL: &str = include_str!("sql/artifact/delete_artifact_key.sql");

// audit events
const INSERT_AUDIT_EVENT_SQL: &str = include_str!("sql/audit/insert_audit_event.sql");

pub struct MySQLQueryHelper;

impl MySQLQueryHelper {
    pub fn get_uid_query(table: &CardTable) -> String {
        format!("SELECT uid FROM {} WHERE uid = ?", table)
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

    pub fn get_experiment_metrics_insert_query(nbr_records: usize) -> String {
        // values will be a vec of tuples
        let mut query = format!(
            "INSERT INTO {} (
                experiment_uid, 
                name, 
                value,
                step,
                timestamp
            ) VALUES ",
            CardTable::Metrics
        );

        for i in 0..nbr_records {
            query.push_str("(?, ?, ?, ?, ?) ");

            // add comma if not last record
            if i < nbr_records - 1 {
                query.push_str(", ");
            } else {
                query.push(';');
            }
        }

        query

        // remove last co
    }

    pub fn get_experiment_metric_query(names: &[String]) -> (String, Vec<String>) {
        let mut query = GET_EXPERIMENT_METRIC_SQL.to_string();
        let mut bindings: Vec<String> = Vec::new();

        // loop through names and bind them. First name = and and others are or

        if !names.is_empty() {
            query.push_str(" AND (");
            for (idx, name) in names.iter().enumerate() {
                if idx > 0 {
                    query.push_str(" OR ");
                }
                query.push_str("name = ?");
                bindings.push(name.to_string());
            }
            query.push(')');
        }

        (query, bindings)
    }

    pub fn get_query_page_query(table: &CardTable, sort_by: &str) -> String {
        let versions_cte = format!(
            "WITH versions AS (
                SELECT 
                    space, 
                    name, 
                    version, 
                    ROW_NUMBER() OVER (PARTITION BY space, name ORDER BY created_at DESC) AS row_num
                FROM {}
                WHERE 1=1
                AND (? IS NULL OR space = ?)
                AND (? IS NULL OR name LIKE ? OR space LIKE ?)
            )",
            table
        );

        let stats_cte = format!(
            ", stats AS (
                SELECT 
                    space, 
                    name, 
                    COUNT(DISTINCT version) AS versions, 
                    MAX(created_at) AS updated_at, 
                    MIN(created_at) AS created_at 
                FROM {}
                WHERE 1=1
                AND (? IS NULL OR space = ?)
                AND (? IS NULL OR name LIKE ? OR space LIKE ?)
                GROUP BY space, name
            )",
            table
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
                    ROW_NUMBER() OVER (ORDER BY stats.{}) AS row_num 
                FROM stats 
                JOIN filtered_versions 
                ON stats.space = filtered_versions.space 
                AND stats.name = filtered_versions.name
            )",
            sort_by
        );

        let combined_query = format!(
            "{}{}{}{} 
            SELECT
            space,
            name,
            version,
            versions,
            updated_at,
            created_at,
            CAST(row_num AS SIGNED) AS row_num
            FROM joined 
            WHERE row_num > ? AND row_num <= ?
            ORDER BY updated_at DESC;",
            versions_cte, stats_cte, filtered_versions_cte, joined_cte
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
                FROM {}
                WHERE space = ?
                AND name = ?
            )", table
        );

        let query = format!(
            "{}
            SELECT
            space,
            name,
            version,
            created_at,
            CAST(row_num AS SIGNED) AS row_num
            FROM versions
            WHERE row_num > ? AND row_num <= ?
            ORDER BY created_at DESC",
            versions_cte
        );

        query
    }

    pub fn get_query_stats_query(table: &CardTable) -> String {
        let base_query = format!(
            "SELECT 
                    COALESCE(COUNT(DISTINCT name), 0) AS nbr_names, 
                    COALESCE(COUNT(major), 0) AS nbr_versions, 
                    COALESCE(COUNT(DISTINCT space), 0) AS nbr_spaces
                FROM {}
                WHERE 1=1
                AND (? IS NULL OR name LIKE ? OR space LIKE ?)
                AND (? IS NULL OR space = ?)
                ",
            table
        );

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
             FROM {}
             WHERE 1=1
                AND name = ?
                AND space = ?
            ",
            table
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
        let mut query = format!(
            "
        SELECT * FROM {}
        WHERE 1=1
        AND (? IS NULL OR uid = ?)
        AND (? IS NULL OR name = ?)
        AND (? IS NULL OR space = ?)
        AND (? IS NULL OR created_at <= STR_TO_DATE(?, '%Y-%m-%d'))
        ",
            table
        );

        // check for uid. If uid is present, we only return that card
        if query_args.uid.is_some() {
            // validate uid
            is_valid_uuidv7(query_args.uid.as_ref().unwrap())?;
        } else {
            // add where clause due to multiple combinations

            if query_args.version.is_some() {
                add_version_bounds(&mut query, query_args.version.as_ref().unwrap())?;
            }

            if query_args.tags.is_some() {
                let tags = query_args.tags.as_ref().unwrap();
                for tag in tags.iter() {
                    query
                        .push_str(format!(" AND JSON_CONTAINS(tags, '\"{}\"', '$')", tag).as_str());
                }
            }

            if query_args.sort_by_timestamp.unwrap_or(false) {
                query.push_str(" ORDER BY created_at DESC");
            } else {
                // sort by major, minor, patch
                query.push_str(" ORDER BY major DESC, minor DESC, patch DESC");
            }
        }

        query.push_str(" LIMIT ?");

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
            query.push_str("(?, ?, ?)");

            // add comma if not last record
            if i < nbr_records - 1 {
                query.push_str(", ");
            } else {
                query.push(';');
            }
        }

        query
    }

    pub fn get_experiment_parameter_query(names: &[String]) -> (String, Vec<String>) {
        let mut query = format!(
            "SELECT *
            FROM {}
            WHERE experiment_uid = ?",
            CardTable::Parameters
        );

        let mut bindings: Vec<String> = Vec::new();

        // loop through names and bind them. First name = and and others are or
        if !names.is_empty() {
            query.push_str(" AND (");
            for (idx, name) in names.iter().enumerate() {
                if idx > 0 {
                    query.push_str(" OR ");
                }
                query.push_str("name = ?");
                bindings.push(name.to_string());
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

    pub fn get_servicecard_insert_query() -> String {
        INSERT_SERVICECARD_SQL.to_string()
    }

    pub fn get_servicecard_update_query() -> String {
        UPDATE_SERVICECARD_SQL.to_string()
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

        let query_cards_query = MySQLQueryHelper::get_query_cards_query(table, query_args)?;

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
}
