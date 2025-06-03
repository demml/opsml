use opsml_types::cards::MemoryMetricLogger;
// Default sizes in bytes
pub const DEFAULT_UPLOAD_CHUNK_SIZE: usize = 1024 * 1024 * 32; // 32 MB default
pub const DEFAULT_DOWNLOAD_CHUNK_SIZE: usize = 1024 * 1024 * 32; // 32 MB default
pub const MIN_CHUNK_SIZE: usize = 1024 * 1024 * 8; // 8 MB minimum
pub const MAX_CHUNK_SIZE: usize = 1024 * 1024 * 64; // 64 MB maximum
pub const MAX_FILE_SIZE: usize = 1024 * 1024 * 1024 * 50; // 50 GB maximum

/// Helper function that is used to dynamically set the upload chunk size based on the file size and available memory
/// # Arguments
/// * `file_size` - The size of the file being uploaded
/// * `available_memory` - The available memory in bytes, if None, it will use the system's available memory
/// # Returns
/// * `usize` - The optimal chunk size in bytes
pub fn set_upload_chunk_size(file_size: usize, available_memory: Option<usize>) -> usize {
    let mut optimal_size = DEFAULT_UPLOAD_CHUNK_SIZE;
    let available_memory = available_memory
        .unwrap_or(MemoryMetricLogger::new().get_metrics().available_memory as usize);

    if file_size < 1024 * 1024 * 100 {
        // Under 100MB
        optimal_size = MIN_CHUNK_SIZE;
    } else if file_size > 1024 * 1024 * 1024 {
        // Over 1GB
        optimal_size = MAX_CHUNK_SIZE;
    }

    // get 5% of available memory (trying to be conservative here)
    let memory_limit = (available_memory as f64 * 0.05) as usize;

    optimal_size = optimal_size
        .min(memory_limit)
        .max(MIN_CHUNK_SIZE)
        .min(MAX_CHUNK_SIZE);

    tracing::info!(
        "Set upload chunk size to {} bytes ({} MB)",
        optimal_size,
        optimal_size as f64 / (1024.0 * 1024.0)
    );

    optimal_size
}

/// Helper function that is used to dynamically set the download chunk size based on the file size and available memory
/// # Arguments
/// * `file_size` - The size of the file being downloaded
/// * `available_memory` - The available memory in bytes, if None, it will use the system's available memory
/// # Returns
/// * `usize` - The optimal chunk size in bytes
pub fn set_download_chunk_size(file_size: usize, available_memory: Option<usize>) -> usize {
    let mut optimal_size = DEFAULT_DOWNLOAD_CHUNK_SIZE;
    let available_memory = available_memory
        .unwrap_or(MemoryMetricLogger::new().get_metrics().available_memory as usize);

    if file_size < 1024 * 1024 * 100 {
        // Under 100MB
        optimal_size = MIN_CHUNK_SIZE;
    } else if file_size > 1024 * 1024 * 1024 * 2 {
        // Over 2GB
        optimal_size = MAX_CHUNK_SIZE;
    }

    // using a higher threshold for download chunk size
    let memory_limit = (available_memory as f64 * 0.10) as usize;

    optimal_size = optimal_size
        .min(memory_limit)
        .max(MIN_CHUNK_SIZE)
        .min(MAX_CHUNK_SIZE);

    tracing::info!(
        "Set download chunk size to {} bytes ({:.2} MB)",
        optimal_size,
        optimal_size as f64 / (1024.0 * 1024.0)
    );

    optimal_size
}

//test
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_set_upload_chunk_size() {
        let test_memory_size = 8 * 1024 * 1024 * 1024; // 8 GB for testing

        // Test with a small file size (50 mb)
        let upload_size = set_upload_chunk_size(1024 * 1024 * 50, Some(test_memory_size));
        assert_eq!(upload_size, MIN_CHUNK_SIZE);

        // Test with a large file size (2 GB)
        let upload_size = set_upload_chunk_size(1024 * 1024 * 2000, Some(test_memory_size));
        assert_eq!(upload_size, MAX_CHUNK_SIZE);

        // Test with a medium file size (500 mb)
        let upload_size = set_upload_chunk_size(1024 * 1024 * 500, Some(test_memory_size));
        assert!(upload_size >= MIN_CHUNK_SIZE && upload_size <= MAX_CHUNK_SIZE);
    }

    #[test]
    fn test_set_download_chunk_size() {
        let test_memory_size = 8 * 1024 * 1024 * 1024; // 8 GB for testing

        // Test with a small file size (50 mb)
        let download_size = set_download_chunk_size(1024 * 1024 * 50, Some(test_memory_size));
        assert_eq!(download_size, MIN_CHUNK_SIZE);

        // Test with a large file size (3 GB)
        let download_size = set_download_chunk_size(1024 * 1024 * 1024 * 3, Some(test_memory_size));
        assert_eq!(download_size, MAX_CHUNK_SIZE);

        // Test with a medium file size (500 mb)
        let download_size = set_download_chunk_size(1024 * 1024 * 500, Some(test_memory_size));
        assert!(download_size >= MIN_CHUNK_SIZE && download_size <= MAX_CHUNK_SIZE);
    }
}
