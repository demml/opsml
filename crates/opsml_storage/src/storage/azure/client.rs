use crate::storage::azure::error::AzureError;
use crate::storage::base::get_files;
use crate::storage::base::PathExt;
use crate::storage::base::StorageClient;
use crate::storage::error::StorageError;
use crate::storage::filesystem::FileSystem;
use crate::storage::utils::get_chunk_parts;
use crate::storage::utils::set_download_chunk_size;
use async_trait::async_trait;
use azure_storage::prelude::*;
use azure_storage::shared_access_signature::service_sas::BlobSasPermissions;
use azure_storage_blobs::container::operations::BlobItem;
use azure_storage_blobs::prelude::*;
use base64::prelude::*;
use futures::stream::StreamExt;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_types::contracts::CompleteMultipartUpload;
use opsml_types::contracts::MultipartCompleteParts;
use opsml_types::contracts::{FileInfo, UploadPartArgs};
use opsml_types::StorageType;
use opsml_utils::ChunkParts;
use reqwest::Client as HttpClient;
use std::env;
use std::fs::File;
use std::io::BufReader;
use std::io::Read;
use std::io::Seek;
use std::io::Write;
use std::path::{Path, PathBuf};
use time::{Duration, OffsetDateTime};

pub struct AzureCreds {
    pub account: String,
    pub creds: StorageCredentials,
}

impl AzureCreds {
    pub async fn new() -> Result<Self, AzureError> {
        let credential = azure_identity::create_credential()?;
        let account = env::var("AZURE_STORAGE_ACCOUNT")?;
        let creds = StorageCredentials::token_credential(credential);

        Ok(Self { account, creds })
    }
}

pub struct AzureMultipartUpload {
    client: HttpClient,
    pub signed_url: String,
    file: File,
}

pub struct UploadState {
    block_parts: Vec<BlobBlockType>,
    bytes_uploaded: u64,
}

impl AzureMultipartUpload {
    pub async fn new(signed_url: &str, path: &str, client: HttpClient) -> Result<Self, AzureError> {
        let file = File::open(path)?;

        Ok(Self {
            client,
            signed_url: signed_url.to_string(),
            file,
        })
    }

    pub async fn upload_file_in_chunks(&self, chunk_parts: ChunkParts) -> Result<(), AzureError> {
        let mut upload_state = UploadState {
            block_parts: Vec::new(),
            bytes_uploaded: 0,
        };

        for chunk_index in 0..chunk_parts.chunk_count {
            let this_chunk = if chunk_parts.chunk_count - 1 == chunk_index {
                chunk_parts.size_of_last_chunk
            } else {
                chunk_parts.chunk_size
            };

            let upload_args = UploadPartArgs {
                chunk_size: chunk_parts.chunk_size,
                chunk_index,
                this_chunk_size: this_chunk,
            };

            upload_state = self.upload_chunk(&upload_args, upload_state).await?;
        } // extract the range from the result and update the first_byte and last_byte

        self.complete_upload(upload_state.block_parts).await?;

        Ok(())

        // check if enum is Ok
    }

    async fn upload_chunk(
        &self,
        upload_args: &UploadPartArgs,
        mut state: UploadState,
    ) -> Result<UploadState, AzureError> {
        let buffer = self.read_chunk(upload_args)?;
        let block_id = format!("{:06}", upload_args.chunk_index);

        self.upload_block(&block_id, &buffer).await?;

        state
            .block_parts
            .push(BlobBlockType::Uncommitted(BlockId::new(block_id)));
        state.bytes_uploaded += buffer.len() as u64;

        Ok(state)
    }

    fn read_chunk(&self, upload_args: &UploadPartArgs) -> Result<Vec<u8>, AzureError> {
        let mut reader = BufReader::new(&self.file);
        let offset = upload_args.chunk_index * upload_args.chunk_size;

        reader.seek(std::io::SeekFrom::Start(offset))?;

        let mut buffer = vec![0; upload_args.this_chunk_size as usize];
        let bytes_read = reader.read(&mut buffer)?;

        buffer.truncate(bytes_read);
        Ok(buffer)
    }

    async fn upload_block(&self, block_id: &str, data: &[u8]) -> Result<(), AzureError> {
        let url = format!(
            "{}&comp=block&blockid={}",
            self.signed_url,
            BASE64_STANDARD.encode(block_id)
        );

        self.client.put(&url).body(data.to_vec()).send().await?;

        Ok(())
    }

