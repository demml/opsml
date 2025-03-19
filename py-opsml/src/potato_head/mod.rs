use ::potato_head::{
    AudioUrl, BinaryContent, DocumentUrl, ImageUrl, PIIConfig, Prompt, RiskLevel,
    SanitizationConfig,
};

use pyo3::prelude::*;

#[pymodule]
pub fn potato_head(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Prompt>()?;
    m.add_class::<ImageUrl>()?;
    m.add_class::<AudioUrl>()?;
    m.add_class::<DocumentUrl>()?;
    m.add_class::<BinaryContent>()?;
    m.add_class::<PIIConfig>()?;
    m.add_class::<RiskLevel>()?;
    m.add_class::<SanitizationConfig>()?;
    Ok(())
}
