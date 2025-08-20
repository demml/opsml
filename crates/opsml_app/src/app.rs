use crate::{
    error::AppError,
    reloader::{ReloadConfig, ServiceReloader},
};
use opsml_cards::{card_service::ServiceInfo, ServiceCard};
use opsml_state::app_state;
use opsml_storage::{copy_objects, StorageError};
use opsml_types::{cards::ServiceCardMapping, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use scouter_client::ScouterQueue;
use std::path::{Path, PathBuf};
use std::sync::{Arc, RwLock};
use std::time::Duration;
use tokio::time::sleep;
use tracing::{debug, error, info};

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
/// * `service_info` - The ServiceCard to use for the reloader
/// * `reload_config` - The optional reload configuration. Defaults to every day
/// # Returns
/// * `ServiceReloader` - The created service reloader
pub fn create_service_reloader(
    service_info: ServiceInfo,
    reload_config: Option<ReloadConfig>,
    service_path: PathBuf,
) -> Result<ServiceReloader, AppError> {
    let reload_config = reload_config.unwrap_or_else(|| ReloadConfig::default());
    let service_info = Arc::new(RwLock::new(service_info));
    let reloader = ServiceReloader::new(service_info, reload_config, service_path);
    Ok(reloader)
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
    service: Arc<RwLock<Py<ServiceCard>>>,
    queue: Option<Arc<RwLock<Py<ScouterQueue>>>>,
    reloader: ServiceReloader,
    reload_handle: Option<tokio::task::JoinHandle<()>>,
    load_kwargs: Arc<RwLock<Option<Py<PyDict>>>>,
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
    #[pyo3(signature = (service, queue=None, reload_config=None, path=None))]
    pub fn new(
        py: Python<'_>,
        service: Bound<'_, ServiceCard>,
        queue: Option<Bound<'_, ScouterQueue>>,
        reload_config: Option<ReloadConfig>,
        path: Option<PathBuf>,
    ) -> Result<Self, AppError> {
        let service = service.unbind();
        let queue = queue.map(|q| Arc::new(RwLock::new(q.unbind())));

        let service_info = service
            .bind(py)
            .call_method0("service_info")?
            .extract::<ServiceInfo>()?;

        let service_path = path.unwrap_or_else(|| PathBuf::from(SaveName::ServiceCard));
        let reloader = create_service_reloader(service_info, reload_config, service_path)?;

        Ok(AppState {
            service: Arc::new(RwLock::new(service)),
            queue,
            reloader,
            reload_handle: None,
            load_kwargs: Arc::new(RwLock::new(None)),
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
        let service_path = path.unwrap_or_else(|| PathBuf::from(SaveName::ServiceCard));

        // Load the service card from path
        let service = Py::new(
            py,
            ServiceCard::from_path_rs(py, &service_path, load_kwargs)?,
        )?;
        let service_info = service
            .bind(py)
            .call_method0("service_info")?
            .extract::<ServiceInfo>()?;

        // Get the drift map in cap of drift profiles
        let card_map = load_card_map(&service_path).inspect_err(|e| {
            error!("Failed to load card map from: {:?}", e);
        })?;

        let queue =
            create_scouter_queue(py, card_map, transport_config)?.map(|q| Arc::new(RwLock::new(q)));

        // Create the service reloader
        let reloader = create_service_reloader(service_info, reload_config, service_path)?;

        let kwargs = load_kwargs.map(|kw| kw.clone().unbind());

        Ok(AppState {
            service: Arc::new(RwLock::new(service)),
            queue,
            reloader,
            reload_handle: None,
            load_kwargs: Arc::new(RwLock::new(kwargs)),
        })
    }

    #[getter]
    pub fn service<'py>(&self, py: Python<'py>) -> Result<Bound<'py, ServiceCard>, AppError> {
        Ok(self.service.read().unwrap().bind(py).clone())
    }

    #[getter]
    pub fn queue<'py>(&self, py: Python<'py>) -> Result<Bound<'py, ScouterQueue>, AppError> {
        if let Some(queue) = &self.queue {
            Ok(queue.read().unwrap().bind(py).clone())
        } else {
            Err(AppError::QueueNotFoundError)
        }
    }

    #[getter]
    pub fn reloader_running(&self) -> bool {
        // return initialized if reloader is present
        *self.reloader.running.read().unwrap()
    }

    pub fn reload(&self) -> Result<(), AppError> {
        self.reloader.reload()
    }

    /// Start the reloader functionality
    pub fn start_reloader(&mut self) -> Result<(), AppError> {
        debug!("Starting reloader");
        if self.reloader_running() {
            return Ok(());
        }

        self.start_background_reloader()?;
        let running = self.reloader.running.clone();
        let reload_ready = self.reloader.reload_ready.clone();
        let reload_path = self.reloader.config.write_path.clone();
        let service_path = self.reloader.service_path.clone();
        let load_kwargs = self.load_kwargs.clone();
        let service_arc = self.service.clone();
        let max_retries = self.reloader.config.max_retries;

        debug!(
            "Starting reload loop with arguments running: {:?}, reload_ready: {:?}, reload_path: {:?}",
            running, reload_ready, reload_path
        );

        let handle = app_state().runtime.spawn(async move {
            while Self::check_running_state(&running) {
                if Self::check_reload_ready(&reload_ready) {
                    info!("Ready for a reload");

                    let mut retry_count = 0;

                    retry_count += 1;
                    while retry_count < max_retries {
                        // Perform the reload operation
                        match Self::perform_service_reload(&service_arc, &reload_path, &load_kwargs)
                        {
                            Ok(()) => {
                                info!("Service reloaded successfully");

                                // if successful, move object from reload directory to base directory for service
                                if let Err(e) = Self::cleanup(&reload_path, &service_path) {
                                    error!("Failed to clean up after reload: {:?}", e);
                                }
                                break;
                            }
                            Err(e) => {
                                error!(
                                    "Failed to reload service: {:?}, retry attempt: {}",
                                    e, retry_count
                                );
                                sleep(Duration::from_millis(100 * 2_u64.pow(retry_count))).await;
                                retry_count += 1;
                            }
                        }
                    }

                    // If we exhausted all retries, we should notify the user
                    if retry_count == max_retries {
                        error!("Max retries reached, giving up");
                    }

                    // We don't want infinite retry loops
                    Self::reset_reload_ready_state(&reload_ready);
                }

                tokio::time::sleep(std::time::Duration::from_millis(500)).await;
            }

            debug!("Reload loop terminated");
        });

        self.reload_handle = Some(handle);

        Ok(())
    }

    pub fn stop_reloader(&mut self) -> Result<(), AppError> {
        if !self.reloader_running() {
            return Ok(());
        }

        // Shutdown thread first
        if let Some(handle) = self.reload_handle.take() {
            handle.abort();
            info!("Reload task aborted");
        }

        // shutdown background reloader
        self.reloader.shutdown();

        Ok(())
    }
}

