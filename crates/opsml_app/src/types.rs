// module for shared types
use crate::error::AppError;
use opsml_cards::ServiceCard;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};
use scouter_client::{EventState, ScouterQueue};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::RwLock;
use std::time::Duration;
use tokio::sync::mpsc::UnboundedSender;
use tokio::task::{AbortHandle, JoinHandle};
use tokio_util::sync::CancellationToken;
use tracing::{debug, error, instrument};
/// QueueState consists of the ScouterQueue and its associated event loops
/// The event loops are pulled out into a separate field so that we can close the loops without needing
/// access to the python GIL - usually we would need to call queue.bind(py).call_method("shutdown")?
#[derive(Debug)]
pub struct QueueState {
    pub queue: Py<ScouterQueue>,
    pub queue_event_loops: HashMap<String, Arc<EventState>>,
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
    Ready,
}

#[derive(Debug, Clone)]
pub enum DownloadEvent {
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

impl ReloaderState {
    pub fn update_service(&self, service: Py<ServiceCard>) -> Result<(), AppError> {
        let mut guard = self
            .service
            .write()
            .map_err(|_| AppError::PoisonError("Failed to write service".to_string()))?;
        *guard = service;
        Ok(())
    }
}

#[derive(Debug)]
pub struct Loop {
    pub abort_handle: Option<AbortHandle>,
    pub running: bool,
    pub cancel_token: Option<CancellationToken>,
}

impl Loop {
    pub fn new() -> Self {
        Loop {
            abort_handle: None,
            running: false,
            cancel_token: None,
        }
    }
}

impl Default for Loop {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone)]
pub struct ReloadEventState {
    // track the loop that downloads service artifacts
    pub download_events: Arc<RwLock<Loop>>,
    // track the loop that reloads the service cards
    pub reload_events: Arc<RwLock<Loop>>,

    pub download_event: Option<UnboundedSender<DownloadEvent>>,
    pub reload_event: Option<UnboundedSender<ReloadEvent>>,
}

impl ReloadEventState {
    pub fn new() -> Self {
        ReloadEventState {
            download_events: Arc::new(RwLock::new(Loop::new())),
            reload_events: Arc::new(RwLock::new(Loop::new())),
            download_event: None,
            reload_event: None,
        }
    }

    pub fn running(&self) -> bool {
        self.download_events.read().unwrap().running || self.reload_events.read().unwrap().running
    }

    pub fn download_loop_running(&self) -> bool {
        self.download_events.read().unwrap().running
    }

    pub fn reload_loop_running(&self) -> bool {
        self.reload_events.read().unwrap().running
    }

    pub fn set_download_loop_running(&self, running: bool) -> Result<(), AppError> {
        if let Ok(mut guard) = self.download_events.write() {
            guard.running = running;
            Ok(())
        } else {
            error!("Failed to set download loop running state");
            Err(AppError::LockError)
        }
    }

    pub fn set_reload_loop_running(&self, running: bool) -> Result<(), AppError> {
        if let Ok(mut guard) = self.reload_events.write() {
            guard.running = running;
            Ok(())
        } else {
            error!("Failed to set reload loop running state");
            Err(AppError::LockError)
        }
    }

    pub fn set_reload_tx(&mut self, tx: UnboundedSender<ReloadEvent>) -> Result<(), AppError> {
        self.reload_event = Some(tx);
        Ok(())
    }

    pub fn set_download_tx(&mut self, tx: UnboundedSender<DownloadEvent>) -> Result<(), AppError> {
        self.download_event = Some(tx);
        Ok(())
    }

    pub fn trigger_download_event(&self) -> Result<(), AppError> {
        if let Some(tx) = &self.download_event {
            tx.send(DownloadEvent::Force)?;
        }
        Ok(())
    }

    pub fn trigger_reload_event(&self) -> Result<(), AppError> {
        if let Some(tx) = &self.reload_event {
            tx.send(ReloadEvent::Ready)?;
        }
        Ok(())
    }

    pub fn add_download_abort_handle(&mut self, handle: JoinHandle<()>) {
        self.download_events
            .write()
            .unwrap()
            .abort_handle
            .replace(handle.abort_handle());
    }

    pub fn add_reload_abort_handle(&mut self, handle: JoinHandle<()>) {
        self.reload_events
            .write()
            .unwrap()
            .abort_handle
            .replace(handle.abort_handle());
    }
}

impl Default for ReloadEventState {
    fn default() -> Self {
        Self::new()
    }
}
