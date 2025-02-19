use crate::model::huggingface::{HuggingFaceSampleData, HuggingFaceTask};
use opsml_types::{
    CommonKwargs, DataType, ModelInterfaceType, ModelType, SaveName, Suffix, TaskType,
};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use crate::base::{
    parse_save_kwargs, ExtraMetadata, ModelInterfaceMetadata, ModelInterfaceSaveMetadata,
};
use crate::data::generate_feature_schema;
use crate::data::DataInterface;
use crate::model::ModelInterface;
use crate::types::{FeatureSchema, ProcessorType};
use crate::OnnxModelConverter;
use crate::OnnxSession;
use crate::{DataProcessor, ModelLoadKwargs, ModelSaveKwargs};
use opsml_error::{InterfaceError, OnnxError, OpsmlError};
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use pyo3::PyTraverseError;
use pyo3::PyVisit;
use std::path::{Path, PathBuf};
use tracing::{debug, error, info, instrument, warn};

pub type ProcessorNames = (String, String, String);

fn get_processor_names<'py>(
    tokenizer: Option<&Bound<'py, PyAny>>,
    feature_extractor: Option<&Bound<'py, PyAny>>,
    image_processor: Option<&Bound<'py, PyAny>>,
) -> ProcessorNames {
    (
        tokenizer.map_or(CommonKwargs::Undefined.to_string(), |tokenizer| {
            tokenizer
                .getattr("__class__")
                .unwrap()
                .getattr("__name__")
                .unwrap()
                .to_string()
        }),
        feature_extractor.map_or(CommonKwargs::Undefined.to_string(), |feature| {
            feature
                .getattr("__class__")
                .unwrap()
                .getattr("__name__")
                .unwrap()
                .to_string()
        }),
        image_processor.map_or(CommonKwargs::Undefined.to_string(), |processor| {
            processor
                .getattr("__class__")
                .unwrap()
                .getattr("__name__")
                .unwrap()
                .to_string()
        }),
    )
}

fn get_processor_names_from_pipeline(pipeline: &Bound<'_, PyAny>) -> ProcessorNames {
    let get_attr = |name: &str| {
        pipeline
            .getattr(name)
            .ok()
            .and_then(|attr| (!attr.is_none()).then_some(attr))
    };

    get_processor_names(
        get_attr("tokenizer").as_ref(),
        get_attr("feature_extractor").as_ref(),
        get_attr("image_processor").as_ref(),
    )
}

fn validate_image_processor(py: Python, image_processor: &Bound<'_, PyAny>) -> PyResult<bool> {
    let base_processor = py
        .import("transformers")
        .unwrap()
        .getattr("BaseImageProcessor")?;

    match image_processor.is_instance(&base_processor).unwrap() {
        true => Ok(true),
        false => Err(OpsmlError::new_err(
            "Image Processor must be an instance of BaseImageProcessor",
        )),
    }
}

fn validate_tokenizer(py: Python, tokenizer: &Bound<'_, PyAny>) -> PyResult<bool> {
    let base_processor = py
        .import("transformers")?
        .getattr("PreTrainedTokenizerBase")?;

    match tokenizer.is_instance(&base_processor).unwrap() {
        true => Ok(true),
        false => Err(OpsmlError::new_err(
            "Tokenizer must be an instance of PreTrainedTokenizerBase",
        )),
    }
}

fn validate_feature_extractor(py: Python, feature_extractor: &Bound<'_, PyAny>) -> PyResult<bool> {
    let base_processor = py
        .import("transformers")?
        .getattr("feature_extraction_utils")?
        .getattr("PreTrainedFeatureExtractor")?;

    match feature_extractor.is_instance(&base_processor).unwrap() {
        true => Ok(true),
        false => Err(OpsmlError::new_err(
            "Feature Extractor must be an instance of PreTrainedFeatureExtractor",
        )),
    }
}

fn is_pretrained_torch_model(py: Python, model: &Bound<'_, PyAny>) -> PyResult<bool> {
    let transformers = py.import("transformers")?.getattr("PreTrainedModel")?;

    Ok(model.is_instance(&transformers).unwrap())
}

fn is_pretrained_tensorflow_model(py: Python, model: &Bound<'_, PyAny>) -> PyResult<bool> {
    let transformers = py.import("transformers")?.getattr("TFPreTrainedModel")?;

    Ok(model.is_instance(&transformers).unwrap())
}

