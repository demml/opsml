use crate::base::ExtraMetadata;
use crate::error::TypeError;
use opsml_types::{SaveName, Suffix};
use opsml_utils::{json_to_pyobject, pyobject_to_json};
use opsml_utils::{FileUtils, PyHelperFuncs};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::ser::SerializeStruct;
use serde::{Deserialize, Serialize};
use serde_json::json;
use serde_json::Value;
use std::{
    collections::HashMap,
    path::{Path, PathBuf},
};

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DependentVars {
    #[pyo3(get, set)]
    pub column_names: Vec<String>,

    #[pyo3(get, set)]
    pub column_indices: Vec<usize>,

    pub is_idx: bool,
}

#[pymethods]
impl DependentVars {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (column_names=None, column_indices=None))]
    pub fn new(column_names: Option<Vec<String>>, column_indices: Option<Vec<usize>>) -> Self {
        let column_names = column_names.unwrap_or_default();
        let column_indices = column_indices.unwrap_or_default();

        let is_idx = !column_indices.is_empty();

        DependentVars {
            column_names,
            column_indices,
            is_idx,
        }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl DependentVars {
    pub fn get_column_indices(&self) -> Vec<usize> {
        self.column_indices.clone()
    }

    pub fn column_empty(&self) -> bool {
        self.column_names.is_empty()
    }

    pub fn idx_empty(&self) -> bool {
        self.column_indices.is_empty()
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct SqlLogic {
    #[pyo3(get, set)]
    pub queries: HashMap<String, String>,
}

#[pymethods]
impl SqlLogic {
    #[new]
    #[pyo3(signature = (queries=None))]
    pub fn new(queries: Option<HashMap<String, String>>) -> Result<Self, TypeError> {
        Ok(SqlLogic {
            queries: SqlLogic::extract_sql_logic(queries.unwrap_or_default())?,
        })
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    #[pyo3(signature = (name, query=None, filepath=None))]
    pub fn add_sql_logic(
        &mut self,
        name: String,
        query: Option<String>,
        filepath: Option<String>,
    ) -> Result<(), TypeError> {
        let query = query.unwrap_or_default();
        let filepath = filepath.unwrap_or_default();

        if !query.is_empty() && !filepath.is_empty() {
            return Err(TypeError::OnlyOneQueryorFilenameError);
        }

        if !query.is_empty() {
            self.queries.insert(name, query);
        } else {
            let query = FileUtils::open_file(&filepath)?;
            self.queries.insert(name, query);
        }

        Ok(())
    }

    pub fn __getitem__(&self, key: &str) -> Result<String, TypeError> {
        match self.queries.get(key) {
            Some(query) => Ok(query.clone()),
            None => Err(TypeError::KeyNotFound),
        }
    }
}

impl SqlLogic {
    fn extract_sql_logic(
        sql_logic: HashMap<String, String>,
    ) -> Result<HashMap<String, String>, TypeError> {
        // check if sql logic is present
        if sql_logic.is_empty() {
            return Ok(sql_logic);
        }

        // get the sql logic
        sql_logic
            .into_iter()
            .map(|(key, value)| {
                if value.ends_with(".sql") {
                    let sql = FileUtils::open_file(&value)?;
                    Ok((key, sql))
                } else {
                    Ok((key, value))
                }
            })
            .collect()
    }

    pub fn save(&self, save_path: &Path) -> Result<PathBuf, TypeError> {
        let sql_directory = save_path.join(SaveName::Sql);

        // create directory if it does not exist
        if !sql_directory.exists() {
            std::fs::create_dir_all(&sql_directory)?;
        }

        for (key, value) in &self.queries {
            let save_path = sql_directory.join(key).with_extension(Suffix::Sql);

            // save string to file
            std::fs::write(save_path, value)?;
        }

        Ok(sql_directory)
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DataInterfaceSaveMetadata {
    #[pyo3(get)]
    pub data_uri: PathBuf,

    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data_profile_uri: Option<PathBuf>,

    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sql_uri: Option<PathBuf>,

    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extra: Option<ExtraMetadata>,

    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub save_kwargs: Option<DataSaveKwargs>,
}

#[pymethods]
impl DataInterfaceSaveMetadata {
    #[new]
    #[pyo3(signature = (data_uri, sql_uri=None, data_profile_uri=None, extra=None, save_kwargs=None))]
    pub fn new(
        data_uri: PathBuf,
        sql_uri: Option<PathBuf>,
        data_profile_uri: Option<PathBuf>,
        extra: Option<ExtraMetadata>,
        save_kwargs: Option<DataSaveKwargs>,
    ) -> Self {
        DataInterfaceSaveMetadata {
            data_uri,
            sql_uri,
            data_profile_uri,
            extra,
            save_kwargs,
        }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass]
#[derive(Debug, Default)]
pub struct DataSaveKwargs {
    pub data: Option<Py<PyDict>>,
}

#[pymethods]
impl DataSaveKwargs {
    #[new]
    #[pyo3(signature = (data=None))]
    pub fn new(data: Option<Bound<'_, PyDict>>) -> Result<Self, TypeError> {
        // check if onnx is None, PyDict or HuggingFaceOnnxArgs

        let data = data.map(|data| data.unbind());

        Ok(Self { data })
    }

    pub fn __str__(&self, py: Python) -> String {
        let mut data = Value::Null;

        if let Some(data_args) = &self.data {
            data = pyobject_to_json(data_args.bind(py)).unwrap();
        }

        let json = json!({
            "data": data,
        });

        PyHelperFuncs::__str__(json)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> DataSaveKwargs {
        serde_json::from_str(&json_string).unwrap()
    }
}

impl DataSaveKwargs {
    pub fn data_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.data.as_ref().map(|data| data.bind(py))
    }
}

impl Serialize for DataSaveKwargs {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        Python::attach(|py| {
            let mut state = serializer.serialize_struct("DataSaveKwargs", 1)?;
            let data = self
                .data
                .as_ref()
                .map(|onnx| pyobject_to_json(onnx.bind(py)).unwrap());

            state.serialize_field("data", &data)?;
            state.end()
        })
    }
}

impl<'de> Deserialize<'de> for DataSaveKwargs {
    fn deserialize<D>(deserializer: D) -> Result<DataSaveKwargs, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        struct DataSaveKwargsVisitor;

        impl<'de> serde::de::Visitor<'de> for DataSaveKwargsVisitor {
            type Value = DataSaveKwargs;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct DataSaveKwargs")
            }

            fn visit_map<A>(self, mut map: A) -> Result<DataSaveKwargs, A::Error>
            where
                A: serde::de::MapAccess<'de>,
            {
                Python::attach(|py| {
                    let mut data = None;

                    while let Some(key) = map.next_key::<String>()? {
                        match key.as_str() {
                            "data" => {
                                let value = map.next_value::<serde_json::Value>()?;
                                match value {
                                    serde_json::Value::Null => {
                                        data = None;
                                    }
                                    _ => {
                                        let dict =
                                            json_to_pyobject(py, &value, &PyDict::new(py)).unwrap();
                                        data = Some(dict.unbind());
                                    }
                                }
                            }
                            _ => {
                                let _: serde::de::IgnoredAny = map.next_value()?;
                            }
                        }
                    }
                    let kwargs = DataSaveKwargs { data };
                    Ok(kwargs)
                })
            }
        }

        deserializer.deserialize_struct(
            "DataSaveKwargs",
            &["onnx", "model", "preprocessor"],
            DataSaveKwargsVisitor,
        )
    }
}

impl Clone for DataSaveKwargs {
    fn clone(&self) -> Self {
        Python::attach(|py| {
            let data = self.data.as_ref().map(|data| data.clone_ref(py));

            DataSaveKwargs { data }
        })
    }
}

#[pyclass]
#[derive(Debug, Default)]
pub struct DataLoadKwargs {
    #[pyo3(get, set)]
    data: Option<Py<PyDict>>,
}

#[pymethods]
impl DataLoadKwargs {
    #[new]
    #[pyo3(signature = (data=None))]
    pub fn new(data: Option<Bound<'_, PyDict>>) -> Result<Self, TypeError> {
        let data = data.map(|data| data.unbind());

        Ok(Self { data })
    }
}

impl DataLoadKwargs {
    pub fn data_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.data.as_ref().map(|data| data.bind(py))
    }
}

impl Clone for DataLoadKwargs {
    fn clone(&self) -> Self {
        Python::attach(|py| {
            let data = self.data.as_ref().map(|data| data.clone_ref(py));

            DataLoadKwargs { data }
        })
    }
}
