fn main() {
    let args: Vec<String> = std::env::args().collect();
    if let Err(e) = opsml_cli::run_cli(args) {
        eprintln!("Error: {e:#}");
        std::process::exit(1);
    }
}
