use crate::error::{ModelInterfaceError, TypeError};
use crate::model::huggingface::types::HuggingFaceOnnxArgs;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::IntoPyObjectExt;
use pythonize::{depythonize, pythonize};
use serde::{
    de::{MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};
use serde_json::json;
use serde_json::Value;
use std::collections::HashMap;

#[pyclass(eq)]
#[derive(PartialEq, Debug)]
pub enum InterfaceDataType {
    Pandas,
    Polars,
    Numpy,
    Arrow,
    Torch,
}

impl InterfaceDataType {
    pub fn from_module_name(module_name: &str) -> Result<Self, TypeError> {
        match module_name {
            "pandas.core.frame.DataFrame" => Ok(InterfaceDataType::Pandas),
            "polars.dataframe.frame.DataFrame" => Ok(InterfaceDataType::Polars),
            "numpy.ndarray" => Ok(InterfaceDataType::Numpy),
            "pyarrow.lib.Table" => Ok(InterfaceDataType::Arrow),
            "torch.Tensor" => Ok(InterfaceDataType::Torch),
            _ => Err(TypeError::InvalidDataType),
        }
    }
}

#[pyclass]
#[derive(Debug, Default, Clone, Deserialize, Serialize)]
pub struct DriftArgs {
    #[pyo3(get, set)]
    pub active: bool,

    #[pyo3(get, set)]
    pub deactivate_others: bool,
}

#[pymethods]
impl DriftArgs {
    #[new]
    #[pyo3(signature = (active=true, deactivate_others=false))]
    pub fn new(active: bool, deactivate_others: bool) -> Self {
        Self {
            active,
            deactivate_others,
        }
    }
}

#[pyclass]
#[derive(Debug, Default)]
pub struct ModelSaveKwargs {
    pub onnx: Option<Py<PyDict>>,

    pub model: Option<Py<PyDict>>,

    pub preprocessor: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    pub save_onnx: bool,

    #[pyo3(get, set)]
    pub drift: Option<DriftArgs>,
}

#[pymethods]
impl ModelSaveKwargs {
    #[new]
    #[pyo3(signature = (onnx=None, model=None, preprocessor=None, save_onnx=None, drift=None))]
    pub fn new<'py>(
        onnx: Option<Bound<'py, PyAny>>,
        model: Option<Bound<'py, PyDict>>,
        preprocessor: Option<Bound<'py, PyDict>>,
        save_onnx: Option<bool>,
        drift: Option<DriftArgs>,
    ) -> Result<Self, TypeError> {
        let mut save_onnx = save_onnx.unwrap_or(false);
        // check if onnx is None, PyDict or HuggingFaceOnnxArgs

        let onnx = onnx.map(|onnx| {
            if onnx.is_instance_of::<HuggingFaceOnnxArgs>() {
                let onnx_dict = onnx.call_method0("to_dict").unwrap();
                Ok(onnx_dict.cast::<PyDict>().unwrap().clone().unbind())
            } else if onnx.is_instance_of::<PyDict>() {
                Ok(onnx.cast::<PyDict>().unwrap().clone().unbind())
            } else {
                Err(TypeError::InvalidOnnxType)
            }
        });

        // set save_onnx to true if onnx is not None
        let onnx = match onnx {
            Some(Ok(onnx)) => {
                save_onnx = true;
                Some(onnx)
            }
            Some(Err(e)) => return Err(e),
            None => None,
        };

        let model = model.map(|model| model.unbind());
        let preprocessor = preprocessor.map(|preprocessor| preprocessor.unbind());
        Ok(Self {
            onnx,
            model,
            preprocessor,
            save_onnx,
            drift,
        })
    }

    pub fn __str__(&self, py: Python) -> String {
        let mut onnx = Value::Null;
        let mut model = Value::Null;
        let mut preprocessor = Value::Null;

        if let Some(onnx_args) = &self.onnx {
            onnx = depythonize(onnx_args.bind(py)).unwrap();
        }

        if let Some(model_args) = &self.model {
            model = depythonize(model_args.bind(py)).unwrap();
        }

        if let Some(preprocessor_args) = &self.preprocessor {
            preprocessor = depythonize(preprocessor_args.bind(py)).unwrap();
        }

        let json = json!({
            "onnx": onnx,
            "model": model,
            "preprocessor": preprocessor,
        });

        PyHelperFuncs::__str__(json)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> ModelSaveKwargs {
        serde_json::from_str(&json_string).unwrap()
    }
}

impl ModelSaveKwargs {
    pub fn onnx_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.onnx.as_ref().map(|onnx| onnx.bind(py))
    }

    pub fn model_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.model.as_ref().map(|model| model.bind(py))
    }

    pub fn preprocessor_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.preprocessor
            .as_ref()
            .map(|preprocessor| preprocessor.bind(py))
    }

    pub fn save_onnx(&self) -> bool {
        self.save_onnx
    }
}

