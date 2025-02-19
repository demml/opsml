use opsml_error::error::SqlError;

use opsml_semver::VersionParser;
/// this file contains helper logic for generating sql queries across different databases
use opsml_types::{cards::CardTable, contracts::CardQueryArgs};
use opsml_utils::utils::is_valid_uuid4;

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
pub struct PostgresQueryHelper;

impl PostgresQueryHelper {
    pub fn get_uid_query(table: &CardTable) -> String {
        format!("SELECT uid FROM {} WHERE uid = $1", table).to_string()
    }

    pub fn get_user_insert_query() -> String {
        format!(
            "INSERT INTO {} (username, password_hash, permissions, group_permissions) VALUES ($1, $2, $3, $4)",
            CardTable::Users
        )
        .to_string()
    }

    pub fn get_user_query() -> String {
        format!(
            "SELECT id, created_at, active, username, password_hash, permissions, group_permissions, refresh_token FROM {} WHERE username = $1",
            CardTable::Users
        )
        .to_string()
    }

    pub fn get_user_update_query() -> String {
        format!(
            "UPDATE {} SET 
            active = $1, 
            password_hash = $2, 
            permissions = $3, 
            group_permissions = $4,
            refresh_token = $5
            WHERE username = $6",
            CardTable::Users
        )
        .to_string()
    }

