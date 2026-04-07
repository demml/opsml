mod card;
pub mod error;
pub mod target;

pub use card::{SubAgentCard, parse_subagent_markdown};
pub use error::SubAgentError;
pub use target::{
    ClaudeCodeTarget, CodexTarget, CopilotTarget, GeminiCliTarget, SubAgentCliTarget,
};
