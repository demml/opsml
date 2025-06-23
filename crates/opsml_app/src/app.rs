use crate::error::AppError;
use opsml_cards::CardDeck;
use opsml_state::app_state;
use opsml_types::{cards::CardDeckMapping, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use scouter_client::ScouterQueue;
use std::path::{Path, PathBuf};
use tracing::{debug, error};

/// Load a card map from path
fn load_card_map(path: &Path) -> Result<CardDeckMapping, AppError> {
    let card_mapping_path = path.join(SaveName::CardMap).with_extension(Suffix::Json);
    debug!("Loading card mapping from: {:?}", card_mapping_path);
    let mapping = CardDeckMapping::from_path(&card_mapping_path)?;
    Ok(mapping)
}

#[pyclass]
#[derive(Debug)]
pub struct AppState {
    deck: Py<CardDeck>,
    queue: Option<Py<ScouterQueue>>,
}

#[pymethods]
impl AppState {
    /// Instantiate a new application state. Typically from_path is used; however, an new/init
    /// method is provided for consistency with other classes
    /// # Arguments
    /// * `deck` - The CardDeck to use for the application state
    /// * `queue` - An optional ScouterQueue to use for the application state. If not provided,
    /// no queue will be created.
    ///
    /// # Returns
    /// * `AppState` - The application state containing the CardDeck and optional ScouterQueue  
    #[new]
    #[pyo3(signature = (deck, queue=None))]
    pub fn new(
        deck: Bound<'_, CardDeck>,
        queue: Option<Bound<'_, ScouterQueue>>,
    ) -> Result<Self, AppError> {
        let deck = deck.unbind();
        let queue = queue.map(|q| q.unbind());
        Ok(AppState { deck, queue })
    }
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
        let card_map = load_card_map(&path).map_err(|e| {
            error!("Failed to load card map from: {:?}", e);
            e
        })?;

        let queue = if !card_map.drift_paths.is_empty() {
            debug!("Drift paths found in card map, creating ScouterQueue");
            match transport_config {
                Some(config) => {
                    let rt = app_state().runtime.clone();
                    let scouter_queue =
                        ScouterQueue::from_path_rs(py, card_map.drift_paths, config, rt)?;
                    Some(Py::new(py, scouter_queue)?)
                }
                None => {
                    debug!("No transport config found in card map");
                    None
                }
            }
        } else {
            debug!("No drift paths or transport config found in card map");
            None
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
