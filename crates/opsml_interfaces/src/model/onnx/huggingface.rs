use crate::model::base::utils::OnnxExtension;
use crate::model::onnx::OnnxSession;
use crate::types::ModelType;
use opsml_error::OpsmlError;
use opsml_types::SaveName;
use pyo3::prelude::*;
use pyo3::types::PyBool;
use pyo3::types::PyDict;
use std::fs;
use std::path::Path;
use std::path::PathBuf;
use tempfile::tempdir;
use tracing::debug;

pub struct HuggingFaceOnnxModelConverter {
    pub model_path: PathBuf,
    pub onnx_path: PathBuf,
    pub quantize_path: PathBuf,
}

impl HuggingFaceOnnxModelConverter {
    pub fn new(path: &Path) -> Self {
        let model_save_path = path.join(SaveName::Model);
        let full_model_save_path = path.join(&model_save_path);

        let onnx_save_path = PathBuf::from(SaveName::OnnxModel);
        let full_onnx_save_path = path.join(&onnx_save_path);

        let quantize_save_path = PathBuf::from(SaveName::QuantizedModel);
        let full_quantize_save_path = path.join(&quantize_save_path);

        HuggingFaceOnnxModelConverter {
            model_path: full_model_save_path,
            onnx_path: full_onnx_save_path,
            quantize_path: full_quantize_save_path,
        }
    }

    fn get_onnx_session(&self, py: Python, ort_model: &Bound<'_, PyAny>) -> PyResult<OnnxSession> {
        //get path to file ending with .onnx
        let onnx_file = fs::read_dir(&self.onnx_path)?
            .filter_map(|entry| {
                entry.ok().and_then(|e| {
                    let path = e.path();
                    if path.is_file() && path.extension().unwrap() == "onnx" {
                        Some(path)
                    } else {
                        None
                    }
                })
            })
            .next()
            .ok_or_else(|| OpsmlError::new_err("No ONNX file found"))?;

        // load model_path to onnx_bytes
        let onnx_bytes = fs::read(&onnx_file)
            .map_err(|e| OpsmlError::new_err(format!("Failed to read ONNX model: {}", e)))?;

        OnnxSession::new_from_hf_session(py, ort_model, onnx_bytes)
            .map_err(|e| OpsmlError::new_err(format!("Failed to create ONNX session: {}", e)))
    }

    pub fn parse_kwargs<'py>(
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<(String, bool, Bound<'py, PyDict>)> {
        let kwargs = kwargs.ok_or_else(|| OpsmlError::new_err("ONNX kwargs are required"))?;

        let ort_type = kwargs
            .get_item("ort_type")
            .map_err(|e| OpsmlError::new_err(format!("Failed to get ort_type: {}", e)))?
            .unwrap()
            .to_string();

        let quantize = kwargs
            .get_item("quantize")
            .map_err(|e| OpsmlError::new_err(format!("Failed to get quantize: {}", e)))?
            .unwrap()
            .extract::<bool>()
            .unwrap();

        // delete ort_type from kwargs
        kwargs
            .del_item("ort_type")
            .map_err(|e| OpsmlError::new_err(format!("Failed to delete ort_type: {}", e)))?;

        //delete quantize from kwargs
        kwargs
            .del_item("quantize")
            .map_err(|e| OpsmlError::new_err(format!("Failed to delete quantize: {}", e)))?;

        Ok((ort_type, quantize, kwargs.clone()))
    }

    fn quantize_model<'py>(
        &self,
        py: Python<'py>,
        ort_module: &Bound<'py, PyModule>,
        onnx_model: &Bound<'py, PyAny>,
        kwargs: Bound<'py, PyDict>,
    ) -> PyResult<()> {
        let quantizer = ort_module.getattr("ORTQuantizer")?;

        let quantizer = quantizer.call_method1("from_pretrained", (onnx_model,))?;

        let quantize_kwargs = PyDict::new(py);
        let config = kwargs.get_item("config")?;

        quantize_kwargs.set_item("quantization_config", config)?;
        quantizer.call_method("quantize", (&self.quantize_path,), Some(&quantize_kwargs))?;

        Ok(())
    }

    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<OnnxSession> {
        debug!("Step 1: Converting HuggingFace model to ONNX");

        let (ort_type, quantize, kwargs) = Self::parse_kwargs(kwargs)?;

        let opt_rt = py.import("optimum.onnxruntime")?;

        // set export to true to convert model to onnx
        let ort_model = opt_rt
            .getattr(&ort_type)?
            .call_method("from_pretrained", (&self.model_path, true), Some(&kwargs))
            .map_err(|e| {
                OpsmlError::new_err(format!("Failed to load model for onnx conversion: {}", e))
            })?;

        // saves to model.onnx
        ort_model.call_method("save_pretrained", (&self.onnx_path,), Some(&kwargs))?;
        debug!("Step 2: Extracting ONNX schema");
        let mut onnx_session = self.get_onnx_session(py, &ort_model)?;

        if quantize {
            debug!("Quantizing ONNX model");
            self.quantize_model(py, &opt_rt, &ort_model, kwargs)?;
            onnx_session.quantized = true;
        }

        debug!("ONNX model conversion complete");

        Ok(onnx_session)
    }
}