impl AppState {
    /// Check if the reloader is still running
    fn check_running_state(running: &Arc<RwLock<bool>>) -> bool {
        running.read().map(|guard| *guard).unwrap_or_else(|e| {
            error!("Failed to read running state: {:?}", e);
            false
        })
    }

    fn check_reload_ready(reload_ready: &Arc<RwLock<bool>>) -> bool {
        reload_ready.read().map(|guard| *guard).unwrap_or_else(|e| {
            debug!("Failed to read reload_ready state: {:?}", e);
            false
        })
    }

    fn reset_reload_ready_state(reload_ready: &Arc<RwLock<bool>>) {
        match reload_ready.write() {
            Ok(mut guard) => {
                *guard = false;
                info!("Reload ready state reset");
            }
            Err(e) => {
                error!("Failed to reset reload ready state: {:?}", e);
            }
        }
    }

    fn perform_service_reload(
        service_arc: &Arc<RwLock<Py<ServiceCard>>>,
        write_path: &PathBuf,
        load_kwargs: &Arc<RwLock<Option<Py<PyDict>>>>,
    ) -> Result<(), AppError> {
        // Acquire the GIL and load the new service
        let reload_result = Python::with_gil(|py| -> Result<Py<ServiceCard>, AppError> {
            // Read load_kwargs first, in a separate scope to minimize lock duration
            let lock = load_kwargs.read().unwrap();
            let kwargs = lock.as_ref().map(|kw| kw.bind(py));
            // Load the new service card
            let new_service = ServiceCard::from_path_rs(py, write_path, kwargs)?;
            Ok(Py::new(py, new_service)?)
        });

        match reload_result {
            Ok(new_service) => {
                // Now update the service with minimal lock time
                match service_arc.write() {
                    Ok(mut service_guard) => {
                        *service_guard = new_service;
                        info!("Py service updated successfully");
                        Ok(())
                    }
                    Err(e) => {
                        error!("Failed to acquire write lock for service update: {:?}", e);
                        Err(AppError::UpdateServiceError(e.to_string()))
                    }
                }
            }
            Err(e) => {
                error!("Failed to reload service: {:?}", e);
                Err(AppError::ReloadServiceError(e.to_string()))
            }
        }
    }

    fn cleanup(reload_path: &PathBuf, service_path: &PathBuf) -> Result<(), AppError> {
        // Move contents of reload_path to service_path
        copy_objects(reload_path, service_path)?;

        // delete contents of reload_path
        std::fs::remove_dir_all(reload_path).map_err(|e| {
            error!("Failed to delete service path contents: {:?}", e);
            StorageError::IoError(e)
        })?;

        Ok(())
    }

    /// Helper to get the internal service reloader
    pub fn start_background_reloader(&mut self) -> Result<(), AppError> {
        let (event_rx, shutdown_rx) = self.reloader.create_channels()?;
        let running = self.reloader.running.clone();
        let reload_ready = self.reloader.reload_ready.clone();

        ServiceReloader::start_reloader(
            app_state().runtime.clone(),
            self.reloader.config.clone(),
            event_rx,
            shutdown_rx,
            running,
            self.reloader.service_info.clone(),
            reload_ready,
            self.reloader.config.write_path.clone(),
        )?;

        self.reloader.start()?;

        Ok(())
    }
}
