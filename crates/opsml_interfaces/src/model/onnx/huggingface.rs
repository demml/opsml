use crate::model::onnx::OnnxSession;
use opsml_error::OpsmlError;
use opsml_types::SaveName;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::fs;
use std::path::Path;
use std::path::PathBuf;
use tracing::debug;

pub type HuggingFaceKwargs<'py> = (String, Option<Bound<'py, PyDict>>, bool, Bound<'py, PyDict>);

pub struct HuggingFaceOnnxModelConverter {
    pub model_path: PathBuf,
    pub onnx_path: PathBuf,
    pub quantize_path: PathBuf,
}

impl HuggingFaceOnnxModelConverter {
    pub fn new(path: &Path) -> Self {
        let model_save_path = path.join(SaveName::Model);

        let onnx_save_path = PathBuf::from(SaveName::OnnxModel);
        let full_onnx_save_path = path.join(&onnx_save_path);

        let quantize_save_path = PathBuf::from(SaveName::QuantizedModel);
        let full_quantize_save_path = path.join(&quantize_save_path);

        HuggingFaceOnnxModelConverter {
            model_path: model_save_path,
            onnx_path: full_onnx_save_path,
            quantize_path: full_quantize_save_path,
        }
    }

    fn get_onnx_session(&self, py: Python, ort_type: &str) -> PyResult<OnnxSession> {
        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

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

        OnnxSession::new(py, onnx_version, onnx_bytes, ort_type.to_string(), None)
            .map_err(|e| OpsmlError::new_err(format!("Failed to create ONNX session: {}", e)))
    }

    pub fn parse_kwargs<'py>(
        py: Python<'py>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<HuggingFaceKwargs<'py>> {
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

        let quantize_kwargs = PyDict::new(py);
        let config = kwargs.get_item("config")?;
        quantize_kwargs.set_item("quantization_config", config)?;

        let onnx_kwargs = kwargs
            .get_item("extra_kwargs")?
            .map(|x| x.downcast::<PyDict>().unwrap().clone());

        Ok((ort_type, onnx_kwargs, quantize, quantize_kwargs))
    }

    fn quantize_model<'py>(
        &self,
        ort_module: &Bound<'py, PyModule>,
        onnx_model: &Bound<'py, PyAny>,
        quantize_kwargs: Bound<'py, PyDict>,
    ) -> PyResult<()> {
        let quantizer = ort_module.getattr("ORTQuantizer")?;

        debug!("Loading model for quantization");
        let quantizer = quantizer.call_method1("from_pretrained", (onnx_model,))?;
        quantize_kwargs.set_item("save_dir", &self.quantize_path)?;

        debug!("Quantizing model");
        quantizer.call_method("quantize", (), Some(&quantize_kwargs))?;

        Ok(())
    }

    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<OnnxSession> {
        debug!("Step 1: Converting HuggingFace model to ONNX");

        let kwargs = Self::parse_kwargs(py, kwargs)?;

        let opt_rt = py.import("optimum.onnxruntime")?;

        // set export to true to convert model to onnx
        let ort_model = opt_rt
            .getattr(&kwargs.0)?
            .call_method(
                "from_pretrained",
                (&self.model_path, true),
                kwargs.1.as_ref(),
            )
            .map_err(|e| {
                OpsmlError::new_err(format!("Failed to load model for onnx conversion: {}", e))
            })?;

        // saves to model.onnx
        ort_model
            .call_method("save_pretrained", (&self.onnx_path,), kwargs.1.as_ref())
            .map_err(|e| OpsmlError::new_err(format!("Failed to save ONNX model: {}", e)))?;

        debug!("Step 2: Extracting ONNX schema");
        let mut onnx_session = self.get_onnx_session(py, &kwargs.0)?;

        if kwargs.2 {
            debug!("Step 3: Quantizing ONNX model");
            self.quantize_model(&opt_rt, &ort_model, kwargs.3)?;
            onnx_session.quantized = true;
        }

        debug!("ONNX model conversion complete");

        Ok(onnx_session)
    }
}
