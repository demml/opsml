use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm,
    Key, // Or `Aes128Gcm`
    Nonce,
};

use hkdf::Hkdf;
use hmac::Hmac;
use opsml_error::CryptError;
use pbkdf2::pbkdf2;
use rand::rngs::OsRng as RandOsRng;
use rand::RngCore;
use sha2::Sha256;

const PBKDF2_ITERATIONS: u32 = 100_000;

/// Derive a master key from a password and salt
/// The master key is a PBKDF2 and is always stored on the server-side.
/// For client interaction an additional key is derived from the master key on the server and sent to the client.
/// A master key should always be stored in a secret manager
///
/// # Arguments
///
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
    .map_err(|_| CryptError::Error("Failed to derive master key".to_string()))?;

    Ok(master_key)
}

/// Derive an encryption key from a master key
///
/// # Arguments
///
/// * `master_key` - A byte slice containing the master key
/// * `salt` - A byte slice containing the salt
/// * `info` - A byte slice containing the info
///
/// # Returns
///
/// A 32-byte array containing the derived encryption key
pub fn derive_encryption_key(master_key: &[u8], salt: &[u8], info: &[u8]) -> [u8; 32] {
    let hk = Hkdf::<Sha256>::new(Some(salt), master_key);
    let mut okm = [0u8; 32];
    hk.expand(info, &mut okm).expect("Failed to derive key");
    okm
}

/// Generate a random salt
pub fn generate_salt() -> [u8; 16] {
    let mut salt = [0u8; 16];
    RandOsRng.fill_bytes(&mut salt);
    salt
}

/// Encrypt a key using AES-256-GCM
/// This us used to encrypt the encryption key for storing in databases. This is typically run on the server-side.
///
/// # Arguments
///
/// * `master_key` - A byte slice containing the master key
/// * `key` - A byte slice containing the key to encrypt
///
/// # Returns
///
/// A vector containing the nonce and the encrypted key
pub fn encrypt_key(master_key: &[u8], key: &[u8]) -> Vec<u8> {
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(master_key));
    let nonce = Aes256Gcm::generate_nonce(&mut OsRng);
    let encrypted_key = cipher.encrypt(&nonce, key).expect("encryption failure!");
    [nonce.as_slice(), encrypted_key.as_slice()].concat()
}

/// Decrypt a key using AES-256-GCM
/// This is used to decrypt the encryption key for use in the client. This is done on the server-side.
///
/// # Arguments
///
/// * `master_key` - A byte slice containing the master key
/// * `encrypted_key` - A byte slice containing the encrypted key
///
/// # Returns
///
/// A vector containing the decrypted key
pub fn decrypt_key(master_key: &[u8], encrypted_key: &[u8]) -> Vec<u8> {
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(master_key));
    let nonce = Nonce::from_slice(&encrypted_key[..12]);
    let key = cipher
        .decrypt(nonce, &encrypted_key[12..])
        .expect("decryption failure!");
    key
}

// tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_derive_master_key() {
        let password = b"password";
        let salt = generate_salt();
        let master_key = derive_master_key(password, &salt, Some(2)).unwrap();
        assert_eq!(master_key.len(), 32);
    }

    #[test]
    fn test_generate_salt() {
        let salt = generate_salt();
        assert_eq!(salt.len(), 16);

        let password = b"password";
        let salt = generate_salt();
        let _key = derive_master_key(password, &salt, Some(1)).unwrap();
    }

    #[test]
    fn test_derive_encryption_key() {
        let password = b"password";
        let salt = generate_salt();
        let master_key = derive_master_key(password, &salt, Some(2)).unwrap();
        let info = b"info";
        let derived_key = derive_encryption_key(&master_key, &salt, info);
        assert_eq!(derived_key.len(), 32);

        // encrypt and decrypt derived key
        let encrypted_key = encrypt_key(&master_key, &derived_key);
        let decrypted_key = decrypt_key(&master_key, &encrypted_key);

        assert_eq!(derived_key, decrypted_key.as_slice());
    }
}