    async fn complete_upload(&self, block_parts: Vec<BlobBlockType>) -> Result<(), AzureError> {
        let url = format!("{}&comp=blocklist", self.signed_url);
        let block_list = BlockList {
            blocks: block_parts,
        };
        let block_xml = block_list.to_xml();

        self.client
            .put(&url)
            .header("Content-Type", "application/xml")
            .body(block_xml)
            .send()
            .await?;

        Ok(())
    }
}

#[derive(Clone)]
pub struct AzureStorageClient {
    pub client: BlobServiceClient,
    pub bucket: String,
}

#[async_trait]
impl StorageClient for AzureStorageClient {
    fn storage_type(&self) -> StorageType {
        StorageType::Azure
    }

    async fn bucket(&self) -> &str {
        &self.bucket
    }

    async fn new(settings: &OpsmlStorageSettings) -> Result<Self, StorageError> {
        // Get Azure credentials (anonymous if client mode, else use AzureCreds)
        let creds = AzureCreds::new().await?;

        let client = BlobServiceClient::new(creds.account, creds.creds);

        let bucket = settings
            .storage_uri
            .strip_prefix("az://")
            .unwrap_or(&settings.storage_uri)
            .to_string();

        Ok(Self { client, bucket })
    }

    async fn copy_object(&self, src: &str, dest: &str) -> Result<bool, StorageError> {
        let container = self.client.container_client(self.bucket.as_str());
        let src_blob = container.blob_client(src);
        let dest_blob = container.blob_client(dest);

        let _response = dest_blob
            .copy_from_url(src_blob.url().map_err(AzureError::CoreError)?)
            .await
            .map_err(AzureError::CoreError)?;

        Ok(true)
    }

    async fn copy_objects(&self, src: &str, dest: &str) -> Result<bool, StorageError> {
        let objects = self.find(src).await?;
        let dest = Path::new(dest);
        let src = PathBuf::from(src);

        for obj in objects {
            let file_path = Path::new(obj.as_str());
            let relative_path = file_path.relative_path(&src)?;
            let remote_path = dest.join(relative_path);

            self.copy_object(file_path.to_str().unwrap(), remote_path.to_str().unwrap())
                .await?;
        }

        Ok(true)
    }

    async fn get_object(&self, lpath: &str, rpath: &str) -> Result<(), StorageError> {
        let lpath = Path::new(lpath);
        let rpath = Path::new(rpath);

        if lpath.extension().is_none() || rpath.extension().is_none() {
            return Err(StorageError::PathMustBeDirectoryError);
        }

        // create and open lpath file
        let prefix = Path::new(lpath).parent().unwrap();

        if !prefix.exists() {
            // create the directory if it does not exist and skip errors
            std::fs::create_dir_all(prefix)?;
        }

        // create and open lpath file
        let mut file = File::create(lpath)?;
        let file_size = file.metadata()?.len();

        let chunk_size = set_download_chunk_size(file_size, None);

        let container = self.client.container_client(self.bucket.as_str());
        let blob = container.blob_client(rpath.to_str().unwrap());

        let mut stream = blob.get().chunk_size(chunk_size as u64).into_stream();

        // iterate over the stream and write to the file
        while let Some(value) = stream.next().await {
            let chunk = value.map_err(AzureError::CoreError)?.data;

            // collect into bytes
            let bytes = chunk.collect().await.map_err(AzureError::CoreError)?;

            file.write_all(&bytes)?;
        }

        Ok(())
    }

    async fn generate_presigned_url(
        &self,
        path: &str,
        expiration: u64,
    ) -> Result<String, StorageError> {
        let start = OffsetDateTime::now_utc();
        let expiry = start + Duration::seconds(expiration as i64);
        let response = self
            .client
            .get_user_deligation_key(start, expiry)
            .await
            .map_err(AzureError::CoreError)?;

        let container = self.client.container_client(self.bucket.as_str());
        let blob = container.blob_client(path);

        let sas = blob
            .user_delegation_shared_access_signature(
                BlobSasPermissions {
                    read: true,
                    ..Default::default()
                },
                &response.user_deligation_key,
            )
            .await
            .map_err(AzureError::CoreError)?;
        let url = blob
            .generate_signed_blob_url(&sas)
            .map_err(AzureError::CoreError)?;

        Ok(url.to_string())
    }

    async fn find(&self, path: &str) -> Result<Vec<String>, StorageError> {
        let container = self.client.container_client(self.bucket.as_str());
        let mut results = Vec::new();

        let rpath = path.to_string();
        let mut stream = container.list_blobs().prefix(rpath).into_stream();

        while let Some(value) = stream.next().await {
            let value = value.unwrap();

            let blobs = value.blobs.items;
            // iterate over the blobs and match to enum
            for blob in blobs {
                match blob {
                    BlobItem::Blob(blob) => {
                        results.push(blob.name);
                    }
                    BlobItem::BlobPrefix(_prefix) => {
                        // pass
                    }
                }
            }
        }

        Ok(results)
    }

