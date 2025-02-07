pub use opsml_storage::PyFileSystemStorage;
pub use opsml_types::contracts::FileInfo;
pub use opsml_types::StorageType;
use pyo3::prelude::*;

#[pymodule]
pub fn storage(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyFileSystemStorage>()?;
    m.add_class::<FileInfo>()?;
    m.add_class::<StorageType>()?;

    Ok(())
}
