use crate::types::{DownloadEvent, QueueState, ReloadEvent, ReloadTaskState, ReloaderState};
use crate::utils::{wait_for_download_task, wait_for_reload_task};
use crate::{
    error::AppError,
    reloader::{ReloadConfig, ServiceReloader, start_background_download_task},
};
use opsml_cards::{ServiceCard, card_service::ServiceInfo};
use opsml_cli::actions::lock::{install_service_from_spec, install_service_locally};
use opsml_state::app_state;
use opsml_storage::{StorageError, copy_objects};
use opsml_toml::LockFile;
use opsml_types::{SaveName, Suffix, cards::ServiceCardMapping};
use pyo3::PyTraverseError;
use pyo3::PyVisit;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use scouter_client::BatchConfig;
use scouter_client::SCOUTER_ENTITY;
use scouter_client::ScouterQueue;
use scouter_client::is_pydantic_basemodel;
use std::path::{Path, PathBuf};
use std::sync::{Arc, RwLock};
use std::time::Duration;
use tokio::sync::mpsc::{self, UnboundedReceiver};
use tokio::time::sleep;
use tokio_util::sync::CancellationToken;
use tracing::{Instrument, debug, error, info, info_span};

/// Loads the service card mapping saved beside a service artifact directory.
///
/// The mapping is expected at `<path>/card_map.json` and contains drift profile
/// paths used to construct Scouter queues. Returns an [`AppError`] when the
/// mapping file is missing or cannot be deserialized.
///
/// # Arguments
/// * `path` - Service artifact directory that contains the card mapping file.
///
/// # Returns
/// The deserialized [`ServiceCardMapping`] for the service directory.
///
/// # Errors
/// Returns [`AppError`] when the mapping file cannot be read or parsed.
fn load_card_map(path: &Path) -> Result<ServiceCardMapping, AppError> {
    let card_mapping_path = path.join(SaveName::CardMap).with_extension(Suffix::Json);
    debug!("Loading card mapping from: {:?}", card_mapping_path);
    let mapping = ServiceCardMapping::from_path(&card_mapping_path)?;
    Ok(mapping)
}

/// Creates the optional Scouter queue for a loaded service.
///
/// A queue is only created when the service card mapping contains drift paths
/// and the caller provides a Python transport config. The transport config is
/// stored as an owned `Py<PyAny>` so the queue state can outlive the borrowed
/// PyO3 argument passed during construction.
///
/// # Arguments
/// * `py` - The Python interpreter instance
/// * `card_map` - Service card mapping containing drift profile paths
/// * `transport_config` - Optional Scouter transport config from Python
/// * `wait_for_startup` - Whether queue startup should block until ready
///
/// # Returns
/// `Some(QueueState)` when monitoring can be enabled, or `None` when there are
/// no drift paths or no transport config.
///
/// # Errors
/// Returns [`AppError`] when Scouter queue creation fails or PyO3 cannot create
/// the Python-owned queue object.
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

        let scouter_queue =
            ScouterQueue::from_path_rs(py, card_map.drift_paths, config, wait_for_startup)?;
        let event_state = scouter_queue.queue_state.clone();
        let shutdown_fn: Arc<dyn Fn() -> Result<(), AppError> + Send + Sync> =
            Arc::new(move || {
                for (alias, task_state) in event_state.iter() {
                    debug!("Shutting down queue: {}", alias);
                    task_state.shutdown_tasks()?;
                }
                Ok(())
            });

        Some(QueueState {
            queue: Some(Py::new(py, scouter_queue)?),
            shutdown_fn,
            transport_config: config.clone().unbind(),
        })
    } else {
        debug!("No transport config provided");
        None
    };

    Ok(queue)
}

/// Resolves a service instance identifier for OpenTelemetry resource metadata.
///
/// The `HOSTNAME` environment variable takes precedence. When it is not set,
/// the system hostname is used if it can be read and converted to UTF-8.
///
/// # Returns
/// `Some(String)` containing a non-empty hostname, or `None` when no valid
/// hostname can be resolved.
fn resolve_instance_id() -> Option<String> {
    if let Ok(hostname) = std::env::var("HOSTNAME")
        && !hostname.is_empty()
    {
        return Some(hostname);
    }

    hostname::get()
        .ok()
        .and_then(|hostname| hostname.into_string().ok())
        .filter(|hostname| !hostname.is_empty())
}

