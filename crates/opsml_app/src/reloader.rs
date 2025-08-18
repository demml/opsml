use crate::error::AppError;
use crate::utils::get_next_cron_timestamp;
use chrono::DateTime;
use chrono::Utc;
use opsml_cards::card_service::ServiceInfo;
use opsml_cards::ServiceCard;
use opsml_registry::base::OpsmlRegistry;
use opsml_registry::download::download_service_from_registry;
use opsml_types::contracts::CardQueryArgs;
use opsml_types::SaveName;
use opsml_types::{contracts::CardRecord, RegistryType};
use pyo3::prelude::*;
use pyo3::types::PyDict;

use std::path::Path;
use std::sync::Arc;
use std::sync::RwLock;
use std::sync::RwLockReadGuard;
use tokio::runtime::Runtime;
use tokio::sync::mpsc;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};
use tokio::sync::oneshot;
use tokio::time::{sleep, Duration};
use tracing::{debug, error, info, instrument};

/// Helper for listing cards
pub fn list_cards(args: &CardQueryArgs) -> Result<Vec<CardRecord>, AppError> {
    // get registry
    let registry = OpsmlRegistry::new(args.registry_type.clone())?;
    let cards = registry.list_cards(args)?;
    Ok(cards)
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

fn load_from_path(
    service: &Bound<'_, ServiceCard>,
    path: &Path,
    load_kwargs: Option<&Bound<'_, PyDict>>,
) -> Result<(), AppError> {
    //let service_card = ServiceCard::from_path_rs(py, &path, load_kwargs)?;
    //let card_map = load_card_map(&path).map_err(|e| {
    //    error!("Failed to load card map from: {:?}", e);
    //    e
    //})?;

    let _ = service.call_method("mut_from_path", (path,), load_kwargs);

    //let queue = if !card_map.drift_paths.is_empty() {
    //    debug!("Drift paths found in card map, creating ScouterQueue");
    //    match transport_config {
    //        Some(config) => {
    //            let rt = runtime.clone();
    //            let scouter_queue =
    //                ScouterQueue::from_path_rs(py, card_map.drift_paths, config, rt)?;
    //            Some(Py::new(py, scouter_queue)?)
    //        }
    //        None => {
    //            debug!("No transport config found in card map");
    //            None
    //        }
    //    }
    //} else {
    //    debug!("No drift paths or transport config found in card map");
    //    None
    //};

    Ok(())
}

#[derive(Debug, Clone)]
pub enum ReloadEvent {
    Initialize,
    ForceReload,
}

#[pyclass]
#[derive(Clone, Debug)]
pub struct ReloadConfig {
    #[pyo3(get, set)]
    pub cron: String,
}

#[pymethods]
impl ReloadConfig {
    #[new]
    pub fn new(cron: String) -> Self {
        ReloadConfig { cron }
    }
}

fn reload_task(
    py: Python<'_>,
    service: Py<ServiceCard>,
    service_info: RwLockReadGuard<ServiceInfo>,
) -> Result<Option<String>, AppError> {
    // list latest service card. If different version:
    // 1. Download new artifacts (including drift profile, to a new directory)
    // 2. Reload ServiceCard
    let bound_service = service.bind(py);

    let mut query_args = CardQueryArgs {
        space: Some(service_info.space.clone()),
        name: Some(service_info.name.clone()),
        version: None,
        registry_type: RegistryType::Service,
        sort_by_timestamp: Some(true),
        limit: Some(1),
        ..Default::default()
    };

    let latest_card = list_cards(&query_args)?
        .into_iter()
        .next()
        .ok_or(AppError::CardNotFound)?;

    if !is_latest(&service_info.version, latest_card.version()) {
        // If the latest card is not the same as the current version, we need to reload
        info!(
            "Detected new version, reloading service {}:{}:{}",
            service_info.space,
            service_info.name,
            latest_card.version()
        );
        let latest_version = latest_card.version().to_string();
        query_args.version = Some(latest_version.clone());

        let write_path = std::env::current_dir()?
            .as_path()
            .join(SaveName::ServiceReload);

        download_service_from_registry(&query_args, &write_path)?;

        load_from_path(bound_service, &write_path, None)?;

        return Ok(Some(latest_version));
    }

    Ok(None)
}

#[allow(clippy::too_many_arguments)]
async fn start_background_reload_process(
    service: Py<ServiceCard>,
    mut event_rx: mpsc::UnboundedReceiver<ReloadEvent>,
    mut shutdown_rx: oneshot::Receiver<()>,
    runtime: Arc<Runtime>,
    scheduled_reload: Arc<RwLock<DateTime<Utc>>>,
    config: ReloadConfig,
    initialized: Arc<RwLock<bool>>,
    service_info: Arc<RwLock<ServiceInfo>>,
) -> Result<(), AppError> {
    let cron = config.cron;

    let future = async move {
        loop {
            tokio::select! {
                _ = sleep(Duration::from_secs(2)) => {


                    if is_past_scheduled_reload(&scheduled_reload.read().unwrap()) {

                        Python::with_gil(|py| {
                            let service_info_read = service_info.read().unwrap();
                            if let Ok(Some(latest_version)) = reload_task(py, service.clone_ref(py), service_info_read) {
                                let mut service_info_write = service_info.write().unwrap();
                                service_info_write.version = latest_version;
                            }
                        });

                        let mut reload_timestamp = scheduled_reload.write().unwrap();
                        *reload_timestamp = get_next_cron_timestamp(&cron)?;
                    }
                },
                event = event_rx.recv() => {
                    match event {
                        Some(ReloadEvent::Initialize) => {
                            info!("Reloader initialized and ready");
                            match initialized.write() {
                            Ok(mut init) => {
                                *init = true;
                                debug!("Reloader initialized successfully");
                            }
                            Err(e) => {
                                    error!("Failed to write to initialized lock for reloader: {}", e);
                                }
                            }
                        },
                        Some(ReloadEvent::ForceReload) => {
                            info!("Force reload requested");
                            println!("Force reload requested");
                            Python::with_gil(|py| {
                                let service_info_read = service_info.read().unwrap();
                                if let Ok(Some(latest_version)) = reload_task(py, service.clone_ref(py), service_info_read) {
                                    let mut service_info_write = service_info.write().unwrap();
                                    service_info_write.version = latest_version;
                                }
                            });

                            let mut reload_timestamp = scheduled_reload.write().unwrap();
                            *reload_timestamp = get_next_cron_timestamp(&cron)?;
                            },
                        None => {
                                debug!("Event channel closed");
                                break;
                        }
                    }
                },
                _ = &mut shutdown_rx => {
                    info!("Stopping background task");
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
    tx: UnboundedSender<ReloadEvent>,
    shutdown_tx: Option<oneshot::Sender<()>>,
    pub initialized: Arc<RwLock<bool>>,
    pub service_info: Arc<RwLock<ServiceInfo>>,
}

impl ServiceReloader {
    #[instrument(skip_all)]
    pub fn new(
        service_info: Arc<RwLock<ServiceInfo>>,
    ) -> (Self, UnboundedReceiver<ReloadEvent>, oneshot::Receiver<()>) {
        debug!("Creating unbounded QueueBus");
        let (tx, rx) = mpsc::unbounded_channel();
        let (shutdown_tx, shutdown_rx) = oneshot::channel();
        let initialized = Arc::new(RwLock::new(false));

        (
            Self {
                tx,
                shutdown_tx: Some(shutdown_tx),
                initialized,
                service_info,
            },
            rx,
            shutdown_rx,
        )
    }

    pub fn start_reloader(
        shared_runtime: Arc<tokio::runtime::Runtime>,
        service: Py<ServiceCard>,
        config: ReloadConfig,
        event_rx: mpsc::UnboundedReceiver<ReloadEvent>,
        shutdown_rx: oneshot::Receiver<()>,
        initialized: Arc<RwLock<bool>>,
        service_info: Arc<RwLock<ServiceInfo>>,
    ) -> Result<(), AppError> {
        let reloader_runtime = shared_runtime.clone();
        let scheduled_reload = Arc::new(RwLock::new(get_next_cron_timestamp(&config.cron)?));

        shared_runtime.spawn(async move {
            match start_background_reload_process(
                service,
                event_rx,
                shutdown_rx,
                reloader_runtime,
                scheduled_reload,
                config.clone(),
                initialized,
                service_info,
            )
            .await
            {
                Ok(_) => debug!("Service Reloader started successfully"),
                Err(e) => error!("Service Reloader exited with error: {}", e),
            }
        });

        Ok(())
    }

    #[instrument(skip_all)]
    pub fn publish(&self, event: ReloadEvent) -> Result<(), AppError> {
        Ok(self.tx.send(event)?)
    }

    pub fn is_initialized(&self) -> bool {
        // Check if the bus is initialized
        if let Ok(initialized) = self.initialized.read() {
            *initialized
        } else {
            false
        }
    }

    #[instrument(skip_all)]
    pub fn shutdown(&mut self) {
        // Signal shutdown
        if let Some(shutdown_tx) = self.shutdown_tx.take() {
            let _ = shutdown_tx.send(());
        }
    }

    pub fn init(&self) -> Result<(), AppError> {
        std::thread::sleep(std::time::Duration::from_millis(20));
        let mut attempts = 0;
        while !self.is_initialized() {
            debug!("Reloader is not initialized, waiting...");
            if attempts >= 100 {
                return Err(AppError::FailedToInitializeReloader);
            }
            attempts += 1;
            std::thread::sleep(std::time::Duration::from_millis(10));

            let event = ReloadEvent::Initialize;
            debug!("Initializing Reloader");
            self.publish(event)?;
        }
        Ok(())
    }

    pub fn reload(&self) -> Result<(), AppError> {
        if !self.is_initialized() {
            return Err(AppError::ReloaderNotFound);
        }

        debug!("Reloading service via reloader");
        self.publish(ReloadEvent::ForceReload)?;
        Ok(())
    }
    // create function that spawns a task and reloads the service card
}
