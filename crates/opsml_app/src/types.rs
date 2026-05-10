// module for shared types
use crate::error::AppError;
use opsml_cards::ServiceCard;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};
use scouter_client::ScouterQueue;
use std::fmt;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::RwLock;
use tokio::sync::mpsc::UnboundedSender;
use tokio::task::{AbortHandle, JoinHandle};
use tokio_util::sync::CancellationToken;
use tracing::{debug, error};
/// Runtime state for an optional Scouter queue.
///
/// The queue object and transport config are Python-owned values, while
/// `shutdown_fn` lets Rust stop Scouter queue tasks without calling back into
/// Python during app shutdown.
pub struct QueueState {
    /// Python-owned Scouter queue exposed through `AppState.queue`.
    pub queue: Option<Py<ScouterQueue>>,
    /// Rust-side shutdown hook for Scouter queue background tasks.
    pub shutdown_fn: Arc<dyn Fn() -> Result<(), AppError> + Send + Sync>,
    /// Python-owned transport config reused when reloading the queue.
    pub transport_config: Py<PyAny>,
}

impl fmt::Debug for QueueState {
    /// Formats queue state without trying to format Python transport config internals.
    ///
    /// # Arguments
    /// * `f` - Formatter receiving the debug representation.
    ///
    /// # Returns
    /// A formatting result from the formatter.
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("QueueState")
            .field("queue", &self.queue)
            .finish_non_exhaustive()
    }
}

impl QueueState {
    /// Shuts down the Scouter queue and its associated event loops.
    ///
    /// # Returns
    /// `Ok(())` after the queue shutdown hook completes.
    ///
    /// # Errors
    /// Returns [`AppError`] when the queue shutdown hook fails.
    pub fn shutdown(&self) -> Result<(), AppError> {
        (self.shutdown_fn)()
    }

    /// Returns the Python-bound Scouter queue for the active interpreter.
    ///
    /// Callers must only invoke this when `queue` is `Some`; app-state accessors
    /// enforce that before reaching this method.
    ///
    /// # Arguments
    /// * `py` - Active Python interpreter token used to bind the queue object.
    ///
    /// # Returns
    /// A Python-bound [`ScouterQueue`].
    ///
    /// # Panics
    /// Panics when `queue` is `None`.
    pub fn get_queue<'py>(&self, py: Python<'py>) -> Bound<'py, ScouterQueue> {
        self.queue.as_ref().unwrap().bind(py).clone()
    }
}

/// Event sent to the reload loop after a new service artifact has been downloaded.
#[derive(Debug, Clone)]
pub enum ReloadEvent {
    /// Indicates that downloaded artifacts are ready to load into app state.
    Ready,
}

/// Event sent to the download loop to request registry checks.
#[derive(Debug, Clone)]
pub enum DownloadEvent {
    /// Forces an immediate registry check outside the cron schedule.
    Force,
}

/// Shared state needed by the background reload loop.
///
/// This type carries the active service path, staging path, optional queue,
/// Python-owned load kwargs, and task state required to replace the loaded
/// service after a new artifact is downloaded.
pub struct ReloaderState {
    /// Directory containing the newly downloaded service artifacts.
    pub reload_path: Arc<PathBuf>,
    /// Directory containing the currently active service artifacts.
    pub service_path: Arc<PathBuf>,
    /// Optional Python load kwargs reused when loading replacement artifacts.
    pub load_kwargs: Option<Arc<RwLock<Py<PyDict>>>>,
    /// Shared currently loaded service card.
    pub service: Arc<RwLock<Py<ServiceCard>>>,
    /// Optional shared Scouter queue to reload with the service.
    pub queue: Option<Arc<RwLock<QueueState>>>,
    /// Maximum retry attempts for a failed reload.
    pub max_retries: u32,
    /// Download and reload task handles, senders, and cancellation tokens.
    pub task_state: ReloadTaskState,
}

