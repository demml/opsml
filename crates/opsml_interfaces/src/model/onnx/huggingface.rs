use crate::error::OnnxError;
use crate::model::onnx::OnnxSession;

use opsml_types::SaveName;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::fs;
use std::path::Path;
use std::path::PathBuf;
use tracing::{debug, instrument};

pub type HuggingFaceKwargs<'py> = (String, Bound<'py, PyDict>, bool, Bound<'py, PyDict>);

pub struct HuggingFaceOnnxConverter {
    pub model_path: PathBuf,
    pub onnx_path: PathBuf,
    pub quantize_path: PathBuf,
}

impl HuggingFaceOnnxConverter {
    pub fn new(path: &Path) -> Self {
        let model_save_path = path.join(SaveName::Model);

        let onnx_save_path = PathBuf::from(SaveName::OnnxModel);
        let full_onnx_save_path = path.join(&onnx_save_path);

        let quantize_save_path = PathBuf::from(SaveName::QuantizedModel);
        let full_quantize_save_path = path.join(&quantize_save_path);

        HuggingFaceOnnxConverter {
            model_path: model_save_path,
            onnx_path: full_onnx_save_path,
            quantize_path: full_quantize_save_path,
        }
    }

    fn get_onnx_session(&self, py: Python) -> Result<OnnxSession, OnnxError> {
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
            .ok_or_else(|| OnnxError::NoOnnxFile)?;

        // load model_path to onnx_bytes
        OnnxSession::from_file(py, &onnx_file, None)
    }

    pub fn parse_kwargs<'py>(
        py: Python<'py>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<HuggingFaceKwargs<'py>> {
        let kwargs = kwargs.ok_or_else(|| OnnxError::MissingOnnxKwargs)?;

        let ort_type = kwargs
            .get_item("ort_type")
            .map_err(OnnxError::MissingOrtType)?
            .unwrap()
            .to_string();

        let quantize = kwargs
            .get_item("quantize")
            .map_err(OnnxError::QuantizeArgError)?
            .unwrap()
            .extract::<bool>()
            .unwrap();

        let quantize_kwargs = PyDict::new(py);
        let config = kwargs.get_item("config")?;
        quantize_kwargs.set_item("quantization_config", config)?;

        // get onnx_kwargs or create an empty dict
        let onnx_kwargs = kwargs
            .get_item("extra_kwargs")?
            .map(|x| x.downcast::<PyDict>().unwrap().clone())
            .unwrap_or_else(|| PyDict::new(py));

        // add export=True to onnx_kwargs
        onnx_kwargs.set_item("export", true)?;

        Ok((ort_type, onnx_kwargs, quantize, quantize_kwargs))
    }

    fn quantize_model<'py>(
        &self,
        ort_module: &Bound<'py, PyModule>,
        onnx_model: &Bound<'py, PyAny>,
        quantize_kwargs: Bound<'py, PyDict>,
    ) -> Result<(), OnnxError> {
        let quantizer = ort_module.getattr("ORTQuantizer")?;

        debug!("Loading model for quantization");
        let quantizer = quantizer.call_method1("from_pretrained", (onnx_model,))?;
        quantize_kwargs.set_item("save_dir", &self.quantize_path)?;

        debug!("Quantizing model");
        quantizer.call_method("quantize", (), Some(&quantize_kwargs))?;

        Ok(())
    }

    #[instrument(skip_all)]
    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<OnnxSession, OnnxError> {
        debug!("Step 1: Converting HuggingFace model to ONNX");

        let kwargs = Self::parse_kwargs(py, kwargs)?;

        let opt_rt = py.import("optimum.onnxruntime")?;

        // set export to true to convert model to onnx
        let ort_model = opt_rt
            .getattr(&kwargs.0)?
            .call_method("from_pretrained", (&self.model_path,), Some(&kwargs.1))
            .map_err(OnnxError::LoadModelError)?;

        // saves to model.onnx
        ort_model
            .call_method("save_pretrained", (&self.onnx_path,), Some(&kwargs.1))
            .map_err(OnnxError::PyOnnxConversionError)?;

        debug!("Step 2: Extracting ONNX schema");
        let mut onnx_session = self.get_onnx_session(py)?;

        if kwargs.2 {
            debug!("Step 3: Quantizing ONNX model");
            self.quantize_model(&opt_rt, &ort_model, kwargs.3)?;
            onnx_session.quantized = true;
        }

        debug!("ONNX model conversion complete");

        Ok(onnx_session)
    }
}
