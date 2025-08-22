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
use tokio::sync::mpsc::UnboundedSender;
use tokio::task::JoinHandle;
use tracing::{debug, error};

/// QueueState consists of the ScouterQueue and its associated event loops
/// The event loops are pulled out into a separate field so that we can close the loops without needing
/// access to the python GIL - usually we would need to call queue.bind(py).call_method("shutdown")?
#[derive(Debug)]
pub struct QueueState {
    pub queue: Arc<RwLock<Py<ScouterQueue>>>,
    pub queue_event_loops: HashMap<String, Arc<EventLoops>>,
    pub transport_config: Arc<RwLock<Py<PyAny>>>,
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
    pub queue: Option<Arc<QueueState>>,
    pub max_retries: u32,
}

#[derive(Debug, Clone)]
pub struct ReloadEventLoops {
    // track the loop that receives events
    pub download_loop: Option<Arc<RwLock<JoinHandle<()>>>>,
    pub download_loop_running: Arc<RwLock<bool>>,
    pub download_tx: Option<UnboundedSender<DownloadEvent>>,

    // track the loop that processes background tasks (only applies to psi and custom)
    pub reload_loop: Option<Arc<RwLock<JoinHandle<()>>>>,
    pub reload_loop_running: Arc<RwLock<bool>>,
    pub reload_tx: Option<UnboundedSender<ReloadEvent>>,
}

impl ReloadEventLoops {
    pub fn new() -> Self {
        ReloadEventLoops {
            download_loop: None,
            download_loop_running: Arc::new(RwLock::new(false)),
            download_tx: None,
            reload_loop: None,
            reload_loop_running: Arc::new(RwLock::new(false)),
            reload_tx: None,
        }
    }

    pub fn running(&self) -> bool {
        *self.download_loop_running.read().unwrap() || *self.reload_loop_running.read().unwrap()
    }

    pub fn download_loop_running(&self) -> bool {
        *self.download_loop_running.read().unwrap()
    }

    pub fn reload_loop_running(&self) -> bool {
        *self.reload_loop_running.read().unwrap()
    }

    pub fn set_download_loop_running(&self, running: bool) -> Result<(), AppError> {
        if let Ok(mut guard) = self.download_loop_running.write() {
            *guard = running;
            Ok(())
        } else {
            error!("Failed to set download loop running state");
            Err(AppError::LockError)
        }
    }

    pub fn set_reload_loop_running(&self, running: bool) -> Result<(), AppError> {
        if let Ok(mut guard) = self.reload_loop_running.write() {
            *guard = running;
            Ok(())
        } else {
            error!("Failed to set reload loop running state");
            Err(AppError::LockError)
        }
    }

    pub fn trigger_download_event(&self) -> Result<(), AppError> {
        if let Some(tx) = &self.download_tx {
            let _ = tx.send(DownloadEvent::Force)?;
        }
        Ok(())
    }

    pub fn add_download_handle(&mut self, handle: JoinHandle<()>) {
        self.download_loop = Some(Arc::new(RwLock::new(handle)));
    }

    pub fn add_reload_handle(&mut self, handle: JoinHandle<()>) {
        self.reload_loop = Some(Arc::new(RwLock::new(handle)));
    }
}
