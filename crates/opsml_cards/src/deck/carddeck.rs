use chrono::{DateTime, Utc};
use opsml_error::{CardError, OpsmlError};
use opsml_types::cards::BaseArgs;
use opsml_types::SaveName;
use opsml_types::Suffix;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::PyTraverseError;
use pyo3::PyVisit;
use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};
use std::collections::HashMap;
use std::path::PathBuf;
use tracing::error;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Card {
    #[pyo3(get, set)]
    pub space: String,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub registry_type: String,

    #[pyo3(get, set)]
    pub alias: String,
}

/// CardDeck is a collection of cards that can be used to create a card deck and load in one call
///
#[pyclass]
#[derive(Debug)]
pub struct CardDeck {
    #[pyo3(get, set)]
    pub space: String,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub created_at: DateTime<Utc>,

    #[pyo3(get, set)]
    pub cards: Vec<Card>,

    #[pyo3(get)]
    pub opsml_version: String,

    // this is the holder for the card objects (ModelCard, DataCard, etc.)
    pub card_objs: HashMap<String, PyObject>,
}

#[pymethods]
impl CardDeck {
    #[new]
    #[pyo3(signature = (space, name,  cards, version=None))]
    pub fn new(space: &str, name: &str, cards: Vec<Card>, version: Option<&str>) -> PyResult<Self> {
        let base_args =
            BaseArgs::create_args(Some(name), Some(space), version, None).map_err(|e| {
                error!("Failed to create base args: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;
        Ok(CardDeck {
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            created_at: Utc::now(),
            cards,
            opsml_version: env!("CARGO_PKG_VERSION").to_string(),
            card_objs: HashMap::new(),
        })
    }

    pub fn save_card(&self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, &card_save_path)?;

        Ok(())
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        for card_obj in self.card_objs.values() {
            visit.call(card_obj)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.card_objs.clear();
    }
}

impl Serialize for CardDeck {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("CardDeck", 7)?;

        // set session to none
        state.serialize_field("space", &self.space)?;
        state.serialize_field("name", &self.name)?;
        state.serialize_field("version", &self.version)?;
        state.serialize_field("uid", &self.uid)?;
        state.serialize_field("created_at", &self.created_at)?;
        state.serialize_field("cards", &self.cards)?;
        state.serialize_field("opsml_version", &self.opsml_version)?;
        state.end()
    }
}

impl<'de> Deserialize<'de> for CardDeck {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(field_identifier, rename_all = "snake_case")]
        enum Field {
            Space,
            Name,
            Version,
            Uid,
            CreatedAt,
            OpsmlVersion,
            Cards,
            CardObjs,
        }

        struct CardDeckVisitor;

        impl<'de> Visitor<'de> for CardDeckVisitor {
            type Value = CardDeck;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct CardDeck")
            }

            fn visit_map<V>(self, mut map: V) -> Result<CardDeck, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut space = None;
                let mut name = None;
                let mut version = None;
                let mut uid = None;
                let mut created_at = None;
                let mut opsml_version = None;
                let mut cards = None;
                let mut card_objs = None;

                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Space => {
                            space = Some(map.next_value()?);
                        }
                        Field::Name => {
                            name = Some(map.next_value()?);
                        }
                        Field::Version => {
                            version = Some(map.next_value()?);
                        }
                        Field::Uid => {
                            uid = Some(map.next_value()?);
                        }

                        Field::CreatedAt => {
                            created_at = Some(map.next_value()?);
                        }

                        Field::OpsmlVersion => {
                            opsml_version = Some(map.next_value()?);
                        }
                        Field::Cards => {
                            cards = Some(map.next_value()?);
                        }
                        Field::CardObjs => {
                            card_objs = None;
                        }
                    }
                }

                let space = space.ok_or_else(|| de::Error::missing_field("space"))?;
                let name = name.ok_or_else(|| de::Error::missing_field("name"))?;
                let version = version.ok_or_else(|| de::Error::missing_field("version"))?;
                let uid = uid.ok_or_else(|| de::Error::missing_field("uid"))?;
                let created_at =
                    created_at.ok_or_else(|| de::Error::missing_field("created_at"))?;
                let opsml_version =
                    opsml_version.ok_or_else(|| de::Error::missing_field("opsml_version"))?;
                let cards = cards.ok_or_else(|| de::Error::missing_field("cards"))?;
                let card_objs = card_objs.unwrap_or_else(|| HashMap::new());

                Ok(CardDeck {
                    space,
                    name,
                    version,
                    uid,
                    created_at,
                    cards,
                    opsml_version,
                    card_objs,
                })
            }
        }

        const FIELDS: &[&str] = &[
            "space",
            "name",
            "version",
            "uid",
            "created_at",
            "opsml_version",
            "cards",
            "card_objs",
        ];
        deserializer.deserialize_struct("CardDeck", FIELDS, CardDeckVisitor)
    }
}
