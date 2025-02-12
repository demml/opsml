use pyo3::prelude::*;
use std::sync::Arc;
use std::thread::sleep;
use std::time::Duration;

#[cfg(feature = "server")]
use opsml_server::{start_server_in_background, stop_server};

#[cfg(feature = "server")]
use tokio::{runtime::Runtime, sync::Mutex, task::JoinHandle};

#[pyclass]
pub struct OpsmlTestServer {
    #[cfg(feature = "server")]
    handle: Arc<Mutex<Option<JoinHandle<()>>>>,
    #[cfg(feature = "server")]
    runtime: Arc<Runtime>,
}

#[pymethods]
impl OpsmlTestServer {
    #[new]
    fn new() -> Self {
        OpsmlTestServer {
            #[cfg(feature = "server")]
            handle: Arc::new(Mutex::new(None)),
            #[cfg(feature = "server")]
            runtime: Arc::new(Runtime::new().unwrap()),
        }
    }

    fn start_server(&mut self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            let handle = self.handle.clone();
            let runtime = self.runtime.clone();
            runtime.spawn(async move {
                let server_handle = start_server_in_background();
                *handle.lock().await = server_handle.lock().await.take();
            });

            let client = reqwest::blocking::Client::new();
            let mut attempts = 0;
            let max_attempts = 5;

            while attempts < max_attempts {
                let res = client.get("http://localhost:3000/opsml/healthcheck").send();
                if let Ok(response) = res {
                    if response.status() == 200 {
                        println!("Opsml Server started successfully");
                        return Ok(());
                    }
                }
                attempts += 1;
                sleep(Duration::from_secs(2));

                // set env vars for OPSML_TRACKING_URI
                std::env::set_var("OPSML_TRACKING_URI", "http://localhost:3000");
            }

            return Err(opsml_error::OpsmlError::new_err(
                "Failed to start Opsml Server",
            ));
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
            let runtime = self.runtime.clone();
            runtime.spawn(async move {
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
