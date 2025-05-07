use crate::error::VersionError;
use pyo3::prelude::*;
use semver::{BuildMetadata, Prerelease, Version};
use serde::{Deserialize, Serialize};
use std::str::FromStr;
use std::string::ToString;
#[pyclass]
#[derive(Debug, PartialEq, Deserialize, Serialize, Clone)]
pub enum VersionType {
    Major,
    Minor,
    Patch,
    Pre,
    Build,
    PreBuild,
}

impl FromStr for VersionType {
    type Err = ();

    fn from_str(input: &str) -> Result<VersionType, Self::Err> {
        match input.to_lowercase().as_str() {
            "major" => Ok(VersionType::Major),
            "minor" => Ok(VersionType::Minor),
            "patch" => Ok(VersionType::Patch),
            "pre" => Ok(VersionType::Pre),
            "build" => Ok(VersionType::Build),
            "pre_build" => Ok(VersionType::PreBuild),
            _ => Err(()),
        }
    }
}

#[pymethods]
impl VersionType {
    #[new]
    fn new(version_type: &str) -> PyResult<Self> {
        match VersionType::from_str(version_type) {
            Ok(version_type) => Ok(version_type),
            Err(()) => Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid version type",
            )),
        }
    }

    fn __eq__(&self, other: &Self) -> bool {
        self == other
    }
}

#[derive(Debug, PartialEq)]
pub struct VersionArgs {
    pub version: String,
    pub version_type: VersionType,
    pub pre: Option<String>,
    pub build: Option<String>,
}

pub struct VersionValidator {}

impl VersionValidator {
    pub fn validate_version(version: &str) -> Result<(), VersionError> {
        match Version::parse(version) {
            Ok(_) => Ok(()),
            Err(e) => Err(VersionError::InvalidVersion(e)),
        }
    }

    pub fn bump_version(version_args: &VersionArgs) -> Result<Version, VersionError> {
        // parse the version
        let version = match Version::parse(&version_args.version) {
            Ok(v) => v,
            Err(e) => return Err(VersionError::InvalidVersion(e)),
        };

        let mut new_version = Version::new(version.major, version.minor, version.patch);

        // check if version type is major, minor, or patch. If not, return the version as is
        match version_args.version_type {
            VersionType::Major => {
                new_version.major += 1;
                new_version.minor = 0;
                new_version.patch = 0;
            }
            VersionType::Minor => {
                new_version.minor += 1;
                new_version.patch = 0;
            }
            VersionType::Patch => new_version.patch += 1,

            // do nothing for pre and build
            VersionType::Pre | VersionType::Build | VersionType::PreBuild => {}
        };

        // its possible someone creates a major, minor, patch version with a pre or build, or both
        // in this case, we need to add the pre and build to the new version
        if let Some(pre) = &version_args.pre {
            new_version.pre = match Prerelease::new(pre) {
                Ok(p) => p,
                Err(e) => return Err(VersionError::InvalidPreReleaseIdentifier(e)),
            };
        }

        if let Some(build) = &version_args.build {
            new_version.build = match BuildMetadata::new(build) {
                Ok(b) => b,
                Err(e) => return Err(VersionError::InvalidPreReleaseIdentifier(e)),
            };
        }

        Ok(new_version)
    }

    pub fn sort_string_versions(versions: Vec<String>) -> Result<Vec<String>, VersionError> {
        let mut versions: Vec<Version> = versions
            .iter()
            .map(|v| Version::parse(v).map_err(VersionError::InvalidVersion))
            .collect::<Result<Vec<_>, _>>()?;

        versions.sort();

        Ok(versions.iter().map(ToString::to_string).collect())
    }

    pub fn sort_semver_versions(
        mut versions: Vec<Version>,
        reverse: bool,
    ) -> Result<Vec<String>, VersionError> {
        if versions.is_empty() {
            return Ok(vec![]);
        } else {
            versions.sort();

            if reverse {
                versions.reverse();
            }
        }

        Ok(versions.iter().map(ToString::to_string).collect())
    }

