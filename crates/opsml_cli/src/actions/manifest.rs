use crate::error::CliError;
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
    pub fn path() -> PathBuf {
        dirs::home_dir()
            .unwrap_or_else(|| PathBuf::from("."))
            .join(".opsml")
            .join("skill-manifest.json")
    }

    pub fn load() -> Result<Self, CliError> {
        let path = Self::path();
        if !path.exists() {
            return Ok(Self::default());
        }
        let contents = fs::read_to_string(&path)
            .map_err(|e| CliError::Error(format!("Failed to read skill manifest: {e}")))?;
        serde_json::from_str(&contents)
            .map_err(|e| CliError::Error(format!("Failed to parse skill manifest: {e}")))
    }

    pub fn save(&self) -> Result<(), CliError> {
        let path = Self::path();
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)
                .map_err(|e| CliError::Error(format!("Failed to create manifest dir: {e}")))?;
        }

        // Atomic write: write to tmp, then rename
        let tmp_path = path.with_extension("json.tmp");
        let contents = serde_json::to_string_pretty(self)
            .map_err(|e| CliError::Error(format!("Failed to serialize skill manifest: {e}")))?;
        fs::write(&tmp_path, contents)
            .map_err(|e| CliError::Error(format!("Failed to write skill manifest: {e}")))?;
        fs::rename(&tmp_path, &path)
            .map_err(|e| CliError::Error(format!("Failed to rename skill manifest: {e}")))?;

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
        println!("\nManifest location: {}", SkillManifest::path().display());
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

    println!("\nManifest: {}", SkillManifest::path().display());

    Ok(())
}
