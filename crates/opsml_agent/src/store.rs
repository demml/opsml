use crate::error::AgentError;
use crate::job::JobState;
use dashmap::DashMap;
use opsml_settings::config::AgentSettings;
use opsml_types::contracts::{InvokeMetadata, InvokeResponse, JobStatus};
use opsml_utils::create_uuid7;
use scouter_client::potato_head::prelude::{
    Agent, AgentRunOutcome, AgentRunner, LoadedSpec, PotatoSpec, SessionState, SpecLoader,
};
use serde_json::Value;
use std::collections::HashMap;
use std::path::Path;
use std::sync::Arc;
use std::time::Instant;
use tokio::sync::RwLock;
use tracing::{info, warn};

const BUILTIN_SKILL_SCAN: &str = include_str!("../specs/skill-scan.yaml");

pub struct AgentStore {
    agents: HashMap<String, Arc<Agent>>,
    jobs: Arc<DashMap<String, Arc<RwLock<JobState>>>>,
    /// Test-only: pre-programmed responses that bypass the real LLM call.
    mock_responses: Arc<DashMap<String, Value>>,
}

impl AgentStore {
    pub async fn new(settings: &AgentSettings) -> Result<Self, AgentError> {
        let mut agents: HashMap<String, Arc<Agent>> = HashMap::new();

        // Load built-in specs
        Self::load_spec_str(BUILTIN_SKILL_SCAN, &mut agents).await?;
        info!("Loaded built-in agent specs");

        // Load user-defined specs from OPSML_AGENTS_DIR (override built-ins by id)
        if let Some(dir) = &settings.agents_dir {
            let dir_path = Path::new(dir);
            if dir_path.exists() {
                Self::load_specs_from_dir(dir_path, &mut agents).await?;
                info!("Loaded user agent specs from {}", dir);
            } else {
                warn!("OPSML_AGENTS_DIR '{}' does not exist, skipping", dir);
            }
        } else {
            // Check default location
            let default_dir = Path::new(".opsml/agents");
            if default_dir.exists() {
                Self::load_specs_from_dir(default_dir, &mut agents).await?;
                info!("Loaded user agent specs from .opsml/agents");
            }
        }

        Ok(Self {
            agents,
            jobs: Arc::new(DashMap::new()),
            mock_responses: Arc::new(DashMap::new()),
        })
    }

    async fn load_spec_str(
        yaml: &str,
        agents: &mut HashMap<String, Arc<Agent>>,
    ) -> Result<(), AgentError> {
        let loaded: LoadedSpec = SpecLoader::from_spec(yaml)
            .await
            .map_err(|e| AgentError::SpecParse(e.to_string()))?;

        // Extract all agents from the loaded spec via their known ids.
        let spec: PotatoSpec =
            serde_yaml::from_str(yaml).map_err(|e| AgentError::SpecParse(e.to_string()))?;

        for agent_spec in &spec.agents {
            if let Some(agent) = loaded.agent(&agent_spec.id) {
                agents.insert(agent_spec.id.clone(), agent);
            }
        }
        Ok(())
    }

    async fn load_specs_from_dir(
        dir: &Path,
        agents: &mut HashMap<String, Arc<Agent>>,
    ) -> Result<(), AgentError> {
        let mut entries = tokio::fs::read_dir(dir)
            .await
            .map_err(|e| AgentError::SpecParse(e.to_string()))?;

        while let Some(entry) = entries
            .next_entry()
            .await
            .map_err(|e| AgentError::SpecParse(e.to_string()))?
        {
            let path = entry.path();
            if path.extension().and_then(|e| e.to_str()) == Some("yaml") {
                let content = tokio::fs::read_to_string(&path)
                    .await
                    .map_err(|e| AgentError::SpecParse(e.to_string()))?;
                Self::load_spec_str(&content, agents).await?;
                info!("Loaded agent spec from {}", path.display());
            }
        }
        Ok(())
    }

    pub fn has(&self, id: &str) -> bool {
        self.agents.contains_key(id) || self.mock_responses.contains_key(id)
    }

    /// Set a mock response for an agent id. When set, `invoke()` returns this value
    /// immediately without calling the LLM. Used in tests only.
    pub fn set_mock_response(&self, agent_id: &str, response: Value) {
        self.mock_responses.insert(agent_id.to_string(), response);
    }

