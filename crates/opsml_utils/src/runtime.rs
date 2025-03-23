// OpsML relies on both sync and async code in order to run. In order to make async compatible with
// pyo3, we need to create a tokio runtime that is separate from the main python runtime in order to prevent
// deadlocks. This module is responsible for creating a shared and reusable runtime that can be shared across
// public python interfaces.

use opsml_error::OpsmlError;
use std::sync::{Arc, OnceLock};
use tokio::runtime::{Builder, Runtime};
use tracing::error;

static RUNTIME: OnceLock<Arc<Runtime>> = OnceLock::new();

pub fn get_runtime() -> &'static Arc<Runtime> {
    RUNTIME.get_or_init(|| {
        Arc::new(
            Builder::new_multi_thread()
                .enable_all()
                .thread_name("opsml-worker")
                .thread_stack_size(3 * 1024 * 1024)
                .build()
                .map_err(|e| {
                    error!("Failed to create runtime: {}", e);
                    OpsmlError::new_err(e.to_string())
                })
                .unwrap(),
        )
    })
}
