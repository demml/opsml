use crate::error::SettingsError;
use base64::prelude::*;
use opsml_types::{SqlType, StorageType};
use rusty_logging::LogLevel;
use rusty_logging::logger::{LoggingConfig, WriteLevel};
use serde::Serialize;
use std::default::Default;
use std::env;
use std::path::PathBuf;
use std::str::FromStr;
use tracing::warn;

#[derive(Debug, Clone, Serialize, PartialEq)]
pub enum OpsmlMode {
    Client,
    Server,
}

#[derive(Debug, Clone)]
pub struct ApiSettings {
    pub base_url: String,
    pub opsml_dir: String,
    pub username: String,
    pub password: String,
    pub prod_token: Option<String>,
    pub use_sso: bool,
}

/// StorageSettings for used with all storage clients
#[derive(Debug, Clone)]
pub struct OpsmlStorageSettings {
    pub storage_uri: String,
    pub api_settings: ApiSettings,
    pub storage_type: StorageType,
    pub encryption_key: Vec<u8>,
}

impl OpsmlStorageSettings {
    /// Create a new OpsmlStorageSettings instance
    ///
    /// # Returns
    ///
    /// `OpsmlStorageSettings`: A new instance of OpsmlStorageSettings
    pub fn new(storage_uri: &str) -> Self {
        OpsmlStorageSettings {
            encryption_key: vec![],
            storage_uri: storage_uri.to_string(),
            api_settings: ApiSettings {
                base_url: "".to_string(),
                opsml_dir: "".to_string(),
                username: "guest".to_string(),
                password: "guest".to_string(),
                use_sso: false,
                prod_token: None,
            },
            storage_type: StorageType::Local,
        }
    }
}

/// DatabaseSettings for used with all database clients
#[derive(Debug, Clone, Serialize)]
pub struct DatabaseSettings {
    pub connection_uri: String,
    pub max_connections: u32,
    pub sql_type: SqlType,
}

#[derive(Debug, Clone, Default, Serialize)]
pub struct AuthSettings {
    pub jwt_secret: String,
    pub refresh_secret: String,
    pub username: String,
    pub password: String,
    pub prod_token: Option<String>,
    pub scouter_secret: String,
    pub use_sso: bool,
}

#[derive(Debug, Clone, Default, Serialize)]
pub struct ScouterSettings {
    pub server_uri: String,

    // Token used to sync users across Opsml and Scouter
    pub bootstrap_token: String,
}

impl ScouterSettings {
    pub fn enabled(&self) -> bool {
        !self.server_uri.is_empty()
    }
}

/// OpsmlConfig for use with both server and client implementations
/// OpsmlConfig is the main primary configuration struct for the Opsml system
/// Based on provided env variables, it will be used to determine if opsml is running in client or server mode.
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
    pub logging_config: LoggingConfig,
    pub mode: OpsmlMode,
    pub base_path: PathBuf,
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

        let mode = OpsmlConfig::get_mode(&opsml_tracking_uri);

        // set scouter settings
        let scouter_settings = ScouterSettings {
            server_uri: env::var("SCOUTER_SERVER_URI").unwrap_or("".to_string()),
            bootstrap_token: env::var(
                "SCOUTER_BOOTSTRAP_TOKEN
            ",
            )
            .unwrap_or(generate_default_secret()),
        };

        // set auth settings
        let auth_settings = AuthSettings {
            jwt_secret: env::var("OPSML_ENCRYPT_SECRET").unwrap_or_else(|_| {
                if mode == OpsmlMode::Server {
                    warn!(
                        "Using default secret for encryption 
                        This is not recommended for production use."
                    );
                }
                generate_default_secret()
            }),
            refresh_secret: env::var("OPSML_REFRESH_SECRET").unwrap_or_else(|_| {
                if mode == OpsmlMode::Server {
                    warn!(
                        "Using default secret for refreshing. 
                        This is not recommended for production use."
                    );
                }
                generate_default_secret()
            }),
            scouter_secret: env::var("SCOUTER_AUTH_SECRET").unwrap_or_else(|_| {
                if mode == OpsmlMode::Server {
                    warn!(
                        "Using default secret for scouter. 
                        This is not recommended for production use."
                    );
                }
                generate_default_secret()
            }),

            username: env::var("OPSML_USERNAME").unwrap_or("guest".to_string()),
            password: env::var("OPSML_PASSWORD").unwrap_or("guest".to_string()),
            use_sso: env::var("OPSML_USE_SSO")
                .unwrap_or_else(|_| "false".to_string())
                .parse()
                .unwrap_or(false),
            prod_token: env::var("OPSML_PROD_TOKEN").ok(),
        };

        // set database settings
        let database_settings = DatabaseSettings {
            connection_uri: opsml_tracking_uri.clone(),
            max_connections: env::var("OPSML_MAX_POOL_CONNECTIONS")
                .unwrap_or_else(|_| "30".to_string())
                .parse()
                .unwrap_or(30),
            sql_type: OpsmlConfig::get_sql_type(&opsml_tracking_uri),
        };

        let log_level =
            LogLevel::from_str(&env::var("LOG_LEVEL").unwrap_or_else(|_| "info".to_string()))
                .unwrap_or(LogLevel::Info);

        let log_json = env::var("LOG_JSON")
            .unwrap_or_else(|_| "false".to_string())
            .parse()
            .unwrap_or(false);

        let logging_config =
            LoggingConfig::rust_new(false, log_level, WriteLevel::Stdout, log_json);

        // check OPSML_BASE_PATH or use current directory
        let base_path = match env::var("OPSML_BASE_PATH") {
            Ok(path) => {
                let path = PathBuf::from(path);
                if path.exists() {
                    path
                } else {
                    warn!("OPSML_BASE_PATH does not exist, using current directory");
                    std::env::current_dir().expect("Failed to get current directory")
                }
            }
            Err(_) => std::env::current_dir().expect("Failed to get current directory"),
        };

        OpsmlConfig {
            app_name: "opsml".to_string(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            app_version: opsml_version::version(),
            opsml_storage_uri: OpsmlConfig::set_opsml_storage_uri(opsml_storage_uri, &mode),
            opsml_tracking_uri,

            opsml_proxy_root: "opsml-root:/".to_string(),
            opsml_registry_path: env::var("OPSML_REGISTRY_PATH")
                .unwrap_or_else(|_| "opsml_registry".to_string()),

            database_settings,
            scouter_settings,
            auth_settings,
            mode,
            logging_config,
            base_path,
        }
    }
}