    /// Take a semver that may be incomplete and expand it to a full semver
    ///
    fn expand_version(version: &str) -> String {
        let version_parts: Vec<&str> = version.split('.').collect();

        // Return early if we already have all parts
        if version_parts.len() >= 3 {
            return version.to_string();
        }

        // Create a new vector with the existing parts
        let mut expanded_version = version_parts.to_vec();

        // Fill in missing parts with "0"
        while expanded_version.len() < 3 {
            expanded_version.push("0");
        }

        // Join parts with dots and return owned String
        expanded_version.join(".")
    }

    pub fn clean_version(version: &str) -> Result<Version, VersionError> {
        // Check if the version is empty
        if version.is_empty() {
            return Err(VersionError::EmptyVersionString);
        }

        match Version::parse(&Self::expand_version(version)) {
            Ok(version) => Ok(version),
            Err(e) => Err(VersionError::InvalidVersion(e)),
        }
    }
}

#[derive(Debug, PartialEq)]
pub struct VersionBounds {
    pub lower_bound: Version,
    pub upper_bound: Version,
    pub no_upper_bound: bool,
    pub parser_type: VersionParser,
    pub num_parts: usize,
}

#[derive(PartialEq, Debug)]
pub enum VersionParser {
    Star,
    Caret,
    Tilde,
    Exact,
}

impl VersionParser {
    /// Create a new VersionParser from a version string
    ///
    /// # Errors
    ///
    /// Returns an error if the version string is invalid
    pub fn new(version: &str) -> Result<VersionParser, VersionError> {
        // check if version contains
        if version.contains('*') {
            Ok(VersionParser::Star)
        } else if version.contains('^') {
            Ok(VersionParser::Caret)
        } else if version.contains('~') {
            Ok(VersionParser::Tilde)
        } else {
            Ok(VersionParser::Exact)
        }
    }

    pub fn remove_version_prefix(&self, version: &str) -> String {
        // break version into parts
        match self {
            VersionParser::Star => version.replace('*', ""),
            VersionParser::Caret => version.replace('^', ""),
            VersionParser::Tilde => version.replace('~', ""),
            VersionParser::Exact => version.to_string(),
        }
    }

    /// Parse a version string into a Version struct
    ///
    /// # Errors
    /// Errors if the version string is invalid
    fn parse_version(version: &str) -> Result<Version, VersionError> {
        Version::parse(version).map_err(VersionError::InvalidVersion)
    }

    /// Create a VersionBounds struct from a lower and upper version string
    ///
    /// # Errors
    /// Errors if the version strings are invalid
    fn create_bounds(
        lower: &str,
        upper: &str,
        parser_type: VersionParser,
        num_parts: usize,
        no_upper_bound: bool,
    ) -> Result<VersionBounds, VersionError> {
        Ok(VersionBounds {
            lower_bound: Self::parse_version(lower)?,
            upper_bound: Self::parse_version(upper)?,
            no_upper_bound,
            parser_type,
            num_parts,
        })
    }

