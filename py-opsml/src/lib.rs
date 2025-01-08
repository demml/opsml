use opsml_cards::{CardInfo, DataCard, DataCardMetadata, DataSchema, Description, OnnxSchema};
use opsml_contracts::{Card, CardList};
use opsml_error::error::OpsmlError;
use opsml_interfaces::{
    data::{
        generate_feature_schema, ArrowData, ColType, ColValType, ColumnSplit, Data, DataInterface,
        DataInterfaceSaveMetadata, DataSplit, DataSplits, DataSplitter, DependentVars, IndiceSplit,
        Inequality, NumpyData, PandasData, PolarsData, SqlData, SqlLogic, StartStopSplit,
        TorchData,
    },
    CatBoostModelInterfaceMetadata, Feature, FeatureMap, HuggingFaceModelInterfaceMetadata,
    HuggingFaceORTModel, HuggingFaceOnnxArgs, HuggingFaceOnnxSaveArgs,
    LightGBMModelInterfaceMetadata, LightningInterfaceMetadata, ModelDataInterfaceSaveMetadata,
    ModelInterfaceMetadata, ModelInterfaceType, ModelSaveMetadata, SklearnModelInterfaceMetadata,
    TensorFlowInterfaceMetadata, TorchInterfaceMetadata, TorchOnnxArgs, TorchSaveArgs,
    VowpalWabbitInterfaceMetadata, XGBoostModelInterfaceMetadata,
};
use opsml_logging::logging::{LogLevel, OpsmlLogger};
use opsml_registry::PyCardRegistry;
#[cfg(feature = "server")]
use opsml_registry::RegistryTestHelper;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;
use scouter_client::*;

use opsml_types::{
    CommonKwargs, DataType, InterfaceType, RegistryType, SaveName, SaverPath, Suffix,
};
use opsml_utils::FileUtils;
use pyo3::prelude::*;

