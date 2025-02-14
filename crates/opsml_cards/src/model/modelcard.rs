use crate::BaseArgs;
use opsml_error::error::{CardError, OpsmlError};
use opsml_interfaces::ModelInterface;
use opsml_interfaces::SaveKwargs;
use opsml_interfaces::{
    CatBoostModel, HuggingFaceModel, LightGBMModel, LightningModel, SklearnModel, TorchModel,
    XGBoostModel,
};
use opsml_interfaces::{LoadKwargs, ModelInterfaceMetadata};
use opsml_settings::config::OpsmlConfig;
use opsml_storage::FileSystemStorage;
use opsml_types::cards::{CardTable, CardType};
use opsml_types::contracts::{Card, ModelCardClientRecord};
use opsml_types::{ModelInterfaceType, SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::types::PyList;
use pyo3::{IntoPyObjectExt, PyObject};
use pyo3::{PyTraverseError, PyVisit};
use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};
use std::fmt;
use std::path::{Path, PathBuf};
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

    pub decryption_key: Option<Vec<u8>>,
}

#[pyclass]
#[derive(Debug)]
pub struct ModelCard {
    #[pyo3(get, set)]
    pub interface: Option<PyObject>,

    #[pyo3(get, set)]
    pub repository: String,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub contact: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub tags: Vec<String>,

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
    #[pyo3(signature = (interface, repository=None, name=None,  contact=None, version=None, uid=None, tags=None, to_onnx=None))]
    pub fn new(
        py: Python,
        interface: &Bound<'_, PyAny>,
        repository: Option<&str>,
        name: Option<&str>,
        contact: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        tags: Option<&Bound<'_, PyList>>,
        to_onnx: Option<bool>,
    ) -> PyResult<Self> {
        let tags = match tags {
            None => Vec::new(),
            Some(t) => t
                .extract::<Vec<String>>()
                .map_err(|e| OpsmlError::new_err(e.to_string()))?,
        };

        let base_args =
            BaseArgs::create_args(name, repository, contact, version, uid).map_err(|e| {
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
            repository: base_args.0,
            name: base_args.1,
            contact: base_args.2,
            version: base_args.3,
            uid: base_args.4,
            tags,
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

    pub fn add_tags(&mut self, tags: Vec<String>) {
        self.tags.extend(tags);
    }

    #[pyo3(signature = (path, save_kwargs=None))]
    pub fn save<'py>(
        &mut self,
        py: Python<'py>,
        path: PathBuf,
        save_kwargs: Option<SaveKwargs>,
    ) -> Result<(), CardError> {
        // save model interface
        // if option raise error
        let model = self
            .interface
            .as_ref()
            .ok_or_else(|| CardError::Error("Model interface not found".to_string()))?;

        let metadata =
            model
                .bind(py)
                .call_method("save", (path.clone(), self.to_onnx, save_kwargs), None)?;

        // extract into ModelInterfaceMetadata
        let interface_metadata = metadata.extract::<ModelInterfaceMetadata>()?;

        // update metadata
        self.metadata.interface_metadata = interface_metadata;

        // save modelcard
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&self, card_save_path)?;

        Ok(())
    }

    #[pyo3(signature = (model=true, onnx=false, drift_profile=false, sample_data=false, preprocessor=false, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn load(
        &self,
        py: Python,
        model: bool,
        onnx: bool,
        drift_profile: bool,
        sample_data: bool,
        preprocessor: bool,
        load_kwargs: Option<LoadKwargs>,
    ) -> PyResult<()> {
        //// download assets from uri
        let tmp_dir = tempfile::TempDir::new().map_err(|e| {
            error!("Failed to create temporary directory: {}", e);
            OpsmlError::new_err("Failed to create temporary directory".to_string())
        })?;

        let tmp_path = tmp_dir.into_path();

        // download assets
        self._download(
            &tmp_path,
            model,
            onnx,
            drift_profile,
            sample_data,
            preprocessor,
        )?;

        // load model interface
        self.interface.as_ref().unwrap().bind(py).call_method(
            "load",
            (
                tmp_path,
                model,
                onnx,
                drift_profile,
                sample_data,
                preprocessor,
                load_kwargs,
            ),
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

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Some(ref interface) = self.interface {
            visit.call(interface)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.interface = None;
    }

    pub fn get_registry_card(&self) -> Result<Card, CardError> {
        let record = ModelCardClientRecord {
            created_at: None,
            app_env: None,
            repository: self.repository.clone(),
            name: self.name.clone(),
            contact: self.contact.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            tags: self.tags.clone(),
            datacard_uid: self.metadata.datacard_uid.clone(),
            data_type: self.metadata.interface_metadata.data_type.to_string(),
            model_type: self.metadata.interface_metadata.model_type.to_string(),
            runcard_uid: self.metadata.runcard_uid.clone(),
            pipelinecard_uid: self.metadata.pipelinecard_uid.clone(),
            auditcard_uid: self.metadata.auditcard_uid.clone(),
            interface_type: self.metadata.interface_metadata.interface_type.to_string(),
            task_type: self.metadata.interface_metadata.task_type.to_string(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
        };

        Ok(Card::Model(record))
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

impl ModelCard {
    async fn _download_model(
        &self,
        lpath: &Path,
        rpath: &Path,
        fs: &mut FileSystemStorage,
    ) -> Result<(), CardError> {
        fs.get(
            &if rpath.extension().is_some() {
                lpath.join(&rpath)
            } else {
                lpath.to_path_buf()
            },
            &self.uri().join(&rpath),
            rpath.extension().is_none(),
        )
        .await?;

        Ok(())
    }
    pub fn _download(
        &self,
        path: &Path,
        model: bool,
        _onnx: bool,
        _drift_profile: bool,
        _sample_data: bool,
        _preprocessor: bool,
    ) -> Result<(), CardError> {
        // Create a new tokio runtime for the registry (needed for async calls)
        let rt = tokio::runtime::Runtime::new().map_err(|e| {
            error!("Failed to create tokio runtime: {}", e);
            CardError::Error(e.to_string())
        })?;

        let config = OpsmlConfig::default();
        let mut storage_settings = config.storage_settings()?.clone();
        let save_metadata = self.metadata.interface_metadata.save_metadata.clone();

        if model {
            rt.block_on(async {
                let mut fs = FileSystemStorage::new(&mut storage_settings).await?;
                self._download_model(path, &save_metadata.model_uri, &mut fs)
                    .await
            })?;
        }

        Ok(())
    }
}
