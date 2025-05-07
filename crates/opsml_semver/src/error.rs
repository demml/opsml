use thiserror::Error;

#[derive(Error, Debug)]
pub enum VersionError {
    #[error("Invalid version string: {0}")]
    InvalidVersionString(String),

    #[error("Invalid version")]
    InvalidVersion(#[source] semver::Error),

    #[error("Invalid pre release identifier")]
    InvalidPreReleaseIdentifier(#[source] semver::Error),

    #[error("Version string is empty")]
    EmptyVersionString,

    #[error("Invalid version parse error")]
    ParseError(#[source] core::num::ParseIntError),

    #[error("Invalid version provided with * syntax")]
    StarSyntaxError,

    #[error("Invalid version provided with ^ syntax")]
    CaretSyntaxError,

    #[error("Invalid version provided with exact syntax")]
    ExactSyntaxError,
}