/// Creates a [`ServiceReloader`] for a loaded service.
///
/// The reloader owns the service path, resolved reload config, shared service
/// identity, and task state used by the background download and reload loops.
/// When no reload config is provided, the default daily reload schedule is used.
///
/// # Arguments
/// * `service_info` - Space/name/version metadata for the active service
/// * `reload_config` - Optional reload configuration
/// * `service_path` - Directory containing the currently loaded service
/// * `reload_state` - Shared task/event state used by the reloader
///
/// # Returns
/// A configured [`ServiceReloader`].
///
/// # Errors
/// This helper currently does not produce an error, but it returns
/// `Result<ServiceReloader, AppError>` to match app-state construction call
/// sites.
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
#[pyclass(skip_from_py_object)]
#[derive(Debug)]
pub struct AppState {
    /// Loaded service card shared with request handlers and reload tasks.
    pub service: Arc<RwLock<Py<ServiceCard>>>,

    /// An optional ScouterQueue for real-time model monitoring
    pub queue: Option<Arc<RwLock<QueueState>>>,

    /// Service reloader configuration and service identity.
    pub reloader: ServiceReloader,

    /// Optional keyword arguments reused when reloading service artifacts.
    pub load_kwargs: Option<Arc<RwLock<Py<PyDict>>>>,

    /// State for managing download and reload tasks.
    pub reload_state: ReloadTaskState,

    /// Information about the service used for instrumentation metadata.
    service_info: ServiceInfo,
}

