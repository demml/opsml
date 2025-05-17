use rand::distr::Alphanumeric;
use rand::Rng;

/// helper for generating recovery codes
///
/// # Arguments
/// * `count` - The number of recovery codes to generate
///
/// # Returns
/// A vector of recovery codes
pub fn generate_recovery_codes(count: usize) -> Vec<String> {
    let mut codes = Vec::with_capacity(count);

    for _ in 0..count {
        // Generate 16 random alphanumeric characters
        let rand_string: String = rand::rng()
            .sample_iter(&Alphanumeric)
            .take(16)
            .map(char::from)
            .collect();

        // Split into groups of 4 for readability
        let formatted = rand_string
            .chars()
            .collect::<Vec<char>>()
            .chunks(4)
            .map(|c| c.iter().collect::<String>())
            .collect::<Vec<String>>()
            .join("-");

        codes.push(formatted);
    }

    codes
}
