use crate::error::AppError;
use opsml_types::{cards::ServiceCardMapping, SaveName, Suffix};
use std::path::Path;
use tracing::debug;

/// Load a card map from path
pub fn load_card_map(path: &Path) -> Result<ServiceCardMapping, AppError> {
    let card_mapping_path = path.join(SaveName::CardMap).with_extension(Suffix::Json);
    debug!("Loading card mapping from: {:?}", card_mapping_path);
    let mapping = ServiceCardMapping::from_path(&card_mapping_path)?;
    Ok(mapping)
}
