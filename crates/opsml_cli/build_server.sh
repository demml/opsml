#!/bin/bash
set -e

# Get the CLI directory path
CLI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRATES_DIR="$(dirname "$CLI_DIR")"

# Set paths
SERVER_DIR="$CRATES_DIR/opsml_server"
TARGET_DIR="$CLI_DIR/src/server"

echo "🔨 Building opsml-server..."

# Build the server
cd "$SERVER_DIR"
cargo build

# Create server directory in CLI if it doesn't exist
mkdir -p "$TARGET_DIR"

# Copy the binary to the CLI's server directory
cp "$CRATES_DIR/../target/release/opsml-server" "$TARGET_DIR/"

# Make the binary executable
chmod +x "$TARGET_DIR/opsml-server"

echo "✅ Server binary installed to src/server/"