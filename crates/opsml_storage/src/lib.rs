pub mod storage;

#[cfg(feature = "server")]
pub use storage::enums::client::StorageClientEnum;

pub use storage::filesystem::{reset_storage_client, storage_client, FileSystemStorage};
pub use storage::http::client::HttpFSStorageClient;
