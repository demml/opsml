use crate::error::UiError;
use anyhow::Result;
use reqwest;
use std::process::Child;
use std::{
    env, fs,
    path::{Path, PathBuf},
    process::Command,
};
use sysinfo::{Pid, System};

const GITHUB_REPO: &str = "demml/opsml";
const CACHE_DIR: &str = ".opsml-cache";
const PID_FILE: &str = "opsml-server.pid";

pub fn save_process_id(process: &Child) -> Result<(), UiError> {
    let pid_path = get_pid_file_path()?;
    fs::write(&pid_path, process.id().to_string()).map_err(UiError::ProcessIdWriteError)
}

fn get_pid_file_path() -> Result<PathBuf, UiError> {
    let cache_dir = get_cache_dir()?;
    Ok(cache_dir.join(PID_FILE))
}

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
pub fn start_ui(version: &str, artifact_url: Option<String>) -> Result<(), UiError> {
    let platform = detect_platform()?;
    let cache_dir = get_cache_dir()?;
    let binary_path = cache_dir.join(format!("opsml-server-v{version}"));

    if !binary_path.exists() {
        download_binary(&platform, version, &cache_dir, artifact_url)?;
        cleanup_old_binaries(&cache_dir, version, &platform)?;
    }

    execute_binary(&binary_path)?;
    Ok(())
}

pub fn stop_ui() -> Result<(), UiError> {
    let pid_path = get_pid_file_path()?;

    if !pid_path.exists() {
        return Err(UiError::NoRunningServer);
    }

    let pid_str = fs::read_to_string(&pid_path).map_err(UiError::ProcessIdReadError)?;

    let pid: usize = pid_str
        .trim()
        .parse()
        .map_err(UiError::ProcessIdParseError)?;

    let s = System::new_all();
    if let Some(process) = s.process(Pid::from(pid)) {
        println!("Stopping OpsML UI server (PID: {pid})");
        process
            .kill_and_wait()
            .map_err(|_| UiError::ProcessKillError(format!("{pid}")))?;
    }

    Ok(())
}

/// Attempts to detect the current platform (Windows, MacOS, or Linux) and architecture (x86_64 or aarch64).
fn detect_platform() -> Result<Platform, UiError> {
    let os = env::consts::OS;
    let arch = env::consts::ARCH;

    match (os, arch) {
        ("windows", _) => Ok(Platform::Windows),
        ("macos", "x86_64") => Ok(Platform::MacOS("x86_64".to_string())),
        ("macos", "aarch64") => Ok(Platform::MacOS("aarch64".to_string())),
        ("linux", "x86_64") => Ok(Platform::Linux("x86_64".to_string())),
        ("linux", "aarch64") => Ok(Platform::Linux("aarch64".to_string())),
        _ => Err(UiError::UnsupportedPlatformError(os, arch)),
    }
}