#[pymethods]
impl AppState {
    /// Loads an `AppState` from a service artifact directory.
    ///
    /// This is the primary Python-facing constructor for API frameworks that
    /// need a shared OpsML service, optional Scouter queue, and optional reload
    /// loop state. When `path` is omitted, `opsml_service` is used. In offline
    /// mode, a failed explicit path load falls back to `from_spec(...,
    /// register=false)` using the path's parent directory.
    ///
    /// # Arguments
    /// * `py` - Python interpreter state
    /// * `path` - Service artifact directory. Defaults to `opsml_service`.
    /// * `transport_config` - Optional Scouter transport config. Omit to skip queue creation.
    /// * `reload_config` - Optional reload schedule and write-path config.
    /// * `load_kwargs` - Optional keyword arguments passed to service card loading.
    ///
    /// # Returns
    /// A fully loaded [`AppState`] or an [`AppError`] from service, mapping,
    /// queue, or reloader construction.
    ///
    /// # Errors
    /// Returns [`AppError`] when the service cannot be loaded, the card mapping
    /// cannot be read, the Scouter queue cannot be created, or offline fallback
    /// via [`AppState::from_spec`] fails.
    #[staticmethod]
    #[pyo3(signature = (path=None, transport_config=None, reload_config=None, load_kwargs=None))]
    pub fn from_path(
        py: Python,
        path: Option<PathBuf>,
        transport_config: Option<&Bound<'_, PyAny>>,
        reload_config: Option<ReloadConfig>,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Self, AppError> {
        match path {
            Some(service_path) => match Self::from_path_inner(
                py,
                service_path.clone(),
                transport_config,
                reload_config.clone(),
                load_kwargs,
            ) {
                Ok(app_state) => Ok(app_state),
                Err(err) if app_state().is_offline() => {
                    let spec_dir = service_path
                        .parent()
                        .unwrap_or_else(|| Path::new("."))
                        .to_path_buf();
                    debug!(
                        "OPSML_OFFLINE=1 and provided service path failed to load: {}. Falling back to from_spec at {:?} without registration",
                        err, spec_dir
                    );
                    Self::from_spec(
                        py,
                        Some(spec_dir),
                        transport_config,
                        reload_config,
                        load_kwargs,
                        Some(false),
                    )
                }
                Err(err) => Err(err),
            },
            None if app_state().is_offline() => Self::from_spec(
                py,
                None,
                transport_config,
                reload_config,
                load_kwargs,
                Some(false),
            ),
            None => Self::from_path_inner(
                py,
                PathBuf::from(SaveName::ServiceCard),
                transport_config,
                reload_config,
                load_kwargs,
            ),
        }
    }

    /// Loads an `AppState` from an `opsmlspec.yaml` file.
    ///
    /// Finds `opsmlspec.yaml` in `path` (or the current directory if `None`), installs the
    /// service, then delegates to [`AppState::from_path`].
    ///
    /// When `register` is `true` (default), cards are registered normally.
    /// When `register` is `false`, the service is installed locally — no `ServiceCard`
    /// registration, no encryption keys, no uploads. `Path` variant sub-cards are loaded
    /// directly from disk; `Card` variant sub-cards are still downloaded from the registry.
    ///
    /// # Arguments
    /// * `py` - Python interpreter state used to load the installed service.
    /// * `path` - Directory containing `opsmlspec.yaml`. Defaults to current directory.
    /// * `transport_config` - Transport config for the `ScouterQueue`. Pass `None` to skip.
    /// * `reload_config` - Reload config for `ServiceReloader`. Pass `None` to skip.
    /// * `load_kwargs` - Per-card load kwargs (same format as `from_path`).
    /// * `register` - Whether to register the `ServiceCard`. Defaults to `true`.
    ///
    /// # Returns
    /// * `AppState` — the fully loaded application state.
    ///
    /// # Errors
    /// Returns [`AppError`] when the spec directory cannot be resolved, service
    /// installation fails, `opsml.lock` cannot be read, the lock file contains
    /// no artifacts, or loading the installed service fails.
    #[staticmethod]
    #[pyo3(signature = (path=None, transport_config=None, reload_config=None, load_kwargs=None, register=None))]
    pub fn from_spec(
        py: Python,
        path: Option<PathBuf>,
        transport_config: Option<&Bound<'_, PyAny>>,
        reload_config: Option<ReloadConfig>,
        load_kwargs: Option<&Bound<'_, PyDict>>,
        register: Option<bool>,
    ) -> Result<Self, AppError> {
        // if path is file, get parent directory, if not use path, if None use current directory
        let spec_dir = match path {
            Some(p) if p.is_file() => p.parent().unwrap_or_else(|| Path::new(".")).to_path_buf(),
            Some(p) => p,
            None => std::env::current_dir()?,
        };

        let register_service = register.unwrap_or(true) && !app_state().is_offline();

        if register_service {
            install_service_from_spec(spec_dir.clone(), Some(spec_dir.clone()))
                .map_err(|e| AppError::Error(e.to_string()))?;
        } else {
            if app_state().is_offline() {
                debug!("OPSML_OFFLINE=1, installing service locally without registration");
            }
            install_service_locally(spec_dir.clone(), Some(spec_dir.clone()))
                .map_err(|e| AppError::Error(e.to_string()))?;
        }

        let lock_file = LockFile::read(&spec_dir).map_err(|e| AppError::Error(e.to_string()))?;

        let write_dir = lock_file
            .artifact
            .first()
            .map(|a| a.write_dir.clone())
            .ok_or_else(|| AppError::Error("Lock file contains no artifacts".to_string()))?;

        Self::from_path_inner(
            py,
            spec_dir.join(write_dir),
            transport_config,
            reload_config,
            load_kwargs,
        )
    }

    #[getter]
    /// Returns the currently loaded service card to Python.
    ///
    /// The service is read from the shared lock and rebound to the active Python
    /// interpreter. A poisoned lock is converted to [`AppError::PoisonError`].
    ///
    /// # Arguments
    /// * `py` - Active Python interpreter token used to bind the service card.
    ///
    /// # Returns
    /// A Python-bound [`ServiceCard`] reference.
    ///
    /// # Errors
    /// Returns [`AppError::PoisonError`] when the service lock is poisoned.
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
    /// Returns the active Scouter queue to Python.
    ///
    /// If the app state was created without a queue, this returns
    /// [`AppError::QueueNotFoundError`]. A poisoned queue lock is converted to
    /// [`AppError::PoisonError`].
    ///
    /// # Arguments
    /// * `py` - Active Python interpreter token used to bind the Scouter queue.
    ///
    /// # Returns
    /// A Python-bound [`ScouterQueue`] reference.
    ///
    /// # Errors
    /// Returns [`AppError::QueueNotFoundError`] when no queue exists, or
    /// [`AppError::PoisonError`] when the queue lock is poisoned.
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
    /// Reports whether either background reloader task is currently running.
    ///
    /// # Returns
    /// `true` when the download task or reload task is marked running.
    pub fn reloader_running(&self) -> bool {
        // return initialized if reloader is present
        self.reload_state.running()
    }

    /// Requests an immediate reload check from Python.
    ///
    /// This sends a force-download event to the background download task. If the
    /// task has not been started yet, the call is a no-op and returns `Ok(())`.
    ///
    /// # Returns
    /// `Ok(())` after the force-download event is sent or skipped.
    ///
    /// # Errors
    /// Returns [`AppError`] when sending the force-download event fails because
    /// the download channel is closed.
    pub fn reload(&self) -> Result<(), AppError> {
        self.reload_state.trigger_download_event()
    }

    /// Starts the background download and reload loops.
    ///
    /// The download task polls according to [`ReloadConfig::cron`] and can also
    /// be triggered by [`AppState::reload`]. The reload task receives ready
    /// events after a new service version is downloaded, then reloads the
    /// service card and Scouter queue in place. Calling this while already
    /// running is idempotent.
    ///
    /// # Returns
    /// `Ok(())` once both background tasks have started or when they were
    /// already running.
    ///
    /// # Errors
    /// Returns [`AppError`] when task channels cannot be stored, the download
    /// task cannot be started, task startup cannot be observed, or reload task
    /// state cannot be updated.
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
                                let mut retry_count: u32 = 0;

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
                                            sleep(Duration::from_millis(
                                                100 * 2_u64.pow(retry_count.min(10)),
                                            ))
                                            .await;
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

    /// Visits Python-owned references for PyO3 garbage collection.
    ///
    /// This lets Python's cyclic GC see the service card, queue object, and
    /// transport config held inside Rust-managed state.
    ///
    /// # Arguments
    /// * `visit` - PyO3 visitor used to register Python-owned references.
    ///
    /// # Returns
    /// `Ok(())` after all reachable Python objects have been visited.
    ///
    /// # Errors
    /// Returns [`PyTraverseError`] when PyO3 fails to visit a referenced Python
    /// object.
    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Ok(service) = self.service.read() {
            visit.call(&*service)?;
        }
        if let Some(queue_state) = &self.queue
            && let Ok(guard) = queue_state.read()
        {
            visit.call(&guard.queue)?;
            visit.call(&guard.transport_config)?;
        }
        Ok(())
    }

