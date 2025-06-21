use crate::error::AppError;
use opsml_cards::CardDeck;
use opsml_state::app_state;
use opsml_types::{cards::CardDeckMapping, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use scouter_client::ScouterQueue;
use std::path::{Path, PathBuf};
/// Load a card map from path
fn load_card_map(path: &Path) -> Result<CardDeckMapping, AppError> {
    let card_mapping_path = path.join(SaveName::CardMap).with_extension(Suffix::Json);
    let mapping = CardDeckMapping::from_path(&card_mapping_path)?;
    Ok(mapping)
}

#[pyclass]
#[derive(Debug)]
struct AppState {
    deck: Py<CardDeck>,
    queue: Option<Py<ScouterQueue>>,
}

#[pymethods]
impl AppState {
    /// This method will load an application state from a path
    /// This is primarily used for loading an application during api start where a user
    /// may wish to load an Opsml CardDeck along with the appropriate ScouterQueue for monitoring
    /// This class and it's functionality may expand in the future
    ///
    /// # Arguments
    /// * `py` - Python interpreter state
    /// * `path` - The root path to the application directory containing files
    /// * `load_kwargs` - Load kwargs to pass to the CardDeck loader
    /// * `transport_config` = The transport config to use with the ScouterQueue. If not provided,
    /// no queue will be created.
    #[staticmethod]
    #[pyo3(signature = (path=None, load_kwargs=None, transport_config=None))]
    pub fn from_path(
        py: Python,
        path: Option<PathBuf>,
        load_kwargs: Option<&Bound<'_, PyDict>>,
        transport_config: Option<&Bound<'_, PyAny>>,
    ) -> Result<Self, AppError> {
        let path = path.unwrap_or_else(|| PathBuf::from(SaveName::CardDeck));
        let deck = Py::new(py, CardDeck::from_path_rs(py, &path, load_kwargs)?)?;
        let card_map_path = path.join(SaveName::CardMap).with_extension(Suffix::Json);
        let card_map = load_card_map(&card_map_path)?;

        let queue = match transport_config {
            Some(config) => {
                // get the opsml state shared runtime
                let rt = app_state().runtime.clone();

                Some(Py::new(
                    py,
                    ScouterQueue::from_path_rs(py, card_map.drift_paths, config, rt)?,
                )?)
            }
            None => None,
        };

        Ok(AppState { deck, queue })
    }

    #[getter]
    pub fn deck<'py>(&self, py: Python<'py>) -> Result<&Bound<'py, CardDeck>, AppError> {
        Ok(self.deck.bind(py))
    }

    #[getter]
    pub fn queue<'py>(&self, py: Python<'py>) -> Result<&Bound<'py, ScouterQueue>, AppError> {
        if let Some(queue) = &self.queue {
            Ok(queue.bind(py))
        } else {
            Err(AppError::QueueNotFoundError)
        }
    }
}
