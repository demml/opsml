use crate::error::AppError;
use crate::types::{DownloadEvent, ReloadTaskState};
use crate::utils::get_next_cron_timestamp;
use chrono::DateTime;
use chrono::Utc;
use opsml_cards::card_service::ServiceInfo;
use opsml_registry::download::async_download_service_from_registry;
use opsml_registry::registries::async_registry::AsyncOpsmlRegistry;
use opsml_types::contracts::CardQueryArgs;
use opsml_types::contracts::sort_cards_by_version;
use opsml_types::{RegistryType, SaveName};
use pyo3::prelude::*;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::RwLock;
use tokio::runtime::Runtime;
use tokio::sync::mpsc::UnboundedReceiver;
use tokio::task::JoinHandle;
use tokio::time::{Duration, sleep};
use tokio_util::sync::CancellationToken;
use tracing::{Instrument, debug, error, info, info_span, instrument};

/// Lists matching service cards and returns the highest semantic version.
///
/// The registry response is sorted by version before the first card is read.
/// Returns [`AppError::CardNotFound`] when the query finds no matching service
/// cards.
///
/// # Arguments
/// * `args` - Query arguments used to list matching service cards.
/// * `registry` - Async registry client used to perform the query.
///
/// # Returns
/// The latest matching service card version as a string.
///
/// # Errors
/// Returns [`AppError`] when the registry query fails or no matching card is
/// found.
pub async fn get_latest_version(
    args: &CardQueryArgs,
    registry: &AsyncOpsmlRegistry,
) -> Result<String, AppError> {
    // get registry
    debug!("Listing cards with args: {:?}", args);

    let mut cards = registry.list_cards(args).await?;

    debug!("Cards found: {:?}", cards);

    sort_cards_by_version(&mut cards, true);

    let latest_version = cards
        .first()
        .ok_or(AppError::CardNotFound)?
        .version()
        .to_string();

    debug!("Most recent version found: {:?}", &latest_version);
    Ok(latest_version)
}

/// Returns whether the currently loaded service version matches the registry version.
///
/// # Arguments
/// * `current_version` - Version currently loaded in app state.
/// * `latest_version` - Latest version reported by the registry.
///
/// # Returns
/// `true` when both version strings are equal.
pub fn is_latest(current_version: &str, latest_version: &str) -> bool {
    current_version == latest_version
}

/// Returns whether a scheduled reload timestamp is due.
///
/// # Arguments
/// * `scheduled_reload` - UTC timestamp for the next scheduled reload check.
///
/// # Returns
/// `true` when `scheduled_reload` is less than or equal to the current UTC time.
pub fn is_past_scheduled_reload(scheduled_reload: &DateTime<Utc>) -> bool {
    let now = Utc::now();
    *scheduled_reload <= now
}

/// Python-facing configuration for service reload polling.
///
/// The cron expression controls when registry checks run, `max_retries`
/// controls retry attempts after a reload failure, and `write_path` is the
/// temporary directory where new service artifacts are downloaded before being
/// swapped into the active service path.
#[pyclass(from_py_object)]
#[derive(Clone, Debug)]
pub struct ReloadConfig {
    /// Cron expression used to schedule registry checks.
    #[pyo3(get, set)]
    pub cron: String,

    /// Maximum retry attempts for a failed service reload.
    #[pyo3(get, set)]
    pub max_retries: u32,

    /// Directory where newly downloaded service artifacts are staged.
    pub write_path: Arc<PathBuf>,
}

#[pymethods]
impl ReloadConfig {
    /// Creates a reload config from Python.
    ///
    /// `max_retries` defaults to `3`. `write_path` defaults to
    /// `<current_dir>/service_reload`, matching [`ReloadConfig::default`].
    ///
    /// # Arguments
    /// * `cron` - Cron expression used to schedule registry checks.
    /// * `max_retries` - Optional retry limit. Defaults to `3`.
    /// * `write_path` - Optional staging directory. Defaults to `<current_dir>/service_reload`.
    ///
    /// # Returns
    /// A [`ReloadConfig`] with defaults applied for omitted optional values.
    ///
    /// # Errors
    /// Returns [`AppError`] when the current directory cannot be resolved while
    /// deriving the default `write_path`.
    #[new]
    #[pyo3(signature = (cron, max_retries=None, write_path=None))]
    pub fn new(
        cron: String,
        max_retries: Option<u32>,
        write_path: Option<PathBuf>,
    ) -> Result<Self, AppError> {
        let resolved_write_path = match write_path {
            Some(path) => path,
            None => std::env::current_dir()?.join(SaveName::ServiceReload),
        };
        Ok(ReloadConfig {
            cron,
            max_retries: max_retries.unwrap_or(3),
            write_path: Arc::new(resolved_write_path),
        })
    }