    /// Clears Python-owned queue state during PyO3 garbage collection.
    ///
    /// The service card remains owned by the app state; only the optional queue
    /// reference is dropped here.
    fn __clear__(&mut self) {
        self.queue = None; // Clear the queue
    }

    /// Stops background reload tasks and removes the reload write directory.
    ///
    /// Missing reload directories are ignored so shutdown remains safe after a
    /// partial startup or prior cleanup.
    ///
    /// # Returns
    /// `Ok(())` after task shutdown has been requested and cleanup has run.
    ///
    /// # Errors
    /// Returns [`AppError`] when reload task shutdown fails. Filesystem cleanup
    /// errors other than `NotFound` are logged and treated as soft failures.
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

    /// Shuts down queue and reload resources owned by this app state.
    ///
    /// Queue shutdown errors are logged and treated as soft failures when the
    /// underlying Scouter channel is already closed. Reload task shutdown errors
    /// are propagated.
    ///
    /// # Returns
    /// `Ok(())` after queue shutdown and reloader shutdown complete.
    ///
    /// # Errors
    /// Returns [`AppError::ScouterQueueLockError`] when the queue lock cannot be
    /// acquired, or any [`AppError`] propagated by [`AppState::stop_reloader`].
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

    /// Convenience wrapper for OpenTelemetry instrumentation with Scouter.
    ///
    /// This is equivalent to calling `ScouterInstrumentor().instrument()` in
    /// Python, but it reuses the queue and service metadata already stored in
    /// `AppState`. When `transport_config` is omitted, the existing queue's
    /// transport config is reused; if there is no queue, an error is returned.
    /// The service UID and service identity fields are added to the instrumentor
    /// kwargs before the Python instrumentor is invoked.
    ///
    /// # Arguments
    /// * `py` - Active Python interpreter token used to call the Python instrumentor.
    /// * `transport_config` - Optional transport config; defaults to the existing queue config.
    /// * `exporter` - Optional exporter passed through to the Python instrumentor.
    /// * `batch_config` - Optional Scouter batch config.
    /// * `sample_ratio` - Optional trace sampling ratio.
    /// * `attributes` - Optional mapping or Pydantic model merged with the service UID.
    /// * `eval_profiles` - Optional evaluation profiles passed through to Scouter.
    /// * `propagate_baggage` - Optional baggage propagation flag.
    /// * `kwargs` - Additional keyword arguments to pass to the ScouterInstrumentor.instrument() method
    ///
    /// # Returns
    /// `Ok(())` after the Python instrumentor has been called.
    ///
    /// # Errors
    /// Returns [`AppError`] when Python imports or method calls fail,
    /// `attributes` is not a mapping/Pydantic model, no transport config is
    /// available, or service metadata cannot be read.
    ///
    /// # Panics
    /// Panics if the service or queue locks are poisoned while reading metadata
    /// or the existing queue transport config.
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (
        transport_config=None,
        exporter=None,
        batch_config=None,
        sample_ratio=None,
        attributes=None,
        eval_profiles=None,
        propagate_baggage=None,
        **kwargs))]
    pub fn instrument(
        &self,
        py: Python,
        transport_config: Option<&Bound<'_, PyAny>>,
        exporter: Option<&Bound<'_, PyAny>>,
        batch_config: Option<Py<BatchConfig>>,
        sample_ratio: Option<f64>,
        attributes: Option<Bound<'_, PyAny>>,
        eval_profiles: Option<Bound<'_, PyAny>>,
        propagate_baggage: Option<bool>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<(), AppError> {
        let instrumentor = py
            .import("opsml")?
            .getattr("scouter")?
            .getattr("tracing")?
            .getattr("ScouterInstrumentor")?
            .call0()?;

        let scouter_queue = match &self.queue {
            Some(queue) => {
                debug!("Using existing queue for instrumentation");
                Some(queue.read().unwrap().get_queue(py))
            }
            None => None,
        };

        // if transport_config is not provided, attempt to get from existing queue
        // This allows users to call instrument without having to provide another transport config
        // if they have already provided one during AppState initialization
        let transport_config = match transport_config {
            Some(config) => config.clone(),
            None => match &self.queue {
                Some(queue) => {
                    let config = queue.read().unwrap().transport_config.bind(py).clone();
                    debug!("Using transport config from existing queue: {:?}", config);
                    config
                }
                None => return Err(AppError::TransportConfigNotFound),
            },
        };

        // add service uid to attributes
        let uid = self
            .service
            .read()
            .unwrap()
            .getattr(py, "uid")?
            .extract::<String>(py)?;

        let attributes = add_uid_to_attributes(py, SCOUTER_ENTITY, &uid, attributes)?;
        let instrument_kwargs = match kwargs {
            Some(kw) => kw.clone(),
            None => PyDict::new(py),
        };

        // add kwargs
        instrument_kwargs.set_item("transport_config", transport_config)?;
        instrument_kwargs.set_item("exporter", exporter)?;
        instrument_kwargs.set_item("batch_config", batch_config)?;
        instrument_kwargs.set_item("sample_ratio", sample_ratio)?;
        instrument_kwargs.set_item("scouter_queue", scouter_queue)?;
        instrument_kwargs.set_item("attributes", attributes.clone())?;
        instrument_kwargs.set_item("eval_profiles", eval_profiles)?;
        instrument_kwargs.set_item("propagate_baggage", propagate_baggage)?;
        instrument_kwargs.set_item("service_name", self.service_info.name.clone())?;
        instrument_kwargs.set_item("service_namespace", self.service_info.space.clone())?;
        instrument_kwargs.set_item("service_version", self.service_info.version.clone())?;
        if let Some(instance_id) = resolve_instance_id() {
            instrument_kwargs.set_item("service_instance_id", instance_id)?;
        }

        // debug log all kwargs being passed to instrumentor
        debug!("Instrumenting with kwargs: {:?}", instrument_kwargs);

        // call instrumentor with provided arguments and kwargs
        let _instrumented = instrumentor.call_method("instrument", (), Some(&instrument_kwargs))?;
        Ok(())
    }
}

