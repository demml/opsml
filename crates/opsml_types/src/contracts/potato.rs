use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(default, rename_all = "camelCase")]
pub struct ToolRef {
    pub space: String,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
pub struct SkillRef {
    pub space: String,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum PotatoMemoryType {
    #[default]
    InMemory,
    Windowed,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct PotatoMemoryConfig {
    pub memory_type: PotatoMemoryType,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub window_size: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum CriteriaType {
    #[default]
    StructuredOutput,
    MaxIterations,
    Custom(String),
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct PotatoCriteria {
    pub criteria_type: CriteriaType,
    pub schema: Option<serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct PotatoAgentConfig {
    pub provider: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub model: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub system_prompt: Option<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub tools: Vec<ToolRef>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub skills: Vec<SkillRef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_iterations: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub memory: Option<PotatoMemoryConfig>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub criteria: Vec<PotatoCriteria>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub callbacks: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_potato_agent_config_roundtrip() {
        let config = PotatoAgentConfig {
            provider: "anthropic".to_string(),
            model: Some("claude-sonnet-4-6".to_string()),
            system_prompt: Some("You are a helpful agent.".to_string()),
            tools: vec![ToolRef {
                space: "platform".to_string(),
                name: "search".to_string(),
                version: None,
            }],
            skills: vec![SkillRef {
                space: "platform".to_string(),
                name: "code-reviewer".to_string(),
                version: Some("1.0.0".to_string()),
            }],
            max_iterations: Some(20),
            memory: Some(PotatoMemoryConfig {
                memory_type: PotatoMemoryType::Windowed,
                window_size: Some(10),
            }),
            criteria: vec![PotatoCriteria {
                criteria_type: CriteriaType::MaxIterations,
                schema: None,
            }],
            callbacks: vec!["on_complete".to_string()],
        };

        let json = serde_json::to_string(&config).unwrap();
        let roundtrip: PotatoAgentConfig = serde_json::from_str(&json).unwrap();

        assert_eq!(config.provider, roundtrip.provider);
        assert_eq!(config.model, roundtrip.model);
        assert_eq!(config.max_iterations, roundtrip.max_iterations);
        assert_eq!(config.tools.len(), roundtrip.tools.len());
        assert_eq!(config.skills.len(), roundtrip.skills.len());
    }

    #[test]
    fn test_potato_agent_config_defaults_empty() {
        let config = PotatoAgentConfig::default();
        let json = serde_json::to_string(&config).unwrap();
        let roundtrip: PotatoAgentConfig = serde_json::from_str(&json).unwrap();

        assert_eq!(roundtrip.provider, "");
        assert!(roundtrip.model.is_none());
        assert!(roundtrip.tools.is_empty());
        assert!(roundtrip.skills.is_empty());
        assert!(roundtrip.memory.is_none());
    }
}
