use anyhow::Result;
use opsml_error::CliError;
use reqwest;
use std::{
    env, fs,
    path::{Path, PathBuf},
    process::Command,
};

const GITHUB_REPO: &str = "demml/opsml";
const CACHE_DIR: &str = "opsml-cache";

#[derive(Debug)]
pub enum Platform {
    Windows,

    // needs to hold x86_64 or aarch64
    MacOS(String),

    // needs to hold x86_64 or aarch64
    Linux(String),
}

///  Start the OpsML UI. Attempts to load the current UI version from the cache
/// if it exists. If not, it downloads the latest version from the GitHub
/// repository and starts the UI.
///
/// # Arguments
/// * `version` - The version of the OpsML UI to start. If not provided, the latest version will be used.
pub fn start_ui(version: &str, artifact_url: Option<String>) -> Result<(), CliError> {
    let platform = detect_platform()?;
    let cache_dir = get_cache_dir()?;
    let binary_path = cache_dir.join(format!("opsml-server-v{}", version));

    if !binary_path.exists() {
        download_binary(&platform, version, &cache_dir, artifact_url)?;
        cleanup_old_binaries(&cache_dir, version, &platform)?;
    }

    execute_binary(&binary_path)?;
    Ok(())
}

/// Attempts to detect the current platform (Windows, MacOS, or Linux) and architecture (x86_64 or aarch64).
fn detect_platform() -> Result<Platform, CliError> {
    let os = env::consts::OS;
    let arch = env::consts::ARCH;

    match (os, arch) {
        ("windows", _) => Ok(Platform::Windows),
        ("macos", "x86_64") => Ok(Platform::MacOS("x86_64".to_string())),
        ("macos", "aarch64") => Ok(Platform::MacOS("aarch64".to_string())),
        ("linux", "x86_64") => Ok(Platform::Linux("x86_64".to_string())),
        ("linux", "aarch64") => Ok(Platform::Linux("aarch64".to_string())),
        _ => Err(CliError::UnsupportedPlatform(
            os.to_string(),
            arch.to_string(),
        )),
    }
}

/// Gets/Creates a cache directory for OpsML
fn get_cache_dir() -> Result<PathBuf, CliError> {
    let home = dirs::home_dir().ok_or(CliError::HomeDirError)?;
    let cache_dir = home.join(CACHE_DIR);

    if !cache_dir.exists() {
        fs::create_dir_all(&cache_dir).map_err(|e| CliError::CreateCacheDirError(e))?;
    }

    Ok(cache_dir)
}

