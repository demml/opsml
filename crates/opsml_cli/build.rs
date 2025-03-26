use std::env;
use std::path::Path;
use std::process::Command;

fn main() {
    // Only build server if the "server" feature is enabled
    if env::var("CARGO_FEATURE_SERVER").is_ok() {
        println!("cargo:rerun-if-changed=build_server.sh");

        let manifest_dir = env::var("CARGO_MANIFEST_DIR").unwrap();

        // Path to build script
        let script_path = Path::new(&manifest_dir).join("build_server.sh");

        // Make script executable
        Command::new("chmod")
            .arg("+x")
            .arg(&script_path)
            .status()
            .expect("Failed to make build script executable");

        // Execute build script
        let status = Command::new(&script_path)
            .status()
            .expect("Failed to execute build script");

        if !status.success() {
            panic!("Failed to build server");
        }

        println!("cargo:rerun-if-changed=src/server/opsml-server");
    }
}