impl Serialize for ModelSaveKwargs {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        Python::attach(|py| {
            let mut state = serializer.serialize_struct("ModelSaveKwargs", 5)?;

            let onnx: Option<serde_json::Value> = self
                .onnx
                .as_ref()
                .map(|onnx| depythonize(onnx.bind(py)))
                .transpose()
                .map_err(|e| {
                    serde::ser::Error::custom(format!("Failed to serialize onnx: {}", e))
                })?;

            let model: Option<serde_json::Value> = self
                .model
                .as_ref()
                .map(|model| depythonize(model.bind(py)))
                .transpose()
                .map_err(|e| {
                    serde::ser::Error::custom(format!("Failed to serialize model: {}", e))
                })?;

            let preprocessor: Option<serde_json::Value> = self
                .preprocessor
                .as_ref()
                .map(|preprocessor| depythonize(preprocessor.bind(py)))
                .transpose()
                .map_err(|e| {
                    serde::ser::Error::custom(format!("Failed to serialize preprocessor: {}", e))
                })?;

            state.serialize_field("onnx", &onnx)?;
            state.serialize_field("model", &model)?;
            state.serialize_field("preprocessor", &preprocessor)?;
            state.serialize_field("save_onnx", &self.save_onnx)?;
            state.serialize_field("drift", &self.drift)?;
            state.end()
        })
    }
}

/// Deserialize a dictionary field that may be null into Option<Py<PyDict>>
fn deserialize_dict_field<'de, A>(
    map: &mut A,
    py: Python<'_>,
) -> Result<Option<Py<PyDict>>, A::Error>
where
    A: MapAccess<'de>,
{
    let value = map.next_value::<serde_json::Value>()?;
    match value {
        serde_json::Value::Null => Ok(None),
        _ => {
            let py_obj = pythonize(py, &value)
                .map_err(|e| serde::de::Error::custom(format!("Deserialization failed: {}", e)))?;

            let dict = py_obj
                .cast::<PyDict>()
                .map_err(|_| serde::de::Error::custom("Expected a dictionary"))?
                .clone();

            Ok(Some(dict.unbind()))
        }
    }
}

impl<'de> Deserialize<'de> for ModelSaveKwargs {
    fn deserialize<D>(deserializer: D) -> Result<ModelSaveKwargs, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        struct ModelSaveKwargsVisitor;

        impl<'de> serde::de::Visitor<'de> for ModelSaveKwargsVisitor {
            type Value = ModelSaveKwargs;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct ModelSaveKwargs")
            }

            fn visit_map<A>(self, mut map: A) -> Result<ModelSaveKwargs, A::Error>
            where
                A: serde::de::MapAccess<'de>,
            {
                Python::attach(|py| {
                    let mut onnx = None;
                    let mut model = None;
                    let mut preprocessor = None;
                    let mut save_onnx = None;
                    let mut drift = None;

                    while let Some(key) = map.next_key::<String>()? {
                        match key.as_str() {
                            "onnx" => {
                                onnx = deserialize_dict_field(&mut map, py)?;
                            }
                            "model" => {
                                model = deserialize_dict_field(&mut map, py)?;
                            }
                            "preprocessor" => {
                                preprocessor = deserialize_dict_field(&mut map, py)?;
                            }
                            "save_onnx" => {
                                save_onnx = map.next_value::<Option<bool>>()?;
                            }
                            "drift" => {
                                drift = map.next_value::<Option<DriftArgs>>()?;
                            }
                            _ => {
                                let _: serde::de::IgnoredAny = map.next_value()?;
                            }
                        }
                    }

                    let kwargs = ModelSaveKwargs {
                        onnx,
                        model,
                        preprocessor,
                        save_onnx: save_onnx.unwrap_or(false),
                        drift,
                    };
                    Ok(kwargs)
                })
            }
        }

        deserializer.deserialize_struct(
            "ModelSaveKwargs",
            &["onnx", "model", "preprocessor", "save_onnx"],
            ModelSaveKwargsVisitor,
        )
    }
}

