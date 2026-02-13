pub mod storage;

#[cfg(feature = "server")]
pub use storage::enums::client::StorageClientEnum;

pub use crate::storage::error::StorageError;
pub use crate::storage::local::client::copy_objects;
pub use storage::filesystem::{
    FileSystemStorage, async_storage_client, reset_storage_client, storage_client,
};
pub use storage::http::client::HttpFSStorageClient;
