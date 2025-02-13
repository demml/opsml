use pyo3::prelude::*;
use std::sync::Arc;
use std::thread::sleep;
use std::time::Duration;

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

    fn set_env_vars_for_client(&self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            std::env::set_var("OPSML_TRACKING_URI", "http://localhost:3000");
            Ok(())
        }
        #[cfg(not(feature = "server"))]
        {
            return Err(opsml_error::OpsmlError::new_err(
                "Opsml Server feature not enabled",
            ));
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
                        self.set_env_vars_for_client()?;
                        println!("Opsml Server started successfully");
                        return Ok(());
                    }
                }
                attempts += 1;
                sleep(Duration::from_secs(2));

                // set env vars for OPSML_TRACKING_URI
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

    fn __enter__(mut self_: PyRefMut<Self>) -> PyResult<PyRefMut<Self>> {
        self_.start_server()?;
        Ok(self_)
    }

    fn __exit__(
        &self,
        _exc_type: PyObject,
        _exc_value: PyObject,
        _traceback: PyObject,
    ) -> PyResult<()> {
        self.stop_server()
    }
}

#[pymodule]
pub fn test(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OpsmlTestServer>()?;
    Ok(())
}
