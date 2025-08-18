use crate::{
    error::AppError,
    reloader::{ReloadConfig, ServiceReloader},
};
use opsml_cards::{card_service::ServiceInfo, ServiceCard};
use opsml_state::app_state;
use opsml_types::{cards::ServiceCardMapping, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use scouter_client::ScouterQueue;
use std::path::{Path, PathBuf};
use std::sync::{Arc, RwLock};
use tracing::{debug, error};

/// Load a card map from path
fn load_card_map(path: &Path) -> Result<ServiceCardMapping, AppError> {
    let card_mapping_path = path.join(SaveName::CardMap).with_extension(Suffix::Json);
    debug!("Loading card mapping from: {:?}", card_mapping_path);
    let mapping = ServiceCardMapping::from_path(&card_mapping_path)?;
    Ok(mapping)
}

/// Helper for loading a scouter queue
/// This function will create a ScouterQueue from the card map and transport config if they exist
/// # Arguments
/// * `py` - The Python interpreter instance
/// * `card_map` - The service card mapping
/// * `transport_config` - The transport config for the scouter queue
/// # Returns
/// * `Some(Py<ScouterQueue>)` if the scouter queue was created successfully
/// * `None` if the scouter queue could not be created
pub fn create_scouter_queue(
    py: Python<'_>,
    card_map: ServiceCardMapping,
    transport_config: Option<&Bound<'_, PyAny>>,
) -> Result<Option<Py<ScouterQueue>>, AppError> {
    let queue = if card_map.drift_paths.is_empty() {
        debug!("No drift paths or transport config found in card map");
        None
    } else if let Some(config) = transport_config {
        debug!("Drift paths found in card map, creating ScouterQueue");
        let rt = app_state().runtime.clone();
        let scouter_queue = ScouterQueue::from_path_rs(py, card_map.drift_paths, config, rt)?;
        Some(Py::new(py, scouter_queue)?)
    } else {
        debug!("No transport config found in card map");
        None
    };

    Ok(queue)
}

/// Creates a  ServiceReloader from a ServiceCard and optional ReloadConfig.
/// # Arguments
/// * `py` - The Python interpreter instance
/// * `service` - The ServiceCard to use for the reloader
/// * `reload_config` - The optional reload config to use for the reloader
/// # Returns
/// * `Some(ServiceReloader)` if the reloader was created successfully
/// * `None` if the reloader could not be created
pub fn create_service_reloader(
    py: Python<'_>,
    service: Py<ServiceCard>,
    reload_config: Option<ReloadConfig>,
) -> Result<Option<ServiceReloader>, AppError> {
    match reload_config {
        Some(config) => {
            let service_info = Arc::new(RwLock::new(
                service
                    .bind(py)
                    .call_method0("service_info")?
                    .extract::<ServiceInfo>()?,
            ));
            let (reloader, event_rx, shutdown_rx) = ServiceReloader::new(service_info.clone());
            let initialized = reloader.initialized.clone();
            ServiceReloader::start_reloader(
                app_state().runtime.clone(),
                service.clone_ref(py),
                config,
                event_rx,
                shutdown_rx,
                initialized,
                service_info,
            )?;

            // check for background initialization
            reloader.init()?;

            Ok(Some(reloader))
        }
        None => Ok(None),
    }
}

/// Helper for managing application state. Intended to be used with api frameworks like FastAPI
/// where an api app can be created with a lifespan and internal application state that is available
/// to all request handlers. The OpsML application state contains:
/// - A ServiceCard that contains one or more models or prompts
/// - An optional ScouterQueue for real-time model monitoring. This is loaded from
/// the card map that is created when the ServiceCard is loaded
/// - An optional reloader that is responsible for reloading the ServiceCard and its associated
/// resources when changes are detected
#[pyclass]
#[derive(Debug)]
pub struct AppState {
    service: Py<ServiceCard>,
    queue: Option<Py<ScouterQueue>>,
    reloader: Option<ServiceReloader>,
}

#[pymethods]
impl AppState {
    /// Instantiate a new application state. Typically from_path is used; however, an new/init
    /// method is provided for consistency with other classes
    /// # Arguments
    /// * `service` - The ServiceCard to use for the application state
    /// * `queue` - An optional ScouterQueue to use for the application state. If not provided,
    /// no queue will be created.
    ///
    /// # Returns
    /// * `AppState` - The application state containing the ServiceCard and optional ScouterQueue  
    #[new]
    #[pyo3(signature = (service, queue=None))]
    pub fn new(
        service: Bound<'_, ServiceCard>,
        queue: Option<Bound<'_, ScouterQueue>>,
    ) -> Result<Self, AppError> {
        let service = service.unbind();
        let queue = queue.map(|q| q.unbind());
        Ok(AppState {
            service,
            queue,
            reloader: None,
        })
    }
    /// This method will load an application state from a path
    /// This is primarily used for loading an application during api start where a user
    /// may wish to load an Opsml ServiceCard along with the appropriate ScouterQueue for monitoring
    /// This class and it's functionality may expand in the future
    ///
    /// # Arguments
    /// * `py` - Python interpreter state
    /// * `path` - The root path to the application directory containing files
    /// * `transport_config` - The transport config to use with the ScouterQueue. If not provided,
    /// no queue will be created.
    /// * `reload_config` - The reload config to use with the ServiceReloader. If not provided,
    /// no reloader will be created.
    /// * `load_kwargs` - Load kwargs to pass to the ServiceCard loader
    #[staticmethod]
    #[pyo3(signature = (path=None, transport_config=None, reload_config=None, load_kwargs=None))]
    pub fn from_path(
        py: Python,
        path: Option<PathBuf>,
        transport_config: Option<&Bound<'_, PyAny>>,
        reload_config: Option<ReloadConfig>,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Self, AppError> {
        let path = path.unwrap_or_else(|| PathBuf::from(SaveName::ServiceCard));

        // Load the service card from path
        let service = Py::new(py, ServiceCard::from_path_rs(py, &path, load_kwargs)?)?;

        // Get the drift map in cap of drift profiles
        let card_map = load_card_map(&path).inspect_err(|e| {
            error!("Failed to load card map from: {:?}", e);
        })?;

        let queue = create_scouter_queue(py, card_map, transport_config)?;

        // Create the service reloader if reload config is provided
        let reloader = create_service_reloader(py, service.clone_ref(py), reload_config)?;

        Ok(AppState {
            service,
            queue,
            reloader,
        })
    }

    #[getter]
    pub fn service<'py>(&self, py: Python<'py>) -> Result<&Bound<'py, ServiceCard>, AppError> {
        Ok(self.service.bind(py))
    }

    #[getter]
    pub fn queue<'py>(&self, py: Python<'py>) -> Result<&Bound<'py, ScouterQueue>, AppError> {
        if let Some(queue) = &self.queue {
            Ok(queue.bind(py))
        } else {
            Err(AppError::QueueNotFoundError)
        }
    }

    #[getter]
    pub fn has_reloader(&self) -> bool {
        // return initialized if reloader is present
        if let Some(reloader) = &self.reloader {
            *reloader.initialized.read().unwrap()
        } else {
            false
        }
    }

    pub fn reload(&self) -> Result<(), AppError> {
        if let Some(reloader) = &self.reloader {
            reloader.reload()
        } else {
            Err(AppError::ReloaderNotFound)
        }
    }
}
