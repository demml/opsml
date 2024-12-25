use opsml_error::error::CardError;
use opsml_types::*;
use opsml_utils::{clean_string, validate_name_repository_pattern};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;

#[derive(Debug, Serialize, Deserialize)]
#[pyclass]
pub struct CardInfo {
    #[pyo3(get)]
    pub name: Option<String>,

    #[pyo3(get)]
    pub repository: Option<String>,

    #[pyo3(get)]
    pub contact: Option<String>,

    #[pyo3(get)]
    pub uid: Option<String>,

    #[pyo3(get)]
    pub version: Option<String>,

    #[pyo3(get)]
    pub tags: Option<HashMap<String, String>>,
}

#[pymethods]
impl CardInfo {
    #[new]
    #[pyo3(signature = (name=None, repository=None, contact=None, uid=None, version=None, tags=None))]
    pub fn new(
        name: Option<String>,
        repository: Option<String>,
        contact: Option<String>,
        uid: Option<String>,
        version: Option<String>,
        tags: Option<HashMap<String, String>>,
    ) -> Self {
        Self {
            name,
            repository,
            contact,
            uid,
            version,
            tags,
        }
    }
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }

    pub fn set_env(&self) {
        // if check name, repo and contact. If any is set, set environment variable
        // if name is set, set OPSML_RUNTIME_NAME
        // if repository is set, set OPSML_RUNTIME_REPOSITORY
        // if contact is set, set OPSML_RUNTIME_CONTACT

        if let Some(name) = &self.name {
            std::env::set_var("OPSML_RUNTIME_NAME", name);
        }

        if let Some(repo) = &self.repository {
            std::env::set_var("OPSML_RUNTIME_REPOSITORY", repo);
        }

        if let Some(contact) = &self.contact {
            std::env::set_var("OPSML_RUNTIME_CONTACT", contact);
        }
    }

    // primarily used for checking and testing. Do not write .pyi file for this method
    pub fn get_vars(&self) -> HashMap<String, String> {
        // check if OPSML_RUNTIME_NAME, OPSML_RUNTIME_REPOSITORY, OPSML_RUNTIME_CONTACT are set
        // Print out the values if they are set

        let name = std::env::var("OPSML_RUNTIME_NAME").unwrap_or_default();
        let repo = std::env::var("OPSML_RUNTIME_REPOSITORY").unwrap_or_default();
        let contact = std::env::var("OPSML_RUNTIME_CONTACT").unwrap_or_default();

        // print
        let mut map = HashMap::new();
        map.insert("OPSML_RUNTIME_NAME".to_string(), name);
        map.insert("OPSML_RUNTIME_REPOSITORY".to_string(), repo);
        map.insert("OPSML_RUNTIME_CONTACT".to_string(), contact);

        map
    }
}

impl CardInfo {
    pub fn get_value_by_name(&self, name: &str) -> &Option<String> {
        match name {
            "name" => &self.name,
            "repository" => &self.repository,
            "contact" => &self.contact,
            "uid" => &self.uid,
            "version" => &self.version,
            _ => &None,
        }
    }
}

impl FromPyObject<'_> for CardInfo {
    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        let name = ob.getattr("name").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let repository = ob.getattr("repository").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let contact = ob.getattr("contact").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let version = ob.getattr("version").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let uid = ob.getattr("uid").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let tags = ob.getattr("tags").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<HashMap<String, String>>()?))
            }
        })?;

        Ok(CardInfo {
            name,
            repository,
            contact,
            uid,
            version,
            tags,
        })
    }
}

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