impl Clone for ModelSaveKwargs {
    fn clone(&self) -> Self {
        Python::attach(|py| {
            let onnx = self.onnx.as_ref().map(|onnx| onnx.clone_ref(py));
            let model = self.model.as_ref().map(|model| model.clone_ref(py));
            let preprocessor = self
                .preprocessor
                .as_ref()
                .map(|preprocessor| preprocessor.clone_ref(py));
            let save_onnx = self.save_onnx;
            let drift = self.drift.clone();

            ModelSaveKwargs {
                onnx,
                model,
                preprocessor,
                save_onnx,
                drift,
            }
        })
    }
}

#[pyclass]
#[derive(Debug, Default)]
pub struct ModelLoadKwargs {
    #[pyo3(get, set)]
    pub onnx: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    pub model: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    pub preprocessor: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    pub load_onnx: bool,
}

#[pymethods]
impl ModelLoadKwargs {
    #[new]
    #[pyo3(signature = (onnx=None, model=None, preprocessor=None, load_onnx=false))]
    pub fn new<'py>(
        onnx: Option<Bound<'py, PyAny>>,
        model: Option<Bound<'py, PyDict>>,
        preprocessor: Option<Bound<'py, PyDict>>,
        load_onnx: Option<bool>,
    ) -> Result<Self, TypeError> {
        // check if onnx is None, PyDict or HuggingFaceOnnxArgs

        let onnx = onnx.map(|onnx| {
            if onnx.is_instance_of::<HuggingFaceOnnxArgs>() {
                let onnx_dict = onnx.call_method0("to_dict").unwrap();
                Ok(onnx_dict.cast::<PyDict>().unwrap().clone().unbind())
            } else if onnx.is_instance_of::<PyDict>() {
                Ok(onnx.cast::<PyDict>().unwrap().clone().unbind())
            } else {
                // return error
                Err(TypeError::InvalidOnnxType)
            }
        });

        // check for error
        let onnx = match onnx {
            Some(Ok(onnx)) => Some(onnx),
            Some(Err(e)) => return Err(e),
            None => None,
        };

        let load_onnx = if onnx.is_some() {
            load_onnx.unwrap_or(true)
        } else {
            load_onnx.unwrap_or(false)
        };

        let model = model.map(|model| model.unbind());
        let preprocessor = preprocessor.map(|preprocessor| preprocessor.unbind());
        Ok(Self {
            onnx,
            model,
            preprocessor,
            load_onnx,
        })
    }
}

impl ModelLoadKwargs {
    pub fn onnx_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.onnx.as_ref().map(|onnx| onnx.bind(py))
    }

    pub fn model_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.model.as_ref().map(|model| model.bind(py))
    }

    pub fn preprocessor_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.preprocessor
            .as_ref()
            .map(|preprocessor| preprocessor.bind(py))
    }
}

impl Clone for ModelLoadKwargs {
    fn clone(&self) -> Self {
        Python::attach(|py| {
            let onnx = self.onnx.as_ref().map(|onnx| onnx.clone_ref(py));
            let model = self.model.as_ref().map(|model| model.clone_ref(py));
            let preprocessor = self
                .preprocessor
                .as_ref()
                .map(|preprocessor| preprocessor.clone_ref(py));
            let load_onnx = self.load_onnx;

            ModelLoadKwargs {
                onnx,
                model,
                preprocessor,
                load_onnx,
            }
        })
    }
}

#[pyclass]
#[derive(Debug)]
pub struct ExtraMetadata {
    metadata: Py<PyDict>,
}

#[pymethods]
impl ExtraMetadata {
    #[new]
    #[pyo3(signature = (metadata))]
    pub fn new(metadata: Bound<'_, PyDict>) -> Self {
        // check if onnx is None, PyDict or HuggingFaceOnnxArgs

        let metadata = metadata.unbind();
        Self { metadata }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__json__(self)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> ModelSaveKwargs {
        serde_json::from_str(&json_string).unwrap()
    }
}

impl Serialize for ExtraMetadata {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        Python::attach(|py| {
            let mut state = serializer.serialize_struct("ExtraMetadata", 1)?;
            let metadata: serde_json::Value = depythonize(self.metadata.bind(py)).map_err(|e| {
                serde::ser::Error::custom(format!("Failed to serialize metadata: {}", e))
            })?;

            state.serialize_field("metadata", &metadata)?;
            state.end()
        })
    }
}

impl<'de> Deserialize<'de> for ExtraMetadata {
    fn deserialize<D>(deserializer: D) -> Result<ExtraMetadata, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        struct ExtraMetadataVisitor;

        impl<'de> serde::de::Visitor<'de> for ExtraMetadataVisitor {
            type Value = ExtraMetadata;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct ExtraMetadata")
            }

