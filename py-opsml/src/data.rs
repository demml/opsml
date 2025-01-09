use opsml_interfaces::data::{
    generate_feature_schema, ArrowData, ColType, ColValType, ColumnSplit, Data, DataInterface,
    DataInterfaceSaveMetadata, DataSplit, DataSplits, DataSplitter, DependentVars, IndiceSplit,
    Inequality, NumpyData, PandasData, PolarsData, SqlData, SqlLogic, StartStopSplit, TorchData,
};

use pyo3::prelude::*;

#[pymodule]
pub fn data(m: &Bound<'_, PyModule>) -> PyResult<()> {
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

    Ok(())
}
