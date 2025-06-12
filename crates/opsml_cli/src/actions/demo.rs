use crate::error::CliError;
use std::process::{Command, Stdio};

const PYTHON_DEMO_CODE: &str = include_str!("assets/demo.py");

pub fn run_python_code() -> Result<(), CliError> {
    // Prefer python3, fallback to python
    let python = if Command::new("python3").arg("--version").output().is_ok() {
        "python3"
    } else {
        "python"
    };

    let mut cmd = Command::new(python);
    cmd.arg("-c").arg(PYTHON_DEMO_CODE);

    cmd.stdout(Stdio::inherit());
    cmd.stderr(Stdio::inherit());

    let status = cmd.status().map_err(CliError::IoError)?;
    if status.success() {
        Ok(())
    } else {
        Err(CliError::FailedToRunDemo)
    }
}
