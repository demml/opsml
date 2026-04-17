use crate::error::ModelInterfaceError;
use opsml_types::error::TypeError;
use opsml_types::interfaces::HuggingFaceOnnxArgs;
use opsml_utils::PyHelperFuncs;
use pyo3::IntoPyObjectExt;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde::{
    Deserialize, Deserializer, Serialize, Serializer,
    de::{MapAccess, Visitor},
    ser::SerializeStruct,
};
use serde_json::json;
use std::collections::HashMap;
use tracing::{debug, instrument};

#[pyclass(eq, skip_from_py_object)]
#[derive(PartialEq, Debug)]
pub enum InterfaceDataType {
    Pandas,
    Polars,
    Numpy,
    Arrow,
    Torch,
}

impl InterfaceDataType {
    #[instrument(skip_all)]
    pub fn from_module_name(module_name: &str) -> Result<Self, TypeError> {
        debug!("Mapping module name to InterfaceDataType: {}", module_name);
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

#[pyclass(from_py_object)]
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

#[pyclass(skip_from_py_object)]
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
            .ok_or_else(|| ModelInterfaceError::DriftProfileNotFoundInMap)
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
