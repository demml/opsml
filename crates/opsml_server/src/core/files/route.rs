use crate::core::error::internal_server_error;
use crate::core::error::OpsmlServerError;
use crate::core::files::utils::download_artifact;
use crate::core::state::AppState;
use axum::extract::DefaultBodyLimit;
use axum::extract::Multipart;

use anyhow::{Context, Result};
use axum::{
    body::Body,
    extract::{Query, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::{delete, get, post},
    Extension, Json, Router,
};
use headers::HeaderMap;
use opsml_auth::permission::UserPermissions;
use opsml_sql::base::SqlClient;
use opsml_types::{contracts::*, StorageType, MAX_FILE_SIZE};

use tokio::fs::File;
use tokio::io::AsyncWriteExt;

use base64::prelude::*;
use mime_guess::mime;
/// Route for debugging information
use serde_json::json;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::path::Path;
use std::path::PathBuf;
use std::sync::Arc;
use tempfile::tempdir;
use tokio_util::io::ReaderStream;
use tracing::debug;
use tracing::{error, info, instrument};

/// Create a multipart upload session (write)
///
/// # Parameters
///
/// - `state` - The shared state of the application
/// - `params` - The query parameters for the request
///
/// # Returns
///
/// The session URL for the multipart upload
#[instrument(skip_all)]
pub async fn create_multipart_upload(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    headers: HeaderMap,
    Query(params): Query<MultiPartQuery>,
) -> Result<Json<MultiPartSession>, (StatusCode, Json<OpsmlServerError>)> {
    // If auth is enabled, check permissions or other auth-related logic
    // get user for headers (as string)

    debug!(
        "Checking permissions for create_multipart_upload for user: {:?}",
        headers.get("username")
    );

    let space_id = Path::new(&params.path).iter().next().ok_or_else(|| {
        (
            StatusCode::BAD_REQUEST,
            Json(OpsmlServerError::invalid_path()),
        )
    })?;

    // check if user has permission to write to the repo
    if !perms.has_write_permission(space_id.to_str().unwrap()) {
        return Err((
            StatusCode::FORBIDDEN,
            Json(OpsmlServerError::permission_denied()),
        ));
    }

    let path = Path::new(&params.path);
    debug!("Creating multipart upload for path: {}", path.display());

    let session_url = state.storage_client.create_multipart_upload(path).await;

    debug!("Session URL: {:?}", session_url);

    let session_url = match session_url {
        Ok(session_url) => session_url,
        Err(e) => {
            error!("Failed to create multipart upload: {}", e);
            return Err(internal_server_error(
                e,
                "Failed to create multipart upload",
            ));
        }
    };

    // if storageclient enum is aws then we need to get the bucket
    let bucket = match state.storage_client.storage_type() {
        StorageType::Aws => Some(state.storage_client.bucket().to_string()),
        _ => None,
    };

    Ok(Json(MultiPartSession {
        session_url,
        bucket,
    }))
}

/// Generate a presigned URL for a file (read)
///
/// # Parameters
///
/// - `state` - The shared state of the application
/// - `params` - The query parameters for the request
///
/// # Returns
///
/// The presigned URL for the file
pub async fn generate_presigned_url(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<PresignedQuery>,
) -> Result<Json<PresignedUrl>, (StatusCode, Json<OpsmlServerError>)> {
    // check for read access

    let path = Path::new(&params.path);

    let space_id = path.iter().next().ok_or_else(|| {
        (
            StatusCode::BAD_REQUEST,
            Json(OpsmlServerError::invalid_path()),
        )
    })?;

    if !perms.has_read_permission(space_id.to_str().unwrap()) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let for_multi_part = params.for_multi_part.unwrap_or(false);

    // for multi part uploads, we need to get the session url and part number
    if for_multi_part {
        let session_url = params
            .session_url
            .as_ref()
            .ok_or_else(|| {
                (
                    StatusCode::BAD_REQUEST,
                    Json(OpsmlServerError::missing_session_uri()),
                )
            })?
            .to_string();

        let part_number = params.part_number.ok_or_else(|| {
            (
                StatusCode::BAD_REQUEST,
                Json(OpsmlServerError::missing_part_number()),
            )
        })?;

        let path = Path::new(&params.path);
        let url = state
            .storage_client
            .generate_presigned_url_for_part(part_number, path, session_url)
            .await;

        let url = match url {
            Ok(url) => url,
            Err(e) => {
                error!("Failed to generate presigned url: {}", e);
                return Err(internal_server_error(e, "Failed to generate presigned url"));
            }
        };
        return Ok(Json(PresignedUrl { url }));
    }

    let url = state.storage_client.generate_presigned_url(path, 600).await;

    let url = match url {
        Ok(url) => url,
        Err(e) => {
            error!("Failed to generate presigned url: {}", e);
            return Err(internal_server_error(e, "Failed to generate presigned url"));
        }
    };

    Ok(Json(PresignedUrl { url }))
}

#[instrument(skip_all)]
pub async fn complete_multipart_upload(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,

    Json(req): Json<CompleteMultipartUpload>,
) -> Result<Json<UploadResponse>, (StatusCode, Json<OpsmlServerError>)> {
    // check for write access

    if !perms.has_write_permission("") {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    state
        .storage_client
        .complete_multipart_upload(req)
        .await
        .map_err(|e| {
            error!("Failed to complete multipart upload: {}", e);
            internal_server_error(e, "Failed to complete multipart upload")
        })?;

    Ok(Json(UploadResponse {
        uploaded: true,
        message: "".to_string(),
    }))
}

// this is for local storage only
#[instrument(skip_all)]
pub async fn upload_multipart(
    State(state): State<Arc<AppState>>,
    mut multipart: Multipart,
) -> Result<Json<UploadResponse>, (StatusCode, Json<OpsmlServerError>)> {
    while let Some(field) = multipart.next_field().await.unwrap() {
        let file_name = field.file_name().unwrap().to_string();
        let data = field.bytes().await.map_err(|e| {
            error!("Failed to read file: {}", e);
            internal_server_error(e, "Failed to read file")
        })?;
        let bucket = state.config.opsml_storage_uri.to_owned();

        // join the bucket and the file name
        let rpath = Path::new(&bucket).join(&file_name);

        // create the directory if it doesn't exist
        if let Some(parent) = rpath.parent() {
            tokio::fs::create_dir_all(parent).await.map_err(|e| {
                error!("Failed to create directory: {}", e);
                internal_server_error(e, "Failed to create directory")
            })?;
        }

        let mut file = File::create(&rpath).await.map_err(|e| {
            error!("Failed to create file: {}", e);
            internal_server_error(e, "Failed to create file")
        })?;
        file.write_all(&data).await.map_err(|e| {
            error!("Failed to write file: {}", e);
            internal_server_error(e, "Failed to write file")
        })?;
    }

    Ok(Json(UploadResponse {
        uploaded: true,
        message: "".to_string(),
    }))
}

pub async fn list_files(
    State(state): State<Arc<AppState>>,
    Query(params): Query<ListFileQuery>,
) -> Result<Json<ListFileResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let path = Path::new(&params.path);
    info!("Listing files for: {}", path.display());

    let files = state.storage_client.find(path).await;

    let files = match files {
        Ok(files) => files,
        Err(e) => {
            error!("Failed to list files: {}", e);
            return Err(internal_server_error(e, "Failed to list files"));
        }
    };

    Ok(Json(ListFileResponse { files }))
}

pub async fn list_file_info(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<ListFileQuery>,
) -> Result<Json<ListFileInfoResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let path = Path::new(&params.path);

    debug!("Getting file info for: {}", path.display(),);

    let space_id = path.iter().next().ok_or_else(|| {
        (
            StatusCode::BAD_REQUEST,
            Json(OpsmlServerError::invalid_path()),
        )
    })?;

    if !perms.has_read_permission(space_id.to_str().unwrap()) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let files = state.storage_client.find_info(path).await;

    let files = match files {
        Ok(files) => files,
        Err(e) => {
            error!("Failed to list files: {}", e);
            return Err(internal_server_error(e, "Failed to list files"));
        }
    };

    Ok(Json(ListFileInfoResponse { files }))
}

