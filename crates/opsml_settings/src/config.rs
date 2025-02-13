use base64::prelude::*;
use opsml_error::StorageError;
use opsml_types::{SqlType, StorageType};
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use rusty_logging::logger::LoggingConfig;
use serde::Serialize;
use std::default::Default;
use std::env;
use std::path::PathBuf;

/// ApiSettings for use with ApiClient
#[pyclass]
#[derive(Debug, Clone)]
pub struct ApiSettings {
    pub base_url: String,
    pub use_auth: bool,
    pub opsml_dir: String,
    pub scouter_dir: String,
    pub username: String,
    pub password: String,
    pub auth_token: String,
    pub prod_token: Option<String>,
}

/// StorageSettings for used with all storage clients
#[pyclass]
#[derive(Debug, Clone)]
pub struct OpsmlStorageSettings {
    #[pyo3(get)]
    pub storage_uri: String,

    #[pyo3(get)]
    pub client_mode: bool,

    #[pyo3(get)]
    pub api_settings: ApiSettings,

    #[pyo3(get)]
    pub storage_type: StorageType,

    pub encryption_key: Vec<u8>,
}

#[pymethods]
impl OpsmlStorageSettings {
    /// Create a new OpsmlStorageSettings instance
    ///
    /// # Returns
    ///
    /// `OpsmlStorageSettings`: A new instance of OpsmlStorageSettings
    #[new]
    #[pyo3(signature = (storage_uri="./opsml_registries", client_mode=false))]
    pub fn new(storage_uri: &str, client_mode: bool) -> Self {
        OpsmlStorageSettings {
            encryption_key: vec![],
            storage_uri: storage_uri.to_string(),
            client_mode,
            api_settings: ApiSettings {
                base_url: "".to_string(),
                use_auth: false,
                opsml_dir: "".to_string(),
                scouter_dir: "".to_string(),
                username: "guest".to_string(),
                password: "guest".to_string(),
                auth_token: "".to_string(),
                prod_token: None,
            },
            storage_type: StorageType::Local,
        }
    }
}

/// DatabaseSettings for used with all database clients
#[pyclass]
#[derive(Debug, Clone, Serialize)]
pub struct DatabaseSettings {
    pub connection_uri: String,
    pub max_connections: u32,
    pub sql_type: SqlType,
}

#[pyclass]
#[derive(Debug, Clone, Default, Serialize)]
pub struct AuthSettings {
    pub enabled: bool,
    pub jwt_secret: String,
    pub refresh_secret: String,
    pub username: String,
    pub password: String,
    pub prod_token: Option<String>,
}

#[pyclass]
#[derive(Debug, Clone, Default, Serialize)]
pub struct ScouterSettings {
    pub server_uri: Option<String>,
    pub username: Option<String>,
    pub password: Option<String>,
    pub auth: bool,
}

/// OpsmlConfig for use with both server and client implementations
/// OpsmlConfig is the main primary configuration struct for the Opsml system
/// Based on provided env variables, it will be used to determine if opsml is running in client or server mode.
#[pyclass]
#[derive(Debug, Clone, Serialize)]
pub struct OpsmlConfig {
    pub app_name: String,
    pub app_env: String,
    pub app_version: String,
    pub opsml_storage_uri: String,
    pub opsml_tracking_uri: String,
    pub opsml_proxy_root: String,
    pub opsml_registry_path: String,
    pub scouter_settings: ScouterSettings,
    pub auth_settings: AuthSettings,
    pub database_settings: DatabaseSettings,
    pub client_mode: bool,
    pub logging_config: LoggingConfig,
}

