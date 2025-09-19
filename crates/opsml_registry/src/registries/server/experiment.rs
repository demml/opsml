use crate::error::RegistryError;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_settings::DatabaseSettings;
use opsml_sql::enums::client::get_sql_client;
use opsml_sql::enums::utils::get_next_version;
use opsml_sql::{enums::client::SqlClientEnum, schemas::*, traits::*};
use opsml_types::{
    cards::{
        CPUMetrics, CardTable, HardwareMetrics, MemoryMetrics, Metric, NetworkRates, Parameter,
    },
    contracts::*,
    *,
};
use opsml_utils::get_utc_datetime;
use sqlx::types::Json as SqlxJson;
use std::sync::Arc;

#[derive(Debug, Clone)]
pub struct ServerExperiment {
    sql_client: Arc<SqlClientEnum>,
    pub table_name: CardTable,
    pub storage_settings: OpsmlStorageSettings,
}

impl ServerExperiment {
    pub fn mode(&self) -> RegistryMode {
        RegistryMode::Server
    }

    pub fn table_name(&self) -> String {
        self.table_name.to_string()
    }
    pub async fn new(
        storage_settings: OpsmlStorageSettings,
        database_settings: DatabaseSettings,
    ) -> Result<Self, RegistryError> {
        let sql_client = Arc::new(get_sql_client(&database_settings).await?);
        let table_name = CardTable::from_registry_type(&RegistryType::Experiment);

        Ok(Self {
            sql_client,
            table_name,
            storage_settings,
        })
    }

    pub async fn insert_hardware_metrics(
        &self,
        metrics: &HardwareMetricRequest,
    ) -> Result<(), RegistryError> {
        let created_at = get_utc_datetime();

        let record = HardwareMetricsRecord {
            experiment_uid: metrics.experiment_uid.clone(),
            created_at: created_at.clone(),
            cpu_percent_utilization: metrics.metrics.cpu.cpu_percent_utilization,
            cpu_percent_per_core: SqlxJson(metrics.metrics.cpu.cpu_percent_per_core.clone()),
            free_memory: metrics.metrics.memory.free_memory,
            total_memory: metrics.metrics.memory.total_memory,
            used_memory: metrics.metrics.memory.used_memory,
            available_memory: metrics.metrics.memory.available_memory,
            used_percent_memory: metrics.metrics.memory.used_percent_memory,
            bytes_recv: metrics.metrics.network.bytes_recv,
            bytes_sent: metrics.metrics.network.bytes_sent,
        };
        Ok(self.sql_client.insert_hardware_metrics(&record).await?)
    }

    pub async fn log_artifact(
        &self,
        space: String,
        name: String,
        version: String,
        media_type: String,
        artifact_type: ArtifactType,
    ) -> Result<CreateArtifactResponse, RegistryError> {
        let version_request = CardVersionRequest {
            space: space.clone(),
            name: name.clone(),
            version: Some(version.clone()),
            pre_tag: None,
            build_tag: None,
            version_type: opsml_semver::VersionType::Major,
        };

        let version = get_next_version(
            self.sql_client.clone(),
            &CardTable::Artifact,
            version_request,
        )
        .await?;

        let artifact_record =
            ArtifactSqlRecord::new(space, name, version, media_type, artifact_type.to_string());

        self.sql_client
            .insert_artifact_record(&artifact_record)
            .await?;

        let response = CreateArtifactResponse {
            uid: artifact_record.uid.clone(),
            space: artifact_record.space,
            name: artifact_record.name,
            version: artifact_record.version,
        };

        Ok(response)
    }

    pub async fn get_hardware_metrics(
        &self,
        request: &GetHardwareMetricRequest,
    ) -> Result<Vec<HardwareMetrics>, RegistryError> {
        let records = self
            .sql_client
            .get_hardware_metric(&request.experiment_uid)
            .await?;

        let metrics = records
            .into_iter()
            .map(|m| HardwareMetrics {
                created_at: m.created_at,
                cpu: CPUMetrics {
                    cpu_percent_utilization: m.cpu_percent_utilization,
                    cpu_percent_per_core: m.cpu_percent_per_core.to_vec(),
                },
                memory: MemoryMetrics {
                    free_memory: m.free_memory,
                    total_memory: m.total_memory,
                    used_memory: m.used_memory,
                    available_memory: m.available_memory,
                    used_percent_memory: m.used_percent_memory,
                },
                network: NetworkRates {
                    bytes_recv: m.bytes_recv,
                    bytes_sent: m.bytes_sent,
                },
            })
            .collect::<Vec<_>>();

        Ok(metrics)
    }

    pub async fn insert_metrics(&self, metrics: &MetricRequest) -> Result<(), RegistryError> {
        let records = metrics
            .metrics
            .iter()
            .map(|m| {
                MetricRecord::new(
                    metrics.experiment_uid.clone(),
                    m.name.clone(),
                    m.value,
                    m.step,
                    m.timestamp,
                    m.is_eval,
                )
            })
            .collect::<Vec<_>>();

        Ok(self.sql_client.insert_experiment_metrics(&records).await?)
    }

    pub async fn get_metrics(
        &self,
        metrics: &GetMetricRequest,
    ) -> Result<Vec<Metric>, RegistryError> {
        let records = self
            .sql_client
            .get_experiment_metric(&metrics.experiment_uid, &metrics.names, metrics.is_eval)
            .await?;

        let metrics = records
            .into_iter()
            .map(|m| Metric {
                created_at: m.created_at,
                name: m.name,
                value: m.value,
                step: m.step,
                timestamp: m.timestamp,
                is_eval: m.is_eval,
            })
            .collect::<Vec<_>>();

        Ok(metrics)
    }

    pub async fn insert_parameters(
        &self,
        parameters: &ParameterRequest,
    ) -> Result<(), RegistryError> {
        let records = parameters
            .parameters
            .iter()
            .map(|p| {
                ParameterRecord::new(
                    parameters.experiment_uid.clone(),
                    p.name.clone(),
                    p.value.clone(),
                )
            })
            .collect::<Vec<_>>();

        Ok(self
            .sql_client
            .insert_experiment_parameters(&records)
            .await?)
    }

    pub async fn get_parameters(
        &self,
        parameters: &GetParameterRequest,
    ) -> Result<Vec<Parameter>, RegistryError> {
        let records = self
            .sql_client
            .get_experiment_parameter(&parameters.experiment_uid, &parameters.names)
            .await?;

        let params = records
            .into_iter()
            .map(|m| Parameter {
                name: m.name,
                value: m.value.0,
            })
            .collect::<Vec<_>>();

        Ok(params)
    }
}
