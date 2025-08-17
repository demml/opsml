use crate::error::AppError;
use chrono::{DateTime, Utc};
use opsml_types::{cards::ServiceCardMapping, SaveName, Suffix};
use std::path::Path;
use std::str::FromStr;
use tracing::debug;
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
