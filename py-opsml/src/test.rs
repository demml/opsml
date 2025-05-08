#[cfg(feature = "server")]
use opsml_server::{start_server_in_background, stop_server};
#[cfg(feature = "server")]
use opsml_state::app_state;
#[cfg(feature = "server")]
use opsml_storage::reset_storage_client;
#[cfg(feature = "server")]
use std::net::TcpListener as StdTcpListener;
#[cfg(feature = "server")]
use std::sync::Arc;
#[cfg(feature = "server")]
use std::thread::sleep;
#[cfg(feature = "server")]
use std::time::Duration;
#[cfg(feature = "server")]
use tokio::{runtime::Runtime, sync::Mutex, task::JoinHandle};

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::PyErr;
use pyo3::PyResult;
use std::path::PathBuf;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum TestServerError {
    #[error("Failed to find available port")]
    PortNotFound,

    #[error("Failed to start Opsml Server")]
    ServerStartError,

    #[error("Failed to set environment variables for client")]
    SetEnvVarsError,

    #[error("{0}")]
    CustomError(String),
}

impl From<TestServerError> for PyErr {
    fn from(err: TestServerError) -> PyErr {
        let msg = err.to_string();
        PyRuntimeError::new_err(msg)
    }
}

#[pyclass]
#[allow(dead_code)]
pub struct OpsmlTestServer {
    #[cfg(feature = "server")]
    handle: Arc<Mutex<Option<JoinHandle<()>>>>,
    #[cfg(feature = "server")]
    runtime: Arc<Runtime>,
    cleanup: bool,
    base_path: Option<PathBuf>,
}

#[pymethods]
impl OpsmlTestServer {
    #[new]
    #[pyo3(signature = (cleanup = true, base_path = None))]
    fn new(cleanup: bool, base_path: Option<PathBuf>) -> Self {
        OpsmlTestServer {
            #[cfg(feature = "server")]
            handle: Arc::new(Mutex::new(None)),
            #[cfg(feature = "server")]
            runtime: Arc::new(Runtime::new().unwrap()),
            cleanup,
            base_path,
        }
    }

    pub fn set_env_vars_for_client(&self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            std::env::set_var("OPSML_TRACKING_URI", "http://localhost:3000");
            std::env::set_var("APP_ENV", "dev_client");
            Ok(())
        }
        #[cfg(not(feature = "server"))]
        {
            Err(TestServerError::CustomError("Opsml Server feature not enabled".to_string()).into())
        }
    }

    fn start_server(&mut self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            println!("Starting Opsml Server...");
            self.cleanup()?;

            // set server env vars
            std::env::set_var("APP_ENV", "dev_server");

            if self.base_path.is_some() {
                std::env::set_var("OPSML_BASE_PATH", self.base_path.as_ref().unwrap());
            }

            let handle = self.handle.clone();
            let runtime = self.runtime.clone();

            let port = match (3000..3010)
                .find(|port| StdTcpListener::bind(("127.0.0.1", *port)).is_ok())
            {
                Some(p) => p,
                None => {
                    return Err(TestServerError::PortNotFound.into());
                }
            };

            std::env::set_var("OPSML_SERVER_PORT", port.to_string());

            runtime.spawn(async move {
                let server_handle = start_server_in_background();
                *handle.lock().await = server_handle.lock().await.take();
            });

            let client = reqwest::blocking::Client::new();
            let mut attempts = 0;
            let max_attempts = 20;

            while attempts < max_attempts {
                let res = client
                    .get("http://localhost:3000/opsml/api/healthcheck")
                    .send();
                if let Ok(response) = res {
                    if response.status() == 200 {
                        self.set_env_vars_for_client()?;
                        println!("Opsml Server started successfully");
                        app_state().reset_app_state().map_err(|e| {
                            TestServerError::CustomError(format!(
                                "Failed to reset app state: {}",
                                e
                            ))
                        })?;
                        return Ok(());
                    }
                }
                attempts += 1;
                sleep(Duration::from_millis(100));

                // set env vars for OPSML_TRACKING_URI
            }

            return Err(TestServerError::ServerStartError.into());
        }
        #[cfg(not(feature = "server"))]
        {
            Err(TestServerError::CustomError("Opsml Server feature not enabled".to_string()).into())
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

            if self.cleanup {
                println!("Cleaning up Opsml Server...");
                self.cleanup()?;
            }

            Ok(())
        }
        #[cfg(not(feature = "server"))]
        {
            Err(TestServerError::CustomError("Opsml Server feature not enabled".to_string()).into())
        }
    }

    pub fn remove_env_vars_for_client(&self) -> PyResult<()> {
        std::env::remove_var("APP_ENV");
        std::env::remove_var("OPSML_TRACKING_URI");
        std::env::remove_var("OPSML_SERVER_PORT");
        std::env::remove_var("OPSML_BASE_PATH");
        Ok(())
    }

    fn cleanup(&self) -> PyResult<()> {
        let current_dir = std::env::current_dir().unwrap();
        let db_file = current_dir.join("opsml.db");
        let storage_dir = current_dir.join("opsml_registries");

        // unset env vars
        self.remove_env_vars_for_client()?;

        if db_file.exists() {
            std::fs::remove_file(db_file).unwrap();
        }

        if storage_dir.exists() {
            std::fs::remove_dir_all(storage_dir).unwrap();
        }

        Ok(())
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

// create context manager that can be use in server test to cleanup resources

#[pyclass]
pub struct OpsmlServerContext {}

#[pymethods]
impl OpsmlServerContext {
    #[new]
    fn new() -> Self {
        OpsmlServerContext {}
    }

    fn __enter__(&self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            app_state().reset_app_state().map_err(|e| {
                TestServerError::CustomError(format!("Failed to reset app state: {}", e))
            })?;
            reset_storage_client().map_err(|e| {
                TestServerError::CustomError(format!("Failed to reset storage client: {}", e))
            })?;
        }

        self.cleanup()?;
        Ok(())
    }

    fn __exit__(
        &self,
        _exc_type: PyObject,
        _exc_value: PyObject,
        _traceback: PyObject,
    ) -> PyResult<()> {
        self.cleanup()?;
        Ok(())
    }

    fn cleanup(&self) -> PyResult<()> {
        let current_dir = std::env::current_dir().unwrap();
        let db_file = current_dir.join("opsml.db");
        let storage_dir = current_dir.join("opsml_registries");

        if db_file.exists() {
            std::fs::remove_file(db_file).unwrap();
        }

        if storage_dir.exists() {
            std::fs::remove_dir_all(storage_dir).unwrap();
        }

        Ok(())
    }
}

#[pymodule]
pub fn test(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OpsmlTestServer>()?;
    m.add_class::<OpsmlServerContext>()?;
    Ok(())
}