/// Adds a service identifier to an OpenTelemetry attribute mapping.
///
/// `attributes` may be `None`, a Python `dict`, or a Pydantic BaseModel. The
/// returned dictionary is owned by the active Python interpreter and includes
/// `key = value`. Any other attribute type returns
/// [`AppError::AttributesMustBeMapping`].
///
/// # Arguments
/// * `py` - Active Python interpreter token used to create or inspect mappings.
/// * `key` - Attribute key to insert.
/// * `value` - Attribute value to insert.
/// * `attributes` - Optional Python dict or Pydantic BaseModel to merge into.
///
/// # Returns
/// A Python dictionary containing the original attributes plus `key = value`.
///
/// # Errors
/// Returns [`AppError::AttributesMustBeMapping`] when `attributes` is neither a
/// dict nor a Pydantic BaseModel, or [`AppError`] when Python conversion or
/// mutation fails.
fn add_uid_to_attributes<'py>(
    py: Python<'py>,
    key: &str,
    value: &str,
    attributes: Option<Bound<'py, PyAny>>,
) -> Result<Bound<'py, PyDict>, AppError> {
    let attributes = match attributes {
        Some(attrs) => {
            if is_pydantic_basemodel(py, &attrs)? {
                let dumped = attrs.call_method0("model_dump")?;
                dumped.cast::<PyDict>()?.clone()
            } else if attrs.is_instance_of::<PyDict>() {
                attrs.cast::<PyDict>()?.clone()
            } else {
                return Err(AppError::AttributesMustBeMapping);
            }
        }
        None => PyDict::new(py),
    };
    attributes.set_item(key, value)?;

    Ok(attributes.clone())
}

