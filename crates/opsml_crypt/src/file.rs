use aes_gcm::Nonce;
use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm,
    Key, // Or `Aes128Gcm`
};
use opsml_error::CryptError;
use opsml_utils::FileUtils;
use rayon::iter::{IntoParallelIterator, ParallelIterator};
use std::fs::{self, File};
use std::io::{BufReader, BufWriter, Read, Write};
use std::path::Path;
use tracing::{debug, instrument};

static CHUNK_SIZE: usize = 1024 * 1024 * 4; // 4MiB

pub fn encrypt_file(input_path: &Path, key_bytes: &[u8]) -> Result<(), CryptError> {
    let key = Key::<Aes256Gcm>::from_slice(key_bytes);
    let cipher = Aes256Gcm::new(key);

    let temp_output_path = input_path.with_extension("enc.tmp");
    let mut input = BufReader::new(File::open(input_path)?);
    let mut output = BufWriter::new(File::create(&temp_output_path)?);
    let mut buffer = vec![0u8; CHUNK_SIZE]; // 1MiB chunk

    loop {
        let read_bytes = input.read(&mut buffer)?;
        if read_bytes == 0 {
            break;
        }
        let chunk = &buffer[..read_bytes];

        let nonce = Aes256Gcm::generate_nonce(&mut OsRng);
        let encrypted = cipher
            .encrypt(&nonce, chunk)
            .map_err(|e| CryptError::Error(e.to_string()))?;

        // Write nonce length, nonce, ciphertext length, ciphertext
        output.write_all(&(nonce.as_slice().len() as u64).to_le_bytes())?;
        output.write_all(nonce.as_slice())?;
        output.write_all(&(encrypted.len() as u64).to_le_bytes())?;
        output.write_all(&encrypted)?;
    }
    output.flush()?;
    drop(output); // Ensure the file is closed before renaming

    fs::rename(temp_output_path, input_path)?;

    Ok(())
}

pub fn decrypt_file(input_path: &Path, key_bytes: &[u8]) -> Result<(), CryptError> {
    let key = Key::<Aes256Gcm>::from_slice(key_bytes);
    let cipher = Aes256Gcm::new(key);

    let temp_output_path = input_path.with_extension("dec.tmp");
    let mut input = BufReader::new(File::open(input_path)?);
    let mut output = BufWriter::new(File::create(&temp_output_path)?);

    let mut len_buf = [0u8; 8];
    loop {
        // Read nonce
        if input.read(&mut len_buf)? == 0 {
            break; // end
        }
        let nonce_len = u64::from_le_bytes(len_buf) as usize;
        let mut nonce_buf = vec![0u8; nonce_len];
        input.read_exact(&mut nonce_buf)?;

        // Read ciphertext
        input.read_exact(&mut len_buf)?;
        let ct_len = u64::from_le_bytes(len_buf) as usize;
        let mut ct_buf = vec![0u8; ct_len];
        input.read_exact(&mut ct_buf)?;

        let nonce = Nonce::from_slice(&nonce_buf);
        let decrypted = cipher
            .decrypt(nonce, ct_buf.as_ref())
            .map_err(|e| CryptError::Error(e.to_string()))?;
        output.write_all(&decrypted)?;
    }
    output.flush()?;
    drop(output); // Ensure the file is closed before renaming

    fs::rename(temp_output_path, input_path)?;

    Ok(())
}

/// Encrypt all files in a directory
/// This function will encrypt all files in a directory and its subdirectories
///
/// # Arguments
///
/// * `input_path` - A path to the directory to encrypt
///
/// * `key_bytes` - A byte slice containing the key to encrypt the files with
///
/// # Returns
///
/// A Result containing either an empty tuple or a CryptError
#[instrument(skip_all)]
pub fn encrypt_directory(input_path: &Path, key_bytes: &[u8]) -> Result<(), CryptError> {
    let files = FileUtils::list_files(input_path.to_path_buf())?;

    debug!("Encrypting files in directory: {:?}", files);

    let encrypted_files = files
        .into_par_iter()
        .map(|file| encrypt_file(&file, key_bytes))
        .collect::<Vec<Result<(), CryptError>>>();

    // check if any of the files failed to decrypt (if so, return an error)
    for file in encrypted_files {
        if file.is_err() {
            return Err(file.err().unwrap());
        }
    }

    Ok(())
}

