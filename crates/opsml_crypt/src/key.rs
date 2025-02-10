use hkdf::Hkdf;
use hmac::Hmac;
use opsml_error::CryptoError;
use pbkdf2::pbkdf2;
use rand::rngs::OsRng;
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
pub fn derive_master_key(password: &[u8], salt: &[u8]) -> Result<[u8; 32], CryptoError> {
    let mut master_key = [0u8; 32];
    pbkdf2::<Hmac<Sha256>>(password, salt, PBKDF2_ITERATIONS, &mut master_key)
        .map_err(|_| CryptoError::Error("Failed to derive master key".to_string()))?;

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

pub fn generate_salt() -> [u8; 16] {
    let mut salt = [0u8; 16];
    OsRng.fill_bytes(&mut salt);
    salt
}

// tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_derive_master_key() {
        let password = b"password";
        let salt = generate_salt();
        let master_key = derive_master_key(password, &salt).unwrap();
        assert_eq!(master_key.len(), 32);
    }

    #[test]
    fn test_generate_salt() {
        let salt = generate_salt();
        assert_eq!(salt.len(), 16);
    }

    #[test]
    fn test_derive_encryption_key() {
        let password = b"password";
        let salt = generate_salt();
        let master_key = derive_master_key(password, &salt).unwrap();
        let info = b"info";
        let encryption_key = derive_encryption_key(&master_key, &salt, info);
        assert_eq!(encryption_key.len(), 32);
    }
}
