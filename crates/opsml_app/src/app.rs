use crate::types::{DownloadEvent, QueueState, ReloadEvent, ReloadTaskState, ReloaderState};
use crate::utils::{wait_for_download_task, wait_for_reload_task};
use crate::{
    error::AppError,
    reloader::{start_background_download_task, ReloadConfig, ServiceReloader},
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
use tokio_util::sync::CancellationToken;
use tracing::{debug, error, info, info_span, Instrument};

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
/// * `Some(Arc<QueueState>)` if the scouter queue was created successfully
/// * `None` if the scouter queue could not be created
pub fn create_scouter_queue(
    py: Python<'_>,
    card_map: ServiceCardMapping,
    transport_config: Option<&Bound<'_, PyAny>>,
    wait_for_startup: bool,
) -> Result<Option<QueueState>, AppError> {
    let queue = if card_map.drift_paths.is_empty() {
        debug!("No drift paths or transport config found in card map");
        None
    } else if let Some(config) = transport_config {
        debug!("Drift paths found in card map, creating ScouterQueue");
        let rt = app_state().runtime.clone();
        let scouter_queue =
            ScouterQueue::from_path_rs(py, card_map.drift_paths, config, rt, wait_for_startup)?;
        let event_state = scouter_queue.queue_state.clone();

        Some(QueueState {
            queue: Some(Py::new(py, scouter_queue)?),
            task_state: event_state,
            transport_config: config.clone().unbind(),
        })
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
    reload_state: ReloadTaskState,
) -> Result<ServiceReloader, AppError> {
    let reload_config = reload_config.unwrap_or_default();
    let service_info = Arc::new(RwLock::new(service_info));
    let reloader = ServiceReloader::new(service_info, reload_config, service_path, reload_state);
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

    /// An optional ScouterQueue for real-time model monitoring
    pub queue: Option<Arc<RwLock<QueueState>>>,

    pub reloader: ServiceReloader,

    pub load_kwargs: Option<Arc<RwLock<Py<PyDict>>>>,

    // State for managing reload tasks
    pub reload_state: ReloadTaskState,
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

        let reload_state = ReloadTaskState::new();
        let queue = create_scouter_queue(py, card_map, transport_config, true)?
            .map(|q| Arc::new(RwLock::new(q)));

        // Create the service reloader
        let reloader = create_service_reloader(
            service_info,
            reload_config,
            service_path,
            reload_state.clone(),
        )?;

        let kwargs = load_kwargs.map(|kw| kw.clone().unbind());

        Ok(AppState {
            service: Arc::new(RwLock::new(service)),
            queue,
            reloader,
            load_kwargs: kwargs.map(|kw| Arc::new(RwLock::new(kw))),
            reload_state,
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
            .read()
            .map_err(|e| {
                error!("Failed to read queue: {:?}", e);
                AppError::PoisonError(e.to_string())
            })?
            .get_queue(py))
    }

    #[getter]
    pub fn reloader_running(&self) -> bool {
        // return initialized if reloader is present
        self.reload_state.running()
    }

    pub fn reload(&self) -> Result<(), AppError> {
        self.reload_state.trigger_download_event()
    }

    /// Start the reloader functionality
    pub fn start_reloader(&mut self) -> Result<(), AppError> {
        debug!("Starting reloader");
        if self.reloader_running() {
            return Ok(());
        }

        let (download_tx, download_rx) = mpsc::unbounded_channel();
        let (reload_tx, mut reload_rx) = mpsc::unbounded_channel();

        self.reload_state.set_reload_tx(reload_tx)?;
        self.reload_state.set_download_tx(download_tx)?;

        // This will continually poll based on the config schedule and download any new service to the reload_path
        // This is separated out from model and queue reloading because we want to isolate
        // any GIL interaction as much as possible
        self.start_download_task(&mut self.reload_state.clone(), download_rx)?;

        debug!("Starting reload loop with arguments running");
        let cancellation_token = CancellationToken::new();
        self.reload_state
            .add_reload_cancellation_token(cancellation_token.clone());

        // Setup state for the background thread
        let reload_state = ReloaderState {
            reload_path: self.reloader.config.write_path.clone(),
            service_path: self.reloader.service_path.clone(),
            load_kwargs: self.load_kwargs.clone(),
            service: self.service.clone(),
            queue: self.queue.clone(),
            max_retries: self.reloader.config.max_retries,
            task_state: self.reload_state.clone(),
        };

        let handle = app_state().runtime.spawn(async move {

            match reload_state.task_state.set_reload_task_running(true) {
                Ok(()) => info!("Reload loop is now running"),
                Err(e) => error!("Failed to set reload loop running: {:?}", e),
            }

            loop {
                tokio::select! {
                    Some(event) = reload_rx.recv() => {
                        match event {
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
                    _ = cancellation_token.cancelled() => {
                        debug!("Reload cancellation requested, exiting reload loop");
                        match reload_state.task_state.set_reload_task_running(false) {
                            Ok(()) => info!("Reload loop is now stopped"),
                            Err(e) => error!("Failed to set reload loop stopped: {:?}", e),
                        }
                       break;
                    }
                    else => {
                        debug!("Reload channel closed, exiting reload loop");
                        match reload_state.task_state.set_reload_task_running(false) {
                            Ok(()) => info!("Reload loop is now stopped"),
                            Err(e) => error!("Failed to set reload loop stopped: {:?}", e),
                        }
                        break;
                    }
                }

                tokio::time::sleep(std::time::Duration::from_millis(500)).await;
            }

            debug!("Reload loop terminated");
        }.instrument(info_span!("reload_task")));

        self.reload_state.add_reload_abort_handle(handle);

        // Send start event
        wait_for_download_task(&self.reload_state)?;

        // Wait for start event to trigger loop is running
        wait_for_reload_task(&self.reload_state)?;

        std::thread::sleep(Duration::from_secs(1));

        Ok(())
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        let service = self.service.read().unwrap();
        visit.call(&*service)?;

        match self.queue {
            Some(ref queue_state) => {
                let queue_guard = &queue_state.read().unwrap().queue;
                visit.call(queue_guard)?
            }
            None => return Ok(()),
        };

        if let Some(queue) = &self.queue {
            let config_guard = &queue.read().unwrap().transport_config;
            visit.call(config_guard)?;
        }

        Ok(())
    }

    fn __clear__(&mut self) {
        self.queue = None; // Clear the queue
    }

    pub fn stop_reloader(&self) -> Result<(), AppError> {
        debug!("Triggered stop reloader");
        // shutdown tasks
        self.reload_state.shutdown_tasks()?;

        // cleanup any remaining resources (soft failure)
        // if No such file or directory, ignore the error
        match std::fs::remove_dir_all(&*self.reloader.config.write_path) {
            Ok(()) => info!("Successfully deleted service path contents"),
            Err(e) => {
                if e.kind() != std::io::ErrorKind::NotFound {
                    error!("Failed to delete service path contents: {:?}", e);
                }
            }
        }

        Ok(())
    }

    pub fn shutdown(&mut self) -> Result<(), AppError> {
        // shutdown ScouterQueues
        std::thread::sleep(Duration::from_secs(1));
        if let Some(queue) = &self.queue {
            match queue
                .write()
                .map_err(|e| AppError::ScouterQueueLockError(e.to_string()))?
                .shutdown()
            {
                Ok(()) => info!("Successfully shutdown ScouterQueue"),
                // match on channel closed (RuntimeError)
                Err(e) => match e {
                    AppError::ScouterQueueRuntimeError(msg) if msg.contains("channel closed") => {
                        info!("ScouterQueue already shutdown (channel closed)")
                    }
                    _ => {
                        error!("Failed to shutdown ScouterQueue: {:?}", e);
                    }
                },
            }
        }

        // shutdown reloader
        self.stop_reloader()?;

        Ok(())
    }
}

impl AppState {
    fn reload_queue(
        queue_state: &Arc<RwLock<QueueState>>,
        reload_path: &Path,
    ) -> Result<(), AppError> {
        let card_map = load_card_map(reload_path)?;

        let mut queue_guard = queue_state.as_ref().write().unwrap();
        queue_guard.shutdown()?;

        debug!("Reloading queue with new card map");
        let new_queue_state = Python::with_gil(|py| -> Result<Option<QueueState>, AppError> {
            // Get transport config from existing queue state
            let transport_config = queue_guard.transport_config.bind(py);
            create_scouter_queue(py, card_map, Some(transport_config), false)
        })?;

        // set queue to None to drop
        queue_guard.queue = new_queue_state.and_then(|q| q.queue);
        debug!("New queue state created");

        Ok(())
    }

    fn reload_service_card(
        reload_path: &Path,
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
        let reloaded_service =
            Self::reload_service_card(&reload_state.reload_path, &reload_state.load_kwargs)?;

        // attempt to write to service card
        reload_state.update_service(reloaded_service)?;

        if let Some(queue) = &reload_state.queue {
            Self::reload_queue(queue, &reload_state.reload_path)?;
        }

        Ok(())
    }

    fn cleanup(reload_path: &Path, service_path: &Path) -> Result<(), AppError> {
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
        state: &mut ReloadTaskState,
        download_rx: UnboundedReceiver<DownloadEvent>,
    ) -> Result<(), AppError> {
        debug!("Starting download task with state: {:?}", state);

        let cancellation_token = CancellationToken::new();
        state.add_download_cancellation_token(cancellation_token.clone());

        let handle = start_background_download_task(
            download_rx,
            app_state().runtime.clone(),
            self.reloader.config.clone(),
            self.reloader.service_info.clone(),
            self.reloader.config.write_path.clone(),
            state.clone(),
            cancellation_token,
        )?;

        state.add_download_abort_handle(handle);

        Ok(())
    }
}
