use crate::error::AppError;
use crate::types::ReloadTaskState;
use chrono::{DateTime, Utc};
use opsml_types::{SaveName, Suffix, cards::ServiceCardMapping};
use std::path::Path;
use std::str::FromStr;
use std::sync::Arc;
use std::sync::RwLock;
use tokio::time::Duration;
use tracing::{debug, error};
/// Load a card map from path
pub fn load_card_map(path: &Path) -> Result<ServiceCardMapping, AppError> {
    let card_mapping_path = path.join(SaveName::CardMap).with_extension(Suffix::Json);
    debug!("Loading card mapping from: {:?}", card_mapping_path);
    let mapping = ServiceCardMapping::from_path(&card_mapping_path)?;
    Ok(mapping)
}

/// get the next timestamp from a given cron
/// # Arguments
/// * `cron` - A string slice that holds the cron schedule
///
/// # Returns
/// * `Result<DateTime<Utc>, AppError>` - The next scheduled time or an error
pub fn get_next_cron_timestamp(cron: &str) -> Result<DateTime<Utc>, AppError> {
    let schedule = cron::Schedule::from_str(cron)?;

    schedule
        .upcoming(Utc)
        .next()
        .ok_or(AppError::NoUpcomingSchedule)
}

/// helper for reading RWLocks within the reloader logic
/// # Arguments
/// * `lock` - The Arc<RwLock<bool>> to read from
/// # Returns
/// * `bool` - The value of the boolean lock
pub fn is_true(lock: &Arc<RwLock<bool>>) -> bool {
    match lock.read() {
        Ok(guard) => *guard,
        Err(_) => {
            error!("Failed to read boolean lock");
            false
        }
    }
}

/// Helper that updates a boolean lock. Used within app reloader logic
/// This is mainly a convenience function to help with unwrapping and handling errors
/// # Arguments
/// * `lock` - The Arc<RwLock<bool>> to update
/// * `value` - The new value to set the lock to
pub fn update_bool_lock(lock: &Arc<RwLock<bool>>, value: bool) -> Result<(), AppError> {
    match lock.write() {
        Ok(mut guard) => {
            *guard = value;
            Ok(())
        }
        Err(_) => {
            error!("Failed to write boolean lock");
            Err(AppError::UpdateLockError)
        }
    }
}

/// Waits for the download task to start
pub fn wait_for_download_task(task_state: &ReloadTaskState) -> Result<(), AppError> {
    // Signal confirm start

    let mut max_retries = 20;
    while max_retries > 0 {
        if task_state.is_download_task_running() {
            debug!("Download task started successfully");
            return Ok(());
        }
        max_retries -= 1;
        std::thread::sleep(Duration::from_millis(200));
    }
    error!("Download task failed to start");
    Err(AppError::DownloadTaskFailedToStartError)
}

/// Waits for the reload task to start
pub fn wait_for_reload_task(task_state: &ReloadTaskState) -> Result<(), AppError> {
    // Signal confirm start

    let mut max_retries = 20;
    while max_retries > 0 {
        if task_state.is_reload_task_running() {
            debug!("Reload task started successfully");
            return Ok(());
        }
        max_retries -= 1;
        std::thread::sleep(Duration::from_millis(200));
    }
    error!("Event task failed to start");
    Err(AppError::ReloadTaskFailedToStartError)
}