    pub fn get_hardware_metric_query() -> String {
        let query = format!(
            "SELECT * FROM {} WHERE run_uid = $1",
            CardTable::HardwareMetrics
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
            ) VALUES ($1, $2, $3, $4, $5)",
            CardTable::Metrics
        )
        .to_string()
    }

    pub fn get_run_metrics_insert_query(nbr_records: usize) -> String {
        let mut query = format!(
            "INSERT INTO {} (
                run_uid, 
                name, 
                value,
                step,
                timestamp
            ) VALUES ",
            CardTable::Metrics
        );

        for i in 0..nbr_records {
            if i > 0 {
                query.push_str(", ");
            }
            query.push_str(&format!(
                "(${}, ${}, ${}, ${}, ${})",
                5 * i + 1,
                5 * i + 2,
                5 * i + 3,
                5 * i + 4,
                5 * i + 5
            ));
        }

        query
    }
    pub fn get_run_metric_query(names: &[String]) -> (String, Vec<String>) {
        let mut query = format!(
            "SELECT *
            FROM {}
            WHERE run_uid = $1",
            CardTable::Metrics
        );

        let mut bindings: Vec<String> = Vec::new();
        let mut param_index = 2; // Start from 2 because $1 is used for run_uid

        if !names.is_empty() {
            query.push_str(" AND (");
            for (idx, name) in names.iter().enumerate() {
                if idx > 0 {
                    query.push_str(" OR ");
                }
                query.push_str(&format!("name = ${}", param_index));
                bindings.push(name.to_string());
                param_index += 1;
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
                (SELECT project_id FROM {} WHERE name = $1 AND repository = $2),
                (SELECT COALESCE(max_id, 0) + 1 FROM max_project)
            ) AS project_id",
            CardTable::Project,
            CardTable::Project
        )
        .to_string()
    }
    pub fn get_query_page_query(table: &CardTable, sort_by: &str) -> String {
        let versions_cte = format!(
            "WITH versions AS (
                SELECT 
                    repository, 
                    name, 
                    version, 
                    ROW_NUMBER() OVER (PARTITION BY repository, name ORDER BY created_at DESC) AS row_num 
                FROM {}
                WHERE ($1 IS NULL OR repository = $1)
                AND ($2 IS NULL OR name LIKE $3 OR repository LIKE $3)
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
                WHERE ($1 IS NULL OR repository = $1)
                AND ($2 IS NULL OR name LIKE $3 OR repository LIKE $3)
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
            SELECT * FROM joined 
            WHERE row_num BETWEEN $4 AND $5
            ORDER BY updated_at DESC",
            versions_cte, stats_cte, filtered_versions_cte, joined_cte
        );

        combined_query
    }
    pub fn get_query_stats_query(table: &CardTable) -> String {
        let base_query = format!(
            "SELECT 
            COALESCE(CAST(COUNT(DISTINCT name) AS INTEGER), 0) AS nbr_names, 
            COALESCE(CAST(COUNT(major) AS INTEGER), 0) AS nbr_versions, 
            COALESCE(CAST(COUNT(DISTINCT repository) AS INTEGER), 0) AS nbr_repositories 
            FROM {}
            WHERE 1=1
            AND ($1 IS NULL OR name LIKE $1 OR repository LIKE $1)",
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
             repository, 
             major, minor, 
             patch, 
             pre_tag, 
             build_tag, 
             uid
             FROM {}
             WHERE 1=1
                AND name = $1
                AND repository = $2
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
        AND ($1 IS NULL OR uid = $1)
        AND ($2 IS NULL OR name = $2)
        AND ($3 IS NULL OR repository = $3)
        AND ($4 IS NULL OR created_at <= TO_DATE($4, 'YYYY-MM-DD'))
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
                for tag in tags.iter() {
                    query.push_str(format!(" AND EXISTS(SELECT 1 FROM jsonb_array_elements(tags) WHERE value::text = '\"{}\"')", tag).as_str());
                }
            }

            if query_args.sort_by_timestamp.unwrap_or(false) {
                query.push_str(" ORDER BY created_at DESC");
            } else {
                // sort by major, minor, patch
                query.push_str(" ORDER BY major DESC, minor DESC, patch DESC");
            }
        }

        query.push_str(" LIMIT $5");

        Ok(query)
    }
    pub fn get_run_parameters_insert_query(nbr_records: usize) -> String {
        let mut query = format!(
            "INSERT INTO {} (
                run_uid, 
                name, 
                value
            ) VALUES ",
            CardTable::Parameters
        )
        .to_string();

        for i in 0..nbr_records {
            if i > 0 {
                query.push_str(", ");
            }
            query.push_str(&format!("(${}, ${}, ${})", 3 * i + 1, 3 * i + 2, 3 * i + 3));
        }

        query
    }
    pub fn get_run_parameter_query(names: &[String]) -> (String, Vec<String>) {
        let mut query = format!(
            "SELECT *
            FROM {}
            WHERE run_uid = $1",
            CardTable::Parameters
        );

        let mut bindings: Vec<String> = Vec::new();
        let mut param_index = 2; // Start from 2 because $1 is used for run_uid

        if !names.is_empty() {
            query.push_str(" AND (");
            for (idx, name) in names.iter().enumerate() {
                if idx > 0 {
                    query.push_str(" OR ");
                }
                query.push_str(&format!("name = ${}", param_index));
                bindings.push(name.to_string());
                param_index += 1;
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
            CardTable::HardwareMetrics
        )
        .to_string();

        for i in 0..nbr_records {
            query.push_str(&format!("(${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${}, ${})", 19 * i + 1, 19 * i + 2, 19 * i + 3, 19 * i + 4, 19 * i + 5, 19 * i + 6, 19 * i + 7, 19 * i + 8, 19 * i + 9, 19 * i + 10, 19 * i + 11, 19 * i + 12, 19 * i + 13, 19 * i + 14, 19 * i + 15, 19 * i + 16, 19 * i + 17, 19 * i + 18, 19 * i + 19));
            if i < nbr_records - 1 {
                query.push_str(", ");
            } else {
                query.push(';');
            }
        }

        query
    }
    pub fn get_projectcard_insert_query() -> String {
        format!(
            "INSERT INTO {} (
        uid, 
        name, 
        repository, 
        app_env,
        project_id, 
        major, 
        minor, 
        patch, 
        version, 
        pre_tag,
        build_tag,
        username) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)",
            CardTable::Project
        )
        .to_string()
    }

    pub fn get_datacard_insert_query() -> String {
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
        data_type, 
        interface_type, 
        tags, 
        runcard_uid, 
        pipelinecard_uid, 
        auditcard_uid, 
        pre_tag, 
        build_tag,
        username
        ) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)",
            CardTable::Data
        )
        .to_string()
    }

    pub fn get_modelcard_insert_query() -> String {
        format!("INSERT INTO {} (
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
        data_type, 
        model_type, 
        interface_type, 
        task_type, 
        tags, 
        runcard_uid, 
        pipelinecard_uid, 
        auditcard_uid, 
        pre_tag, 
        build_tag,
        username
        ) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)", CardTable::Model).to_string()
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
        build_tag,
        username
        ) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)",
            CardTable::Run
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
        build_tag,
        username
        ) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)",
            CardTable::Audit
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
        build_tag,
        username
         ) 
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)",
            CardTable::Pipeline
        )
        .to_string()
    }

    pub fn get_datacard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = $1, 
        name = $2, 
        repository = $3, 
        major = $4, 
        minor = $5, 
        patch = $6, 
        version = $7, 
        contact = $8, 
        data_type = $9, 
        interface_type = $10, 
        tags = $11, 
        runcard_uid = $12, 
        pipelinecard_uid = $13, 
        auditcard_uid = $14, 
        pre_tag = $15, 
        build_tag = $16,
        username = $17
        WHERE uid = $18",
            CardTable::Data
        )
        .to_string()
    }

    pub fn get_modelcard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = $1, 
        name = $2, 
        repository = $3, 
        major = $4, 
        minor = $5, 
        patch = $6, 
        version = $7, 
        contact = $8, 
        datacard_uid = $9, 
        data_type = $10, 
        model_type = $11, 
        interface_type = $12, 
        task_type = $13, 
        tags = $14, 
        runcard_uid = $15, 
        pipelinecard_uid = $16, 
        auditcard_uid = $17, 
        pre_tag = $18, 
        build_tag = $19,
        username = $20
        WHERE uid = $21",
            CardTable::Model
        )
        .to_string()
    }

    pub fn get_runcard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = $1, 
        name = $2, 
        repository = $3, 
        major = $4, 
        minor = $5, 
        patch = $6, 
        version = $7, 
        contact = $8, 
        project = $9, 
        tags = $10, 
        datacard_uids = $11, 
        modelcard_uids = $12, 
        pipelinecard_uid = $13, 
        artifact_uris = $14, 
        compute_environment = $15, 
        pre_tag = $16, 
        build_tag = $17,
        username = $18
        WHERE uid = $19",
            CardTable::Run
        )
        .to_string()
    }

    pub fn get_auditcard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = $1, 
        name = $2, 
        repository = $3, 
        major = $4, 
        minor = $5, 
        patch = $6, 
        version = $7, 
        contact = $8, 
        tags = $9, 
        approved = $10, 
        datacard_uids = $11, 
        modelcard_uids = $12, 
        runcard_uids = $13, 
        pre_tag = $14, 
        build_tag = $15,
        username = $16
        WHERE uid = $17",
            CardTable::Audit
        )
        .to_string()
    }

    pub fn get_pipelinecard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = $1, 
        name = $2, 
        repository = $3, 
        major = $4, 
        minor = $5, 
        patch = $6, 
        version = $7, 
        contact = $8, 
        tags = $9, 
        pipeline_code_uri = $10, 
        datacard_uids = $11, 
        modelcard_uids = $12, 
        runcard_uids = $13, 
        pre_tag = $14, 
        build_tag = $15,
        username = $16
        WHERE uid = $17",
            CardTable::Pipeline
        )
        .to_string()
    }

    pub fn get_artifact_key_insert_query() -> String {
        format!(
            "INSERT INTO {} (uid, registry_type, encrypted_key, storage_key) VALUES ($1, $2, $3, $4)",
            CardTable::ArtifactKey
        )
        .to_string()
    }

    pub fn get_artifact_key_select_query() -> String {
        format!(
            "SELECT uid, registry_type, encrypted_key, storage_key FROM {} WHERE uid = $1 AND registry_type = $2",
            CardTable::ArtifactKey
        )
        .to_string()
    }

    pub fn get_artifact_key_update_query() -> String {
        format!(
            "UPDATE {} SET encrypted_key = $1, created_at = NOW() WHERE uid = $2 AND registry_type = $3",
            CardTable::ArtifactKey
        )
        .to_string()
    }

    pub fn get_operation_insert_query() -> String {
        format!(
            "INSERT INTO {} (username, access_type, access_location) VALUES ($1, $2, $3)",
            CardTable::Operations
        )
        .to_string()
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
            SELECT a.uid, a.registry_type, a.encrypted_key, a.storage_key
            FROM {} as a
            INNER JOIN query_cards as b 
                ON a.uid = b.uid;",
            query_cards_query,
            CardTable::ArtifactKey
        );

        Ok(query)
    }

    pub fn get_artifact_key_delete_query() -> String {
        format!(
            "DELETE FROM {} WHERE uid = $1 AND registry_type = $2",
            CardTable::ArtifactKey
        )
        .to_string()
    }
}
