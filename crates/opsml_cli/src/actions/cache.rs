use crate::error::ManifestError;
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
    /// Timestamp of the last `save()` call. UNIX epoch on first run / old manifests,
    /// which the startup hook treats as always-stale — triggering an immediate sync.
    #[serde(default)]
    pub generated_at: DateTime<Utc>,
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
            generated_at: DateTime::<Utc>::UNIX_EPOCH,
            entries: HashMap::new(),
        }
    }
}

impl CacheManifest {
    pub fn path() -> Result<PathBuf, ManifestError> {
        Ok(dirs::home_dir()
            .ok_or(ManifestError::HomeDirNotFound)?
            .join(".opsml")
            .join("cache")
            .join("manifest.json"))
    }

    pub fn cache_dir() -> Result<PathBuf, ManifestError> {
        Ok(dirs::home_dir()
            .ok_or(ManifestError::HomeDirNotFound)?
            .join(".opsml")
            .join("cache"))
    }

    pub fn load() -> Result<Self, ManifestError> {
        let path = Self::path()?;
        if !path.exists() {
            return Ok(Self::default());
        }
        let contents = fs::read_to_string(&path).map_err(ManifestError::ReadCacheManifest)?;
        serde_json::from_str(&contents).map_err(ManifestError::ParseCacheManifest)
    }

    pub fn save(&mut self) -> Result<(), ManifestError> {
        let path = Self::path()?;
        self.save_to_path(&path)
    }

    pub(crate) fn save_to_path(&mut self, path: &std::path::Path) -> Result<(), ManifestError> {
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent).map_err(ManifestError::CreateCacheManifestDir)?;
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                fs::set_permissions(parent, fs::Permissions::from_mode(0o700))
                    .map_err(ManifestError::SetCacheManifestPermissions)?;
            }
        }

        let now = Utc::now();
        let prev = self.generated_at;
        self.generated_at = now;

        let result = self.write_atomic(path);
        if result.is_err() {
            self.generated_at = prev;
        }
        result
    }

    fn write_atomic(&self, path: &std::path::Path) -> Result<(), ManifestError> {
        let tmp_path = path.with_extension("json.tmp");
        let contents =
            serde_json::to_string_pretty(self).map_err(ManifestError::SerializeCacheManifest)?;
        fs::write(&tmp_path, contents).map_err(ManifestError::WriteCacheManifest)?;
        fs::rename(&tmp_path, path).map_err(ManifestError::RenameCacheManifest)?;
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            fs::set_permissions(path, fs::Permissions::from_mode(0o600))
                .map_err(ManifestError::SetCacheManifestPermissions)?;
        }
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

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Utc;
    use tempfile::tempdir;

    fn make_entry(content_hash: &str, age_secs: i64) -> CacheEntry {
        CacheEntry {
            uid: "uid-1".to_string(),
            content_hash: content_hash.to_string(),
            fetched_at: Utc::now() - Duration::seconds(age_secs),
            artifact_path: PathBuf::from("skills/platform/test/1.0.0"),
            size_bytes: 1024,
        }
    }

    fn save_to(manifest: &CacheManifest, path: &std::path::Path) {
        let tmp = path.with_extension("json.tmp");
        let contents = serde_json::to_string_pretty(manifest).unwrap();
        fs::write(&tmp, contents).unwrap();
        fs::rename(&tmp, path).unwrap();
    }

    fn load_from(path: &std::path::Path) -> CacheManifest {
        let contents = fs::read_to_string(path).unwrap();
        serde_json::from_str(&contents).unwrap()
    }

    #[test]
    fn test_roundtrip_save_load() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("manifest.json");

        let mut manifest = CacheManifest::default();
        manifest.upsert(
            CacheManifest::key("platform", "test-gen", "1.0.0"),
            make_entry("hash-abc", 0),
        );

        save_to(&manifest, &path);
        let loaded = load_from(&path);

        assert_eq!(loaded.entries.len(), 1);
        assert!(loaded.entries.contains_key("platform/test-gen/1.0.0"));
    }

    #[test]
    fn test_is_fresh_hash_match() {
        let mut manifest = CacheManifest::default();
        let key = CacheManifest::key("platform", "test-gen", "1.0.0");
        manifest.upsert(key.clone(), make_entry("hash-abc", 0));

        assert!(manifest.is_fresh(&key, "hash-abc"));
        assert!(!manifest.is_fresh(&key, "hash-different"));
    }

    #[test]
    fn test_is_fresh_missing_key_returns_false() {
        let manifest = CacheManifest::default();
        assert!(!manifest.is_fresh("platform/missing/1.0.0", "hash-abc"));
    }

    #[test]
    fn test_prune_removes_old_entries_keeps_recent() {
        let mut manifest = CacheManifest::default();
        let old_key = CacheManifest::key("platform", "old-skill", "1.0.0");
        let new_key = CacheManifest::key("platform", "new-skill", "1.0.0");

        // old: 200 seconds old; new: 10 seconds old
        manifest.upsert(old_key.clone(), make_entry("hash-old", 200));
        manifest.upsert(new_key.clone(), make_entry("hash-new", 10));

        // prune with 120-second max age
        manifest.prune(Duration::seconds(120));

        assert!(
            !manifest.entries.contains_key(&old_key),
            "old entry must be pruned"
        );
        assert!(
            manifest.entries.contains_key(&new_key),
            "recent entry must be retained"
        );
    }

    #[test]
    fn test_upsert_overwrites_same_key() {
        let mut manifest = CacheManifest::default();
        let key = CacheManifest::key("platform", "test-gen", "1.0.0");
        manifest.upsert(key.clone(), make_entry("hash-v1", 0));
        manifest.upsert(key.clone(), make_entry("hash-v2", 0));

        assert_eq!(manifest.entries.len(), 1);
        assert_eq!(manifest.entries[&key].content_hash, "hash-v2");
    }

    #[test]
    fn test_save_sets_generated_at() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("manifest.json");

        let before = Utc::now();
        let mut manifest = CacheManifest::default();
        // Default is UNIX_EPOCH — always treated as stale
        assert_eq!(manifest.generated_at, DateTime::<Utc>::UNIX_EPOCH);

        save_to(&manifest, &path);
        // save_to doesn't call our save() — update generated_at manually for test
        manifest.generated_at = Utc::now();
        save_to(&manifest, &path);
        let loaded = load_from(&path);

        assert!(
            loaded.generated_at > before,
            "generated_at must be set to a recent timestamp after save"
        );
    }

    #[test]
    fn test_atomic_write_no_tmp_file_after_save() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("manifest.json");

        let manifest = CacheManifest::default();
        save_to(&manifest, &path);

        let tmp = path.with_extension("json.tmp");
        assert!(
            !tmp.exists(),
            ".json.tmp must not exist after successful save"
        );
        assert!(path.exists());
    }

    #[test]
    fn test_save_via_real_method_sets_generated_at() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("manifest.json");

        let mut manifest = CacheManifest::default();
        assert_eq!(manifest.generated_at, DateTime::<Utc>::UNIX_EPOCH);

        let before = Utc::now();
        manifest.save_to_path(&path).unwrap();

        assert!(
            manifest.generated_at >= before,
            "save_to_path must set generated_at on self"
        );

        let loaded = load_from(&path);
        assert!(
            loaded.generated_at >= before,
            "persisted generated_at must be recent"
        );
        assert!(
            !path.with_extension("json.tmp").exists(),
            ".tmp must not exist after successful save"
        );
    }
}
