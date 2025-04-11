use opsml_error::TypeError;
use opsml_state::app_state;
use opsml_types::{CommonKwargs, RegistryType};
use opsml_utils::{clean_string, validate_name_space_pattern};

pub type BaseArgsResult = (String, String, String, String);

pub struct BaseArgs {}

impl BaseArgs {
    pub fn create_args(
        name: Option<&str>,
        space: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        registry_type: &RegistryType,
    ) -> Result<BaseArgsResult, TypeError> {
        let name = clean_string(&Self::get_value("name", name, registry_type)?)?;
        let space = clean_string(&Self::get_value("space", space, registry_type)?)?;

        let version = match version {
            Some(v) => v.to_string(),
            None => Self::get_config_value("version", registry_type)?
                .unwrap_or_else(|| CommonKwargs::BaseVersion.to_string()),
        };

        let uid = uid.map_or(CommonKwargs::Undefined.to_string(), |v| v.to_string());

        validate_name_space_pattern(&name, &space)?;

        Ok((space, name, version, uid))
    }

    fn get_value(
        key: &str,
        value: Option<&str>,
        registry_type: &RegistryType,
    ) -> Result<String, TypeError> {
        let config_value = Self::get_config_value(key, registry_type)?;

        value
            .as_ref()
            .map(|s| s.to_string())
            .or(config_value)
            .ok_or_else(|| TypeError::Error(format!("{key} not provided")))
    }

    fn get_config_value(
        key: &str,
        registry_type: &RegistryType,
    ) -> Result<Option<String>, TypeError> {
        // Get reference to Arc<Option<OpsmlTools>> once
        let state = app_state();
        let tools = state.tools()?;

        match &*tools {
            Some(tools) => Ok(tools.get_attribute_key_value(key, registry_type)),
            None => Ok(None),
        }
    }
}
