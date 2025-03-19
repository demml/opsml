use std::path::PathBuf;

use opsml_error::error::{OpsmlError, UtilError};
use pyo3::prelude::*;
use std::path::Path;
use walkdir::WalkDir;

#[pyclass]
pub struct FileUtils;

#[pymethods]
impl FileUtils {
    #[staticmethod]
    pub fn open_file(filepath: &str) -> PyResult<String> {
        // get file name of path
        let path = FileUtils::find_path_to_file(filepath)?;
        std::fs::read_to_string(path).map_err(OpsmlError::new_err)
    }

    #[staticmethod]
    pub fn find_path_to_file(filepath: &str) -> PyResult<String> {
        // get file name of path
        let path = std::path::Path::new(&filepath)
            .file_name()
            .ok_or_else(|| OpsmlError::new_err("Invalid file path"))?
            .to_str()
            .ok_or_else(|| OpsmlError::new_err("Invalid file path"))?;

        let current_dir = std::env::current_dir().map_err(OpsmlError::new_err)?;
        // recursively search for file in current directory
        for entry in WalkDir::new(current_dir) {
            let entry = entry.map_err(|e| OpsmlError::new_err(e.to_string()))?;
            if entry.file_type().is_file() && entry.file_name().to_string_lossy() == path {
                // return the full path to the file
                return Ok(entry.path().to_str().unwrap().to_string());
            }
        }
        // raise error if file not found
        let msg = format!("File not found: {filepath}");
        Err(OpsmlError::new_err(msg))
    }
}

impl FileUtils {
    pub fn list_files(path: &Path) -> Result<Vec<PathBuf>, UtilError> {
        let mut files = Vec::new();
        for entry in WalkDir::new(path) {
            let entry =
                entry.map_err(|e| UtilError::Error(format!("Unable to read directory: {e}")))?;
            if entry.file_type().is_file() {
                files.push(entry.path().to_path_buf());
            }
        }
        Ok(files)
    }

    pub fn get_chunk_count(path: &PathBuf, chunk_size: u64) -> Result<(u64, u64, u64), UtilError> {
        let file_size = std::fs::metadata(path)
            .map_err(|e| UtilError::Error(format!("Unable to read file metadata: {e}")))?
            .len();

        let chunk_size = std::cmp::min(file_size, chunk_size);

        let mut chunk_count = (file_size / chunk_size) + 1;
        let mut size_of_last_chunk = file_size % chunk_size;

        // if the last chunk is empty, reduce the number of parts
        if size_of_last_chunk == 0 {
            size_of_last_chunk = chunk_size;
            chunk_count -= 1;
        }

        Ok((chunk_count, size_of_last_chunk, chunk_size))
    }
}