#[pymodule]
fn _opsml(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_logging
    m.add_class::<LogLevel>()?;
    m.add_class::<OpsmlLogger>()?;

    // opsml_errors
    m.add("OpsmlError", m.py().get_type::<OpsmlError>())?;

    // opsml_settings
    m.add_class::<OpsmlConfig>()?;

    // opsml_types
    m.add_class::<CommonKwargs>()?;
    m.add_class::<SaveName>()?;
    m.add_class::<Suffix>()?;
    m.add_class::<RegistryType>()?;
    m.add_class::<DataType>()?;
    m.add_class::<InterfaceType>()?;
    m.add_class::<SaverPath>()?;

    // opsml_semver
    m.add_class::<VersionType>()?;

    // opsml_utils
    m.add_class::<FileUtils>()?;

    // opsml_interfaces
    m.add_class::<HuggingFaceOnnxArgs>()?;
    m.add_class::<HuggingFaceORTModel>()?;
    m.add_class::<HuggingFaceOnnxSaveArgs>()?;
    m.add_class::<TorchOnnxArgs>()?;
    m.add_class::<TorchSaveArgs>()?;
    m.add_class::<Feature>()?;
    m.add_class::<FeatureMap>()?;
    m.add_class::<Description>()?;
    m.add_class::<DataSchema>()?;
    m.add_class::<OnnxSchema>()?;
    m.add_class::<CardInfo>()?;
    m.add_class::<Card>()?;
    m.add_class::<CardList>()?;
    m.add_class::<DataCard>()?;
    m.add_class::<DataCardMetadata>()?;

    // Model Interface
    m.add_class::<ModelDataInterfaceSaveMetadata>()?;
    m.add_class::<ModelInterfaceMetadata>()?;

    // Model Interface args
    m.add_class::<CatBoostModelInterfaceMetadata>()?;
    m.add_class::<HuggingFaceModelInterfaceMetadata>()?;
    m.add_class::<LightGBMModelInterfaceMetadata>()?;
    m.add_class::<LightningInterfaceMetadata>()?;
    m.add_class::<SklearnModelInterfaceMetadata>()?;
    m.add_class::<TensorFlowInterfaceMetadata>()?;
    m.add_class::<TorchInterfaceMetadata>()?;
    m.add_class::<VowpalWabbitInterfaceMetadata>()?;
    m.add_class::<XGBoostModelInterfaceMetadata>()?;
    m.add_class::<ModelSaveMetadata>()?;
    m.add_class::<ModelDataInterfaceSaveMetadata>()?;
    m.add_class::<ModelInterfaceType>()?;

    // data_splitter
    m.add_class::<DataSplit>()?;
    m.add_class::<Data>()?;
    m.add_class::<ColumnSplit>()?;
    m.add_class::<StartStopSplit>()?;
    m.add_class::<IndiceSplit>()?;
    m.add_class::<ColType>()?;
    m.add_class::<ColValType>()?;
    m.add_class::<DataSplitter>()?;
    m.add_class::<Inequality>()?;
    m.add_class::<DependentVars>()?;
    m.add_class::<SqlLogic>()?;
    m.add_class::<DataSplits>()?;

    // data_interface
    m.add_class::<DataInterface>()?;
    m.add_class::<NumpyData>()?;
    m.add_class::<PolarsData>()?;
    m.add_class::<PandasData>()?;
    m.add_class::<ArrowData>()?;
    m.add_class::<DataInterfaceSaveMetadata>()?;
    m.add_class::<SqlData>()?;
    m.add_class::<TorchData>()?;
    m.add_function(wrap_pyfunction!(generate_feature_schema, m)?)?;

    // opsml_registry
    m.add_class::<PyCardRegistry>()?;

    #[cfg(feature = "server")]
    m.add_class::<RegistryTestHelper>()?;

    // scouter_client (we need to re-export types, so that we don't need to install scouter on the python side)
    // opsml_errors
    m.add("ScouterError", m.py().get_type::<PyScouterError>())?;
    m.add_class::<SpcDrifter>()?;
    m.add_class::<SpcDriftProfile>()?;
    m.add_class::<SpcFeatureDriftProfile>()?;
    m.add_class::<DataProfile>()?;
    m.add_class::<FeatureProfile>()?;
    m.add_class::<Distinct>()?;
    m.add_class::<Histogram>()?;
    m.add_class::<SpcDriftMap>()?;
    m.add_class::<SpcFeatureDrift>()?;
    m.add_class::<SpcDriftConfig>()?;
    m.add_class::<SpcAlertType>()?;
    m.add_class::<AlertZone>()?;
    m.add_class::<SpcAlert>()?;
    m.add_class::<PsiDriftConfig>()?;
    m.add_class::<SpcFeatureAlerts>()?;
    m.add_class::<SpcFeatureAlert>()?;
    m.add_class::<SpcAlertRule>()?;
    m.add_class::<Every1Minute>()?;
    m.add_class::<Every5Minutes>()?;
    m.add_class::<Every15Minutes>()?;
    m.add_class::<Every30Minutes>()?;
    m.add_class::<EveryHour>()?;
    m.add_class::<Every6Hours>()?;
    m.add_class::<Every12Hours>()?;
    m.add_class::<EveryDay>()?;
    m.add_class::<EveryWeek>()?;
    m.add_class::<CommonCron>()?;
    m.add_class::<SpcAlertConfig>()?;
    m.add_class::<AlertDispatchType>()?;
    m.add_class::<FeatureMap>()?;
    m.add_class::<SpcFeatureQueue>()?;
    m.add_class::<PsiFeatureQueue>()?;
    m.add_class::<DriftType>()?;
    m.add_class::<RecordType>()?;
    m.add_class::<ServerRecords>()?;
    m.add_class::<SpcServerRecord>()?;
    m.add_class::<PsiServerRecord>()?;
    m.add_class::<ServerRecord>()?;
    m.add_class::<Observer>()?;
    m.add_class::<RouteMetrics>()?;
    m.add_class::<LatencyMetrics>()?;
    m.add_class::<ObservabilityMetrics>()?;
    m.add_class::<PsiAlertConfig>()?;
    m.add_class::<Bin>()?;
    m.add_class::<PsiFeatureDriftProfile>()?;
    m.add_class::<PsiDriftProfile>()?;
    m.add_class::<PsiDriftMap>()?;
    m.add_class::<PsiDrifter>()?;
    m.add_class::<CustomMetricAlertCondition>()?;
    m.add_class::<CustomMetricAlertConfig>()?;
    m.add_class::<CustomMetricDriftConfig>()?;
    m.add_class::<CustomMetric>()?;
    m.add_class::<AlertThreshold>()?;
    m.add_class::<CustomDriftProfile>()?;
    m.add_class::<CustomDrifter>()?;
    m.add_class::<CustomMetricServerRecord>()?;
    m.add_class::<Feature>()?;
    m.add_class::<Features>()?;
    m.add_class::<DataProfiler>()?;

    Ok(())
}
