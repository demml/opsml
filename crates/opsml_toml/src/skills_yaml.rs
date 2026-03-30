use crate::error::PyProjectTomlError;
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ArtifactRef {
    pub space: String,
    pub name: String,
    /// Semver range or `"latest"`. `None` is treated as latest.
    pub version: Option<String>,
}

fn default_ttl() -> u64 {
    60
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OpsmlSkillsYaml {
    pub registry: String,
    #[serde(default = "default_ttl")]
    pub ttl_minutes: u64,
    #[serde(default)]
    pub skills: Vec<ArtifactRef>,
    #[serde(default)]
    pub tools: Vec<ArtifactRef>,
    #[serde(default)]
    pub agents: Vec<ArtifactRef>,
}

impl OpsmlSkillsYaml {
    /// Load from a YAML file.
    pub fn load(path: &Path) -> Result<Self, PyProjectTomlError> {
        let content =
            std::fs::read_to_string(path).map_err(PyProjectTomlError::FailedToReadSkillsYaml)?;
        serde_yaml::from_str(&content).map_err(PyProjectTomlError::FailedToParseSkillsYaml)
    }

    /// Write a starter template. Returns `Err` if the file already exists.
    pub fn scaffold(path: &Path) -> Result<(), PyProjectTomlError> {
        if path.exists() {
            return Err(PyProjectTomlError::SkillsYamlAlreadyExists);
        }
        if let Some(parent) = path.parent()
            && !parent.as_os_str().is_empty()
        {
            std::fs::create_dir_all(parent).map_err(PyProjectTomlError::FailedToWriteSkillsYaml)?;
        }
        let template = concat!(
            "registry: http://localhost:8000\n",
            "ttl_minutes: 60\n",
            "skills:\n",
            "  - space: my-space\n",
            "    name: my-skill\n",
            "    version: latest\n",
        );
        std::fs::write(path, template).map_err(PyProjectTomlError::FailedToWriteSkillsYaml)
    }

    /// Append a skill entry if not already present. Creates the file if missing.
    pub fn append_skill(path: &Path, skill: &ArtifactRef) -> Result<(), PyProjectTomlError> {
        let mut yaml = if path.exists() {
            Self::load(path)?
        } else {
            let registry = std::env::var("OPSML_TRACKING_URI")
                .unwrap_or_else(|_| "http://localhost:8000".to_string());
            OpsmlSkillsYaml {
                registry,
                ttl_minutes: 60,
                skills: Vec::new(),
                tools: Vec::new(),
                agents: Vec::new(),
            }
        };

        if yaml
            .skills
            .iter()
            .any(|s| s.space == skill.space && s.name == skill.name)
        {
            return Ok(());
        }

        yaml.skills.push(skill.clone());

        let content =
            serde_yaml::to_string(&yaml).map_err(PyProjectTomlError::FailedToParseSkillsYaml)?;
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)
                .map_err(PyProjectTomlError::FailedToWriteSkillsYaml)?;
        }
        std::fs::write(path, content).map_err(PyProjectTomlError::FailedToWriteSkillsYaml)
    }

    /// Remove a skill entry by space + name. No-op if not found.
    pub fn remove_skill(
        path: &Path,
        space: &str,
        name: &str,
    ) -> Result<(), PyProjectTomlError> {
        if !path.exists() {
            return Ok(());
        }
        let mut yaml = Self::load(path)?;
        yaml.skills
            .retain(|s| !(s.space == space && s.name == name));
        let content =
            serde_yaml::to_string(&yaml).map_err(PyProjectTomlError::FailedToParseSkillsYaml)?;
        std::fs::write(path, content).map_err(PyProjectTomlError::FailedToWriteSkillsYaml)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn test_roundtrip_load() {
        let dir = tempdir().unwrap();
        let path = dir.path().join(".opsml-skills.yaml");
        OpsmlSkillsYaml::scaffold(&path).unwrap();
        let yaml = OpsmlSkillsYaml::load(&path).unwrap();
        assert_eq!(yaml.registry, "http://localhost:8000");
        assert_eq!(yaml.ttl_minutes, 60);
        assert_eq!(yaml.skills.len(), 1);
        assert_eq!(yaml.skills[0].space, "my-space");
        assert_eq!(yaml.skills[0].name, "my-skill");
        assert_eq!(yaml.skills[0].version.as_deref(), Some("latest"));
        assert!(yaml.tools.is_empty());
        assert!(yaml.agents.is_empty());
    }

    #[test]
    fn test_defaults_applied() {
        let content = "registry: http://example.com\n";
        let yaml: OpsmlSkillsYaml = serde_yaml::from_str(content).unwrap();
        assert_eq!(yaml.ttl_minutes, 60);
        assert!(yaml.skills.is_empty());
        assert!(yaml.tools.is_empty());
        assert!(yaml.agents.is_empty());
    }

    #[test]
    fn test_scaffold_refuses_overwrite() {
        let dir = tempdir().unwrap();
        let path = dir.path().join(".opsml-skills.yaml");
        OpsmlSkillsYaml::scaffold(&path).unwrap();
        assert!(OpsmlSkillsYaml::scaffold(&path).is_err());
    }

    #[test]
    fn test_artifact_ref_version_none() {
        let content = "registry: http://example.com\nskills:\n  - space: s\n    name: n\n";
        let yaml: OpsmlSkillsYaml = serde_yaml::from_str(content).unwrap();
        assert_eq!(yaml.skills[0].version, None);
    }

    #[test]
    fn test_scaffold_creates_nested_parent_dirs() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("subdir/nested/.opsml-skills.yaml");
        OpsmlSkillsYaml::scaffold(&path).unwrap();
        assert!(path.exists());
        let loaded = OpsmlSkillsYaml::load(&path).unwrap();
        assert_eq!(loaded.ttl_minutes, 60);
    }

    #[test]
    fn test_append_skill_creates_file_if_missing() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("skills.yaml");
        let skill = ArtifactRef {
            space: "team".into(),
            name: "my-skill".into(),
            version: Some("1.0.0".into()),
        };
        OpsmlSkillsYaml::append_skill(&path, &skill).unwrap();
        assert!(path.exists());
        let yaml = OpsmlSkillsYaml::load(&path).unwrap();
        assert_eq!(yaml.skills.len(), 1);
        assert_eq!(yaml.skills[0].name, "my-skill");
    }

    #[test]
    fn test_append_skill_idempotent() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("skills.yaml");
        let skill = ArtifactRef {
            space: "team".into(),
            name: "my-skill".into(),
            version: None,
        };
        OpsmlSkillsYaml::append_skill(&path, &skill).unwrap();
        OpsmlSkillsYaml::append_skill(&path, &skill).unwrap();
        let yaml = OpsmlSkillsYaml::load(&path).unwrap();
        assert_eq!(yaml.skills.len(), 1);
    }

    #[test]
    fn test_remove_skill() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("skills.yaml");
        let skill = ArtifactRef {
            space: "team".into(),
            name: "my-skill".into(),
            version: None,
        };
        OpsmlSkillsYaml::append_skill(&path, &skill).unwrap();
        OpsmlSkillsYaml::remove_skill(&path, "team", "my-skill").unwrap();
        let yaml = OpsmlSkillsYaml::load(&path).unwrap();
        assert!(yaml.skills.is_empty());
    }

    #[test]
    fn test_remove_skill_nonexistent_is_ok() {
        let dir = tempdir().unwrap();
        let path = dir.path().join("skills.yaml");
        // File doesn't exist — no-op
        assert!(OpsmlSkillsYaml::remove_skill(&path, "team", "nope").is_ok());
    }

    #[test]
    fn test_multiple_artifact_types() {
        let content = concat!(
            "registry: http://example.com\n",
            "ttl_minutes: 30\n",
            "skills:\n  - space: s1\n    name: n1\n    version: \"1.0.0\"\n",
            "tools:\n  - space: t1\n    name: tool1\n",
            "agents:\n  - space: a1\n    name: agent1\n    version: latest\n",
        );
        let yaml: OpsmlSkillsYaml = serde_yaml::from_str(content).unwrap();
        assert_eq!(yaml.ttl_minutes, 30);
        assert_eq!(yaml.skills.len(), 1);
        assert_eq!(yaml.tools.len(), 1);
        assert_eq!(yaml.agents.len(), 1);
        assert_eq!(yaml.skills[0].version.as_deref(), Some("1.0.0"));
    }
}