impl Default for OpsmlConfig {
    fn default() -> Self {
        let opsml_storage_uri =
            env::var("OPSML_STORAGE_URI").unwrap_or_else(|_| "./opsml_registries".to_string());

        let opsml_tracking_uri = env::var("OPSML_TRACKING_URI").unwrap_or_else(|_| {
            let mut current_dir = env::current_dir().expect("Failed to get current directory");
            current_dir.push("opsml.db");
            format!(
                "sqlite://{}",
                current_dir
                    .to_str()
                    .expect("Failed to convert path to string")
            )
        });

        let using_client = OpsmlConfig::is_using_client(&opsml_tracking_uri);

        // set scouter settings
        let scouter_settings = ScouterSettings {
            server_uri: env::var("SCOUTER_SERVER_URI").ok(),
            username: env::var("SCOUTER_USERNAME").ok(),
            password: env::var("SCOUTER_PASSWORD").ok(),
            auth: env::var("SCOUTER_AUTH")
                .unwrap_or_else(|_| "false".to_string())
                .parse()
                .unwrap_or(false),
        };

        // set auth settings
        let auth_settings = AuthSettings {
            jwt_secret: env::var("OPSML_ENCRYPT_SECRET").unwrap_or_else(|_| generate_jwt_secret()),
            refresh_secret: env::var("OPSML_REFRESH_SECRET")
                .unwrap_or_else(|_| generate_jwt_secret()),

            username: env::var("OPSML_USERNAME").unwrap_or("guest".to_string()),
            password: env::var("OPSML_PASSWORD").unwrap_or("guest".to_string()),
            enabled: env::var("OPSML_AUTH")
                .unwrap_or_else(|_| "false".to_string())
                .parse()
                .unwrap_or(false),
            prod_token: env::var("OPSML_PROD_TOKEN").ok(),
        };

        // set database settings
        let database_settings = DatabaseSettings {
            connection_uri: opsml_tracking_uri.clone(),
            max_connections: env::var("OPSML_MAX_POOL_CONNECTIONS")
                .unwrap_or_else(|_| "10".to_string())
                .parse()
                .unwrap_or(10),
            sql_type: OpsmlConfig::get_sql_type(&opsml_tracking_uri),
        };

        let logging_config = LoggingConfig::json_default();

        OpsmlConfig {
            app_name: "opsml".to_string(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            app_version: env!("CARGO_PKG_VERSION").to_string(),
            opsml_storage_uri: OpsmlConfig::set_opsml_storage_uri(opsml_storage_uri, using_client),
            opsml_tracking_uri,

            opsml_proxy_root: "opsml-root:/".to_string(),
            opsml_registry_path: env::var("OPSML_REGISTRY_PATH")
                .unwrap_or_else(|_| "model_registry".to_string()),

            database_settings,
            scouter_settings,
            auth_settings,
            client_mode: using_client,
            logging_config,
        }
    }
}

fn generate_jwt_secret() -> String {
    // always creates a deterministic key
    // this should be replaced when using AUTH and Encryption in production
    let mut key = [0u8; 32];
    for i in 0..32 {
        key[i] = i as u8;
    }

    BASE64_STANDARD.encode(&key)
}

impl OpsmlConfig {
    pub fn set_opsml_storage_uri(opsml_storage_uri: String, using_client: bool) -> String {
        if using_client {
            return opsml_storage_uri;
        }

        if opsml_storage_uri.starts_with("gs://")
            || opsml_storage_uri.starts_with("s3://")
            || opsml_storage_uri.starts_with("az://")
        {
            opsml_storage_uri
        } else {
            let path = PathBuf::from(opsml_storage_uri);

            // check if the path exists, if not create it
            if !path.exists() {
                std::fs::create_dir_all(&path).unwrap();
            }

            path.canonicalize().unwrap().to_str().unwrap().to_string()
        }
    }

    pub fn is_using_client(opsml_tracking_uri: &str) -> bool {
        opsml_tracking_uri.to_lowercase().trim().starts_with("http")
    }

    pub fn storage_root(&self) -> String {
        if !self.client_mode {
            let storage_uri_lower = self.opsml_storage_uri.to_lowercase();
            if let Some(stripped) = storage_uri_lower.strip_prefix("gs://") {
                stripped.to_string()
            } else if let Some(stripped) = storage_uri_lower.strip_prefix("s3://") {
                stripped.to_string()
            } else if let Some(stripped) = storage_uri_lower.strip_prefix("az://") {
                stripped.to_string()
            } else {
                storage_uri_lower
            }
        } else {
            self.opsml_proxy_root.clone()
        }
    }

