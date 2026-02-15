use crate::error::CardError;
use names::Generator;
use opsml_state::{StateError, app_state};
use opsml_types::error::TypeError;
use opsml_types::{CommonKwargs, RegistryType};
use opsml_utils::{clean_string, validate_name_space_pattern};

pub type BaseArgsResult = (String, String, String, String);

pub struct BaseArgs {}

impl BaseArgs {
    /// Create base arguments for a card. Attempt to pull from config if not provided.
    ///
    /// # Arguments
    /// * `name` - Optional name of the card
    /// * `space` - Optional space of the card
    /// * `version` - Optional version of the card
    /// * `uid` - Optional uid of the card
    /// * `registry_type` - Type of the registry
    ///
    /// # Returns
    /// * `Result<BaseArgsResult, TypeError>` - A tuple containing the space, name, version, and uid of the card
    pub fn create_args(
        name: Option<&str>,
        space: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        registry_type: &RegistryType,
    ) -> Result<BaseArgsResult, CardError> {
        let name = clean_string(&Self::get_value("name", name, registry_type)?)?;
        let space = clean_string(&Self::get_value("space", space, registry_type)?)?;

        let version = match version {
            Some(v) => v.to_string(),
            None => Self::get_config_value("version", registry_type)?
                .unwrap_or_else(|| CommonKwargs::BaseVersion.to_string()),
        };

        let uid = uid.map_or(CommonKwargs::Undefined.to_string(), |v| v.to_string());

        // we want to ensure some kind of pattern for the space and name validation
        validate_name_space_pattern(&name, &space)?;

        Ok((space, name, version, uid))
    }

    fn get_value(
        key: &str,
        value: Option<&str>,
        registry_type: &RegistryType,
    ) -> Result<String, CardError> {
        let config_value = Self::get_config_value(key, registry_type)?;

        // exception for experiment card. If not name provided, default to random name
        if key == "name"
            && value.is_none()
            && config_value.is_none()
            && registry_type == &RegistryType::Experiment
        {
            let name = value.map(String::from).unwrap_or_else(|| {
                let mut generator = Generator::default();
                generator.next().unwrap_or_else(|| "experiment".to_string())
            });

            return Ok(name);
        }

        Ok(value
            .as_ref()
            .map(|s| s.to_string())
            .or(config_value)
            .ok_or(TypeError::MissingKeyError)?)
    }

    fn get_config_value(
        key: &str,
        registry_type: &RegistryType,
    ) -> Result<Option<String>, StateError> {
        // Get reference to Arc<Option<OpsmlTools>> once
        let state = app_state();
        let tools = state.tools()?;

        match &*tools {
            Some(tools) => Ok(tools.get_attribute_key_value(key, registry_type)),
            None => Ok(None),
        }
    }
}
