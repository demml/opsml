use crate::error::RegistryError;
use crate::registries::client::base::Registry;
use crate::registries::client::experiment::ClientExperimentRegistry;
use crate::registries::client::experiment::ExperimentRegistry;
use opsml_settings::config::OpsmlMode;
use opsml_state::{app_state, get_api_client};
use opsml_types::cards::{HardwareMetrics, Metric, Parameter};
use opsml_types::contracts::{
    GetHardwareMetricRequest, GetMetricRequest, GetParameterRequest, HardwareMetricRequest,
    MetricRequest, ParameterRequest,
};
use opsml_types::*;
use tracing::{error, instrument};

#[cfg(feature = "server")]
use crate::registries::server::experiment::ServerExperimentRegistry;

#[derive(Debug)]
pub enum OpsmlExperimentRegistry {
    Client(ClientExperimentRegistry),

    #[cfg(feature = "server")]
    Server(ServerExperimentRegistry),
}

impl OpsmlExperimentRegistry {
    #[instrument(skip_all)]
    pub fn new(registry_type: RegistryType) -> Result<Self, RegistryError> {
        let state = &app_state();
        let mode = &*state.mode()?;

        match mode {
            OpsmlMode::Client => {
                let api_client = get_api_client().clone();
                let client_registry = ClientExperimentRegistry::new(registry_type, api_client)?;
                Ok(Self::Client(client_registry))
            }
            OpsmlMode::Server => {
                #[cfg(feature = "server")]
                {
                    let config = state.config()?;
                    let settings = config.storage_settings().inspect_err(|e| {
                        error!("Failed to get storage settings: {e}");
                    })?;

                    let db_settings = config.database_settings.clone();

                    // TODO (steven): Why clone config when we could use app state directly in server registry?
                    let server_registry = state.block_on(async {
                        ServerExperimentRegistry::new(registry_type, settings, db_settings).await
                    })?;

                    Ok(Self::Server(server_registry))
                }
                #[cfg(not(feature = "server"))]
                {
                    error!("Server feature not enabled");
                    Err(RegistryError::ServerFeatureNotEnabled)
                }
            }
        }
    }

    pub fn mode(&self) -> RegistryMode {
        match self {
            Self::Client(client_registry) => client_registry.mode(),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => server_registry.mode(),
        }
    }

    pub fn table_name(&self) -> String {
        match self {
            Self::Client(client_registry) => client_registry.table_name(),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => server_registry.table_name(),
        }
    }

    pub async fn insert_hardware_metrics(
        &self,
        metrics: HardwareMetricRequest,
    ) -> Result<(), RegistryError> {
        match self {
            Self::Client(client_registry) => {
                // Clone the client_registry to avoid lifetime issues
                let client_registry = client_registry.clone();
                let _ = app_state()
                    .runtime
                    .spawn_blocking(move || client_registry.insert_hardware_metrics(&metrics))
                    .await
                    .map_err(|e| {
                        error!("Failed to insert hardware metrics: {e}");
                        RegistryError::from(e)
                    })?;
                Ok(())
            }
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                server_registry.insert_hardware_metrics(&metrics).await
            }
        }
    }

    pub fn get_hardware_metrics(
        &self,
        request: &GetHardwareMetricRequest,
    ) -> Result<Vec<HardwareMetrics>, RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.get_hardware_metrics(request)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async { server_registry.get_hardware_metrics(request).await })
            }
        }
    }

    pub fn insert_metrics(&self, metrics: &MetricRequest) -> Result<(), RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.insert_metrics(metrics)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async { server_registry.insert_metrics(metrics).await })
            }
        }
    }

    pub fn get_metrics(&self, metrics: &GetMetricRequest) -> Result<Vec<Metric>, RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.get_metrics(metrics)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async { server_registry.get_metrics(metrics).await })
            }
        }
    }

    pub fn insert_parameters(&self, parameters: &ParameterRequest) -> Result<(), RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.insert_parameters(parameters)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async { server_registry.insert_parameters(parameters).await })
            }
        }
    }

    pub fn get_parameters(
        &self,
        parameters: &GetParameterRequest,
    ) -> Result<Vec<Parameter>, RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.get_parameters(parameters)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async { server_registry.get_parameters(parameters).await })
            }
        }
    }
}
