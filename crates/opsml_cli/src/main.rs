fn main() {
    // run_cli does skip(1) to drop a leading Python/wrapper binary name.
    // Insert a dummy element so skip(1) removes it and clap receives the
    // real binary path as its program name, followed by the actual args.
    let mut args: Vec<String> = std::env::args().collect();
    args.insert(0, String::new());
    if let Err(e) = opsml_cli::run_cli(args) {
        eprintln!("Error: {e:#}");
        std::process::exit(1);
    }
}