fn is_hf_pipeline(py: Python, pipeline: &Bound<'_, PyAny>) -> PyResult<bool> {
    let transformers = py.import("transformers")?;

    Ok(pipeline
        .is_instance(&transformers.getattr("Pipeline")?)
        .unwrap())
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HFBaseArgs {
    pub hf_task: HuggingFaceTask,
    pub model_backend: ModelType,
    pub is_pipeline: bool,
    pub has_tokenizer: bool,
    pub has_feature_extractor: bool,
    pub has_image_processor: bool,
    pub tokenizer_name: String,
    pub feature_extractor_name: String,
    pub image_processor_name: String,
    pub hf_model_type: String,
    pub ort_type: String,
}

impl Default for HFBaseArgs {
    fn default() -> Self {
        HFBaseArgs {
            hf_task: HuggingFaceTask::Undefined,
            model_backend: ModelType::Pytorch,
            is_pipeline: false,
            has_tokenizer: false,
            has_feature_extractor: false,
            has_image_processor: false,
            tokenizer_name: CommonKwargs::Undefined.to_string(),
            feature_extractor_name: CommonKwargs::Undefined.to_string(),
            image_processor_name: CommonKwargs::Undefined.to_string(),
            hf_model_type: CommonKwargs::Undefined.to_string(),
            ort_type: CommonKwargs::Undefined.to_string(),
        }
    }
}

impl HFBaseArgs {
    pub fn has_processors(&self) -> bool {
        self.has_tokenizer || self.has_feature_extractor || self.has_image_processor
    }

    pub fn model_dump_json(&self) -> serde_json::Value {
        serde_json::json!({
            "hf_task": self.hf_task,
            "model_backend": self.model_backend,
            "is_pipeline": self.is_pipeline,
            "has_tokenizer": self.has_tokenizer,
            "has_feature_extractor": self.has_feature_extractor,
            "has_image_processor": self.has_image_processor,
            "tokenizer_name": self.tokenizer_name,
            "feature_extractor_name": self.feature_extractor_name,
            "image_processor_name": self.image_processor_name,
            "hf_model_type": self.hf_model_type,
            "ort_type": self.ort_type,
        })
    }

    pub fn model_validate_json(record: String) -> HFBaseArgs {
        serde_json::from_str(&record).unwrap_or_default()
    }
}

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct HuggingFaceModel {
    #[pyo3(get)]
    pub model: Option<PyObject>,

    #[pyo3(get)]
    pub tokenizer: Option<PyObject>,

    #[pyo3(get)]
    pub feature_extractor: Option<PyObject>,

    #[pyo3(get)]
    pub image_processor: Option<PyObject>,

    pub onnx_session: Option<Py<OnnxSession>>,

    #[pyo3(get)]
    pub model_type: ModelType,

    #[pyo3(get)]
    pub interface_type: ModelInterfaceType,

    #[pyo3(get)]
    pub huggingface_task: HuggingFaceTask,

    pub sample_data: HuggingFaceSampleData,

    pub base_args: HFBaseArgs,
}

#[pymethods]
impl HuggingFaceModel {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, tokenizer=None, feature_extractor=None, image_processor=None, sample_data=None, hf_task=None, task_type=None, schema=None, drift_profile=None))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        tokenizer: Option<&Bound<'py, PyAny>>,
        feature_extractor: Option<&Bound<'py, PyAny>>,
        image_processor: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        hf_task: Option<HuggingFaceTask>,
        task_type: Option<TaskType>,
        schema: Option<FeatureSchema>,
        drift_profile: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<(Self, ModelInterface)> {
        // check if model is a Transformers Pipeline, PreTrainedModel, or TFPPreTrainedModel
        let mut base_args = HFBaseArgs::default();

        if hf_task.is_some() {
            base_args.hf_task = hf_task.unwrap();
        }

        let mut processor_names =
            get_processor_names(tokenizer, feature_extractor, image_processor);

        // process model/pipeline
        let model = if let Some(model) = model {
            if is_hf_pipeline(py, model)? {
                // set model type to TransformersPipeline and get task
                base_args.is_pipeline = true;
                base_args.hf_task =
                    HuggingFaceTask::from_string(&model.getattr("task")?.to_string());
                processor_names = get_processor_names_from_pipeline(model);
                base_args.hf_model_type = model
                    .getattr("model")?
                    .getattr("__class__")?
                    .getattr("__name__")?
                    .to_string();
            } else if is_pretrained_torch_model(py, model)? {
                base_args.model_backend = ModelType::Pytorch;
                base_args.hf_model_type =
                    model.getattr("__class__")?.getattr("__name__")?.to_string();
            } else if is_pretrained_tensorflow_model(py, model)? {
                base_args.model_backend = ModelType::TensorFlow;
                base_args.hf_model_type =
                    model.getattr("__class__")?.getattr("__name__")?.to_string();
            } else {
                return Err(OpsmlError::new_err(
                    "Model must be an instance of transformers",
                ));
            }
            Some(model.into_py_any(py)?)
        } else {
            None
        };

        // validate processors

        let tokenizer = if let Some(tokenizer) = tokenizer {
            validate_tokenizer(py, tokenizer)?;
            base_args.has_tokenizer = true;
            Some(tokenizer.into_py_any(py)?)
        } else {
            None
        };

        let feature_extractor = if let Some(feature_extractor) = feature_extractor {
            validate_feature_extractor(py, feature_extractor)?;
            base_args.has_feature_extractor = true;
            Some(feature_extractor.into_py_any(py)?)
        } else {
            None
        };

        let image_processor = if let Some(image_processor) = image_processor {
            validate_image_processor(py, image_processor)?;
            base_args.has_image_processor = true;
            Some(image_processor.into_py_any(py)?)
        } else {
            None
        };

        // process preprocessor

        let mut model_interface =
            ModelInterface::new(py, None, None, task_type, schema, drift_profile, None)?;

        // override ModelInterface SampleData with TorchSampleData
        let sample_data = match sample_data {
            // attempt to create sample data. If it fails, return default sample data and log a warning
            Some(data) => HuggingFaceSampleData::new(data).unwrap_or_else(|e| {
                warn!("Failed to create sample data. Defaulting to None: {}", e);
                HuggingFaceSampleData::default()
            }),
            None => HuggingFaceSampleData::default(),
        };

        model_interface.data_type = sample_data.get_data_type();
        base_args.tokenizer_name = processor_names.0.clone();
        base_args.feature_extractor_name = processor_names.1.clone();
        base_args.image_processor_name = processor_names.2.clone();

        Ok((
            HuggingFaceModel {
                model,
                tokenizer,
                feature_extractor,
                image_processor,
                interface_type: ModelInterfaceType::HuggingFace,
                model_type: base_args.model_backend.clone(),
                onnx_session: None,
                huggingface_task: base_args.hf_task.clone(),
                sample_data,
                base_args,
            },
            // pass all the arguments to the ModelInterface
            model_interface,
        ))
    }

    #[setter]
    pub fn set_tokenizer(&mut self, tokenizer: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = tokenizer.py();

        // check if data is None
        if PyAnyMethods::is_none(tokenizer) {
            self.tokenizer = None;
            return Ok(());
        } else {
            validate_tokenizer(py, tokenizer)?;
            self.tokenizer = Some(tokenizer.into_py_any(py)?)
        };

        Ok(())
    }

    #[setter]
    pub fn set_feature_extractor(&mut self, feature_extractor: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = feature_extractor.py();

        // check if data is None
        if PyAnyMethods::is_none(feature_extractor) {
            self.feature_extractor = None;
            return Ok(());
        } else {
            validate_feature_extractor(py, feature_extractor)?;
            self.feature_extractor = Some(feature_extractor.into_py_any(py)?)
        };

        Ok(())
    }

    #[setter]
    pub fn set_image_processor(&mut self, image_processor: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = image_processor.py();

        // check if data is None
        if PyAnyMethods::is_none(image_processor) {
            self.image_processor = None;
            return Ok(());
        } else {
            validate_image_processor(py, image_processor)?;
            self.image_processor = Some(image_processor.into_py_any(py)?)
        };

        Ok(())
    }

    #[setter]
    pub fn set_model(&mut self, model: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = model.py();

        // check if data is None
        if PyAnyMethods::is_none(model) {
            self.model = None;
            return Ok(());
        } else {
            if is_hf_pipeline(py, model)? {
                // set model type to TransformersPipeline and get task
                self.base_args.is_pipeline = true;
                self.huggingface_task =
                    HuggingFaceTask::from_string(&model.getattr("task")?.to_string());
                let processor_names = get_processor_names_from_pipeline(model);
                self.base_args.tokenizer_name = processor_names.0;
                self.base_args.feature_extractor_name = processor_names.1;
                self.base_args.image_processor_name = processor_names.2;
                self.base_args.hf_model_type = model
                    .getattr("model")?
                    .getattr("__class__")?
                    .getattr("__name__")?
                    .to_string();
            } else if is_pretrained_torch_model(py, model)? {
                self.base_args.model_backend = ModelType::Pytorch;
                self.base_args.hf_model_type =
                    model.getattr("__class__")?.getattr("__name__")?.to_string();
            } else if is_pretrained_tensorflow_model(py, model)? {
                self.base_args.model_backend = ModelType::TensorFlow;
                self.base_args.hf_model_type =
                    model.getattr("__class__")?.getattr("__name__")?.to_string();
            } else {
                return Err(OpsmlError::new_err(
                    "Model must be an instance of transformers",
                ));
            }
            self.model = Some(model.into_py_any(py)?)
        };

        Ok(())
    }

    #[getter]
    pub fn get_onnx_session(&self, py: Python) -> PyResult<Option<Py<OnnxSession>>> {
        // return mutable reference to onnx session
        Ok(self.onnx_session.as_ref().map(|sess| sess.clone_ref(py)))
    }

    #[getter]
    pub fn get_sample_data<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        Ok(self.sample_data.get_data(py).unwrap().bind(py).clone())
    }

    /// Save the interface model
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `path` - Path to save the data
    /// * `kwargs` - Additional save kwargs
    ///
    /// # Returns
    ///
    /// * `PyResult<DataInterfaceSaveMetadata>` - DataInterfaceSaveMetadata
    #[pyo3(signature = (path, to_onnx=false, save_kwargs=None))]
    #[instrument(skip(self_, py, path, to_onnx, save_kwargs) name = "save_huggingface_interface")]
    pub fn save(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        to_onnx: bool,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> PyResult<ModelInterfaceMetadata> {
        let mut extra = None;
        let cloned_kwargs = save_kwargs.clone();

        let drift_profile_uri = if self_.as_super().drift_profile.is_empty() {
            None
        } else {
            Some(self_.as_super().save_drift_profile(&path)?)
        };

        // parse the save args
        let (onnx_kwargs, model_kwargs, preprocessor_kwargs) = parse_save_kwargs(py, &save_kwargs);

        let processors = self_.save_processors(py, &path, preprocessor_kwargs.as_ref())?;

        let data_processor_map = processors
            .iter()
            .map(|p| (p.name.clone(), p.clone()))
            .collect();

        debug!("Saving sample data");
        let sample_data_uri = self_.save_data(py, &path, None)?;

        debug!("Creating feature schema");
        self_.as_super().schema = self_.create_feature_schema(py)?;

        let mut onnx_model_uri = None;

        debug!("Saving model");
        let model_uri = self_.save_model(py, &path, model_kwargs.as_ref())?;

        if to_onnx {
            debug!("Saving ONNX model");
            let paths = self_.convert_to_onnx(py, &path, onnx_kwargs.as_ref())?;
            onnx_model_uri = paths.get("onnx").cloned();

            // if quantized exists, add to extra metadata
            if let Some(quantized) = paths.get("quantized") {
                let meta = PyDict::new(py);
                meta.set_item("quantized_model_uri", quantized.to_str().unwrap())?;
                extra = Some(ExtraMetadata::new(meta));
            }
        }

        let save_metadata = ModelInterfaceSaveMetadata {
            model_uri,
            data_processor_map,
            sample_data_uri,
            onnx_model_uri,
            drift_profile_uri,
            extra,
            save_kwargs: cloned_kwargs,
        };

        let onnx_session = {
            self_.as_super().onnx_session.as_ref().map(|sess| {
                let sess = sess.bind(py);
                // extract OnnxSession from py object
                let onnx_session = sess.extract::<OnnxSession>().unwrap();
                onnx_session
            })
        };

        let mut metadata = ModelInterfaceMetadata::new(
            save_metadata,
            self_.as_super().task_type.clone(),
            self_.model_type.clone(),
            self_.sample_data.get_data_type(),
            self_.as_super().schema.clone(),
            self_.interface_type.clone(),
            onnx_session,
            HashMap::new(),
        );

        metadata.model_specific_metadata = self_.base_args.model_dump_json();

        Ok(metadata)
    }

    /// Dynamically load the model interface components
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `path` - Path to load from
    /// * `onnx` - Whether to load the onnx model (default: false)
    /// * `load_kwargs` - Additional load kwargs to pass to the individual load methods
    ///
    /// # Returns
    ///
    /// * `PyResult<DataInterfaceMetadata>` - DataInterfaceMetadata
    #[pyo3(signature = (path, onnx=false, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    #[instrument(
        skip_all
        name = "load_huggingface_interface"
    )]
    pub fn load(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        onnx: bool,
        load_kwargs: Option<ModelLoadKwargs>,
    ) -> PyResult<()> {
        // if kwargs is not None, unwrap, else default to None
        let load_kwargs = load_kwargs.unwrap_or_default();

        debug!("Loading model");
        self_.load_model(py, &path, load_kwargs.model_kwargs(py))?;

        if onnx {
            debug!("Loading ONNX model");
            self_.load_onnx_model(py, &path, load_kwargs.onnx_kwargs(py))?;
        }

        debug!("Loading sample data");
        let data_type = self_.as_super().data_type.clone();
        self_.load_data(py, &path, &data_type, None)?;

        debug!("Loading preprocessor");
        self_.load_preprocessor(py, &path, load_kwargs.preprocessor_kwargs(py))?;

        debug!("Loading drift profile");
        self_.as_super().load_drift_profile(&path)?;

        Ok(())
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Some(ref tokenizer) = self.tokenizer {
            visit.call(tokenizer)?;
        }

        if let Some(ref image_processor) = self.image_processor {
            visit.call(image_processor)?;
        }

        if let Some(ref feature_extractor) = self.feature_extractor {
            visit.call(feature_extractor)?;
        }

        if let Some(ref model) = self.model {
            visit.call(model)?;
        }

        if let Some(ref onnx_session) = self.onnx_session {
            visit.call(onnx_session)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.tokenizer = None;
        self.feature_extractor = None;
        self.image_processor = None;
        self.model = None;
        self.onnx_session = None;
    }
}

