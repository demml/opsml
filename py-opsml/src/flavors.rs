use opsml_cards::ModelCard;
use opsml_experiment::active;
use opsml_interfaces::{
    CatBoostModel, HuggingFaceModel, HuggingFaceTask, LightGBMModel, LightningModel, OnnxModel,
    SklearnModel, TensorFlowModel, TorchModel, XGBoostModel,
};
use opsml_semver::VersionType;
use opsml_types::TaskType;
use pyo3::prelude::*;

fn resolve_space(py: Python<'_>, explicit: Option<String>) -> PyResult<String> {
    if let Some(space) = explicit {
        return Ok(space);
    }

    let exp = active::current(py)?;
    let exp_ref = exp.borrow(py);
    exp_ref
        .experiment
        .bind(py)
        .getattr("space")?
        .extract::<String>()
}

fn register_built_interface<'py>(
    py: Python<'py>,
    interface: Bound<'py, PyAny>,
    space: String,
    name: String,
    save_kwargs: Option<&Bound<'py, PyAny>>,
) -> PyResult<Py<ModelCard>> {
    let card = ModelCard::new(
        py,
        &interface,
        Some(&space),
        Some(&name),
        None,
        None,
        None,
        None,
        None,
    )?;
    let card_py = Py::new(py, card)?;
    let card_bound = card_py.bind(py).clone().into_any();

    let exp = active::current(py)?;
    exp.borrow_mut(py)
        .register_card(&card_bound, VersionType::Minor, None, None, save_kwargs)?;

    Ok(card_py)
}

macro_rules! impl_simple_log_model {
    ($fn_name:ident, $iface_ty:ty) => {
        #[pyfunction]
        #[pyo3(signature = (
                                    model, *, name, space=None, sample_data=None, preprocessor=None,
                                    task_type=None, drift_profile=None, save_kwargs=None
                                ))]
        #[allow(clippy::too_many_arguments)]
        pub fn $fn_name<'py>(
            py: Python<'py>,
            model: Bound<'py, PyAny>,
            name: String,
            space: Option<String>,
            sample_data: Option<Bound<'py, PyAny>>,
            preprocessor: Option<Bound<'py, PyAny>>,
            task_type: Option<TaskType>,
            drift_profile: Option<Bound<'py, PyAny>>,
            save_kwargs: Option<Bound<'py, PyAny>>,
        ) -> PyResult<Py<ModelCard>> {
            let space = resolve_space(py, space)?;
            let (sub, base) = <$iface_ty>::new(
                py,
                Some(&model),
                preprocessor.as_ref(),
                sample_data.as_ref(),
                task_type,
                drift_profile.as_ref(),
            )?;

            let init = pyo3::PyClassInitializer::from(base).add_subclass(sub);
            let iface_py: Py<$iface_ty> = Py::new(py, init)?;
            let iface_bound = iface_py.bind(py).clone().into_any();
            register_built_interface(py, iface_bound, space, name, save_kwargs.as_ref())
        }
    };
}

impl_simple_log_model!(sklearn_log_model, SklearnModel);
impl_simple_log_model!(xgboost_log_model, XGBoostModel);
impl_simple_log_model!(lightgbm_log_model, LightGBMModel);
impl_simple_log_model!(catboost_log_model, CatBoostModel);
impl_simple_log_model!(torch_log_model, TorchModel);
impl_simple_log_model!(tensorflow_log_model, TensorFlowModel);

#[pyfunction]
#[pyo3(signature = (
    trainer, *, name, space=None, sample_data=None, preprocessor=None,
    task_type=None, drift_profile=None, save_kwargs=None
))]
#[allow(clippy::too_many_arguments)]
pub fn lightning_log_model<'py>(
    py: Python<'py>,
    trainer: Bound<'py, PyAny>,
    name: String,
    space: Option<String>,
    sample_data: Option<Bound<'py, PyAny>>,
    preprocessor: Option<Bound<'py, PyAny>>,
    task_type: Option<TaskType>,
    drift_profile: Option<Bound<'py, PyAny>>,
    save_kwargs: Option<Bound<'py, PyAny>>,
) -> PyResult<Py<ModelCard>> {
    let space = resolve_space(py, space)?;
    let (sub, base) = LightningModel::new(
        py,
        Some(&trainer),
        preprocessor.as_ref(),
        sample_data.as_ref(),
        task_type,
        drift_profile.as_ref(),
    )?;
    let init = pyo3::PyClassInitializer::from(base).add_subclass(sub);
    let iface_py: Py<LightningModel> = Py::new(py, init)?;
    register_built_interface(
        py,
        iface_py.bind(py).clone().into_any(),
        space,
        name,
        save_kwargs.as_ref(),
    )
}

#[pyfunction]
#[pyo3(signature = (
    model, *, name, space=None, sample_data=None,
    tokenizer=None, feature_extractor=None, image_processor=None,
    hf_task=None, task_type=None, drift_profile=None, save_kwargs=None
))]
#[allow(clippy::too_many_arguments)]
pub fn huggingface_log_model<'py>(
    py: Python<'py>,
    model: Bound<'py, PyAny>,
    name: String,
    space: Option<String>,
    sample_data: Option<Bound<'py, PyAny>>,
    tokenizer: Option<Bound<'py, PyAny>>,
    feature_extractor: Option<Bound<'py, PyAny>>,
    image_processor: Option<Bound<'py, PyAny>>,
    hf_task: Option<HuggingFaceTask>,
    task_type: Option<TaskType>,
    drift_profile: Option<Bound<'py, PyAny>>,
    save_kwargs: Option<Bound<'py, PyAny>>,
) -> PyResult<Py<ModelCard>> {
    let space = resolve_space(py, space)?;
    let (sub, base) = HuggingFaceModel::new(
        py,
        Some(&model),
        tokenizer.as_ref(),
        feature_extractor.as_ref(),
        image_processor.as_ref(),
        sample_data.as_ref(),
        hf_task,
        task_type,
        drift_profile.as_ref(),
    )?;
    let init = pyo3::PyClassInitializer::from(base).add_subclass(sub);
    let iface_py: Py<HuggingFaceModel> = Py::new(py, init)?;
    register_built_interface(
        py,
        iface_py.bind(py).clone().into_any(),
        space,
        name,
        save_kwargs.as_ref(),
    )
}

#[pyfunction]
#[pyo3(signature = (
    model, *, name, space=None, sample_data=None,
    task_type=None, drift_profile=None, save_kwargs=None
))]
#[allow(clippy::too_many_arguments)]
pub fn onnx_log_model<'py>(
    py: Python<'py>,
    model: Bound<'py, PyAny>,
    name: String,
    space: Option<String>,
    sample_data: Option<Bound<'py, PyAny>>,
    task_type: Option<TaskType>,
    drift_profile: Option<Bound<'py, PyAny>>,
    save_kwargs: Option<Bound<'py, PyAny>>,
) -> PyResult<Py<ModelCard>> {
    let space = resolve_space(py, space)?;
    let (sub, base) = OnnxModel::new(
        py,
        Some(&model),
        sample_data.as_ref(),
        task_type,
        drift_profile.as_ref(),
    )?;
    let init = pyo3::PyClassInitializer::from(base).add_subclass(sub);
    let iface_py: Py<OnnxModel> = Py::new(py, init)?;
    register_built_interface(
        py,
        iface_py.bind(py).clone().into_any(),
        space,
        name,
        save_kwargs.as_ref(),
    )
}