impl ReloaderState {
    /// Replaces the currently loaded service card.
    ///
    /// A poisoned service lock is converted to [`AppError::PoisonError`].
    ///
    /// # Arguments
    /// * `service` - Replacement Python-owned service card.
    ///
    /// # Returns
    /// `Ok(())` after the shared service card has been replaced.
    ///
    /// # Errors
    /// Returns [`AppError::PoisonError`] when the service lock is poisoned.
    pub fn update_service(&self, service: Py<ServiceCard>) -> Result<(), AppError> {
        let mut guard = self
            .service
            .write()
            .map_err(|_| AppError::PoisonError("Failed to write service".to_string()))?;
        *guard = service;
        Ok(())
    }
}

/// Tracks one background task's running state and cancellation handles.
#[derive(Debug)]
pub struct Task {
    /// Abort handle used to stop the Tokio task.
    pub abort_handle: Option<AbortHandle>,
    /// Whether the task has marked itself as running.
    pub running: bool,
    /// Cooperative cancellation token observed by the task.
    pub cancel_token: Option<CancellationToken>,
}

impl Task {
    /// Creates an empty task tracker with no running task.
    ///
    /// # Returns
    /// A [`Task`] with no abort handle, no cancellation token, and
    /// `running = false`.
    pub fn new() -> Self {
        Task {
            abort_handle: None,
            running: false,
            cancel_token: None,
        }
    }
}

impl Default for Task {
    /// Creates an empty task tracker.
    ///
    /// # Returns
    /// A default [`Task`] equivalent to [`Task::new`].
    fn default() -> Self {
        Self::new()
    }
}

/// Shared lifecycle state for the app-state download and reload loops.
///
/// This state owns task trackers plus optional channels used to request forced
/// downloads and service reloads.
#[derive(Debug, Clone)]
pub struct ReloadTaskState {
    /// Tracks the loop that downloads service artifacts.
    pub download_task: Arc<RwLock<Task>>,
    /// Tracks the loop that reloads service cards and queues.
    pub reload_task: Arc<RwLock<Task>>,

    /// Sender used to request download checks.
    pub download_event: Option<UnboundedSender<DownloadEvent>>,
    /// Sender used to notify the reload loop that artifacts are ready.
    pub reload_event: Option<UnboundedSender<ReloadEvent>>,
}

impl ReloadTaskState {
    /// Creates empty lifecycle state for download and reload tasks.
    ///
    /// # Returns
    /// A [`ReloadTaskState`] with empty task trackers and no event senders.
    pub fn new() -> Self {
        ReloadTaskState {
            download_task: Arc::new(RwLock::new(Task::new())),
            reload_task: Arc::new(RwLock::new(Task::new())),
            download_event: None,
            reload_event: None,
        }
    }

    /// Returns whether either background task is marked as running.
    ///
    /// # Returns
    /// `true` when either the download task or reload task is marked running.
    ///
    /// # Panics
    /// Panics if either task lock is poisoned.
    pub fn running(&self) -> bool {
        self.download_task.read().unwrap().running || self.reload_task.read().unwrap().running
    }

    /// Returns whether the download task is marked as running.
    ///
    /// # Returns
    /// `true` when the download task is marked running.
    ///
    /// # Panics
    /// Panics if the download task lock is poisoned.
    pub fn is_download_task_running(&self) -> bool {
        self.download_task.read().unwrap().running
    }

    /// Returns whether the reload task is marked as running.
    ///
    /// # Returns
    /// `true` when the reload task is marked running.
    ///
    /// # Panics
    /// Panics if the reload task lock is poisoned.
    pub fn is_reload_task_running(&self) -> bool {
        self.reload_task.read().unwrap().running
    }

