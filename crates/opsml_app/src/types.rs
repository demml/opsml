// module for shared types
use crate::error::AppError;
use opsml_cards::ServiceCard;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};
use scouter_client::{EventLoops, ScouterQueue};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::RwLock;
use std::time::Duration;
use tokio::sync::mpsc::UnboundedSender;
use tokio::task::JoinHandle;
use tracing::{debug, error, instrument};
/// QueueState consists of the ScouterQueue and its associated event loops
/// The event loops are pulled out into a separate field so that we can close the loops without needing
/// access to the python GIL - usually we would need to call queue.bind(py).call_method("shutdown")?
#[derive(Debug)]
pub struct QueueState {
    pub queue: Py<ScouterQueue>,
    pub queue_event_loops: HashMap<String, Arc<EventLoops>>,
    pub transport_config: Py<PyAny>,
}

impl QueueState {
    /// Shutdown the ScouterQueue and its associated event loops
    pub fn shutdown(&self) -> Result<(), AppError> {
        for (alias, event_loop) in &self.queue_event_loops {
            debug!("Shutting down queue: {}", alias);
            // shutdown the queue
            event_loop.shutdown()?;

            // wait for event and background cleanup
            while event_loop.running() {
                std::thread::sleep(std::time::Duration::from_millis(100));
            }
        }

        Ok(())
    }
}

#[derive(Debug, Clone)]
pub enum ReloadEvent {
    Start,
    Ready,
    Stop,
}

#[derive(Debug, Clone)]
pub enum DownloadEvent {
    Start,
    Stop,
    Force,
}

pub struct ReloaderState {
    pub reload_path: Arc<PathBuf>,
    pub service_path: Arc<PathBuf>,
    pub load_kwargs: Option<Arc<RwLock<Py<PyDict>>>>,
    pub service: Arc<RwLock<Py<ServiceCard>>>,
    pub queue: Option<Arc<RwLock<QueueState>>>,
    pub max_retries: u32,
}

#[derive(Debug)]
pub struct DownloadEventLoops {
    // track the loop that receives events
    pub download_loop: Option<JoinHandle<()>>,
    pub download_loop_running: bool,
    pub download_tx: Option<UnboundedSender<DownloadEvent>>,
}

impl DownloadEventLoops {
    pub fn new() -> Self {
        DownloadEventLoops {
            download_loop: None,
            download_loop_running: false,
            download_tx: None,
        }
    }
}

#[derive(Debug)]
pub struct ReloadEventLoops {
    pub reload_loop: Option<JoinHandle<()>>,
    pub reload_loop_running: bool,
    pub reload_tx: Option<UnboundedSender<ReloadEvent>>,
}

impl ReloadEventLoops {
    pub fn new() -> Self {
        ReloadEventLoops {
            reload_loop: None,
            reload_loop_running: false,
            reload_tx: None,
        }
    }
}

#[derive(Debug, Clone)]
pub struct StateEventLoops {
    // track the loop that downloads service artifacts
    pub download_events: Arc<RwLock<DownloadEventLoops>>,

    // track the loop that reloads the service cards
    pub reload_events: Arc<RwLock<ReloadEventLoops>>,
}

impl StateEventLoops {
    pub fn new() -> Self {
        StateEventLoops {
            download_events: Arc::new(RwLock::new(DownloadEventLoops::new())),
            reload_events: Arc::new(RwLock::new(ReloadEventLoops::new())),
        }
    }

    pub fn running(&self) -> bool {
        self.download_events.read().unwrap().download_loop_running
            || self.reload_events.read().unwrap().reload_loop_running
    }

    pub fn download_loop_running(&self) -> bool {
        self.download_events.read().unwrap().download_loop_running
    }

    pub fn reload_loop_running(&self) -> bool {
        self.reload_events.read().unwrap().reload_loop_running
    }

    pub fn set_download_loop_running(&self, running: bool) -> Result<(), AppError> {
        if let Ok(mut guard) = self.download_events.write() {
            guard.download_loop_running = running;
            Ok(())
        } else {
            error!("Failed to set download loop running state");
            Err(AppError::LockError)
        }
    }

    pub fn set_reload_loop_running(&self, running: bool) -> Result<(), AppError> {
        if let Ok(mut guard) = self.reload_events.write() {
            guard.reload_loop_running = running;
            Ok(())
        } else {
            error!("Failed to set reload loop running state");
            Err(AppError::LockError)
        }
    }