pub async fn file_tree(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<ListFileQuery>,
) -> Result<Json<FileTreeResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let path = Path::new(&params.path);

    let space_id = path.iter().next().ok_or_else(|| {
        (
            StatusCode::BAD_REQUEST,
            Json(OpsmlServerError::invalid_path()),
        )
    })?;

    if !perms.has_read_permission(space_id.to_str().unwrap()) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let files = state.storage_client.find_info(path).await;

    let files = match files {
        Ok(files) => files,
        Err(e) => {
            error!("Failed to list files: {}", e);
            return Err(internal_server_error(e, "Failed to list files"));
        }
    };

    let mut file_tree_nodes: Vec<FileTreeNode> = Vec::new();
    let mut seen_directories: std::collections::HashSet<String> = std::collections::HashSet::new();

    for file_info in files {
        let stripped_path = file_info.stripped_path.clone();
        let parts: Vec<&str> = stripped_path.split('/').collect();

        if parts.len() > 1 {
            let dir_name = parts[0].to_string();
            let dir_path = file_info.name
                [..file_info.name.find(&dir_name).unwrap() + dir_name.len()]
                .to_string();

            if !seen_directories.contains(&dir_path) {
                seen_directories.insert(dir_path.clone());
                file_tree_nodes.push(FileTreeNode {
                    name: dir_name,
                    created_at: file_info.created.clone(),
                    object_type: "directory".to_string(),
                    size: 0,
                    path: dir_path,
                    suffix: "".to_string(),
                });
            }
        } else if !stripped_path.is_empty() {
            file_tree_nodes.push(FileTreeNode {
                name: stripped_path.clone(),
                created_at: file_info.created.clone(),
                object_type: "file".to_string(),
                size: file_info.size,
                path: file_info.name.clone(),
                suffix: file_info.suffix.clone(),
            });
        }
    }

    file_tree_nodes.sort_by(|a, b| {
        if a.object_type == b.object_type {
            a.name.cmp(&b.name)
        } else if a.object_type == "directory" {
            std::cmp::Ordering::Less
        } else {
            std::cmp::Ordering::Greater
        }
    });

    Ok(Json(FileTreeResponse {
        files: file_tree_nodes,
    }))
}