/// Download a specific OpsML UI binary for the current platform and version
///
/// # Arguments
/// * `platform` - The platform to download the binary for
/// * `version` - The version of the binary to download
/// * `cache_dir` - The directory to cache the downloaded binary
///
/// # Returns
/// A Result indicating success or failure
fn download_binary(
    platform: &Platform,
    version: &str,
    cache_dir: &Path,
    artifact_url: Option<String>,
) -> Result<(), CliError> {
    // standardize naming
    let archive_name = match platform {
        Platform::Windows => "opsml-server-x86_64-windows.zip".to_string(),
        Platform::MacOS(arch) => format!("opsml-server-{}-darwin.zip", arch),
        Platform::Linux(arch) => format!("opsml-server-{}-linux-gnu.tar.gz", arch),
    };

    let url = artifact_url.unwrap_or(format!(
        "https://github.com/{}/releases/download/v{}/{}",
        GITHUB_REPO, version, archive_name
    ));

    let response =
        reqwest::blocking::get(&url).map_err(|e| CliError::DownloadBinaryError(e.to_string()))?;
    let archive_path = cache_dir.join(&archive_name);

    let bytes = response
        .bytes()
        .map_err(|e| CliError::DownloadBinaryError(e.to_string()))?;
    fs::write(&archive_path, bytes).map_err(|e| CliError::WriteBinaryError(e.to_string()))?;

    match platform {
        Platform::Windows | Platform::MacOS(_) => {
            let reader = fs::File::open(&archive_path)
                .map_err(|e| CliError::ArchiveOpenError(e.to_string()))?;
            let mut archive = zip::ZipArchive::new(reader)
                .map_err(|e| CliError::ArchiveOpenError(e.to_string()))?;

            archive
                .extract(cache_dir)
                .map_err(|e| CliError::ArchiveExtractionError(e.to_string()))?;
        }
        Platform::Linux(_) => {
            #[cfg(target_os = "linux")]
            {
                let tar_gz = fs::File::open(&archive_path)?;
                let tar = flate2::read::GzDecoder::new(tar_gz);
                let mut archive = tar::Archive::new(tar);
                archive
                    .unpack(cache_dir)
                    .map_err(|e| CliError::ArchiveExtractionError(e.to_string()))?;
            }
            #[cfg(not(target_os = "linux"))]
            {
                return Err(CliError::ArchiveExtractionError(
                    "Could not extract UI archive due to unsupported platform".to_string(),
                ));
            }
        }
    }

    let expected_binary_path = cache_dir.join(format!(
        "opsml-server-v{}{}",
        version,
        match platform {
            Platform::Windows => ".exe",
            _ => "",
        }
    ));

    let extracted_binary_name = match platform {
        Platform::Windows => "opsml-server.exe",
        Platform::MacOS(_) | Platform::Linux(_) => "opsml-server",
    };

    let extracted_path = cache_dir.join(extracted_binary_name);
    if !extracted_path.exists() {
        return Err(CliError::BinaryNotFound);
    } else {
        // rename the extracted binary to the versioned name while preserving the .exe extension for Windows
        fs::rename(&extracted_path, &expected_binary_path)
            .map_err(|e| CliError::RenameBinaryError(e))?;
    }

    // Clean up archive
    fs::remove_file(archive_path).map_err(|e| {
        CliError::RemoveArchiveError(format!("Failed to remove archive: {}", e.to_string()))
    })?;

    Ok(())
}

///// Execute the OpsML UI binary
///
/// # Arguments
/// * `binary_path` - The path to the OpsML UI binary
///
/// # Returns
/// A Result indicating success or failure
///
/// # Errors
/// * `CliError::BinaryExecutionError` - If the binary execution fails
fn execute_binary(binary_path: &Path) -> Result<(), CliError> {
    let mut child_process = Command::new(binary_path).spawn().map_err(|e| {
        CliError::BinaryExecutionError(format!("Failed to spawn child process: {}", e.to_string()))
    })?;

    // Wait for the process to finish
    let status = child_process.wait().map_err(|e| {
        CliError::BinaryExecutionError(format!(
            "Failed to wait for child process: {}",
            e.to_string()
        ))
    })?;

    if !status.success() {
        return Err(CliError::BinaryExecutionError(
            "Failed to start the UI".to_string(),
        ));
    }

    Ok(())
}

