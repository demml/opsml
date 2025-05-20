use password_auth::generate_hash;
use rand::distr::Alphanumeric;
use rand::Rng;
use rayon::prelude::*;

pub fn generate_recovery_codes_with_hashes(count: usize) -> (Vec<String>, Vec<String>) {
    // Generate codes in parallel
    let results: Vec<(String, String)> = (0..count)
        .into_par_iter()
        .map(|_| {
            // Generate random code
            let code: String = rand::rng()
                .sample_iter(&Alphanumeric)
                .take(16)
                .map(char::from)
                .collect();

            // Hash the code
            let hashed = generate_hash(&code);

            (code, hashed)
        })
        .collect();

    // Unzip results into separate vectors
    results.into_iter().unzip()
}