    fn get_storage_type(&self) -> StorageType {
        let storage_uri_lower = self.opsml_storage_uri.to_lowercase();
        if storage_uri_lower.starts_with("gs://") {
            StorageType::Google
        } else if storage_uri_lower.starts_with("s3://") {
            StorageType::Aws
        } else if storage_uri_lower.starts_with("az://") {
            StorageType::Azure
        } else {
            StorageType::Local
        }
    }

    fn get_sql_type(tracking_uri: &str) -> SqlType {
        let tracking_uri_lower = tracking_uri.to_lowercase();
        if tracking_uri_lower.starts_with("postgres") {
            SqlType::Postgres
        } else if tracking_uri_lower.starts_with("mysql") {
            SqlType::MySql
        } else {
            SqlType::Sqlite
        }
    }

    /// Get the storage settings for the OpsmlConfig
    pub fn storage_settings(&self) -> Result<OpsmlStorageSettings, StorageError> {
        Ok(OpsmlStorageSettings {
            encryption_key: BASE64_STANDARD
                .decode(self.auth_settings.jwt_secret.clone())
                .map_err(|e| StorageError::Error(e.to_string()))?,
            storage_uri: self.opsml_storage_uri.clone(),
            client_mode: self.client_mode,
            storage_type: self.get_storage_type(),
            api_settings: ApiSettings {
                base_url: self.opsml_tracking_uri.clone(),
                use_auth: self.auth_settings.enabled,
                opsml_dir: "opsml".to_string(),
                scouter_dir: "scouter".to_string(),
                username: self.auth_settings.username.clone(),
                password: self.auth_settings.password.clone(),
                auth_token: "".to_string(),
                prod_token: self.auth_settings.prod_token.clone(),
            },
        })
    }
}

#[pymethods]
impl OpsmlConfig {
    /// Create a new OpsmlConfig instance
    ///
    /// # Returns
    ///
    /// `OpsmlConfig`: A new instance of OpsmlConfig
    #[new]
    #[pyo3(signature = (client_mode=None))]
    pub fn new(client_mode: Option<bool>) -> Self {
        let mut config = OpsmlConfig::default();

        if let Some(client_mode) = client_mode {
            config.client_mode = client_mode;
        }

        config
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[cfg(test)]
mod tests {
    use std::path::Path;

    use super::*;

    fn cleanup() {
        // remove the directory
        // silently ignore errors
        std::fs::remove_dir_all("./test-bucket").ok();
        std::fs::remove_dir_all("./opsml_registries").ok();
    }

    #[test]
    fn test_generate_jwt_secret() {
        let jwt_secret = generate_jwt_secret();
        assert_eq!(jwt_secret.len(), 32);
    }

    #[test]
    fn test_set_opsml_storage_uri() {
        let opsml_storage_uri = "gs://test-bucket".to_string();
        let result = OpsmlConfig::set_opsml_storage_uri(opsml_storage_uri, false);
        assert_eq!(result, "gs://test-bucket");

        let opsml_storage_uri = "s3://test-bucket".to_string();
        let result = OpsmlConfig::set_opsml_storage_uri(opsml_storage_uri, false);
        assert_eq!(result, "s3://test-bucket");

        let opsml_storage_uri = "az://test-bucket".to_string();
        let result = OpsmlConfig::set_opsml_storage_uri(opsml_storage_uri, false);
        assert_eq!(result, "az://test-bucket");

        let opsml_storage_uri = "./test-bucket".to_string();
        let result = OpsmlConfig::set_opsml_storage_uri(opsml_storage_uri, false);
        assert_eq!(
            result,
            Path::new("./test-bucket")
                .canonicalize()
                .unwrap()
                .to_str()
                .unwrap()
        );

        // remove the directory
        std::fs::remove_dir_all("./test-bucket").unwrap();
    }

    #[test]
    fn test_is_tracking_local() {
        let opsml_config = OpsmlConfig {
            opsml_tracking_uri: "sqlite:///opsml.db".to_string(),
            ..Default::default()
        };
        assert!(opsml_config.client_mode);

        let opsml_config = OpsmlConfig {
            opsml_tracking_uri: "http://localhost:5000".to_string(),
            ..Default::default()
        };
        assert!(!opsml_config.client_mode);

        cleanup();
    }

    #[test]
    fn test_storage_root() {
        let opsml_config = OpsmlConfig {
            opsml_storage_uri: "gs://test-bucket".to_string(),
            ..Default::default()
        };
        assert_eq!(opsml_config.storage_root(), "test-bucket");

        let opsml_config = OpsmlConfig {
            opsml_storage_uri: "s3://test-bucket".to_string(),
            ..Default::default()
        };
        assert_eq!(opsml_config.storage_root(), "test-bucket");

        let opsml_config = OpsmlConfig {
            opsml_storage_uri: "az://test-bucket".to_string(),
            ..Default::default()
        };

        assert_eq!(opsml_config.storage_root(), "test-bucket");

        let opsml_config = OpsmlConfig {
            opsml_storage_uri: "./test-bucket".to_string(),
            ..Default::default()
        };

        assert_eq!(opsml_config.storage_root(), "./test-bucket");

        let opsml_config = OpsmlConfig {
            opsml_tracking_uri: "http://localhost:5000".to_string(),
            opsml_storage_uri: "gs://test-bucket".to_string(),
            opsml_proxy_root: "opsml-root:/".to_string(),
            ..Default::default()
        };

        assert_eq!(opsml_config.storage_root(), "opsml-root:/");

        let opsml_config = OpsmlConfig {
            opsml_tracking_uri: "http://localhost:5000".to_string(),
            opsml_storage_uri: "s3://test-bucket".to_string(),
            opsml_proxy_root: "opsml-root:/".to_string(),
            ..Default::default()
        };

        assert_eq!(opsml_config.storage_root(), "opsml-root:/");
        cleanup();
    }

    #[test]
    fn test_auth_settings() {
        let opsml_config = OpsmlConfig {
            auth_settings: AuthSettings {
                enabled: true,
                ..Default::default()
            },
            ..Default::default()
        };
        assert!(opsml_config.auth_settings.enabled);

        let opsml_config = OpsmlConfig {
            auth_settings: AuthSettings {
                enabled: false,
                ..Default::default()
            },
            ..Default::default()
        };

        assert!(!opsml_config.auth_settings.enabled);
        cleanup();
    }

    #[test]
    fn test_default() {
        let opsml_config = OpsmlConfig::default();
        assert_eq!(opsml_config.app_name, "opsml");
        assert_eq!(opsml_config.app_env, "development");
        assert_eq!(opsml_config.app_version, env!("CARGO_PKG_VERSION"));
        assert_eq!(
            opsml_config.opsml_storage_uri,
            Path::new("./opsml_registries")
                .canonicalize()
                .unwrap()
                .to_str()
                .unwrap()
        );
        assert_eq!(opsml_config.opsml_tracking_uri, "sqlite:///opsml.db");
        assert_eq!(
            opsml_config.auth_settings.prod_token,
            Some("staging".to_string())
        );
        assert_eq!(opsml_config.opsml_proxy_root, "opsml-root:/");
        assert_eq!(opsml_config.opsml_registry_path, "model_registry");

        assert_eq!(opsml_config.auth_settings.jwt_secret.len(), 32);
        assert_eq!(opsml_config.auth_settings.username, "guest");
        assert_eq!(opsml_config.auth_settings.password, "guest");
        assert_eq!(opsml_config.scouter_settings.server_uri, None);
        assert_eq!(opsml_config.scouter_settings.username, None);
        assert_eq!(opsml_config.scouter_settings.password, None);
        assert!(!opsml_config.scouter_settings.auth);
        assert!(!opsml_config.auth_settings.enabled);

        cleanup();
    }
}
