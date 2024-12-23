use opsml_error::error::SqlError;

/// this file contains helper logic for generating sql queries across different databases
use crate::base::add_version_bounds;
use opsml_types::{CardQueryArgs, CardSQLTableNames};
use opsml_utils::utils::is_valid_uuid4;
pub struct SqliteQueryHelper;

impl SqliteQueryHelper {
    pub fn get_uid_query(table: &CardSQLTableNames) -> String {
        format!("SELECT uid FROM {} WHERE uid = ?", table).to_string()
    }
    pub fn get_user_insert_query() -> String {
        format!(
            "INSERT INTO {} (username, password_hash, permissions, group_permissions) VALUES (?, ?, ?, ?)",
            CardSQLTableNames::Users
        )
        .to_string()
    }

    pub fn get_user_query() -> String {
        format!(
            "SELECT id, created_at, active, username, password_hash, permissions, group_permissions, refresh_token FROM {} WHERE username = ?",
            CardSQLTableNames::Users
        )
        .to_string()
    }

    pub fn get_user_update_query() -> String {
        format!(
            "UPDATE {} SET 
            active = ?, 
            password_hash = ?, 
            permissions = ?, 
            group_permissions = ? ,
            refresh_token = ? 
            WHERE username = ?",
            CardSQLTableNames::Users
        )
        .to_string()
    }
    pub fn get_hardware_metric_query() -> String {
        let query = format!(
            "SELECT
            run_uid,
            created_at,
            cpu_percent_utilization,
            cpu_percent_per_core,
            compute_overall,
            compute_utilized,
            load_avg,
            sys_ram_total,
            sys_ram_used,
            sys_ram_available,
            sys_ram_percent_used,
            sys_swap_total,
            sys_swap_used,
            sys_swap_free,
            sys_swap_percent,
            bytes_recv,
            bytes_sent,
            gpu_percent_utilization,
            gpu_percent_per_core
            FROM {} WHERE run_uid = ?",
            CardSQLTableNames::HardwareMetrics
        );

        query
    }
    pub fn get_run_metric_insert_query() -> String {
        format!(
            "INSERT INTO {} (
                run_uid, 
                name, 
                value,
                step,
                timestamp
            ) VALUES (?, ?, ?, ?, ?)",
            CardSQLTableNames::Metrics
        )
        .to_string()
    }

    pub fn get_run_metrics_insert_query(nbr_records: usize) -> String {
        // values will be a vec of tuples
        let mut query = format!(
            "INSERT INTO {} (
                run_uid, 
                name, 
                value,
                step,
                timestamp
            ) VALUES ",
            CardSQLTableNames::Metrics
        )
        .to_string();

        for i in 0..nbr_records {
            query.push_str("(?, ?, ?, ?, ?)");

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
    pub fn get_run_metric_query(names: &[String]) -> (String, Vec<String>) {
        let mut query = format!(
            "SELECT *
            FROM {}
            WHERE run_uid = ?",
            CardSQLTableNames::Metrics
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

    pub fn get_project_id_query() -> String {
        format!(
            "WITH max_project AS (
                SELECT MAX(project_id) AS max_id FROM {}
            )
            SELECT COALESCE(
                (SELECT project_id FROM {} WHERE name = ? AND repository = ?),
                (SELECT COALESCE(max_id, 0) + 1 FROM max_project)
            ) AS project_id",
            CardSQLTableNames::Project,
            CardSQLTableNames::Project
        )
        .to_string()
    }
    pub fn get_query_page_query(table: &CardSQLTableNames, sort_by: &str) -> String {
        let versions_cte = format!(
            "WITH versions AS (
                SELECT 
                    repository, 
                    name, 
                    version, 
                    ROW_NUMBER() OVER (PARTITION BY repository, name ORDER BY created_at DESC) AS row_num
                FROM {}
                WHERE (?1 IS NULL OR repository = ?1)
                AND (?2 IS NULL OR name LIKE ?3 OR repository LIKE ?3)
            )", table
        );

        let stats_cte = format!(
            ", stats AS (
                SELECT 
                    repository, 
                    name, 
                    COUNT(DISTINCT version) AS versions, 
                    MAX(created_at) AS updated_at, 
                    MIN(created_at) AS created_at 
                FROM {}
                WHERE (?1 IS NULL OR repository = ?1)
                AND (?2 IS NULL OR name LIKE ?3 OR repository LIKE ?3)
                GROUP BY repository, name
            )",
            table
        );

        let filtered_versions_cte = ", filtered_versions AS (
            SELECT 
                repository, 
                name, 
                version, 
                row_num
            FROM versions 
            WHERE row_num = 1
        )";

        let joined_cte = format!(
            ", joined AS (
                SELECT 
                    stats.repository, 
                    stats.name, 
                    filtered_versions.version, 
                    stats.versions, 
                    stats.updated_at, 
                    stats.created_at, 
                    ROW_NUMBER() OVER (ORDER BY stats.{}) AS row_num 
                FROM stats 
                JOIN filtered_versions 
                ON stats.repository = filtered_versions.repository 
                AND stats.name = filtered_versions.name
            )",
            sort_by
        );

        let combined_query = format!(
            "{}{}{}{} 
            SELECT
            repository,
            name,
            version,
            versions,
            updated_at,
            created_at,
            row_num
            FROM joined 
            WHERE row_num BETWEEN ?4 AND ?5
            ORDER BY updated_at DESC",
            versions_cte, stats_cte, filtered_versions_cte, joined_cte
        );

        combined_query
    }
    pub fn get_query_stats_query(table: &CardSQLTableNames) -> String {
        let base_query = format!(
            "SELECT 
                    COALESCE(COUNT(DISTINCT name), 0) AS nbr_names, 
                    COALESCE(COUNT(major), 0) AS nbr_versions, 
                    COALESCE(COUNT(DISTINCT repository), 0) AS nbr_repositories 
                FROM {}
                WHERE 1=1
                AND (?1 IS NULL OR name LIKE ?1 OR repository LIKE ?1)
                ",
            table
        );

        base_query
    }
    pub fn get_versions_query(
        table: &CardSQLTableNames,
        version: Option<&str>,
    ) -> Result<String, SqlError> {
        let mut query = format!(
            "
            SELECT
             created_at,
             name, 
             repository, 
             major, minor, 
             patch, 
             pre_tag, 
             build_tag, 
             contact, 
             uid
             FROM {}
             WHERE 1=1
                AND name = ?
                AND repository = ?
            ",
            table
        );

        if let Some(version) = version {
            add_version_bounds(&mut query, version)?;
        }

        query.push_str(" ORDER BY created_at DESC LIMIT 20;");

        Ok(query)
    }

    pub fn get_query_cards_query(
        table: &CardSQLTableNames,
        query_args: &CardQueryArgs,
    ) -> Result<String, SqlError> {
        let mut query = format!(
            "
        SELECT * FROM {}
        WHERE 1==1
        AND (?1 IS NULL OR uid = ?1)
        AND (?2 IS NULL OR name = ?2)
        AND (?3 IS NULL OR repository = ?3)
        AND (?4 IS NULL OR created_at <= DATETIME(?4))
        ",
            table
        );

        // check for uid. If uid is present, we only return that card
        if query_args.uid.is_some() {
            // validate uid
            is_valid_uuid4(query_args.uid.as_ref().unwrap())
                .map_err(|e| SqlError::GeneralError(e.to_string()))?;
        } else {
            // add where clause due to multiple combinations

            if query_args.version.is_some() {
                add_version_bounds(&mut query, query_args.version.as_ref().unwrap())?;
            }

            if query_args.tags.is_some() {
                let tags = query_args.tags.as_ref().unwrap();
                for (key, value) in tags.iter() {
                    query.push_str(
                        format!(" AND json_extract(tags, '$.{}') == '{}'", key, value).as_str(),
                    );
                }
            }

            if query_args.sort_by_timestamp.unwrap_or(false) {
                query.push_str(" ORDER BY created_at DESC");
            } else {
                // sort by major, minor, patch
                query.push_str(" ORDER BY major DESC, minor DESC, patch DESC");
            }
        }

        query.push_str(" LIMIT ?5");

        Ok(query)
    }
    pub fn get_run_parameters_insert_query(nbr_records: usize) -> String {
        let mut query = format!(
            "INSERT INTO {} (
                run_uid, 
                name, 
                value
            ) VALUES ",
            CardSQLTableNames::Parameters
        )
        .to_string();

        for i in 0..nbr_records {
            query.push_str("(?, ?, ?) ");

            // add comma if not last record
            if i < nbr_records - 1 {
                query.push_str(", ");
            } else {
                query.push(';');
            }
        }

        query
    }
    pub fn get_run_parameter_query(names: &[String]) -> (String, Vec<String>) {
        let mut query = format!(
            "SELECT *
            FROM {}
            WHERE run_uid = ?",
            CardSQLTableNames::Parameters
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
    pub fn get_hardware_metrics_insert_query(nbr_records: usize) -> String {
        let mut query = format!(
            "INSERT INTO {} (
                run_uid, 
                created_at,
                cpu_percent_utilization, 
                cpu_percent_per_core, 
                compute_overall, 
                compute_utilized, 
                load_avg, 
                sys_ram_total, 
                sys_ram_used, 
                sys_ram_available, 
                sys_ram_percent_used, 
                sys_swap_total, 
                sys_swap_used, 
                sys_swap_free, 
                sys_swap_percent, 
                bytes_recv, 
                bytes_sent, 
                gpu_percent_utilization, 
                gpu_percent_per_core
            ) VALUES ",
            CardSQLTableNames::HardwareMetrics
        )
        .to_string();

        for i in 0..nbr_records {
            query.push_str("(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");

            // add comma if not last record
            if i < nbr_records - 1 {
                query.push_str(", ");
            } else {
                query.push(';');
            }
        }

        query
    }

    pub fn get_projectcard_insert_query() -> String {
        format!("INSERT INTO {} (uid, name, repository, project_id, major, minor, patch, version, pre_tag, build_tag) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CardSQLTableNames::Project)
            .to_string()
    }

    pub fn get_datacard_insert_query() -> String {
        format!("INSERT INTO {} (uid, app_env, name, repository, major, minor, patch, version, contact, data_type, interface_type, tags, runcard_uid, pipelinecard_uid, auditcard_uid, pre_tag, build_tag) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CardSQLTableNames::Data)
            .to_string()
    }

    pub fn get_modelcard_insert_query() -> String {
        format!(
            "INSERT INTO {} (
        uid, 
        app_env, 
        name, 
        repository, 
        major, 
        minor, 
        patch, 
        version, 
        contact, 
        datacard_uid, 
        sample_data_type, 
        model_type, 
        interface_type, 
        task_type, 
        tags, 
        runcard_uid, 
        pipelinecard_uid, 
        auditcard_uid, 
        pre_tag, 
        build_tag
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            CardSQLTableNames::Model
        )
        .to_string()
    }

    pub fn get_runcard_insert_query() -> String {
        format!(
            "INSERT INTO {} (
        uid, 
        app_env, 
        name, 
        repository, 
        major, 
        minor, 
        patch, 
        version, 
        contact, 
        project, 
        tags, 
        datacard_uids,
        modelcard_uids, 
        pipelinecard_uid, 
        artifact_uris, 
        compute_environment, 
        pre_tag, 
        build_tag
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            CardSQLTableNames::Run
        )
        .to_string()
    }

    pub fn get_auditcard_insert_query() -> String {
        format!(
            "INSERT INTO {} (
        uid, 
        app_env, 
        name, 
        repository, 
        major, 
        minor, 
        patch, 
        version, 
        contact, 
        tags, 
        approved, 
        datacard_uids, 
        modelcard_uids, 
        runcard_uids, 
        pre_tag, 
        build_tag
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            CardSQLTableNames::Audit
        )
        .to_string()
    }

    pub fn get_pipelinecard_insert_query() -> String {
        format!(
            "INSERT INTO {} (
        uid, 
        app_env, 
        name, 
        repository, 
        major, 
        minor, 
        patch, 
        version, 
        contact, 
        tags, 
        pipeline_code_uri, 
        datacard_uids, 
        modelcard_uids, 
        runcard_uids, 
        pre_tag, 
        build_tag
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            CardSQLTableNames::Pipeline
        )
        .to_string()
    }

    pub fn get_datacard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = ?, 
        name = ?, 
        repository = ?, 
        major = ?, 
        minor = ?, 
        patch = ?, 
        version = ?, 
        contact = ?, 
        data_type = ?, 
        interface_type = ?, 
        tags = ?, 
        runcard_uid = ?, 
        pipelinecard_uid = ?, 
        auditcard_uid = ?, 
        pre_tag = ?, 
        build_tag = ? 
        WHERE uid = ?",
            CardSQLTableNames::Data
        )
        .to_string()
    }

    pub fn get_modelcard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = ?, 
        name = ?, 
        repository = ?, 
        major = ?, 
        minor = ?, 
        patch = ?, 
        version = ?, 
        contact = ?, 
        datacard_uid = ?, 
        sample_data_type = ?, 
        model_type = ?, 
        interface_type = ?, 
        task_type = ?, 
        tags = ?, 
        runcard_uid = ?, 
        pipelinecard_uid = ?, 
        auditcard_uid = ?, 
        pre_tag = ?, 
        build_tag = ? 
        WHERE uid = ?",
            CardSQLTableNames::Model
        )
        .to_string()
    }

    pub fn get_runcard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = ?, 
        name = ?, 
        repository = ?, 
        major = ?, 
        minor = ?, 
        patch = ?, 
        version = ?, 
        contact = ?, 
        project = ?, 
        tags = ?, 
        datacard_uids = ?, 
        modelcard_uids = ?, 
        pipelinecard_uid = ?, 
        artifact_uris = ?, 
        compute_environment = ?, 
        pre_tag = ?, 
        build_tag = ? 
        WHERE uid = ?",
            CardSQLTableNames::Run
        )
        .to_string()
    }

    pub fn get_auditcard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = ?, 
        name = ?, 
        repository = ?, 
        major = ?, 
        minor = ?, 
        patch = ?, 
        version = ?, 
        contact = ?, 
        tags = ?, 
        approved = ?, 
        datacard_uids = ?, 
        modelcard_uids = ?, 
        runcard_uids = ?, 
        pre_tag = ?, 
        build_tag = ?
        WHERE uid = ?",
            CardSQLTableNames::Audit
        )
        .to_string()
    }

    pub fn get_pipelinecard_update_query() -> String {
        format!(
            "UPDATE {} SET  
        app_env = ?, 
        name = ?, 
        repository = ?, 
        major = ?, 
        minor = ?, 
        patch = ?, 
        version = ?, 
        contact = ?, 
        tags = ?, 
        pipeline_code_uri = ?, 
        datacard_uids = ?, 
        modelcard_uids = ?, 
        runcard_uids = ?, 
        pre_tag = ?, 
        build_tag = ? 
        WHERE uid = ?",
            CardSQLTableNames::Pipeline
        )
        .to_string()
    }
}