    pub fn get_version_to_search(version: &str) -> Result<VersionBounds, VersionError> {
        let parser = VersionParser::new(version)?;

        let cleaned_version = parser.remove_version_prefix(version);

        // determine number of "." in the version and split into int parts
        let version_parts = cleaned_version
            .split('.')
            .filter(|v| !v.is_empty())
            .map(str::parse::<u64>)
            .collect::<Result<Vec<_>, _>>()
            .map_err(VersionError::ParseError)?;

        let num_parts = version_parts.len();

        match parser {
            VersionParser::Star => match num_parts {
                0 => Self::create_bounds("0.0.0", "0.0.0", VersionParser::Star, num_parts, true),
                1 => Self::create_bounds(
                    &format!("{}.0.0", version_parts[0]),
                    &format!("{}.0.0", version_parts[0] + 1),
                    VersionParser::Star,
                    num_parts,
                    false,
                ),
                2 => Self::create_bounds(
                    &format!("{}.{}.0", version_parts[0], version_parts[1]),
                    &format!("{}.{}.0", version_parts[0], version_parts[1] + 1),
                    VersionParser::Star,
                    num_parts,
                    false,
                ),
                3 => Self::create_bounds(
                    &format!(
                        "{}.{}.{}",
                        version_parts[0], version_parts[1], version_parts[2]
                    ),
                    &format!(
                        "{}.{}.{}",
                        version_parts[0],
                        version_parts[1],
                        version_parts[2] + 1
                    ),
                    VersionParser::Star,
                    num_parts,
                    false,
                ),
                _ => Err(VersionError::StarSyntaxError),
            },
            VersionParser::Tilde => match num_parts {
                1 => Self::create_bounds(
                    &format!("{}.0.0", version_parts[0]),
                    &format!("{}.0.0", version_parts[0] + 1),
                    VersionParser::Tilde,
                    num_parts,
                    false,
                ),
                2 => Self::create_bounds(
                    &format!("{}.{}.0", version_parts[0], version_parts[1]),
                    &format!("{}.{}.0", version_parts[0], version_parts[1] + 1),
                    VersionParser::Tilde,
                    num_parts,
                    false,
                ),
                _ => Self::create_bounds(
                    &format!(
                        "{}.{}.{}",
                        version_parts[0], version_parts[1], version_parts[2]
                    ),
                    &format!("{}.{}.0", version_parts[0], version_parts[1] + 1),
                    VersionParser::Tilde,
                    num_parts,
                    false,
                ),
            },
            VersionParser::Caret => {
                if num_parts >= 2 {
                    Self::create_bounds(
                        &format!(
                            "{}.{}.{}",
                            version_parts[0], version_parts[1], version_parts[2]
                        ),
                        &format!("{}.{}.0", version_parts[0], version_parts[1] + 1),
                        VersionParser::Caret,
                        num_parts,
                        false,
                    )
                } else {
                    Err(VersionError::CaretSyntaxError)
                }
            }
            VersionParser::Exact => match num_parts {
                1 => Self::create_bounds(
                    &format!("{}.0.0", version_parts[0]),
                    &format!("{}.0.0", version_parts[0] + 1),
                    VersionParser::Exact,
                    num_parts,
                    false,
                ),
                2 => Self::create_bounds(
                    &format!("{}.{}.0", version_parts[0], version_parts[1]),
                    &format!("{}.{}.0", version_parts[0], version_parts[1] + 1),
                    VersionParser::Exact,
                    num_parts,
                    false,
                ),
                3 => Self::create_bounds(
                    &format!(
                        "{}.{}.{}",
                        version_parts[0], version_parts[1], version_parts[2]
                    ),
                    &format!(
                        "{}.{}.{}",
                        version_parts[0],
                        version_parts[1],
                        version_parts[2] + 1
                    ),
                    VersionParser::Exact,
                    num_parts,
                    false,
                ),
                _ => Err(VersionError::ExactSyntaxError),
            },
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use semver::Version;

    #[test]
    fn test_version_validator_validate_version() {
        assert!(VersionValidator::validate_version("1.2.3").is_ok());
        assert!(VersionValidator::validate_version("invalid.version").is_err());

        // validate default
        assert_eq!(
            VersionValidator::clean_version("1.2.3-alpha").unwrap(),
            Version::parse("1.2.3-alpha").unwrap()
        );

        // validate with build
        assert_eq!(
            VersionValidator::clean_version("1.2.3+001").unwrap(),
            Version::parse("1.2.3+001").unwrap()
        );

        // validate with pre and build
        assert_eq!(
            VersionValidator::clean_version("1.2.3-alpha+001").unwrap(),
            Version::parse("1.2.3-alpha+001").unwrap()
        );

        // validate missing parts
        assert_eq!(
            VersionValidator::clean_version("1.2").unwrap(),
            Version::parse("1.2.0").unwrap()
        );

        assert_eq!(
            VersionValidator::clean_version("1").unwrap(),
            Version::parse("1.0.0").unwrap()
        );
    }

    #[test]
    fn test_version_validator_bump_version() {
        let args = VersionArgs {
            version: "1.2.3".to_string(),
            version_type: VersionType::Major,
            pre: None,
            build: None,
        };
        assert_eq!(
            VersionValidator::bump_version(&args).unwrap(),
            Version::parse("2.0.0").unwrap()
        );

        let args = VersionArgs {
            version: "1.2.3".to_string(),
            version_type: VersionType::Minor,
            pre: None,
            build: None,
        };
        assert_eq!(
            VersionValidator::bump_version(&args).unwrap(),
            Version::parse("1.3.0").unwrap()
        );

        let args = VersionArgs {
            version: "1.2.3".to_string(),
            version_type: VersionType::Patch,
            pre: None,
            build: None,
        };
        assert_eq!(
            VersionValidator::bump_version(&args).unwrap(),
            Version::parse("1.2.4").unwrap()
        );

        let args = VersionArgs {
            version: "1.2.3".to_string(),
            version_type: VersionType::Pre,
            pre: Some("alpha".to_string()),
            build: None,
        };
        assert_eq!(
            VersionValidator::bump_version(&args).unwrap(),
            Version::parse("1.2.3-alpha").unwrap()
        );

        let args = VersionArgs {
            version: "1.2.3".to_string(),
            version_type: VersionType::Build,
            pre: None,
            build: Some("001".to_string()),
        };
        assert_eq!(
            VersionValidator::bump_version(&args).unwrap(),
            Version::parse("1.2.3+001").unwrap()
        );

        let args = VersionArgs {
            version: "1.2.3".to_string(),
            version_type: VersionType::PreBuild,
            pre: Some("alpha".to_string()),
            build: Some("001".to_string()),
        };
        assert_eq!(
            VersionValidator::bump_version(&args).unwrap(),
            Version::parse("1.2.3-alpha+001").unwrap()
        );
    }

    #[test]
    fn test_version_validator_sort_versions() {
        let versions = vec![
            "1.2.1".to_string(),
            "1.3.0".to_string(),
            "1.2.2".to_string(),
            "1.2.3-alpha+001".to_string(),
            "1.2.3+001".to_string(),
            "1.2.3+0b1".to_string(),
            "1.2.3".to_string(),
        ];
        let sorted_versions = VersionValidator::sort_string_versions(versions).unwrap();
        assert_eq!(
            sorted_versions,
            vec![
                "1.2.1",
                "1.2.2",
                "1.2.3-alpha+001",
                "1.2.3",
                "1.2.3+001",
                "1.2.3+0b1",
                "1.3.0"
            ]
        );
    }

    #[test]
    fn test_version_parser_new() {
        assert_eq!(VersionParser::new("*").unwrap(), VersionParser::Star);
        assert_eq!(VersionParser::new("^1.2.3").unwrap(), VersionParser::Caret);
        assert_eq!(VersionParser::new("~1.2.3").unwrap(), VersionParser::Tilde);
        assert_eq!(VersionParser::new("1.2.3").unwrap(), VersionParser::Exact);
    }

    #[test]
    fn test_version_parser_remove_version_prefix() {
        assert_eq!(VersionParser::Star.remove_version_prefix("*"), "");
        assert_eq!(VersionParser::Star.remove_version_prefix("*1"), "1");
        assert_eq!(VersionParser::Star.remove_version_prefix("1.*"), "1.0");
        assert_eq!(VersionParser::Star.remove_version_prefix("1.2.*"), "1.2.0");
        assert_eq!(
            VersionParser::Caret.remove_version_prefix("^1.2.3"),
            "1.2.3"
        );
        assert_eq!(
            VersionParser::Tilde.remove_version_prefix("~1.2.3"),
            "1.2.3"
        );
        assert_eq!(VersionParser::Exact.remove_version_prefix("1.2.3"), "1.2.3");
    }

    #[test]
    fn test_version_parser_get_version_to_search() {
        let bounds = VersionParser::get_version_to_search("*").unwrap();
        assert_eq!(bounds.lower_bound, Version::parse("0.0.0").unwrap());
        assert!(bounds.no_upper_bound);

        let bounds = VersionParser::get_version_to_search("1.*").unwrap();
        assert_eq!(bounds.lower_bound, Version::parse("1.0.0").unwrap());
        assert_eq!(bounds.upper_bound, Version::parse("1.1.0").unwrap());

        let bounds = VersionParser::get_version_to_search("^1.2.3").unwrap();
        assert_eq!(bounds.lower_bound, Version::parse("1.2.3").unwrap());
        assert_eq!(bounds.upper_bound, Version::parse("1.3.0").unwrap());

        let bounds = VersionParser::get_version_to_search("~1.2.3").unwrap();
        assert_eq!(bounds.lower_bound, Version::parse("1.2.3").unwrap());
        assert_eq!(bounds.upper_bound, Version::parse("1.3.0").unwrap());
    }
}