#[instrument(skip_all)]
pub async fn get_file_for_ui(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<RawFileRequest>,
) -> Result<Json<RawFile>, (StatusCode, Json<OpsmlServerError>)> {
    let file_path = PathBuf::from(&req.path);

    let space_id = file_path.iter().next().ok_or_else(|| {
        (
            StatusCode::BAD_REQUEST,
            Json(OpsmlServerError::invalid_path()),
        )
    })?;

    if !perms.has_read_permission(space_id.to_str().unwrap()) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let files = state.storage_client.find_info(&file_path).await;

    let files = match files {
        Ok(files) => files,
        Err(e) => {
            error!("Failed to list files: {}", e);
            return Err(internal_server_error(e, "Failed to list files"));
        }
    };

    // check if empty, if not get first
    let file = match files.first() {
        Some(file) => file,
        None => {
            error!("File not found");
            return OpsmlServerError::no_files_found().into_response(StatusCode::NOT_FOUND);
        }
    };

    // check if size is less than 50 mb
    if file.size > 50_000_000 {
        error!("File size too large");
        return OpsmlServerError::file_too_large().into_response(StatusCode::BAD_REQUEST);
    }

    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {}", e);
        internal_server_error(e, "Failed to create temp dir")
    })?;

    let lpath = tmp_dir.path().join(file_path.file_name().unwrap());

    download_artifact(
        state.storage_client.clone(),
        state.sql_client.clone(),
        &lpath,
        &file.name,
        &req.registry_type.to_string(),
        Some(&req.uid),
    )
    .await
    .map_err(|e| {
        error!("Failed to download artifact: {}", e);
        internal_server_error(e, "Failed to download artifact")
    })?;

    debug!("Downloaded file to: {}", lpath.display());

    let mime_type = mime_guess::from_path(&lpath).first_or_octet_stream();

    let content = if mime_type.type_() == mime::IMAGE {
        let bytes = std::fs::read(&lpath).map_err(|e| {
            error!("Failed to read file: {}", e);
            internal_server_error(e, "Failed to read file")
        })?;
        BASE64_STANDARD.encode(&bytes)
    } else {
        std::fs::read_to_string(&lpath).map_err(|e| {
            error!("Failed to read file: {}", e);
            internal_server_error(e, "Failed to read file")
        })?
    };

    Ok(Json(RawFile {
        content,
        suffix: file.suffix.to_string(),
        mime_type: mime_type.to_string(),
    }))
}