    async fn find_info(&self, path: &str) -> Result<Vec<FileInfo>, StorageError> {
        let container = self.client.container_client(self.bucket.as_str());
        let mut results = Vec::new();

        let rpath = path.to_string();
        let mut stream = container.list_blobs().prefix(rpath).into_stream();

        while let Some(value) = stream.next().await {
            let value = value.map_err(AzureError::CoreError)?;
            let blobs = value.blobs.items;
            // iterate over the blobs and match to enum
            for blob in blobs {
                match blob {
                    BlobItem::Blob(blob) => {
                        let name = blob.name;

                        let filepath = name
                            .strip_prefix(&format!("{}/", self.bucket))
                            .unwrap_or(&name);

                        let stripped_path = name
                            .strip_prefix(path)
                            .unwrap_or(filepath)
                            .strip_prefix("/")
                            .unwrap_or(filepath)
                            .to_string();

                        let suffix = name.split('.').next_back().unwrap().to_string();
                        let info = FileInfo {
                            name: filepath.to_string(),
                            size: blob.properties.content_length as i64,
                            created: blob.properties.creation_time.to_string(),
                            object_type: "file".to_string(),
                            suffix,
                            stripped_path,
                        };
                        results.push(info);
                    }
                    BlobItem::BlobPrefix(_prefix) => {
                        // pass
                    }
                }
            }
        }

        Ok(results)
    }

    async fn delete_object(&self, path: &str) -> Result<bool, StorageError> {
        let container = self.client.container_client(self.bucket.as_str());
        let blob = container.blob_client(path);

        let response = blob.delete().await.map_err(AzureError::CoreError)?;

        Ok(response.delete_type_permanent)
    }

    async fn delete_objects(&self, path: &str) -> Result<bool, StorageError> {
        let objects = self.find(path).await?;

        for obj in objects {
            self.delete_object(obj.as_str()).await?;
        }

        Ok(true)
    }
}

impl AzureStorageClient {
    async fn generate_presigned_url_for_block_upload(
        &self,
        path: &str,
        expiration: u64,
    ) -> Result<String, AzureError> {
        let start = OffsetDateTime::now_utc();
        let expiry = start + Duration::seconds(expiration as i64);
        let response = self.client.get_user_deligation_key(start, expiry).await?;

        let container = self.client.container_client(self.bucket.as_str());
        let blob = container.blob_client(path);

        let sas = blob
            .user_delegation_shared_access_signature(
                BlobSasPermissions {
                    read: true,
                    write: true,
                    create: true,
                    ..Default::default()
                },
                &response.user_deligation_key,
            )
            .await
            .map_err(AzureError::CoreError)?;
        let url = blob.generate_signed_blob_url(&sas)?;

        Ok(url.to_string())
    }
}

#[derive(Clone)]
pub struct AzureFSStorageClient {
    client: AzureStorageClient,
    http_client: HttpClient,
}

#[async_trait]
impl FileSystem for AzureFSStorageClient {
    fn name(&self) -> &str {
        "AzureFSStorageClient"
    }

    fn bucket(&self) -> &str {
        &self.client.bucket
    }

    fn storage_type(&self) -> StorageType {
        StorageType::Local
    }

    async fn new(settings: &OpsmlStorageSettings) -> Self {
        let client = AzureStorageClient::new(settings).await.unwrap();
        let http_client = HttpClient::new();
        Self {
            client,
            http_client,
        }
    }

