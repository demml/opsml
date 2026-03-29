use crate::error::{CliError, ManifestError};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;

/// Tracks which skills are installed locally.
/// Lives at `~/.opsml/skill-manifest.json`.
#[derive(Debug, Serialize, Deserialize)]
pub struct SkillManifest {
    pub version: u32,
    pub entries: HashMap<String, SkillEntry>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SkillEntry {
    pub space: String,
    pub name: String,
    pub version: String,
    pub content_hash: String,
    pub uid: String,
    pub installed_at: DateTime<Utc>,
    pub server_url: String,
    pub targets: Vec<String>,
}

impl Default for SkillManifest {
    fn default() -> Self {
        Self {
            version: 1,
            entries: HashMap::new(),
        }
    }
}

impl SkillManifest {
    pub fn path() -> Result<PathBuf, ManifestError> {
        Ok(dirs::home_dir()
            .ok_or(ManifestError::HomeDirNotFound)?
            .join(".opsml")
            .join("skill-manifest.json"))
    }

    pub fn load() -> Result<Self, ManifestError> {
        let path = Self::path()?;
        if !path.exists() {
            return Ok(Self::default());
        }
        let contents = fs::read_to_string(&path).map_err(ManifestError::ReadSkillManifest)?;
        serde_json::from_str(&contents).map_err(ManifestError::ParseSkillManifest)
    }

    pub fn save(&self) -> Result<(), ManifestError> {
        let path = Self::path()?;
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent).map_err(ManifestError::CreateSkillManifestDir)?;
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                fs::set_permissions(parent, fs::Permissions::from_mode(0o700))
                    .map_err(ManifestError::SetSkillManifestPermissions)?;
            }
        }

        // Atomic write: write to tmp, then rename
        let tmp_path = path.with_extension("json.tmp");
        let contents =
            serde_json::to_string_pretty(self).map_err(ManifestError::SerializeSkillManifest)?;
        fs::write(&tmp_path, contents).map_err(ManifestError::WriteSkillManifest)?;
        fs::rename(&tmp_path, &path).map_err(ManifestError::RenameSkillManifest)?;
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            fs::set_permissions(&path, fs::Permissions::from_mode(0o600))
                .map_err(ManifestError::SetSkillManifestPermissions)?;
        }

        Ok(())
    }

    /// Key format: `{space}/{name}`
    pub fn key(space: &str, name: &str) -> String {
        format!("{space}/{name}")
    }

    pub fn upsert(&mut self, entry: SkillEntry) {
        let key = Self::key(&entry.space, &entry.name);
        self.entries.insert(key, entry);
    }

    pub fn remove(&mut self, key: &str) {
        self.entries.remove(key);
    }

    pub fn get(&self, key: &str) -> Option<&SkillEntry> {
        self.entries.get(key)
    }
}

pub fn print_skill_status() -> Result<(), CliError> {
    let manifest = SkillManifest::load()?;

    if manifest.entries.is_empty() {
        println!("No skills installed.");
        if let Ok(path) = SkillManifest::path() {
            println!("\nManifest location: {}", path.display());
        }
        return Ok(());
    }

    println!("Installed Skills\n");
    println!(
        "  {:<15} {:<20} {:<10} {:<22} TARGETS",
        "SPACE", "NAME", "VERSION", "INSTALLED"
    );

    let mut entries: Vec<_> = manifest.entries.values().collect();
    entries.sort_by(|a, b| (&a.space, &a.name).cmp(&(&b.space, &b.name)));

    for entry in entries {
        println!(
            "  {:<15} {:<20} {:<10} {:<22} {}",
            entry.space,
            entry.name,
            entry.version,
            entry.installed_at.format("%Y-%m-%d %H:%M"),
            entry.targets.join(", ")
        );
    }

    if let Ok(path) = SkillManifest::path() {
        println!("\nManifest: {}", path.display());
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Utc;
    use tempfile::tempdir;

    fn make_entry(space: &str, name: &str) -> SkillEntry {
        SkillEntry {
            space: space.to_string(),
            name: name.to_string(),
            version: "1.0.0".to_string(),
            content_hash: "abc123".to_string(),
            uid: "uid-1".to_string(),
            installed_at: Utc::now(),
            server_url: "https://opsml.example.com".to_string(),
            targets: vec!["claude".to_string()],
        }
    }

    fn save_to(manifest: &SkillManifest, path: &std::path::Path) {
        let tmp = path.with_extension("json.tmp");
        let contents = serde_json::to_string_pretty(manifest).unwrap();
        fs::write(&tmp, contents).unwrap();
        fs::rename(&tmp, path).unwrap();
    }

    fn load_from(path: &std::path::Path) -> SkillManifest {
        let contents = fs::read_to_string(path).unwrap();
        serde_json::from_str(&contents).unwrap()
    }

    #[test]
    fn roundtrip_save_load() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("skill-manifest.json");

        let mut manifest = SkillManifest::default();
        manifest.upsert(make_entry("platform", "code-review"));
        manifest.upsert(make_entry("platform", "test-gen"));

        save_to(&manifest, &path);
        let loaded = load_from(&path);

        assert_eq!(loaded.entries.len(), 2);
        assert!(loaded.entries.contains_key("platform/code-review"));
        assert!(loaded.entries.contains_key("platform/test-gen"));
    }

    #[test]
    fn upsert_overwrites_same_key() {
        let mut manifest = SkillManifest::default();
        manifest.upsert(make_entry("platform", "code-review"));
        manifest.upsert(SkillEntry {
            version: "2.0.0".to_string(),
            ..make_entry("platform", "code-review")
        });

        assert_eq!(manifest.entries.len(), 1);
        assert_eq!(manifest.entries["platform/code-review"].version, "2.0.0");
    }

    #[test]
    fn remove_deletes_entry() {
        let mut manifest = SkillManifest::default();
        manifest.upsert(make_entry("platform", "code-review"));
        manifest.remove("platform/code-review");
        assert!(manifest.entries.is_empty());
    }

    #[test]
    fn atomic_write_no_tmp_file_after_save() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("skill-manifest.json");

        let manifest = SkillManifest::default();
        save_to(&manifest, &path);

        let tmp = path.with_extension("json.tmp");
        assert!(
            !tmp.exists(),
            ".json.tmp must not exist after successful save"
        );
        assert!(path.exists(), "manifest file must exist after save");
    }
}
