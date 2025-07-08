use crate::error::CliError;
use base64::prelude::*;
use opsml_colors::Colorize;
pub use opsml_crypt::{derive_master_key, generate_salt};
use pyo3::prelude::*;

/// Create a structured response for the generated key
///
/// # Arguments
/// * `key` - A string slice containing the generated key
///
/// # Returns
/// A formatted string containing the structured response
pub fn create_response(key: &str) -> String {
    let header = Colorize::green(
        "############################### Generated Key ###############################",
    );
    let key_response = Colorize::purple(&format!("Key: {key}"));
    let footer = Colorize::green(
        "#############################################################################",
    );
    let structured_response = format!(
        r#"
{header}
    This key will not be saved. Make sure to save it in a secure location
    {key_response}
{footer}
"#
    );

    structured_response
}

/// Generate a pbkdf2 key for the given password
///
/// # Arguments
/// * `password` - A byte slice containing the password
/// * `rounds` - An optional u32 containing the number of rounds
///
/// # Returns
/// A 32-byte array containing the derived key
///
/// # Errors
/// * `CliError::GenerateKeyError` - If the key generation fails

#[pyfunction]
#[pyo3(signature = (password, rounds=100_000))]
pub fn generate_key(password: &str, rounds: u32) -> Result<(), CliError> {
    let salt = generate_salt()?;

    // convert password to bytes
    let password = password.as_bytes();

    let key = derive_master_key(password, &salt, Some(rounds))?;

    // base64 encode the key
    let encoded_key = BASE64_STANDARD.encode(key);
    let structured_response = create_response(&encoded_key);
    println!("{structured_response}");

    Ok(())
}