/// Cleans up old binary versions from the cache directory
/// Keeps only the current version
///
/// # Arguments
/// * `cache_dir` - The cache directory containing the binaries
/// * `current_version` - The version to keep
/// * `platform` - The current platform to determine file extension
fn cleanup_old_binaries(
    cache_dir: &Path,
    current_version: &str,
    platform: &Platform,
) -> Result<(), CliError> {
    let extension = match platform {
        Platform::Windows => ".exe",
        _ => "",
    };

    let prefix = "opsml-server-v";
    let current_binary = format!("{}{}{}", prefix, current_version, extension);

    for entry in fs::read_dir(cache_dir).map_err(|e| CliError::ReadError(e))? {
        let entry = entry.map_err(|e| CliError::ReadError(e))?;
        let path = entry.path();

        if let Some(file_name) = path.file_name().and_then(|f| f.to_str()) {
            // Check if it's a server binary and not the current version
            if file_name.starts_with(prefix)
                && file_name.ends_with(extension)
                && file_name != current_binary
            {
                fs::remove_file(&path).map_err(|e| CliError::RemoveFileError(e))?;
            }
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use mockito::{Server, ServerGuard};
    use std::io::Write;
    use tempfile::TempDir;
    use zip::write::FileOptions;

    #[cfg(target_os = "linux")]
    use flate2::{write::GzEncoder, Compression};
    #[cfg(target_os = "linux")]
    use tar::Header;

    struct MockServer {
        server: ServerGuard,
        url: String,
    }
    impl MockServer {
        fn new() -> Self {
            let server = Server::new();
            let url = server.url().to_string();
            MockServer { server, url }
        }

        #[cfg(target_os = "windows")]
        fn mock_windows_binary(&mut self, version: &str) -> mockito::Mock {
            // Create a proper zip archive in memory for Windows
            let mut buffer = Vec::new();
            {
                let mut zip = zip::ZipWriter::new(std::io::Cursor::new(&mut buffer));
                let options: FileOptions<'_, ()> = FileOptions::default()
                    .compression_method(zip::CompressionMethod::Stored)
                    .unix_permissions(0o755);

                // Add the binary file (with .exe) to the archive
                zip.start_file("opsml-server.exe", options).unwrap();
                zip.write_all(b"mock windows binary content").unwrap();
                zip.finish().unwrap();
            }

            // Construct the path that download_binary will request
            let arch = "x86_64"; // Windows is typically x86_64 for this naming convention
            let archive_name = format!("opsml-server-{}-windows.zip", arch);
            let mock_path = format!("/releases/download/v{}/{}", version, archive_name);

            self.server
                .mock("GET", mock_path.as_str())
                .with_status(200)
                .with_body(buffer)
                .create()
        }

        fn mock_macos_binary(&mut self, version: &str, arch: &str) -> mockito::Mock {
            // Create a proper zip archive in memory
            let mut buffer = Vec::new();
            {
                let mut zip = zip::ZipWriter::new(std::io::Cursor::new(&mut buffer));
                let options: FileOptions<'_, ()> = FileOptions::default()
                    .compression_method(zip::CompressionMethod::Stored)
                    .unix_permissions(0o755);

                // Add the binary file to the archive
                zip.start_file("opsml-server", options).unwrap();
                zip.write_all(b"mock macos binary content").unwrap();
                zip.finish().unwrap();
            }

            // Construct the path that download_binary will request
            let archive_name = format!("opsml-server-{}-darwin.zip", arch);
            // Mock the specific path that will be requested
            let mock_path = format!("/releases/download/v{}/{}", version, archive_name);

            self.server
                .mock("GET", mock_path.as_str()) // Mock the full path
                .with_status(200)
                .with_body(buffer)
                .create()
        }

        #[cfg(target_os = "linux")]
        fn mock_linux_binary(&mut self, version: &str, arch: &str) -> mockito::Mock {
            // Create a proper tar.gz archive in memory for Linux
            let mut buffer = Vec::new();
            {
                let encoder = GzEncoder::new(&mut buffer, Compression::default());
                let mut tar_builder = tar::Builder::new(encoder);

                let binary_content = b"mock linux binary content";
                let mut header = Header::new_gnu();
                header.set_path("opsml-server").unwrap();
                header.set_size(binary_content.len() as u64);
                header.set_mode(0o755); // Executable permissions
                header.set_cksum(); // Recalculate checksum

                tar_builder
                    .append(&header, binary_content as &[u8])
                    .unwrap();
                // Finish writing the tar archive
                let gz_encoder = tar_builder.into_inner().unwrap();
                // Finish writing the gzip stream
                gz_encoder.finish().unwrap();
            }

            // Construct the path that download_binary will request
            let archive_name = format!("opsml-server-{}-linux-gnu.tar.gz", arch);
            let mock_path = format!("/releases/download/v{}/{}", version, archive_name);

            self.server
                .mock("GET", mock_path.as_str())
                .with_status(200)
                .with_body(buffer)
                .create()
        }
    }

    #[test]
    fn test_detect_platform() {
        let platform = detect_platform().unwrap();

        match env::consts::OS {
            "windows" => assert!(matches!(platform, Platform::Windows)),
            "macos" => match env::consts::ARCH {
                "x86_64" => assert!(matches!(platform, Platform::MacOS(ref s) if s == "x86_64")),
                "aarch64" => assert!(matches!(platform, Platform::MacOS(ref s) if s == "aarch64")),
                _ => panic!("Unexpected architecture"),
            },
            "linux" => match env::consts::ARCH {
                "x86_64" => assert!(matches!(platform, Platform::Linux(ref s) if s == "x86_64")),
                "aarch64" => assert!(matches!(platform, Platform::Linux(ref s) if s == "aarch64")),
                _ => panic!("Unexpected architecture"),
            },
            _ => panic!("Unexpected OS"),
        }
    }

    #[test]
    fn test_get_cache_dir() {
        let cache_dir = get_cache_dir().unwrap();
        assert!(cache_dir.ends_with(CACHE_DIR));
        assert!(cache_dir.exists());
    }

    #[test]
    #[cfg(target_os = "macos")]
    fn test_download_binary_macos() -> Result<(), Box<dyn std::error::Error>> {
        let mut mock_server = MockServer::new();
        let version = "0.1.0";
        let arch = "x86_64";
        let platform = Platform::MacOS(arch.to_string());
        let _mock_reqwest = mock_server.mock_macos_binary(version, arch); // Pass version and arch

        let temp_cache_dir = TempDir::new()?;
        let cache_path = temp_cache_dir.path();

        let archive_name = format!("opsml-server-{}-darwin.zip", arch);
        let full_mock_url = format!(
            "{}/releases/download/v{}/{}",
            mock_server.url, // Base URL from mockito
            version,
            archive_name
        );

        // Call download_binary directly for more focused testing
        download_binary(&platform, version, cache_path, Some(full_mock_url))?;

        // Assert that the binary was extracted and renamed correctly
        let expected_binary_path = cache_path.join(format!("opsml-server-v{}", version));
        assert!(
            expected_binary_path.exists(),
            "Expected binary file does not exist"
        );

        // Assert that the archive file was removed
        let archive_path = cache_path.join(archive_name);
        assert!(!archive_path.exists(), "Archive file was not cleaned up");

        Ok(())
    }

    #[test]
    #[cfg(target_os = "windows")] // Only run this test on Windows
    fn test_download_binary_windows() -> Result<(), Box<dyn std::error::Error>> {
        let mut mock_server = MockServer::new();
        let version = "0.2.0"; // Use a different version for clarity
        let platform = Platform::Windows;
        let _mock_reqwest = mock_server.mock_windows_binary(version);

        let temp_cache_dir = TempDir::new()?;
        let cache_path = temp_cache_dir.path();

        let arch = "x86_64"; // Assume x86_64 for windows archive name
        let archive_name = format!("opsml-server-{}-windows.zip", arch);
        let full_mock_url = format!(
            "{}/releases/download/v{}/{}",
            mock_server.url, version, archive_name
        );

        download_binary(&platform, version, cache_path, Some(full_mock_url))?;

        // Windows binaries have .exe extension
        let expected_binary_path = cache_path.join(format!("opsml-server-v{}.exe", version));
        assert!(
            expected_binary_path.exists(),
            "Expected Windows binary file does not exist: {:?}",
            expected_binary_path
        );

        let archive_path = cache_path.join(archive_name);
        assert!(
            !archive_path.exists(),
            "Windows archive file was not cleaned up"
        );

        Ok(())
    }

    #[test]
    #[cfg(target_os = "linux")] // Only run this test on Linux
    fn test_download_binary_linux() -> Result<(), Box<dyn std::error::Error>> {
        let mut mock_server = MockServer::new();
        let version = "0.3.0"; // Use a different version for clarity
                               // Determine arch based on the actual test environment
        let arch = if cfg!(target_arch = "aarch64") {
            "aarch64"
        } else {
            "x86_64"
        };
        let platform = Platform::Linux(arch.to_string());
        let _mock_reqwest = mock_server.mock_linux_binary(version, arch);

        let temp_cache_dir = TempDir::new()?;
        let cache_path = temp_cache_dir.path();

        let archive_name = format!("opsml-server-{}-linux-gnu.tar.gz", arch);
        let full_mock_url = format!(
            "{}/releases/download/v{}/{}",
            mock_server.url, version, archive_name
        );

        // download_binary contains the cfg logic for extraction, so we call it directly
        download_binary(&platform, version, cache_path, Some(full_mock_url))?;

        // Linux binaries have no extension in this setup
        let expected_binary_path = cache_path.join(format!("opsml-server-v{}", version));
        assert!(
            expected_binary_path.exists(),
            "Expected Linux binary file does not exist: {:?}",
            expected_binary_path
        );

        let archive_path = cache_path.join(archive_name);
        assert!(
            !archive_path.exists(),
            "Linux archive file was not cleaned up"
        );

        Ok(())
    }

    #[test]
    fn test_cleanup_old_binaries() -> Result<(), Box<dyn std::error::Error>> {
        let temp_dir = TempDir::new()?;
        let cache_path = temp_dir.path();
        let current_version = "1.1.0";
        let platform = Platform::MacOS("aarch64".to_string()); // Example platform
        let extension = ""; // No extension for MacOS/Linux
        let prefix = "opsml-server-v";

        // Files to create
        let current_binary_name = format!("{}{}{}", prefix, current_version, extension);
        let old_binary_name_1 = format!("{}{}{}", prefix, "1.0.0", extension);
        let old_binary_name_2 = format!("{}{}{}", prefix, "0.9.0", extension);
        let unrelated_file_name = "some-other-file.txt";

        let current_binary_path = cache_path.join(&current_binary_name);
        let old_binary_path_1 = cache_path.join(&old_binary_name_1);
        let old_binary_path_2 = cache_path.join(&old_binary_name_2);
        let unrelated_file_path = cache_path.join(unrelated_file_name);

        // Create dummy files
        fs::write(&current_binary_path, "current binary data")?;
        fs::write(&old_binary_path_1, "old binary data 1")?;
        fs::write(&old_binary_path_2, "old binary data 2")?;
        fs::write(&unrelated_file_path, "some text data")?;

        // Run the cleanup function
        cleanup_old_binaries(cache_path, current_version, &platform)?;

        // Assertions
        assert!(
            current_binary_path.exists(),
            "Current binary should not be deleted"
        );
        assert!(
            !old_binary_path_1.exists(),
            "Old binary 1 should be deleted"
        );
        assert!(
            !old_binary_path_2.exists(),
            "Old binary 2 should be deleted"
        );
        assert!(
            unrelated_file_path.exists(),
            "Unrelated file should not be deleted"
        );

        Ok(())
    }

    #[test]
    fn test_cleanup_old_binaries_windows() -> Result<(), Box<dyn std::error::Error>> {
        let temp_dir = TempDir::new()?;
        let cache_path = temp_dir.path();
        let current_version = "2.0.0";
        let platform = Platform::Windows;
        let extension = ".exe"; // Extension for Windows
        let prefix = "opsml-server-v";

        // Files to create
        let current_binary_name = format!("{}{}{}", prefix, current_version, extension);
        let old_binary_name_1 = format!("{}{}{}", prefix, "1.9.0", extension);
        let old_binary_name_no_ext = format!("{}{}", prefix, "1.8.0"); // Should not match prefix logic

        let current_binary_path = cache_path.join(&current_binary_name);
        let old_binary_path_1 = cache_path.join(&old_binary_name_1);
        let old_binary_no_ext_path = cache_path.join(&old_binary_name_no_ext);

        // Create dummy files
        fs::write(&current_binary_path, "current windows binary data")?;
        fs::write(&old_binary_path_1, "old windows binary data 1")?;
        fs::write(&old_binary_no_ext_path, "old windows binary data no ext")?;

        // Run the cleanup function
        cleanup_old_binaries(cache_path, current_version, &platform)?;

        // Assertions
        assert!(
            current_binary_path.exists(),
            "Current windows binary should not be deleted"
        );
        assert!(
            !old_binary_path_1.exists(),
            "Old windows binary 1 should be deleted"
        );
        assert!(
            old_binary_no_ext_path.exists(),
            "Old windows binary without correct extension should not be deleted"
        );

        Ok(())
    }
}
