pub struct UploadPartArgs {
    pub presigned_url: String,
    pub chunk_size: u64,
    pub chunk_index: u64,
    pub this_chunk_size: u64,
}