    async fn find(&self, path: &Path) -> Result<Vec<String>, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        self.client.find(stripped_path.to_str().unwrap()).await
    }

    async fn find_info(&self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        self.client.find_info(stripped_path.to_str().unwrap()).await
    }

    async fn get(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        // strip the paths
        let stripped_rpath = rpath.strip_path(self.client.bucket().await);
        let stripped_lpath = lpath.strip_path(self.client.bucket().await);

        if recursive {
            // list all objects in the path
            let objects = self.client.find(stripped_rpath.to_str().unwrap()).await?;

            // iterate over each object and get it
            for obj in objects {
                let file_path = Path::new(obj.as_str());
                let stripped_path = file_path.strip_path(self.client.bucket().await);
                let relative_path = file_path.relative_path(&stripped_rpath)?;
                let local_path = stripped_lpath.join(relative_path);

                self.client
                    .get_object(
                        local_path.to_str().unwrap(),
                        stripped_path.to_str().unwrap(),
                    )
                    .await?;
            }
        } else {
            self.client
                .get_object(
                    stripped_lpath.to_str().unwrap(),
                    stripped_rpath.to_str().unwrap(),
                )
                .await?;
        }

        Ok(())
    }

    async fn copy(&self, src: &Path, dest: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_src = src.strip_path(self.client.bucket().await);
        let stripped_dest = dest.strip_path(self.client.bucket().await);

        if recursive {
            self.client
                .copy_objects(
                    stripped_src.to_str().unwrap(),
                    stripped_dest.to_str().unwrap(),
                )
                .await?;
        } else {
            self.client
                .copy_object(
                    stripped_src.to_str().unwrap(),
                    stripped_dest.to_str().unwrap(),
                )
                .await?;
        }

        Ok(())
    }

    async fn rm(&self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);

        if recursive {
            self.client
                .delete_objects(stripped_path.to_str().unwrap())
                .await?;
        } else {
            self.client
                .delete_object(stripped_path.to_str().unwrap())
                .await?;
        }

        Ok(())
    }

    async fn exists(&self, path: &Path) -> Result<bool, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        let objects = self.client.find(stripped_path.to_str().unwrap()).await?;

        Ok(!objects.is_empty())
    }

    async fn generate_presigned_url(
        &self,
        path: &Path,
        expiration: u64,
    ) -> Result<String, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        self.client
            .generate_presigned_url(stripped_path.to_str().unwrap(), expiration)
            .await
    }

    async fn put(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_lpath = lpath.strip_path(self.client.bucket().await);
        let stripped_rpath = rpath.strip_path(self.client.bucket().await);

        if recursive {
            if !stripped_lpath.is_dir() {
                return Err(StorageError::PathMustBeDirectoryError);
            }

            let files: Vec<PathBuf> = get_files(&stripped_lpath)?;

            for file in files {
                let chunk_parts = get_chunk_parts(&file)?;

                let stripped_file_path = file.strip_path(self.client.bucket().await);
                let relative_path = file.relative_path(&stripped_lpath)?;
                let remote_path = stripped_rpath.join(relative_path);

                let uploader = self
                    .create_multipart_uploader(&stripped_file_path, &remote_path)
                    .await?;

                uploader.upload_file_in_chunks(chunk_parts).await?;
            }
        } else {
            let chunk_parts = get_chunk_parts(&stripped_lpath)?;

            let uploader = self
                .create_multipart_uploader(&stripped_lpath, &stripped_rpath)
                .await?;

            uploader.upload_file_in_chunks(chunk_parts).await?;
        };

        Ok(())
    }

    async fn complete_multipart_upload(
        &self,
        request: CompleteMultipartUpload,
    ) -> Result<(), StorageError> {
        let url = format!("{}&comp=blocklist", request.session_url);

        let block_list = match request.parts {
            MultipartCompleteParts::Azure(parts) => BlockList {
                blocks: parts
                    .iter()
                    .map(|part| {
                        let block_id = BlockId::new(part.clone());
                        BlobBlockType::Uncommitted(block_id)
                    })
                    .collect(),
            },
            _ => return Err(AzureError::InvalidPartsTypeError.into()),
        };

        let block_xml = block_list.to_xml();

        self.http_client
            .put(&url)
            .header("Content-Type", "application/xml")
            .body(block_xml)
            .send()
            .await
            .map_err(AzureError::ReqwestError)?;

        Ok(())
    }
}

impl AzureFSStorageClient {
    pub async fn create_multipart_uploader(
        &self,
        lpath: &Path,
        rpath: &Path,
    ) -> Result<AzureMultipartUpload, AzureError> {
        let signed_url = self
            .client
            .generate_presigned_url_for_block_upload(rpath.to_str().unwrap(), 600)
            .await?;

        AzureMultipartUpload::new(
            &signed_url,
            lpath.to_str().unwrap(),
            self.http_client.clone(),
        )
        .await
    }