    /// Updates the download task running flag.
    ///
    /// Returns [`AppError::LockError`] if the task lock cannot be acquired.
    ///
    /// # Arguments
    /// * `running` - New running state for the download task.
    ///
    /// # Returns
    /// `Ok(())` after the running flag is updated.
    ///
    /// # Errors
    /// Returns [`AppError::LockError`] when the download task lock cannot be
    /// acquired.
    pub fn set_download_task_running(&self, running: bool) -> Result<(), AppError> {
        if let Ok(mut guard) = self.download_task.write() {
            guard.running = running;
            Ok(())
        } else {
            error!("Failed to set download task running state");
            Err(AppError::LockError)
        }
    }

    /// Updates the reload task running flag.
    ///
    /// Returns [`AppError::LockError`] if the task lock cannot be acquired.
    ///
    /// # Arguments
    /// * `running` - New running state for the reload task.
    ///
    /// # Returns
    /// `Ok(())` after the running flag is updated.
    ///
    /// # Errors
    /// Returns [`AppError::LockError`] when the reload task lock cannot be
    /// acquired.
    pub fn set_reload_task_running(&self, running: bool) -> Result<(), AppError> {
        if let Ok(mut guard) = self.reload_task.write() {
            guard.running = running;
            Ok(())
        } else {
            error!("Failed to set reload loop running state");
            Err(AppError::LockError)
        }
    }

    /// Stores the sender used by download code to notify the reload loop.
    ///
    /// # Arguments
    /// * `tx` - Sender used to deliver [`ReloadEvent`] values to the reload loop.
    ///
    /// # Returns
    /// `Ok(())` after the sender is stored.
    ///
    /// # Errors
    /// This method currently does not return an error, but uses `Result` to
    /// match the task-state setup API.
    pub fn set_reload_tx(&mut self, tx: UnboundedSender<ReloadEvent>) -> Result<(), AppError> {
        self.reload_event = Some(tx);
        Ok(())
    }

    /// Stores the sender used to request download checks.
    ///
    /// # Arguments
    /// * `tx` - Sender used to deliver [`DownloadEvent`] values to the download loop.
    ///
    /// # Returns
    /// `Ok(())` after the sender is stored.
    ///
    /// # Errors
    /// This method currently does not return an error, but uses `Result` to
    /// match the task-state setup API.
    pub fn set_download_tx(&mut self, tx: UnboundedSender<DownloadEvent>) -> Result<(), AppError> {
        self.download_event = Some(tx);
        Ok(())
    }

    /// Sends a force-download event when the download loop has been started.
    ///
    /// If no sender has been registered yet, this is a no-op.
    ///
    /// # Returns
    /// `Ok(())` after the event is sent or skipped.
    ///
    /// # Errors
    /// Returns [`AppError`] when the registered download channel is closed.
    pub fn trigger_download_event(&self) -> Result<(), AppError> {
        if let Some(tx) = &self.download_event {
            tx.send(DownloadEvent::Force)?;
        }
        Ok(())
    }

    /// Sends a reload-ready event when the reload loop has been started.
    ///
    /// If no sender has been registered yet, this is a no-op.
    ///
    /// # Returns
    /// `Ok(())` after the event is sent or skipped.
    ///
    /// # Errors
    /// Returns [`AppError`] when the registered reload channel is closed.
    pub fn trigger_reload_event(&self) -> Result<(), AppError> {
        if let Some(tx) = &self.reload_event {
            tx.send(ReloadEvent::Ready)?;
        }
        Ok(())
    }

    /// Stores the abort handle for the running download task.
    ///
    /// # Arguments
    /// * `handle` - Join handle for the spawned download task.
    ///
    /// # Panics
    /// Panics if the download task lock is poisoned.
    pub fn add_download_abort_handle(&mut self, handle: JoinHandle<()>) {
        self.download_task
            .write()
            .unwrap()
            .abort_handle
            .replace(handle.abort_handle());
    }

