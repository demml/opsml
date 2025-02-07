use crate::types::Tags;
use crate::{BaseArgs, CardInfo};
use core::error;
use opsml_error::error::OpsmlError;
use opsml_interfaces::catboost::interface;
use opsml_interfaces::SaveKwargs;
use opsml_interfaces::{
    CatBoostModel, HuggingFaceModel, LightGBMModel, LightningModel, SklearnModel, TorchModel,
    XGBoostModel,
};
use opsml_interfaces::{LoadKwargs, ModelInterfaceMetadata};
use opsml_interfaces::{ModelInterface, ModelInterfaceType};
use opsml_types::cards::{CardTable, CardType};
use opsml_types::{SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::{IntoPyObjectExt, PyObject};
use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};
use std::collections::HashMap;
use std::fmt;
use std::path::PathBuf;
use tracing::error;

fn interface_from_metadata<'py>(
    py: Python<'py>,
    metadata: &ModelInterfaceMetadata,
) -> PyResult<Bound<'py, PyAny>> {
    match metadata.interface_type {
        ModelInterfaceType::Sklearn => SklearnModel::from_metadata(py, metadata),
        ModelInterfaceType::CatBoost => CatBoostModel::from_metadata(py, metadata),
        ModelInterfaceType::LightGBM => LightGBMModel::from_metadata(py, metadata),
        ModelInterfaceType::XGBoost => XGBoostModel::from_metadata(py, metadata),
        ModelInterfaceType::Torch => TorchModel::from_metadata(py, metadata),
        ModelInterfaceType::Lightning => LightningModel::from_metadata(py, metadata),
        ModelInterfaceType::HuggingFace => HuggingFaceModel::from_metadata(py, metadata),

        _ => {
            error!("Interface type not found");
            Err(OpsmlError::new_err("Interface type not found"))
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ModelCardMetadata {
    #[pyo3(get, set)]
    pub datacard_uid: Option<String>,

    #[pyo3(get, set)]
    pub runcard_uid: Option<String>,

    #[pyo3(get, set)]
    pub pipelinecard_uid: Option<String>,

    #[pyo3(get, set)]
    pub auditcard_uid: Option<String>,

    pub interface_metadata: ModelInterfaceMetadata,
}

#[pyclass]
#[derive(Debug)]
pub struct ModelCard {
    #[pyo3(get, set)]
    pub interface: Option<PyObject>,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub repository: String,

    #[pyo3(get, set)]
    pub contact: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub tags: Tags,

    #[pyo3(get, set)]
    pub metadata: ModelCardMetadata,

    #[pyo3(get)]
    pub card_type: CardType,

    #[pyo3(get)]
    pub to_onnx: bool,
}

#[pymethods]
impl ModelCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (interface, repository=None, name=None,  contact=None, version=None, uid=None, info=None, tags=None, to_onnx=None))]
    pub fn new(
        py: Python,
        interface: &Bound<'_, PyAny>,
        repository: Option<String>,
        name: Option<String>,
        contact: Option<String>,
        version: Option<String>,
        uid: Option<String>,
        info: Option<CardInfo>,
        tags: Option<&Bound<'_, PyAny>>,
        to_onnx: Option<bool>,
    ) -> PyResult<Self> {
        let tags = match tags {
            None => Tags::new(None),
            Some(t) => {
                if t.is_instance_of::<PyDict>() {
                    let dict = t.extract::<HashMap<String, String>>().unwrap();
                    Tags::new(Some(dict))
                } else {
                    t.extract::<Tags>()
                        .map_err(|e| OpsmlError::new_err(e.to_string()))?
                }
            }
        };

        let base_args = BaseArgs::new(name, repository, contact, version, uid, info, tags)
            .map_err(|e| {
                error!("Failed to create base args: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        if interface.is_instance_of::<ModelInterface>() {
            //
        } else {
            return Err(OpsmlError::new_err(
                "interface must be an instance of ModelInterface",
            ));
        }

        Ok(Self {
            interface: Some(
                interface
                    .into_py_any(py)
                    .map_err(|e| OpsmlError::new_err(e.to_string()))?,
            ),
            name: base_args.name,
            repository: base_args.repository,
            contact: base_args.contact,
            version: base_args.version,
            uid: base_args.uid,
            tags: base_args.tags,
            metadata: ModelCardMetadata::default(),
            card_type: CardType::Model,
            to_onnx: to_onnx.unwrap_or(false),
        })
    }

    #[setter]
    pub fn set_interface(&mut self, interface: &Bound<'_, PyAny>) -> PyResult<()> {
        if interface.is_instance_of::<ModelInterface>() {
            self.interface = Some(
                interface
                    .into_py_any(interface.py())
                    .map_err(|e| OpsmlError::new_err(e.to_string()))
                    .unwrap(),
            );
            Ok(())
        } else {
            return Err(OpsmlError::new_err(
                "interface must be an instance of ModelInterface",
            ));
        }
    }

    #[getter]
    pub fn uri(&self) -> PathBuf {
        let uri = format!(
            "{}/{}/{}/v{}",
            CardTable::Model,
            self.repository,
            self.name,
            self.version
        );

        PathBuf::from(uri)
    }

    #[pyo3(signature = (path, save_kwargs=None))]
    pub fn save<'py>(
        &mut self,
        py: Python<'py>,
        path: PathBuf,
        save_kwargs: Option<SaveKwargs>,
    ) -> PyResult<()> {
        // save model interface
        let metadata = self.interface.as_ref().unwrap().bind(py).call_method(
            "save",
            (path.clone(), self.to_onnx, save_kwargs),
            None,
        )?;

        // extract into ModelInterfaceMetadata
        let interface_metadata = metadata.extract::<ModelInterfaceMetadata>()?;

        // update metadata
        self.metadata.interface_metadata = interface_metadata;

        // save modelcard
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&self, card_save_path)?;

        Ok(())
    }

    #[pyo3(signature = (path, model=true, onnx=false, drift_profile=false, sample_data=false, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn load(
        &self,
        py: Python,
        path: PathBuf,
        model: bool,
        onnx: bool,
        drift_profile: bool,
        sample_data: bool,
        load_kwargs: Option<LoadKwargs>,
    ) -> PyResult<()> {
        self.interface.as_ref().unwrap().bind(py).call_method(
            "load",
            (path, model, onnx, drift_profile, sample_data, load_kwargs),
            None,
        )?;

        Ok(())
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    #[pyo3(signature = (json_string, interface=None))]
    pub fn model_validate_json(
        py: Python,
        json_string: String,
        interface: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<ModelCard> {
        let mut card: ModelCard = serde_json::from_str(&json_string).map_err(|e| {
            error!("Failed to validate json: {}", e);
            OpsmlError::new_err(e.to_string())
        })?;

        card.load_interface(py, interface)?;

        Ok(card)
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(&self)
    }
}

impl ModelCard {
    fn load_interface(&mut self, py: Python, interface: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
        if let Some(interface) = interface {
            self.set_interface(interface)
        } else {
            // match interface type
            let interface = interface_from_metadata(py, &self.metadata.interface_metadata)?;
            self.set_interface(&interface)
        }
    }
}

impl Serialize for ModelCard {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("ModelCard", 10)?;

        // set session to none
        state.serialize_field("name", &self.name)?;
        state.serialize_field("repository", &self.repository)?;
        state.serialize_field("contact", &self.contact)?;
        state.serialize_field("version", &self.version)?;
        state.serialize_field("uid", &self.uid)?;
        state.serialize_field("tags", &self.tags)?;
        state.serialize_field("metadata", &self.metadata)?;
        state.serialize_field("card_type", &self.card_type)?;
        state.serialize_field("to_onnx", &self.to_onnx)?;
        state.end()
    }
}

