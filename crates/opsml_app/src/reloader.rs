use crate::error::AppError;
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
use tokio::runtime::Runtime;
use tokio::sync::mpsc;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};
use tracing::{debug, error, info, instrument};

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

#[derive(Debug, Clone)]
pub enum ReloadEvent {
    Start,
    Stop,
    ForceReload,
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
async fn start_background_reload_process(
    mut event_rx: mpsc::UnboundedReceiver<ReloadEvent>,
    runtime: Arc<Runtime>,
    scheduled_reload: Arc<RwLock<DateTime<Utc>>>,
    config: ReloadConfig,
    service_info: Arc<RwLock<ServiceInfo>>,
    reload_ready: Arc<RwLock<bool>>,
    write_path: Arc<PathBuf>,
    running: Arc<RwLock<bool>>,
) -> Result<(), AppError> {
    let cron = config.cron;
    let future = async move {
        loop {
            tokio::select! {

                event = event_rx.recv() => {
                    match event {
                        Some(ReloadEvent::Stop) => {
                            info!("Stopping Reloader");
                            let mut running = running.write().unwrap();
                            *running = false;
                            break;

                        },
                        Some(ReloadEvent::Start) => {
                            info!("Reloader started");
                            let mut running = running.write().unwrap();
                            *running = true;
                        },
                        Some(ReloadEvent::ForceReload) => {
                            info!("Force reload requested");

                            let service_info_cloned = {
                                let guard = service_info.read().unwrap();
                                guard.clone()
                            };

                            match reload_task(service_info_cloned, &write_path).await {
                                Ok(true) => {
                                    // Set reload ready flag
                                    if let Err(e) = reload_ready.write().map(|mut ready| *ready = true) {
                                        error!("Failed to write to reload_ready lock: {}", e);
                                    } else {
                                        debug!("New version detected. Starting reload");
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

                        None => {
                                debug!("Event channel closed");
                                break;
                        }
                    }
                },
                else => {
                    debug!("Event channel closed");
                    break;
                }
            }
        }
        Ok(()) as Result<(), AppError>
    };

    runtime.spawn(async move {
        if let Err(e) = future.await {
            debug!("Background queue exited with error: {:?}", e);
        }
    });

    Ok(())
}

#[derive(Debug)]
pub struct ServiceReloader {
    tx: Option<UnboundedSender<ReloadEvent>>,
    pub service_info: Arc<RwLock<ServiceInfo>>,
    pub reload_ready: Arc<RwLock<bool>>,
    pub config: ReloadConfig,
    pub service_path: Arc<PathBuf>,
    pub running: Arc<RwLock<bool>>,
}

impl ServiceReloader {
    #[instrument(skip_all)]
    pub fn new(
        service_info: Arc<RwLock<ServiceInfo>>,
        config: ReloadConfig,
        service_path: PathBuf,
    ) -> Self {
        debug!("Creating unbounded QueueBus");
        let reload_ready = Arc::new(RwLock::new(false));
        let service_path = Arc::new(service_path);
        let running = Arc::new(RwLock::new(false));

        Self {
            tx: None,
            service_info,
            reload_ready,
            config,
            service_path,
            running,
        }
    }

    /// Creates event channels for the reloader. This will create
    /// an mpsc channel for sending events and a shutdown channel used for shutting down
    /// the reloader background task
    pub fn create_trx_channel(&mut self) -> Result<UnboundedReceiver<ReloadEvent>, AppError> {
        let (tx, rx) = mpsc::unbounded_channel();
        self.tx = Some(tx);
        Ok(rx)
    }

    pub fn start_reloader(
        shared_runtime: Arc<tokio::runtime::Runtime>,
        config: ReloadConfig,
        event_rx: mpsc::UnboundedReceiver<ReloadEvent>,
        service_info: Arc<RwLock<ServiceInfo>>,
        reload_ready: Arc<RwLock<bool>>,
        write_path: Arc<PathBuf>,
        running: Arc<RwLock<bool>>,
    ) -> Result<(), AppError> {
        let reloader_runtime = shared_runtime.clone();
        let scheduled_reload = Arc::new(RwLock::new(get_next_cron_timestamp(&config.cron)?));

        shared_runtime.spawn(async move {
            match start_background_reload_process(
                event_rx,
                reloader_runtime,
                scheduled_reload,
                config.clone(),
                service_info,
                reload_ready,
                write_path,
                running,
            )
            .await
            {
                Ok(_) => debug!("Service Reloader started successfully"),
                Err(e) => error!("Service Reloader exited with error: {}", e),
            }
        });

        Ok(())
    }

    pub fn start(&self) -> Result<(), AppError> {
        std::thread::sleep(std::time::Duration::from_millis(20));
        let mut attempts = 0;
        debug!("Initializing reloader");
        while !self.is_running() {
            if attempts >= 100 {
                error!("Failed to start reloader after 100 attempts");
                return Err(AppError::FailedToInitializeReloader);
            }
            attempts += 1;
            std::thread::sleep(std::time::Duration::from_millis(10));

            let event = ReloadEvent::Start;
            self.publish(event)?;
        }

        debug!("Reloader started successfully");
        Ok(())
    }

    #[instrument(skip_all)]
    pub fn publish(&self, event: ReloadEvent) -> Result<(), AppError> {
        if let Some(tx) = &self.tx {
            Ok(tx.send(event)?)
        } else {
            Err(AppError::ReloaderNotRunning)
        }
    }

    #[instrument(skip_all)]
    pub fn shutdown(&mut self) -> Result<(), AppError> {
        if !self.is_running() {
            return Err(AppError::ReloaderNotFound);
        }
        debug!("Stopping service reloader");
        self.publish(ReloadEvent::Stop)?;
        Ok(())
    }

    pub fn reload(&self) -> Result<(), AppError> {
        if !self.is_running() {
            return Err(AppError::ReloaderNotFound);
        }
        debug!("Reloading service via reloader");
        self.publish(ReloadEvent::ForceReload)?;
        Ok(())
    }

    pub fn is_running(&self) -> bool {
        // Check if the bus is running
        if let Ok(running) = self.running.read() {
            *running
        } else {
            false
        }
    }

    // create function that spawns a task and reloads the service card
}