    #[getter]
    /// Returns the staging directory used for downloaded service artifacts.
    ///
    /// # Returns
    /// A cloned [`PathBuf`] for the configured reload staging directory.
    pub fn write_path(&self) -> PathBuf {
        self.write_path.as_ref().clone()
    }

    #[setter]
    /// Updates the staging directory used for future downloaded artifacts.
    ///
    /// # Arguments
    /// * `path` - New reload staging directory.
    pub fn set_write_path(&mut self, path: PathBuf) {
        self.write_path = Arc::new(path);
    }
}

impl Default for ReloadConfig {
    /// Creates the default daily reload configuration.
    ///
    /// The default cron schedule runs once per day at midnight, retries failed
    /// reloads three times, and stages downloads under `service_reload` in the
    /// current directory.
    ///
    /// # Returns
    /// A default [`ReloadConfig`].
    fn default() -> Self {
        ReloadConfig {
            cron: "0 0 0 * * *".to_string(), // Default to daily at midnight
            max_retries: 3,
            write_path: Arc::new(
                std::env::current_dir()
                    .unwrap_or_else(|_| PathBuf::from("."))
                    .join(SaveName::ServiceReload),
            ),
        }
    }
}

/// Checks the registry for a newer service version and downloads it when found.
///
/// Returns `Ok(true)` after a newer version is downloaded into `write_path`,
/// `Ok(false)` when the loaded version is already current, and an error when
/// the registry query or download fails.
///
/// # Arguments
/// * `service_info` - Metadata for the currently loaded service.
/// * `write_path` - Directory where newer service artifacts should be downloaded.
///
/// # Returns
/// `Ok(true)` when a newer service version was downloaded, or `Ok(false)` when
/// no newer version exists.
///
/// # Errors
/// Returns [`AppError`] when registry creation, latest-version lookup, or
/// artifact download fails.
async fn reload_task(
    service_info: ServiceInfo,
    write_path: &Arc<PathBuf>,
) -> Result<bool, AppError> {
    // list latest service card. If different version:
    // 1. Download new artifacts (including drift profile, to a new directory)
    // 2. Reload ServiceCard

    let mut query_args = CardQueryArgs {
        space: Some(service_info.space.clone()),
        name: Some(service_info.name.clone()),
        version: None,
        registry_type: RegistryType::Service,
        sort_by_timestamp: Some(true),
        limit: Some(10),
        ..Default::default()
    };

    let registry = AsyncOpsmlRegistry::new().await?;
    let latest_version = get_latest_version(&query_args, &registry).await?;

    if !is_latest(&service_info.version, &latest_version) {
        // If the latest card is not the same as the current version, we need to reload
        info!(
            "Detected new version, reloading service {}:{}:{}",
            service_info.space, service_info.name, &latest_version
        );

        query_args.version = Some(latest_version);

        async_download_service_from_registry(&query_args, write_path, &registry).await?;
        debug!("Download complete");

        return Ok(true);
    }

    Ok(false)
}

/// Attempts one scheduled or forced download cycle.
///
/// This reads the current service identity, checks for a newer service version,
/// emits a reload event after a successful download, and advances the next
/// scheduled reload timestamp.
///
/// # Arguments
/// * `service_info` - The service information
/// * `write_path` - The path to write the downloaded artifacts
/// * `state` - The current state of the reload task
/// * `scheduled_reload` - The scheduled reload time
/// * `cron` - The cron expression for the reload schedule
///
/// # Returns
/// `Ok(())` after the download check completes and the next schedule is
/// computed.
///
/// # Errors
/// Returns [`AppError`] when the next cron timestamp cannot be computed.
/// Registry and download failures are logged and do not abort the background
/// loop.
///
/// # Panics
/// Panics if the `service_info` lock is poisoned.
async fn download(
    service_info: &Arc<RwLock<ServiceInfo>>,
    write_path: &Arc<PathBuf>,
    state: &ReloadTaskState,
    scheduled_reload: &mut DateTime<Utc>,
    cron: &str,
) -> Result<(), AppError> {
    let service_info_cloned = {
        let guard = service_info.read().unwrap();
        guard.clone()
    };

    match reload_task(service_info_cloned, write_path).await {
        Ok(true) => match state.trigger_reload_event() {
            Ok(_) => debug!("Sent reload event"),
            Err(e) => error!("Failed to send reload event: {}", e),
        },
        Ok(false) => {
            info!("No new version detected, skipping reload");
        }
        Err(e) => {
            error!("Error during reload task: {}", e);
        }
    }

    *scheduled_reload = get_next_cron_timestamp(cron)?;
    Ok(())
}

