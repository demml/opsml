use std::path::PathBuf;

use crate::error::UtilError;
use std::path::Path;
use walkdir::WalkDir;

pub struct FileUtils;

impl FileUtils {
    pub fn open_file(filepath: &str) -> Result<String, UtilError> {
        // get file name of path
        let path = FileUtils::find_path_to_file(filepath)?;
        Ok(std::fs::read_to_string(path)?)
    }

    pub fn find_path_to_file(filepath: &str) -> Result<String, UtilError> {
        // get file name of path
        let path = std::path::Path::new(&filepath)
            .file_name()
            .ok_or(UtilError::FilePathNotFoundError)?
            .to_str()
            .ok_or(UtilError::FilePathNotFoundError)?;

        let current_dir = std::env::current_dir()?;
        // recursively search for file in current directory
        for entry in WalkDir::new(current_dir) {
            let entry = entry?;
            if entry.file_type().is_file() && entry.file_name().to_string_lossy() == path {
                // return the full path to the file
                return Ok(entry.path().to_str().unwrap().to_string());
            }
        }

        Err(UtilError::FileNotFoundError)
    }
}

impl FileUtils {
    pub fn list_files(path: &Path) -> Result<Vec<PathBuf>, UtilError> {
        let mut files = Vec::new();
        for entry in WalkDir::new(path) {
            let entry = entry?;
            if entry.file_type().is_file() {
                files.push(entry.path().to_path_buf());
            }
        }
        Ok(files)
    }

    pub fn get_chunk_count(file_size: u64, chunk_size: u64) -> Result<ChunkParts, UtilError> {
        let chunk_size = std::cmp::min(file_size, chunk_size);

        let mut chunk_count = (file_size / chunk_size) + 1;
        let mut size_of_last_chunk = file_size % chunk_size;

        // if the last chunk is empty, reduce the number of parts
        if size_of_last_chunk == 0 {
            size_of_last_chunk = chunk_size;
            chunk_count -= 1;
        }

        Ok(ChunkParts {
            chunk_count,
            size_of_last_chunk,
            chunk_size,
        })
    }
}

pub struct ChunkParts {
    pub chunk_count: u64,
    pub size_of_last_chunk: u64,
    pub chunk_size: u64,
}
