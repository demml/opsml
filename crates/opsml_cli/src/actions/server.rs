use opsml_error::CliError;
use std::path::PathBuf;
use std::process::Command;

fn get_server_path() -> Result<PathBuf, CliError> {
    let manifest_dir = env!("CARGO_MANIFEST_DIR");
    let server_path = PathBuf::from(manifest_dir)
        .join("src")
        .join("server")
        .join("opsml-server");

    if server_path.exists() {
        Ok(server_path)
    } else {
        Err(CliError::Error("Server binary not found".to_string()))
    }
}

fn start_server() -> Result<(), CliError> {
    let server_path = get_server_path()?;
    let output = Command::new(server_path)
        .output()
        .map_err(|e| CliError::Error(format!("{}", e)))?;

    if output.status.success() {
        Ok(())
    } else {
        Err(CliError::Error(format!(
            "Server failed to start: {}",
            String::from_utf8_lossy(&output.stderr)
        )))
    }
}
