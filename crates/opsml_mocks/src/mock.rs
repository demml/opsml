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
use tokio::{runtime::Runtime, sync::Mutex, task::JoinHandle};

#[cfg(feature = "server")]
use mockito;
#[cfg(feature = "server")]
use scouter_client::RegisteredProfileResponse;
#[cfg(feature = "server")]
use scouter_client::{BinnedMetrics, BinnedPsiFeatureMetrics, SpcDriftFeatures};
#[cfg(feature = "server")]
use serde_json;

use crate::error::TestServerError;
use pyo3::prelude::*;
use pyo3::PyResult;

use std::path::PathBuf;
use std::time::Duration;

#[cfg(feature = "server")]
pub struct ScouterServer {
    pub url: String,
    pub server: mockito::ServerGuard,
}

#[cfg(feature = "server")]
impl ScouterServer {
    pub fn new() -> Self {
        let mut server = mockito::Server::new();

        let register_profile_response = RegisteredProfileResponse {
            space: "space".to_string(),
            name: "name".to_string(),
            version: "version".to_string(),
            status: "success".to_string(),
            active: true,
        };

        // Healthcheck mock
        server
            .mock("GET", "/scouter/healthcheck")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"alive": true}"#)
            .create();

        // auth mocks
        server
            .mock("GET", "/scouter/auth/login")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"token": "my-jwt-token"}"#)
            .create();

        // User mocks
        server
            .mock("POST", "/scouter/user")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "created_user"}"#)
            .create();

        server
            .mock("PUT", "/scouter/user")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "updated_user"}"#)
            .create();

        server
            .mock("DELETE", "/scouter/user")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "deleted_user"}"#)
            .create();

        // Profile mocks
        server
            .mock("POST", "/scouter/profile")
            .match_header("content-type", mockito::Matcher::Any)
            .match_header("authorization", mockito::Matcher::Any)
            .match_body(mockito::Matcher::Any)
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(serde_json::to_string(&register_profile_response).unwrap())
            .create();

        server
            .mock("PUT", "/scouter/profile")
            .match_header("content-type", mockito::Matcher::Any)
            .match_header("authorization", mockito::Matcher::Any)
            .match_body(mockito::Matcher::Any)
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "Profile updated"}"#)
            .create();

        server
            .mock("PUT", "/scouter/profile/status")
            .match_header("content-type", mockito::Matcher::Any)
            .match_header("authorization", mockito::Matcher::Any)
            .match_body(mockito::Matcher::Any)
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"status": "success", "message": "Profile updated"}"#)
            .create();

        // Drift feature mocks
        server
            .mock("GET", "/scouter/drift/spc")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(serde_json::to_string(&SpcDriftFeatures::default()).unwrap())
            .create();

        server
            .mock("GET", "/scouter/drift/psi")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(serde_json::to_string(&BinnedPsiFeatureMetrics::default()).unwrap())
            .create();

        server
            .mock("GET", "/scouter/drift/custom")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(serde_json::to_string(&BinnedMetrics::default()).unwrap())
            .create();

        server
            .mock("GET", "/scouter/drift/llm")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(serde_json::to_string(&BinnedMetrics::default()).unwrap())
            .create();

        server
            .mock("POST", "/scouter/drift")
            .match_query(mockito::Matcher::Any)
            .with_status(200)
            .with_body(
                serde_json::to_string(&scouter_client::ScouterResponse {
                    status: "success".to_string(),
                    message: "Drift records queued for processing".to_string(),
                })
                .unwrap(),
            )
            .create();

        Self {
            url: server.url(),
            server,
        }
    }
}

#[pyclass]
#[allow(dead_code)]
pub struct OpsmlTestServer {
    #[cfg(feature = "server")]
    handle: Arc<Mutex<Option<JoinHandle<()>>>>,

    #[cfg(feature = "server")]
    runtime: Arc<Runtime>,

    #[cfg(feature = "server")]
    scouter_server: Option<ScouterServer>,

