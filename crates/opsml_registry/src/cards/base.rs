use opsml_error::error::CardError;
use opsml_types::*;
use opsml_utils::{clean_string, validate_name_repository_pattern};
use pyo3::prelude::*;
use std::collections::HashMap;
use std::env;

pub struct BaseArgs {
    pub name: String,
    pub repository: String,
    pub contact: String,
    pub version: String,
    pub uid: String,
    pub tags: HashMap<String, String>,
}

impl BaseArgs {
    pub fn new(
        name: Option<String>,
        repository: Option<String>,
        contact: Option<String>,
        version: Option<String>,
        uid: Option<String>,
        info: Option<CardInfo>,
        tags: HashMap<String, String>,
    ) -> Result<Self, CardError> {
        let name = clean_string(&Self::get_value(
            "NAME",
            &name,
            info.as_ref().map(|i| &i.name),
        )?);
        let repository = clean_string(&Self::get_value(
            "REPOSITORY",
            &repository,
            info.as_ref().map(|i| &i.repository),
        )?);
        let contact = Self::get_value("CONTACT", &contact, info.as_ref().map(|i| &i.contact))?;

        let version = version.unwrap_or_else(|| CommonKwargs::BaseVersion.to_string());
        let uid = uid.unwrap_or_else(|| CommonKwargs::Undefined.to_string());

        validate_name_repository_pattern(&name, &repository)?;

        Ok(Self {
            name,
            repository,
            contact,
            version,
            uid,
            tags,
        })
    }

    fn get_value(
        key: &str,
        value: &Option<String>,
        card_info_value: Option<&Option<String>>,
    ) -> Result<String, CardError> {
        let env_key = format!("OPSML_RUNTIME_{}", key.to_uppercase());
        let env_val = env::var(&env_key).ok();

        value
            .as_ref()
            .or_else(|| card_info_value.and_then(|v| v.as_ref()))
            .or(env_val.as_ref())
            .map(|s| s.to_string())
            .ok_or_else(|| CardError::Error(format!("{} not provided", key)))
    }
}

pub trait BaseCard {
    fn register_card(
        &self,
        card: &Bound<'_, PyAny>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> CardType;
}