pub async fn delete_file(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,

    Query(params): Query<DeleteFileQuery>,
) -> Result<Json<DeleteFileResponse>, (StatusCode, Json<OpsmlServerError>)> {
    // check for delete access

    // check if user has permission to write to the repo
    let space_id = Path::new(&params.path).iter().next().ok_or_else(|| {
        (
            StatusCode::BAD_REQUEST,
            Json(OpsmlServerError::invalid_path()),
        )
    })?;

    if !perms.has_delete_permission(space_id.to_str().unwrap()) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let path = Path::new(&params.path);
    let recursive = params.recursive;

    info!("Deleting path: {}", path.display());

    let files = state.storage_client.rm(path, recursive).await;

    //
    if let Err(e) = files {
        return Err({
            error!("Failed to delete files: {}", e);
            internal_server_error(e, "Failed to delete files")
        });
    }

    // check if file exists
    let exists = state.storage_client.exists(path).await;

    match exists {
        Ok(exists) => {
            if exists {
                OpsmlServerError::failed_to_delete_file()
                    .into_response(StatusCode::INTERNAL_SERVER_ERROR)
            } else {
                Ok(Json(DeleteFileResponse { deleted: true }))
            }
        }
        Err(e) => {
            error!("Failed to check if file exists: {}", e);
            Err(internal_server_error(e, "Failed to check if file exists"))
        }
    }
}

// for use with local storage only
pub async fn download_file(
    State(state): State<Arc<AppState>>,
    Query(params): Query<DownloadFileQuery>,
) -> Response<Body> {
    // check if storage client is local (fails if not)
    if state.storage_client.storage_type() != StorageType::Local {
        return (
            StatusCode::BAD_REQUEST,
            Json(json!({ "error": "Download is only supported for local storage" })),
        )
            .into_response();
    }

    // need to join the bucket and the file name

    let path = Path::new(&params.path);
    let bucket = state.config.opsml_storage_uri.clone();
    let rpath = Path::new(&bucket).join(path);

    let file = match File::open(&rpath).await {
        Ok(file) => file,
        Err(e) => {
            error!("Failed to open file: {}", e);
            return internal_server_error(e, "Failed to open file").into_response();
        }
    };

    let stream = ReaderStream::new(file);
    let body = Body::from_stream(stream);

    (StatusCode::OK, body).into_response()
}

#[instrument(skip_all)]
pub async fn get_artifact_key(
    State(state): State<Arc<AppState>>,
    Query(req): Query<ArtifactKeyRequest>,
) -> Result<Json<ArtifactKey>, (StatusCode, Json<OpsmlServerError>)> {
    debug!("Getting artifact key for: {:?}", req);
    let key = state
        .sql_client
        .get_artifact_key(&req.uid, &req.registry_type.to_string())
        .await
        .map_err(|e| {
            error!("Failed to get artifact key: {}", e);
            internal_server_error(e, "Failed to get artifact key")
        })?;

    Ok(Json(key))
}

pub async fn get_file_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{}/files/multipart", prefix),
                get(create_multipart_upload),
            )
            .route(
                &format!("{}/files/multipart", prefix),
                post(upload_multipart).layer(DefaultBodyLimit::max(MAX_FILE_SIZE)),
            )
            .route(
                &format!("{}/files/multipart/complete", prefix),
                post(complete_multipart_upload),
            )
            .route(&format!("{}/files", prefix), get(download_file))
            .route(
                &format!("{}/files/presigned", prefix),
                get(generate_presigned_url),
            )
            .route(&format!("{}/files/list", prefix), get(list_files))
            .route(&format!("{}/files/tree", prefix), get(file_tree))
            .route(&format!("{}/files/list/info", prefix), get(list_file_info))
            .route(&format!("{}/files/delete", prefix), delete(delete_file))
            .route(&format!("{}/files/key", prefix), get(get_artifact_key))
            .route(&format!("{}/files/content", prefix), post(get_file_for_ui))
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create file router");
            // panic
            Err(anyhow::anyhow!("Failed to create file router"))
                .context("Panic occurred while creating the router")
        }
    }
}
