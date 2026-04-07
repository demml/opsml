mod card;
mod error;
mod installer;

pub use card::{ToolCard, parse_tool_markdown};
pub use error::ToolError;
pub use installer::{
    ClaudeCodeInstaller, CodexInstaller, CopilotInstaller, GeminiCliInstaller, HookInstaller,
    McpConfigInstaller, SlashCommandInstaller,
};

#[cfg(test)]
pub(crate) mod test_util {
    use std::path::Path;
    use std::sync::Mutex;

    pub(crate) static CWD_LOCK: Mutex<()> = Mutex::new(());

    pub(crate) fn with_tempdir<F: FnOnce(&Path)>(f: F) {
        let _guard = CWD_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let tmp = tempfile::tempdir().expect("tempdir");
        std::env::set_current_dir(tmp.path()).expect("set_current_dir");
        f(tmp.path());
    }
}
