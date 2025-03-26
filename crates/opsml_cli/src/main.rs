pub mod cli;

use anyhow::{Context, Result};
use clap::Parser;
use owo_colors::OwoColorize;

fn main() -> Result<()> {
    let cli = Cli::parse();
}
