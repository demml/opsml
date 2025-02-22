use chrono::Utc;
use opsml_error::ExperimentError;
use opsml_registry::enums::OpsmlRegistry;
use opsml_types::{cards::HardwareMetricLogger, contracts::HardwareMetricRequest};
use std::sync::Arc;
use tokio::sync::{watch, Mutex};
use tokio::time::{self, Duration};
use tracing::Instrument;
use tracing::{debug, error, info, info_span};

async fn insert_metrics(
    registry: Arc<Mutex<OpsmlRegistry>>,
    hw_logger: &mut HardwareMetricLogger,
    experiment_uid: &str,
) -> Result<(), ExperimentError> {
    debug!("Locking registry");
    let mut registry = registry.lock().await;

    debug!("Getting metrics");
    let metrics = hw_logger.get_metrics();
    let request = HardwareMetricRequest {
        experiment_uid: experiment_uid.to_string(),
        metrics: metrics.clone(),
    };
    registry.insert_hardware_metrics(request).await?;

    Ok(())
}

fn start_background_task(
    rt: Arc<tokio::runtime::Runtime>,
    registry: Arc<Mutex<OpsmlRegistry>>,
    mut stop_rx: watch::Receiver<()>,
    experiment_uid: String,
) -> Result<(), ExperimentError> {
    let registry = registry.clone();
    let handle = rt.clone();
    let mut last_inserted = Utc::now().naive_utc();
    let mut hw_logger = HardwareMetricLogger::new();

    debug!("Starting background task");

    // spawn the background task using the already cloned handle
    let future = async move {
        loop {
            tokio::select! {

                _ = time::sleep(Duration::from_secs(5)) => {

                    debug!("Getting metrics");
                    let now = Utc::now().naive_utc();
                    let elapsed = now - last_inserted;

                    debug!("Elapsed: {:?}", elapsed);

                    if elapsed.num_seconds() >= 5 {
                        let inserted = insert_metrics(registry.clone(), &mut hw_logger, &experiment_uid).await;

                        if let Err(e) = inserted {
                            error!("Error inserting metrics: {:?}", e);
                        }

                        last_inserted = now;
                    }
                },
                _ = stop_rx.changed() => {
                    info!("Stopping background task");

                    break;
                }
            }
        }
    };

    handle.spawn(future.instrument(info_span!("Hardware Queue")));

    Ok(())
}

pub struct HardwareQueue {
    stop_tx: watch::Sender<()>,
}

impl HardwareQueue {
    pub fn start(
        rt: Arc<tokio::runtime::Runtime>,
        registry: Arc<Mutex<OpsmlRegistry>>,
        experiment_uid: String,
    ) -> Result<Self, ExperimentError> {
        let (stop_tx, stop_rx) = watch::channel(());

        start_background_task(rt, registry, stop_rx, experiment_uid)?;

        Ok(Self { stop_tx })
    }
    pub fn stop(&mut self) {
        let _ = self.stop_tx.send(());
    }
}
