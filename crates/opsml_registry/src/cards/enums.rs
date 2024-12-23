use crate::cards::{DataCard, ModelCard};
use opsml_error::error::CardError;
use opsml_types::{CommonKwargs, RegistryType};
use pyo3::prelude::*;

#[derive(Debug)]
pub enum CardEnum {
    Data(DataCard),
    Model(ModelCard),
}

impl CardEnum {
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

    pub fn uri(&self) -> String {
        match self {
            CardEnum::Data(card) => card.uri(),
            CardEnum::Model(card) => card.uri(),
        }
    }

    pub fn set_uid(&mut self, py: Python, uid: &str) -> Result<(), CardError> {
        match self {
            CardEnum::Data(_) => Ok(()),
            CardEnum::Model(card) => card.set_uid(py, uid),
        }
    }
}
