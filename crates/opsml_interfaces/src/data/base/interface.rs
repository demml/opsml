use crate::data::DataSaveKwargs;
use crate::data::{
    Data, DataInterfaceSaveMetadata, DataLoadKwargs, DataSplit, DataSplits, DependentVars,
    SqlLogic, generate_feature_schema,
};
use crate::error::DataInterfaceError;
use crate::types::FeatureSchema;
use opsml_types::{DataInterfaceType, DataType, SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::{PyAny, PyAnyMethods, PyList};
use pyo3::{IntoPyObjectExt, PyTraverseError, PyVisit};
use scouter_client::{DataProfile, DataProfiler};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::path::Path;
use std::path::PathBuf;
use tracing::debug;
use tracing::instrument;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DataInterfaceMetadata {
    #[pyo3(get)]
    pub save_metadata: DataInterfaceSaveMetadata,

    #[pyo3(get)]
    pub schema: FeatureSchema,

    #[pyo3(get)]
    pub extra_metadata: HashMap<String, String>,

    #[pyo3(get, set)]
    pub sql_logic: SqlLogic,

    #[pyo3(get)]
    pub interface_type: DataInterfaceType,

    #[pyo3(get)]
    pub data_splits: DataSplits,

    #[pyo3(get)]
    pub dependent_vars: DependentVars,

    #[pyo3(get)]
    pub data_type: DataType,

    pub data_specific_metadata: Value,
}

#[pymethods]
impl DataInterfaceMetadata {
    #[new]
    #[pyo3(signature = (save_metadata, schema=FeatureSchema::default(), extra_metadata=HashMap::new(), sql_logic=SqlLogic::default(),interface_type=DataInterfaceType::Base, dependent_vars=DependentVars::default(), data_splits=DataSplits::default(), data_type=DataType::Base))]
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        save_metadata: DataInterfaceSaveMetadata,
        schema: FeatureSchema,
        extra_metadata: HashMap<String, String>,
        sql_logic: SqlLogic,
        interface_type: DataInterfaceType,
        dependent_vars: DependentVars,
        data_splits: DataSplits,
        data_type: DataType,
    ) -> Self {
        DataInterfaceMetadata {
            save_metadata,
            schema,
            extra_metadata,
            sql_logic,
            interface_type,
            dependent_vars,
            data_splits,
            data_type,
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

pub fn check_data_splits(
    data_splits: Option<&Bound<'_, PyAny>>,
) -> Result<DataSplits, DataInterfaceError> {
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

    Ok(splits)
}

pub fn check_dependent_vars(
    dependent_vars: Option<&Bound<'_, PyAny>>,
) -> Result<DependentVars, DataInterfaceError> {
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

    Ok(depen_vars)
}

#[pyclass(subclass)]
pub struct DataInterface {
    #[pyo3(get)]
    pub data: Option<Py<PyAny>>,

    #[pyo3(get)]
    pub data_splits: DataSplits,

    #[pyo3(get)]
    pub dependent_vars: DependentVars,

    #[pyo3(get, set)]
    pub schema: FeatureSchema,

    #[pyo3(get, set)]
    pub sql_logic: SqlLogic,

    #[pyo3(get)]
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
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, sql_logic=None, data_profile=None))]
    pub fn new<'py>(
        py: Python,
        data: Option<&Bound<'py, PyAny>>, // data can be any pyobject
        data_splits: Option<&Bound<'py, PyAny>>, //
        dependent_vars: Option<&Bound<'py, PyAny>>,
        sql_logic: Option<SqlLogic>,
        data_profile: Option<DataProfile>,
    ) -> Result<Self, DataInterfaceError> {
        // define data splits
        let splits: DataSplits = check_data_splits(data_splits)?;
        let depen_vars: DependentVars = check_dependent_vars(dependent_vars)?;

        let sql_logic = sql_logic.unwrap_or_default();

        let data = match data {
            Some(data) => Some(data.into_py_any(py)?),
            None => None,
        };
        Ok(DataInterface {
            data,
            data_splits: splits,
            dependent_vars: depen_vars,
            schema: FeatureSchema::default(),
            sql_logic,
            data_type: DataType::Base,
            interface_type: DataInterfaceType::Base,
            data_profile,
        })
    }

    #[setter]
    pub fn set_data(&mut self, data: &Bound<'_, PyAny>) -> Result<(), DataInterfaceError> {
        let py = data.py();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            self.data = None;
            return Ok(());
        } else {
            self.data = Some(data.into_py_any(py)?);
        };

        Ok(())
    }

    #[setter]
    pub fn set_data_profile(
        &mut self,
        data_profile: &Bound<'_, PyAny>,
    ) -> Result<(), DataInterfaceError> {
        // check if data_profile is None
        if PyAnyMethods::is_none(data_profile) {
            self.data_profile = None;
            return Ok(());
        } else {
            self.data_profile = Some(data_profile.extract::<DataProfile>()?);
        };

        Ok(())
    }

    #[setter]
    pub fn set_data_splits(
        &mut self,
        data_splits: &Bound<'_, PyAny>,
    ) -> Result<(), DataInterfaceError> {
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
    pub fn set_dependent_vars(
        &mut self,
        dependent_vars: &Bound<'_, PyAny>,
    ) -> Result<(), DataInterfaceError> {
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
    /// * `Result<DataInterfaceSaveMetadata>` - DataInterfaceSaveMetadata
    #[pyo3(signature = (path, save_kwargs=None))]
    pub fn save(
        &mut self,
        py: Python,
        path: PathBuf,
        save_kwargs: Option<DataSaveKwargs>,
    ) -> Result<DataInterfaceMetadata, DataInterfaceError> {
        let data_kwargs = save_kwargs
            .as_ref()
            .and_then(|args| args.data_kwargs(py))
            .cloned();

        let data_uri = self.save_data(py, path.clone(), data_kwargs.as_ref())?;

        // save sql logic
        let sql_uri = self.save_sql(path.clone())?;
        self.schema = self.create_schema(py)?;

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
            self.dependent_vars.clone(),
            self.data_splits.clone(),
            self.data_type.clone(),
        ))
    }
    #[pyo3(signature = (path, metadata, load_kwargs = None))]
    pub fn load(
        &mut self,
        py: Python,
        path: PathBuf,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Option<DataLoadKwargs>,
    ) -> Result<(), DataInterfaceError> {
        let load_path = path.join(metadata.data_uri);
        let joblib = py.import("joblib")?;
        let load_kwargs = load_kwargs.unwrap_or_default();

        // Load the data using joblib
        let data = joblib.call_method("load", (load_path,), load_kwargs.data_kwargs(py))?;

        self.data = Some(data.into());

        Ok(())
    }

    #[pyo3(signature = (name, query=None, filepath=None))]
    pub fn add_sql_logic(
        &mut self,
        name: String,
        query: Option<String>,
        filepath: Option<String>,
    ) -> Result<(), DataInterfaceError> {
        self.sql_logic.add_sql_logic(name, query, filepath)?;

        Ok(())
    }

    pub fn split_data(&mut self, py: Python) -> Result<HashMap<String, Data>, DataInterfaceError> {
        // check if data is None
        if self.data.is_none() {
            return Err(DataInterfaceError::MissingDataError);
        }

        if self.data_splits.is_empty() {
            return Err(DataInterfaceError::MissingDataSplitsError);
        }

        let dependent_vars = self.dependent_vars.clone();

        self.data_splits.split_data(
            self.data.as_ref().unwrap().bind(py),
            &self.data_type,
            &dependent_vars,
        )
    }

    #[pyo3(signature = (bin_size=20, compute_correlations=false))]
    pub fn create_data_profile(
        &mut self,
        py: Python,
        bin_size: usize,
        compute_correlations: bool,
    ) -> Result<DataProfile, DataInterfaceError> {
        let mut profiler = DataProfiler::new();

        // get ScouterDataType from opsml DataType

        let data_type = match self.data_type {
            DataType::Numpy => Some(&scouter_client::DataType::Numpy),
            DataType::Pandas => Some(&scouter_client::DataType::Pandas),
            DataType::Polars => Some(&scouter_client::DataType::Polars),
            DataType::Arrow => Some(&scouter_client::DataType::Arrow),
            _ => Err(DataInterfaceError::DataTypeNotSupportedForProfilingError)?,
        };

        debug!("Creating data profile with data type: {:?}", data_type);

        let profile = profiler.create_data_profile(
            py,
            self.data.as_ref().unwrap().bind(py),
            data_type,
            Some(bin_size),
            Some(compute_correlations),
        )?;

        self.data_profile = Some(profile.clone());

        Ok(profile)
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Some(ref data) = self.data {
            visit.call(data)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.data = None;
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
    pub fn save_sql(&self, path: PathBuf) -> Result<Option<PathBuf>, DataInterfaceError> {
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
    /// * `Result<FeatureMap>` - FeatureMap
    pub fn create_schema(&mut self, py: Python) -> Result<FeatureSchema, DataInterfaceError> {
        // Create and insert the feature
        let feature_map =
            generate_feature_schema(self.data.as_ref().unwrap().bind(py), &self.data_type)?;

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
    /// * `Result<PathBuf>` - Path to the saved data
    ///
    pub fn save_data(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PathBuf, DataInterfaceError> {
        // check if data is None
        if self.data.is_none() {
            return Err(DataInterfaceError::MissingDataError);
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
    /// * `Result<PathBuf>` - Path to saved drift profile
    #[instrument(skip_all)]
    pub fn save_data_profile(&self, path: &Path) -> Result<PathBuf, DataInterfaceError> {
        let profile_path = PathBuf::from(SaveName::DataProfile).with_extension(Suffix::Json);
        let profile_save_path = path.join(profile_path.clone());
        self.data_profile
            .as_ref()
            .unwrap()
            .save_to_json(Some(profile_save_path.clone()))
            .map_err(DataInterfaceError::ScouterSaveError)?;

        Ok(profile_path)
    }
}
