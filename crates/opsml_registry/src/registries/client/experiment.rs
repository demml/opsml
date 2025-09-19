use crate::error::RegistryError;
use crate::registries::client::artifact::ArtifactRegistry;
use crate::registries::client::base::Registry;
use opsml_client::OpsmlApiClient;
use opsml_types::{
    api::*,
    cards::{CardTable, HardwareMetrics, Metric, Parameter},
    contracts::*,
    RegistryType,
};
use std::sync::Arc;
use tracing::error;

#[derive(Debug, Clone)]
pub struct ClientExperiment {
    pub api_client: Arc<OpsmlApiClient>,
}

impl ClientExperiment {
    pub fn new(api_client: Arc<OpsmlApiClient>) -> Result<Self, RegistryError> {
        Ok(Self { api_client })
    }
}

impl Registry for ClientExperiment {
    fn client(&self) -> &Arc<OpsmlApiClient> {
        &self.api_client
    }
    fn table_name(&self) -> String {
        CardTable::from_registry_type(&RegistryType::Experiment).to_string()
    }

    fn registry_type(&self) -> &RegistryType {
        &RegistryType::Experiment
    }
}

pub trait ExperimentRegistry: Registry {
    fn insert_hardware_metrics(
        &self,
        metrics: &HardwareMetricRequest,
    ) -> Result<(), RegistryError> {
        let body = serde_json::to_value(metrics)?;

        let response = self
            .client()
            .request(
                Routes::ExperimentHardwareMetrics,
                RequestType::Put,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to insert hardware metrics {}", e);
            })?;

        let inserted = response
            .json::<HardwareMetricResponse>()
            .map_err(RegistryError::RequestError)?;

        if inserted.success {
            Ok(())
        } else {
            Err(RegistryError::InsertHardwareMetricError)
        }
    }

    fn get_hardware_metrics(
        &self,
        metrics: &GetHardwareMetricRequest,
    ) -> Result<Vec<HardwareMetrics>, RegistryError> {
        let query_string = serde_qs::to_string(metrics)?;

        let response = self
            .client()
            .request(
                Routes::ExperimentHardwareMetrics,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to get hardware metrics {}", e);
            })?;

        response
            .json::<Vec<HardwareMetrics>>()
            .map_err(RegistryError::RequestError)
    }

    fn insert_metrics(&self, metrics: &MetricRequest) -> Result<(), RegistryError> {
        let body = serde_json::to_value(metrics)?;

        let response = self
            .client()
            .request(
                Routes::ExperimentMetrics,
                RequestType::Put,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to insert metrics {}", e);
            })?;

        let inserted = response
            .json::<MetricResponse>()
            .map_err(RegistryError::RequestError)?;

        if inserted.success {
            Ok(())
        } else {
            Err(RegistryError::InsertMetricError)
        }
    }

    fn get_metrics(&self, metrics: &GetMetricRequest) -> Result<Vec<Metric>, RegistryError> {
        let body = serde_json::to_value(metrics)?;

        let response = self
            .client()
            .request(
                Routes::ExperimentMetrics,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to get metrics {}", e);
            })?;

        response
            .json::<Vec<Metric>>()
            .map_err(RegistryError::RequestError)
    }

    fn insert_parameters(&self, parameters: &ParameterRequest) -> Result<(), RegistryError> {
        let body = serde_json::to_value(parameters)?;

        let response = self
            .client()
            .request(
                Routes::ExperimentParameters,
                RequestType::Put,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to insert parameters {}", e);
            })?;

        let inserted = response.json::<ParameterResponse>()?;

        if inserted.success {
            Ok(())
        } else {
            Err(RegistryError::InsertParameterError)
        }
    }

    fn get_parameters(
        &self,
        parameters: &GetParameterRequest,
    ) -> Result<Vec<Parameter>, RegistryError> {
        let body = serde_json::to_value(parameters)?;

        let response = self
            .client()
            .request(
                Routes::ExperimentParameters,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to get parameters {}", e);
            })?;

        response
            .json::<Vec<Parameter>>()
            .map_err(RegistryError::RequestError)
    }
}

impl ExperimentRegistry for ClientExperiment {}
impl ArtifactRegistry for ClientExperiment {}
