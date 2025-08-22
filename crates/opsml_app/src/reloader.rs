use crate::error::AppError;
use crate::types::{DownloadEvent, ReloadEvent, ReloadEventLoops};
use crate::utils::get_next_cron_timestamp;
use chrono::DateTime;
use chrono::Utc;
use opsml_cards::card_service::ServiceInfo;
use opsml_registry::async_base::AsyncOpsmlRegistry;
use opsml_registry::download::async_download_service_from_registry;
use opsml_types::contracts::sort_cards_by_version;
use opsml_types::contracts::CardQueryArgs;
use opsml_types::{RegistryType, SaveName};
use pyo3::prelude::*;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::RwLock;
use std::time::Duration;
use tokio::runtime::Runtime;
use tokio::sync::mpsc;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};
use tokio::task::JoinHandle;
use tracing::{debug, error, info, info_span, instrument, Instrument};

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

        return Ok(true);
    }

    Ok(false)
}

#[allow(clippy::too_many_arguments)]
fn start_background_download_loop(
    mut download_rx: UnboundedReceiver<DownloadEvent>,
    runtime: Arc<Runtime>,
    scheduled_reload: Arc<RwLock<DateTime<Utc>>>,
    config: ReloadConfig,
    service_info: Arc<RwLock<ServiceInfo>>,
    write_path: Arc<PathBuf>,
    reload_loops: ReloadEventLoops,
) -> Result<JoinHandle<()>, AppError> {
    let cron = config.cron;

    let future = async move {
        loop {
            tokio::select! {

                event = download_rx.recv() => {
                    match event {

                        Some(DownloadEvent::Start) => {
                            info!("Reloader started");
                            reload_loops.set_download_loop_running(true)?;
                        },
                        Some(DownloadEvent::Force) => {
                            info!("Force reload requested");

                            let service_info_cloned = {
                                let guard = service_info.read().unwrap();
                                guard.clone()
                            };

                            match reload_task(service_info_cloned, &write_path).await {
                                Ok(true) => {
                                    // Send ReloadEvent to inform AppState to Reload
                                    if let Some(reload_tx) = &reload_loops.reload_tx {
                                        match reload_tx.send(ReloadEvent::Ready) {
                                            Ok(_) => debug!("Sent reload event"),
                                            Err(e) => error!("Failed to send reload event: {}", e),
                                        }
                                    }
                                }
                                Ok(false) => {
                                    info!("No new version detected, skipping reload");
                                }
                                Err(e) => {
                                    error!("Error during reload task: {}", e);
                                }
                            }

                            let mut reload_timestamp = scheduled_reload.write().unwrap();
                            *reload_timestamp = get_next_cron_timestamp(&cron)?;
                        },
                        Some(DownloadEvent::Stop) => {
                            info!("Stopping Reloader");
                            reload_loops.set_download_loop_running(false)?;
                            break;

                        },
                        None => {
                                debug!("Event channel closed");
                                reload_loops.set_download_loop_running(false)?;
                                break;
                        }
                    }
                },
                else => {
                    debug!("Event channel closed");
                    reload_loops.set_download_loop_running(false)?;
                    break;
                }
            }
        }
        Ok(()) as Result<(), AppError>
    };

    let span = info_span!("background_task");
    let handle = runtime.spawn(async move {
        if let Err(e) = future.instrument(span).await {
            error!("Failed to run background task: {}", e);
        }
    });

    Ok(handle)
}

#[derive(Debug)]
pub struct ServiceReloader {
    tx: Option<UnboundedSender<DownloadEvent>>,
    pub service_info: Arc<RwLock<ServiceInfo>>,
    pub config: ReloadConfig,
    pub service_path: Arc<PathBuf>,
    pub event_loops: ReloadEventLoops,
}

impl ServiceReloader {
    #[instrument(skip_all)]
    pub fn new(
        service_info: Arc<RwLock<ServiceInfo>>,
        config: ReloadConfig,
        service_path: PathBuf,
        event_loops: ReloadEventLoops,
    ) -> Self {
        debug!("Creating unbounded QueueBus");
        let service_path = Arc::new(service_path);

        Self {
            tx: None,
            service_info,
            config,
            service_path,
            event_loops,
        }
    }

    /// Starts the background download task by creating a background download loop to continually check for and download
    /// new ServiceCards. This logic also adds the download task handle to the app state event loops and confirms
    /// that the download loop is running.
    /// # Arguments
    /// * `shared_runtime` - The shared Tokio runtime
    /// * `config` - The reload configuration
    /// * `download_rx` - The download event receiver
    /// * `write_path` - The path to write the downloaded ServiceCard
    /// * `reload_loops` - The reload event loops
    pub fn start_download_task(
        &self,
        shared_runtime: Arc<tokio::runtime::Runtime>,
        config: ReloadConfig,
        download_rx: mpsc::UnboundedReceiver<DownloadEvent>,
        service_info: Arc<RwLock<ServiceInfo>>,
        write_path: Arc<PathBuf>,
        reload_loops: &mut ReloadEventLoops,
    ) -> Result<(), AppError> {
        let scheduled_reload = Arc::new(RwLock::new(get_next_cron_timestamp(&config.cron)?));

        let handle = start_background_download_loop(
            download_rx,
            shared_runtime,
            scheduled_reload,
            config,
            service_info,
            write_path,
            reload_loops.clone(),
        )?;

        reload_loops.add_download_handle(handle);

        self.start()?;

        self.confirm_start()?;

        Ok(())
    }

    #[instrument(skip_all)]
    pub fn publish(&self, event: DownloadEvent) -> Result<(), AppError> {
        if let Some(tx) = &self.tx {
            Ok(tx.send(event)?)
        } else {
            Err(AppError::ReloaderNotRunning)
        }
    }

    #[instrument(skip_all)]
    pub fn shutdown(&self) -> Result<(), AppError> {
        debug!("Stopping service reloader");
        self.publish(DownloadEvent::Stop)?;
        Ok(())
    }

    #[instrument(skip_all)]
    pub fn start(&self) -> Result<(), AppError> {
        debug!("Starting service reloader");
        self.publish(DownloadEvent::Start)?;
        Ok(())
    }

    #[instrument(skip_all)]
    pub fn confirm_start(&self) -> Result<(), AppError> {
        // Signal confirm start
        let mut max_retries = 20;
        while max_retries > 0 {
            if self.event_loops.download_loop_running() {
                debug!("Download loop started successfully");
                return Ok(());
            }
            max_retries -= 1;
            std::thread::sleep(Duration::from_millis(100));
        }
        error!("Download loop failed to start");
        Err(AppError::DownloadLoopFailedToStartError)
    }

    // create function that spawns a task and reloads the service card
}
