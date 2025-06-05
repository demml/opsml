use serde::Deserialize;
// only extracting fields we need for user info
// We only need the name, preferred_username, and email. If the user response is valid, we will generate
// an opsml-held jwt token
#[derive(Deserialize, Debug)]
pub struct UserInfo {
    pub username: String,
}