    cleanup: bool,

    base_path: Option<PathBuf>,

    root_dir: PathBuf,
}

#[pymethods]
impl OpsmlTestServer {
    #[new]
    #[pyo3(signature = (cleanup = true, base_path = None))]
    fn new(cleanup: bool, base_path: Option<PathBuf>) -> Self {
        let rand = opsml_utils::create_uuid7();
        let root_dir = std::env::current_dir().unwrap().join(rand);
        OpsmlTestServer {
            #[cfg(feature = "server")]
            handle: Arc::new(Mutex::new(None)),
            #[cfg(feature = "server")]
            runtime: Arc::new(Runtime::new().unwrap()),
            #[cfg(feature = "server")]
            scouter_server: None,
            cleanup,
            base_path,
            root_dir,
        }
    }

    #[cfg(feature = "server")]
    pub fn start_mock_scouter(&mut self) -> PyResult<()> {
        let scouter_server = ScouterServer::new();
        std::env::set_var("SCOUTER_SERVER_URI", &scouter_server.url);
        println!("Mock Scouter Server started at {}", scouter_server.url);
        self.scouter_server = Some(scouter_server);
        Ok(())
    }

    #[cfg(feature = "server")]
    pub fn stop_mock_scouter(&mut self) {
        if let Some(server) = self.scouter_server.take() {
            drop(server);
            std::env::remove_var("SCOUTER_SERVER_URI");
        }
        println!("Mock Scouter Server stopped");
    }

    pub fn set_env_vars_for_client(&self, _port: u16) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            std::env::set_var("OPSML_TRACKING_URI", format!("http://localhost:{}", _port));
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
            self.cleanup()?;

            println!("Starting Scouter Server...");
            self.start_mock_scouter()?;

            println!("Starting Opsml Server...");

            // set server env vars
            std::env::set_var("APP_ENV", "dev_server");

            if self.base_path.is_some() {
                std::env::set_var("OPSML_BASE_PATH", self.base_path.as_ref().unwrap());
            }

            let handle = self.handle.clone();
            let runtime = self.runtime.clone();

            let port = match (8000..8010)
                .find(|port| StdTcpListener::bind(("127.0.0.1", *port)).is_ok())
            {
                Some(p) => p,
                None => {
                    return Err(TestServerError::PortNotFound.into());
                }
            };

            std::env::set_var("OPSML_SERVER_PORT", port.to_string());

            let sql_path = format!("sqlite://{}/opsml.db", self.root_dir.display());
            let registry_path = self.root_dir.join("opsml_registries").display().to_string();

            runtime.spawn(async move {
                std::env::set_var("OPSML_TRACKING_URI", sql_path);
                std::env::set_var("OPSML_STORAGE_URI", registry_path);
                let server_handle = start_server_in_background();
                *handle.lock().await = server_handle.lock().await.take();
            });

            let client = reqwest::blocking::Client::new();
            let mut attempts = 0;
            let max_attempts = 30;

            while attempts < max_attempts {
                println!(
                    "Checking if Opsml Server is running at http://localhost:{}/opsml/api/healthcheck",
                    port
                );
                let res = client
                    .get(&format!("http://localhost:{}/opsml/api/healthcheck", port))
                    .send();
                if let Ok(response) = res {
                    if response.status() == 200 {
                        self.set_env_vars_for_client(port)?;
                        println!("Opsml Server started successfully");
                        app_state().reset_app_state().map_err(|e| {
                            TestServerError::CustomError(format!(
                                "Failed to reset app state: {}",
                                e
                            ))
                        })?;
                        return Ok(());
                    }
                } else {
                    let resp_msg = res.unwrap_err().to_string();
                    println!("Opsml Server not yet ready: {}", resp_msg);
                }

                attempts += 1;
                sleep(Duration::from_millis(100 + (attempts * 10)));

                // set env vars for OPSML_TRACKING_URI
            }

