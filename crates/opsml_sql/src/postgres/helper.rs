use crate::error::SqlError;

use opsml_semver::VersionParser;
/// this file contains helper logic for generating sql queries across different databases
use opsml_types::{cards::CardTable, contracts::CardQueryArgs};
use opsml_utils::utils::is_valid_uuidv7;

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
        format!("SELECT uid FROM {} WHERE uid = $1", table)
    }

    pub fn get_user_insert_query() -> String {
        format!(
            "INSERT INTO {} (username, password_hash, hashed_recovery_codes, permissions, group_permissions, role, active, email) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            CardTable::Users
        )
    }

    pub fn get_user_query() -> String {
        format!(
            "SELECT id, created_at, active, username, password_hash, hashed_recovery_codes, permissions, group_permissions, role, refresh_token, email, updated_at FROM {} WHERE username = $1",
            CardTable::Users
        )
    }

    pub fn get_user_delete_query() -> String {
        format!("DELETE FROM {} WHERE username = $1", CardTable::Users).to_string()
    }

    pub fn get_users_query() -> String {
        format!(
            "SELECT id, created_at, active, username, password_hash, hashed_recovery_codes, permissions, group_permissions, role, refresh_token, email, updated_at FROM {}",
            CardTable::Users
        )
        .to_string()
    }

    pub fn get_last_admin_query() -> String {
        format!(
            "SELECT username FROM {} WHERE role = 'admin'",
            CardTable::Users
        )
        .to_string()
    }

    pub fn get_user_update_query() -> String {
        format!(
            "UPDATE {} SET 
            active = $1, 
            password_hash = $2, 
            hashed_recovery_codes = $3,
            permissions = $4, 
            group_permissions = $5,
            refresh_token = $6,
            email = $7,
            updated_at = CURRENT_TIMESTAMP
            WHERE username = $8",
            CardTable::Users
        )
    }

    pub fn get_hardware_metric_query() -> String {
        let query = format!(
            "SELECT * FROM {} WHERE experiment_uid = $1",
            CardTable::HardwareMetrics
        );

        query
    }
    pub fn get_experiment_metric_insert_query() -> String {
        format!(
            "INSERT INTO {} (
                experiment_uid, 
                name, 
                value,
                step,
                timestamp
            ) VALUES ($1, $2, $3, $4, $5)",
            CardTable::Metrics
        )
    }

    pub fn get_experiment_metrics_insert_query(nbr_records: usize) -> String {
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
    pub fn get_experiment_metric_query(names: &[String]) -> (String, Vec<String>) {
        let mut query = format!(
            "SELECT *
            FROM {}
            WHERE experiment_uid = $1",
            CardTable::Metrics
        );

        let mut bindings: Vec<String> = Vec::new();
        let mut param_index = 2; // Start from 2 because $1 is used for experiment_uid

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

    pub fn get_query_page_query(table: &CardTable, sort_by: &str) -> String {
        let versions_cte = format!(
            "WITH versions AS (
                SELECT 
                    space, 
                    name, 
                    version, 
                    ROW_NUMBER() OVER (PARTITION BY space, name ORDER BY created_at DESC) AS row_num 
                FROM {}
                WHERE ($1 IS NULL OR space = $1)
                AND ($2 IS NULL OR name LIKE $3 OR space LIKE $3)
            )", table
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
                WHERE ($1 IS NULL OR space = $1)
                AND ($2 IS NULL OR name LIKE $3 OR space LIKE $3)
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
            SELECT * FROM joined 
            WHERE row_num > $4 AND row_num <= $5
            ORDER BY updated_at DESC",
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
                WHERE space = $1
                AND name = $2
            )", table
        );

        let query = format!(
            "{}
            SELECT
            space,
            name,
            version,
            created_at,
            row_num
            FROM versions
            WHERE row_num > $3 AND row_num <= $4
            ORDER BY created_at DESC",
            versions_cte
        );

        query
    }

    pub fn get_query_stats_query(table: &CardTable) -> String {
        let base_query = format!(
            "SELECT
            COALESCE(CAST(COUNT(DISTINCT name) AS INTEGER), 0) AS nbr_names, 
            COALESCE(CAST(COUNT(major) AS INTEGER), 0) AS nbr_versions, 
            COALESCE(CAST(COUNT(DISTINCT space) AS INTEGER), 0) AS nbr_spaces 
            FROM {}
            WHERE 1=1
            AND ($1 IS NULL OR name LIKE $1 OR space LIKE $1)
            AND ($2 IS NULL OR name = $2 OR space = $2)",
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
                AND name = $1
                AND space = $2
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
        AND ($3 IS NULL OR space = $3)
        AND ($4 IS NULL OR created_at <= TO_DATE($4, 'YYYY-MM-DD'))
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
                query.push_str(&format!("name = ${}", param_index));
                bindings.push(name.to_string());
                param_index += 1;
            }
            query.push(')');
        }

        (query, bindings)
    }
    pub fn get_hardware_metrics_insert_query() -> String {
        format!(
            "INSERT INTO {} (
                experiment_uid,
                created_at,
                cpu_percent_utilization,
                cpu_percent_per_core,
                free_memory,
                total_memory,
                used_memory,
                available_memory,
                used_percent_memory,
                bytes_recv,
                bytes_sent
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)",
            CardTable::HardwareMetrics
        )
    }

    pub fn get_datacard_insert_query() -> String {
        format!(
            "INSERT INTO {} (
        uid, 
        app_env, 
        name, 
        space, 
        major, 
        minor, 
        patch, 
        version, 
        data_type, 
        interface_type, 
        tags, 
        experimentcard_uid, 
        auditcard_uid, 
        pre_tag, 
        build_tag,
        username,
        opsml_version
        ) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)",
            CardTable::Data,
        )
    }

    pub fn get_promptcard_insert_query() -> String {
        format!(
            "INSERT INTO {} (
            uid, 
            app_env, 
            name, 
            space, 
            major, 
            minor, 
            patch, 
            version, 
            tags, 
            experimentcard_uid, 
            auditcard_uid, 
            pre_tag, 
            build_tag,
            username,
            opsml_version
            ) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)",
            CardTable::Prompt
        )
    }

    pub fn get_modelcard_insert_query() -> String {
        format!("INSERT INTO {} (
        uid, 
        app_env, 
        name, 
        space, 
        major, 
        minor, 
        patch, 
        version, 
        datacard_uid, 
        data_type, 
        model_type, 
        interface_type, 
        task_type, 
        tags, 
        experimentcard_uid, 
        auditcard_uid, 
        pre_tag, 
        build_tag,
        username,
        opsml_version
        ) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)", CardTable::Model)
    }

    pub fn get_experimentcard_insert_query() -> String {
        format!(
            "INSERT INTO {} (
        uid,
        app_env, 
        name, 
        space, 
        major, 
        minor, 
        patch, 
        version, 
        tags, 
        datacard_uids, 
        modelcard_uids, 
        promptcard_uids,
        card_deck_uids,
        experimentcard_uids,
        pre_tag, 
        build_tag,
        username,
        opsml_version
        ) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)",
            CardTable::Experiment
        )
    }

    pub fn get_auditcard_insert_query() -> String {
        format!(
            "INSERT INTO {} (
        uid, 
        app_env, 
        name, 
        space, 
        major, 
        minor, 
        patch, 
        version, 
        tags, 
        approved, 
        datacard_uids, 
        modelcard_uids, 
        experimentcard_uids, 
        pre_tag, 
        build_tag,
        username,
        opsml_version
        ) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)",
            CardTable::Audit
        )
    }

    pub fn get_carddeck_insert_query() -> String {
        format!("INSERT INTO {} (uid, app_env, name, space, major, minor, patch, version, pre_tag, build_tag, cards, username, opsml_version) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)", CardTable::Deck)
            .to_string()
    }

    pub fn get_carddeck_update_query() -> String {
        format!(
            "UPDATE {} SET 
            app_env = $1, 
            name = $2,
            space = $3,
            major = $4, 
            minor = $5,
            patch = $6, 
            version = $7, 
            cards = $8,
            username = $9,
            opsml_version = $10
            WHERE uid = $11",
            CardTable::Deck
        )
        .to_string()
    }

    pub fn get_datacard_update_query() -> String {
        format!(
            "UPDATE {} SET 
            app_env = $1, 
            name = $2, 
            space = $3, 
            major = $4, 
            minor = $5, 
            patch = $6, 
            version = $7, 
            data_type = $8, 
            interface_type = $9, 
            tags = $10, 
            experimentcard_uid = $11, 
            auditcard_uid = $12, 
            pre_tag = $13, 
            build_tag = $14,
            username = $15,
            opsml_version = $16
            WHERE uid = $17",
            CardTable::Data
        )
    }

    pub fn get_promptcard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = $1, 
        name = $2, 
        space = $3, 
        major = $4, 
        minor = $5, 
        patch = $6, 
        version = $7, 
        tags = $8, 
        experimentcard_uid = $9, 
        auditcard_uid = $10, 
        pre_tag = $11, 
        build_tag = $12,
        username = $13,
        opsml_version = $14
        WHERE uid = $15",
            CardTable::Prompt
        )
    }

    pub fn get_modelcard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = $1, 
        name = $2, 
        space = $3, 
        major = $4, 
        minor = $5, 
        patch = $6, 
        version = $7, 
        datacard_uid = $8, 
        data_type = $9, 
        model_type = $10, 
        interface_type = $11, 
        task_type = $12, 
        tags = $13, 
        experimentcard_uid = $14, 
        auditcard_uid = $15, 
        pre_tag = $16, 
        build_tag = $17,
        username = $18,
        opsml_version = $19
        WHERE uid = $20",
            CardTable::Model
        )
    }

    pub fn get_experimentcard_update_query() -> String {
        format!(
            "UPDATE {} SET 
            app_env = $1, 
            name = $2, 
            space = $3, 
            major = $4, 
            minor = $5, 
            patch = $6, 
            version = $7, 
            tags = $8, 
            datacard_uids = $9, 
            modelcard_uids = $10, 
            promptcard_uids = $11,
            card_deck_uids = $12,
            experimentcard_uids = $13, 
            pre_tag = $14, 
            build_tag = $15,
            username = $16,
            opsml_version = $17
            WHERE uid = $18",
            CardTable::Experiment
        )
    }

    pub fn get_auditcard_update_query() -> String {
        format!(
            "UPDATE {} SET 
        app_env = $1, 
        name = $2, 
        space = $3, 
        major = $4, 
        minor = $5, 
        patch = $6, 
        version = $7, 
        tags = $8, 
        approved = $9, 
        datacard_uids = $10, 
        modelcard_uids = $11, 
        experimentcard_uids = $12, 
        pre_tag = $13, 
        build_tag = $14,
        username = $15,
        opsml_version = $16
        WHERE uid = $17",
            CardTable::Audit
        )
    }

    pub fn get_artifact_key_insert_query() -> String {
        format!(
            "INSERT INTO {} (uid, space, registry_type, encrypted_key, storage_key) VALUES ($1, $2, $3, $4, $5)",
            CardTable::ArtifactKey
        )
    }

    pub fn get_artifact_key_select_query() -> String {
        format!(
            "SELECT uid, space, registry_type, encrypted_key, storage_key FROM {} WHERE uid = $1 AND registry_type = $2",
            CardTable::ArtifactKey
        )
    }

    pub fn get_artifact_key_update_query() -> String {
        format!(
            "UPDATE {} SET encrypted_key = $1, created_at = NOW() WHERE uid = $2 AND registry_type = $3",
            CardTable::ArtifactKey
        )
    }

    pub fn get_audit_event_insert_query() -> String {
        format!(
            "INSERT INTO {} (
            username, 
            client_ip, 
            user_agent, 
            operation, 
            resource_type, 
            resource_id,
            access_location,
            status,
            error_message,
            metadata,
            registry_type,
            route
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)",
            CardTable::AuditEvent
        )
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

    pub fn get_artifact_key_from_storage_path_query() -> String {
        format!(
            "SELECT uid, registry_type, encrypted_key, storage_key FROM {} WHERE storage_key = $1 AND registry_type = $2",
            CardTable::ArtifactKey
        )
    }

    pub fn get_artifact_key_delete_query() -> String {
        format!(
            "DELETE FROM {} WHERE uid = $1 AND registry_type = $2",
            CardTable::ArtifactKey
        )
    }
}
