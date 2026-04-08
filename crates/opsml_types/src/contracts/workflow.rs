use crate::RegistryType;
use crate::contracts::ToolSpec;
use crate::error::TypeError;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet, VecDeque};

/// Reference to a registered card by space/name/optional version.
/// Used in WorkflowStep to reference skills, agents, and MCP servers.
#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(default, rename_all = "camelCase")]
pub struct CardRef {
    pub space: String,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
}

/// Canvas position for the future no-code workflow builder UI.
#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(default, rename_all = "camelCase")]
pub struct Position {
    pub x: f64,
    pub y: f64,
}

/// Optional display metadata attached to a step for a future drag-and-drop composer.
/// No UI in this PR — stored as part of WorkflowSpec for forward compatibility.
#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(default, rename_all = "camelCase")]
pub struct StepDisplay {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub label: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub icon: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub position: Option<Position>,
}

/// A typed workflow input declaration (maps to `inputs:` section of opsmlspec.yaml).
#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(default, rename_all = "camelCase")]
pub struct WorkflowInput {
    /// Input type: "string", "number", "boolean", "json"
    #[serde(rename = "type")]
    pub input_type: String,
    #[serde(default)]
    pub required: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub default: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
}

/// A single step in a workflow DAG. Exactly one action field
/// (skill, agent, mcp, tool, or prompt) must be set.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct WorkflowStep {
    pub name: String,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub depends_on: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub skill: Option<CardRef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub agent: Option<CardRef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mcp: Option<CardRef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tool: Option<ToolSpec>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub prompt: Option<String>,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub inputs: HashMap<String, String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub outputs: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub condition: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timeout_seconds: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub display: Option<StepDisplay>,
}

impl WorkflowStep {
    fn has_action(&self) -> bool {
        self.skill.is_some()
            || self.agent.is_some()
            || self.mcp.is_some()
            || self.tool.is_some()
            || self.prompt.is_some()
    }
}

/// A DAG-based workflow definition. Steps are executed in dependency order.
/// Registered as a ServiceCard with ServiceType::Workflow — no separate registry table.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct WorkflowSpec {
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub inputs: HashMap<String, WorkflowInput>,
    pub steps: Vec<WorkflowStep>,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub outputs: HashMap<String, String>,
}

impl WorkflowSpec {
    /// Validate the workflow:
    /// - no duplicate step names
    /// - all depends_on targets reference existing steps
    /// - every step has at least one action (skill/agent/mcp/tool/prompt)
    /// - the DAG is acyclic (Kahn's algorithm)
    pub fn validate(&self) -> Result<(), TypeError> {
        let mut seen_names: HashSet<&str> = HashSet::new();

        for step in &self.steps {
            if step.name.is_empty() {
                return Err(TypeError::WorkflowValidation(
                    "step name must not be empty".into(),
                ));
            }
            if !seen_names.insert(step.name.as_str()) {
                return Err(TypeError::WorkflowValidation(format!(
                    "duplicate step name: '{}'",
                    step.name
                )));
            }
            if !step.has_action() {
                return Err(TypeError::WorkflowValidation(format!(
                    "step '{}' has no action (skill, agent, mcp, tool, or prompt required)",
                    step.name
                )));
            }
        }

        let step_names: HashSet<&str> = self.steps.iter().map(|s| s.name.as_str()).collect();

        for step in &self.steps {
            for dep in &step.depends_on {
                if !step_names.contains(dep.as_str()) {
                    return Err(TypeError::WorkflowValidation(format!(
                        "step '{}' depends_on unknown step '{}'",
                        step.name, dep
                    )));
                }
            }
        }

        // Kahn's algorithm for cycle detection
        let mut in_degree: HashMap<&str, usize> = self
            .steps
            .iter()
            .map(|s| (s.name.as_str(), 0))
            .collect();

        for step in &self.steps {
            for dep in &step.depends_on {
                *in_degree.entry(step.name.as_str()).or_insert(0) += 1;
                let _ = dep; // dep drives step's in-degree; we already counted above
            }
        }

        // Re-compute cleanly: in_degree[step] = number of steps that step depends on
        let mut in_degree: HashMap<&str, usize> =
            self.steps.iter().map(|s| (s.name.as_str(), s.depends_on.len())).collect();

        // Build reverse adjacency: for each dep, which steps depend on it
        let mut dependents: HashMap<&str, Vec<&str>> = self
            .steps
            .iter()
            .map(|s| (s.name.as_str(), Vec::new()))
            .collect();

        for step in &self.steps {
            for dep in &step.depends_on {
                dependents.entry(dep.as_str()).or_default().push(step.name.as_str());
            }
        }

        let mut queue: VecDeque<&str> = in_degree
            .iter()
            .filter(|(_, deg)| **deg == 0)
            .map(|(name, _)| *name)
            .collect();

        let mut processed = 0usize;
        while let Some(node) = queue.pop_front() {
            processed += 1;
            for &dependent in dependents.get(node).map(|v| v.as_slice()).unwrap_or(&[]) {
                let deg = in_degree.entry(dependent).or_insert(0);
                *deg = deg.saturating_sub(1);
                if *deg == 0 {
                    queue.push_back(dependent);
                }
            }
        }

        if processed != self.steps.len() {
            return Err(TypeError::WorkflowValidation(
                "workflow contains a dependency cycle".into(),
            ));
        }

        Ok(())
    }

