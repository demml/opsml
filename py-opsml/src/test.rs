use pyo3::prelude::*;
use std::sync::Arc;

#[cfg(feature = "server")]
use opsml_server::{start_server_in_background, stop_server};

#[cfg(feature = "server")]
use tokio::{sync::Mutex, task::JoinHandle};

#[pyclass]
pub struct OpsmlTestServer {
    #[cfg(feature = "server")]
    handle: Arc<Mutex<Option<JoinHandle<()>>>>,
}

#[pymethods]
impl OpsmlTestServer {
    #[new]
    fn new() -> Self {
        OpsmlTestServer {
            #[cfg(feature = "server")]
            handle: Arc::new(Mutex::new(None)),
        }
    }

    fn start_server(&mut self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            self.handle = start_server_in_background();
            Ok(())
        }
        #[cfg(not(feature = "server"))]
        {
            return Err(opsml_error::OpsmlError::new_err(
                "Opsml Server feature not enabled",
            ));
        }
    }

    fn stop_server(&self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            let handle = self.handle.clone();
            tokio::spawn(async move {
                stop_server(handle).await;
            });
            Ok(())
        }
        #[cfg(not(feature = "server"))]
        {
            return Err(opsml_error::OpsmlError::new_err(
                "Opsml Server feature not enabled",
            ));
        }
    }
}

#[pymodule]
pub fn test(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OpsmlTestServer>()?;
    Ok(())
}
