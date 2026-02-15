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

/// Helper for listing cards
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

/// Checks if the current version is the latest version
pub fn is_latest(current_version: &str, latest_version: &str) -> bool {
    current_version == latest_version
}

/// Checks if the scheduled reload time has passed
pub fn is_past_scheduled_reload(scheduled_reload: &DateTime<Utc>) -> bool {
    let now = Utc::now();
    *scheduled_reload <= now
}

#[pyclass]
#[derive(Clone, Debug)]
pub struct ReloadConfig {
    #[pyo3(get, set)]
    pub cron: String,

    #[pyo3(get, set)]
    pub max_retries: u32,

    pub write_path: Arc<PathBuf>,
}

#[pymethods]
impl ReloadConfig {
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
    pub fn write_path(&self) -> PathBuf {
        self.write_path.as_ref().clone()
    }

    #[setter]
    pub fn set_write_path(&mut self, path: PathBuf) {
        self.write_path = Arc::new(path);
    }
}

impl Default for ReloadConfig {
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

/// Attempts to download the latest service artifacts
/// # Arguments
/// * `service_info` - The service information
/// * `write_path` - The path to write the downloaded artifacts
/// * `state` - The current state of the reload task
/// * `scheduled_reload` - The scheduled reload time
/// * `cron` - The cron expression for the reload schedule
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

/// Starts the background download task by creating a background download loop to continually check for and download
/// new ServiceCards. This logic also adds the download task handle to the app state event loops and confirms
/// that the download loop is running.
/// # Arguments
/// * `download_rx` - The download event receiver
/// * `runtime` - The shared Tokio runtime
/// * `config` - The reload configuration
/// * `write_path` - The path to write the downloaded ServiceCard
/// * `state` - The current state of the reload task
/// * `cancellation_token` - The cancellation token for the task
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

#[derive(Debug)]
pub struct ServiceReloader {
    pub service_info: Arc<RwLock<ServiceInfo>>,
    pub config: ReloadConfig,
    pub service_path: Arc<PathBuf>,
    pub state: ReloadTaskState,
}

impl ServiceReloader {
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