/// Internal builder for `AppState` construction.
///
/// The builder owns only Rust values (`PathBuf` and `ReloadConfig`). Borrowed
/// PyO3 values are accepted by `build` and helper methods so their lifetimes
/// stay scoped to the Python call that initiated construction.
struct AppStateBuilder {
    service_path: PathBuf,
    reload_config: Option<ReloadConfig>,
}

impl AppStateBuilder {
    /// Creates a builder for a resolved service artifact directory.
    ///
    /// # Arguments
    /// * `service_path` - Directory containing the service artifacts to load.
    /// * `reload_config` - Optional reload configuration for the resulting app state.
    ///
    /// # Returns
    /// A builder that owns Rust-only construction inputs.
    fn new(service_path: PathBuf, reload_config: Option<ReloadConfig>) -> Self {
        Self {
            service_path,
            reload_config,
        }
    }

    /// Builds the full app state from the configured service path.
    ///
    /// The construction order is service card, service metadata, card mapping,
    /// reload task state, optional Scouter queue, service reloader, and stored
    /// load kwargs. Errors from any step are returned without fallback logic;
    /// public entrypoints handle fallback behavior before calling this builder.
    /// Borrowed PyO3 arguments are accepted here instead of being stored so
    /// Python lifetimes stay local to this construction call.
    ///
    /// # Arguments
    /// * `py` - Active Python interpreter token used during service and queue construction.
    /// * `transport_config` - Optional borrowed Scouter transport config.
    /// * `load_kwargs` - Optional borrowed Python kwargs for service loading.
    ///
    /// # Returns
    /// A fully constructed [`AppState`].
    ///
    /// # Errors
    /// Returns [`AppError`] from service loading, service metadata extraction,
    /// card mapping load, queue creation, or reloader creation.
    fn build(
        self,
        py: Python<'_>,
        transport_config: Option<&Bound<'_, PyAny>>,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<AppState, AppError> {
        let service = self.load_service(py, load_kwargs)?;
        let service_info = Self::extract_service_info(py, &service)?;
        let card_map = self.load_card_mapping()?;
        let reload_state = Self::create_reload_state();
        let queue = Self::create_queue(py, card_map, transport_config)?;
        let reloader = self.create_reloader(service_info.clone(), reload_state.clone())?;
        let load_kwargs = Self::store_load_kwargs(load_kwargs);

        Ok(AppState {
            service: Arc::new(RwLock::new(service)),
            queue,
            reloader,
            load_kwargs,
            reload_state,
            service_info,
        })
    }

    /// Loads the service card from disk and converts it into a Python-owned object.
    ///
    /// `load_kwargs` remains borrowed only for this call and is passed directly
    /// to `ServiceCard::from_path_rs`.
    ///
    /// # Arguments
    /// * `py` - Active Python interpreter token used to create `Py<ServiceCard>`.
    /// * `load_kwargs` - Optional borrowed Python kwargs for service loading.
    ///
    /// # Returns
    /// A Python-owned [`ServiceCard`].
    ///
    /// # Errors
    /// Returns [`AppError`] when the service cannot be loaded from disk or PyO3
    /// cannot allocate the Python-owned service object.
    fn load_service(
        &self,
        py: Python<'_>,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Py<ServiceCard>, AppError> {
        Ok(Py::new(
            py,
            ServiceCard::from_path_rs(py, &self.service_path, load_kwargs)?,
        )?)
    }

    /// Extracts service metadata used by reload and instrumentation code.
    ///
    /// The metadata is read through the Python-bound `service_info` method so it
    /// matches the service object exposed to Python.
    ///
    /// # Arguments
    /// * `py` - Active Python interpreter token used to bind `service`.
    /// * `service` - Python-owned service card to inspect.
    ///
    /// # Returns
    /// [`ServiceInfo`] containing the service space, name, and version.
    ///
    /// # Errors
    /// Returns [`AppError`] when the Python method call or extraction fails.
    fn extract_service_info(
        py: Python<'_>,
        service: &Py<ServiceCard>,
    ) -> Result<ServiceInfo, AppError> {
        Ok(service
            .bind(py)
            .call_method0("service_info")?
            .extract::<ServiceInfo>()?)
    }

