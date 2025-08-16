use crate::error::AppError;
use chrono::DateTime;
use chrono::Utc;
use opsml_cards::Card;
/// This module contains the logic for reloading a ServiceCard
use opsml_cards::ServiceCard;
use opsml_cli::actions::download::download_service;
use opsml_cli::cli::arg::DownloadCard;
use opsml_registry::CardRegistry;
use opsml_types::RegistryType;
use pyo3::prelude::*;
use std::str::FromStr;
use std::sync::Arc;
use std::sync::RwLock;
use tokio::runtime::Runtime;
use tokio::sync::watch;
use tokio::time::{sleep, Duration};
use tracing::{debug, info, info_span, Instrument};

fn get_latest_card(
    space: &str,
    name: &str,
    registry: Arc<CardRegistry>,
) -> Result<ServiceCard, AppError> {
    // This function should query the registry for the latest version of the ServiceCard
    // For now, we will return a dummy ServiceCard
    Ok(ServiceCard {
        space: space.to_string(),
        name: name.to_string(),
        version: "1.0.0".to_string(),
        uid: "dummy-uid".to_string(),
        write_dir: "dummy_write_dir".to_string(),
    })
}

pub struct ReloadConfig {
    pub cron: String,
}

fn reload_task(
    space: &str,
    name: &str,
    version: &str,
    registry: Arc<CardRegistry>,
) -> Result<(), AppError> {
    // list latest service card. If different version:
    // 1. Download new artifacts (including drift profile, to a new directory)
    // 2. Reload ServiceCard

    let write_path = std::env::current_dir()?.as_path().to_path_buf();

    let card = registry
        .list_cards(
            None,
            Some(space.to_string()),
            Some(name.to_string()),
            None,
            None,
            None,
            None,
            1,
        )?
        .cards
        .get(0)
        .unwrap();
    // if latest version matches current version, skip

    let args = DownloadCard {
        space: Some(card.space().to_string()),
        name: Some(card.name().to_string()),
        version: Some(card.version().to_string()),
        uid: Some(card.uid().to_string()),
        write_dir: write_path
            .join("temp")
            .into_os_string()
            .into_string()
            .map_err(|_| CliError::WritePathError)?,
    };

    download_service(&args)?;

    Ok(())
}

pub struct ServiceReloader {
    pub space: String,
    pub name: String,
    pub version: String,
    config: ReloadConfig,
    registry: Arc<CardRegistry>,
}

impl ServiceReloader {
    pub fn new(
        space: String,
        name: String,
        version: String,
        config: ReloadConfig,
    ) -> Result<Self, AppError> {
        let registry = Arc::new(CardRegistry::rust_new(&RegistryType::Service)?);
        Ok(ServiceReloader {
            space,
            name,
            version,
            config,
            registry,
        })
    }

    pub fn start_background_queue(
        &self,
        py: Python,
        mut stop_rx: watch::Receiver<()>,
        runtime: Arc<Runtime>,
        last_check: Arc<RwLock<DateTime<Utc>>>,
    ) -> Result<(), AppError> {
        //let service = self.service.clone_ref(py);
        let cron = self.config.cron.clone();

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
                            // Optionally: Call reload_task(service.clone()) here
                            // reload_task(service.clone()).map_err(|e| {
                            //     debug!("Failed to reload service card: {:?}", e);
                            //     e
                            // })?;
                            let mut last = last_check.write().unwrap();
                            *last = next_run;
                        }
                    },
                    _ = stop_rx.changed() => {
                        info!("Stopping background task");
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

    // create function that spawns a task and reloads the service card
}
