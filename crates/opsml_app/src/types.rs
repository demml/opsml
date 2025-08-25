// module for shared types
use crate::error::AppError;
use opsml_cards::ServiceCard;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};
use scouter_client::{ScouterQueue, TaskState};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::RwLock;
use tokio::sync::mpsc::UnboundedSender;
use tokio::task::{AbortHandle, JoinHandle};
use tokio_util::sync::CancellationToken;
use tracing::{debug, error};
/// QueueState consists of the ScouterQueue and its associated event loops
/// The event loops are pulled out into a separate field so that we can close the loops without needing
/// access to the python GIL - usually we would need to call queue.bind(py).call_method("shutdown")?
#[derive(Debug)]
pub struct QueueState {
    pub queue: Option<Py<ScouterQueue>>,
    pub task_state: Arc<HashMap<String, TaskState>>,
    pub transport_config: Py<PyAny>,
}

impl QueueState {
    /// Shutdown the ScouterQueue and its associated event loops
    pub fn shutdown(&self) -> Result<(), AppError> {
        // add delay to allow for any insertions to finish
        for (alias, task_state) in self.task_state.iter() {
            debug!("Shutting down queue: {}", alias);
            // shutdown the queue
            task_state.shutdown_tasks()?;
        }

        Ok(())
    }

    pub fn get_queue<'py>(&self, py: Python<'py>) -> Bound<'py, ScouterQueue> {
        self.queue.as_ref().unwrap().bind(py).clone()
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
    pub task_state: ReloadTaskState,
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
pub struct Task {
    pub abort_handle: Option<AbortHandle>,
    pub running: bool,
    pub cancel_token: Option<CancellationToken>,
}

impl Task {
    pub fn new() -> Self {
        Task {
            abort_handle: None,
            running: false,
            cancel_token: None,
        }
    }
}

impl Default for Task {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone)]
pub struct ReloadTaskState {
    // track the loop that downloads service artifacts
    pub download_task: Arc<RwLock<Task>>,
    // track the loop that reloads the service cards
    pub reload_task: Arc<RwLock<Task>>,

    pub download_event: Option<UnboundedSender<DownloadEvent>>,
    pub reload_event: Option<UnboundedSender<ReloadEvent>>,
}

impl ReloadTaskState {
    pub fn new() -> Self {
        ReloadTaskState {
            download_task: Arc::new(RwLock::new(Task::new())),
            reload_task: Arc::new(RwLock::new(Task::new())),
            download_event: None,
            reload_event: None,
        }
    }

    pub fn running(&self) -> bool {
        self.download_task.read().unwrap().running || self.reload_task.read().unwrap().running
    }

    pub fn is_download_task_running(&self) -> bool {
        self.download_task.read().unwrap().running
    }

    pub fn is_reload_task_running(&self) -> bool {
        self.reload_task.read().unwrap().running
    }

    pub fn set_download_task_running(&self, running: bool) -> Result<(), AppError> {
        if let Ok(mut guard) = self.download_task.write() {
            guard.running = running;
            Ok(())
        } else {
            error!("Failed to set download task running state");
            Err(AppError::LockError)
        }
    }

    pub fn set_reload_task_running(&self, running: bool) -> Result<(), AppError> {
        if let Ok(mut guard) = self.reload_task.write() {
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
        self.download_task
            .write()
            .unwrap()
            .abort_handle
            .replace(handle.abort_handle());
    }

    pub fn add_reload_abort_handle(&mut self, handle: JoinHandle<()>) {
        self.reload_task
            .write()
            .unwrap()
            .abort_handle
            .replace(handle.abort_handle());
    }

    pub fn add_download_cancellation_token(&mut self, token: CancellationToken) {
        self.download_task.write().unwrap().cancel_token = Some(token);
    }

    pub fn add_reload_cancellation_token(&mut self, token: CancellationToken) {
        self.reload_task.write().unwrap().cancel_token = Some(token);
    }

    pub fn cancel_download_task(&self) {
        let cancel_token = &self.download_task.read().unwrap().cancel_token;
        if let Some(cancel_token) = cancel_token {
            debug!("Cancelling download task");
            cancel_token.cancel();
        }
    }

    pub fn cancel_reload_task(&self) {
        let cancel_token = &self.reload_task.read().unwrap().cancel_token;
        if let Some(cancel_token) = cancel_token {
            debug!("Cancelling reload task");
            cancel_token.cancel();
        }
    }

    fn shutdown_download_task(&self) -> Result<(), AppError> {
        self.cancel_download_task();

        // abort the download loop
        let download_handle = {
            let guard = self.download_task.write().unwrap().abort_handle.take();
            guard
        };

        if let Some(handle) = download_handle {
            handle.abort();
            debug!("Download loop handle shut down");
        }

        Ok(())
    }

    fn shutdown_reload_task(&self) -> Result<(), AppError> {
        self.cancel_reload_task();

        // abort the reload loop
        let reload_handle = {
            let guard = self.reload_task.write().unwrap().abort_handle.take();
            guard
        };

        if let Some(handle) = reload_handle {
            handle.abort();
            debug!("Reload loop handle shut down");
        }

        Ok(())
    }

    pub fn shutdown_tasks(&self) -> Result<(), AppError> {
        self.shutdown_download_task()?;
        self.shutdown_reload_task()?;
        Ok(())
    }
}

impl Default for ReloadTaskState {
    fn default() -> Self {
        Self::new()
    }
}