    /// Loads the service card mapping for queue construction.
    ///
    /// Errors are logged with the mapping path context and propagated to the
    /// caller.
    ///
    /// # Returns
    /// The deserialized [`ServiceCardMapping`] for this builder's service path.
    ///
    /// # Errors
    /// Returns [`AppError`] when the card mapping cannot be read or parsed.
    fn load_card_mapping(&self) -> Result<ServiceCardMapping, AppError> {
        load_card_map(&self.service_path).inspect_err(|e| {
            error!("Failed to load card map from: {:?}", e);
        })
    }

    /// Creates a fresh reload task state for a new app state instance.
    ///
    /// # Returns
    /// A new [`ReloadTaskState`] with no running tasks or registered channels.
    fn create_reload_state() -> ReloadTaskState {
        ReloadTaskState::new()
    }

    /// Creates and wraps the optional Scouter queue for shared app-state use.
    ///
    /// Initial construction waits for queue startup so `AppState.from_path` and
    /// `AppState.from_spec` only return after the queue is ready or skipped.
    /// Borrowed PyO3 config is used only during queue construction and is then
    /// converted into owned queue state by [`create_scouter_queue`].
    ///
    /// # Arguments
    /// * `py` - Active Python interpreter token used to create the Scouter queue.
    /// * `card_map` - Service card mapping containing drift profile paths.
    /// * `transport_config` - Optional borrowed Scouter transport config.
    ///
    /// # Returns
    /// A shared optional [`QueueState`] suitable for storing on [`AppState`].
    ///
    /// # Errors
    /// Returns [`AppError`] when Scouter queue creation fails.
    fn create_queue(
        py: Python<'_>,
        card_map: ServiceCardMapping,
        transport_config: Option<&Bound<'_, PyAny>>,
    ) -> Result<Option<Arc<RwLock<QueueState>>>, AppError> {
        Ok(create_scouter_queue(py, card_map, transport_config, true)?
            .map(|queue| Arc::new(RwLock::new(queue))))
    }

    /// Creates the service reloader using the builder-owned path and config.
    ///
    /// # Arguments
    /// * `service_info` - Metadata for the loaded service.
    /// * `reload_state` - Shared lifecycle state for reload tasks.
    ///
    /// # Returns
    /// A configured [`ServiceReloader`].
    ///
    /// # Errors
    /// Returns [`AppError`] from [`create_service_reloader`].
    fn create_reloader(
        self,
        service_info: ServiceInfo,
        reload_state: ReloadTaskState,
    ) -> Result<ServiceReloader, AppError> {
        create_service_reloader(
            service_info,
            self.reload_config,
            self.service_path,
            reload_state,
        )
    }

