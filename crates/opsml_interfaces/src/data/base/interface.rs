use crate::data::DataSaveKwargs;
use crate::data::{
    generate_feature_schema, Data, DataInterfaceSaveMetadata, DataSplit, DataSplits, DependentVars,
    SqlLogic,
};
use crate::types::FeatureSchema;
use opsml_error::error::OpsmlError;
use opsml_types::{DataInterfaceType, DataType, SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::{PyAny, PyAnyMethods, PyList};
use pyo3::IntoPyObjectExt;
use scouter_client::{DataProfile, DataProfiler};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::path::Path;
use std::path::PathBuf;
use tracing::instrument;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DataInterfaceMetadata {
    #[pyo3(get)]
    save_metadata: DataInterfaceSaveMetadata,

    #[pyo3(get)]
    schema: FeatureSchema,

    #[pyo3(get)]
    pub extra_metadata: HashMap<String, String>,

    #[pyo3(get, set)]
    pub sql_logic: SqlLogic,

    #[pyo3(get)]
    pub interface_type: DataInterfaceType,

    pub data_specific_metadata: Value,
}

#[pymethods]
impl DataInterfaceMetadata {
    #[new]
    #[pyo3(signature = (save_metadata, schema=FeatureSchema::default(), extra_metadata=HashMap::new(), sql_logic=SqlLogic::default(),interface_type=DataInterfaceType::Base))]
    pub fn new(
        save_metadata: DataInterfaceSaveMetadata,
        schema: FeatureSchema,
        extra_metadata: HashMap<String, String>,
        sql_logic: SqlLogic,
        interface_type: DataInterfaceType,
    ) -> Self {
        DataInterfaceMetadata {
            save_metadata,
            schema,
            extra_metadata,
            sql_logic,
            interface_type,
            data_specific_metadata: Value::Null,
        }
    }
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> DataInterfaceMetadata {
        serde_json::from_str(&json_string).unwrap()
    }
}

#[pyclass(subclass)]
pub struct DataInterface {
    #[pyo3(get)]
    pub data: PyObject,

    #[pyo3(get)]
    pub data_splits: DataSplits,

    #[pyo3(get)]
    pub dependent_vars: DependentVars,

    #[pyo3(get, set)]
    pub schema: FeatureSchema,

    #[pyo3(get, set)]
    pub sql_logic: SqlLogic,

    #[pyo3(get, set)]
    pub data_profile: Option<DataProfile>,

    #[pyo3(get)]
    pub data_type: DataType,

    #[pyo3(get)]
    pub interface_type: DataInterfaceType,
}

#[pymethods]
impl DataInterface {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, schema=None, sql_logic=None, data_profile=None))]
    pub fn new<'py>(
        py: Python,
        data: Option<&Bound<'py, PyAny>>, // data can be any pyobject
        data_splits: Option<&Bound<'py, PyAny>>, //
        dependent_vars: Option<&Bound<'py, PyAny>>,
        schema: Option<FeatureSchema>,
        sql_logic: Option<SqlLogic>,
        data_profile: Option<DataProfile>,
    ) -> PyResult<Self> {
        // define data splits
        let splits: DataSplits = {
            if let Some(data_splits) = data_splits {
                // check if data_splits is either Vec<DataSplit> or DataSplits
                if data_splits.is_instance_of::<DataSplits>() {
                    data_splits.extract::<DataSplits>()?
                } else if data_splits.is_instance_of::<PyList>() {
                    // pylist should be list of DataSplit
                    DataSplits::new(data_splits.extract::<Vec<DataSplit>>()?)
                } else {
                    DataSplits::default()
                }
            } else {
                DataSplits::default()
            }
        };

        // define dependent vars
        let depen_vars: DependentVars = {
            if let Some(dependent_vars) = dependent_vars {
                // check if dependent_vars is either DependentVars or Vec<String>, Vec<usize> or DependentVars
                if dependent_vars.is_instance_of::<DependentVars>() {
                    dependent_vars.extract::<DependentVars>()?
                } else if dependent_vars.is_instance_of::<PyList>() {
                    // pylist should be list of string or list of int
                    if dependent_vars.extract::<Vec<String>>().is_ok() {
                        let column_names = dependent_vars.extract::<Vec<String>>()?;
                        DependentVars::new(Some(column_names), None)
                    } else if dependent_vars.extract::<Vec<usize>>().is_ok() {
                        let column_indices = dependent_vars.extract::<Vec<usize>>()?;
                        DependentVars::new(None, Some(column_indices))
                    } else {
                        DependentVars::default()
                    }
                } else {
                    DependentVars::default()
                }
            } else {
                DependentVars::default()
            }
        };

        let schema = schema.unwrap_or_default();
        let sql_logic = sql_logic.unwrap_or_default();

        let data = match data {
            Some(data) => data.into_py_any(py)?,
            None => py.None(),
        };
        Ok(DataInterface {
            data,
            data_splits: splits,
            dependent_vars: depen_vars,
            schema,
            sql_logic,
            data_type: DataType::Base,
            interface_type: DataInterfaceType::Base,
            data_profile,
        })
    }

    #[setter]
    pub fn set_data(&mut self, data: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = data.py();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            self.data = py.None();
            return Ok(());
        } else {
            self.data = data.into_py_any(py)?;
        };

        Ok(())
    }

    #[setter]
    pub fn set_data_splits(&mut self, data_splits: &Bound<'_, PyAny>) -> PyResult<()> {
        // check if data_splits is None
        if PyAnyMethods::is_none(data_splits) {
            self.data_splits = DataSplits::default();
            return Ok(());
        }

        // check if data_splits is either Vec<DataSplit> or DataSplits
        if data_splits.is_instance_of::<DataSplits>() {
            self.data_splits = data_splits.extract::<DataSplits>()?;
        } else if data_splits.is_instance_of::<PyList>() {
            // pylist should be list of DataSplit
            self.data_splits = DataSplits::new(data_splits.extract::<Vec<DataSplit>>()?);
        } else {
            self.data_splits = DataSplits::default();
        }

        Ok(())
    }

    #[setter]
    pub fn set_dependent_vars(&mut self, dependent_vars: &Bound<'_, PyAny>) -> PyResult<()> {
        // check if dependent_vars is None
        if PyAnyMethods::is_none(dependent_vars) {
            self.dependent_vars = DependentVars::default();
            return Ok(());
        }

        // check if dependent_vars is either DependentVars or Vec<String>, Vec<usize> or DependentVars
        if dependent_vars.is_instance_of::<DependentVars>() {
            self.dependent_vars = dependent_vars.extract::<DependentVars>()?;
        } else if dependent_vars.is_instance_of::<PyList>() {
            // pylist should be list of string or list of int
            if dependent_vars.extract::<Vec<String>>().is_ok() {
                let column_names = dependent_vars.extract::<Vec<String>>()?;
                self.dependent_vars = DependentVars::new(Some(column_names), None);
            } else if dependent_vars.extract::<Vec<usize>>().is_ok() {
                let column_indices = dependent_vars.extract::<Vec<usize>>()?;
                self.dependent_vars = DependentVars::new(None, Some(column_indices));
            } else {
                self.dependent_vars = DependentVars::default();
            }
        } else {
            self.dependent_vars = DependentVars::default();
        }

        Ok(())
    }

    /// Save the data and SQL logic
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
    #[pyo3(signature = (path, save_kwargs=None))]
    pub fn save(
        &mut self,
        py: Python,
        path: PathBuf,
        save_kwargs: Option<DataSaveKwargs>,
    ) -> PyResult<DataInterfaceMetadata> {
        let data_kwargs = save_kwargs
            .as_ref()
            .and_then(|args| args.data_kwargs(py))
            .cloned();

        let data_uri = self.save_data(py, path.clone(), data_kwargs.as_ref())?;

        // save sql logic
        let sql_uri = self.save_sql(path.clone())?;
        self.schema = self.create_feature_map(py)?;

        let data_profile_uri = if self.data_profile.is_none() {
            None
        } else {
            Some(self.save_data_profile(&path)?)
        };

        let save_metadata =
            DataInterfaceSaveMetadata::new(data_uri, sql_uri, data_profile_uri, None, save_kwargs);

        Ok(DataInterfaceMetadata::new(
            save_metadata,
            self.schema.clone(),
            HashMap::new(),
            self.sql_logic.clone(),
            self.interface_type.clone(),
        ))
    }
    #[pyo3(signature = (path, **kwargs))]
    pub fn load_data(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Joblib);
        let joblib = py.import("joblib")?;

        // Load the data using joblib
        self.data = joblib.call_method("load", (load_path,), kwargs)?.into();

        Ok(())
    }

    #[pyo3(signature = (name, query=None, filepath=None))]
    pub fn add_sql_logic(
        &mut self,
        name: String,
        query: Option<String>,
        filepath: Option<String>,
    ) -> PyResult<()> {
        self.sql_logic.add_sql_logic(name, query, filepath)?;

        Ok(())
    }

    pub fn split_data(&mut self, py: Python) -> PyResult<HashMap<String, Data>> {
        // check if data is None
        if self.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        if self.data_splits.is_empty() {
            return Err(OpsmlError::new_err(
                "No data splits detected in interface for splitting",
            ));
        }

        let dependent_vars = self.dependent_vars.clone();

        self.data_splits
            .split_data(self.data.bind(py), &self.data_type, &dependent_vars)
    }

    #[pyo3(signature = (bin_size=20, compute_correlations=false))]
    pub fn create_data_profile(
        &mut self,
        py: Python,
        bin_size: Option<usize>,
        compute_correlations: Option<bool>,
    ) -> PyResult<DataProfile> {
        let mut profiler = DataProfiler::new();

        // get ScouterDataType from opsml DataType

        let data_type = match self.data_type {
            DataType::Numpy => Some(&scouter_client::DataType::Numpy),
            DataType::Pandas => Some(&scouter_client::DataType::Pandas),
            DataType::Polars => Some(&scouter_client::DataType::Polars),
            DataType::Arrow => Some(&scouter_client::DataType::Arrow),
            _ => Err(OpsmlError::new_err("Data type not supported for profiling"))?,
        };

        let profile = profiler.create_data_profile(
            py,
            self.data.bind(py),
            data_type,
            bin_size,
            compute_correlations,
        )?;

        self.data_profile = Some(profile.clone());

        Ok(profile)
    }
}