impl HuggingFaceModel {
    pub fn from_metadata<'py>(
        py: Python<'py>,
        metadata: &ModelInterfaceMetadata,
    ) -> PyResult<Bound<'py, PyAny>> {
        let base_args: HFBaseArgs =
            serde_json::from_value(metadata.model_specific_metadata.clone()).map_err(|e| {
                error!("Failed to deserialize model specific metadata: {}", e);
                OpsmlError::new_err("Failed to deserialize model specific metadata")
            })?;

        // convert onnx session to to Py<OnnxSession>
        let onnx_session = metadata
            .onnx_session
            .as_ref()
            .map(|session| Py::new(py, session.clone()).unwrap());

        let huggingface_interface = HuggingFaceModel {
            model: None,
            tokenizer: None,
            feature_extractor: None,
            image_processor: None,
            onnx_session,
            model_type: metadata.model_type.clone(),
            interface_type: metadata.interface_type.clone(),
            huggingface_task: base_args.hf_task.clone(),
            sample_data: HuggingFaceSampleData::default(),
            base_args,
        };

        let mut interface = ModelInterface::new(
            py,
            None,
            None,
            Some(metadata.task_type.clone()),
            Some(metadata.schema.clone()),
            None,
            None,
        )?;

        interface.data_type = metadata.data_type.clone();
        interface.model_type = metadata.model_type.clone();
        interface.interface_type = metadata.interface_type.clone();

        Ok(Py::new(py, (huggingface_interface, interface))?.into_bound_py_any(py)?)
    }

    /// Load the preprocessor from a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to load the model from
    /// * `kwargs` - Additional keyword arguments to pass to the load
    ///
    #[instrument(skip(self, py, path, kwargs))]
    pub fn load_preprocessor(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<(), InterfaceError> {
        // self.tokenizer = getattr(transformers, self.tokenizer_name).from_pretrained(path)
        if self.base_args.has_tokenizer {
            let save_path = PathBuf::from(SaveName::Tokenizer);
            let full_save_path = path.join(&save_path);
            self.tokenizer = Some(
                py.import("transformers")?
                    .getattr(&self.base_args.tokenizer_name)?
                    .call_method("from_pretrained", (full_save_path,), kwargs)?
                    .unbind(),
            );

            debug!("Tokenizer loaded");
        }

        if self.base_args.has_feature_extractor {
            let save_path = PathBuf::from(SaveName::FeatureExtractor);
            let full_save_path = path.join(&save_path);
            self.feature_extractor = Some(
                py.import("transformers")?
                    .getattr(&self.base_args.feature_extractor_name)?
                    .call_method("from_pretrained", (full_save_path,), kwargs)?
                    .unbind(),
            );

            debug!("Feature Extractor loaded");
        }

        if self.base_args.has_image_processor {
            let save_path = PathBuf::from(SaveName::ImageProcessor);
            let full_save_path = path.join(&save_path);
            self.image_processor = Some(
                py.import("transformers")?
                    .getattr(&self.base_args.image_processor_name)?
                    .call_method("from_pretrained", (full_save_path,), kwargs)?
                    .unbind(),
            );

            debug!("Image Processor loaded");
        }

        info!("Preprocessor loaded");
        Ok(())
    }

    #[instrument(skip(self, py, path, kwargs))]
    pub fn convert_to_onnx(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<HashMap<String, PathBuf>, OnnxError> {
        let mut paths = HashMap::new();

        let session = OnnxModelConverter::convert_model(
            py,
            py.None().bind(py),
            &self.sample_data,
            &ModelInterfaceType::HuggingFace,
            &self.model_type,
            path,
            kwargs,
        )?;

        paths.insert("onnx".to_string(), PathBuf::from(SaveName::OnnxModel));

        if session.quantized {
            paths.insert(
                "quantized".to_string(),
                PathBuf::from(SaveName::QuantizedModel),
            );
        }

        self.onnx_session = Some(Py::new(py, session)?);

        info!("Model converted to ONNX");

        Ok(paths)
    }

    #[instrument(skip(self, py, path, kwargs))]
    fn save_tokenizer(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PathBuf, InterfaceError> {
        let save_path = PathBuf::from(SaveName::Tokenizer);
        let full_save_path = path.join(&save_path);

        // Save the data using joblib
        self.tokenizer
            .as_ref()
            .unwrap()
            .bind(py)
            .call_method("save_pretrained", (full_save_path,), kwargs)
            .map_err(|e| {
                error!("Failed to save tokenizer: {}", e);
                InterfaceError::Error(e.to_string())
            })?;

        info!("Tokenizer saved");

        Ok(save_path)
    }

    #[instrument(skip(self, py, path, kwargs))]
    fn save_feature_extractor(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PathBuf, InterfaceError> {
        let save_path = PathBuf::from(SaveName::FeatureExtractor);
        let full_save_path = path.join(&save_path);

        // Save the data using joblib
        self.feature_extractor
            .as_ref()
            .unwrap()
            .bind(py)
            .call_method("save_pretrained", (full_save_path,), kwargs)
            .map_err(|e| {
                error!("Failed to save feature extractor: {}", e);
                InterfaceError::Error(e.to_string())
            })?;

        info!("Feature Extractor saved");

        Ok(save_path)
    }

    #[instrument(skip(self, py, path, kwargs))]
    fn save_image_processor(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PathBuf, InterfaceError> {
        let save_path = PathBuf::from(SaveName::ImageProcessor);
        let full_save_path = path.join(&save_path);

        // Save the data using joblib
        self.image_processor
            .as_ref()
            .unwrap()
            .bind(py)
            .call_method("save_pretrained", (full_save_path,), kwargs)
            .map_err(|e| {
                error!("Failed to save image processor: {}", e);
                InterfaceError::Error(e.to_string())
            })?;

        info!("Image Processor saved");

        Ok(save_path)
    }

    /// Save the preprocessor to a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to save the model to
    /// * `kwargs` - Additional keyword arguments to pass to the save
    ///
    #[instrument(skip(self, py, path, kwargs))]
    pub fn save_processors(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Vec<DataProcessor>, InterfaceError> {
        let mut preprocessors = vec![];

        if self.base_args.has_tokenizer {
            debug!("Saving tokenizer");
            let tokenizer_path = self.save_tokenizer(py, path, kwargs)?;
            preprocessors.push(DataProcessor {
                name: self.base_args.tokenizer_name.clone(),
                uri: tokenizer_path,
                r#type: ProcessorType::Tokenizer,
            });
        }

        if self.base_args.has_feature_extractor {
            debug!("Saving feature extractor");
            let feature_extractor_path = self.save_feature_extractor(py, path, kwargs)?;
            preprocessors.push(DataProcessor {
                name: self.base_args.feature_extractor_name.clone(),
                uri: feature_extractor_path,
                r#type: ProcessorType::FeatureExtractor,
            });
        }

        if self.base_args.has_image_processor {
            debug!("Saving image processor");
            let image_processor_path = self.save_image_processor(py, path, kwargs)?;
            preprocessors.push(DataProcessor {
                name: self.base_args.image_processor_name.clone(),
                uri: image_processor_path,
                r#type: ProcessorType::ImageProcessor,
            });
        }

        info!("Preprocessor saved");
        Ok(preprocessors)
    }

    /// Save the model to a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to save the model to
    /// * `kwargs` - Additional keyword arguments to pass to the save
    ///
    #[instrument(skip(self, py, path, kwargs))]
    pub fn save_model(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        let save_path = PathBuf::from(SaveName::Model);
        let full_save_path = path.join(&save_path);

        // Save the data using joblib
        self.model
            .as_ref()
            .unwrap()
            .bind(py)
            .call_method("save_pretrained", (full_save_path,), kwargs)
            .map_err(|e| {
                error!("Failed to save model: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        info!("Model saved");

        Ok(save_path)
    }

    #[instrument(skip(self, py, path, kwargs))]
    pub fn load_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Model);

        if self.base_args.is_pipeline {
            let pipeline = py.import("transformers")?.getattr("pipeline")?;

            let model = pipeline.call((&self.huggingface_task.to_string(), load_path), kwargs)?;
            self.model = Some(model.unbind());

            debug!("Model loaded");
        } else {
            let model = py
                .import("transformers")?
                .getattr(&self.base_args.hf_model_type)?;

            self.model = Some(
                model
                    .call_method("from_pretrained", (load_path,), kwargs)?
                    .unbind(),
            );

            debug!("Model loaded");
        }

        Ok(())
    }

    /// Saves the sample data
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `path` - Path to save the data
    /// * `kwargs` - Additional save kwargs
    ///
    #[instrument(skip(self, py, path, kwargs))]
    pub fn save_data(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Option<PathBuf>> {
        // if sample_data is not None, save the sample data
        let sample_data_uri = self
            .sample_data
            .save_data(py, path, kwargs)
            .unwrap_or_else(|e| {
                warn!("Failed to save sample data. Defaulting to None: {}", e);
                None
            });

        Ok(sample_data_uri)
    }

    /// Load the sample data
    #[instrument(skip(self, py, path, data_type, kwargs))]
    pub fn load_data(
        &mut self,
        py: Python,
        path: &Path,
        data_type: &DataType,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        // load sample data
        self.sample_data = HuggingFaceSampleData::load_data(py, path, data_type, kwargs)?;

        info!("Sample data loaded");

        Ok(())
    }

    /// Load the model from a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to load the model from
    /// * `kwargs` - Additional keyword arguments to pass to the load
    ///
    #[instrument(skip(self, py, path, kwargs))]
    pub fn load_onnx_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        if self.onnx_session.is_none() {
            return Err(OpsmlError::new_err(
                "No ONNX model detected in interface for loading",
            ));
        }

        let load_path = path.join(SaveName::OnnxModel.to_string());

        // get file path to onnx model
        let file_path = std::fs::read_dir(&load_path)?
            .filter_map(|entry| {
                entry.ok().and_then(|e| {
                    let path = e.path();
                    if path.is_file() && path.extension().unwrap() == Suffix::Onnx.as_string() {
                        Some(path)
                    } else {
                        None
                    }
                })
            })
            .next()
            .ok_or_else(|| OpsmlError::new_err("No ONNX file found"))?;

        let sess = OnnxSession::load_onnx_session(py, file_path, kwargs)?;

        self.onnx_session
            .as_ref()
            .unwrap()
            .setattr(py, "session", Some(sess))?;

        info!("ONNX model loaded");

        Ok(())
    }

    /// Create a feature schema
    ///
    /// # Arguments
    ///
    /// * `name` - Name of the feature
    ///
    /// # Returns
    ///
    /// * `PyResult<FeatureMap>` - FeatureMap
    pub fn create_feature_schema(&mut self, py: Python) -> PyResult<FeatureSchema> {
        // Create and insert the feature

        let mut data = self.sample_data.get_data(py)?.bind(py).clone();

        // if data is instance of DataInterface, get the data
        if data.is_instance_of::<DataInterface>() {
            data = data.getattr("data")?;
        }

        generate_feature_schema(&data, &self.sample_data.get_data_type())
    }
}
