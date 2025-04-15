use anyhow::{Context, Result};
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
enum Platform {
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
pub fn start_ui(version: &str) -> Result<(), CliError> {
    let platform = detect_platform()?;
    let cache_dir = get_cache_dir()?;
    let binary_path = cache_dir.join(format!("opsml-server-v{}", version));

    if !binary_path.exists() {
        download_binary(&platform, version, &cache_dir)?;
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
fn download_binary(platform: &Platform, version: &str, cache_dir: &Path) -> Result<(), CliError> {
    // standardize naming
    let archive_name = match platform {
        Platform::Windows => "opsml-server-x86_64-windows.zip".to_string(),
        Platform::MacOS(arch) => format!("opsml-server-{}-darwin.zip", arch),
        Platform::Linux(arch) => format!("opsml-server-{}-linux-gnu.tar.gz", arch),
    };

    let url = format!(
        "https://github.com/{}/releases/download/v{}/{}",
        GITHUB_REPO, version, archive_name
    );

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
            if file_name.starts_with(prefix) && file_name != current_binary {
                fs::remove_file(&path).map_err(|e| CliError::RemoveFileError(e))?;
            }
        }
    }

    Ok(())
}