fn generate_default_secret() -> String {
    // Creates a deterministic key for development/initialization purposes
    // Should be replaced with a proper secret in production
    let mut key = [0u8; 32];
    for (i, item) in key.iter_mut().enumerate() {
        // Different pattern than the JWT secret (reversed index)
        *item = (31 - i) as u8;
    }

    BASE64_STANDARD.encode(key)
}

impl OpsmlConfig {
    pub fn set_opsml_storage_uri(opsml_storage_uri: String, mode: &OpsmlMode) -> String {
        if mode == &OpsmlMode::Client {
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

    pub fn get_mode(opsml_tracking_uri: &str) -> OpsmlMode {
        match opsml_tracking_uri.to_lowercase().trim().starts_with("http") {
            true => OpsmlMode::Client,
            false => OpsmlMode::Server,
        }
    }

    pub fn storage_root(&self) -> String {
        match self.mode {
            OpsmlMode::Client => self.opsml_proxy_root.clone(),
            OpsmlMode::Server => {
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
            }
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
    pub fn storage_settings(&self) -> Result<OpsmlStorageSettings, SettingsError> {
        Ok(OpsmlStorageSettings {
            encryption_key: BASE64_STANDARD
                .decode(self.auth_settings.jwt_secret.clone())
                .map_err(SettingsError::Base64DecodeError)?,
            storage_uri: self.opsml_storage_uri.clone(),
            storage_type: self.get_storage_type(),
            api_settings: ApiSettings {
                base_url: self.opsml_tracking_uri.clone(),
                opsml_dir: "opsml/api".to_string(),
                username: self.auth_settings.username.clone(),
                password: self.auth_settings.password.clone(),
                use_sso: self.auth_settings.use_sso,
                prod_token: self.auth_settings.prod_token.clone(),
            },
        })
    }
}

impl OpsmlConfig {
    /// Create a new OpsmlConfig instance
    ///
    /// # Returns
    ///
    /// `OpsmlConfig`: A new instance of OpsmlConfig
    pub fn new() -> Self {
        OpsmlConfig::default()
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
    fn test_generate_default_secret() {
        let jwt_secret = generate_default_secret();
        assert_eq!(jwt_secret.len(), 32);
    }

    #[test]
    fn test_set_opsml_storage_uri() {
        let opsml_storage_uri = "gs://test-bucket".to_string();
        let result = OpsmlConfig::set_opsml_storage_uri(opsml_storage_uri, &OpsmlMode::Server);
        assert_eq!(result, "gs://test-bucket");

        let opsml_storage_uri = "s3://test-bucket".to_string();
        let result = OpsmlConfig::set_opsml_storage_uri(opsml_storage_uri, &OpsmlMode::Server);
        assert_eq!(result, "s3://test-bucket");

        let opsml_storage_uri = "az://test-bucket".to_string();
        let result = OpsmlConfig::set_opsml_storage_uri(opsml_storage_uri, &OpsmlMode::Server);
        assert_eq!(result, "az://test-bucket");

        let opsml_storage_uri = "./test-bucket".to_string();
        let result = OpsmlConfig::set_opsml_storage_uri(opsml_storage_uri, &OpsmlMode::Server);
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
        assert!(opsml_config.mode == OpsmlMode::Server);

        let opsml_config = OpsmlConfig {
            opsml_tracking_uri: "http://localhost:5000".to_string(),
            ..Default::default()
        };
        assert!(opsml_config.mode == OpsmlMode::Client);

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
    fn test_default() {
        let opsml_config = OpsmlConfig::default();
        assert_eq!(opsml_config.app_name, "opsml");
        assert_eq!(opsml_config.app_env, "development");
        assert_eq!(opsml_config.app_version, opsml_version::version());
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
        assert_eq!(opsml_config.opsml_registry_path, "opsml_registry");

        assert_eq!(opsml_config.auth_settings.jwt_secret.len(), 32);
        assert_eq!(opsml_config.auth_settings.username, "guest");
        assert_eq!(opsml_config.auth_settings.password, "guest");
        assert_eq!(opsml_config.scouter_settings.server_uri, "");

        cleanup();
    }
}