            fn visit_map<A>(self, mut map: A) -> Result<ExtraMetadata, A::Error>
            where
                A: serde::de::MapAccess<'de>,
            {
                Python::attach(|py| {
                    let mut metadata = None;

                    while let Some(key) = map.next_key::<String>()? {
                        match key.as_str() {
                            "metadata" => {
                                metadata = deserialize_dict_field(&mut map, py)?;
                            }

                            _ => {
                                let _: serde::de::IgnoredAny = map.next_value()?;
                            }
                        }
                    }
                    let kwargs = ExtraMetadata {
                        metadata: metadata.unwrap(),
                    };
                    Ok(kwargs)
                })
            }
        }

        deserializer.deserialize_struct("ExtraMetadata", &["metadata"], ExtraMetadataVisitor)
    }
}

impl Clone for ExtraMetadata {
    fn clone(&self) -> Self {
        Python::attach(|py| {
            let metadata = self.metadata.clone_ref(py);

            ExtraMetadata { metadata }
        })
    }
}

#[pyclass]
#[derive(Debug)]
pub struct DriftProfileMap {
    pub profiles: HashMap<String, Py<PyAny>>,
}

impl Clone for DriftProfileMap {
    fn clone(&self) -> Self {
        Python::attach(|py| {
            let mut profiles = HashMap::new();
            for (k, v) in &self.profiles {
                profiles.insert(k.clone(), v.clone_ref(py));
            }
            Self { profiles }
        })
    }
}

impl Serialize for DriftProfileMap {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let state = serializer.serialize_struct("DriftProfileMap", 0)?;
        state.end()
    }
}

impl<'de> Deserialize<'de> for DriftProfileMap {
    fn deserialize<D>(deserializer: D) -> Result<DriftProfileMap, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct DriftProfileMapVisitor;

        impl<'de> Visitor<'de> for DriftProfileMapVisitor {
            type Value = DriftProfileMap;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct DriftProfileMap")
            }

            fn visit_map<A>(self, _map: A) -> Result<DriftProfileMap, A::Error>
            where
                A: MapAccess<'de>,
            {
                let profile = DriftProfileMap::default();
                Ok(profile)
            }
        }

        deserializer.deserialize_struct("DriftProfileMap", &["profiles"], DriftProfileMapVisitor)
    }
}

#[pymethods]
impl DriftProfileMap {
    #[new]
    pub fn new() -> Self {
        let profiles = HashMap::new();
        DriftProfileMap { profiles }
    }

    pub fn add_profile(
        &mut self,
        py: Python,
        alias: String,
        profile: Bound<'_, PyAny>,
    ) -> Result<(), ModelInterfaceError> {
        self.profiles.insert(alias, profile.into_py_any(py)?);
        Ok(())
    }

    /// Get a drift profile by alias
    ///
    /// # Arguments
    /// * `alias` - The alias of the drift profile
    ///
    /// # Returns
    /// * `PyResult<Bound<'py, PyAny>>` - The drift profile
    pub fn __getitem__<'py>(
        &self,
        py: Python<'py>,
        key: String,
    ) -> Result<&Bound<'py, PyAny>, ModelInterfaceError> {
        let profile = self
            .profiles
            .get(&key)
            .ok_or_else(|| ModelInterfaceError::DriftProfileNotFound)
            .map(|profile| profile.bind(py))?;

        Ok(profile)
    }

    pub fn is_empty(&self) -> bool {
        self.profiles.is_empty()
    }

    pub fn update_config_args(
        &mut self,
        py: Python,
        config_args: &Bound<'_, PyDict>,
    ) -> Result<(), ModelInterfaceError> {
        // iterate over the profiles and update the config args

        for profile in self.profiles.values() {
            let profile = profile.bind(py);
            profile.call_method("update_config_args", (), Some(config_args))?;
        }
        Ok(())
    }

    /// Get the drift profile map as a list of profiles
    /// This is a helper method used during card registration and artifact saving
    pub fn values<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyList>, ModelInterfaceError> {
        let py_list = PyList::empty(py);
        for profile in self.profiles.values() {
            py_list.append(profile.bind(py))?;
        }

        Ok(py_list)
    }

    pub fn __str__(&self, py: Python) -> String {
        let mut map = json!({});
        for (k, v) in &self.profiles {
            let profile = v.bind(py);
            let profile_json = profile
                .call_method0("model_dump_json")
                .unwrap()
                .extract::<String>()
                .unwrap();

            map[k] = serde_json::from_str(&profile_json).unwrap();
        }

        PyHelperFuncs::__str__(map)
    }
}

impl DriftProfileMap {}

impl Default for DriftProfileMap {
    fn default() -> Self {
        Self::new()
    }
}