    /// Stores Python load kwargs for future reloads.
    ///
    /// The borrowed kwargs dict is converted into an owned `Py<PyDict>` before
    /// it is placed behind an `Arc<RwLock<_>>`.
    ///
    /// # Arguments
    /// * `load_kwargs` - Optional borrowed Python kwargs from initial service loading.
    ///
    /// # Returns
    /// Owned kwargs wrapped for sharing with future reload calls, or `None`.
    fn store_load_kwargs(
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Option<Arc<RwLock<Py<PyDict>>>> {
        load_kwargs.map(|kwargs| Arc::new(RwLock::new(kwargs.clone().unbind())))
    }
}

impl AppState {
    /// Loads app state from a concrete service path using the internal builder.
    ///
    /// This helper assumes path/spec fallback has already been resolved by the
    /// public constructor and performs one construction attempt.
    ///
    /// # Arguments
    /// * `py` - Active Python interpreter token used during construction.
    /// * `service_path` - Concrete service artifact directory to load.
    /// * `transport_config` - Optional borrowed Scouter transport config.
    /// * `reload_config` - Optional reload configuration.
    /// * `load_kwargs` - Optional borrowed Python kwargs for service loading.
    ///
    /// # Returns
    /// A fully constructed [`AppState`].
    ///
    /// # Errors
    /// Returns [`AppError`] from service loading, mapping load, queue creation,
    /// or reloader construction.
    fn from_path_inner(
        py: Python,
        service_path: PathBuf,
        transport_config: Option<&Bound<'_, PyAny>>,
        reload_config: Option<ReloadConfig>,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Self, AppError> {
        AppStateBuilder::new(service_path, reload_config).build(py, transport_config, load_kwargs)
    }

    /// Reloads the Scouter queue from a freshly downloaded service directory.
    ///
    /// The existing queue is shut down first, then its transport config is
    /// rebound under the GIL and reused to construct the replacement queue. If
    /// the new card map has no drift paths, the queue object is cleared.
    ///
    /// # Arguments
    /// * `queue_state` - Shared queue state to shut down and replace.
    /// * `reload_path` - Directory containing the downloaded service artifacts.
    ///
    /// # Returns
    /// `Ok(())` after the queue state has been replaced or cleared.
    ///
    /// # Errors
    /// Returns [`AppError`] when the card map cannot be loaded, queue shutdown
    /// fails, or the replacement queue cannot be created.
    ///
    /// # Panics
    /// Panics if the queue lock is poisoned.
    fn reload_queue(
        queue_state: &Arc<RwLock<QueueState>>,
        reload_path: &Path,
    ) -> Result<(), AppError> {
        let card_map = load_card_map(reload_path)?;

        let mut queue_guard = queue_state.as_ref().write().unwrap();
        queue_guard.shutdown()?;

        debug!("Reloading queue with new card map");
        let new_queue_state = Python::attach(|py| -> Result<Option<QueueState>, AppError> {
            // Get transport config from existing queue state
            let transport_config = queue_guard.transport_config.bind(py);
            create_scouter_queue(py, card_map, Some(transport_config), false)
        })?;

        // set queue to None to drop
        if let Some(new_state) = new_queue_state {
            queue_guard.queue = new_state.queue;
            queue_guard.shutdown_fn = new_state.shutdown_fn;
        } else {
            queue_guard.queue = None;
        }
        debug!("New queue state created");

        Ok(())
    }

    /// Reloads a service card from disk for the background reload loop.
    ///
    /// The GIL is acquired only while reading Python load kwargs and creating
    /// the replacement `Py<ServiceCard>`, keeping Python interaction scoped to
    /// the minimum reload boundary.
    ///
    /// # Arguments
    /// * `reload_path` - Directory containing the downloaded service artifacts.
    /// * `load_kwargs` - Optional shared Python kwargs from initial service loading.
    ///
    /// # Returns
    /// A replacement Python-owned [`ServiceCard`].
    ///
    /// # Errors
    /// Returns [`AppError`] when the service cannot be loaded or PyO3 object
    /// allocation fails.
    ///
    /// # Panics
    /// Panics if the `load_kwargs` lock is poisoned.
    fn reload_service_card(
        reload_path: &Path,
        load_kwargs: &Option<Arc<RwLock<Py<PyDict>>>>,
    ) -> Result<Py<ServiceCard>, AppError> {
        // Acquire the GIL and load the new service
        let reload_result = Python::attach(|py| -> Result<Py<ServiceCard>, AppError> {
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

    /// Reloads service and queue state after a new service artifact is downloaded.
    ///
    /// The service card is replaced first. If an existing queue is present, the
    /// queue is then rebuilt from the downloaded card map.
    ///
    /// # Arguments
    /// * `reload_state` - Shared state needed to update service, queue, and reload paths.
    ///
    /// # Returns
    /// `Ok(())` after service state and optional queue state have been updated.
    ///
    /// # Errors
    /// Returns [`AppError`] when service card reload fails, service state cannot
    /// be updated, or queue reload fails.
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

    /// Copies downloaded artifacts into the active service directory and removes the reload directory.
    ///
    /// Storage copy errors and filesystem cleanup errors are propagated so the
    /// reload loop can retry according to the configured retry policy.
    ///
    /// # Arguments
    /// * `reload_path` - Directory containing newly downloaded artifacts.
    /// * `service_path` - Active service artifact directory to replace.
    ///
    /// # Returns
    /// `Ok(())` after artifacts are copied and the reload directory is removed.
    ///
    /// # Errors
    /// Returns [`AppError`] when storage copy fails or filesystem cleanup fails.
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

    /// Starts the background task that checks for newer service versions.
    ///
    /// The task is attached to the shared OpsML runtime, records its abort
    /// handle and cancellation token in `ReloadTaskState`, and emits reload
    /// events after successful downloads.
    ///
    /// # Arguments
    /// * `state` - Mutable reload task state used to record task handles.
    /// * `download_rx` - The receiver for download events
    ///
    /// # Returns
    /// `Ok(())` after the background download task is spawned and tracked.
    ///
    /// # Errors
    /// Returns [`AppError`] when the background task cannot be started or task
    /// state cannot be updated by the spawned task.
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
