use crate::error::CliError;
use chrono::{DateTime, Duration, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;

/// Tracks downloaded skill artifacts for cache invalidation.
/// Lives at `~/.opsml/cache/manifest.json`.
#[derive(Debug, Serialize, Deserialize)]
pub struct CacheManifest {
    pub version: u32,
    pub entries: HashMap<String, CacheEntry>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CacheEntry {
    pub uid: String,
    pub content_hash: String,
    pub fetched_at: DateTime<Utc>,
    pub artifact_path: PathBuf,
    pub size_bytes: u64,
}

impl Default for CacheManifest {
    fn default() -> Self {
        Self {
            version: 1,
            entries: HashMap::new(),
        }
    }
}

impl CacheManifest {
    pub fn path() -> PathBuf {
        dirs::home_dir()
            .unwrap_or_else(|| PathBuf::from("."))
            .join(".opsml")
            .join("cache")
            .join("manifest.json")
    }

    pub fn cache_dir() -> PathBuf {
        dirs::home_dir()
            .unwrap_or_else(|| PathBuf::from("."))
            .join(".opsml")
            .join("cache")
    }

    pub fn load() -> Result<Self, CliError> {
        let path = Self::path();
        if !path.exists() {
            return Ok(Self::default());
        }
        let contents = fs::read_to_string(&path)
            .map_err(|e| CliError::Error(format!("Failed to read cache manifest: {e}")))?;
        serde_json::from_str(&contents)
            .map_err(|e| CliError::Error(format!("Failed to parse cache manifest: {e}")))
    }

    pub fn save(&self) -> Result<(), CliError> {
        let path = Self::path();
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)
                .map_err(|e| CliError::Error(format!("Failed to create cache dir: {e}")))?;
        }

        let tmp_path = path.with_extension("json.tmp");
        let contents = serde_json::to_string_pretty(self)
            .map_err(|e| CliError::Error(format!("Failed to serialize cache manifest: {e}")))?;
        fs::write(&tmp_path, contents)
            .map_err(|e| CliError::Error(format!("Failed to write cache manifest: {e}")))?;
        fs::rename(&tmp_path, &path)
            .map_err(|e| CliError::Error(format!("Failed to rename cache manifest: {e}")))?;

        Ok(())
    }

    /// Key format: `{space}/{name}/{version}`
    pub fn key(space: &str, name: &str, version: &str) -> String {
        format!("{space}/{name}/{version}")
    }

    pub fn is_fresh(&self, key: &str, content_hash: &str) -> bool {
        self.entries
            .get(key)
            .is_some_and(|e| e.content_hash == content_hash)
    }

    pub fn upsert(&mut self, key: String, entry: CacheEntry) {
        self.entries.insert(key, entry);
    }

    pub fn prune(&mut self, max_age: Duration) {
        let cutoff = Utc::now() - max_age;
        self.entries.retain(|_, entry| entry.fetched_at > cutoff);
    }
}