    pub async fn create_multipart_upload(&self, rpath: &Path) -> Result<String, AzureError> {
        self.client
            .generate_presigned_url_for_block_upload(rpath.to_str().unwrap(), 600)
            .await
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::storage::error::StorageError;
    use opsml_settings::config::OpsmlConfig;
    use opsml_utils::create_uuid7;
    use rand::distr::Alphanumeric;
    use rand::rng;
    use rand::Rng;
    use std::path::Path;
    use tempfile::TempDir;

    pub fn create_file(name: &str, chunk_size: &u64) {
        let mut file = File::create(name).expect("Could not create sample file.");

        while file.metadata().unwrap().len() <= chunk_size * 2 {
            let rand_string: String = rng()
                .sample_iter(&Alphanumeric)
                .take(256)
                .map(char::from)
                .collect();
            let return_string: String = "\n".to_string();
            file.write_all(rand_string.as_ref())
                .expect("Error writing to file.");
            file.write_all(return_string.as_ref())
                .expect("Error writing to file.");
        }
    }

    #[tokio::test]
    async fn test_azure_storage_server() -> Result<(), StorageError> {
        let rand_name = create_uuid7();
        let filename = format!("file-{rand_name}.txt");

        let tmp_dir = TempDir::new().unwrap();
        let tmp_path = tmp_dir.path();

        // write file to temp dir (create_file)
        let lpath = tmp_path.join(&filename);
        create_file(lpath.to_str().unwrap(), &1024);

        let settings = OpsmlConfig::default(); // Adjust settings as needed
        let storage_client = AzureFSStorageClient::new(&settings.storage_settings().unwrap()).await;

        let rpath_dir = Path::new("test_dir");
        let rpath = rpath_dir.join(&filename);

        if storage_client.exists(rpath_dir).await? {
            storage_client.rm(rpath_dir, true).await?;
        }

        assert!(!storage_client.exists(rpath_dir).await?);

        // put
        storage_client.put(&lpath, &rpath, false).await?;
        assert!(storage_client.exists(&rpath).await?);

        let nested_path = format!("nested/really/deep/file-{rand_name}.txt");
        let rpath_nested = rpath.parent().unwrap().join(nested_path);

        storage_client.put(&lpath, &rpath_nested, false).await?;

        let path = storage_client.generate_presigned_url(&rpath, 10).await?;
        assert!(!path.is_empty());

        // ls
        assert!(!storage_client
            .find(rpath_nested.parent().unwrap())
            .await?
            .is_empty());

        // find
        let blobs = storage_client.find(rpath_dir).await?;

        assert_eq!(
            blobs,
            vec![
                rpath.to_str().unwrap().to_string(),
                rpath_nested.to_str().unwrap().to_string()
            ]
        );

        // create new temp dir
        let new_tmp_dir = TempDir::new().unwrap();

        let new_lpath = new_tmp_dir.path().join(&filename);

        // get
        storage_client.get(&new_lpath, &rpath, false).await?;
        assert!(new_lpath.exists());

        // rm
        storage_client.rm(&rpath, false).await?;
        assert!(!storage_client.exists(&rpath).await?);

        // rm recursive
        storage_client.rm(rpath_dir, true).await?;
        assert!(!storage_client.exists(rpath_dir).await?);

        Ok(())
    }

    #[tokio::test]
    async fn test_azure_storage_server_trees() -> Result<(), StorageError> {
        let rand_name = create_uuid7();

        let tmp_dir = TempDir::new().unwrap();
        let tmp_path = tmp_dir.path();
        let settings = OpsmlConfig::default(); // Adjust settings as needed
        let storage_client = AzureFSStorageClient::new(&settings.storage_settings().unwrap()).await;

        let child = tmp_path.join("child");
        let grand_child = child.join("grandchild");
        for path in &[tmp_path, &child, &grand_child] {
            std::fs::create_dir_all(path).unwrap();
            let txt_file = format!("file-{rand_name}.txt");
            let txt_path = path.join(txt_file);
            std::fs::write(&txt_path, "hello, world").unwrap();
        }

        let new_rand_name = create_uuid7();
        let rpath_root = Path::new(&new_rand_name);

        if storage_client.exists(rpath_root).await? {
            storage_client.rm(rpath_root, true).await?;
        }

        // put
        storage_client.put(tmp_path, rpath_root, true).await?;
        assert_eq!(storage_client.find(rpath_root).await?.len(), 3);

        // copy
        let copy_dir = rpath_root.join("copy");
        storage_client
            .copy(&rpath_root.join("child"), &copy_dir, true)
            .await?;
        assert_eq!(storage_client.find(&copy_dir).await?.len(), 2);

        // put
        let put_dir = rpath_root.join("copy2");
        storage_client.put(&child, &put_dir, true).await?;
        assert_eq!(storage_client.find(&put_dir).await?.len(), 2);

        // rm
        storage_client.rm(&put_dir, true).await?;
        assert_eq!(storage_client.find(&put_dir).await?.len(), 0);

        storage_client.rm(rpath_root, true).await?;

        Ok(())
    }
}
