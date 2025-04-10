use opsml_error::PyProjectTomlError;
use opsml_types::RegistryType;
use serde::{de::IntoDeserializer, Deserialize, Serialize};
use std::fs;
use std::path::Path;
use std::str::FromStr;
use toml_edit::{value, ArrayOfTables, DocumentMut, Item, Table};

#[derive(Debug, Serialize, Deserialize)]
pub struct LockEntry {
    pub space: String,
    pub name: String,
    pub version: String,
    pub uid: String,
    pub registry_type: RegistryType,
}

/// LockFile struct to hold the lock entries
#[derive(Debug, Serialize, Deserialize)]
pub struct LockFile {
    // Each entry is considered a service
    pub entries: Vec<LockEntry>,
}

impl LockFile {
    /// Iterate over entries and create a lock file
    ///
    /// # Arguments
    /// * `path` - Optional path to the lock file
    ///
    pub fn write(&self, path: &Path) -> Result<(), PyProjectTomlError> {
        let mut doc = DocumentMut::new();
        doc.insert("version", value(env!("CARGO_PKG_VERSION").to_string()));
        let mut artifacts = ArrayOfTables::new();

        // Create entries for each service
        for entry in &self.entries {
            let mut table = Table::new();
            table["space"] = Item::Value(entry.space.clone().into());
            table["name"] = Item::Value(entry.name.clone().into());
            table["version"] = Item::Value(entry.version.clone().into());
            table["uid"] = Item::Value(entry.uid.clone().into());
            table["registry_type"] = Item::Value(entry.registry_type.to_string().into());
            artifacts.push(table);
        }

        doc.insert("artifact", Item::ArrayOfTables(artifacts));

        // Write to file
        let lock_path = path.join("opsml.lock");
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
    pub fn read(path: &Path) -> Result<Self, PyProjectTomlError> {
        let lock_path = path.join("opsml.lock");
        let content =
            fs::read_to_string(lock_path).map_err(PyProjectTomlError::FailedToReadLockFile)?;

        let lockfile: toml_edit::ImDocument<_> =
            toml_edit::ImDocument::from_str(&content).map_err(PyProjectTomlError::ParseError)?;
        //
        let lockfile = LockFile::deserialize(lockfile.into_deserializer())
            .map_err(PyProjectTomlError::TomlSchema)?;

        Ok(lockfile)
    }
}