impl DataInterface {
    /// Save the SQL logic to a file
    ///
    /// # Arguments
    ///
    /// * `path` - Path to save the SQL logic
    ///
    /// # Returns
    ///
    /// * `Option<PathBuf>` - Path to the saved SQL logic
    pub fn save_sql(&self, path: PathBuf) -> PyResult<Option<PathBuf>> {
        if !self.sql_logic.queries.is_empty() {
            Ok(Some(self.sql_logic.save(&path)?))
        } else {
            Ok(None)
        }
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
    pub fn create_feature_map(&mut self, py: Python) -> PyResult<FeatureSchema> {
        // Create and insert the feature
        let feature_map = generate_feature_schema(self.data.bind(py), &self.data_type)?;

        self.schema = feature_map.clone();

        Ok(feature_map)
    }

    /// Save the data
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `path` - Path to save the data
    /// * `kwargs` - Additional save kwargs
    ///
    /// # Returns
    ///
    /// * `PyResult<PathBuf>` - Path to the saved data
    ///
    pub fn save_data(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        // check if data is None
        if self.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Joblib);
        let full_save_path = path.join(&save_path);
        let joblib = py.import("joblib")?;

        // Save the data using joblib
        joblib.call_method("dump", (&self.data, full_save_path), kwargs)?;

        Ok(save_path)
    }

    /// Save drift profile
    ///
    /// # Arguments
    ///
    /// * `path` - Path to save drift profile
    ///
    /// # Returns
    ///
    /// * `PyResult<PathBuf>` - Path to saved drift profile
    #[instrument(skip(self, path) name = "save_drift_profile")]
    pub fn save_data_profile(&self, path: &Path) -> PyResult<PathBuf> {
        let profile_save_path = path
            .join(SaveName::DataProfile)
            .with_extension(Suffix::Json);
        self.data_profile
            .as_ref()
            .unwrap()
            .save_to_json(Some(profile_save_path.clone()))?;

        Ok(profile_save_path)
    }
}
