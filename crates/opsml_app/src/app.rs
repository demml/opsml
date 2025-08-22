use crate::types::{DownloadEvent, QueueState, ReloadEvent, ReloadEventLoops, ReloaderState};
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
use pyo3::PyTraverseError;
use pyo3::PyVisit;
use scouter_client::ScouterQueue;
use std::path::{Path, PathBuf};
use std::sync::{Arc, RwLock};
use std::time::Duration;
use tokio::sync::mpsc::{self, UnboundedReceiver};
use tokio::time::sleep;
use tracing::{debug, error, info};

/// Load a card map from path
fn load_card_map(path: &Path) -> Result<ServiceCardMapping, AppError> {
    let card_mapping_path = path.join(SaveName::CardMap).with_extension(Suffix::Json);
    debug!("Loading card mapping from: {:?}", card_mapping_path);
    let mapping = ServiceCardMapping::from_path(&card_mapping_path)?;
    Ok(mapping)
}

pub enum AppEvent {
    Reload,
}

/// Helper for loading a scouter queue
/// This function will create a ScouterQueue from the card map and transport config if they exist
/// # Arguments
/// * `py` - The Python interpreter instance
/// * `card_map` - The service card mapping
/// * `transport_config` - The transport config for the scouter queue
/// # Returns
/// * `Some(Arc<QueueState>)` if the scouter queue was created successfully
/// * `None` if the scouter queue could not be created
pub fn create_scouter_queue(
    py: Python<'_>,
    card_map: ServiceCardMapping,
    transport_config: Option<&Bound<'_, PyAny>>,
) -> Result<Option<Arc<QueueState>>, AppError> {
    let queue = if card_map.drift_paths.is_empty() {
        debug!("No drift paths or transport config found in card map");
        None
    } else if let Some(config) = transport_config {
        debug!("Drift paths found in card map, creating ScouterQueue");
        let rt = app_state().runtime.clone();
        let scouter_queue = ScouterQueue::from_path_rs(py, card_map.drift_paths, config, rt)?;
        let event_loops = scouter_queue.queue_event_loops.clone();

        Some(Arc::new(QueueState {
            queue: Arc::new(RwLock::new(Py::new(py, scouter_queue)?)),
            queue_event_loops: event_loops,
            transport_config: Arc::new(RwLock::new(config.clone().unbind())),
        }))
    } else {
        debug!("No transport config provided");
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
    event_loops: ReloadEventLoops,
) -> Result<ServiceReloader, AppError> {
    let reload_config = reload_config.unwrap_or_else(|| ReloadConfig::default());
    let service_info = Arc::new(RwLock::new(service_info));
    let reloader = ServiceReloader::new(service_info, reload_config, service_path, event_loops);
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
/// The service and queue are put behind Arc RWLocks to ensure thread safety when updating using the reloader
#[pyclass]
#[derive(Debug)]
pub struct AppState {
    pub service: Arc<RwLock<Py<ServiceCard>>>,
    pub queue: Option<Arc<QueueState>>,
    pub reloader: ServiceReloader,
    pub load_kwargs: Option<Arc<RwLock<Py<PyDict>>>>,
    pub reload_loops: ReloadEventLoops,
}

#[pymethods]
impl AppState {
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

        let reload_event_loops = ReloadEventLoops::new();
        let queue = create_scouter_queue(py, card_map, transport_config)?;

        // Create the service reloader
        let reloader = create_service_reloader(
            service_info,
            reload_config,
            service_path,
            reload_event_loops.clone(),
        )?;

        let kwargs = load_kwargs.map(|kw| kw.clone().unbind());

        Ok(AppState {
            service: Arc::new(RwLock::new(service)),
            queue,
            reloader,
            load_kwargs: kwargs.map(|kw| Arc::new(RwLock::new(kw))),
            reload_loops: ReloadEventLoops::new(),
        })
    }

    #[getter]
    pub fn service<'py>(&self, py: Python<'py>) -> Result<Bound<'py, ServiceCard>, AppError> {
        Ok(self
            .service
            .read()
            .map_err(|e| {
                error!("Failed to read service: {:?}", e);
                AppError::PoisonError(e.to_string())
            })?
            .bind(py)
            .clone())
    }

    #[getter]
    pub fn queue<'py>(&self, py: Python<'py>) -> Result<Bound<'py, ScouterQueue>, AppError> {
        Ok(self
            .queue
            .as_ref()
            .ok_or(AppError::QueueNotFoundError)?
            .queue
            .read()
            .map_err(|e| {
                error!("Failed to read queue: {:?}", e);
                AppError::PoisonError(e.to_string())
            })?
            .bind(py)
            .clone())
    }

    #[getter]
    pub fn reloader_running(&self) -> bool {
        // return initialized if reloader is present
        self.reload_loops.running()
    }

    pub fn reload(&self) -> Result<(), AppError> {
        self.reload_loops.trigger_download_event()
    }

    /// Start the reloader functionality
    pub fn start_reloader(&mut self) -> Result<(), AppError> {
        debug!("Starting reloader");
        if self.reloader_running() {
            return Ok(());
        }

        let (download_tx, download_rx) = mpsc::unbounded_channel();
        let (reload_tx, mut reload_rx) = mpsc::unbounded_channel();

        self.reload_loops.reload_tx = Some(reload_tx);
        self.reload_loops.download_tx = Some(download_tx);
        let mut loops = self.reload_loops.clone();

        // This will continually poll based on the config schedule and download
        // any new service to the reload_path
        self.start_download_task(&mut loops, download_rx)?;

        // Setup state for the background thread
        let reload_state = ReloaderState {
            reload_path: self.reloader.config.write_path.clone(),
            service_path: self.reloader.service_path.clone(),
            load_kwargs: self.load_kwargs.clone(),
            service: self.service.clone(),
            queue: self.queue.clone(),
            max_retries: self.reloader.config.max_retries,
        };

        debug!("Starting reload loop with arguments running");

        let handle = app_state().runtime.spawn(async move {
            loop {
                tokio::select! {
                    Some(event) = reload_rx.recv() => {
                        match event {
                            ReloadEvent::Start => {
                                info!("Reloader started");
                                match loops.set_reload_loop_running(true) {
                                    Ok(()) => info!("Reload loop is now running"),
                                    Err(e) => error!("Failed to set reload loop running: {:?}", e),
                                }
                            },

                            ReloadEvent::Ready => {
                                info!("Received reload event");
                                // Set reload ready to true
                                let mut retry_count = 0;

                                retry_count += 1;
                                while retry_count < reload_state.max_retries {
                                    match Self::reload_service(&reload_state) {
                                        Ok(()) => {
                                            info!("Service reloaded successfully");

                                            // if successful, move object from reload directory to base directory for service
                                            if let Err(e) = Self::cleanup(
                                                &reload_state.reload_path,
                                                &reload_state.service_path,
                                            ) {
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
                            }
                        }
                    }
                    else => {
                        debug!("Reload channel closed, exiting reload loop");
                        break;
                    }
                }

                tokio::time::sleep(std::time::Duration::from_millis(500)).await;
            }

            debug!("Reload loop terminated");
        });

        self.reload_loops.add_reload_handle(handle);

        Ok(())
    }

    pub fn stop_reloader(&mut self) -> Result<(), AppError> {
        if !self.reloader_running() {
            return Ok(());
        }

        // shutdown background reloader
        self.reloader.shutdown()?;

        Ok(())
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        let service = self.service.read().unwrap();
        visit.call(&*service)?;

        match self.queue {
            Some(ref queue_state) => {
                let queue_guard = queue_state.queue.read().unwrap();
                visit.call(&*queue_guard)?
            }
            None => return Ok(()),
        };

        if let Some(queue) = &self.queue {
            let config_guard = queue.transport_config.read().unwrap();
            visit.call(&*config_guard)?;
        }

        Ok(())
    }

    fn __clear__(&mut self) {
        self.queue = None; // Clear the queue
    }
}

impl AppState {
    fn shutdown_event_loops(&mut self) -> Result<(), AppError> {
        if let Some(ref queue_state) = self.queue {
            return queue_state.shutdown();
        }

        Ok(())
    }

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

    fn reload_queue(
        queue_state: &Arc<QueueState>,
        reload_path: &PathBuf,
    ) -> Result<Option<Py<ScouterQueue>>, AppError> {
        let card_map = load_card_map(reload_path)?;

        // First shutdown the existing queue properly
        //Python::with_gil(|py| -> Result<(), AppError> {
        //    match queue_arc.write() {
        //        Ok(mut queue_guard) => {
        //            if let Some(queue) = queue_guard.as_ref() {
        //                // Shutdown the existing queue
        //                info!("Shutting down existing ScouterQueue");
        //                if let Err(e) = queue.bind(py).call_method0("shutdown") {
        //                    error!("Failed to shutdown queue: {:?}", e);
        //                } else {
        //                    info!("Successfully shutdown existing queue");
        //                }
        //            } else {
        //                debug!("No existing ScouterQueue to shutdown");
        //            }
        //
        //            // Set queue to None using the existing guard
        //            *queue_guard = None;
        //            debug!("Queue set to None after shutdown");
        //        }
        //        Err(e) => {
        //            error!("Failed to acquire write lock for queue shutdown: {:?}", e);
        //            return Err(AppError::UpdateServiceError(format!(
        //                "Failed to acquire queue lock: {}",
        //                e
        //            )));
        //        }
        //    }
        //    Ok(())
        //})?;

        // Create new queue
        //debug!("Creating new ScouterQueue");
        //let _new_queue = Python::with_gil(|py| -> Result<Option<Py<ScouterQueue>>, AppError> {
        //    let transport_config = transport_config
        //        .as_ref()
        //        .map(|tc| tc.read().unwrap().bind(py).clone());
        //
        //    create_scouter_queue(py, card_map, transport_config.as_ref())
        //})?;

        Ok(None)
    }

    fn reload_service_card(
        reload_path: &PathBuf,
        load_kwargs: &Option<Arc<RwLock<Py<PyDict>>>>,
    ) -> Result<Py<ServiceCard>, AppError> {
        // Acquire the GIL and load the new service
        let reload_result = Python::with_gil(|py| -> Result<Py<ServiceCard>, AppError> {
            // Read load_kwargs first, in a separate scope to minimize lock duration
            let kwargs = load_kwargs
                .as_ref()
                .map(|kw| kw.read().unwrap().bind(py).clone());
            // Load the new service card
            let new_service = ServiceCard::from_path_rs(py, reload_path, kwargs.as_ref())?;

            Ok(Py::new(py, new_service)?)
        })?;

        Ok(reload_result)
    }

    /// Top method for reloading a service. This will attempt to reload the actual service card and
    /// it's artifacts as well as reload the ScouterQueue, if it exists.
    /// # Arguments
    /// * `service_arc` - The service card to reload
    /// * `queue_arc` - The optional queue to reload
    /// * `write_path` - The path to the write directory
    /// * `load_kwargs` - The keyword arguments for loading the service artifacts
    /// * `transport_config` - The optional transport configuration
    fn reload_service(reload_state: &ReloaderState) -> Result<(), AppError> {
        // Reload the service card
        let _reloaded_service =
            Self::reload_service_card(&reload_state.reload_path, &reload_state.load_kwargs)?;

        // Reload the queue if it exists

        if let Some(queue) = &reload_state.queue {
            let _reloaded_queue = Self::reload_queue(&queue, &reload_state.reload_path)?;
        }

        //if let Some(new_queue) = queue {
        //    match queue_arc.write() {
        //        Ok(mut queue_guard) => {
        //            *queue_guard = new_queue;
        //            info!("Queue updated successfully");
        //        }
        //        Err(e) => {
        //            error!("Failed to acquire write lock for queue update: {:?}", e);
        //            return Err(AppError::UpdateServiceError(e.to_string()));
        //        }
        //    }
        //}
        Ok(())
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
    /// # Arguments
    /// * `reload_loops` - The reload event loops to use
    /// * `download_rx` - The receiver for download events
    pub fn start_download_task(
        &self,
        reload_loops: &mut ReloadEventLoops,
        download_rx: UnboundedReceiver<DownloadEvent>,
    ) -> Result<(), AppError> {
        self.reloader.start_download_task(
            app_state().runtime.clone(),
            self.reloader.config.clone(),
            download_rx,
            self.reloader.service_info.clone(),
            self.reloader.config.write_path.clone(),
            reload_loops,
        )?;

        Ok(())
    }
}