    /// Collect all CardRefs from steps along with their expected registry type.
    /// skill → RegistryType::Skill, agent → RegistryType::Agent, mcp → RegistryType::Mcp
    pub fn card_refs(&self) -> Vec<(&CardRef, RegistryType)> {
        let mut refs = Vec::new();
        for step in &self.steps {
            if let Some(skill) = &step.skill {
                refs.push((skill, RegistryType::Skill));
            }
            if let Some(agent) = &step.agent {
                refs.push((agent, RegistryType::Agent));
            }
            if let Some(mcp) = &step.mcp {
                refs.push((mcp, RegistryType::Mcp));
            }
        }
        refs
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contracts::ToolType;

    fn make_step(name: &str, action: &str) -> WorkflowStep {
        let mut step = WorkflowStep {
            name: name.to_string(),
            ..Default::default()
        };
        match action {
            "skill" => {
                step.skill = Some(CardRef {
                    space: "platform".into(),
                    name: "my-skill".into(),
                    version: None,
                })
            }
            "agent" => {
                step.agent = Some(CardRef {
                    space: "platform".into(),
                    name: "my-agent".into(),
                    version: Some("1.*".into()),
                })
            }
            "prompt" => step.prompt = Some("You are a reviewer.".into()),
            _ => {}
        }
        step
    }

    #[test]
    fn test_workflow_spec_roundtrip() {
        let spec = WorkflowSpec {
            inputs: {
                let mut m = HashMap::new();
                m.insert(
                    "repo_url".into(),
                    WorkflowInput {
                        input_type: "string".into(),
                        required: true,
                        default: None,
                        description: Some("Repository URL".into()),
                    },
                );
                m
            },
            steps: vec![
                make_step("fetch", "skill"),
                {
                    let mut s = make_step("review", "agent");
                    s.depends_on = vec!["fetch".into()];
                    s
                },
            ],
            outputs: {
                let mut m = HashMap::new();
                m.insert("summary".into(), "{{ review.summary }}".into());
                m
            },
        };

        let json = serde_json::to_string(&spec).unwrap();
        let roundtrip: WorkflowSpec = serde_json::from_str(&json).unwrap();
        assert_eq!(spec.steps.len(), roundtrip.steps.len());
        assert_eq!(spec.inputs.len(), roundtrip.inputs.len());
        assert_eq!(spec.outputs, roundtrip.outputs);
    }

    #[test]
    fn test_workflow_spec_defaults_empty() {
        let spec = WorkflowSpec::default();
        let json = serde_json::to_string(&spec).unwrap();
        assert!(!json.contains("inputs"));
        assert!(!json.contains("outputs"));
        let roundtrip: WorkflowSpec = serde_json::from_str(&json).unwrap();
        assert_eq!(spec.steps.len(), roundtrip.steps.len());
    }

    #[test]
    fn test_workflow_valid_dag() {
        let spec = WorkflowSpec {
            steps: vec![
                make_step("a", "skill"),
                {
                    let mut s = make_step("b", "agent");
                    s.depends_on = vec!["a".into()];
                    s
                },
                {
                    let mut s = make_step("c", "prompt");
                    s.depends_on = vec!["b".into()];
                    s
                },
            ],
            ..Default::default()
        };
        assert!(spec.validate().is_ok());
    }

    #[test]
    fn test_workflow_cycle_detection() {
        let spec = WorkflowSpec {
            steps: vec![
                {
                    let mut s = make_step("a", "skill");
                    s.depends_on = vec!["b".into()];
                    s
                },
                {
                    let mut s = make_step("b", "agent");
                    s.depends_on = vec!["a".into()];
                    s
                },
            ],
            ..Default::default()
        };
        let err = spec.validate().unwrap_err();
        assert!(err.to_string().contains("cycle"));
    }

    #[test]
    fn test_workflow_duplicate_step_names() {
        let spec = WorkflowSpec {
            steps: vec![make_step("foo", "skill"), make_step("foo", "agent")],
            ..Default::default()
        };
        let err = spec.validate().unwrap_err();
        assert!(err.to_string().contains("duplicate step name"));
    }

    #[test]
    fn test_workflow_step_requires_action() {
        let spec = WorkflowSpec {
            steps: vec![WorkflowStep {
                name: "empty".into(),
                ..Default::default()
            }],
            ..Default::default()
        };
        let err = spec.validate().unwrap_err();
        assert!(err.to_string().contains("no action"));
    }

    #[test]
    fn test_workflow_missing_depends_on_target() {
        let spec = WorkflowSpec {
            steps: vec![{
                let mut s = make_step("a", "skill");
                s.depends_on = vec!["nonexistent".into()];
                s
            }],
            ..Default::default()
        };
        let err = spec.validate().unwrap_err();
        assert!(err.to_string().contains("unknown step"));
    }

    #[test]
    fn test_workflow_card_refs() {
        let spec = WorkflowSpec {
            steps: vec![
                make_step("s1", "skill"),
                make_step("s2", "agent"),
                make_step("s3", "prompt"),
            ],
            ..Default::default()
        };
        let refs = spec.card_refs();
        assert_eq!(refs.len(), 2);
        assert_eq!(refs[0].1, RegistryType::Skill);
        assert_eq!(refs[1].1, RegistryType::Agent);
    }

    #[test]
    fn test_position_json() {
        let pos = Position { x: 1.0, y: 2.0 };
        let json = serde_json::to_string(&pos).unwrap();
        assert_eq!(json, r#"{"x":1.0,"y":2.0}"#);
        let roundtrip: Position = serde_json::from_str(&json).unwrap();
        assert_eq!(pos, roundtrip);
    }

    #[test]
    fn test_step_display_roundtrip() {
        let display = StepDisplay {
            label: Some("Review Code".into()),
            description: Some("Runs the reviewer agent".into()),
            icon: Some("robot".into()),
            position: Some(Position { x: 100.0, y: 200.0 }),
        };
        let json = serde_json::to_string(&display).unwrap();
        let roundtrip: StepDisplay = serde_json::from_str(&json).unwrap();
        assert_eq!(display, roundtrip);
    }

    #[test]
    fn test_workflow_input_type_serializes_as_type() {
        let input = WorkflowInput {
            input_type: "string".into(),
            required: true,
            ..Default::default()
        };
        let json = serde_json::to_string(&input).unwrap();
        assert!(json.contains(r#""type":"string""#));
        assert!(!json.contains("inputType"));
        let roundtrip: WorkflowInput = serde_json::from_str(&json).unwrap();
        assert_eq!(input, roundtrip);
    }

    #[test]
    fn test_card_ref_roundtrip() {
        let card_ref = CardRef {
            space: "platform".into(),
            name: "code-analyzer".into(),
            version: Some("2.*".into()),
        };
        let json = serde_json::to_string(&card_ref).unwrap();
        let roundtrip: CardRef = serde_json::from_str(&json).unwrap();
        assert_eq!(card_ref, roundtrip);
    }

    #[test]
    fn test_workflow_step_with_tool_roundtrip() {
        let step = WorkflowStep {
            name: "fetch".into(),
            tool: Some(ToolSpec {
                name: "git-clone".into(),
                description: "Clone repository".into(),
                tool_type: ToolType::ShellScript,
                args_schema: None,
                output_schema: None,
                script_config: None,
                api_config: None,
                mcp_server_name: None,
                allowed_tools: vec![],
                requires_approval: false,
                hook_events: vec![],
                hook_matcher: None,
            }),
            outputs: vec!["repo_path".into()],
            ..Default::default()
        };
        let json = serde_json::to_string(&step).unwrap();
        assert!(json.contains("git-clone"));
        let roundtrip: WorkflowStep = serde_json::from_str(&json).unwrap();
        assert_eq!(step.name, roundtrip.name);
        assert!(roundtrip.tool.is_some());
    }
}
