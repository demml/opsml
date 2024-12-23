use opsml_error::error::OpsmlError;
use pyo3::prelude::*;
use walkdir::WalkDir;

#[pyclass]
pub struct FileUtils;

#[pymethods]
impl FileUtils {
    #[staticmethod]
    pub fn find_filepath(filepath: &str) -> PyResult<String> {
        // get file name of path
        let path = std::path::Path::new(&filepath)
            .file_name()
            .unwrap()
            .to_str()
            .unwrap();

        let current_dir = std::env::current_dir().map_err(|e| OpsmlError::new_err(e))?;
        // recursively search for file in current directory
        for entry in WalkDir::new(current_dir) {
            let entry = entry.map_err(|e| OpsmlError::new_err(e.to_string()))?;
            if entry.file_type().is_file() && entry.file_name().to_string_lossy() == path {
                // open the file and read it to a string
                let file =
                    std::fs::read_to_string(entry.path()).map_err(|e| OpsmlError::new_err(e))?;

                return Ok(file);
            }
        }
        // raise error if file not found
        Err(OpsmlError::new_err("File not found"))
    }
}