            return Err(TestServerError::ServerStartError.into());
        }
        #[cfg(not(feature = "server"))]
        {
            Err(TestServerError::CustomError("Opsml Server feature not enabled".to_string()).into())
        }
    }

    fn stop_server(&mut self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            let handle = self.handle.clone();
            let runtime = self.runtime.clone();
            runtime.spawn(async move {
                stop_server(handle).await;
            });

            std::thread::sleep(Duration::from_millis(500));

            if self.cleanup {
                println!("Cleaning up Opsml Server...");
                self.stop_mock_scouter();
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
        // unset env vars
        self.remove_env_vars_for_client()?;

        if self.root_dir.exists() {
            let max_attempts = 5;
            let mut attempt = 0;

            while attempt < max_attempts {
                match std::fs::remove_dir_all(&self.root_dir) {
                    Ok(_) => return Ok(()),
                    Err(e) => {
                        if attempt == max_attempts - 1 {
                            tracing::error!(
                                "Failed to remove root directory after {max_attempts} attempts: {e}",
                            );
                            return Err(TestServerError::CustomError(format!(
                                "Failed to remove root directory: {e}",
                            ))
                            .into());
                        }
                        // Wait before retrying
                        std::thread::sleep(Duration::from_millis(100 * (attempt + 1) as u64));
                        attempt += 1;
                    }
                }
            }
        }

        Ok(())
    }

    fn __enter__(mut self_: PyRefMut<Self>) -> PyResult<PyRefMut<Self>> {
        self_.start_server()?;
        Ok(self_)
    }

    fn __exit__(
        &mut self,
        _exc_type: Py<PyAny>,
        _exc_value: Py<PyAny>,
        _traceback: Py<PyAny>,
    ) -> PyResult<()> {
        self.stop_server()
    }
}

// create context manager that can be use in server test to cleanup resources

#[pyclass]
pub struct OpsmlServerContext {
    #[cfg(feature = "server")]
    scouter_server: Option<ScouterServer>,
}

#[pymethods]
impl OpsmlServerContext {
    #[new]
    fn new() -> Self {
        OpsmlServerContext {
            #[cfg(feature = "server")]
            scouter_server: None,
        }
    }

    #[cfg(feature = "server")]
    pub fn start_mock_scouter(&mut self) -> PyResult<()> {
        let scouter_server = ScouterServer::new();
        std::env::set_var("SCOUTER_SERVER_URI", &scouter_server.url);
        println!("Mock Scouter Server started at {}", scouter_server.url);
        self.scouter_server = Some(scouter_server);
        Ok(())
    }

    #[cfg(feature = "server")]
    pub fn stop_mock_scouter(&mut self) {
        if let Some(server) = self.scouter_server.take() {
            drop(server);
            std::env::remove_var("SCOUTER_SERVER_URI");
        }
        println!("Mock Scouter Server stopped");
    }

    fn __enter__(&mut self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            #[cfg(feature = "server")]
            self.start_mock_scouter()?;

            app_state().reset_app_state().map_err(|e| {
                TestServerError::CustomError(format!("Failed to reset app state: {e}"))
            })?;
            reset_storage_client().map_err(|e| {
                TestServerError::CustomError(format!("Failed to reset storage client: {e}"))
            })?;
        }

        self.cleanup()?;

        Ok(())
    }

    #[getter]
    pub fn server_uri(&self) -> PyResult<String> {
        #[cfg(feature = "server")]
        {
            if let Some(server) = &self.scouter_server {
                Ok(server.url.clone())
            } else {
                Err(TestServerError::CustomError("Scouter server not started".to_string()).into())
            }
        }
        #[cfg(not(feature = "server"))]
        {
            Err(TestServerError::CustomError("Server feature not enabled".to_string()).into())
        }
    }

    fn __exit__(
        &mut self,
        _exc_type: Py<PyAny>,
        _exc_value: Py<PyAny>,
        _traceback: Py<PyAny>,
    ) -> PyResult<()> {
        #[cfg(feature = "server")]
        self.stop_mock_scouter();

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
