use crate::error::PyProjectTomlError;
use opsml_types::RegistryType;
use serde::{Deserialize, Serialize, de::IntoDeserializer};
use std::fs;
use std::path::Path;
use std::str::FromStr;
use toml_edit::{ArrayOfTables, DocumentMut, Item, Table, value};

#[derive(Debug, Serialize, Deserialize)]
pub struct LockArtifact {
    pub space: String,
    pub name: String,
    pub version: String,
    pub uid: String,
    pub registry_type: RegistryType,
    pub write_dir: String,
}

/// LockFile struct to hold the lock entries
#[derive(Debug, Serialize, Deserialize)]
pub struct LockFile {
    // Each entry is considered a service
    pub artifact: Vec<LockArtifact>,
}

impl LockFile {
    /// Iterate over entries and create a lock file
    ///
    /// # Arguments
    /// * `root_path` - Optional path to write the lockfile
    ///
    pub fn write(&self, root_path: &Path) -> Result<(), PyProjectTomlError> {
        let mut doc = DocumentMut::new();
        doc.insert("version", value(opsml_version::version()));
        let mut artifacts = ArrayOfTables::new();

        // Create entries for each service
        for artifact in &self.artifact {
            let mut table = Table::new();
            table["space"] = Item::Value(artifact.space.clone().into());
            table["name"] = Item::Value(artifact.name.clone().into());
            table["version"] = Item::Value(artifact.version.clone().into());
            table["uid"] = Item::Value(artifact.uid.clone().into());
            table["write_dir"] = Item::Value(artifact.write_dir.clone().into());
            table["registry_type"] = Item::Value(artifact.registry_type.to_string().into());
            artifacts.push(table);
        }

        doc.insert("artifact", Item::ArrayOfTables(artifacts));

        let lock_path = root_path.join("opsml.lock");

        fs::write(lock_path, doc.to_string()).map_err(PyProjectTomlError::FailedToLockFile)?;

        Ok(())
    }

    /// Read the lock file and deserialize it
    ///
    /// # Arguments
    /// * `path` - Path to the lock file
    ///
    /// # Returns
    /// Result<Self, PyProjectTomlError>
    ///
    /// # Errors
    /// PyProjectTomlError if:
    /// * The lock file cannot be read
    /// * The lock file cannot be parsed
    /// * The lock file cannot be deserialized
    pub fn read(path: &Path) -> Result<Self, PyProjectTomlError> {
        let lock_path = path.join("opsml.lock");
        let content =
            fs::read_to_string(lock_path).map_err(PyProjectTomlError::FailedToReadLockFile)?;

        let lockfile: toml_edit::DocumentMut =
            toml_edit::DocumentMut::from_str(&content).map_err(PyProjectTomlError::ParseError)?;
        //
        let lockfile = LockFile::deserialize(lockfile.into_deserializer())
            .map_err(PyProjectTomlError::TomlSchema)?;

        Ok(lockfile)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    fn create_test_lockfile() -> LockFile {
        LockFile {
            artifact: vec![
                LockArtifact {
                    space: "test-space".to_string(),
                    name: "test-artifact".to_string(),
                    version: "1.0.0".to_string(),
                    uid: "abc123".to_string(),
                    registry_type: RegistryType::Model,
                    write_dir: "artifacts".to_string(),
                },
                LockArtifact {
                    space: "test-space-2".to_string(),
                    name: "test-artifact-2".to_string(),
                    version: "2.0.0".to_string(),
                    uid: "def456".to_string(),
                    registry_type: RegistryType::Data,
                    write_dir: "artifacts".to_string(),
                },
            ],
        }
    }

    #[test]
    fn test_write_and_read_lockfile() {
        let temp_dir = TempDir::new().unwrap();
        let lock_file = create_test_lockfile();

        // Write the lock file
        lock_file.write(temp_dir.path()).unwrap();

        // Verify the file exists
        assert!(temp_dir.path().join("opsml.lock").exists());

        // print the contents of the lock file
        let contents = fs::read_to_string(temp_dir.path().join("opsml.lock")).unwrap();

        // load file from tests/example.lock
        let expected_content = fs::read_to_string("test/example.lock").unwrap();
        // Check if contents contain expected content
        assert!(contents.contains(&expected_content));

        // Read the lock file back
        let read_lock_file = LockFile::read(temp_dir.path()).unwrap();

        // Verify the contents
        assert_eq!(read_lock_file.artifact.len(), 2);
        //
        let first_entry = &read_lock_file.artifact[0];
        assert_eq!(first_entry.space, "test-space");
        assert_eq!(first_entry.name, "test-artifact");
        assert_eq!(first_entry.version, "1.0.0");
        assert_eq!(first_entry.uid, "abc123");
        assert_eq!(first_entry.registry_type, RegistryType::Model);
        //
        let second_entry = &read_lock_file.artifact[1];
        assert_eq!(second_entry.space, "test-space-2");
        assert_eq!(second_entry.name, "test-artifact-2");
        assert_eq!(second_entry.version, "2.0.0");
        assert_eq!(second_entry.uid, "def456");
        assert_eq!(second_entry.registry_type, RegistryType::Data);
    }
}