    /// Stores the abort handle for the running reload task.
    ///
    /// # Arguments
    /// * `handle` - Join handle for the spawned reload task.
    ///
    /// # Panics
    /// Panics if the reload task lock is poisoned.
    pub fn add_reload_abort_handle(&mut self, handle: JoinHandle<()>) {
        self.reload_task
            .write()
            .unwrap()
            .abort_handle
            .replace(handle.abort_handle());
    }

    /// Stores the cancellation token for the running download task.
    ///
    /// # Arguments
    /// * `token` - Cancellation token observed by the download task.
    ///
    /// # Panics
    /// Panics if the download task lock is poisoned.
    pub fn add_download_cancellation_token(&mut self, token: CancellationToken) {
        self.download_task.write().unwrap().cancel_token = Some(token);
    }

    /// Stores the cancellation token for the running reload task.
    ///
    /// # Arguments
    /// * `token` - Cancellation token observed by the reload task.
    ///
    /// # Panics
    /// Panics if the reload task lock is poisoned.
    pub fn add_reload_cancellation_token(&mut self, token: CancellationToken) {
        self.reload_task.write().unwrap().cancel_token = Some(token);
    }

    /// Requests cooperative cancellation of the download task.
    ///
    /// # Panics
    /// Panics if the download task lock is poisoned.
    pub fn cancel_download_task(&self) {
        let cancel_token = &self.download_task.read().unwrap().cancel_token;
        if let Some(cancel_token) = cancel_token {
            debug!("Cancelling download task");
            cancel_token.cancel();
        }
    }

    /// Requests cooperative cancellation of the reload task.
    ///
    /// # Panics
    /// Panics if the reload task lock is poisoned.
    pub fn cancel_reload_task(&self) {
        let cancel_token = &self.reload_task.read().unwrap().cancel_token;
        if let Some(cancel_token) = cancel_token {
            debug!("Cancelling reload task");
            cancel_token.cancel();
        }
    }

    /// Cancels and aborts the download task if one is running.
    ///
    /// # Returns
    /// `Ok(())` after cancellation has been requested and any abort handle has
    /// been consumed.
    ///
    /// # Errors
    /// This method currently does not return an error, but uses `Result` to
    /// match the combined shutdown API.
    ///
    /// # Panics
    /// Panics if the download task lock is poisoned.
    fn shutdown_download_task(&self) -> Result<(), AppError> {
        self.cancel_download_task();

        // abort the download loop
        let download_handle = { self.download_task.write().unwrap().abort_handle.take() };

        if let Some(handle) = download_handle {
            handle.abort();
            debug!("Download loop handle shut down");
        }

        Ok(())
    }

    /// Cancels and aborts the reload task if one is running.
    ///
    /// # Returns
    /// `Ok(())` after cancellation has been requested and any abort handle has
    /// been consumed.
    ///
    /// # Errors
    /// This method currently does not return an error, but uses `Result` to
    /// match the combined shutdown API.
    ///
    /// # Panics
    /// Panics if the reload task lock is poisoned.
    fn shutdown_reload_task(&self) -> Result<(), AppError> {
        self.cancel_reload_task();

        // abort the reload loop
        let reload_handle = { self.reload_task.write().unwrap().abort_handle.take() };

        if let Some(handle) = reload_handle {
            handle.abort();
            debug!("Reload loop handle shut down");
        }

        Ok(())
    }

    /// Cancels and aborts both background tasks.
    ///
    /// # Returns
    /// `Ok(())` after both task trackers have been shut down.
    ///
    /// # Errors
    /// Returns [`AppError`] if either task-specific shutdown helper returns an
    /// error.
    pub fn shutdown_tasks(&self) -> Result<(), AppError> {
        self.shutdown_download_task()?;
        self.shutdown_reload_task()?;
        Ok(())
    }
}

impl Default for ReloadTaskState {
    /// Creates empty lifecycle state for download and reload tasks.
    ///
    /// # Returns
    /// A default [`ReloadTaskState`] equivalent to [`ReloadTaskState::new`].
    fn default() -> Self {
        Self::new()
    }
}
