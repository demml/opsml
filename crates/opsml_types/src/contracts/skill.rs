#[cfg(feature = "python")]
use pyo3::IntoPyObjectExt;
#[cfg(feature = "python")]
use pyo3::prelude::*;
use serde::{Deserialize, Deserializer, Serialize, Serializer};

#[allow(dead_code)]
#[derive(Debug, Clone, PartialEq)]
pub enum CompatibleTool {
    ClaudeCode,
    Codex,
    GeminiCli,
    GithubCopilotCli,
    Custom(String),
}

impl Serialize for CompatibleTool {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(&self.to_string())
    }
}

impl<'de> Deserialize<'de> for CompatibleTool {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let s = String::deserialize(d)?;
        Ok(CompatibleTool::from(s.as_str()))
    }
}

impl std::fmt::Display for CompatibleTool {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            CompatibleTool::ClaudeCode => write!(f, "claude-code"),
            CompatibleTool::Codex => write!(f, "codex"),
            CompatibleTool::GeminiCli => write!(f, "gemini-cli"),
            CompatibleTool::GithubCopilotCli => write!(f, "github-copilot-cli"),
            CompatibleTool::Custom(s) => write!(f, "{s}"),
        }
    }
}

impl From<&str> for CompatibleTool {
    fn from(s: &str) -> Self {
        match s {
            "claude-code" => CompatibleTool::ClaudeCode,
            "codex" => CompatibleTool::Codex,
            "gemini-cli" => CompatibleTool::GeminiCli,
            "github-copilot-cli" => CompatibleTool::GithubCopilotCli,
            other => CompatibleTool::Custom(other.to_string()),
        }
    }
}

#[cfg_attr(feature = "python", pyclass(eq, eq_int, from_py_object))]
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum DependencyKind {
    Skill,
    McpServer,
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SkillDependency {
    pub name: String,
    pub space: String,
    pub version_req: Option<String>,
    pub kind: DependencyKind,
}

impl SkillDependency {
    pub fn new_rs(
        name: String,
        space: String,
        kind: DependencyKind,
        version_req: Option<String>,
    ) -> Self {
        SkillDependency {
            name,
            space,
            version_req,
            kind,
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl SkillDependency {
    #[new]
    #[pyo3(signature = (name, space, kind, version_req=None))]
    pub fn new(
        name: String,
        space: String,
        kind: DependencyKind,
        version_req: Option<String>,
    ) -> Self {
        Self::new_rs(name, space, kind, version_req)
    }

    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }
    #[setter]
    pub fn set_name(&mut self, val: String) {
        self.name = val;
    }

    #[getter]
    pub fn space(&self) -> String {
        self.space.clone()
    }
    #[setter]
    pub fn set_space(&mut self, val: String) {
        self.space = val;
    }

    #[getter]
    pub fn version_req(&self) -> Option<String> {
        self.version_req.clone()
    }
    #[setter]
    pub fn set_version_req(&mut self, val: Option<String>) {
        self.version_req = val;
    }

    #[getter]
    pub fn kind<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        self.kind.clone().into_bound_py_any(py)
    }

    #[setter]
    pub fn set_kind(&mut self, kind: &Bound<'_, PyAny>) -> PyResult<()> {
        self.kind = kind.extract::<DependencyKind>()?;
        Ok(())
    }

    pub fn __repr__(&self) -> String {
        format!(
            "SkillDependency(name={}, space={}, kind={:?}, version_req={:?})",
            self.name, self.space, self.kind, self.version_req
        )
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[cfg_attr(feature = "server", derive(sqlx::FromRow))]
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
pub struct MarketplaceStats {
    pub total_skills: i64,
    pub total_spaces: i64,
    pub total_downloads: i64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_skill_dependency_roundtrip() {
        let dep = SkillDependency {
            name: "my-skill".to_string(),
            space: "my-space".to_string(),
            version_req: Some("^1.0.0".to_string()),
            kind: DependencyKind::Skill,
        };
        let json = serde_json::to_string(&dep).unwrap();
        let roundtripped: SkillDependency = serde_json::from_str(&json).unwrap();
        assert_eq!(dep, roundtripped);
    }

    #[test]
    fn test_skill_dependency_no_version_roundtrip() {
        let dep = SkillDependency {
            name: "my-mcp".to_string(),
            space: "tools".to_string(),
            version_req: None,
            kind: DependencyKind::McpServer,
        };
        let json = serde_json::to_string(&dep).unwrap();
        let roundtripped: SkillDependency = serde_json::from_str(&json).unwrap();
        assert_eq!(dep, roundtripped);
    }

    #[test]
    fn test_dependency_kind_roundtrip() {
        for kind in [DependencyKind::Skill, DependencyKind::McpServer] {
            let json = serde_json::to_string(&kind).unwrap();
            let roundtripped: DependencyKind = serde_json::from_str(&json).unwrap();
            assert_eq!(kind, roundtripped);
        }
    }

    #[test]
    fn test_compatible_tool_github_copilot_roundtrip() {
        let tool = CompatibleTool::GithubCopilotCli;
        assert_eq!(tool.to_string(), "github-copilot-cli");
        assert_eq!(
            CompatibleTool::from("github-copilot-cli"),
            CompatibleTool::GithubCopilotCli
        );
        let json = serde_json::to_string(&tool).unwrap();
        let roundtripped: CompatibleTool = serde_json::from_str(&json).unwrap();
        assert_eq!(tool, roundtripped);
    }

    #[test]
    fn test_compatible_tool_all_variants_display() {
        assert_eq!(CompatibleTool::ClaudeCode.to_string(), "claude-code");
        assert_eq!(CompatibleTool::Codex.to_string(), "codex");
        assert_eq!(CompatibleTool::GeminiCli.to_string(), "gemini-cli");
        assert_eq!(
            CompatibleTool::GithubCopilotCli.to_string(),
            "github-copilot-cli"
        );
        assert_eq!(
            CompatibleTool::Custom("my-tool".to_string()).to_string(),
            "my-tool"
        );
    }
}