/// Starts the background loop that checks for and downloads new service artifacts.
///
/// The loop wakes on the cron schedule and on explicit [`DownloadEvent::Force`]
/// messages. Successful downloads trigger a reload event through
/// [`ReloadTaskState`]. The returned [`JoinHandle`] is tracked by app state so
/// shutdown can abort the task.
///
/// # Arguments
/// * `download_rx` - The download event receiver
/// * `runtime` - The shared Tokio runtime
/// * `config` - The reload configuration
/// * `service_info` - Shared metadata for the currently loaded service
/// * `write_path` - The path to write the downloaded ServiceCard
/// * `state` - The current state of the reload task
/// * `cancellation_token` - The cancellation token for the task
///
/// # Returns
/// A [`JoinHandle`] for the spawned background download loop.
///
/// # Errors
/// This function currently does not return an error before spawning the task,
/// but uses `Result` to match the app-state task startup API. Errors inside the
/// spawned loop are logged by that task.
#[allow(clippy::too_many_arguments)]
pub fn start_background_download_task(
    mut download_rx: UnboundedReceiver<DownloadEvent>,
    runtime: Arc<Runtime>,
    config: ReloadConfig,
    service_info: Arc<RwLock<ServiceInfo>>,
    write_path: Arc<PathBuf>,
    state: ReloadTaskState,
    cancellation_token: CancellationToken,
) -> Result<JoinHandle<()>, AppError> {
    let cron = config.cron;

    let future = async move {
        let mut scheduled_reload = get_next_cron_timestamp(&cron)?;
        state.set_download_task_running(true)?;

        loop {
            tokio::select! {

                // branch that checks every 60 seconds if it's time to reload
                _ = sleep(Duration::from_secs(60)) => {
                    // check if it's time to reload
                    debug!("Checking if it's time to reload. Scheduled reload at: {}", scheduled_reload);
                    if scheduled_reload <= Utc::now() {
                        info!("Triggering scheduled reload");

                        match download(&service_info, &write_path, &state, &mut scheduled_reload, &cron).await {
                            Ok(_) => {
                                info!("Scheduled reload completed");
                            }
                            Err(e) => {
                                error!("Error during scheduled reload: {}", e);
                            }
                        }
                    }
                }
                Some(event) = download_rx.recv() => {
                    match event {

                        DownloadEvent::Force => {
                            info!("Force reload requested");

                            match download(&service_info, &write_path, &state, &mut scheduled_reload, &cron).await {
                                Ok(_) => {
                                    info!("Force reload completed");
                                }
                                Err(e) => {
                                    error!("Error during force reload: {}", e);
                                }
                            }
                        },


                    }
                },
                _ = cancellation_token.cancelled() => {
                    debug!("Cancellation token triggered for download task");
                    state.set_download_task_running(false)?;
                    break;
                }
                else => {
                    debug!("Download channel closed");
                    state.set_download_task_running(false)?;
                    break;
                }
            }
        }
        Ok(()) as Result<(), AppError>
    };

    let span = info_span!("download_task");
    let handle = runtime.spawn(async move {
        if let Err(e) = future.instrument(span).await {
            error!("Failed to run download task: {}", e);
        }
    });

    Ok(handle)
}

/// Holds shared configuration and identity for service reload tasks.
///
/// `ServiceReloader` does not perform reload work directly. It packages the
/// service metadata, active service path, reload config, and task state used by
/// `AppState` when it starts background download and reload loops.
#[derive(Debug)]
pub struct ServiceReloader {
    /// Shared service identity used for registry lookup and instrumentation.
    pub service_info: Arc<RwLock<ServiceInfo>>,
    /// Reload schedule, retry count, and staging directory.
    pub config: ReloadConfig,
    /// Active service artifact directory.
    pub service_path: Arc<PathBuf>,
    /// Shared task state for download/reload lifecycle management.
    pub state: ReloadTaskState,
}

impl ServiceReloader {
    /// Creates a reloader state container for an active service.
    ///
    /// The service path is wrapped in `Arc` so it can be shared with background
    /// tasks without cloning filesystem path contents.
    ///
    /// # Arguments
    /// * `service_info` - Shared metadata for the active service.
    /// * `config` - Reload schedule, retry count, and staging directory.
    /// * `service_path` - Directory containing the active service artifacts.
    /// * `state` - Shared lifecycle state for reload tasks.
    ///
    /// # Returns
    /// A [`ServiceReloader`] containing shared reload configuration and state.
    #[instrument(skip_all)]
    pub fn new(
        service_info: Arc<RwLock<ServiceInfo>>,
        config: ReloadConfig,
        service_path: PathBuf,
        state: ReloadTaskState,
    ) -> Self {
        let service_path = Arc::new(service_path);

        Self {
            service_info,
            config,
            service_path,
            state,
        }
    }

    // create function that spawns a task and reloads the service card
}
