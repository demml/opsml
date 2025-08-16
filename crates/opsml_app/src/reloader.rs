use crate::error::AppError;
use chrono::DateTime;
use chrono::Utc;
use opsml_cards::service;
/// This module contains the logic for reloading a ServiceCard
use opsml_cards::ServiceCard;
use opsml_registry::base::OpsmlRegistry;
use opsml_registry::download::download_service_from_registry;
use opsml_types::contracts::CardQueryArgs;
use opsml_types::{contracts::CardRecord, RegistryType};
use pyo3::prelude::*;
use scouter_client::QueueBus;
use std::str::FromStr;
use std::sync::Arc;
use std::sync::RwLock;
use tokio::runtime::Runtime;
use tokio::sync::mpsc::UnboundedReceiver;
use tokio::sync::oneshot;
use tokio::sync::watch;
use tokio::time::{sleep, Duration};
use tracing::{debug, error, info, info_span, Instrument};

type ServiceArgs = (String, String, String);

/// Helper for listing cards
pub fn list_cards(args: &CardQueryArgs) -> Result<Vec<CardRecord>, AppError> {
    // get registry
    let registry = OpsmlRegistry::new(args.registry_type.clone())?;
    let cards = registry.list_cards(args)?;
    Ok(cards)
}

pub fn is_latest(current_version: &str, latest_version: &str) -> bool {
    // Compare versions, assuming they are in a format that can be compared lexicographically
    current_version == latest_version
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

fn reload_task(space: &str, name: &str, version: &str) -> Result<(), AppError> {
    // list latest service card. If different version:
    // 1. Download new artifacts (including drift profile, to a new directory)
    // 2. Reload ServiceCard

    let query_args = CardQueryArgs {
        space: Some(space.to_string()),
        name: Some(name.to_string()),
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

    if !is_latest(version, latest_card.version()) {
        // If the latest card is not the same as the current version, we need to reload
        debug!("Reloading service card {}:{}:{}", space, name, version);
        reload_task(space, name, version)?;
    }

    let write_path = std::env::current_dir()?.as_path().to_path_buf();

    Ok(())
}

async fn start_background_reload_process(
    args: ServiceArgs,
    service: Py<ServiceCard>,
    mut shutdown_rx: oneshot::Receiver<()>,
    runtime: Arc<Runtime>,
    last_check: Arc<RwLock<DateTime<Utc>>>,
    config: ReloadConfig,
    completion_tx: oneshot::Sender<()>,
) -> Result<(), AppError> {
    let cron = config.cron;
    let args = args.clone();
    let future = async move {
        loop {
            tokio::select! {
                _ = sleep(Duration::from_secs(2)) => {
                    let schedule = match cron::Schedule::from_str(&cron) {
                        Ok(s) => s,
                        Err(_) => return Err(AppError::InvalidCronSchedule),
                    };

                    let next_run = match schedule.upcoming(Utc).take(1).next() {
                        Some(next_run) => next_run,
                        None => return Err(AppError::InvalidCronSchedule),
                    };

                    let current_time = Utc::now();

                    let should_process = {
                        let last = last_check.read().unwrap();
                        current_time > next_run && &*last < &next_run
                    };

                    if should_process {
                        debug!("Processing queued data");
                        // Acquire the GIL and bind the service for Python interaction
                        Python::with_gil(|py| {
                            let _bound_service = service.bind(py);
                            // Optionally: Call reload_task or interact with the bound_service here
                        });
                        let mut last = last_check.write().unwrap();
                        *last = next_run;
                    }
                },
                _ = &mut shutdown_rx => {
                    info!("Stopping background task");
                    completion_tx.send(()).map_err(|_| AppError::SignalCompletionError)?;
                    break;
                }
            }
        }
        Ok(())
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
    pub space: String,
    pub name: String,
    pub version: String,
}

impl ServiceReloader {
    pub fn start_reloader(
        py: Python<'_>,
        shared_runtime: Arc<tokio::runtime::Runtime>,
        service: Py<ServiceCard>,
        config: ReloadConfig,
        space: String,
        name: String,
        version: String,
    ) -> Result<(), AppError> {
        let (completion_tx, _completion_rx) = oneshot::channel();
        let (_shutdown_tx, shutdown_rx) = oneshot::channel();
        let reloader_runtime = shared_runtime.clone();
        let service = service.clone_ref(py);
        let args = (space, name, version);

        shared_runtime.spawn(async move {
            match start_background_reload_process(
                args,
                service,
                shutdown_rx,
                reloader_runtime,
                Arc::new(RwLock::new(Utc::now())),
                config.clone(),
                completion_tx,
            )
            .await
            {
                Ok(_) => debug!("Queue handler started successfully"),
                Err(e) => error!("Queue handler exited with error: {}", e),
            }
        });

        Ok(())
    }
    // create function that spawns a task and reloads the service card
}
