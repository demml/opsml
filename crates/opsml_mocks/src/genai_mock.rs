#[cfg(feature = "server")]
use mockito;
#[cfg(feature = "server")]
use potato_head::agents::provider::openai::OpenAIChatResponse;
#[cfg(feature = "server")]
use serde_json;

use pyo3::prelude::*;
use pyo3::PyResult;

#[cfg(feature = "server")]
const OPENAI_CHAT_COMPLETION_RESPONSE: &str =
    include_str!("assets/openai_chat_completion_response.json");

#[cfg(feature = "server")]
const OPENAI_CHAT_STRUCTURED_RESPONSE: &str =
    include_str!("assets/openai/chat_completion_structured_response.json");

#[cfg(feature = "server")]
const OPENAI_CHAT_STRUCTURED_SCORE_RESPONSE: &str =
    include_str!("assets/openai/chat_completion_structured_score_response.json");

#[cfg(feature = "server")]
pub struct OpenAIMock {
    pub url: String,
    pub server: mockito::ServerGuard,
}

#[cfg(feature = "server")]
impl OpenAIMock {
    pub fn new() -> Self {
        let mut server = mockito::Server::new();
        // load the OpenAI chat completion response
        let chat_msg_response: OpenAIChatResponse =
            serde_json::from_str(OPENAI_CHAT_COMPLETION_RESPONSE).unwrap();
        let chat_structured_response: OpenAIChatResponse =
            serde_json::from_str(OPENAI_CHAT_STRUCTURED_RESPONSE).unwrap();
        let chat_structured_score_response: OpenAIChatResponse =
            serde_json::from_str(OPENAI_CHAT_STRUCTURED_SCORE_RESPONSE).unwrap();

        server
            .mock("POST", "/v1/chat/completions")
            .match_body(mockito::Matcher::PartialJson(serde_json::json!({
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "Score",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "score": { "type": "integer" },
                                "reason": { "type": "string" },
                            },
                            "required": ["score", "reason"]
                        },
                        "strict": true
                    }

                }
            })))
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(serde_json::to_string(&chat_structured_score_response).unwrap())
            .create();

        server
            .mock("POST", "/v1/chat/completions")
            .match_body(mockito::Matcher::PartialJson(serde_json::json!({
                "response_format": {
                    "type": "json_schema"
                }
            })))
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(serde_json::to_string(&chat_structured_response).unwrap())
            .create();

        // Openai chat completion mock
        server
            .mock("POST", "/v1/chat/completions")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(serde_json::to_string(&chat_msg_response).unwrap())
            .create();

        Self {
            url: server.url(),
            server,
        }
    }
}

#[pyclass]
#[allow(dead_code)]
pub struct OpenAITestServer {
    #[cfg(feature = "server")]
    openai_server: Option<OpenAIMock>,
}

#[pymethods]
impl OpenAITestServer {
    #[new]
    fn new() -> Self {
        OpenAITestServer {
            #[cfg(feature = "server")]
            openai_server: None,
        }
    }

    #[cfg(feature = "server")]
    pub fn start_mock_server(&mut self) -> PyResult<()> {
        let openai_server = OpenAIMock::new();
        println!("Mock OpenAI Server started at {}", openai_server.url);
        self.openai_server = Some(openai_server);
        Ok(())
    }

    #[cfg(feature = "server")]
    pub fn stop_mock_server(&mut self) {
        if let Some(server) = self.openai_server.take() {
            drop(server);
            std::env::remove_var("OPENAI_API_URL");
            std::env::remove_var("OPENAI_API_KEY");
        }
        println!("Mock OpenAI Server stopped");
    }

    pub fn set_env_vars_for_client(&self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            std::env::set_var("APP_ENV", "dev_client");
            std::env::set_var("OPENAI_API_KEY", "test_key");
            std::env::set_var(
                "OPENAI_API_URL",
                self.openai_server.as_ref().unwrap().url.clone(),
            );
            Ok(())
        }
        #[cfg(not(feature = "server"))]
        {
            Err(crate::error::TestServerError::CustomError(
                "Opsml Server feature not enabled".to_string(),
            )
            .into())
        }
    }

    fn start_server(&mut self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            self.cleanup()?;

            println!("Starting Mock GenAI Server...");
            self.start_mock_server()?;
            self.set_env_vars_for_client()?;

            // set server env vars
            std::env::set_var("APP_ENV", "dev_server");

            Ok(())
        }
        #[cfg(not(feature = "server"))]
        {
            Err(crate::error::TestServerError::CustomError(
                "GenAI Server feature not enabled".to_string(),
            )
            .into())
        }
    }

    fn stop_server(&mut self) -> PyResult<()> {
        #[cfg(feature = "server")]
        {
            self.cleanup()?;

            Ok(())
        }
        #[cfg(not(feature = "server"))]
        {
            Err(crate::error::TestServerError::CustomError(
                "GenAI Server feature not enabled".to_string(),
            )
            .into())
        }
    }

    pub fn remove_env_vars_for_client(&self) -> PyResult<()> {
        std::env::remove_var("OPENAI_API_URI");
        std::env::remove_var("OPENAI_API_KEY");
        Ok(())
    }

    fn cleanup(&self) -> PyResult<()> {
        // unset env vars
        self.remove_env_vars_for_client()?;

        Ok(())
    }

    fn __enter__(mut self_: PyRefMut<Self>) -> PyResult<PyRefMut<Self>> {
        self_.start_server()?;
        Ok(self_)
    }

    fn __exit__(
        &mut self,
        _exc_type: PyObject,
        _exc_value: PyObject,
        _traceback: PyObject,
    ) -> PyResult<()> {
        self.stop_server()
    }
}
