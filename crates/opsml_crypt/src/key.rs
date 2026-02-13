use aes_gcm::{
    Aes256Gcm,
    Key, // Or `Aes128Gcm`
    Nonce,
    aead::{Aead, AeadCore, KeyInit, OsRng},
};

use crate::error::CryptError;
use base64::Engine;
use base64::engine::general_purpose::URL_SAFE_NO_PAD;
use hkdf::Hkdf;
use hmac::Hmac;
use pbkdf2::pbkdf2;
use rand::distr::Alphanumeric;
use rand::{Rng, TryRngCore, rngs::OsRng as RandOsRng};
use sha2::Digest;
use sha2::Sha256;

const PBKDF2_ITERATIONS: u32 = 100_000;

/// Derive a master key from a password and salt
/// The master key is a PBKDF2 and is always stored on the server-side.
/// For client interaction an additional key is derived from the master key on the server and sent to the client.
/// A master key should always be stored in a secret manager
///
/// # Arguments
/// * `password` - A byte slice containing the password
/// * `salt` - A byte slice containing the salt
///
/// # Returns
///
/// A 32-byte array containing the derived master key
pub fn derive_master_key(
    password: &[u8],
    salt: &[u8],
    rounds: Option<u32>,
) -> Result<[u8; 32], CryptError> {
    let mut master_key = [0u8; 32];
    pbkdf2::<Hmac<Sha256>>(
        password,
        salt,
        rounds.unwrap_or(PBKDF2_ITERATIONS),
        &mut master_key,
    )
    .map_err(|e| CryptError::DeriveKeyError(e.to_string()))?;

    Ok(master_key)
}

/// Derive an encryption key from a master key
///
/// # Arguments
/// * `master_key` - A byte slice containing the master key
/// * `salt` - A byte slice containing the salt
/// * `info` - A byte slice containing the info
///
/// # Returns
/// A 32-byte array containing the derived encryption key
pub fn derive_encryption_key(
    master_key: &[u8],
    salt: &[u8],
    info: &[u8],
) -> Result<[u8; 32], CryptError> {
    let hk = Hkdf::<Sha256>::new(Some(salt), master_key);
    let mut okm = [0u8; 32];
    hk.expand(info, &mut okm)
        .map_err(|e| CryptError::DeriveKeyError(e.to_string()))?;
    Ok(okm)
}

/// Generate a random salt
pub fn generate_salt() -> Result<[u8; 16], CryptError> {
    let mut salt = [0u8; 16];
    RandOsRng
        .try_fill_bytes(&mut salt)
        .map_err(|_| CryptError::GenerateSaltError)?;
    Ok(salt)
}

/// Encrypt a key using AES-256-GCM
/// This us used to encrypt the encryption key for storing in databases. This is typically run on the server-side.
///
/// # Arguments
/// * `master_key` - A byte slice containing the master key
/// * `key` - A byte slice containing the key to encrypt
///
/// # Returns
/// A vector containing the nonce and the encrypted key
pub fn encrypted_key(master_key: &[u8], key: &[u8]) -> Result<Vec<u8>, CryptError> {
    let aes_key = std::panic::catch_unwind(|| Key::<Aes256Gcm>::from_slice(master_key));

    if let Err(panic) = aes_key {
        let panic_msg = panic
            .downcast_ref::<String>()
            .map(|s| s.as_str())
            .or_else(|| panic.downcast_ref::<&str>().copied())
            .unwrap_or("Unknown panic message");

        return Err(CryptError::AesCreateError(panic_msg.to_string()));
    }

    let cipher = Aes256Gcm::new(aes_key.unwrap());
    let nonce = Aes256Gcm::generate_nonce(&mut OsRng);

    let encrypted_key = cipher
        .encrypt(&nonce, key)
        .map_err(|_| CryptError::EncryptKeyError)?;

    Ok([nonce.as_slice(), encrypted_key.as_slice()].concat())
}

/// Decrypt a key using AES-256-GCM
/// This is used to decrypt the encryption key for use in the client. This is done on the server-side.
///
/// # Arguments
/// * `master_key` - A byte slice containing the master key
/// * `encrypted_key` - A byte slice containing the encrypted key
///
/// # Returns
///
/// A vector containing the decrypted key
pub fn decrypt_key(master_key: &[u8], encrypted_key: &[u8]) -> Result<Vec<u8>, CryptError> {
    let aes_key = std::panic::catch_unwind(|| Key::<Aes256Gcm>::from_slice(master_key));

    if let Err(panic) = aes_key {
        let panic_msg = panic
            .downcast_ref::<String>()
            .map(|s| s.as_str())
            .or_else(|| panic.downcast_ref::<&str>().copied())
            .unwrap_or("Unknown panic message");

        return Err(CryptError::AesCreateError(panic_msg.to_string()));
    }

    let cipher = Aes256Gcm::new(aes_key.unwrap());
    let nonce = Nonce::from_slice(&encrypted_key[..12]);
    let key = cipher
        .decrypt(nonce, &encrypted_key[12..])
        .map_err(|_| CryptError::DecryptKeyError)?;
    Ok(key)
}

pub fn generate_code_verifier() -> String {
    rand::rng()
        .sample_iter(&Alphanumeric)
        .take(64)
        .map(char::from)
        .collect()
}

pub fn generate_code_challenge(code_verifier: &str) -> String {
    let hash = Sha256::digest(code_verifier.as_bytes());
    URL_SAFE_NO_PAD.encode(hash)
}

// tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_derive_master_key() {
        let password = b"password";
        let salt = generate_salt();
        let master_key = derive_master_key(password, &salt.unwrap(), Some(2)).unwrap();
        assert_eq!(master_key.len(), 32);
    }

    #[test]
    fn test_generate_salt() {
        let salt = generate_salt().unwrap();
        assert_eq!(salt.len(), 16);

        let password = b"password";
        let salt = generate_salt();
        let _key = derive_master_key(password, &salt.unwrap(), Some(1)).unwrap();
    }

    #[test]
    fn test_derive_encryption_key() {
        let password = b"password";
        let salt = generate_salt().unwrap();
        let master_key = derive_master_key(password, &salt, Some(2)).unwrap();
        let info = b"info";
        let derived_key = derive_encryption_key(&master_key, &salt, info).unwrap();
        assert_eq!(derived_key.len(), 32);

        // encrypt and decrypt derived key
        let encrypted_key = encrypted_key(&master_key, &derived_key).unwrap();
        let decrypted_key = decrypt_key(&master_key, &encrypted_key).unwrap();

        assert_eq!(derived_key, decrypted_key.as_slice());
    }
}
