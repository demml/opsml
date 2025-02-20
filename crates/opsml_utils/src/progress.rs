use indicatif::{MultiProgress, ProgressBar, ProgressStyle};
use opsml_error::{ProgressError, UtilError};

pub struct Progress {
    multi_progress: MultiProgress,
    style: ProgressStyle,
}

impl Progress {
    pub fn new() -> Result<Self, UtilError> {
        let m = MultiProgress::new();
        let style = ProgressStyle::with_template(
            "[{elapsed_precise}] {bar:40.green/magenta} {pos:>7}/{len:7} {msg}",
        )
        .map_err(|e| UtilError::Error(format!("Failed to create progress style: {e}")))?
        .progress_chars("--");

        Ok(Progress {
            multi_progress: m,
            style,
        })
    }

    pub fn create_bar(&self, message: String, total: u64) -> ProgressBar {
        let bar = self.multi_progress.add(ProgressBar::new(total));
        bar.set_style(self.style.clone());
        bar.set_message(message);
        bar
    }

    pub fn finish(&self) -> Result<(), ProgressError> {
        self.multi_progress
            .clear()
            .map_err(|e| ProgressError::Error(format!("Failed to clear progress bar: {e}")))?;

        Ok(())
    }
}

impl Default for Progress {
    fn default() -> Self {
        Self::new().unwrap()
    }
}