/// Gets/Creates a cache directory for OpsML
fn get_cache_dir() -> Result<PathBuf, UiError> {
    let home = dirs::home_dir().ok_or(UiError::HomeDirError)?;
    let cache_dir = home.join(CACHE_DIR);

    if !cache_dir.exists() {
        fs::create_dir_all(&cache_dir).map_err(UiError::CreateCacheDirError)?;
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
) -> Result<(), UiError> {
    // standardize naming
    let archive_name = match platform {
        Platform::Windows => "opsml-server-x86_64-windows.zip".to_string(),
        Platform::MacOS(arch) => format!("opsml-server-{arch}-darwin.zip"),
        Platform::Linux(arch) => format!("opsml-server-{arch}-linux-gnu.tar.gz"),
    };

    let url = artifact_url.unwrap_or(format!(
        "https://github.com/{GITHUB_REPO}/releases/download/v{version}/{archive_name}",
    ));

    let response = reqwest::blocking::get(&url).map_err(UiError::DownloadBinaryError)?;
    let archive_path = cache_dir.join(&archive_name);

    let bytes = response.bytes().map_err(UiError::DownloadBinaryError)?;
    fs::write(&archive_path, bytes).map_err(UiError::WriteBinaryError)?;

    match platform {
        Platform::Windows | Platform::MacOS(_) => {
            let reader = fs::File::open(&archive_path).map_err(UiError::ArchiveOpenError)?;
            let mut archive = zip::ZipArchive::new(reader).map_err(UiError::ArchiveZipError)?;

            archive
                .extract(cache_dir)
                .map_err(UiError::ZipArchiveExtractionError)?;
        }
        Platform::Linux(_) => {
            #[cfg(target_os = "linux")]
            {
                let tar_gz = fs::File::open(&archive_path).map_err(UiError::ArchiveOpenError)?;
                let tar = flate2::read::GzDecoder::new(tar_gz);
                let mut archive = tar::Archive::new(tar);
                archive
                    .unpack(cache_dir)
                    .map_err(UiError::ArchiveExtractionError)?;
            }
            #[cfg(not(target_os = "linux"))]
            {
                return Err(UiError::UnsupportedPlatformExtractionError);
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
        return Err(UiError::BinaryNotFound);
    } else {
        // rename the extracted binary to the versioned name while preserving the .exe extension for Windows
        fs::rename(&extracted_path, &expected_binary_path).map_err(UiError::RenameBinaryError)?;
    }

    // Clean up archive
    fs::remove_file(archive_path).map_err(UiError::RemoveArchiveError)?;

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
/// * `UiError::BinaryExecutionError` - If the binary execution fails
fn execute_binary(binary_path: &Path) -> Result<(), UiError> {
    let child_process = Command::new(binary_path)
        .spawn()
        .map_err(UiError::BinarySpawnError)?;

    // Save the process ID
    save_process_id(&child_process)?;

    let id = child_process.id();

    println!("Started opsml-ui server (PID: {id})");

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
) -> Result<(), UiError> {
    let extension = match platform {
        Platform::Windows => ".exe",
        _ => "",
    };

    let prefix = "opsml-server-v";
    let current_binary = format!("{prefix}{current_version}{extension}");

    for entry in fs::read_dir(cache_dir).map_err(UiError::ReadError)? {
        let entry = entry.map_err(UiError::ReadError)?;
        let path = entry.path();

        if let Some(file_name) = path.file_name().and_then(|f| f.to_str()) {
            // Check if it's a server binary and not the current version
            if file_name.starts_with(prefix)
                && file_name.ends_with(extension)
                && file_name != current_binary
            {
                fs::remove_file(&path).map_err(UiError::RemoveFileError)?;
            }
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use mockito::{Server, ServerGuard};
    use tempfile::TempDir;

    #[cfg(any(target_os = "macos", target_os = "windows"))]
    use std::io::Write;

    #[cfg(any(target_os = "macos", target_os = "windows"))]
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

        #[cfg(target_os = "macos")]
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
            let archive_name = format!("opsml-server-{arch}-darwin.zip");
            // Mock the specific path that will be requested
            let mock_path = format!("/releases/download/v{version}/{archive_name}");

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
            let archive_name = format!("opsml-server-{arch}-linux-gnu.tar.gz");
            let mock_path = format!("/releases/download/v{version}/{archive_name}");

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

        let archive_name = format!("opsml-server-{arch}-darwin.zip");
        let full_mock_url = format!(
            "{}/releases/download/v{}/{}",
            mock_server.url, // Base URL from mockito
            version,
            archive_name
        );

        // Call download_binary directly for more focused testing
        download_binary(&platform, version, cache_path, Some(full_mock_url))?;

        // Assert that the binary was extracted and renamed correctly
        let expected_binary_path = cache_path.join(format!("opsml-server-v{version}"));
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

        let archive_name = format!("opsml-server-{arch}-linux-gnu.tar.gz");
        let full_mock_url = format!(
            "{}/releases/download/v{version}/{archive_name}",
            mock_server.url
        );

        // download_binary contains the cfg logic for extraction, so we call it directly
        download_binary(&platform, version, cache_path, Some(full_mock_url))?;

        // Linux binaries have no extension in this setup
        let expected_binary_path = cache_path.join(format!("opsml-server-v{version}"));
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
        let current_binary_name = format!("{prefix}{current_version}{extension}");
        let old_binary_name_1 = format!("{prefix}1.0.0{extension}");
        let old_binary_name_2 = format!("{prefix}0.9.0{extension}");
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
        let current_binary_name = format!("{prefix}{current_version}{extension}");
        let old_binary_name_1 = format!("{prefix}1.9.0{extension}");
        let old_binary_name_no_ext = format!("{prefix}1.8.0"); // Should not match prefix logic

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
