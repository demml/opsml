use chrono::{NaiveDateTime, Timelike};
use opsml_error::error::UtilError;
use regex::Regex;

use uuid::Uuid;

const PUNCTUATION: &str = "!\"#$%&'()*+,./:;<=>?@[\\]^`{|}~";
const NAME_REPOSITORY_PATTERN: &str = r"^[a-z0-9]+(?:[-a-z0-9]+)*/[-a-z0-9]+$";

pub fn clean_string(input: &str) -> String {
    let pattern = format!("[{}]", regex::escape(PUNCTUATION));
    let re = Regex::new(&pattern.to_string()).unwrap();
    re.replace_all(&input.trim().to_lowercase(), "")
        .to_string()
        .replace("_", "-")
}

pub fn validate_name_repository_pattern(name: &str, repository: &str) -> Result<(), UtilError> {
    let name_repo = format!("{}/{}", name, repository);

    let re = Regex::new(NAME_REPOSITORY_PATTERN)
        .map_err(|_| UtilError::Error("Failed to create regex".to_string()))?;

    if !re.is_match(&name_repo) {
        return Err(UtilError::Error(
            "Invalid name/repository pattern".to_string(),
        ));
    }

    if name.len() > 53 {
        return Err(UtilError::Error("Name is too long".to_string()));
    }

    Ok(())
}

/// Check if a string is a valid UUIDv4
///
/// # Arguments
///
/// * `uid` - A string slice that holds the UUID
///
/// # Returns
///
/// * `bool` - A boolean indicating if the UUID is valid
pub fn is_valid_uuid4(uid: &str) -> Result<bool, UtilError> {
    match Uuid::parse_str(uid) {
        Ok(uuid) => Ok(uuid.get_version_num() == 4),
        Err(_) => Err(UtilError::UuidError),
    }
}

pub fn get_epoch_time_to_search(max_date: &str) -> Result<i64, UtilError> {
    const YEAR_MONTH_DATE: &str = "%Y-%m-%d";

    // Parse the date string into a NaiveDateTime
    let converted_date = NaiveDateTime::parse_from_str(max_date, YEAR_MONTH_DATE)
        .map_err(|_| UtilError::DateError)?;

    // Replace hour, minute, and second to get the max values for the date
    let max_date = converted_date
        .with_hour(23)
        .unwrap()
        .with_minute(59)
        .unwrap()
        .with_second(59)
        .unwrap();

    // Convert NaiveDateTime to timestamp in microseconds
    let timestamp = max_date.and_utc().timestamp() * 1_000_000;

    Ok(timestamp)
}

pub fn get_utc_date() -> String {
    chrono::Utc::now().format("%Y-%m-%d").to_string()
}

pub fn get_utc_timestamp() -> i64 {
    chrono::Utc::now().timestamp()
}

pub fn get_utc_datetime() -> NaiveDateTime {
    chrono::Utc::now().naive_utc()
}

#[cfg(test)]
mod tests {
    use crate::clean_string;

    #[test]
    fn test_remove_punctuation() {
        let text = "Hello?";
        let expected = "hello";
        assert_eq!(clean_string(text), expected);

        let text = "Hel#lo?";
        let expected = "hello";
        assert_eq!(clean_string(text), expected);

        let text = "Hello_World!";
        let expected = "hello-world";
        assert_eq!(clean_string(text), expected);
    }

    #[test]
    fn test_name_repository_validation() {
        let name = "hello";
        let repository = "world";

        assert!(super::validate_name_repository_pattern(name, repository).is_ok());

        let name = "llllllllllllllllloooooooooooooonnnnnnnnnnnnnnggggggggggggggg";
        let repository = "nnnnnnnnnnnnnaaaaaaaaaaaaaaammmmmmmmmmmmmeeeeeeeeeee";

        assert!(super::validate_name_repository_pattern(name, repository).is_err());
    }
}