impl FromPyObject<'_> for ModelCard {
    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        let interface = ob.getattr("interface")?;
        let name = ob.getattr("name")?.extract()?;
        let repository = ob.getattr("repository")?.extract()?;
        let contact = ob.getattr("contact")?.extract()?;
        let version = ob.getattr("version")?.extract()?;
        let uid = ob.getattr("uid")?.extract()?;
        let tags = ob.getattr("tags")?.extract()?;
        let metadata = ob.getattr("metadata")?.extract()?;
        let card_type = ob.getattr("card_type")?.extract()?;
        let to_onnx = ob.getattr("to_onnx")?.extract()?;

        Ok(ModelCard {
            interface: Some(interface.into()),
            name,
            repository,
            contact,
            version,
            uid,
            tags,
            metadata,
            card_type,
            to_onnx,
        })
    }
}

impl<'de> Deserialize<'de> for ModelCard {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(field_identifier, rename_all = "snake_case")]
        enum Field {
            Interface,
            Name,
            Repository,
            Contact,
            Version,
            Uid,
            Tags,
            Metadata,
            CardType,
            ToOnnx,
        }

        struct ModelCardVisitor;

        impl<'de> Visitor<'de> for ModelCardVisitor {
            type Value = ModelCard;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct OnnxSession")
            }

            fn visit_map<V>(self, mut map: V) -> Result<ModelCard, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut interface = None;
                let mut name = None;
                let mut repository = None;
                let mut contact = None;
                let mut version = None;
                let mut uid = None;
                let mut tags = None;
                let mut metadata = None;
                let mut card_type = None;
                let mut to_onnx = None;

                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Interface => {
                            let _interface: Option<serde_json::Value> = map.next_value()?;
                            interface = None; // Default to None always (pyobject)
                        }
                        Field::Name => {
                            name = Some(map.next_value()?);
                        }
                        Field::Repository => {
                            repository = Some(map.next_value()?);
                        }
                        Field::Contact => {
                            contact = Some(map.next_value()?);
                        }
                        Field::Version => {
                            version = Some(map.next_value()?);
                        }
                        Field::Uid => {
                            uid = Some(map.next_value()?);
                        }
                        Field::Tags => {
                            tags = Some(map.next_value()?);
                        }
                        Field::Metadata => {
                            metadata = Some(map.next_value()?);
                        }
                        Field::CardType => {
                            card_type = Some(map.next_value()?);
                        }
                        Field::ToOnnx => {
                            to_onnx = Some(map.next_value()?);
                        }
                    }
                }

                let name = name.ok_or_else(|| de::Error::missing_field("name"))?;
                let repository =
                    repository.ok_or_else(|| de::Error::missing_field("repository"))?;
                let contact = contact.ok_or_else(|| de::Error::missing_field("contact"))?;
                let version = version.ok_or_else(|| de::Error::missing_field("version"))?;
                let uid = uid.ok_or_else(|| de::Error::missing_field("uid"))?;
                let tags = tags.ok_or_else(|| de::Error::missing_field("tags"))?;
                let metadata = metadata.ok_or_else(|| de::Error::missing_field("metadata"))?;
                let card_type = card_type.ok_or_else(|| de::Error::missing_field("card_type"))?;
                let to_onnx = to_onnx.ok_or_else(|| de::Error::missing_field("to_onnx"))?;

                Ok(ModelCard {
                    interface,
                    name,
                    repository,
                    contact,
                    version,
                    uid,
                    tags,
                    metadata,
                    card_type,
                    to_onnx,
                })
            }
        }

        const FIELDS: &[&str] = &[
            "interface",
            "name",
            "repository",
            "contact",
            "version",
            "uid",
            "tags",
            "metadata",
            "card_type",
            "to_onnx",
        ];
        deserializer.deserialize_struct("ModelCard", FIELDS, ModelCardVisitor)
    }
}