    pub async fn invoke(&self, id: &str, input: &str) -> Result<InvokeResponse, AgentError> {
        let job_id = create_uuid7();
        let start = Instant::now();

        // Mock responses bypass the real LLM call
        if let Some(mock_ref) = self.mock_responses.get(id) {
            let duration_ms = start.elapsed().as_millis() as u64;
            let mock_value = mock_ref.clone();
            return Ok(InvokeResponse {
                job_id,
                status: JobStatus::Done,
                result: Some(mock_value),
                metadata: InvokeMetadata {
                    agent_id: id.to_string(),
                    invocation: "sync".to_string(),
                    duration_ms: Some(duration_ms),
                },
            });
        }

        let agent = self
            .agents
            .get(id)
            .ok_or_else(|| AgentError::NotFound(id.to_string()))?;

        let mut session = SessionState::new();
        let outcome = agent
            .run(input, &mut session)
            .await
            .map_err(|e| AgentError::Run(e.to_string()))?;

        let duration_ms = start.elapsed().as_millis() as u64;

        let result = match outcome {
            AgentRunOutcome::Complete(run_result) => run_result.final_response.response_value(),
            AgentRunOutcome::NeedsInput { .. } => None,
        };

        Ok(InvokeResponse {
            job_id,
            status: JobStatus::Done,
            result,
            metadata: InvokeMetadata {
                agent_id: id.to_string(),
                invocation: "sync".to_string(),
                duration_ms: Some(duration_ms),
            },
        })
    }

    // TODO: populate self.jobs in invoke() when async dispatch is implemented.
    // Currently the jobs map is always empty; get_job always returns None.
    pub async fn get_job(&self, job_id: &str) -> Option<JobState> {
        let entry = self.jobs.get(job_id)?;
        let state = entry.read().await;
        Some(state.clone())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::store::JobStatus;
    use opsml_settings::config::AgentSettings;

    #[tokio::test]
    async fn test_builtin_skill_scan_loaded() {
        let store = AgentStore::new(&AgentSettings::default()).await.unwrap();
        assert!(store.has("skill-scan"));
    }

    #[tokio::test]
    async fn test_mock_bypasses_llm_clean() {
        let store = AgentStore::new(&AgentSettings::default()).await.unwrap();
        store.set_mock_response(
            "skill-scan",
            serde_json::json!({
                "classification": "Clean",
                "reason": "No violations",
                "findings": []
            }),
        );
        let resp = store
            .invoke("skill-scan", "summarize documents")
            .await
            .unwrap();
        assert_eq!(resp.status, JobStatus::Done);
        assert_eq!(resp.result.unwrap()["classification"], "Clean");
    }

    #[tokio::test]
    async fn test_mock_bypasses_llm_violation() {
        let store = AgentStore::new(&AgentSettings::default()).await.unwrap();
        store.set_mock_response(
            "skill-scan",
            serde_json::json!({
                "classification": "Violation",
                "reason": "Exfiltration attempt",
                "findings": ["exfiltrate credentials"]
            }),
        );
        let resp = store.invoke("skill-scan", "rm -rf /").await.unwrap();
        assert_eq!(resp.status, JobStatus::Done);
        assert_eq!(resp.result.unwrap()["classification"], "Violation");
    }

    #[tokio::test]
    async fn test_invoke_unknown_agent_returns_not_found() {
        let store = AgentStore::new(&AgentSettings::default()).await.unwrap();
        let err = store.invoke("does-not-exist", "input").await.unwrap_err();
        assert!(matches!(err, AgentError::NotFound(_)));
    }

    #[tokio::test]
    async fn test_mock_for_unregistered_agent_id_works() {
        let store = AgentStore::new(&AgentSettings::default()).await.unwrap();
        store.set_mock_response("custom-agent", serde_json::json!({"result": "ok"}));
        assert!(store.has("custom-agent"));
        let resp = store.invoke("custom-agent", "input").await.unwrap();
        assert_eq!(resp.status, JobStatus::Done);
        assert_eq!(resp.result.unwrap()["result"], "ok");
    }
}