    pub fn trigger_download_event(&self) -> Result<(), AppError> {
        if let Some(tx) = &self.download_events.read().unwrap().download_tx {
            tx.send(DownloadEvent::Force)?;
        }
        Ok(())
    }

    pub fn send_reload_start(&self) -> Result<(), AppError> {
        if let Some(tx) = &self.reload_events.read().unwrap().reload_tx {
            tx.send(ReloadEvent::Start)?;
            Ok(())
        } else {
            error!("No reload_tx found - channel not set up");
            Err(AppError::NoReloadTxError)
        }
    }

    /// Shutdown the download loop. This is used in the reload async task
    pub async fn shutdown_download_loop(&mut self) -> Result<(), AppError> {
        // this sends a stop event to the download loop
        debug!("Sending stop event to download loop");
        if let Some(tx) = &self.download_events.read().unwrap().download_tx {
            tx.send(DownloadEvent::Stop)?;
        }

        let download_handle = {
            let guard = self.download_events.write().unwrap().download_loop.take();
            guard
        };

        if let Some(handle) = download_handle {
            handle.await?;
        }

        Ok(())
    }

    fn abort_download_loop(&self) -> Result<(), AppError> {
        let download_handle = {
            let guard = self.download_events.write().unwrap().download_loop.take();
            guard
        };

        if let Some(handle) = download_handle {
            handle.abort();
            debug!("Download loop handle aborted");
        }

        // set to false
        self.download_events.write().unwrap().download_loop_running = false;

        Ok(())
    }

    fn abort_reload_loop(&self) -> Result<(), AppError> {
        let reload_handle = {
            let guard = self.reload_events.write().unwrap().reload_loop.take();
            guard
        };

        if let Some(handle) = reload_handle {
            handle.abort();
            debug!("Reload loop handle aborted");
        }

        Ok(())
    }

    fn wait_for_download_loop_to_stop(&self) -> Result<(), AppError> {
        let mut max_retries = 50;
        while self.download_events.read().unwrap().download_loop_running {
            std::thread::sleep(Duration::from_millis(100));
            max_retries -= 1;
            if max_retries == 0 {
                error!("Timed out waiting for download loop to stop. Aborting the thread");
                self.abort_download_loop()?;
                break;
            }
        }
        Ok(())
    }

    #[instrument(skip_all)]
    pub fn shutdown_reload_loop(&mut self) -> Result<(), AppError> {
        // this sends a stop event to the reload loop
        debug!("Sending stop event to reload loop");
        if let Some(tx) = &self.reload_events.read().unwrap().reload_tx {
            tx.send(ReloadEvent::Stop)?;
        } else {
            error!("No reload_tx found - channel not set up");
            return Err(AppError::NoReloadTxError);
        }

        self.wait_for_download_loop_to_stop()?;
        self.abort_reload_loop()?;

        Ok(())
    }

    pub fn add_download_handle(&mut self, handle: JoinHandle<()>) {
        self.download_events
            .write()
            .unwrap()
            .download_loop
            .replace(handle);
    }

    pub fn add_reload_handle(&mut self, handle: JoinHandle<()>) {
        self.reload_events
            .write()
            .unwrap()
            .reload_loop
            .replace(handle);
    }

    pub fn set_reload_tx(&self, tx: UnboundedSender<ReloadEvent>) -> Result<(), AppError> {
        if let Ok(mut guard) = self.reload_events.write() {
            guard.reload_tx = Some(tx);
            Ok(())
        } else {
            error!("Failed to set reload tx");
            Err(AppError::LockError)
        }
    }

    /// Set the download event sender  
    pub fn set_download_tx(&self, tx: UnboundedSender<DownloadEvent>) -> Result<(), AppError> {
        if let Ok(mut guard) = self.download_events.write() {
            guard.download_tx = Some(tx);
            Ok(())
        } else {
            error!("Failed to set download tx");
            Err(AppError::LockError)
        }
    }

    pub fn debug_state(&self) {
        let download_guard = self.download_events.read().unwrap();
        let reload_guard = self.reload_events.read().unwrap();

        debug!(
            r#"AppEventState:
                Download loop running: {}
                Download tx exists: {}
                Download handle exists: {}
                Reload loop running: {}
                Reload tx exists: {}
                Reload handle exists: {}"#,
            download_guard.download_loop_running,
            download_guard.download_tx.is_some(),
            download_guard.download_loop.is_some(),
            reload_guard.reload_loop_running,
            reload_guard.reload_tx.is_some(),
            reload_guard.reload_loop.is_some()
        );
    }
}

impl Default for ReloadEventLoops {
    fn default() -> Self {
        Self::new()
    }
}
