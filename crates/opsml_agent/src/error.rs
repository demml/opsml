use thiserror::Error;

#[derive(Error, Debug)]
pub enum AgentError {
    #[error("Agent not found: {0}")]
    NotFound(String),

    #[error("Agent spec parse error: {0}")]
    SpecParse(String),

    #[error("Agent run error: {0}")]
    Run(String),
}
