use crate::{DataCard, ModelCard};

use opsml_crypt::encrypt_file;
use opsml_error::error::CardError;
use opsml_interfaces::SaveKwargs;
use opsml_types::{contracts::Card, CommonKwargs, RegistryType};
use pyo3::prelude::*;
use std::path::PathBuf;
use tempfile::TempDir;
use tracing::{debug, error, instrument};

#[derive(Debug)]
pub enum CardEnum {
    Data(DataCard),
    Model(ModelCard),
}

impl CardEnum {
    pub fn from_py(card: &Bound<'_, PyAny>) -> Result<Self, CardError> {
        if card.is_instance_of::<ModelCard>() {
            let result: ModelCard = card.extract().unwrap();
            Ok(CardEnum::Model(result))
        } else if card.is_instance_of::<DataCard>() {
            let result: DataCard = card.extract().unwrap();
            Ok(CardEnum::Data(result))
        } else {
            Err(CardError::Error("Invalid card type".to_string()))
        }
    }
    pub fn name(&self) -> &str {
        match self {
            CardEnum::Data(card) => &card.name,
            CardEnum::Model(card) => &card.name,
        }
    }

    pub fn repository(&self) -> &str {
        match self {
            CardEnum::Data(card) => &card.repository,
            CardEnum::Model(card) => &card.repository,
        }
    }

    pub fn uid(&self) -> &str {
        match self {
            CardEnum::Data(card) => &card.uid,
            CardEnum::Model(card) => &card.uid,
        }
    }

    pub fn version(&self) -> &str {
        match self {
            CardEnum::Data(card) => &card.version,
            CardEnum::Model(card) => &card.version,
        }
    }

    pub fn verify_card_for_registration(&self) -> Result<(), CardError> {
        // assert card.uid != common_kwargs.undefined
        // assert card.verion != common_kwargs.base_version

        if self.uid() != CommonKwargs::Undefined.to_string()
            && self.version() != CommonKwargs::BaseVersion.to_string()
        {
            let msg = format!(
                "Card {} already exists. Skipping registration. If you'd like to register
                a new card, please instantiate a new Card object. If you'd like to update the
                existing card, please use the update_card method.",
                self.uid()
            );
            return Err(CardError::Error(msg));
        };

        Ok(())
    }

    pub fn match_registry_type(&self, registry_type: &RegistryType) -> bool {
        match self {
            CardEnum::Data(_) => registry_type == &RegistryType::Data,
            CardEnum::Model(_) => registry_type == &RegistryType::Model,
        }
    }

    pub fn update_version(&mut self, version: &str) {
        match self {
            CardEnum::Data(card) => card.version = version.to_string(),
            CardEnum::Model(card) => card.version = version.to_string(),
        }
    }

    pub fn uri(&self) -> PathBuf {
        match self {
            CardEnum::Data(card) => card.uri(),
            CardEnum::Model(card) => card.uri(),
        }
    }

    pub fn update_uid(&mut self, uid: String) {
        match self {
            CardEnum::Data(card) => card.uid = uid,
            CardEnum::Model(card) => card.uid = uid,
        }
    }

    #[instrument(skip_all)]
    pub fn save_card(
        &mut self,
        py: Python,
        encrypt_key: &[u8],
        save_kwargs: Option<SaveKwargs>,
    ) -> Result<(), CardError> {
        debug!("Saving card");

        let tmp_dir = TempDir::new().map_err(|e| {
            error!("Failed to create temporary directory: {}", e);
            CardError::Error("Failed to create temporary directory".to_string())
        })?;

        let tmp_path = tmp_dir.into_path();

        // save all interface assets + Card (
        // Card will serve as metadata source of truth)
        match self {
            CardEnum::Data(_data_card) => {
                // save data card
                // data_card.save_artifacts(tmp_path)?;
            }
            CardEnum::Model(ref mut modelcard) => {
                modelcard.save(py, tmp_path.clone(), save_kwargs)?;
            }
        }

        // encrypt every file in tmp_path with encrypt_key
        

        Ok(())
    }

    pub fn get_registry_card(&self) -> Result<Card, CardError> {
        match self {
            CardEnum::Data(card) => card.get_registry_card(),
            CardEnum::Model(card) => card.get_registry_card(),
        }
    }
}