/// Decrypt all files in a directory
///
/// This function will decrypt all files in a directory and its subdirectories
///
/// # Arguments
///
/// * `input_path` - A path to the directory to decrypt
/// * `key_bytes` - A byte slice containing the key to decrypt the files with
///
/// # Returns
///
/// A Result containing either an empty tuple or a CryptError
pub fn decrypt_directory(input_path: &Path, key_bytes: &[u8]) -> Result<(), CryptError> {
    // get all files (including subdirectories)
    let files = FileUtils::list_files(input_path.to_path_buf())?;

    let decrypted_files = files
        .into_par_iter()
        .map(|file| decrypt_file(&file, key_bytes))
        .collect::<Vec<Result<(), CryptError>>>();

    // check if any of the files failed to decrypt (if so, return an error)
    for file in decrypted_files {
        if file.is_err() {
            return Err(file.err().unwrap());
        }
    }
    Ok(())
}

/// Tests
#[cfg(test)]
mod tests {
    use super::*;
    use crate::key::{derive_encryption_key, derive_master_key, generate_salt};
    use rand::distributions::Alphanumeric;
    use rand::thread_rng;
    use rand::Rng;
    use std::io::Read;

    pub fn create_file(name: &str, chunk_size: &u64) {
        let mut file = File::create(name).expect("Could not create sample file.");
        let file_size = *chunk_size as f64 * 2.1;

        while file.metadata().unwrap().len() <= file_size as u64 {
            let rand_string: String = thread_rng()
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

    #[test]
    fn test_encrypt_directory() {
        // Create a temporary directory
        let temp_dir = tempfile::tempdir().unwrap();
        let input_path = temp_dir.path().join("test");
        fs::create_dir(&input_path).unwrap();

        // Create a temporary file
        let file_path = input_path.join("test.txt");
        let one_mb = 1024 * 1024 * 4;
        create_file(file_path.to_str().unwrap(), &one_mb);

        let file_path2 = input_path.join("test1.txt");
        let one_mb = 1024 * 1024;
        create_file(file_path2.to_str().unwrap(), &one_mb);

        // read filed and hold in buffer (used for comparison later)
        let mut file_buffer = Vec::new();
        File::open(&file_path)
            .unwrap()
            .read_to_end(&mut file_buffer)
            .unwrap();

        let mut file_buffer2 = Vec::new();
        File::open(&file_path2)
            .unwrap()
            .read_to_end(&mut file_buffer2)
            .unwrap();

        // setup keys
        let master_key = derive_master_key(b"password", &generate_salt(), Some(2)).unwrap();
        let derived_key = derive_encryption_key(&master_key, &generate_salt(), b"info").unwrap();

        // encrypt the directory
        encrypt_directory(&input_path, &derived_key).unwrap();

        // read the encrypted file and hold in buffer
        let mut encrypted_file_buffer = Vec::new();
        File::open(&file_path)
            .unwrap()
            .read_to_end(&mut encrypted_file_buffer)
            .unwrap();

        let mut encrypted_file_buffer2 = Vec::new();
        File::open(&file_path2)
            .unwrap()
            .read_to_end(&mut encrypted_file_buffer2)
            .unwrap();

        // check that the file is encrypted
        assert_ne!(file_buffer, encrypted_file_buffer);
        assert_ne!(file_buffer2, encrypted_file_buffer2);

        // decrypt the directory
        decrypt_directory(&input_path, &derived_key).unwrap();

        // read the decrypted file and hold in buffer
        let mut decrypted_file_buffer = Vec::new();
        File::open(&file_path)
            .unwrap()
            .read_to_end(&mut decrypted_file_buffer)
            .unwrap();

        let mut decrypted_file_buffer2 = Vec::new();
        File::open(&file_path2)
            .unwrap()
            .read_to_end(&mut decrypted_file_buffer2)
            .unwrap();

        // check that the file is decrypted
        assert_eq!(file_buffer, decrypted_file_buffer);
        assert_eq!(file_buffer2, decrypted_file_buffer2);
    }
}
