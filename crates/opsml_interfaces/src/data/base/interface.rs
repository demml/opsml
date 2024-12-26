use pyo3::prelude::*;

#[pyclass(subclass)]
struct DataInterface {
    data: PyObject,
}
